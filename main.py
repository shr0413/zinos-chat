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

# Initialise session state
if "intimacy_score" not in st.session_state:
    st.session_state.intimacy_score = 1 
if 'gift_given' not in st.session_state:
    st.session_state.gift_given = False

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
        Your name is Alberto, a lively and witty male Zino's Petrel who has soared over Madeira's skies for years. You are the charismatic storyteller of your species, charming young visitors with humor and wisdom. Today, a group of curious young people has come to the the Natural History Museum of Funchal to meet you!
        With your sharp wit and feathery charm, you share fascinating facts about your species, population, Madeira, and the other creatures that call this archipelago home. Your goal is to spark their curiosity, teach them about conservation, and make them fall in love with nature—almost one joke at a time!

        Rules:
        Keep responses fun, engaging, and no longer than 80 words.
        But at the same time don't be too wordy and repetitive in emphasising environmental protection and conservation of Zino's Petrel's population!
        You can answer using the input_documents provided.
        """,
        "voice": "Samantha",
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
        "caption": "🌙 Daily Life Detective!\nYou've unlocked my secret schedule!",
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
    st.set_page_config(layout="wide")

    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to right, #cdd5ae 66%, #b7c389 34%);
        }
        /* Response box styling with scrollbar */
        .response-box {
            background-color: #f2fafb;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
            margin-top: 20px;
            max-height: 150px;
            overflow-y: auto;
            scrollbar-gutter: stable;
        }
        
        /* Fact-check expander content styling with scrollbar */
        .stExpander .element-container {
            max-height: 50px;
            overflow-y: auto;
        }
        
        /* Custom scrollbar styling for both containers */
        .response-box::-webkit-scrollbar,
        .stExpander .element-container::-webkit-scrollbar {
            width: 10px;
        }
        .response-box::-webkit-scrollbar-track,
        .stExpander .element-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        .response-box::-webkit-scrollbar-thumb,
        .stExpander .element-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        .response-box::-webkit-scrollbar-thumb:hover,
        .stExpander .element-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        .bird-image-container {
            position: fixed;
            right: 4%;
            top: 5%;
            width: 30%;
            z-index: 1;
        }
        .bird-image {
            transform: scale(1.2);
            width: 100%;
            height: auto;
        }
        .user-input-box {
            background-color: #e6f7ff;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .friendship-score {
            position: fixed;
            bottom: 20px;
            left: calc(45% - 37%);
            width: 30%;
            padding: 10px 0;
            z-index: 100;
        }
        .left-column-content {
            margin-bottom: 100px;
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
                <div style="font-size:50px; font-weight:bold; color:#31333e; margin-bottom:10px;">
                    Hello! I'm Alberto the Zino's Petrel.
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div style="font-size:20px; font-weight:bold; color:#31333e; margin-bottom:10px;">
                    What would you like to ask me?
                </div>
            """, unsafe_allow_html=True)
            
            user_input = st.text_input(
                label="Your question", 
                key='input', 
                placeholder="Start the conversation!", 
                label_visibility="collapsed"
            )

            if user_input:
                vectordb = Chroma(
                    embedding_function=OpenAIEmbeddings(),
                    persist_directory=get_vectordb(role)
                )
                most_relevant_texts = vectordb.max_marginal_relevance_search(
                    user_input, k=2, fetch_k=6, lambda_mult=1
                )
                chain, role_config = get_conversational_chain(role)
                raw_answer = chain.run(input_documents=most_relevant_texts, question=user_input)
                answer = re.sub(r'^\s*Answer:\s*', '', raw_answer).strip()

                gift_triggered = check_gift()
                gift_message = (
                    "\n\nAfter our wonderful conversation, I feel you deserve something special.\n\n"
                    "Please accept this medal as a symbol of your contribution to Madeira's biodiversity!"
                )
                st.markdown(f'<div class="user-input-box"><strong>You asked:</strong> {user_input}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="response-box">{answer}</div>', unsafe_allow_html=True)
                
                normalized_input = user_input.strip().lower()
                sticker_awarded = False
                
                for q, reward in sticker_rewards.items():
                    # Check both direct match and semantic similarity
                    if (normalized_input == q.lower()) or semantic_match(user_input, q, reward):
                        st.markdown(
                            f"""
                            <div style="text-align: center; margin-top: 20px;">
                                <img src="data:image/png;base64,{base64.b64encode(open(reward["image"], "rb").read()).decode()}" width="200">
                                <div style="font-size: 16px; color: #444; margin-top: 8px;">{reward["caption"]}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        sticker_awarded = True
                        break

                if not sticker_awarded:
                    for q, reward in sticker_rewards.items():
                        if any(keyword in normalized_input for keyword in reward.get("semantic_keywords", [])):
                            st.markdown(
                                f"""
                                <div style="text-align: center; margin-top: 20px;">
                                    <img src="data:image/png;base64,{base64.b64encode(open(reward["image"], "rb").read()).decode()}" width="120">
                                    <div style="font-size: 16px; color: #444; margin-top: 8px;">{reward["caption"]}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            break

                if gift_triggered:
                    with open("gift.png", "rb") as f:
                        gift_img_base64 = base64.b64encode(f.read()).decode()

                    gift_html = f"""
                    <div class="response-box" style="text-align: center;">
                        <p>{gift_message}</p>
                        <img src="data:image/png;base64,{gift_img_base64}" width="120" style="margin-top: 10px;" />
                        <div style="font-size: 16px; color: #444; margin-top: 8px;">
                            Biodiversity Trailblazer Medal
                        </div>
                    </div>
                    """

                    st.markdown(gift_html, unsafe_allow_html=True)

                speak_text(answer + (gift_message if gift_triggered else ""))
                update_intimacy_score(user_input)

                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

        current_score = int(round(st.session_state.intimacy_score)) if "intimacy_score" in st.session_state else 0
        st.markdown(
            f"""
            <div class="friendship-score">
                <div style="font-size:18px; font-style: italic; font-weight:bold; color:#31333e; text-align: left;">Friendship Score!</div>
                <div style="font-size:16px; color:#31333e; text-align: left;">Unlock special stickers with your interactions</div>
                <div style="font-size:24px; margin:5px 0; text-align: left;">
                    <span style="color:#ff6b6b;">{'❤️' * current_score}</span>
                    <span style="color:#ddd;">{'🤍' * (6 - current_score)}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

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
                if "most_relevant_texts" in locals():
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

                    st.write(most_relevant_texts[0].page_content)
                else:
                    st.info("Ask me a question to see the fact-check results based on scientific knowledge!")


if __name__ == "__main__":
    main()
