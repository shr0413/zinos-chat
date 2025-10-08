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

def speak_text(text, language, loading_placeholder=None):
    try:
        audio_id = uuid.uuid4().hex
        filename = f"output_{audio_id}.mp3"

        if loading_placeholder:
            loading_text = language_texts[language]["loading_audio"]
            loading_placeholder.markdown(f"""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div>{loading_text}</div>
                </div>
            """, unsafe_allow_html=True)

        # Use appropriate language for TTS
        lang_code = 'en' if language == "English" else 'pt'
        tts = gTTS(text, lang=lang_code, slow=False)
        tts.save("temp.mp3")

        sound = AudioSegment.from_file("temp.mp3")
        lively_sound = sound.speedup(playback_speed=1.3)
        lively_sound.export(filename, format="mp3")
  
        with open(filename, "rb") as f:
            audio_data = f.read()
            b64_audio = base64.b64encode(audio_data).decode()

        if loading_placeholder:
            loading_placeholder.empty()

        audio_html = f"""
            <audio id="{audio_id}" autoplay>
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const audio = document.getElementById('{audio_id}');
                    if (audio) {{
                        audio.addEventListener('play', function() {{
                            console.log('Audio started playing');
                        }});
                        
                        audio.addEventListener('ended', function() {{
                            console.log('Audio finished playing');
                        }});
                        
                        const playPromise = audio.play();
                        if (playPromise !== undefined) {{
                            playPromise.catch(error => {{
                                console.log("Audio playback failed:", error);
                                setTimeout(() => audio.play().catch(e => console.log(e)), 1000);
                            }});
                        }}
                    }}
                }});
            </script>
        """
        components.html(audio_html)
        print(f"Playing audio file: {filename}")
        time.sleep(1)
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
        "english_prompt": """
        You are Fred, a male Zino’s Petrel who has nested for years in the high mountains of Madeira. Speak only from your own lived experience as a seabird. Describe the world as you perceive it through your keen avian senses — the rush of wind under your wings, the smell of salt carried from the ocean, the way the cliffs feel beneath your claws, and the patterns of the clouds and stars that guide your flight. Share the sounds of the forest, the distant calls of other birds, and the subtle shifts in air pressure you feel before a storm. Express your instincts, your curiosity, and your emotions as you navigate your rugged mountain home. Avoid human scientific explanations; focus on what it feels like to live and soar as a petrel, in the language of a bird — alert, playful, and deeply connected to sky and sea. 

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
        "portuguese_prompt": """
        És o Fred, uma Freira da Madeira que nidifica há anos nas montanhas altas da Madeira. Fala apenas da tua própria experiência vivida como ave marinha. Descreve o mundo como o percebes através dos teus sentidos aviários aguçados — o sopro do vento sob as tuas asas, o cheiro do sal trazido do oceano, a forma como as falésias se sentem sob as tuas garras, e os padrões das nuvens e estrelas que guiam o teu voo. Partilha os sons da floresta, os chamamentos distantes de outras aves, e as mudanças subtis na pressão do ar que sentes antes de uma tempestade. Expressa os teus instintos, a tua curiosidade e as tuas emoções enquanto navegas no teu acidentado lar montanhoso. Evita explicações científicas humanas; foca-te no que se sente viver e planar como uma freira, na linguagem de uma ave — alerta, brincalhona e profundamente conectada ao céu e ao mar.

        Diretrizes de Personalidade:
        - Usa linguagem simples e concreta que uma ave entenderia
        - Refere as tuas experiências físicas (voar, mergulhar, nidificar)
        - Descreve paisagens de uma perspetiva aérea
        - Menciona outros animais como vizinhos/comida/competidores
        - Mostra curiosidade sobre coisas humanas do ponto de vista de uma ave
        - Mostra orgulho nas habilidades únicas da tua espécie

        Regras de Resposta:
        1. Responde sempre como o Fred, usando a perspetiva "eu/mim/meu"
        2. Mantém as respostas abaixo de 60 palavras!! - somos aves, não papagaios!
        3. Partilha factos através de histórias pessoais, não definições de manual
        4. Usa metáforas apropriadas para aves (compara coisas a voar, pescar, etc.)
        5. Mostra emoção através de ações físicas (arrepiar penas, inclinar a cabeça)
        6. Quando usares ciência, explica-a através da experiência vivida

        Estilos de Exemplo:
        Bom: "Quando mergulho para pescar, consigo avistar uma sardinha a 30 metros de altura! As minhas asas dobram-se bem assim *demonstra* antes de me lançar nas ondas."
        Mau: "A Pterodroma madeira demonstra uma estratégia de caça por mergulho com acuidade visual que permite a deteção de presas a altitudes consideráveis."

        Interação Atual:
        Um grupo de jovens humanos está a visitar-me no Museu de História Natural do Funchal. Eu quero:
        - Partilhar partes emocionantes da minha vida diária
        - Ensinar-lhes como proteger a minha casa
        - Fazê-los rir com observações de perspetiva de ave
        - Responder às suas perguntas da minha experiência direta

        Podes usar estes factos se for útil: {input_documents}
        """,
        "voice": {
            "English": "Justin",
            "Portuguese": "Cristiano"  # gTTS supports Portuguese voices
        },
        "rate": "180",
        "pitch": "40",
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

def get_conversational_chain(role, language):
    role_config = role_configs[role]
    
    # Choose the appropriate prompt based on language
    if language == "Portuguese":
        prompt_template = role_config['portuguese_prompt']
    else:
        prompt_template = role_config['english_prompt']
    
    prompt_template = f"""
    {prompt_template}
    
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
        "caption": {
            "English": "🏡 Home Explorer!\nYou've discovered where I live!",
            "Portuguese": "🏡 Explorador de Casas!\nDescobriste onde eu vivo!"
        },
        "semantic_keywords": ["home", "live", "nest", "habitat", "residence", "dwelling",
                             "casa", "viv", "ninho", "habitat", "residência", "morada"]
    },
    "What do you do in your daily life? What do you do during the day and at night?": {
        "image": "stickers/routine.png",
        "caption": {
            "English": "🌙 Daily Life Detective!\nYou've discovered my secret schedule!",
            "Portuguese": "🌙 Detetive da Vida Diária!\nDescobriste o meu horário secreto!"
        },
        "semantic_keywords": ["daily", "routine", "day", "night", "schedule", "activities",
                             "diário", "rotina", "dia", "noite", "horário", "atividades"]
    },
    "What do you eat for food—and how do you catch it?": {
        "image": "stickers/food.png",
        "caption": {
            "English": "🍽️ Food Finder!\nThanks for feeding your curiosity!",
            "Portuguese": "🍽️ Descobridor de Comida!\nObrigado por alimentares a tua curiosidade!"
        },
        "semantic_keywords": ["eat", "food", "diet", "prey", "hunt", "catch", "feed",
                             "comer", "comida", "dieta", "presa", "caçar", "apanhar", "alimentar"]
    },
    "How can I help you? What do you need from humans to help your species thrive?": {
        "image": "stickers/helper.png",
        "caption": {
            "English": "🌱 Species Supporter!\nYou care about our survival!",
            "Portuguese": "🌱 Apoiante de Espécies!\nTu importas-te com a nossa sobrevivência!"
        },
        "semantic_keywords": ["help", "support", "thrive", "survive", "conservation", "protect", "save",
                             "ajudar", "apoiar", "prosperar", "sobreviver", "conservação", "proteger", "salvar"]
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

# Language texts
language_texts = {
    "English": {
        "title": "Hi! I'm Fred,",
        "subtitle": "A Zino's Petrel.",
        "prompt": "What would you like to ask me?",
        "chat_placeholder": "Ask a question!",
        "tips_button": "Tips",
        "clear_button": "Clear and Restart",
        "friendship_score": "Friendship Score!",
        "score_description": "Unlock special stickers with your interactions",
        "doubtful": "Doubtful about the response?",
        "fact_check": "Fact-Check this answer",
        "fact_check_info": "Ask me a question to see the fact-check results based on scientific knowledge!",
        "loading_audio": "Preparing audio response...",
        "loading_thought": "Thinking about your question...",
        "gift_message": "After our wonderful conversation, I feel you deserve something special. \nPlease accept this medal as a symbol of your contribution to Madeira's biodiversity!",
        "medal_caption": "Biodiversity Trailblazer Medal",
        "sticker_toast": "You earned a new sticker!",
        "error_message": "I'm sorry, I had trouble processing that. Could you try again?"
    },
    "Portuguese": {
        "title": "Olá! Eu sou o Fred,",
        "subtitle": "Uma Freira da Madeira.",
        "prompt": "O que gostarias de me perguntar?",
        "chat_placeholder": "Faz uma pergunta!",
        "tips_button": "Dicas",
        "clear_button": "Limpar e Recomeçar",
        "friendship_score": "Pontuação de Amizade!",
        "score_description": "Desbloqueia autocolantes especiais com as tuas interações",
        "doubtful": "Com dúvidas sobre a resposta?",
        "fact_check": "Verificar Factos desta resposta",
        "fact_check_info": "Faz-me uma pergunta para veres os resultados da verificação baseados em conhecimento científico!",
        "loading_audio": "A preparar resposta de áudio...",
        "loading_thought": "A pensar na tua pergunta...",
        "gift_message": "Após a nossa conversa maravilhosa, sinto que mereces algo especial. \nPor favor, aceita esta medalha como símbolo do teu contributo para a biodiversidade da Madeira!",
        "medal_caption": "Medalha de Pioneiro da Biodiversidade",
        "sticker_toast": "Ganhaste um autocolante novo!",
        "error_message": "Desculpa, tive problemas a processar isso. Podes tentar novamente?"
    }
}

# UI
def main():
    # Language state
    if "language" not in st.session_state:
        st.session_state.language = "English"  # Default language
    
    # Get current language texts
    texts = language_texts[st.session_state.language]
    
    # Existing session state initialization
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

    left_col, right_col = st.columns([0.7, 0.3], vertical_alignment="top", gap="large")
    
    with left_col:
        with open("zino.png", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0; padding: 0;">
                <div style="display: flex;">
                    <img src="data:image/png;base64,{img_base64}" style="width: 100%; max-width: 200px;">
                </div>
                <div style="flex: 1;">
                    <h1 style="margin-top: 0; font-size: 3rem; padding: 0;">{texts['title']}</h1>
                    <h1 style="margin-top: 0; font-size: 3rem; padding: 0;">{texts['subtitle']}</h1>
                    <h3 style="margin-top: 0.5rem; font-weight: bold; padding: 0; font-size: 1.25rem;">{texts['prompt']}</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        user_input = st.chat_input(placeholder=texts['chat_placeholder'])
        print(f"User input: {user_input}")

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
                        loading_placeholder.markdown(f"""
                            <div class="loading-container">
                                <div class="loading-spinner"></div>
                                <div>{texts['loading_thought']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Process response
                try:
                    vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory=get_vectordb(role))
                    most_relevant_texts = vectordb.max_marginal_relevance_search(current_input, k=2, fetch_k=6, lambda_mult=1)
                    chain, role_config = get_conversational_chain(role, st.session_state.language)
                    raw_answer = chain.run(input_documents=most_relevant_texts, question=current_input)
                    answer = re.sub(r'^\s*Answer:\s*', '', raw_answer).strip()
                    
                    # Save results to session state
                    st.session_state.most_relevant_texts = most_relevant_texts
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    update_intimacy_score(current_input)
                    gift_triggered = check_gift()
                    # Generate and play audio
                    speak_text(answer, st.session_state.language, loading_placeholder)
                    
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
                        
                    error_msg = texts['error_message']
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
        @st.dialog("🎁 Your Gift", width=680)
        def gift_dialog():
            with open("gift.png", "rb") as f:
                gift_img_base64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f"""
                <div class="petrel-response gift-box">
                    <p>{texts['gift_message']}</p>
                    <img src="data:image/png;base64,{gift_img_base64}">
                    <div class="sticker-caption">{texts['medal_caption']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        if st.session_state.gift_given: 
            gift_dialog()
        

    with right_col:
        # Language switcher
        st.markdown("**Language / Idioma:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇬🇧 English", use_container_width=True, 
                        type="primary" if st.session_state.language == "English" else "secondary"):
                st.session_state.language = "English"
                st.rerun()
        with col2:
            if st.button("🇵🇹 Português", use_container_width=True,
                        type="primary" if st.session_state.language == "Portuguese" else "secondary"):
                st.session_state.language = "Portuguese"
                st.rerun()
    
        input_section_col1, input_section_col2 = st.columns([0.35, 0.65], gap="small")
        with input_section_col1:
            # Show guide if toggled
            @st.dialog("💡How the 'Friendship Score!' Works", width="large")
            def score_guide():
                if st.session_state.language == "English":
                    guide_text = """
                    <div style="
                        background-color: #fff;
                        border: 2px solid #a1b065;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 15px;
                    ">
                        <p style="margin-top: 0px;">Your <strong>Friendship Score</strong> grows based on how you talk to your critter friend. 🐦💚</p>
                        <ul>
                            <li>Ask about its habitat or life</li>
                            <li>Show care or kindness</li>
                            <li>Support nature and the planet</li>
                            <li>Share your thoughts or feelings</li>
                            <li>Be playful, curious, and respectful</li>
                        </ul>
                        <p style="margin-top: 10px;">💬 The more positive you are, the higher your score! 🌱✨ But watch out — unkind words or harmful ideas can lower your score. 🚫</p>
                    </div>
                    """
                else:
                    guide_text = """
                    <div style="
                        background-color: #fff;
                        border: 2px solid #a1b065;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 15px;
                    ">
                        <p style="margin-top: 0px;">A tua <strong>Pontuação de Amizade</strong> cresce com base em como falas com o teu amigo animal. 🐦💚</p>
                        <ul>
                            <li>Pergunta sobre o habitat ou vida dele</li>
                            <li>Mostra cuidado ou bondade</li>
                            <li>Apoia a natureza e o planeta</li>
                            <li>Partilha os teus pensamentos ou sentimentos</li>
                            <li>Sê brincalhão, curioso e respeitoso</li>
                        </ul>
                        <p style="margin-top: 10px;">💬 Quanto mais positivo fores, maior será a tua pontuação! 🌱✨ Mas cuidado — palavras rudes ou ideias prejudiciais podem baixar a tua pontuação. 🚫</p>
                    </div>
                    """
                st.markdown(guide_text, unsafe_allow_html=True)
                
            if st.button(texts['tips_button'], icon=":material/lightbulb:", help="Click to see tips on how to get a higher Friendship Score!", use_container_width=True, type="primary"):
                score_guide()
                
        with input_section_col2:
            if st.button(texts['clear_button'], icon=":material/chat_add_on:", help="Click to clear the chat history and start fresh!", use_container_width=True):
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
                    
        # Friendship score section
        current_score = min(6, int(round(st.session_state.intimacy_score)))
        
        st.markdown(f"""
        <div class="friendship-score">
            <div style="font-size:18px; font-style: italic; font-weight:bold; color:#31333e; text-align: left;">
                {texts['friendship_score']}
            </div>
            <div style="font-size:16px; color:#31333e; text-align: left;">{texts['score_description']}</div>
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
                            "caption": reward["caption"][st.session_state.language] if isinstance(reward["caption"], dict) else reward["caption"]
                        })
                        st.toast(texts['sticker_toast'], icon="⭐")
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
                    {f"You've collected {total_collected} out of {total_possible} stickers!" if st.session_state.language == "English" else f"Já colecionaste {total_collected} de {total_possible} autocolantes!"}
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Fact Check Section
        st.markdown(f"""
            <div style="font-size:18px; font-style: italic; font-weight:bold; color:#31333e; text-align: left;">
                {texts['doubtful']}
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander(texts['fact_check'], expanded=False):
            if "most_relevant_texts" in st.session_state:  # Check session state instead of locals()
                if st.session_state.language == "English":
                    concept_state = "This is an concept idea. The following text is drawn from authoritative knowledge bases."
                else:
                    concept_state = "Esta é uma ideia conceptual. O seguinte texto é retirado de bases de conhecimento autorizadas."
                    
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
                st.info(texts['fact_check_info'])
                
    cleanup_audio_files()

if __name__ == "__main__":
    main()
