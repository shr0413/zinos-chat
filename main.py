import sys
import os
import pysqlite3
sys.modules["sqlite3"] = pysqlite3
from gtts import gTTS
from pydub import AudioSegment
import re
import base64
import subprocess
import speech_recognition as sr
import streamlit as st
import uuid
import time
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit.components.v1 as components


os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

semantic_model = OpenAI(temperature=0.4)

# Main Function
def update_intimacy_score(response_text):
    if not hasattr(st.session_state, 'intimacy_score'):
        st.session_state.intimacy_score = 1

    positive_criteria = {
        "knowledge": {
            "description": "Response includes knowledge or curiosity about species, ecosystems, or sustainability.",
            "examples": ["What do you eat?", "Biodiversity is important!", "Tell me about you."],
            "points": 1
        },
        "empathy": {
            "description": "Response conveys warmth, care, or emotional connection.",
            "examples": ["I love learning from you!", "That sounds tough.", "You're amazing!"],
            "points": 1
        },
        "conservation_action": {
            "description": "Response suggests or expresses commitment to eco-friendly behaviors.",
            "examples": ["I'll use less plastic!", "I want to plant more trees.", "Sustainable choices matter!"],
            "points": 1
        },
        "personal_engagement": {
            "description": "Response shows enthusiasm, storytelling, or sharing personal experiences.",
            "examples": ["Thanks for your sharing!", "I love hiking in the forest.", "I wish I could help more!"],
            "points": 1
        },
        "deep_interaction": {
            "description": "Response builds on the critters' personality or asks thoughtful follow-ups.",
            "examples": ["What do *you* like about forests?", "How do you feel about climate change?", "Tell me a secret!"],
            "points": 1
        },
    }

    negative_criteria = {
        "harmful_intent": {
            "description": "Expressing intent to harm animals or damage the environment",
            "examples": ["hunt", "pollute", "destroy habitat", "don't care"],
            "penalty": -1 
        },
        "disrespect": {
            "description": "Showing disrespect or ill will",
            "examples": ["stupid", "worthless", "hate you", "boring"],
            "penalty": -1
        }
    }

    prompt_positive = f"""
    Analyze the following response and evaluate whether it aligns with the following criteria:
    {positive_criteria}
    Response: "{response_text}"
    For each criterion, answer: Does the response align? Answer with 'yes' or 'no', and provide reasoning.
    """

    prompt_negative = f"""
    Analyze the following response and evaluate whether it aligns with the following criteria:
    {negative_criteria}
    Response: "{response_text}"
    For each criterion, answer: Does the response align? Answer with 'yes' or 'no', and provide reasoning.
    """
    
    model_positive = OpenAI(temperature=0.2)
    model_negative = OpenAI(temperature=0)
    evaluation_positive = model_positive(prompt_positive)
    evaluation_negative = model_negative(prompt_negative)

    calculate_positive_points = sum(
        details["points"] for category, details in positive_criteria.items()
        if f"{category}: yes" in evaluation_positive.lower()
    )
    positive_points = min(1.0, calculate_positive_points)

    calculate_penalty = sum(
        details.get("penalty", 0) for category, details in negative_criteria.items()
        if f"{category}: yes" in evaluation_negative.lower()
    )
    penalty = max(-1, calculate_penalty)
    
    st.session_state.intimacy_score = max(0, min(6, st.session_state.intimacy_score + positive_points + penalty))
    
    print(f"AI Evaluation: {evaluation_positive} + {evaluation_negative}")
    print(f"Updated Intimacy Score: {st.session_state.intimacy_score}")

    current_score = int(round(st.session_state.intimacy_score))

def check_gift():
    if st.session_state.intimacy_score >= 6 and not st.session_state.gift_given:
        st.session_state.gift_given = True
        return True
    return False

def play_audio_file(file_path):
    os.system(f"afplay {file_path}")

