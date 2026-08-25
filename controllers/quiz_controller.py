"""
Controlador de fluxo e gerenciamento de estado do simulado (Streamlit Session State).
"""
from typing import Dict, Any
import streamlit as st
from utils.csv_topics import carregar_topico_aleatorio
from services.gemini_generator import gerar_pergunta
from services.supabase_service import supabase_service


def reset_to_blocks() -> None:
    """
    O que faz:
    Reinicia o estado da sessão para a tela inicial de seleção de blocos temáticos
    e reseta os contadores de pontuação e dificuldade.

    Por que existe:
    Permite ao usuário abandonar o simulado atual e escolher outro bloco temático a qualquer momento.
    """
    st.session_state.stage = 'select_block'
    st.session_state.score = 0
    st.session_state.questions_answered = 0
    st.session_state.current_difficulty = 1


def reset_to_disciplines() -> None:
    """
    O que faz:
    Retorna o usuário para a tela de seleção de disciplinas mantendo o bloco selecionado.

    Por que existe:
    Permite trocar de matéria dentro do mesmo bloco sem precisar refazer a escolha do bloco inicial.
    """
    st.session_state.stage = 'select_discipline'
    st.session_state.score = 0
    st.session_state.questions_answered = 0
    st.session_state.current_difficulty = 1


def select_block(block_id: str, block_name: str) -> None:
    """
    O que faz:
    Registra o bloco selecionado no session state do Streamlit e transita o fluxo
    para a etapa de seleção de disciplinas.

    Por que existe:
    Guarda o contexto do bloco para direcionar o carregamento do arquivo de conteúdo correspondente.
    """
    st.session_state.selected_block = {'id': block_id, 'name': block_name}
    st.session_state.stage = 'select_discipline'


def start_quiz(discipline: str) -> None:
    """
    O que faz:
    Armazena a disciplina escolhida e dispara o estágio de geração/obtenção da primeira questão.

    Por que existe:
    Inicia formalmente a rodada de simulado com os filtros definidos pelo usuário.
    """
    st.session_state.selected_discipline = discipline
    st.session_state.stage = 'generate_question'


def generate_new_question() -> None:
    """
    O que faz:
    Carrega um tópico do bloco e busca prioritariamente uma questão pré-existente no Supabase.
    Caso não exista, gera uma nova com a IA (Gemini) e a salva no banco de dados para reutilização futura.

    Por que existe:
    Implementa a estratégia de cache/banco de questões: reduz a latência e o consumo de tokens
    da API do Gemini à medida que o banco de dados cresce.
    """
    arquivo_csv = f"csv/bloco_{st.session_state.selected_block['id']}.txt"
    with st.spinner("Carregando questão..."):
        topico = carregar_topico_aleatorio(arquivo_csv, st.session_state.selected_discipline)
        if topico:
            disciplina = topico.get('Disciplina', '')
            topico_nome = topico.get('Tópico', '')
            subtopico = topico.get('Subtópico', '')
            dificuldade = st.session_state.current_difficulty

            # 1. Tenta buscar uma questão pré-existente no banco de dados
            resultado_banco = supabase_service.buscar_questao_existente(
                disciplina=disciplina,
                topico=topico_nome,
                subtopico=subtopico,
                dificuldade=dificuldade
            )

            if resultado_banco:
                question_obj, question_id = resultado_banco
            else:
                # 2. Se não encontrou no banco, gera uma nova com a IA e salva no banco
                try:
                    question_obj = gerar_pergunta(
                        disciplina=disciplina,
                        topico=topico_nome,
                        subtopico=subtopico,
                        dificuldade=dificuldade
                    )
                    question_id = supabase_service.salvar_questao_no_banco(
                        question_obj, st.session_state.selected_block['name']
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar questão com IA: {e}")
                    st.session_state.stage = 'select_discipline'
                    return

            st.session_state.current_question_obj = question_obj
            st.session_state.current_question_id = question_id
            st.session_state.answer_submitted = False
            st.session_state.user_answer_idx = None
            st.session_state.stage = 'show_question'
        else:
            st.error(f"Não foi possível carregar um tópico para '{st.session_state.selected_discipline}'.")
            st.session_state.stage = 'select_discipline'


def handle_answer(user_answer_idx: int) -> None:
    """
    O que faz:
    Compara a alternativa selecionada com o gabarito oficial da questão, atualiza o placar
    e ajusta a dificuldade dinamicamente (aumenta em caso de acerto, diminui em caso de erro),
    além de registrar a resposta no Supabase.

    Por que existe:
    Fornece a lógica adaptativa do simulado (gamificação e calibração de nível) e garante
    a persistência das respostas para análise de desempenho.
    """
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
