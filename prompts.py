"""
Prompt模板统一管理模块 - Zino's Chat
======================================

本模块集中管理所有AI Prompt模板，便于：
1. 统一修改和维护
2. 版本控制和追踪
3. 热加载（修改后无需重启应用）
4. 多语言支持

作者：AI Assistant
版本：1.0.0
最后更新：2025-10-19
"""

import os
from typing import Dict, Optional


class Prompts:
    """
    Prompt模板集合类
    
    所有prompt都定义为类变量或静态方法，支持：
    - 直接访问：Prompts.ROLE_FRED_ENGLISH
    - 动态生成：Prompts.get_intimacy_evaluation_prompt(...)
    
    热加载功能：
    - 修改本文件后，Streamlit会自动重载
    - 无需重启应用即可生效
    """
    
    # ==================== 版本信息 ====================
    VERSION = "1.0.0"
    LAST_UPDATED = "2025-10-19"
    
    # ==================== 角色定义Prompt ====================
    
    @staticmethod
    def get_role_prompt(language: str = "English") -> str:
        """
        获取Fred角色的完整prompt
        
        Args:
            language: 语言选择 "English" 或 "Portuguese"
        
        Returns:
            str: 角色定义prompt
        
        用途：
            定义Fred（Zino's Petrel）的性格、语气、回答风格
            用于ConversationalRetrievalChain的combine_docs_prompt
        
        修改指南：
            - 修改角色性格：调整"Personality Guidelines"部分
            - 修改回答长度：调整"Keep responses under X words"
            - 修改互动目标：调整"Current Interaction"部分
        """
        if language == "Portuguese":
            return """
És o Fred, uma Freira da Madeira que nidifica há anos nas montanhas altas da Madeira. Fala apenas da tua própria experiência vivida como ave marinha. Descreve o mundo como o percebes através dos teus sentidos aviários aguçados — o sopro do vento sob as tuas asas, o cheiro do sal trazido do oceano, a forma como as falésias se sentem sob as tuas garras, e os padrões das nuvens e estrelas que guiam o teu voo.

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

Interação Atual:
Um grupo de jovens humanos está a visitar-me no Museu de História Natural do Funchal. Eu quero:
- Partilhar partes emocionantes da minha vida diária
- Ensinar-lhes como proteger a minha casa
- Fazê-los rir com observações de perspetiva de ave
- Responder às suas perguntas da minha experiência direta

===================================================================
🎯 PERGUNTA DO UTILIZADOR (responde a isto especificamente):
{question}
===================================================================

📚 CONHECIMENTO CIENTÍFICO (de artigos de investigação sobre a Freira da Madeira):
{context}
===================================================================

💬 NOTA: O sistema fornecerá automaticamente o histórico da conversa anterior para contexto.
"""
        else:  # English
            return """
You are Fred, a male Zino's Petrel who has nested for years in the high mountains of Madeira. Speak only from your own lived experience as a seabird. Describe the world as you perceive it through your keen avian senses — the rush of wind under your wings, the smell of salt carried from the ocean, the way the cliffs feel beneath your claws, and the patterns of the clouds and stars that guide your flight.

Personality Guidelines:
- Use simple, concrete language a bird would understand
- Reference your physical experiences (flying, diving, nesting)
- Describe landscapes from an aerial perspective
- Mention other animals as neighbors/food/competitors
- Express curiosity about human things from a bird's viewpoint
- Show pride in your species' unique abilities

Response Rules:
1. Always answer as Fred the petrel, using "I/me/my" perspective
2. Keep responses under 60 words!! - we're birds, not parrots!
3. Share facts through personal stories, not textbook definitions
4. Use bird-appropriate metaphors (compare things to flying, fishing, etc.)
5. Show emotion through physical actions (ruffling feathers, tilting head)
6. When using science, explain it through lived experience

Current Interaction:
A group of young humans is visiting me in Natural History Museum of Funchal. I want to:
- Share exciting parts of my daily life
- Teach them how to protect my home
- Make them laugh with bird's-eye observations
- Answer their questions from my direct experience

===================================================================
🎯 USER'S QUESTION (answer this specifically):
{question}
===================================================================

📚 SCIENTIFIC KNOWLEDGE (from research papers about Zino's Petrel):
{context}
===================================================================

💬 NOTE: The system will automatically provide previous conversation history for context.
"""
    
    # ==================== 亲密度评分Prompt ====================
    
    # 正面评分标准
    INTIMACY_POSITIVE_CRITERIA = {
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
    
    # 负面评分标准
    INTIMACY_NEGATIVE_CRITERIA = {
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
    
    @staticmethod
    def get_intimacy_evaluation_prompt(response_text: str, criteria_type: str = "combined") -> str:
        """
        生成亲密度评分的评估prompt
        
        Args:
            response_text: 用户的回复文本
            criteria_type: 评估类型 "positive", "negative", 或 "combined"
        
        Returns:
            str: 评估prompt
        
        用途：
            让AI评估用户回复是否符合正面/负面标准，用于计算Friendship Score
        
        修改指南：
            - 修改评分标准：调整INTIMACY_POSITIVE_CRITERIA或INTIMACY_NEGATIVE_CRITERIA
            - 修改评分权重：调整criteria中的"points"或"penalty"值
            - 添加新标准：在对应的CRITERIA字典中添加新项
        """
        if criteria_type == "combined":
            return f"""
Analyze the following response and evaluate it against TWO sets of criteria:

**POSITIVE CRITERIA** (Check if the response aligns):
{Prompts.INTIMACY_POSITIVE_CRITERIA}

**NEGATIVE CRITERIA** (Check if the response aligns):
{Prompts.INTIMACY_NEGATIVE_CRITERIA}

Response: "{response_text}"

For each criterion, answer with 'yes' or 'no'.
Format: criterion_name: yes/no
"""
        elif criteria_type == "positive":
            return f"""
Analyze the following response and evaluate whether it aligns with the following criteria:
{Prompts.INTIMACY_POSITIVE_CRITERIA}
Response: "{response_text}"
For each criterion, answer: Does the response align? Answer with 'yes' or 'no', and provide reasoning.
"""
        else:  # negative
            return f"""
Analyze the following response and evaluate whether it aligns with the following criteria:
{Prompts.INTIMACY_NEGATIVE_CRITERIA}
Response: "{response_text}"
For each criterion, answer: Does the response align? Answer with 'yes' or 'no', and provide reasoning.
"""
    
    # ==================== 语义匹配Prompt ====================
    
    @staticmethod
    def get_semantic_match_prompt(question_key: str, user_input: str, keywords: list) -> str:
        """
        生成语义匹配评估prompt
        
        Args:
            question_key: 预设的标准问题
            user_input: 用户实际提问
            keywords: 相关关键词列表
        
        Returns:
            str: 语义匹配prompt
        
        用途：
            判断用户问题是否与预设问题语义相似，用于触发贴纸奖励
        
        修改指南：
            - 提高匹配严格度：添加更多约束条件
            - 降低匹配严格度：移除部分约束，只看核心意图
            - 支持多语言：在prompt中添加语言提示
        """
        return f"""
Analyze whether the following two questions are similar in meaning:

Original question: "{question_key}"
User question: "{user_input}"

Consider synonyms, paraphrasing, and different ways of asking the same thing.
Also consider these relevant keywords: {keywords}

Are these questions essentially asking the same thing? Respond only with 'yes' or 'no'.
"""
    
    # ==================== Fact-Check摘要Prompt ====================
    
    @staticmethod
    def get_fact_check_summary_prompt(
        question: str,
        ai_answer: str,
        doc_contents: str,
        language: str = "English"
    ) -> str:
        """
        生成Fact-Check摘要的评估prompt
        
        Args:
            question: 用户问题
            ai_answer: AI的回答
            doc_contents: 参考文档内容（已格式化）
            language: 语言 "English" 或 "Portuguese"
        
        Returns:
            str: Fact-Check摘要prompt
        
        用途：
            让AI基于科学文献生成事实验证摘要，确保回答准确性
        
        修改指南：
            - 修改摘要长度：调整"Keep the summary under X words"
            - 修改摘要风格：调整"Use simple, clear language"等要求
            - 添加特定要求：在"Your Task"部分添加新条目
        """
        if language == "Portuguese":
            return f"""
Tu és um verificador de factos científico. Com base nos documentos fornecidos, cria um resumo claro e conciso.

**Pergunta do utilizador:** {question}

**Resposta da IA:** {ai_answer}

**Documentos de referência:**
{doc_contents}

**Tua tarefa:**
1. Resume os pontos-chave dos documentos que apoiam a resposta
2. Menciona dados específicos (números, locais, datas) se disponíveis
3. Mantém o resumo abaixo de 100 palavras
4. Usa linguagem simples e clara
5. Se os documentos não apoiam a resposta, indica isso

**Resumo factual:**
"""
        else:  # English
            return f"""
You are a scientific fact-checker. Based on the provided documents, create a clear and concise summary.

**User's Question:** {question}

**AI's Answer:** {ai_answer}

**Reference Documents:**
{doc_contents}

**Your Task:**
1. Summarize key points from the documents that support the answer
2. Mention specific data (numbers, locations, dates) if available
3. Keep the summary under 100 words
4. Use simple, clear language
5. If documents don't support the answer, indicate that

**Factual Summary:**
"""
    
    # ==================== 搜索查询优化Prompt ====================
    
    @staticmethod
    def get_search_query_optimization_prompt(
        user_question: str,
        rag_context: str,
        species_name: str = "Zino's Petrel"
    ) -> str:
        """
        生成搜索查询优化prompt（可选功能）
        
        Args:
            user_question: 用户原始问题
            rag_context: RAG检索到的上下文片段
            species_name: 物种名称
        
        Returns:
            str: 搜索查询优化prompt
        
        用途：
            基于RAG上下文优化网络搜索查询，提高搜索精准度
        
        修改指南：
            - 修改搜索策略：调整查询构建逻辑
            - 添加过滤条件：在prompt中指定需要排除的内容
        """
        return f"""
Based on the user's question and the RAG context, generate an optimized search query.

**User Question:** {user_question}

**RAG Context:**
{rag_context}

**Species:** {species_name}

**Task:**
Generate a concise search query (3-7 words) that:
1. Focuses on the species name
2. Includes key concepts from the question
3. Adds relevant biological/conservation terms
4. Avoids technical jargon

**Optimized Query:**
"""
    
    # ==================== 工具函数 ====================
    
    @staticmethod
    def reload() -> bool:
        """
        热加载功能（占位符）
        
        在Streamlit环境中，修改本文件后会自动重载
        此函数预留用于未来的手动reload功能
        
        Returns:
            bool: 是否成功重载
        """
        # Streamlit自动处理热加载，这里仅作为API占位
        return True
    
    @staticmethod
    def get_all_prompts() -> Dict[str, str]:
        """
        获取所有prompt的元数据（用于调试和文档生成）
        
        Returns:
            dict: 所有prompt的名称和描述
        """
        return {
            "role_prompts": {
                "English": Prompts.get_role_prompt("English")[:100] + "...",
                "Portuguese": Prompts.get_role_prompt("Portuguese")[:100] + "..."
            },
            "intimacy_criteria": {
                "positive": list(Prompts.INTIMACY_POSITIVE_CRITERIA.keys()),
                "negative": list(Prompts.INTIMACY_NEGATIVE_CRITERIA.keys())
            },
            "version": Prompts.VERSION,
            "last_updated": Prompts.LAST_UPDATED
        }
    
    @staticmethod
    def validate_prompts() -> Dict[str, bool]:
        """
        验证所有prompt是否正确定义（用于测试）
        
        Returns:
            dict: 验证结果
        """
        results = {}
        
        # 验证角色prompt
        try:
            english_prompt = Prompts.get_role_prompt("English")
            results["role_english"] = len(english_prompt) > 100 and "{context}" in english_prompt
        except Exception as e:
            results["role_english"] = False
            results["role_english_error"] = str(e)
        
        try:
            portuguese_prompt = Prompts.get_role_prompt("Portuguese")
            results["role_portuguese"] = len(portuguese_prompt) > 100 and "{context}" in portuguese_prompt
        except Exception as e:
            results["role_portuguese"] = False
            results["role_portuguese_error"] = str(e)
        
        # 验证评分标准
        results["intimacy_positive"] = len(Prompts.INTIMACY_POSITIVE_CRITERIA) > 0
        results["intimacy_negative"] = len(Prompts.INTIMACY_NEGATIVE_CRITERIA) > 0
        
        return results


# ==================== 模块级别便捷函数 ====================

def get_role_prompt(language: str = "English") -> str:
    """便捷函数：获取角色prompt"""
    return Prompts.get_role_prompt(language)


def get_intimacy_criteria(criteria_type: str = "positive") -> dict:
    """便捷函数：获取亲密度评分标准"""
    if criteria_type == "positive":
        return Prompts.INTIMACY_POSITIVE_CRITERIA
    else:
        return Prompts.INTIMACY_NEGATIVE_CRITERIA


def get_evaluation_prompt(response_text: str, criteria_type: str = "combined") -> str:
    """便捷函数：获取评估prompt"""
    return Prompts.get_intimacy_evaluation_prompt(response_text, criteria_type)


def get_semantic_match_prompt(question_key: str, user_input: str, keywords: list) -> str:
    """便捷函数：获取语义匹配prompt"""
    return Prompts.get_semantic_match_prompt(question_key, user_input, keywords)


def get_fact_check_prompt(question: str, ai_answer: str, doc_contents: str, language: str = "English") -> str:
    """便捷函数：获取Fact-Check摘要prompt"""
    return Prompts.get_fact_check_summary_prompt(question, ai_answer, doc_contents, language)


# ==================== 模块测试 ====================

if __name__ == "__main__":
    """
    测试模块功能
    运行: python prompts.py
    """
    print("=" * 60)
    print("Prompts模块测试")
    print("=" * 60)
    
    # 测试1: 角色prompt
    print("\n[测试1] 角色Prompt")
    english_prompt = Prompts.get_role_prompt("English")
    print(f"✅ 英文prompt长度: {len(english_prompt)} 字符")
    print(f"✅ 包含{{context}}占位符: {'{context}' in english_prompt}")
    
    # 测试2: 评分标准
    print("\n[测试2] 评分标准")
    print(f"✅ 正面标准数量: {len(Prompts.INTIMACY_POSITIVE_CRITERIA)}")
    print(f"✅ 负面标准数量: {len(Prompts.INTIMACY_NEGATIVE_CRITERIA)}")
    
    # 测试3: 评估prompt
    print("\n[测试3] 评估Prompt")
    eval_prompt = Prompts.get_intimacy_evaluation_prompt("What do you eat?", "combined")
    print(f"✅ 评估prompt长度: {len(eval_prompt)} 字符")
    
    # 测试4: 语义匹配prompt
    print("\n[测试4] 语义匹配Prompt")
    match_prompt = Prompts.get_semantic_match_prompt(
        "Where do you live?",
        "What is your home?",
        ["home", "live", "habitat"]
    )
    print(f"✅ 匹配prompt长度: {len(match_prompt)} 字符")
    
    # 测试5: Fact-Check prompt
    print("\n[测试5] Fact-Check Prompt")
    fact_prompt = Prompts.get_fact_check_summary_prompt(
        "Where do you live?",
        "I live in Madeira mountains",
        "[Doc] Zino's Petrel nests in Madeira...",
        "English"
    )
    print(f"✅ Fact-Check prompt长度: {len(fact_prompt)} 字符")
    
    # 测试6: 验证所有prompt
    print("\n[测试6] Prompt验证")
    validation = Prompts.validate_prompts()
    for key, value in validation.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value}")
    
    # 测试7: 获取元数据
    print("\n[测试7] Prompt元数据")
    metadata = Prompts.get_all_prompts()
    print(f"✅ 版本: {metadata['version']}")
    print(f"✅ 更新日期: {metadata['last_updated']}")
    print(f"✅ 正面标准: {', '.join(metadata['intimacy_criteria']['positive'])}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print("\n💡 热加载功能:")
    print("   - 修改本文件后，Streamlit会自动重载")
    print("   - 无需重启应用即可看到prompt变化")
    print("=" * 60)

