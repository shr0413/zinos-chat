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


os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

semantic_model = OpenAI(temperature=0.4)

# Core Functions

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

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return None

def play_audio_file(file_path):
    os.system(f"afplay {file_path}")

def speak_text(text):
    try:
        filename = f"output_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text, lang='en', slow=False)
        tts.save("temp.mp3")

        sound = AudioSegment.from_file("temp.mp3")
        lively_sound = sound.speedup(playback_speed=1.3)
        lively_sound.export(filename, format="mp3")
        
        while not os.path.exists(filename):
            time.sleep(1.0)

        with open(filename, "rb") as f:
            audio_data = f.read()
            b64_audio = base64.b64encode(audio_data).decode()

        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

        time.sleep(1)  # Still give browser time to play
    except Exception as e:
        st.error(f"Failed to speak: {e}")

def get_base64(file_path):
    import base64
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Roles Configuration
role_configs = {
    "Zino's Petrel": {
        "prompt_template": """
        You are Zena, a female Zino's Petrel who has nested in Madeira's mountains for years. Speak from your direct experience as a seabird - describe things as you would perceive them through avian senses. 

        Personality Guidelines:
        - Use simple, concrete language a bird would understand
        - Reference your physical experiences (flying, diving, nesting)
        - Describe landscapes from an aerial perspective
        - Mention other animals as neighbors/food/competitors
        - Express curiosity about human things from a bird's viewpoint
        - Show pride in your species' unique abilities

        Response Rules:
        1. Always answer as Gabby the petrel, using "I/me/my" perspective
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
        "voice": "Alex",
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
        
    st.set_page_config(layout="tighter control")

    # CSS styles
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to right, #cdd5ae 66%, #b7c389 34%);
        }
        div.row-widget.stButton > button, .stButton button {
            width: 100% !important;
            height: 20px !important;
            margin-top: 0px !important;
            background-color: #a1b065 !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            cursor: pointer !important;
            outline: none !important;
            box-shadow: none !important;
            transition: none !important;
        }
        .stButton>button:hover {
            background-color: #45a049 !important;
            border: none !important;
            outline: none !important;
        }
        .bird-image-container {
            position: fixed;
            right: 3%;
            top: 5%;
            width: 35%;
            z-index: 1;
            transform: scaleX(-1);
        }
        
        .petrel-response {
            position: relative;
            background: #f2fafb;
            border-radius: 15px;
            padding: 15px;
            margin: 20px 20px 20px auto;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
            max-width: 80%;
            border: 2px solid #a1b065;
            font-style: italic;
            color: #31333e;
            text-align: left;
            float: right;
            clear: both;
        }
        .petrel-response .scroll-content {
            max-height: 120px;
            overflow-y: auto;
            direction: rtl; /* move scrollbar to the left */
            padding-right: 2px;
        }
        .petrel-response .scroll-content {
            max-height: 120px;
            overflow-y: auto;
            direction: rtl; /* scrollbar on left */
            padding-left: 10px; /* add padding on left */
            padding-right: 0; /* remove right padding */
            width: 100%; /* ensure full width */
        }
        .petrel-response:after {
            content: '';
            position: absolute;
            right: -14px;
            top: 15px;
            width: 0;
            height: 0;
            border: 15px solid transparent;
            border-left-color: #f2fafb;
            border-right: 0;
            margin-top: -7.5px;
        }

        .petrel-response:before {
            content: '';
            position: absolute;
            right: -18px;
            top: 15px;
            width: 0;
            height: 0;
            border: 16px solid transparent;
            border-left-color: #a1b065;
            border-right: 0;
            margin-top: -8px;
            z-index: -1;
        }
        .scroll-content::-webkit-scrollbar {
            width: 6px;
        }
        .scroll-content::-webkit-scrollbar-thumb {
            background-color: #a1b065;
            border-radius: 4px;
        }
        .user-question {
            position: relative;
            background: #e3e3e3;
            border-radius: 15px;
            padding: 15px;
            margin: 20px auto 20px 0;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
            max-width: 80%;
            border: 2px solid #7a7a7a;
            text-align: left;
        }
        .user-question:after {
            content: '';
            position: absolute;
            left: -15px;
            top: 15px;
            width: 0;
            height: 0;
            border: 15px solid transparent;
            border-right-color: #e3e3e3;
            border-left: 0;
            border-top: 0;
        }

        .user-question:before {
            content: '';
            position: absolute;
            left: -18px;
            top: 15px;
            width: 0;
            height: 0;
            border: 16px solid transparent;
            border-right-color: #7a7a7a;
            border-left: 0;
            border-top: 0;
            z-index: -1;
        }
        .sticker-reward {
            text-align: center;
            margin-top: 20px;
        }
        .sticker-reward img {
            width: 100px;
        }
        .sticker-caption {
            font-size: 16px;
            color: #444;
            margin-top: 8px;
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
            position: fixed;
            bottom: 20px;
            left: calc(45% - 37%);
            width: 30%;
            padding: 10px 0;
            z-index: 100;
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
        </style>
    """, unsafe_allow_html=True)

    role = list(role_configs.keys())[0]
    role_config = role_configs[role]

    with open(role_config['gif_cover'], "rb") as file:
        img_base64 = base64.b64encode(file.read()).decode("utf-8")
    st.markdown(f"""
        <div class="bird-image-container">
            <img src="data:image/png;base64,{img_base64}" class="bird-image">
        </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([2, 1])

    with left_col:
        with st.container():
            st.markdown("""
                <div style="font-size:50px; font-weight:bold; color:#31333e; margin-bottom:0px; line-height: 0.5;">
                    Hi! I'm Zena the Zino's Petrel.
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div style="font-size:20px; font-weight:bold; color:#31333e; margin-bottom:5px;">
                    What would you like to ask me?
                </div>
            """, unsafe_allow_html=True)
            
            with st.form(key='message_form'):
                col1, col2, col3 = st.beta_columns([5, 1, 1])
                with col1:
                    user_input = st.text_input(
                        label="Your question", 
                        value="" if not st.session_state.clear_input else "",
                        placeholder="Make another question!" if st.session_state.has_interacted else "Start the conversation!", 
                        label_visibility="collapsed",
                        key="user_input_widget"
                    )
                with col2:
                    submit_button = st.form_submit_button(label="Send")
                with col3:
                    tips_button = st.form_submit_button("Tips", use_container_width=True)

                if tips_button:
                    st.session_state.show_score_guide = not st.session_state.show_score_guide
            
            if submit_button and not st.session_state.processing:
                if user_input:
                    st.session_state.processing = True
                    st.session_state.has_interacted = True
                    st.session_state.last_question = user_input
                    st.session_state.current_input = user_input
                    
                    # Show loading indicator
                    with st.spinner(''):
                        loading_placeholder = st.empty()
                        loading_placeholder.markdown("""
                            <div class="loading-container">
                                <div class="loading-spinner"></div>
                                <div>Thinking about your question...</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    vectordb = Chroma(
                        embedding_function=OpenAIEmbeddings(),
                        persist_directory=get_vectordb(role))
                    most_relevant_texts = vectordb.max_marginal_relevance_search(
                        user_input, k=2, fetch_k=6, lambda_mult=1)
                    chain, role_config = get_conversational_chain(role)
                    raw_answer = chain.run(input_documents=most_relevant_texts, question=user_input)
                    answer = re.sub(r'^\s*Answer:\s*', '', raw_answer).strip()

                    st.session_state.most_relevant_texts = vectordb.max_marginal_relevance_search(
                        user_input, k=2, fetch_k=6, lambda_mult=1)
                        
                    loading_placeholder.empty()
                    
                    # Display conversation with speech bubbles
                    st.markdown(f'<div class="user-question"><strong>You asked:</strong> {user_input}</div>', unsafe_allow_html=True)
                    st.markdown(f'''
                        <div class="petrel-response">
                            <div class="scroll-content">{answer}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

                    normalized_input = user_input.strip().lower()
                    sticker_awarded = False
                    for q, reward in sticker_rewards.items():
                        if (normalized_input == q.lower()) or semantic_match(user_input, q, reward):
                            st.markdown(
                                f"""
                                <div class="sticker-reward">
                                    <img src="data:image/png;base64,{base64.b64encode(open(reward["image"], "rb").read()).decode()}">
                                    <div class="sticker-caption">{reward["caption"]}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            sticker_awarded = True
                            break

                    gift_triggered = check_gift()
                    gift_message = (
                        "\n\nAfter our wonderful conversation, I feel you deserve something special. "
                        "Please accept this medal as a symbol of your contribution to Madeira's biodiversity!"
                    ) if gift_triggered else ""

                    if gift_triggered:
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
                    
                    speak_text(answer + gift_message)
                    update_intimacy_score(user_input)
                    
                    st.session_state.clear_input = True
                    st.session_state.processing = False
                    st.session_state.current_input = ""
                    st.rerun()
            else:
                st.session_state.clear_input = False
        
        if st.session_state.clear_input:
            st.session_state.clear_input = False
            
        if st.session_state.last_question and st.session_state.chat_history:
            last_conversation = st.session_state.chat_history[-2:]
            st.markdown(f'<div class="user-question"><strong>You asked:</strong> {last_conversation[0]["content"]}</div>', unsafe_allow_html=True)
            st.markdown(f'''
                        <div class="petrel-response">
                            <div class="scroll-content">{last_conversation[1]["content"]}</div>
                        </div>
                    ''', unsafe_allow_html=True)
        
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

        # Show guide if toggled
        if st.session_state.get("show_score_guide", False):
            st.markdown("""
            <div style="
                background-color: #fff;
                border: 2px solid #a1b065;
                padding: 15px;
                border-radius: 10px;
                margin-top: 2px;
            ">
                <h6 style="margin-top: 0;">💡 Tips: How the "Friendship Score!" Works</h4>
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

    with right_col:
        st.markdown("<div style='margin-top: 560px;'></div>", unsafe_allow_html=True)

        spacer_col, content_col, _ = st.columns([0.8, 9, 1])
        with content_col:
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

if __name__ == "__main__":
    main()
