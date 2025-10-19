import sys
import os
# import pysqlite3  # Windows/Conda 环境不需要
# sys.modules["sqlite3"] = pysqlite3
from gtts import gTTS
from pydub import AudioSegment
import re
import base64
import subprocess
import speech_recognition as sr
import streamlit as st
import uuid
import time
from tts_utils import speak as tts_speak, cleanup_audio_files as tts_cleanup
from rag_utils import get_rag_instance
from fact_check_utils import generate_fact_check_content
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import Tongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit.components.v1 as components
from st_supabase_connection import SupabaseConnection, execute_query
import hashlib

# 导入统一的Prompt管理模块
from prompts import Prompts

def get_supabase_connection():
    """获取 Supabase 连接（避免缓存问题）"""
    return st.connection("supabase", type=SupabaseConnection)

def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def log_interaction(user_input, ai_response, intimacy_score, is_sticker_awarded, gift_given=False):
    try:
        session_id = get_session_id()
        
        if is_sticker_awarded:
            # Extract sticker type from the image path (e.g., "stickers/home.png" -> "home")
            st.session_state.last_sticker = st.session_state.awarded_stickers[-1]["image"].split("/")[-1].split(".")[0]
        else:
            st.session_state.last_sticker = None

        # Get response analysis data
        response_analysis = {}
        if hasattr(st.session_state, 'last_analysis'):
            response_analysis = st.session_state.last_analysis
            
        # Insert the interaction record
        data = {
            "session_id": session_id,
            "user_msg": user_input,
            "ai_msg": ai_response,
            "ai_name": "Maria the Zino's Petrel",
            "intimacy_score": float(intimacy_score),
            "sticker_awarded": st.session_state.last_sticker,
            "gift_given": gift_given,
            "response_analysis": response_analysis
        }

        conn = get_supabase_connection()
        execute_query(conn.table("interactions").insert(data, count="None"), ttl='0')
        print(f"Logged interaction to Supabase: {session_id}")
        return True
    except Exception as e:
        print(f"Failed to log interaction: {str(e)}")
        return False

# 配置 Qwen API Key
dashscope_key = os.getenv("DASHSCOPE_API_KEY") or st.secrets.get("DASHSCOPE_API_KEY")
os.environ["DASHSCOPE_API_KEY"] = dashscope_key

semantic_model = Tongyi(
    model_name=os.getenv("QWEN_MODEL_NAME", "qwen-turbo"),
    temperature=0.4,
    dashscope_api_key=dashscope_key
)

# Main Function
def update_intimacy_score(response_text):
    """
    更新亲密度评分（Friendship Score）
    
    使用Prompts模块统一管理的评分标准
    """
    if not hasattr(st.session_state, 'intimacy_score'):
        st.session_state.intimacy_score = 1

    # 从Prompts模块获取评分标准
    positive_criteria = Prompts.INTIMACY_POSITIVE_CRITERIA
    negative_criteria = Prompts.INTIMACY_NEGATIVE_CRITERIA
    
    # 优化：合并两次评分为一次调用，提升速度
    model_scoring = Tongyi(
        model_name=os.getenv("QWEN_MODEL_NAME", "qwen-turbo"),
        temperature=0.1,
        dashscope_api_key=dashscope_key
    )
    
    # 使用Prompts模块生成评估prompt
    combined_prompt = Prompts.get_intimacy_evaluation_prompt(response_text, "combined")
    
    # 使用 invoke() 替代弃用的 __call__()
    combined_evaluation = model_scoring.invoke(combined_prompt)
    evaluation_positive = combined_evaluation
    evaluation_negative = combined_evaluation

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

    # Store the analysis results for logging to Supabase
    st.session_state.last_analysis = {
        "positive_criteria": evaluation_positive,
        "negative_criteria": evaluation_negative
    }
    
    print(f"AI Evaluation: {evaluation_positive} + {evaluation_negative}")
    print(f"Updated Intimacy Score: {st.session_state.intimacy_score}")

    current_score = int(round(st.session_state.intimacy_score))

def check_gift():
    if st.session_state.intimacy_score >= 6 and not st.session_state.gift_given and not st.session_state.gift_shown:
        st.session_state.gift_given = True
        return True
    return False

def play_audio_file(file_path):
    os.system(f"afplay {file_path}")

