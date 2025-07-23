import csv
import random

def carregar_topico_aleatorio(caminho_arquivo_csv: str) -> dict:
    """
    Lê um arquivo CSV e retorna uma linha (tópico) aleatória.

    Args:
        caminho_arquivo_csv: O caminho para o arquivo .csv.

    Returns:
        Um dicionário representando uma linha aleatória do CSV, ou None se o arquivo estiver vazio.
    """
    try:
        with open(caminho_arquivo_csv, mode='r', encoding='utf-8') as file:
            # Usando DictReader para facilitar o acesso às colunas pelo nome
            reader = csv.DictReader(file)
            topicos = list(reader)
            if not topicos:
                return None
            return random.choice(topicos)
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{caminho_arquivo_csv}'")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo CSV: {e}")
        return None

