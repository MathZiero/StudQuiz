"""
Módulo de Fachada para Utilitários de Leitura e Parsing de Arquivos do CNPU.

Por que existe:
Centraliza a interface pública de utilitários CSV do projeto (`carregar_disciplinas_do_bloco`
e `carregar_topico_aleatorio`) para permitir importações simplificadas.
"""
from utils.csv_disciplines import carregar_disciplinas_do_bloco
from utils.csv_topics import carregar_topico_aleatorio

__all__ = ["carregar_disciplinas_do_bloco", "carregar_topico_aleatorio"]
