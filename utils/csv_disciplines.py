"""
Módulo de leitura e extração de disciplinas a partir dos arquivos do edital.
"""
from typing import List
import pandas as pd


def carregar_disciplinas_do_bloco(caminho_arquivo_csv: str) -> List[str]:
    """
    O que faz:
    Lê o arquivo CSV/TXT formatado de um bloco temático específico, extrai todos os valores
    únicos da coluna 'Disciplina' e os retorna em ordem alfabética.

    Por que existe:
    Permite que a interface do Streamlit popule dinamicamente as opções de disciplinas
    disponíveis para o bloco temático selecionado pelo usuário.

    Argumentos:
        caminho_arquivo_csv: Caminho para o arquivo de texto/CSV do bloco (ex: 'csv/bloco_1.txt').

    Retorna:
        List[str]: Lista ordenada com os nomes das disciplinas encontradas, ou lista vazia se falhar.
    """
    try:
        df = pd.read_csv(caminho_arquivo_csv)
        if 'Disciplina' not in df.columns:
            return []
        disciplinas = df['Disciplina'].dropna().unique().tolist()
        return sorted(disciplinas)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de bloco não encontrado em '{caminho_arquivo_csv}'")
        return []
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro ao carregar as disciplinas: {e}")
        return []
