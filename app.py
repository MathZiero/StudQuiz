import streamlit as st
import uuid

from utils.parser import carregar_topico_aleatorio, carregar_disciplinas_do_bloco
from services.gemini import gerar_pergunta
from services.supabase_service import supabase_service
from models.question import Question

# ---------------------------------------------------------------------------
# Configuração da Página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="StudQuiz · CNPU",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------------------------
# Design System — Dark Mode Premium
# ---------------------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
/* ═══════════════════════ RESET & BASE ═══════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stApp"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #0d1117 !important;
}

[data-testid="stHeader"] {
    background-color: #0d1117 !important;
    border-bottom: 1px solid #21262d;
}

.main .block-container {
    padding: 2rem 3rem;
    max-width: 1200px;
    margin: 0 auto;
}

/* ═══════════════════════ SCROLLBAR ═══════════════════════ */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #161b22; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

/* ═══════════════════════ NAVBAR ═══════════════════════ */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 0 2rem 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 2.5rem;
}
.navbar-logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.navbar-logo-icon {
    font-size: 2rem;
    line-height: 1;
}
.navbar-logo-text {
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #58a6ff 0%, #a371f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}
.navbar-badge {
    font-size: 0.7rem;
    font-weight: 600;
    background: rgba(88, 166, 255, 0.15);
    color: #58a6ff;
    border: 1px solid rgba(88, 166, 255, 0.3);
    padding: 2px 8px;
    border-radius: 20px;
    margin-left: 0.5rem;
}
.navbar-meta {
    font-size: 0.85rem;
    color: #8b949e;
}

/* ═══════════════════════ PÁGINA: SELEÇÃO DE BLOCO ═══════════════════════ */
.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #e6edf3;
    margin-bottom: 0.4rem;
    letter-spacing: -1px;
}
.page-subtitle {
    font-size: 1rem;
    color: #8b949e;
    margin-bottom: 2rem;
}

.block-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
}

.block-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.block-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}
.block-card:hover {
    border-color: #58a6ff;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(88, 166, 255, 0.12);
}
.block-number {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8b949e;
    margin-bottom: 0.4rem;
}
.block-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 0.4rem;
}
.block-subtitle {
    font-size: 0.8rem;
    color: #8b949e;
}

/* ═══════════════════════ PÁGINA: SELEÇÃO DE DISCIPLINA ═══════════════════════ */
.breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: #8b949e;
    margin-bottom: 2rem;
}
.breadcrumb span { color: #58a6ff; font-weight: 600; }

/* ═══════════════════════ PÁGINA: QUIZ ═══════════════════════ */
.quiz-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    align-items: start;
}

/* Painel esquerdo */
.question-panel {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 2rem;
}

.question-meta {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.tag {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid;
}
.tag-discipline {
    background: rgba(88, 166, 255, 0.1);
    color: #58a6ff;
    border-color: rgba(88, 166, 255, 0.3);
}
.tag-topic {
    background: rgba(163, 113, 247, 0.1);
    color: #a371f7;
    border-color: rgba(163, 113, 247, 0.3);
}
.tag-difficulty {
    background: rgba(240, 136, 62, 0.1);
    color: #f0883e;
    border-color: rgba(240, 136, 62, 0.3);
}

.question-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #58a6ff;
    margin-bottom: 1rem;
}
.question-text {
    font-size: 1.1rem;
    line-height: 1.75;
    color: #e6edf3;
    font-weight: 500;
}

/* Score bar */
.score-bar {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1.5rem;
}
.score-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.score-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: #e6edf3;
    line-height: 1;
}
.score-label {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8b949e;
    margin-top: 2px;
}
.score-divider {
    width: 1px;
    height: 36px;
    background: #30363d;
}

/* Painel direito */
.answer-panel {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 2rem;
}
.answer-panel-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #8b949e;
    margin-bottom: 1.2rem;
}