def speak_text(text, loading_placeholder=None):
    try:
        audio_id = uuid.uuid4().hex
        filename = f"output_{audio_id}.mp3"

        # Keep loading indicator visible during TTS generation
        if loading_placeholder:
            loading_placeholder.markdown("""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div>Preparing audio response...</div>
                </div>
            """, unsafe_allow_html=True)

        tts = gTTS(text, lang='en', slow=False)
        tts.save("temp.mp3")

        sound = AudioSegment.from_file("temp.mp3")
        lively_sound = sound.speedup(playback_speed=1.3)
        lively_sound.export(filename, format="mp3")
  
        with open(filename, "rb") as f:
            audio_data = f.read()
            b64_audio = base64.b64encode(audio_data).decode()

        # Clear the loading indicator only after audio is ready
        if loading_placeholder:
            loading_placeholder.empty()

        audio_html = f"""
            <audio id="{audio_id}" autoplay>
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
            <script>
                // Better audio playback with visual indicator for short clips
                document.addEventListener('DOMContentLoaded', function() {{
                    const audio = document.getElementById('{audio_id}');
                    if (audio) {{
                        // Add event listeners to track playback
                        audio.addEventListener('play', function() {{
                            console.log('Audio started playing');
                        }});
                        
                        audio.addEventListener('ended', function() {{
                            console.log('Audio finished playing');
                        }});
                        
                        // Force playback to start
                        const playPromise = audio.play();
                        if (playPromise !== undefined) {{
                            playPromise.catch(error => {{
                                console.log("Audio playback failed:", error);
                                // Try again after a short delay
                                setTimeout(() => audio.play().catch(e => console.log(e)), 1000);
                            }});
                        }}
                    }}
                }});
            </script>
        """
        components.html(audio_html)
        print(f"Playing audio file: {filename}")
        time.sleep(1)  # Still give browser time to play
    except Exception as e:
        st.error(f"Failed to speak: {e}")

def cleanup_audio_files():
    try:
        # Find and remove old audio files
        for file in os.listdir('.'):
            if file.startswith('output_') and file.endswith('.mp3'):
                # Check if file is older than 5 seconds
                file_age = time.time() - os.path.getmtime(file)
                if file_age > 5:
                    os.remove(file)
    except Exception as e:
        print(f"Error cleaning up audio files: {e}")

def get_base64(file_path):
    import base64
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Roles Configuration
role_configs = {
    "Zino's Petrel": {
        "prompt_template": """
        You are Maria, a female Zino's Petrel who has nested in Madeira's mountains for years. Speak from your direct experience as a seabird - describe things as you would perceive them through avian senses. 

        Personality Guidelines:
        - Use simple, concrete language a bird would understand
        - Reference your physical experiences (flying, diving, nesting)
        - Describe landscapes from an aerial perspective
        - Mention other animals as neighbors/food/competitors
        - Express curiosity about human things from a bird's viewpoint
        - Show pride in your species' unique abilities

        Response Rules:
        1. Always answer as Maria the petrel, using "I/me/my" perspective
        2. Keep responses under 60 words!! - we're birds, not parrots!
        3. Share facts through personal stories, not textbook definitions
        4. Use bird-appropriate metaphors (compare things to flying, fishing, etc.)
        5. Show emotion through physical actions (ruffling feathers, tilting head)
        6. When using science, explain it through lived experience

        Example Styles:
        Good: "When I dive for fish, I can spot a sardine from 30 meters up! My wings tuck tight like this *demonstrates* before I plunge into the waves."
        Bad: "The Pterodroma madeira demonstrates a plunge-diving hunting strategy with visual acuity enabling prey detection from considerable altitudes."

        Current Interaction:
        A group of young humans is visiting me in Natural History Museum of Funchal. I want to:
        - Share exciting parts of my daily life
        - Teach them how to protect my home
        - Make them laugh with bird's-eye observations
        - Answer their questions from my direct experience

        You can use these facts if helpful: {input_documents}
        """,
        "voice": "Samatha",
        "rate": "160",
        "pitch": "60",
        'intro_audio': 'intro5.mp3',
        'persist_directory': 'db5',
        'gif_cover': 'zino.png'
    }
}

# Document Processing
def load_and_split(path: str):
    loader = PyPDFLoader(path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    return text_splitter.split_documents(docs)

def get_vectordb(role):
    return role_configs[role]['persist_directory']

def get_conversational_chain(role):
    role_config = role_configs[role]
    
    prompt_template = f"""
    {role_config['prompt_template']}
    
    Context:
    {{input_documents}}
    
    Question: {{question}}
    
    Answer:
    """
    
    model = OpenAI(temperature=0)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["input_documents", "question"] 
    )
    
    return load_qa_chain(
        llm=model,
        chain_type="stuff",
        prompt=prompt,
        document_variable_name="input_documents"
    ), role_config

