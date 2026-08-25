"""
Módulo de configuração e autenticação com a API do Google Gemini.
"""
import os
from typing import Optional

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError:
    genai = None
    load_dotenv = None


def configurar_api_gemini() -> bool:
    """
    O que faz:
    Carrega as variáveis de ambiente a partir do arquivo .env, valida a presença
    da GEMINI_API_KEY e inicializa a biblioteca do Google Generative AI.

    Por que existe:
    Isola o processo de autenticação e configuração do SDK do Gemini, permitindo
    que outros módulos validem o acesso à API sem misturar lógica de geração com
    inicialização de credenciais.

    Retorna:
        bool: True se a API foi configurada com sucesso; False caso contrário.
    """
    if load_dotenv is not None:
        load_dotenv()

    if genai is None:
        print("[ERRO] A biblioteca 'google-generativeai' não está instalada.")
        return False

    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("[AVISO] GEMINI_API_KEY não configurada no ambiente ou .env.")
        return False

    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao configurar a API do Gemini: {e}")
        return False
