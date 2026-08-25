import json
from unittest.mock import MagicMock, patch
import pytest
from services.gemini_generator import gerar_pergunta
from models.question import Question


def test_gerar_pergunta_com_mock(monkeypatch):
    mock_json_response = json.dumps({
        "enunciado": "Questão teste de estatística",
        "alternativas": ["A1", "B2", "C3", "D4", "E5"],
        "resposta_correta_idx": 2,
        "explicacao": "Explicação teste"
    })

    mock_response = MagicMock()
    mock_response.text = mock_json_response

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    with patch("services.gemini_generator.configurar_api_gemini", return_value=True), \
         patch("services.gemini_generator.genai") as mock_genai:
        mock_genai.GenerativeModel.return_value = mock_model

        q = gerar_pergunta("Estatística", "Probabilidade", "", 3)

        assert isinstance(q, Question)
        assert q.disciplina == "Estatística"
        assert q.topico == "Probabilidade"
        assert q.enunciado == "Questão teste de estatística"
        assert q.resposta_correta_idx == 2
        assert len(q.alternativas) == 5


def test_gerar_pergunta_sem_api_configurada():
    with patch("services.gemini_generator.configurar_api_gemini", return_value=False):
        with pytest.raises(RuntimeError) as exc_info:
            gerar_pergunta("Direito", "Constitucional", "", 1)
        assert "A API do Gemini não está configurada" in str(exc_info.value)
