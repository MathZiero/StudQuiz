"""
Testes unitários para o serviço de integração com Supabase.
"""
from unittest.mock import MagicMock
from services.supabase_service import SupabaseService
from models.question import Question


def test_supabase_service_salvar_questao_sem_cliente():
    service = SupabaseService()
    service.client = None
    q = Question("Dir", "Top", "", 1, "Enunciado", ["A", "B", "C", "D", "E"], 0, "Exp")
    result = service.salvar_questao_no_banco(q, "Bloco 1")
    assert result is None


def test_supabase_service_salvar_resposta_usuario_sem_cliente():
    service = SupabaseService()
    service.client = None
    result = service.salvar_resposta_usuario("sess_123", "q_456", 0, True)
    assert result is False


def test_supabase_service_buscar_questao_existente_sem_cliente():
    service = SupabaseService()
    service.client = None
    result = service.buscar_questao_existente("Dir", "Top", "", 1)
    assert result is None


def test_supabase_service_buscar_questao_existente_com_mock():
    service = SupabaseService()
    mock_client = MagicMock()
    mock_query = MagicMock()
    
    mock_query.execute.return_value.data = [{
        "id": "uuid-123",
        "disciplina": "Direito",
        "topico": "Constitucional",
        "subtopico": "",
        "dificuldade": 2,
        "enunciado": "Enunciado teste",
        "alternativas": ["A", "B", "C", "D", "E"],
        "resposta_correta_idx": 1,
        "explicacao": "Explicação teste"
    }]
    mock_query.eq.return_value = mock_query
    mock_client.table.return_value.select.return_value = mock_query

    service.client = mock_client
    result = service.buscar_questao_existente("Direito", "Constitucional", "", 2)

    assert result is not None
    q, q_id = result
    assert q.enunciado == "Enunciado teste"
    assert q_id == "uuid-123"
