"""
Modelo de dados para representação estruturada de questões do simulado.
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class Question:
    """
    Representa uma questão de múltipla escolha com todos os seus atributos essenciais.
    
    Por que existe:
    Padroniza a estrutura de dados de uma questão transitada entre a API do Gemini,
    o banco de dados Supabase e os componentes de renderização do Streamlit.
    """
    disciplina: str
    topico: str
    subtopico: str
    dificuldade: int
    enunciado: str
    alternativas: List[str]
    resposta_correta_idx: int  # Índice da resposta correta na lista de alternativas (0 a 4)
    explicacao: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a instância da questão para um dicionário serializável.
        
        Por que existe:
        Facilita a inserção direta dos dados no Supabase e eventuais conversões para JSON.
        """
        return asdict(self)
