import os
import json
from models.question import Question

# Tenta importar as bibliotecas. Se não conseguir, usaremos a simulação.
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError:
    genai = None
    load_dotenv = None

def _configurar_api_gemini():
    """
    Carrega a chave da API do Gemini a partir de um arquivo .env e configura a API.
    Retorna True se bem-sucedido, False caso contrário.
    """
    if not load_dotenv:
        return False

    load_dotenv()  # Carrega as variáveis do arquivo .env para o ambiente
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "SUA_CHAVE_API_AQUI":
        return False

    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Erro ao configurar a API do Gemini: {e}")
        return False

def gerar_pergunta(disciplina: str, topico: str, subtopico: str, dificuldade: int) -> Question:
    """
    Gera uma pergunta de concurso utilizando a API do Gemini.
    Se a API não estiver configurada, recorre à função simulada.
    """
    if not genai or not _configurar_api_gemini():
        print("\nAVISO: API do Gemini não configurada. Usando dados de simulação.")
        return _gerar_pergunta_simulada(disciplina, topico, subtopico, dificuldade)

    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    prompt = f"""
    Aja como um especialista em elaboração de questões para concursos públicos no Brasil.
    Crie uma pergunta de concurso público, com nível de dificuldade {dificuldade} (em uma escala de 1 a 5), sobre a disciplina de '{disciplina}', focando no tópico '{topico}' e, se houver, no subtópico '{subtopico}'.

    A pergunta deve ter exatamente 5 alternativas (A, B, C, D, E), sendo apenas uma correta. As alternativas erradas devem ser plausíveis e relacionadas ao tema, para testar o conhecimento do candidato.

    Sua resposta deve ser **exclusivamente um objeto JSON válido**, sem nenhum texto ou formatação adicional antes ou depois dele. O JSON deve ter a seguinte estrutura:
    {{
      "enunciado": "O texto da pergunta aqui.",
      "alternativas": [
        "Texto da alternativa A.",
        "Texto da alternativa B.",
        "Texto da alternativa C.",
        "Texto da alternativa D.",
        "Texto da alternativa E."
      ],
      "resposta_correta_idx": <índice da resposta correta, de 0 a 4>,
      "explicacao": "Uma explicação clara e detalhada do porquê a alternativa correta está certa e, se possível, por que as outras estão erradas."
    }}
    """

    try:
        print(f"\n--- (Gemini API) Gerando pergunta para: {disciplina} - {topico} ---")
        response = model.generate_content(prompt)
        
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned_response_text)

        return Question(
            disciplina=disciplina,
            topico=topico,
            subtopico=subtopico,
            dificuldade=dificuldade,
            enunciado=data["enunciado"],
            alternativas=data["alternativas"],
            resposta_correta_idx=data["resposta_correta_idx"],
            explicacao=data["explicacao"]
        )
    except Exception as e:
        print(f"Erro ao gerar ou processar a pergunta da API do Gemini: {e}")
        print("Retornando a uma pergunta simulada.")
        return _gerar_pergunta_simulada(disciplina, topico, subtopico, dificuldade)

def _gerar_pergunta_simulada(disciplina: str, topico: str, subtopico: str, dificuldade: int) -> Question:
    """
    Função de fallback que gera uma pergunta estática caso a API do Gemini falhe.
    """
    return Question(
        disciplina=disciplina,
        topico=topico,
        subtopico=subtopico,
        dificuldade=dificuldade,
        enunciado="(Pergunta Simulada) Qual princípio da Seguridade Social garante que ela seja financiada por toda a sociedade?",
        alternativas=[
            "Princípio da Universalidade da Cobertura",
            "Princípio da Solidariedade",
            "Princípio da Equidade na Forma de Participação no Custeio",
            "Princípio da Seletividade e Distributividade",
            "Princípio do Caráter Democrático"
        ],
        resposta_correta_idx=1,
        explicacao="(Explicação Simulada) O princípio da Solidariedade estabelece que a seguridade social é responsabilidade de todos, financiada por contribuições de toda a sociedade para garantir a proteção social."
    )
