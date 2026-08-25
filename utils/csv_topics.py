"""
Módulo de sorteio e filtragem de tópicos a partir dos arquivos do edital.
"""
from typing import Optional, Dict, Any
import pandas as pd


def carregar_topico_aleatorio(caminho_arquivo_csv: str, disciplina: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    O que faz:
    Lê o arquivo de dados do bloco, filtra opcionalmente por uma disciplina específica e sorteia
    aleatoriamente uma linha da tabela, retornando um dicionário com Disciplina, Tópico e Subtópico.

    Por que existe:
    Fornece o conteúdo temático do edital necessário para guiar a IA na elaboração de uma questão
    ou para buscar questões salvas no banco com metadados idênticos.

    Argumentos:
        caminho_arquivo_csv: Caminho para o arquivo CSV/TXT do bloco.
        disciplina: Nome da disciplina para filtro, ou 'Todas as Disciplinas' / None para todas.

    Retorna:
        Dict[str, Any] | None: Dicionário contendo os dados da linha sorteada, ou None se indisponível.
    """
    try:
        df = pd.read_csv(caminho_arquivo_csv)

        if disciplina and disciplina != "Todas as Disciplinas":
            df_filtrado = df[df['Disciplina'] == disciplina]
        else:
            df_filtrado = df

        if df_filtrado.empty:
            return None

        topico_aleatorio = df_filtrado.sample(n=1).to_dict('records')[0]
        return topico_aleatorio

    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado em '{caminho_arquivo_csv}'")
        return None
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro ao ler o arquivo CSV: {e}")
        return None
