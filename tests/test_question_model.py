"""
Testes unitários para o modelo Question e serialização.
"""
from models.question import Question


def test_question_creation_and_to_dict():
    q = Question(
        disciplina="Direito Constitucional",
        topico="Direitos Fundamentais",
        subtopico="Remédios Constitucionais",
        dificuldade=3,
        enunciado="Qual o remédio constitucional cabível contra ilegalidade no direito de ir e vir?",
        alternativas=[
            "Habeas Corpus",
            "Habeas Data",
            "Mandado de Segurança",
            "Mandado de Injunção",
            "Ação Popular"
        ],
        resposta_correta_idx=0,
        explicacao="O Habeas Corpus tutela a liberdade de locomoção."
    )

    assert q.disciplina == "Direito Constitucional"
    assert q.dificuldade == 3
    assert len(q.alternativas) == 5
    assert q.resposta_correta_idx == 0

    d = q.to_dict()
    assert isinstance(d, dict)
    assert d["disciplina"] == "Direito Constitucional"
    assert d["resposta_correta_idx"] == 0