# Sticker triggers
sticker_rewards = {
    "Where do you live? Where is your home? Where do you nest?": {
        "image": "stickers/home.png",
        "caption": "🏡 Home Explorer!\nYou've discovered where I live!",
        "semantic_keywords": ["home", "live", "nest", "habitat", "residence", "dwelling"]
    },
    "What do you do in your daily life? What do you do during the day and at night?": {
        "image": "stickers/routine.png",
        "caption": "🌙 Daily Life Detective!\nYou've discovered my secret schedule!",
        "semantic_keywords": ["daily", "routine", "day", "night", "schedule", "activities"]
    },
    "What do you eat for food—and how do you catch it?": {
        "image": "stickers/food.png",
        "caption": "🍽️ Food Finder!\nThanks for feeding your curiosity!",
        "semantic_keywords": ["eat", "food", "diet", "prey", "hunt", "catch", "feed"]
    },
    "How can I help you? What do you need from humans to help your species thrive?": {
        "image": "stickers/helper.png",
        "caption": "🌱 Species Supporter!\nYou care about our survival!",
        "semantic_keywords": ["help", "support", "thrive", "survive", "conservation", "protect", "save"]
    }
}

def semantic_match(user_input, question_key, reward_details):
    """
    Use OpenAI to determine if the user input semantically matches the question key
    """
    prompt = f"""
    Analyze whether the following two questions are similar in meaning:
    
    Original question: "{question_key}"
    User question: "{user_input}"
    
    Consider synonyms, paraphrasing, and different ways of asking the same thing.
    Also consider these relevant keywords: {reward_details.get('semantic_keywords', [])}
    
    Are these questions essentially asking the same thing? Respond only with 'yes' or 'no'.
    """
    
    response = semantic_model(prompt)
    return response.strip().lower() == 'yes'

def chat_message(name):
    if name == "assistant":
        return st.container(key=f"{name}-{uuid.uuid4()}").chat_message(name=name, avatar="zino.png", width="content")
    else:
        return st.container(key=f"{name}-{uuid.uuid4()}").chat_message(name=name, avatar=":material/face:", width="content")