/* Alternativas */
.alt-btn {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    padding: 1rem 1.2rem;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.18s ease;
    text-align: left;
    margin-bottom: 0.6rem;
    color: #e6edf3;
    font-family: 'Inter', sans-serif;
    font-size: 0.92rem;
    line-height: 1.4;
    font-weight: 500;
}
.alt-btn:hover {
    border-color: #58a6ff;
    background: rgba(88, 166, 255, 0.07);
    transform: translateX(3px);
}
.alt-letter {
    font-size: 0.75rem;
    font-weight: 800;
    color: #58a6ff;
    background: rgba(88, 166, 255, 0.15);
    border-radius: 5px;
    padding: 3px 7px;
    flex-shrink: 0;
}

/* Resultado das alternativas */
.alt-correct {
    border-color: #2ea043 !important;
    background: rgba(46, 160, 67, 0.1) !important;
}
.alt-wrong {
    border-color: #da3633 !important;
    background: rgba(218, 54, 51, 0.1) !important;
    opacity: 0.7;
}
.alt-neutral { opacity: 0.5; }

/* Explicação */
.explanation-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-left: 3px solid #58a6ff;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    font-size: 0.92rem;
    line-height: 1.7;
    color: #c9d1d9;
    margin-top: 1.2rem;
}

.result-correct {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(46, 160, 67, 0.12);
    border: 1px solid rgba(46, 160, 67, 0.4);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    color: #3fb950;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.result-wrong {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(218, 54, 51, 0.12);
    border: 1px solid rgba(218, 54, 51, 0.4);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    color: #f85149;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 1rem;
}

/* ═══════════════════════ BOTÕES STREAMLIT ═══════════════════════ */
.stButton > button {
    background: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.18s ease !important;
    width: auto !important;
}
.stButton > button:hover {
    background: #30363d !important;
    border-color: #58a6ff !important;
    color: #58a6ff !important;
    transform: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    border-color: #2ea043 !important;
    color: white !important;
    font-weight: 700 !important;
    width: 100% !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2ea043, #3fb950) !important;
    box-shadow: 0 4px 16px rgba(46, 160, 67, 0.4) !important;
    transform: translateY(-1px) !important;
}

/* ═══════════════════════ SELECTBOX ═══════════════════════ */
.stSelectbox > div > div {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}

