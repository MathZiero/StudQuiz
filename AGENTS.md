# AGENTS.md — Arquitetura do Projeto & Regras de Desenvolvimento

## 1. Visão Geral da Arquitetura

O **StudQuiz CNPU** é uma aplicação interativa desenvolvida em Python para geração e resolução de questões de simulados adaptativos voltados ao Concurso Nacional Unificado (CNPU).

### Estrutura de Diretórios
```
estuda_cnpu/
├── AGENTS.md                  # Guia de Arquitetura e Regras de Desenvolvimento (este arquivo)
├── app.py                     # Interface gráfica principal em Streamlit (somente UI/Layout)
├── controllers/
│   └── quiz_controller.py     # Gerenciamento de fluxo de sessão do quiz (Streamlit session state)
├── models/
│   └── question.py            # Dataclass Question (estrutura de dados das questões)
├── services/
│   ├── gemini_config.py       # Configuração e autenticação da API Google Gemini
│   ├── gemini_generator.py    # Geração de perguntas via Gemini com prompts calibrados e parse de JSON
│   ├── gemini.py              # Fachada / Re-export do serviço Gemini
│   └── supabase_service.py    # Integração com banco de dados Supabase (persistência de questões e respostas)
├── utils/
│   ├── csv_disciplines.py     # Leitura e parsing de disciplinas a partir de CSVs
│   ├── csv_topics.py          # Seleção aleatória e filtrada de tópicos a partir de CSVs
│   └── parser.py              # Fachada / Re-exports de utilitários CSV
├── csv/                       # Arquivos CSV/TXT contendo o edital codificado dos blocos temáticos
└── tests/                     # Suíte de testes unitários e de integração (Pytest)
```

---

## 2. Regra Mandatória: Test Driven Development (TDD)

Todas as contribuições e modificações no projeto devem seguir rigorosamente o princípio de **Test-Driven Development (TDD)**.

### Diretrizes de TDD do Projeto:
1. **Nenhuma funcionalidade sem testes**: Toda função, serviço ou utilitário criado ou alterado DEVE conter testes unitários ou de integração correspondentes na pasta `tests/`.
2. **Sem regressões (Zero Red Tests)**: Nenhuma alteração deve ser mesclada ou considerada concluída se algum teste da suíte falhar.
3. **Execução de testes contínua**: Sempre execute `pytest` após realizar modificações no código.

### Comando para Executar a Suíte de Testes:
```bash
pytest
```

---

## 3. Padrões de Código e Organização

- **Single Responsibility Principle (SRP)**: Funções isoladas devem residir em arquivos/módulos dedicados com responsabilidades bem definidas.
- **Tratamento Seguro de APIs**: Chamadas a APIs externas (Gemini, Supabase) devem possuir tratamento de exceções robusto. Não são permitidos fallbacks silenciosos ou perguntas fakes/simuladas ocultas.
- **Tipagem Estática (Type Hints)**: Utilize Type Hints do Python (`str`, `int`, `dict`, `List`, `Optional`) em todas as assinaturas de funções.