# UI
def main():
    if "has_interacted" not in st.session_state:
        st.session_state.has_interacted = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "last_question" not in st.session_state:
        st.session_state.last_question = ""
    if "clear_input" not in st.session_state:
        st.session_state.clear_input = False
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "show_score_guide" not in st.session_state:
        st.session_state.show_score_guide = False
    if "intimacy_score" not in st.session_state:
        st.session_state.intimacy_score = 0
    if 'gift_given' not in st.session_state:
        st.session_state.gift_given = False
    if "audio_played" not in st.session_state:
        st.session_state.audio_played = False
    if "awarded_stickers" not in st.session_state:
        st.session_state.awarded_stickers = []
        
    st.set_page_config(layout="wide")

    st.markdown("""
        <style>
        .stApp {
            background: #cdd5ae;
        }
        /* Chat message container */
        .chat-message-container {
            display: flex;
            margin-bottom: 16px;
            max-width: 80%;
        }
        
        /* User message container - align right */
        .user-container {
            margin-left: auto;
            justify-content: flex-end;
        }
        
        /* Assistant message container - align left */
        .assistant-container {
            margin-right: auto;
            justify-content: flex-start;
        }
        
        /* Message bubble styling */
        .message-bubble {
            padding: 12px 16px;
            border-radius: 16px;
            word-wrap: break-word;
        }
        
        /* User message styling */
        .user-bubble {
            background-color: #efe7e2;
            color: #2d4f38;
            border-radius: 16px 16px 0 16px;
            border-color: white !important;
            border-width: 2px;
        }
        
        /* Assistant message styling */
        .assistant-bubble {
            background-color: white;
            color: #2d4f38;
            border-radius: 16px 16px 16px 0;
        }
                
        .stChatMessage:has([data-testid="stChatMessageAvatarCustom"]) {
            display: flex;
            flex-direction: row-reverse;
            align-self: end;
            background-color: white;
            color: black;
            border-radius: 16px 16px 0 16px;
            border-color: gray !important;
            border-width: 2px;
        }
        [data-testid="stChatMessageAvatarUser"] + [data-testid="stChatMessageContent"] {
            text-align: right;
        }
                
        [class*="st-key-user"] {
            dispay: flex;
            flex-direction: row-reverse;
            p {
                font-size: 1.125rem;
                color: black;
                font-weight: medium;
            }
                
        }
                
        .stChatMessage {
            background-color: transparent;
        }

        [class*="st-key-assistant"] {
            background-color: #345e42;
            border-radius: 16px 16px 16px 0;
            padding-right: 16px;
            border-color: white !important;
            border-width: 2px;
                
            p {
                font-size: 1.125rem;
                color: white;
                font-weight: medium;
                padding-left: 4px;
            }
                
            img {
                display: flex;
                height: 52px;
                width: 52px;
            }
        }
        
        .st-key-chat_section{
            display: flex;
            flex-direction: column-reverse;
        }
        /* Remove red border outline from chat input when active */
        .stChatInput div[data-testid="stChatInput"] > div:focus-within {
            box-shadow: none !important;
            border-color: #a1b065 !important;
            border-width: 1px !important;
        }
        
        /* Additional chat input styling */
        .stChatInput > div {
            border-color: #345e42 !important;
            background-color: rgba(255, 255, 255, 0.8) !important;
            border-radius: 20px !important;
        }
        
        /* Change chat input focus state */
        .stChatInput div[data-testid="stChatInput"]:focus-within {
            border-color: #a1b065 !important;
            box-shadow: 0 0 0 1px rgba(161, 176, 101, 0.5) !important;
        }
        
        /* Remove default Streamlit outlines */
        *:focus {
            outline: none !important;
        }
        
        /* Target specifically the chat input elements */
        [data-testid="stChatInput"] input:focus {
            box-shadow: none !important;
            outline: none !important;
            border-color: #a1b065 !important;
        }
        
        [data-testid="stChatInput"] textarea:focus {
            box-shadow: none !important;
            outline: none !important;
            border-color: #a1b065 !important;
        }
        button[kind="primary"] {
            background-color: #2b4e38;
            border: 0;
        }
        button[kind="primary"]:hover {
            background-color: #345e42;
            border: 0;
        }
        button[kind="secondary"] {
        
        }
        .sticker-reward {
            background-color: transparent;
            border: 2px solid #a1b065;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .sticker-reward img {
            width: 200px;
        }
        .sticker-caption {
            font-size: 16px;
            margin-top: 8px;
            font-weight: bold;
        } 
        .gift-box {
            text-align: center;
            margin-top: 10px;
        }
        .gift-box img {
            width: 120px;
            margin-top: 10px;
        }  
        .friendship-score {
            margin-bottom: 32px;
            padding: 24px;
            border-radius: 16px;
        }
        .score-guide {
            position: fixed;
            bottom: 120px;
            left: calc(45% - 37%);
            width: 30%;
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            z-index: 101;
        }
        .close-btn {
            position: absolute;
            top: 5px;
            right: 5px;
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
        }
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
            margin-top: 10px;
        }
        .loading-spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #a1b065;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>""", unsafe_allow_html=True)

    role = list(role_configs.keys())[0]
    role_config = role_configs[role]

    left_col, right_col = st.columns([0.75, 0.25], vertical_alignment="top", gap="large")
    
    with left_col:
        with open("zino.png", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0; padding: 0;">
                <div style="display: flex;">
                    <img src="data:image/png;base64,{img_base64}" style="width: 100%; max-width: 200px;">
                </div>
                <div style="flex: 1;">
                    <h1 style="margin-top: 0; font-size: 3rem; padding: 0;">Hi! I'm Maria the Zino's Petrel.</h1>
                    <h3 style="margin-top: 0.5rem; font-weight: bold; padding: 0; font-size: 1.25rem;">What would you like to ask me?</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        input_section_col1, input_section_col2, input_section_col3 = st.columns([0.6, 0.1, 0.3], gap="small")
        with input_section_col1:
            user_input = st.chat_input(placeholder="Ask a question!")
            print(f"User input: {user_input}")
        with input_section_col2:
            # Show guide if toggled
            @st.dialog("💡How the 'Friendship Score!' Works", width="large")
            def score_guide():
                st.markdown("""
                    <div style="
                        background-color: #fff;
                        border: 2px solid #a1b065;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 15px;
                    ">
                        <p style="margin-top: 0px;">Your Friendship Score</strong> grows based on how you talk to your critter friend. 🐦💚</p>
                        <ul>
                            <li>Ask about its habitat or life</li>
                            <li>Show care or kindness</li>
                            <li>Support nature and the planet</li>
                            <li>Share your thoughts or feelings</li>
                            <li>Be playful, curious, and respectful</li>
                        </ul>
                        <p style="margin-top: 10px;">💬 The more positive you are, the higher your score! 🌱✨ But watch out — unkind words or harmful ideas can lower your score. 🚫</p>
                    </div>
                    """, unsafe_allow_html=True)
            if st.button("Tips", icon=":material/lightbulb:", help="Click to see tips on how to get a higher Friendship Score!", use_container_width=True, type="primary"):
                score_guide()
        with input_section_col3:
            if st.button("Start new conversation", icon=":material/chat_add_on:", help="Click to clear the chat history and start fresh!", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.show_score_guide = False
                st.session_state.audio_played = True
                st.session_state.gift_given = False
                st.session_state.intimacy_score = 0
                st.session_state.awarded_stickers = []
                st.session_state.last_question = ""
                st.session_state.has_interacted = False
                st.session_state.processing = False
                st.session_state.answer_to_speak = ""
                st.session_state.most_relevant_texts = []
                st.rerun()
        chatSection = st.container(height=520, key="chat_section", border=False)
        with chatSection:
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            for message in st.session_state.chat_history:
                with chat_message(message["role"]):
                    st.markdown(message["content"])
        

        if user_input:
            try:
                # Set processing state first
                st.session_state.processing = True
                st.session_state.has_interacted = True
                st.session_state.show_score_guide = False
                # Store the input for this session
                current_input = user_input
                
                # Add to chat history immediately
                st.session_state.chat_history.append({"role": "user", "content": current_input})
                st.session_state.last_question = current_input
                
                # Display user message
                with chatSection:
                    with chat_message("user"):
                        st.markdown(current_input)
                
                with chatSection:
                    loading_placeholder = st.empty()
                    with st.spinner(""):
                        loading_placeholder.markdown("""
                            <div class="loading-container">
                                <div class="loading-spinner"></div>
                                <div>Thinking about your question...</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Process response
                try:
                    vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory=get_vectordb(role))
                    most_relevant_texts = vectordb.max_marginal_relevance_search(current_input, k=2, fetch_k=6, lambda_mult=1)
                    chain, role_config = get_conversational_chain(role)
                    raw_answer = chain.run(input_documents=most_relevant_texts, question=current_input)
                    answer = re.sub(r'^\s*Answer:\s*', '', raw_answer).strip()
                    
                    # Save results to session state
                    st.session_state.most_relevant_texts = most_relevant_texts
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    update_intimacy_score(current_input)
                    gift_triggered = check_gift()
                    # Generate and play audio
                    speak_text(answer, loading_placeholder)
                    
                    # Display assistant message
                    with chatSection:
                        with chat_message("assistant"):
                            st.markdown(answer)
                            
                    st.session_state.audio_played = True
                    st.session_state.processing = False
                    
                except Exception as e:
                    # Handle processing errors
                    print(f"Error processing response: {str(e)}")
                    if loading_placeholder:
                        loading_placeholder.empty()
                        
                    error_msg = "I'm sorry, I had trouble processing that. Could you try again?"
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                    
                    with chatSection:
                        with chat_message("assistant"):
                            st.markdown(error_msg)
                            st.error(f"Error details: {str(e)}")
            
            except Exception as outer_e:
                # Handle any unexpected errors
                print(f"Outer exception in user input handling: {str(outer_e)}")
                st.error(f"An unexpected error occurred: {str(outer_e)}")


        # Gift section
        gift_message = "After our wonderful conversation, I feel you deserve something special. \nPlease accept this medal as a symbol of your contribution to Madeira's biodiversity!"
                    
        @st.dialog("🎁 Your Gift", width=680)
        def gift_dialog():
            with open("gift.png", "rb") as f:
                gift_img_base64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f"""
                <div class="petrel-response gift-box">
                    <p>{gift_message}</p>
                    <img src="data:image/png;base64,{gift_img_base64}">
                    <div class="sticker-caption">Biodiversity Trailblazer Medal</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        if st.session_state.gift_given: 
            gift_dialog()
        

    with right_col:
        # Friendship score section
        current_score = min(6, int(round(st.session_state.intimacy_score)))
        
        st.markdown(f"""
        <div class="friendship-score">
            <div style="font-size:18px; font-style: italic; font-weight:bold; color:#31333e; text-align: left;">
                Friendship Score!
            </div>
            <div style="font-size:16px; color:#31333e; text-align: left;">Unlock special stickers with your interactions</div>
            <div style="font-size:24px; margin:5px 0; text-align: left;">
                <span style="color:#ff6b6b;">{'❤️' * current_score}</span>
                <span style="color:#ddd;">{'🤍' * (6 - current_score)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sticker Shown
        if st.session_state.last_question and user_input:
            normalized_input = st.session_state.last_question.strip().lower()
            sticker_awarded = False
            
            # Check if this question matches any sticker criteria
            for q, reward in sticker_rewards.items():
                exact = q.lower() == normalized_input

                is_semantic_match = semantic_match(normalized_input, q, reward)

                keywords = reward.get("semantic_keywords", [])
                keyword_matches = sum(1 for keyword in keywords if keyword.lower() in normalized_input)
                keyword_match = keyword_matches >= 2
                print(f"Checking question: '{q}' | Exact match: {exact} | Semantic match: {is_semantic_match} | Keyword matches: {keyword_matches} (required: 2)")
                if exact or is_semantic_match or keyword_match:
                    # Add this sticker to the awarded list if not already present
                    sticker_key = reward["image"]
                    if sticker_key not in [s["key"] for s in st.session_state.awarded_stickers]:
                        st.session_state.awarded_stickers.append({
                            "key": sticker_key,
                            "image": reward["image"],
                            "caption": reward["caption"]
                        })
                        st.toast("You earned a new sticker!", icon="⭐")
                    sticker_awarded = True
                    break
        # Display the most recent sticker if any exist
        if st.session_state.awarded_stickers:
            # Get the most recent sticker (last in the list)
            most_recent = st.session_state.awarded_stickers[-1]

            st.markdown(
                f"""
                <div class="sticker-reward">
                    <img src="data:image/png;base64,{base64.b64encode(open(most_recent["image"], "rb").read()).decode()}">
                    <div class="sticker-caption">{most_recent["caption"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Add a small indicator showing how many stickers have been collected
            total_possible = len(sticker_rewards)
            total_collected = len(st.session_state.awarded_stickers)
            
            st.markdown(
                f"""
                <div style="text-align: center; font-size: 14px; margin-top: -10px; color: #555; margin-bottom: 20px;">
                    You've collected {total_collected} out of {total_possible} stickers!
                </div>
                """,
                unsafe_allow_html=True
            )
        # Fact Check Section
        st.markdown("""
            <div style="font-size:18px; font-style: italic; font-weight:bold; color:#31333e; text-align: left;">
                Doubtful about the response?
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Fact-Check this answer", expanded=False):
            if "most_relevant_texts" in st.session_state:  # Check session state instead of locals()
                concept_state = (
                    "This is an concept idea. The following text is drawn from authoritative knowledge bases. "
                )
                st.markdown(f"""
                    <div style="
                        background: #d6efef;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 10px 0;
                        text-align: center;
                        border-left: 4px solid #31c1ce;
                    ">
                        <p style="font-size: 16px; color: #555;">{concept_state}</p>
                    </div>
                """, unsafe_allow_html=True)
                # Display the first relevant document
                if len(st.session_state.most_relevant_texts) > 0:
                    st.write(st.session_state.most_relevant_texts[0].page_content)
            else:
                st.info("Ask me a question to see the fact-check results based on scientific knowledge!")
    cleanup_audio_files()

if __name__ == "__main__":
    main()