/* ═══════════════════════ SPINNER ═══════════════════════ */
[data-testid="stSpinner"] { color: #58a6ff !important; }

/* ═══════════════════════ ALERTS NATIVOS ═══════════════════════ */
[data-testid="stAlert"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    color: #e6edf3 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Estado da Sessão
# ---------------------------------------------------------------------------
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
    st.session_state.user_answer_idx = None

# ---------------------------------------------------------------------------
# Funções de Lógica
# ---------------------------------------------------------------------------
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
    with st.spinner("Gerando questão com IA..."):
        topico = carregar_topico_aleatorio(arquivo_csv, st.session_state.selected_discipline)
        if topico:
            question_obj = gerar_pergunta(
                disciplina=topico.get('Disciplina', ''),
                topico=topico.get('Tópico', ''),
                subtopico=topico.get('Subtópico', ''),
                dificuldade=st.session_state.current_difficulty
            )
            question_id = supabase_service.salvar_questao_no_banco(
                question_obj, st.session_state.selected_block['name']
            )
            st.session_state.current_question_obj = question_obj
            st.session_state.current_question_id = question_id
            st.session_state.answer_submitted = False
            st.session_state.user_answer_idx = None
            st.session_state.stage = 'show_question'
        else:
            st.error(f"Não foi possível carregar um tópico para '{st.session_state.selected_discipline}'.")
            st.session_state.stage = 'select_discipline'

def handle_answer(user_answer_idx):
    st.session_state.answer_submitted = True
    st.session_state.user_answer_idx = user_answer_idx
    is_correct = (user_answer_idx == st.session_state.current_question_obj.resposta_correta_idx)
    if is_correct:
        st.session_state.score += 1
        st.session_state.current_difficulty = min(5, st.session_state.current_difficulty + 1)
    else:
        st.session_state.current_difficulty = max(1, st.session_state.current_difficulty - 1)
    st.session_state.questions_answered += 1
    supabase_service.salvar_resposta_usuario(
        session_id=st.session_state.session_id,
        question_id=st.session_state.current_question_id,
        user_answer_idx=user_answer_idx,
        is_correct=is_correct
    )

LETTERS = ['A', 'B', 'C', 'D', 'E']
BLOCK_DATA = {
    "1": ("Saúde e Seguridade Social",    "Previdência, SUS, Assistência Social"),
    "2": ("Cultura e Educação",            "Educação básica, superior, cultura"),
    "3": ("Ciências, Dados e Tecnologia",  "TIC, Big Data, IoT, Ciência de Dados"),
    "4": ("Engenharias e Arquitetura",     "Civil, Elétrica, Mecânica, Arquitetura"),
    "5": ("Administração e Finanças",      "Contabilidade, Orçamento, Gestão"),
    "6": ("Desenvolvimento Socioeconômico","Economia, Políticas Públicas, Meio Ambiente"),
    "7": ("Justiça e Defesa",              "Direito, Segurança, Defesa Nacional"),
    "8": ("Intermediário — Saúde",         "Questões de nível intermediário"),
    "9": ("Intermediário — Regulação",     "Questões de nível intermediário"),
}

# ---------------------------------------------------------------------------
# NAVBAR (aparece em todas as telas)
# ---------------------------------------------------------------------------
session_info = ""
if st.session_state.stage == 'show_question':
    pct = (st.session_state.score / st.session_state.questions_answered * 100) if st.session_state.questions_answered > 0 else 0
    session_info = f"Sessão · {st.session_state.score}/{st.session_state.questions_answered} ({pct:.0f}%)"

st.markdown(f"""
<div class="navbar">
    <div class="navbar-logo">
        <span class="navbar-logo-icon">🎓</span>
        <span class="navbar-logo-text">StudQuiz</span>
        <span class="navbar-badge">CNPU</span>
    </div>
    <div class="navbar-meta">{session_info}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TELA 1: Seleção de Bloco
# ---------------------------------------------------------------------------
if st.session_state.stage == 'select_block':
    st.markdown('<p class="page-title">Escolha seu Bloco</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Selecione a área temática do CNPU que deseja praticar.</p>', unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, (key, (title, subtitle)) in enumerate(BLOCK_DATA.items()):
        with cols[idx % 3]:
            if st.button(f"**Bloco {key} · {title}**\n\n_{subtitle}_", key=f"bloco_{key}"):
                select_block(key, f"Bloco {key}")
                st.rerun()

# ---------------------------------------------------------------------------
# TELA 2: Seleção de Disciplina
# ---------------------------------------------------------------------------
elif st.session_state.stage == 'select_discipline':
    bloco = st.session_state.selected_block
    block_name = BLOCK_DATA[bloco['id']][0]

    st.markdown(f"""
    <div class="breadcrumb">
        <span>Blocos</span>
        <span>›</span>
        <span style="color:#e6edf3">Bloco {bloco['id']} · {block_name}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="page-title">Escolha a Disciplina</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Filtre por disciplina ou pratique com todas elas misturadas.</p>', unsafe_allow_html=True)

    arquivo_csv = f"csv/bloco_{bloco['id']}.txt"
    disciplinas_raw = carregar_disciplinas_do_bloco(arquivo_csv)
    opcoes = ["Todas as Disciplinas"] + disciplinas_raw

    col_sel, col_btn, col_back = st.columns([3, 1, 1])
    with col_sel:
        escolha = st.selectbox("Disciplina", opcoes, label_visibility="collapsed")
    with col_btn:
        if st.button("Iniciar Quiz →", type="primary"):
            start_quiz(escolha)
            st.rerun()
    with col_back:
        if st.button("← Voltar"):
            reset_to_blocks()
            st.rerun()

# ---------------------------------------------------------------------------
# TELA 3: Geração (intermediária)
# ---------------------------------------------------------------------------
elif st.session_state.stage == 'generate_question':
    generate_new_question()
    st.rerun()

# ---------------------------------------------------------------------------
# TELA 4: Exibição da Questão
# ---------------------------------------------------------------------------
elif st.session_state.stage == 'show_question' and st.session_state.current_question_obj:
    q = st.session_state.current_question_obj
    answered = st.session_state.answer_submitted
    user_idx = st.session_state.user_answer_idx
    stars = "★" * st.session_state.current_difficulty + "☆" * (5 - st.session_state.current_difficulty)

    # ── Linha de status ──
    acc_pct = (st.session_state.score / st.session_state.questions_answered * 100) if st.session_state.questions_answered > 0 else 0
    st.markdown(f"""
    <div class="score-bar">
        <div class="score-item">
            <span class="score-value">{st.session_state.questions_answered}</span>
            <span class="score-label">Respondidas</span>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
            <span class="score-value" style="color:#3fb950">{st.session_state.score}</span>
            <span class="score-label">Acertos</span>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
            <span class="score-value" style="color:#58a6ff">{acc_pct:.0f}%</span>
            <span class="score-label">Aproveitamento</span>
        </div>
        <div class="score-divider"></div>
        <div class="score-item">
            <span class="score-value" style="font-size:1.1rem;color:#f0883e">{stars}</span>
            <span class="score-label">Dificuldade</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Duas colunas ──
    col_q, col_a = st.columns([1, 1], gap="large")

    # ── Coluna esquerda: Enunciado ──
    with col_q:
        st.markdown(f"""
        <div class="question-panel">
            <div class="question-meta">
                <span class="tag tag-discipline">📚 {q.disciplina}</span>
                <span class="tag tag-topic">🗂 {q.topico[:40]}{'...' if len(q.topico) > 40 else ''}</span>
                <span class="tag tag-difficulty">Nível {q.dificuldade}</span>
            </div>
            <div class="question-label">Questão</div>
            <div class="question-text">{q.enunciado}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navegação dentro do quiz
        st.markdown("<br>", unsafe_allow_html=True)
        nav1, nav2 = st.columns(2)
        with nav1:
            if st.button("← Mudar Disciplina"):
                reset_to_disciplines()
                st.rerun()
        with nav2:
            if st.button("⌂ Mudar Bloco"):
                reset_to_blocks()
                st.rerun()

    # ── Coluna direita: Alternativas / Explicação ──
    with col_a:
        if not answered:
            st.markdown('<div class="answer-panel">', unsafe_allow_html=True)
            st.markdown('<div class="answer-panel-title">Escolha a alternativa</div>', unsafe_allow_html=True)

            for i, alt in enumerate(q.alternativas):
                if st.button(
                    f"{LETTERS[i]}     {alt}",
                    key=f"alt_{i}",
                    use_container_width=True
                ):
                    handle_answer(i)
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        else:
            # Resultado
            is_correct = (user_idx == q.resposta_correta_idx)
            result_html = (
                '<div class="result-correct">✅ &nbsp;Resposta Correta! Muito bem!</div>'
                if is_correct else
                '<div class="result-wrong">❌ &nbsp;Resposta Incorreta. Não desista!</div>'
            )

            st.markdown('<div class="answer-panel">', unsafe_allow_html=True)
            st.markdown(result_html, unsafe_allow_html=True)

            # Alternativas com indicação visual
            for i, alt in enumerate(q.alternativas):
                if i == q.resposta_correta_idx:
                    css_class = "alt-correct"
                    letter_style = "background: rgba(46,160,67,0.2); color: #3fb950;"
                elif i == user_idx:
                    css_class = "alt-wrong"
                    letter_style = "background: rgba(218,54,51,0.2); color: #f85149;"
                else:
                    css_class = "alt-neutral"
                    letter_style = ""

                st.markdown(f"""
                <div class="alt-btn {css_class}" style="cursor:default;">
                    <span class="alt-letter" style="{letter_style}">{LETTERS[i]}</span>
                    <span>{alt}</span>
                </div>
                """, unsafe_allow_html=True)

            # Explicação
            st.markdown(f"""
            <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;
                        color:#8b949e;margin:1.5rem 0 0.6rem 0;">💡 Explicação</div>
            <div class="explanation-box">{q.explicacao}</div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Próxima Questão →", type="primary", use_container_width=True):
                st.session_state.stage = 'generate_question'
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)