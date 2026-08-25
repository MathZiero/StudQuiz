# StudQuiz CNPU

Plataforma interativa de simulados adaptativos para o **Concurso Nacional Unificado (CNPU)**. A aplicação gera questões inéditas por disciplina e tópico do edital utilizando a API do Google Gemini, além de persistir e reutilizar automaticamente as questões geradas em um banco de dados Supabase.

---

## Como Funciona

1. **Seleção de Bloco e Disciplina**: O candidato escolhe entre os 9 Blocos Temáticos do CNPU e seleciona uma disciplina específica ou o modo com todas as matérias misturadas.
2. **Consulta e Geração Inteligente**:
   - O sistema sorteia um tópico oficial do edital.
   - Primeiro, verifica se já existe uma questão correspondente na tabela do **Supabase**. Se existir, a questão é carregada imediatamente sem consumir a cota da IA.
   - Se ainda não houver questão salva para o tópico e nível selecionados, a **API do Gemini** gera uma pergunta inédita de 5 alternativas com distratores plausíveis e explicação detalhada, salvando-a no banco para uso futuro.
3. **Simulado Adaptativo**:
   - A cada acerto, o nível de dificuldade aumenta (de 1 a 5).
   - Em caso de erro, o nível de dificuldade é reduzido para reforçar a base teórica.
4. **Feedback Imediato**: Exibição da resposta correta com justificativa fundamentada e atualização do placar de aproveitamento em tempo real.

---

## Estrutura do Projeto

```text
estuda_cnpu/
├── app.py                     # Interface gráfica (Streamlit)
├── controllers/
│   └── quiz_controller.py     # Gerenciador de fluxo e estado do simulado
├── models/
│   └── question.py            # Dataclass Question (estrutura dos dados de questões)
├── services/
│   ├── gemini_config.py       # Autenticação e configuração da API Gemini
│   ├── gemini_generator.py    # Geração de perguntas via prompt estruturado
│   ├── gemini.py              # Fachada dos serviços Gemini
│   └── supabase_service.py    # Persistência e busca de questões/respostas no Supabase
├── utils/
│   ├── csv_disciplines.py     # Leitura e ordenação de disciplinas dos blocos
│   ├── csv_topics.py          # Sorteio e filtragem de tópicos do edital
│   └── parser.py              # Fachada dos utilitários de arquivos
├── csv/                       # Editais codificados dos Blocos 1 a 9
├── tests/                     # Suíte de testes automatizados com Pytest
├── AGENTS.md                  # Regras de arquitetura e diretrizes de TDD
└── pyproject.toml             # Dependências e metadados do projeto
```

---

## Tecnologias Utilizadas

- **Python 3.12+**
- **[Streamlit](https://streamlit.io/)**: Interface web reativa em Dark Mode customizado.
- **[Google Generative AI (Gemini)](https://ai.google.dev/)**: Motor de elaboração de questões e explicações pedagógicas.
- **[Supabase](https://supabase.com/)**: Banco de dados PostgreSQL para armazenamento e reaproveitamento de questões.
- **[Pandas](https://pandas.pydata.org/)**: Processamento e filtragem das matrizes de tópicos dos editais.
- **[uv](https://github.com/astral-sh/uv)**: Gerenciamento rápido de dependências e ambientes virtuais.
- **[Pytest](https://docs.pytest.org/)**: Suíte de testes com mocks para garantir estabilidade e padrão TDD.

---

