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
    layout="wide" # Usa a largura total da tela
)

# --- CSS Customizado para o Novo Layout ---
st.markdown("""
<style>
    /* Remove o padding padrão do Streamlit para usar todo o espaço */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    /* Estilo dos botões de alternativa */
    div.stButton > button {
        width: 100%;
        border: 2px solid #4A4A4A;
        border-radius: 10px;
        padding: 15px 0px; /* Aumenta a altura do botão */
        margin: 8px 0px;
        font-weight: bold;
        color: #4A4A4A;
        background-color: #FFFFFF;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        border-color: #007BFF;
        color: #007BFF;
        transform: scale(1.02);
    }
    /* Estilo para os cards de resposta */
    .answer-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        border-left: 5px solid;
    }
    .user-answer {
        border-left-color: #FFC107; /* Amarelo */
    }
    .correct-answer-card {
        border-left-color: #28A745; /* Verde */
    }
    /* Classes para feedback visual nos botões */
    .correct-answer-btn { background-color: #d4edda !important; color: #155724 !important; border-color: #155724 !important; }
    .wrong-answer-btn { background-color: #f8d7da !important; color: #721c24 !important; border-color: #721c24 !important; }
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
    st.session_state.active_tab = "Alternativas" # Controla a aba ativa

# --- Funções de Lógica do Quiz ---

def reset_to_blocks():
    """Reseta o estado para voltar à tela de seleção de blocos."""
    st.session_state.stage = 'select_block'
    st.session_state.score = 0
    st.session_state.questions_answered = 0
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.current_difficulty = 1
    st.session_state.selected_block = None
    st.session_state.selected_discipline = None

def reset_to_disciplines():
    """Reseta o estado para voltar à tela de seleção de disciplinas, mantendo o bloco."""
    st.session_state.stage = 'select_discipline'
    st.session_state.score = 0
    st.session_state.questions_answered = 0
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.current_difficulty = 1
    st.session_state.selected_discipline = None

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
            st.session_state.active_tab = "Alternativas"
            st.session_state.stage = 'show_question'
        else:
            st.error(f"Não foi possível carregar um tópico para a disciplina '{st.session_state.selected_discipline}'. Tente outra.")
            st.session_state.stage = 'select_discipline'

def handle_answer(user_answer_idx):
    st.session_state.answer_submitted = True
    st.session_state.user_answer_idx = user_answer_idx
    is_correct = (user_answer_idx == st.session_state.current_question_obj.resposta_correta_idx)
    
    if is_correct:
        st.session_state.score += 1
        st.session_state.current_difficulty = min(5, st.session_state.current_difficulty + 1)
    
    st.session_state.questions_answered += 1
    st.session_state.active_tab = "Explicação" # Muda para a aba de explicação
    
    firebase_service.salvar_resposta_usuario(
        session_id=st.session_state.session_id, question_id=st.session_state.current_question_id,
        user_answer_idx=user_answer_idx, is_correct=is_correct
    )

def next_question():
    st.session_state.stage = 'generate_question'

# --- Renderização da Interface ---

# Telas iniciais (Seleção de Bloco e Disciplina)
if st.session_state.stage in ['select_block', 'select_discipline']:
    st.title("🧠 Estuda+ CPNU Quiz")
    st.write("---")
    
    if st.session_state.stage == 'select_block':
        st.header("1. Escolha seu Bloco Temático")
        blocos = {
            "1": "Bloco 1 - Infraestrutura, Exatas e Engenharias",
            "3": "Bloco 3 - Ambiental, Agrário e Biológicas",
            "5": "Bloco 5 - Educação, Saúde, Desenvolvimento Social e Direitos Humanos"
        }
        for key, value in blocos.items():
            if st.button(value, key=f"btn_bloco_{key}"):
                select_block(key, value)
                st.rerun()
    
    elif st.session_state.stage == 'select_discipline':
        st.header(f"2. Escolha a Disciplina")
        st.caption(f"Bloco: {st.session_state.selected_block['name']}")
        arquivo_csv = f"csv/bloco_{st.session_state.selected_block['id']}.txt"
        disciplinas = carregar_disciplinas_do_bloco(arquivo_csv)
        opcoes_disciplina = ["Todas as Disciplinas"] + disciplinas
        disciplina_escolhida = st.selectbox("Selecione uma disciplina:", options=opcoes_disciplina)
        
        if st.button("Iniciar Quiz!", type="primary"):
            start_quiz(disciplina_escolhida)
            st.rerun()

# Etapa de Geração (sem UI)
elif st.session_state.stage == 'generate_question':
    generate_new_question()
    st.rerun()

# Tela Principal do Quiz
elif st.session_state.stage == 'show_question' and st.session_state.current_question_obj:
    q = st.session_state.current_question_obj
    
    # --- Coluna da Esquerda (Informações e Pergunta) ---
    left_col, right_col = st.columns([6, 4]) # Proporção 60% / 40%
    
    with left_col:
        # Header com Placar e Navegação
        h_col1, h_col2, h_col3, h_col4 = st.columns(4)
        with h_col1:
            st.metric("Placar", f"{st.session_state.score}/{st.session_state.questions_answered}")
        with h_col2:
            dificuldade_str = "★" * st.session_state.current_difficulty + "☆" * (5 - st.session_state.current_difficulty)
            st.metric("Nível", dificuldade_str)
        with h_col3:
            if st.button("Disciplinas"):
                reset_to_disciplines()
                st.rerun()
        with h_col4:
            if st.button("Blocos"):
                reset_to_blocks()
                st.rerun()

        st.write("---")
        
        # Detalhes da Pergunta
        st.subheader(f"Disciplina: {q.disciplina}")
        st.caption(f"Tópico: {q.topico}")
        st.title(q.enunciado)

    # --- Coluna da Direita (Alternativas e Explicação) ---
    with right_col:
        # Cria as abas. A aba ativa é controlada pelo session_state
        tab_alternativas, tab_explicacao = st.tabs(["Alternativas", "Explicação"])
        
        with tab_alternativas:
            if st.session_state.active_tab != "Alternativas":
                st.info("Responda a questão para ver a explicação.")
            
            for i, alt in enumerate(q.alternativas):
                # Desabilita os botões após uma resposta ser enviada
                if st.button(alt, key=f"alt_{i}", disabled=st.session_state.answer_submitted):
                    handle_answer(i)
                    st.rerun()

        with tab_explicacao:
            if not st.session_state.answer_submitted:
                st.info("Responda a questão para ver a explicação.")
            else:
                # Feedback visual (Certo/Errado)
                is_correct = (st.session_state.user_answer_idx == q.resposta_correta_idx)
                if is_correct:
                    st.success("✅ Resposta Correta!")
                else:
                    st.error("❌ Resposta Incorreta!")

                # Cards de Resposta
                user_choice_text = q.alternativas[st.session_state.user_answer_idx]
                correct_choice_text = q.alternativas[q.resposta_correta_idx]
                
                st.markdown(f'<div class="answer-card user-answer"><b>Sua Resposta:</b><br>{user_choice_text}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="answer-card correct-answer-card"><b>Resposta Correta:</b><br>{correct_choice_text}</div>', unsafe_allow_html=True)

                # Explicação Detalhada
                st.subheader("Explicação")
                st.write(q.explicacao)
                
                st.write("---")
                if st.button("Próxima Pergunta ➡", type="primary", use_container_width=True):
                    next_question()
                    st.rerun()
