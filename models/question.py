from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Question:
    """
    Representa uma questão de múltipla escolha com todos os seus atributos.
    """
    disciplina: str
    topico: str
    subtopico: str
    dificuldade: int
    enunciado: str
    alternativas: List[str]
    resposta_correta_idx: int  # Índice da resposta correta na lista de alternativas (0 a 4)
    explicacao: str

    def to_dict(self):
        """Converte a instância da classe para um dicionário."""
        return asdict(self)

