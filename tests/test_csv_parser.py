"""
Testes unitários para as funções de leitura e processamento de arquivos do edital.
"""
import os
from utils.csv_disciplines import carregar_disciplinas_do_bloco
from utils.csv_topics import carregar_topico_aleatorio


def test_carregar_disciplinas_do_bloco():
    csv_file = "csv/bloco_1.txt"
    if os.path.exists(csv_file):
        disciplinas = carregar_disciplinas_do_bloco(csv_file)
        assert isinstance(disciplinas, list)
        assert len(disciplinas) > 0


def test_carregar_disciplinas_arquivo_inexistente():
    disciplinas = carregar_disciplinas_do_bloco("csv/inexistente.txt")
    assert disciplinas == []


def test_carregar_topico_aleatorio():
    csv_file = "csv/bloco_1.txt"
    if os.path.exists(csv_file):
        topico = carregar_topico_aleatorio(csv_file)
        assert topico is not None
        assert "Disciplina" in topico
        assert "Tópico" in topico


def test_carregar_topico_aleatorio_com_filtro():
    csv_file = "csv/bloco_1.txt"
    if os.path.exists(csv_file):
        disciplinas = carregar_disciplinas_do_bloco(csv_file)
        if disciplinas:
            topico = carregar_topico_aleatorio(csv_file, disciplina=disciplinas[0])
            assert topico is not None
            assert topico["Disciplina"] == disciplinas[0]


def test_carregar_topico_aleatorio_arquivo_inexistente():
    topico = carregar_topico_aleatorio("csv/inexistente.txt")
    assert topico is None
