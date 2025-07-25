import pandas as pd

def carregar_disciplinas_do_bloco(caminho_arquivo_csv: str) -> list:
    """
    Lê um arquivo CSV de um bloco e retorna uma lista única de disciplinas.
    """
    try:
        df = pd.read_csv(caminho_arquivo_csv)
        # Pega os valores únicos da coluna 'Disciplina' e converte para lista
        disciplinas = df['Disciplina'].unique().tolist()
        return sorted(disciplinas) # Retorna em ordem alfabética
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{caminho_arquivo_csv}'")
        return []
    except Exception as e:
        print(f"Ocorreu um erro ao carregar as disciplinas: {e}")
        return []

def carregar_topico_aleatorio(caminho_arquivo_csv: str, disciplina: str = None) -> dict:
    """
    Lê um arquivo CSV e retorna um tópico aleatório.
    Pode filtrar por uma disciplina específica.
    """
    try:
        df = pd.read_csv(caminho_arquivo_csv)
        
        # Filtra por disciplina se uma for fornecida e não for "Todas as Disciplinas"
        if disciplina and disciplina != "Todas as Disciplinas":
            df_filtrado = df[df['Disciplina'] == disciplina]
        else:
            df_filtrado = df
            
        if df_filtrado.empty:
            return None
            
        # Seleciona uma linha aleatória do dataframe (filtrado ou não)
        topico_aleatorio = df_filtrado.sample(n=1).to_dict('records')[0]
        return topico_aleatorio
        
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{caminho_arquivo_csv}'")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo CSV: {e}")
        return None
