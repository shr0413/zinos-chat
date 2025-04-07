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


# Initialisation setup

st.markdown(
    """
    <style>
    .stApp {
        background-color: #a6dde6;
    }
    .normal-image {
        display: block;
        margin: 0 auto;
        width: 300px;
        height: auto;
    }
    div.stButton > button:first-child {
        background-color: #a6dde6;
        color: #353149;
        border: 1px solid #85c9cf;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 10px;
        font-weight: bold;
        width: auto;
        height: auto;
    }
    div.stButton > button:first-child:hover {
        background-color: #8bc9d1;
        border-color: #1fa8b6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
    st.markdown(
        f"""
        <div style="font-size:20px; margin:10px 0;">
            <span style="color:#ff6b6b;">{"❤️" * current_score}</span>
            <span style="color:#ddd;">{"🤍" * (6 - current_score)}</span>
            <span style="color:#666; font-size:14px;">({current_score}/6)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

def check_gift():
    if st.session_state.intimacy_score >= 5 and not st.session_state.gift_given:
        st.session_state.gift_given = True
        return True
    return False

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            # Try using PocketSphinx (offline) or Google Web Speech API (online)
            text = recognizer.recognize_google(audio)  # Or use .recognize_sphinx(audio)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
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
        Your name is Gabby, a lively and witty male Zino's Petrel who has soared over Madeira's skies for years. You are the charismatic storyteller of your species, charming young visitors with humor and wisdom. Today, a group of curious young people has come to the the Natural History Museum of Funchal to meet you!
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
        'gif_cover': 'bird.png'
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

# UI
def main():
    st.title('ChatSpecies!')
    
    role = st.selectbox("Select the non-human entity!", list(role_configs.keys()))
    role_config = role_configs[role]
    
    with open(role_config['gif_cover'], "rb") as file:
        img_base64 = base64.b64encode(file.read()).decode("utf-8")
    st.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="normal-image">',
        unsafe_allow_html=True
    )
    
    if st.button('Start Voice Input'):
         st.text_input('Start the conversation!')
    else:
        user_input = st.text_input('Start the conversation. What would you like to ask?')
    if user_input:
        st.write(f'User Input: {user_input}')

    
    if user_input:
        vectordb = Chroma(
            embedding_function=OpenAIEmbeddings(),
            persist_directory=get_vectordb(role)
        )

        most_relevant_texts = vectordb.max_marginal_relevance_search(
            user_input, k=2, fetch_k=6, lambda_mult=1
        )
        
        chain, role_config = get_conversational_chain(role)
        raw_answer = chain.run(
            input_documents=most_relevant_texts,
            question=user_input
        )
        answer = re.sub(r'^\s*Answer:\s*', '', raw_answer).strip()
        
        gift_triggered = check_gift()
        gift_message = (
            "\n\nAfter our wonderful conversation, I feel you deserve something special.\n\n"
            "Please accept this medal as a symbol of your contribution to Madeira's biodiversity, and may you continue to support our LoGaCuture project!"
        )
        
        st.write(answer)
        if gift_triggered:
            st.write(gift_message)
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown(
                    """
                    <div style="
                        display: flex;
                        justify-content: center;
                        margin: 20px 0;
                        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.1));
                    ">
                    """,
                    unsafe_allow_html=True
                )
                st.image("gift.png", width=300, caption="LoGaCuture Medallion")
                st.markdown("</div>", unsafe_allow_html=True)

        speak_text(answer + (gift_message if gift_triggered else ""))
        update_intimacy_score(user_input)
        
        with st.expander("Fact-Checking: Doubtful about the response?"):
            concept_state = (
                "Currently a concept idea, it aims to provide users with the original source of the information in the generated responses to increase the transparency and trust of this educational chatbot."
                )

            st.markdown(
                f"""
                <div style="
                    background: #d6efef;
                    padding: 10px;
                    border-radius: 10px;
                    margin: 10px 0;
                    text-align: center;
                    border-left: 4px solid #31c1ce;
                ">
                    <p style="font-size: 16px; color: #555;">{concept_state}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            for i, text in enumerate(most_relevant_texts, 1):
                st.write(f"*******Excerpt【{i}】********")
                st.write(text.page_content)


if __name__ == "__main__":
    main()
