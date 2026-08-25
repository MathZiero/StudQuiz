"""
Módulo de Fachada para o serviço de Inteligência Artificial Google Gemini.

Por que existe:
Centraliza e re-exporta as funcionalidades de configuração (`configurar_api_gemini`)
e geração (`gerar_pergunta`), permitindo importações limpas nos módulos consumidores.
"""
from services.gemini_config import configurar_api_gemini
from services.gemini_generator import gerar_pergunta

__all__ = ["configurar_api_gemini", "gerar_pergunta"]
