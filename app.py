import streamlit as st
import random
import time

# Importando as funções e classes de outros arquivos
from utils.parser import carregar_topico_aleatorio
from services.gemini import gerar_pergunta
from services.firebase_service import salvar_resultado

# --- Configuração da Página ---
st.set_page_config(
    page_title="Estuda+ CPNU Quiz",
    page_icon="🧠",
    layout="centered"
)

# --- CSS Customizado para Estilo ---
st.markdown("""
<style>
    /* Estilo geral */
    .stApp {
        background-color: #616060;
    }
    /* Estilo dos botões de alternativa */
    div.stButton > button {
        width: 100%;
        border: 2px solid #4A4A4A;
        border-radius: 10px;
        padding: 10px 0px;
        margin: 5px 0px;
        font-weight: bold;
        color: #141414;
        background-color: #FFFFFF;
    }
    div.stButton > button:hover {
        border-color: #007BFF;
        color: #007BFF;
    }
    /* Classes para feedback visual */
    .correct-answer {
        background-color: #d4edda !important; /* Verde claro */
        color: #155724 !important;
        border-color: #155724 !important;
    }
    .wrong-answer {
        background-color: #f8d7da !important; /* Vermelho claro */
        color: #721c24 !important;
        border-color: #721c24 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Inicialização do Estado da Sessão ---
# O st.session_state é a "memória" do seu app entre as interações do usuário
if 'stage' not in st.session_state:
    st.session_state.stage = 'select_block'
    st.session_state.score = 0
    st.session_state.questions_answered = 0
    st.session_state.selected_block = None
    st.session_state.current_question = None
    st.session_state.answer_submitted = False

# --- Funções de Lógica do Quiz ---

def start_quiz(block_choice, block_name):
    """Inicia o quiz, gerando a primeira pergunta."""
    st.session_state.selected_block = {'id': block_choice, 'name': block_name}
    st.session_state.stage = 'generate_question'

def generate_new_question():
    """Busca um tópico e gera uma nova pergunta via API."""
    arquivo_csv = f"csv/bloco_{st.session_state.selected_block['id']}.txt"
    with st.spinner("Gerando uma nova pergunta desafiadora... 🧠"):
        topico = carregar_topico_aleatorio(arquivo_csv)
        if topico:
            dificuldade = random.randint(2, 5) # Perguntas um pouco mais difíceis
            st.session_state.current_question = gerar_pergunta(
                disciplina=topico['Disciplina'],
                topico=topico['Tópico'],
                subtopico=topico.get('Subtópico', ''),
                dificuldade=dificuldade
            )
            st.session_state.answer_submitted = False
            st.session_state.stage = 'show_question'
        else:
            st.error("Não foi possível carregar um tópico. Verifique os arquivos CSV.")
            st.session_state.stage = 'select_block'

def handle_answer(user_answer_idx):
    """Processa a resposta do usuário e atualiza o estado."""
    st.session_state.answer_submitted = True
    st.session_state.user_answer_idx = user_answer_idx
    
    if user_answer_idx == st.session_state.current_question.resposta_correta_idx:
        st.session_state.score += 1
        st.balloons() # Efeito de comemoração!
    
    st.session_state.questions_answered += 1
    
    # Salvar no Firebase (futura implementação)
    # resultado = { ... }
    # salvar_resultado(resultado)

def next_question():
    """Prepara para a próxima pergunta."""
    st.session_state.stage = 'generate_question'


# --- Renderização da Interface ---

st.title("🧠 Estuda+ CPNU Quiz")

# ETAPA 1: Seleção do Bloco
if st.session_state.stage == 'select_block':
    st.header("1. Escolha seu campo de batalha!")
    st.write("Selecione um bloco temático para começar a responder.")
    
    blocos = {
        "1": "Bloco 1 - Infraestrutura, Exatas e Engenharias",
        "3": "Bloco 3 - Ambiental, Agrário e Biológicas",
        "5": "Bloco 5 - Educação, Saúde, Desenvolvimento Social e Direitos Humanos"
    }
    
    for key, value in blocos.items():
        if st.button(value, key=f"btn_bloco_{key}"):
            start_quiz(key, value)
            st.rerun() # Reinicia o script para passar para a próxima etapa

# ETAPA 2: Geração da Pergunta (etapa lógica, sem UI)
elif st.session_state.stage == 'generate_question':
    generate_new_question()
    st.rerun()

# ETAPA 3: Exibição da Pergunta e Resposta
elif st.session_state.stage == 'show_question' and st.session_state.current_question:
    q = st.session_state.current_question

    # Placar
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Placar", f"{st.session_state.score} / {st.session_state.questions_answered}")
    with col2:
        dificuldade_str = "★" * q.dificuldade + "☆" * (5 - q.dificuldade)
        st.metric("Dificuldade", dificuldade_str)

    # Informações da Questão
    st.subheader(f"Disciplina: {q.disciplina}")
    st.caption(f"Tópico: {q.topico}")
    st.write("---")
    
    # Enunciado
    st.write(f"**{q.enunciado}**")

    # Alternativas
    for i, alt in enumerate(q.alternativas):
        # Se a resposta ainda não foi enviada, mostra botões normais
        if not st.session_state.answer_submitted:
            if st.button(alt, key=f"alt_{i}"):
                handle_answer(i)
                st.rerun()
        # Se já foi enviada, mostra os botões com feedback
        else:
            is_correct = (i == q.resposta_correta_idx)
            is_user_choice = (i == st.session_state.user_answer_idx)
            
            # Define o estilo do botão com base na resposta
            btn_class = ""
            if is_correct:
                btn_class = "correct-answer"
            elif is_user_choice and not is_correct:
                btn_class = "wrong-answer"

            # Usa HTML para aplicar a classe ao botão (workaround do Streamlit)
            st.markdown(f'<button class="{btn_class}" style="width:100%; border-radius:10px; padding:10px 0; margin:5px 0; border: 2px solid; font-weight:bold;">{alt}</button>', unsafe_allow_html=True)

    # Se a resposta foi enviada, mostra a explicação e o botão de próxima
    if st.session_state.answer_submitted:
        if st.session_state.user_answer_idx == q.resposta_correta_idx:
            st.success("✅ Resposta Correta!")
        else:
            st.error("❌ Resposta Incorreta!")
        
        with st.expander("Ver explicação detalhada"):
            st.write(q.explicacao)
        
        st.write("---")
        if st.button("Próxima Pergunta ➡", type="primary"):
            next_question()
            st.rerun()
