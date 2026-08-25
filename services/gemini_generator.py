"""
Módulo gerador de questões via Google Gemini API.
"""
import os
import json
from typing import Any
from models.question import Question
from services.gemini_config import configurar_api_gemini

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def _limpar_campo(val: Any) -> str:
    """
    O que faz:
    Converte valores nulos, None, NaN ou floats em string limpa sem espaços extras.

    Por que existe:
    Evita erros de concatenação no prompt quando linhas lidas do CSV possuem campos
    opcionais vazios (como a coluna 'Subtópico').
    """
    if val is None or (isinstance(val, float) and val != val):
        return ""
    return str(val).strip()


def gerar_pergunta(disciplina: str, topico: str, subtopico: str, dificuldade: int) -> Question:
    """
    O que faz:
    Monta um prompt estruturado com as diretrizes de concurso público, envia para o
    modelo da Google (Gemini), processa a resposta em formato JSON e retorna uma
    instância do modelo `Question`.

    Por que existe:
    É o motor central de geração de conteúdo inteligente da aplicação. Permite criar
    questões inéditas, contextualizadas e no nível de dificuldade adaptativo solicitado.

    Argumentos:
        disciplina: Nome da matéria/disciplina temática.
        topico: Tópico específico do edital.
        subtopico: Subtópico ou detalhamento do tema (opcional).
        dificuldade: Nível de cobrança de 1 a 5.

    Retorna:
        Question: Objeto populado com enunciado, 5 alternativas, índice correto e explicação.

    Lança:
        RuntimeError: Se a chave da API não estiver configurada ou se ocorrer erro na resposta do Gemini.
    """
    disciplina_limpa = _limpar_campo(disciplina)
    topico_limpo = _limpar_campo(topico)
    subtopico_limpo = _limpar_campo(subtopico)

    if not genai or not configurar_api_gemini():
        raise RuntimeError("A API do Gemini não está configurada corretamente (chave ausente ou biblioteca não instalada).")

    # Modelo Gemini configurável via variável de ambiente ou padrão gemini-1.5-flash
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)

    # Inclusão condicional do subtópico apenas se preenchido
    texto_subtopico = f" e focando especificamente no subtópico '{subtopico_limpo}'" if subtopico_limpo else ""

    prompt = f"""
Você é uma banca examinadora sênior especializada em elaboração de questões de alto nível para concursos públicos federais no Brasil (como o Concurso Nacional Unificado - CNPU).

Crie uma pergunta inédita e de alta qualidade com as seguintes especificações:
- **Disciplina**: {disciplina_limpa}
- **Tópico**: {topico_limpo}{texto_subtopico}
- **Nível de Dificuldade**: {dificuldade} (em uma escala de 1 a 5, onde 1 = conceitual e direta; 3 = nível médio de concurso; 5 = caso prático complexo com pegadinhas doutrinárias e raciocínio avançado).

REGRAS OBRIGATÓRIAS:
1. A pergunta deve conter um **enunciado bem articulado** (pode conter uma situação hipotética se a dificuldade for >= 3).
2. Forneça exatamente **5 alternativas** (índices 0 a 4 correspondentes a A, B, C, D, E).
3. Apenas UMA alternativa deve ser correta. As 4 alternativas incorretas devem ser distratores plausíveis e fundamentados no tema.
4. Forneça uma **explicação detalhada e didática** justificando a resposta correta e apontando o erro das demais.
5. Retorne **EXCLUSIVAMENTE** um JSON válido com o seguinte formato, sem marcações adicionais ou textos fora do JSON:

{{
  "enunciado": "Texto completo da questão...",
  "alternativas": [
    "Alternativa A",
    "Alternativa B",
    "Alternativa C",
    "Alternativa D",
    "Alternativa E"
  ],
  "resposta_correta_idx": 0,
  "explicacao": "Justificativa detalhada..."
}}
"""

    try:
        print(f"\n--- (Gemini API) Gerando pergunta [{model_name}] para: {disciplina_limpa} - {topico_limpo} (Dificuldade {dificuldade}) ---")
        response = model.generate_content(prompt)

        response_text = response.text.strip()
        cleaned_json_text = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned_json_text)

        return Question(
            disciplina=disciplina_limpa,
            topico=topico_limpo,
            subtopico=subtopico_limpo,
            dificuldade=dificuldade,
            enunciado=data["enunciado"],
            alternativas=data["alternativas"],
            resposta_correta_idx=int(data["resposta_correta_idx"]),
            explicacao=data["explicacao"]
        )
    except Exception as e:
        print(f"[ERRO] Falha ao processar resposta da API Gemini: {e}")
        raise RuntimeError(f"Erro ao gerar questão via Gemini: {e}") from e
