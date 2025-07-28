import streamlit as st
import random
import uuid

# Importando as funções e classes dos seus outros arquivos
from utils.parser import carregar_topico_aleatorio, carregar_disciplinas_do_bloco
from services.gemini import gerar_pergunta
from services.firebase_service import firebase_service
from models.question import Question

# --- Configuração da Página ---
st.set_page_config(
    page_title="Estuda+ CPNU Quiz",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS Customizado Simplificado ---
st.markdown("""
<style>
    /* Reset básico */
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 100%;
    }
    
    /* Header estilizado */
    .quiz-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        margin: -1rem -2rem 2rem -2rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
    }
    
    .quiz-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .quiz-subtitle {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Cards para métricas */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1e293b;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    /* Info da disciplina */
    .discipline-info {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .discipline-name {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    
    .topic-name {
        color: #3730a3;
        font-size: 1rem;
    }
    
    /* Enunciado */
    .question-statement {
        font-size: 1.4rem;
        font-weight: 500;
        line-height: 1.6;
        color: #1f2937;
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    
    /* Botões personalizados */
    .stButton > button {
        width: 100%;
        background: white;
        color: #374151;
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        margin: 0.5rem 0;
    }
    
    .stButton > button:hover {
        border-color: #3b82f6;
        background: #f8fafc;
        color: #1e40af;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Botões primários */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        font-weight: bold;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    /* Seleção de blocos */
    .block-selection {
        max-width: 600px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .block-selection h3 {
        text-align: center;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .block-selection p {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    /* Tabs do Streamlit */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f1f5f9;
        padding: 4px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #64748b;
        font-weight: 600;
        padding: 12px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #3b82f6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 8px;
    }
    
    .stError {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
    }
    
    .stInfo {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
    }
    
    /* Explicação */
    .explanation-text {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        line-height: 1.6;
        color: #374151;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    /* Responsivo */
    @media (max-width: 768px) {
        .quiz-title {
            font-size: 2rem;
        }
        
        .quiz-subtitle {
            font-size: 1rem;
        }
        
        .question-statement {
            font-size: 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Inicialização do Estado da Sessão ---
if 'stage' not in st.session_state:
    st.session_state.stage = 'select_block'
    st.session_state.score = 0
    st.session_state.questions_answered = 0
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.current_difficulty = 1
    st.session_state.selected_block = None
    st.session_state.selected_discipline = None
    st.session_state.current_question_obj = None
    st.session_state.current_question_id = None
    st.session_state.answer_submitted = False
    st.session_state.active_tab = "alternativas"

# --- Funções de Lógica ---
def reset_to_blocks():
    st.session_state.stage = 'select_block'
    st.session_state.score = 0
    st.session_state.questions_answered = 0
    st.session_state.current_difficulty = 1

def reset_to_disciplines():
    st.session_state.stage = 'select_discipline'
    st.session_state.score = 0
    st.session_state.questions_answered = 0
    st.session_state.current_difficulty = 1

def select_block(block_id, block_name):
    st.session_state.selected_block = {'id': block_id, 'name': block_name}
    st.session_state.stage = 'select_discipline'

def start_quiz(discipline):
    st.session_state.selected_discipline = discipline
    st.session_state.stage = 'generate_question'

def generate_new_question():
    arquivo_csv = f"csv/bloco_{st.session_state.selected_block['id']}.txt"
    with st.spinner(f"Gerando uma pergunta nível {st.session_state.current_difficulty} ★..."):
        topico = carregar_topico_aleatorio(arquivo_csv, st.session_state.selected_discipline)
        if topico:
            question_obj = gerar_pergunta(
                disciplina=topico['Disciplina'], topico=topico['Tópico'],
                subtopico=topico.get('Subtópico', ''), dificuldade=st.session_state.current_difficulty
            )
            question_id = firebase_service.salvar_questao_no_banco(
                question_obj, st.session_state.selected_block['name']
            )
            st.session_state.current_question_obj = question_obj
            st.session_state.current_question_id = question_id
            st.session_state.answer_submitted = False
            st.session_state.active_tab = "alternativas"
            st.session_state.stage = 'show_question'
        else:
            st.error(f"Não foi possível carregar um tópico para a disciplina '{st.session_state.selected_discipline}'.")
            st.session_state.stage = 'select_discipline'

def handle_answer(user_answer_idx):
    st.session_state.answer_submitted = True
    st.session_state.user_answer_idx = user_answer_idx
    is_correct = (user_answer_idx == st.session_state.current_question_obj.resposta_correta_idx)
    if is_correct:
        st.session_state.score += 1
        st.session_state.current_difficulty = min(5, st.session_state.current_difficulty + 1)
    st.session_state.questions_answered += 1
    st.session_state.active_tab = "explicacao"
    firebase_service.salvar_resposta_usuario(
        session_id=st.session_state.session_id, 
        question_id=st.session_state.current_question_id,
        user_answer_idx=user_answer_idx, 
        is_correct=is_correct
    )

def next_question():
    st.session_state.stage = 'generate_question'

# --- Header Principal ---
st.markdown("""
<div class="quiz-header">
    <h1 class="quiz-title">🧠 Estuda+ CPNU Quiz</h1>
    <p class="quiz-subtitle">Sistema Inteligente de Estudos para Concursos</p>
</div>
""", unsafe_allow_html=True)

# --- Renderização das Telas ---

if st.session_state.stage == 'select_block':
    st.markdown('<div class="block-selection">', unsafe_allow_html=True)
    st.markdown("### 🎯 Escolha seu Bloco Temático")
    st.markdown("Selecione o bloco de estudos que deseja praticar:")
    
    blocos = {
        "1": "Bloco 1 - Saúde e Seguridade Social", 
        "2": "Bloco 2 - Cultura e Educação", 
        "3": "Bloco 3 - Ciências, Dados e Tecnologia", 
        "4": "Bloco 4 - Engenharias e Arquitetura",
        "5": "Bloco 5 - Administração e Finanças",
        "6": "Bloco 6 - Desenvolvimento Socioeconômico",
        "7": "Bloco 7 - Justiça e Defesa",
        "8": "Bloco 8 - Intermediário - Saúde", 
        "9": "Bloco 9 - Intermediário - Regulação"
    }
    
    for key, value in blocos.items():
        if st.button(value, key=f"btn_bloco_{key}"):
            select_block(key, value.split(" - ")[0].replace("📚 ", "").replace("💼 ", "").replace("🔬 ", ""))
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.stage == 'select_discipline':
    st.markdown('<div class="block-selection">', unsafe_allow_html=True)
    st.markdown("### 📖 Escolha a Disciplina")
    st.info(f"**Bloco selecionado:** {st.session_state.selected_block['name']}")
    
    arquivo_csv = f"csv/bloco_{st.session_state.selected_block['id']}.txt"
    disciplinas = ["🎯 Todas as Disciplinas"] + [f"📋 {d}" for d in carregar_disciplinas_do_bloco(arquivo_csv)]
    
    disciplina_escolhida = st.selectbox(
        "Selecione uma disciplina:", 
        options=disciplinas
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar aos Blocos"):
            reset_to_blocks()
            st.rerun()
    with col2:
        if st.button("🚀 Iniciar Quiz!", type="primary"):
            disciplina_limpa = disciplina_escolhida.replace("🎯 ", "").replace("📋 ", "")
            start_quiz(disciplina_limpa)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.stage == 'generate_question':
    generate_new_question()
    st.rerun()

elif st.session_state.stage == 'show_question' and st.session_state.current_question_obj:
    q = st.session_state.current_question_obj
    
    # Layout em duas colunas
    col1, col2 = st.columns([1.2, 1], gap="large")
    
    with col1:
        # Métricas
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state.score}/{st.session_state.questions_answered}</div>
                <div class="metric-label">Placar</div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_col2:
            stars = "★" * st.session_state.current_difficulty + "☆" * (5 - st.session_state.current_difficulty)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stars}</div>
                <div class="metric-label">Nível</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Navegação
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("📖 Disciplinas", key="nav_disc"):
                reset_to_disciplines()
                st.rerun()
        with nav_col2:
            if st.button("🎯 Blocos", key="nav_blocos"):
                reset_to_blocks()
                st.rerun()
        
        # Info da disciplina
        st.markdown(f"""
        <div class="discipline-info">
            <div class="discipline-name">{q.disciplina}</div>
            <div class="topic-name">Tópico: {q.topico}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enunciado
        st.markdown(f'<div class="question-statement">{q.enunciado}</div>', unsafe_allow_html=True)
    
    with col2:
        # Tabs
        tab1, tab2 = st.tabs(["🔤 Alternativas", "💡 Explicação"])
        
        with tab1:
            if not st.session_state.answer_submitted:
                st.markdown("**Selecione a alternativa correta:**")
                for i, alt in enumerate(q.alternativas):
                    if st.button(alt, key=f"alt_{i}"):
                        handle_answer(i)
                        st.rerun()
            else:
                st.info("✅ Resposta enviada! Veja a explicação na outra aba.")
                
                for i, alt in enumerate(q.alternativas):
                    if i == q.resposta_correta_idx:
                        st.success(f"✅ {alt}")
                    elif i == st.session_state.user_answer_idx and i != q.resposta_correta_idx:
                        st.error(f"❌ {alt}")
                    else:
                        st.write(f"• {alt}")
        
        with tab2:
            if not st.session_state.answer_submitted:
                st.info("🤔 Responda a questão primeiro para ver a explicação.")
            else:
                is_correct = (st.session_state.user_answer_idx == q.resposta_correta_idx)
                
                if is_correct:
                    st.success("🎉 **Parabéns! Resposta Correta!**")
                else:
                    st.error("❌ **Resposta Incorreta**")
                
                st.markdown("### 📝 Explicação")
                st.markdown(f'<div class="explanation-text">{q.explicacao}</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                if st.button("➡️ Próxima Pergunta", type="primary"):
                    next_question()
                    st.rerun()