def speak_text(text, loading_placeholder=None):
    """
    智能 TTS 函数 - 使用 Qwen TTS 优先，gTTS 降级
    """
    try:
        # 显示加载指示器
        if loading_placeholder:
            loading_placeholder.markdown("""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div>🎤 生成语音中...</div>
                </div>
            """, unsafe_allow_html=True)

        # 获取用户选择的音色（如果有）
        voice = st.session_state.get('tts_voice', 'Cherry')
        
        # 使用智能 TTS（Qwen 优先，自动降级）
        success, result, method = tts_speak(text, voice=voice, timeout=10)
        
        # 清除加载指示器
        if loading_placeholder:
            loading_placeholder.empty()
        
        if success:
            # 显示音频播放器
            components.html(result, height=0)
            print(f"[TTS] ✅ Audio generated using {method}")
        else:
            # TTS 失败
            st.warning(f"⚠️ 语音生成失败: {result}")
            print(f"[TTS] ❌ {result}")
    
    except Exception as e:
        if loading_placeholder:
            loading_placeholder.empty()
        st.error(f"TTS error: {e}")
        print(f"[TTS] ❌ Exception: {e}")

def cleanup_audio_files():
    """清理临时音频文件"""
    tts_cleanup()

def get_base64(file_path):
    import base64
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Roles Configuration
# 角色prompt已移至prompts.py统一管理
role_configs = {
    "Zino's Petrel": {
        "voice": {
            "English": "Cherry",
            "Portuguese": "Cherry"
        },
        'intro_audio': 'intro5.mp3',
        'persist_directory': 'db5_qwen',
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

def get_conversational_chain(role, language="English", vectordb=None):
    """
    创建带有对话记忆的 RAG Chain
    
    Args:
        role: 角色配置名称
        language: 语言选择 (English/Portuguese)
        vectordb: ChromaDB 向量数据库实例
    
    Returns:
        ConversationalRetrievalChain: 带记忆的对话检索链
        dict: 角色配置
    """
    role_config = role_configs[role]
    
    # 从Prompts模块获取角色prompt（已移至prompts.py统一管理）
    base_prompt = Prompts.get_role_prompt(language)
    
    # 创建 LLM
    model = Tongyi(
        model_name=os.getenv("QWEN_MODEL_NAME", "qwen-turbo"),
        temperature=0,
        dashscope_api_key=dashscope_key
    )
    
    # 创建 Retriever（从 vectordb）
    retriever = vectordb.as_retriever(
        search_type="mmr",  # 使用最大边际相关性
        search_kwargs={
            "k": 3,  # 返回3个最相关文档
            "fetch_k": 9,  # 从9个候选中选择
            "lambda_mult": 0.3  # 平衡相关性和多样性
        }
    )
    
    # 创建对话记忆（保留最近5轮对话）
    memory = ConversationBufferWindowMemory(
        k=5,  # 保留最近5轮对话
        memory_key="chat_history",  # LangChain 标准 key
        return_messages=True,  # 返回消息对象而不是字符串
        output_key="answer"  # ConversationalRetrievalChain 的输出key
    )
    
    # 自定义提示词（用于文档合成）
    # Prompts模块中的角色prompt已使用{context}占位符
    combine_docs_prompt = PromptTemplate(
        template=base_prompt,
        input_variables=["context", "question"]
    )
    
    # 创建 ConversationalRetrievalChain
    chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": combine_docs_prompt},
        return_source_documents=True,  # 返回源文档用于 Fact-Check
        verbose=False
    )
    
    return chain, role_config, memory

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
    优化后的语义匹配：使用Prompts模块统一管理prompt
    """
    # 从Prompts模块获取语义匹配prompt
    keywords = reward_details.get('semantic_keywords', [])
    prompt = Prompts.get_semantic_match_prompt(question_key, user_input, keywords)
    
    # 优化：使用 invoke() 替代弃用的 __call__()
    response = semantic_model.invoke(prompt)
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
        "error_message": "I'm sorry, I had trouble processing that. Could you try again?",
        "voice_selector": "🎤 Voice",
        "voice_help": "Cherry: Female (lively) | Ethan: Male",
        "stickers_collected": "You've collected {current} out of {total} stickers!",
        "tips_content": """
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
        "error_message": "Desculpa, tive problemas a processar isso. Podes tentar novamente?",
        "voice_selector": "🎤 Voz",
        "voice_help": "Cherry: Feminina (animada) | Ethan: Masculina",
        "stickers_collected": "Já colecionaste {current} de {total} autocolantes!",
        "tips_content": """
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
    }
}
# UI
def main():
    # Language state (initialize first)
    if "language" not in st.session_state:
        st.session_state.language = "English"  # Default language
    
    # Get current language texts
    texts = language_texts[st.session_state.language]
    
    # Other session state initialization
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
    if "last_sticker" not in st.session_state:
        st.session_state.last_sticker = None
    if "last_analysis" not in st.session_state:
        st.session_state.last_analysis = {}
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = ""
    if "last_question" not in st.session_state:
        st.session_state.last_question = ""
    if "newly_awarded_sticker" not in st.session_state:
        st.session_state.newly_awarded_sticker = False
    if "gift_shown" not in st.session_state:
        st.session_state.gift_shown = False
    
    # 会话记忆初始化（用于 ConversationalRetrievalChain）
    if "conversation_chain" not in st.session_state:
        st.session_state.conversation_chain = None
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = None
        
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
            justify-content: flex-end;
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
            background-color: rgba(255, 255, 255, 0.9) !important;
            border-radius: 20px !important;
        }
        
        /* Input text color */
        .stChatInput input,
        .stChatInput textarea {
            color: #2d4f38 !important;
            font-weight: 500 !important;
        }
        
        /* Placeholder text color */
        .stChatInput input::placeholder,
        .stChatInput textarea::placeholder {
            color: #6b8576 !important;
            opacity: 0.7 !important;
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
                    <h1 style="margin-top: 0; font-size: 3rem; padding: 0;">{texts['title']}</h1>
                    <h1 style="margin-top: 0; font-size: 3rem; padding: 0;">{texts['subtitle']}</h1>
                    <h3 style="margin-top: 0.5rem; font-weight: bold; padding: 0; font-size: 1.25rem;">{texts['prompt']}</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Chat input (full width under title)
        user_input = st.chat_input(placeholder=texts['chat_placeholder'])
        print(f"User input: {user_input}")
        
        # Chat Section
        chatSection = st.container(height=520, key="chat_section", border=False)
        with chatSection:
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            for message in st.session_state.chat_history:
                with chat_message(message["role"]):
                    st.markdown(message["content"])
        

        if user_input and user_input != st.session_state.last_question:
            try:
                # ============ 方案1：严格状态隔离 + 防重机制 ============
                
                # 1. 生成唯一的交互ID，防止重复处理
                interaction_id = str(uuid.uuid4())
                if "processed_interactions" not in st.session_state:
                    st.session_state.processed_interactions = set()
                
                # 2. 立即保存输入到session_state，确保变量作用域
                st.session_state.current_question = user_input
                st.session_state.last_question = user_input
                
                # 3. 调试日志：记录输入
                print("=" * 60)
                print(f"[交互 {interaction_id[:8]}] 用户输入")
                print("=" * 60)
                print(f"问题: {user_input}")
                print(f"上一个问题: {st.session_state.get('last_question', 'None')}")
                
                # 4. 设置处理状态
                st.session_state.processing = True
                st.session_state.has_interacted = True
                st.session_state.show_score_guide = False
                
                # 5. 添加到UI显示历史
                st.session_state.chat_history.append({
                    "role": "user", 
                    "content": st.session_state.current_question
                })
                
                # 6. 显示用户消息
                with chatSection:
                    with chat_message("user"):
                        st.markdown(st.session_state.current_question)
                
                # 7. 显示加载动画
                with chatSection:
                    loading_placeholder = st.empty()
                    with st.spinner(""):
                        loading_placeholder.markdown(f"""
                            <div class="loading-container">
                                <div class="loading-spinner"></div>
                                <div>{texts['loading_thought']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                # ============ 处理AI回复 ============
                try:
                    # 8. 获取RAG实例
                    rag = get_rag_instance(
                        persist_directory=get_vectordb(role),
                        dashscope_api_key=dashscope_key
                    )
                    
                    # 9. 创建或重用ConversationalRetrievalChain
                    if (st.session_state.conversation_chain is None or 
                        st.session_state.conversation_memory is None):
                        # 第一次创建chain和memory
                        print(f"[交互 {interaction_id[:8]}] 创建新的Chain和Memory")
                        chain, role_config, memory = get_conversational_chain(
                            role=role, 
                            language=st.session_state.language,
                            vectordb=rag.vectordb
                        )
                        st.session_state.conversation_chain = chain
                        st.session_state.conversation_memory = memory
                    else:
                        # 重用现有chain和memory
                        print(f"[交互 {interaction_id[:8]}] 重用现有Chain和Memory")
                        chain = st.session_state.conversation_chain
                        memory = st.session_state.conversation_memory
                    
                    # 10. 调试日志：检查Memory状态
                    print(f"[交互 {interaction_id[:8]}] Memory状态检查")
                    print(f"  - Memory对象: {memory is not None}")
                    if memory:
                        print(f"  - 历史轮数: {len(memory.chat_memory.messages) // 2}")
                        print(f"  - 最近消息数: {len(memory.chat_memory.messages)}")
                        if len(memory.chat_memory.messages) > 0:
                            last_msg = memory.chat_memory.messages[-1]
                            print(f"  - 最后消息: {last_msg.content[:50]}...")
                    
                    # 11. 调用Chain（传入当前问题，Memory会自动注入历史）
                    print(f"[交互 {interaction_id[:8]}] 调用Chain处理问题")
                    print(f"  - 问题: {st.session_state.current_question}")
                    
                    result = chain.invoke({"question": st.session_state.current_question})
                    
                    # 12. 处理返回结果
                    answer = result.get("answer", "")
                    answer = re.sub(r'^\s*Answer:\s*', '', answer).strip()
                    
                    print(f"[交互 {interaction_id[:8]}] AI回答生成")
                    print(f"  - 回答长度: {len(answer)} 字符")
                    print(f"  - 回答预览: {answer[:100]}...")
                    
                    st.session_state.last_answer = answer
                    
                    # 13. 提取源文档
                    most_relevant_texts = result.get("source_documents", [])
                    st.session_state.most_relevant_texts = most_relevant_texts
                    print(f"  - 检索文档数: {len(most_relevant_texts)}")

                    # 14. 保存到UI显示历史
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": answer
                    })
                    
                    # 15. 更新亲密度评分
                    update_intimacy_score(st.session_state.current_question)
                    gift_triggered = check_gift()

                    # 16. 生成并播放语音
                    speak_text(answer, loading_placeholder)
                    
                    # 17. 显示AI回答
                    with chatSection:
                        with chat_message("assistant"):
                            st.markdown(answer)
                    
                    # 18. 标记处理完成
                    st.session_state.audio_played = True
                    st.session_state.processing = False
                    st.session_state.processed_interactions.add(interaction_id)
                    
                    print(f"[交互 {interaction_id[:8]}] 处理完成 ✅")
                    print("=" * 60)
                    
                except Exception as e:
                    # 处理AI回复错误
                    print(f"[交互 {interaction_id[:8]}] 错误: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                    if loading_placeholder:
                        loading_placeholder.empty()
                        
                    error_msg = texts['error_message']
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
                    
                    with chatSection:
                        with chat_message("assistant"):
                            st.markdown(error_msg)
                            st.error(f"Error details: {str(e)}")
                    
                    st.session_state.processing = False
            
            except Exception as outer_e:
                # 处理外层异常
                print(f"[错误] 外层异常: {str(outer_e)}")
                import traceback
                traceback.print_exc()
                st.error(f"An unexpected error occurred: {str(outer_e)}")
                st.session_state.processing = False


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
        if st.session_state.gift_given and not st.session_state.gift_shown: 
            gift_dialog()
            st.session_state.gift_shown = True
            
        

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
        
        # Voice selector
        st.markdown(f"**{texts['voice_selector']}**")
        if 'tts_voice' not in st.session_state:
            st.session_state.tts_voice = 'Cherry'
        
        # Voice options with descriptions
        if st.session_state.language == "Portuguese":
            voice_options = {
                'Cherry': '🎤 Cherry (Feminina - Animada)',
                'Ethan': '🎙️ Ethan (Masculina)'
            }
        else:
            voice_options = {
                'Cherry': '🎤 Cherry (Female - Lively)',
                'Ethan': '🎙️ Ethan (Male)'
            }
        
        voice_labels = list(voice_options.values())
        voice_keys = list(voice_options.keys())
        current_index = voice_keys.index(st.session_state.tts_voice)
        
        selected_label = st.selectbox(
            label="Voice",
            options=voice_labels,
            index=current_index,
            key='voice_selector',
            label_visibility="collapsed"
        )
        
        # Update session state with selected voice key
        selected_key = voice_keys[voice_labels.index(selected_label)]
        st.session_state.tts_voice = selected_key
        
        # Tips and Clear buttons
        input_section_col1, input_section_col2 = st.columns([0.35, 0.65], gap="small")
        with input_section_col1:
            # Show guide if toggled
            @st.dialog("💡How the 'Friendship Score!' Works", width="large")
            def score_guide():
                st.markdown(texts['tips_content'], unsafe_allow_html=True)
                
            if st.button(texts['tips_button'], icon=":material/lightbulb:", 
                        help="Click to see tips on how to get a higher Friendship Score!", 
                        use_container_width=True, type="primary"):
                score_guide()
                
        with input_section_col2:
            if st.button(texts['clear_button'], icon=":material/chat_add_on:", 
                        help="Click to clear the chat history and start fresh!", 
                        use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.show_score_guide = False
                st.session_state.audio_played = True
                st.session_state.gift_given = False
                st.session_state.intimacy_score = 0
                st.session_state.awarded_stickers = []
                st.session_state.last_question = ""
                st.session_state.has_interacted = False
                st.session_state.processing = False
                st.session_state.most_relevant_texts = []
                st.session_state.last_answer = ""
                st.session_state.last_sticker = None
                st.session_state.last_analysis = {}
                st.session_state.newly_awarded_sticker = False
                st.session_state.gift_shown = False
                # 清除对话记忆（重要！）
                st.session_state.conversation_chain = None
                st.session_state.conversation_memory = None
                if "session_id" in st.session_state:
                    del st.session_state["session_id"]
                if "logged_interactions" in st.session_state:
                    del st.session_state["logged_interactions"]
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
            
            st.session_state.newly_awarded_sticker = False
            
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
                        # Use language-specific caption if available
                        caption = reward["caption"][st.session_state.language] if isinstance(reward["caption"], dict) else reward["caption"]
                        st.session_state.awarded_stickers.append({
                            "key": sticker_key,
                            "image": reward["image"],
                            "caption": caption
                        })
                        st.toast(texts['sticker_toast'], icon="⭐")
                        st.session_state.newly_awarded_sticker = True
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
                    {texts['stickers_collected'].format(current=total_collected, total=total_possible)}
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
            if "most_relevant_texts" in st.session_state and "last_question" in st.session_state and "last_answer" in st.session_state:
                # 生成智能摘要（替代原始文档内容）
                if len(st.session_state.most_relevant_texts) > 0:
                    try:
                        fact_check_summary = generate_fact_check_content(
                            question=st.session_state.last_question,
                            retrieved_docs=st.session_state.most_relevant_texts,
                            ai_answer=st.session_state.last_answer,
                            language=st.session_state.language
                        )
                        
                        # 使用容器样式包裹 Markdown 内容
                        st.markdown("""
                            <style>
                            .fact-check-box {
                                background: #f0f8ff;
                                padding: 20px;
                                border-radius: 10px;
                                margin: 10px 0;
                                border-left: 4px solid #4a90e2;
                                color: #2c3e50;
                                line-height: 1.6;
                            }
                            .fact-check-box p {
                                margin-bottom: 10px;
                            }
                            .fact-check-box strong {
                                color: #1e3a8a;
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        
                        # 直接使用 st.markdown 渲染，应用样式类
                        st.markdown(f'<div class="fact-check-box">', unsafe_allow_html=True)
                        st.markdown(fact_check_summary)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # 可选：显示原始文档（折叠状态）
                        with st.expander("📄 查看原始文档 / View Raw Documents", expanded=False):
                            for i, doc in enumerate(st.session_state.most_relevant_texts[:2], 1):
                                source = doc.metadata.get('source_file', 'Unknown')
                                page = doc.metadata.get('page', 'N/A')
                                st.markdown(f"**{i}. {source} (Page {page})**")
                                st.text(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
                                st.markdown("---")
                    
                    except Exception as e:
                        # 降级：显示原始内容
                        print(f"[Fact-Check] 摘要生成失败: {str(e)}")
                        st.write(st.session_state.most_relevant_texts[0].page_content[:300] + "...")
            else:
                st.info(texts['fact_check_info'])
    cleanup_audio_files()

    # Log the interaction to Supabase
    if st.session_state.last_question:
        # Check if this specific interaction has already been logged
        if "logged_interactions" not in st.session_state:
            st.session_state.logged_interactions = set()
        
        combined = f"{st.session_state.last_question}|{st.session_state.last_answer}"

        interaction_key = hashlib.md5(combined.encode()).hexdigest()
        if interaction_key not in st.session_state.logged_interactions:
            log_interaction(
                user_input=st.session_state.last_question,
                ai_response=st.session_state.last_answer,
                intimacy_score=st.session_state.intimacy_score,
                is_sticker_awarded=st.session_state.newly_awarded_sticker,
                gift_given=st.session_state.gift_given
            )
            st.session_state.logged_interactions.add(interaction_key)

if __name__ == "__main__":
    main()
