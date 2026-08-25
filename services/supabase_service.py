"""
Módulo de integração com a plataforma Supabase (Banco de Dados PostgreSQL e Autenticação).
"""
import os
from typing import Optional, Tuple, Dict, Any

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv = None


class SupabaseService:
    """
    Serviço centralizado para persistência de questões, histórico de respostas e autenticação.

    Por que existe:
    Isola a comunicação com a API do Supabase em uma única camada de acesso a dados (DAO),
    garantindo que o resto da aplicação não dependa de chamadas diretas de banco de dados.
    """

    def __init__(self):
        """
        O que faz:
        Lê as configurações de URL e chaves do Supabase a partir das variáveis de ambiente
        e inicializa o cliente oficial do Supabase.

        Por que existe:
        Garante uma conexão única e reutilizável pelo singleton `supabase_service`.
        """
        url = os.getenv("SUPABASE_URL")
        # Prioriza a chave de serviço (service role) se disponível, ou a chave pública anônima
        key = os.getenv("supabase_sec") or os.getenv("SUPABASE_KEY")

        if url:
            url = url.strip()
            if url.endswith("/rest/v1/"):
                url = url.replace("/rest/v1/", "")
            elif url.endswith("/rest/v1"):
                url = url.replace("/rest/v1", "")

        if not url or not key or not create_client:
            print("[AVISO] SUPABASE_URL, chaves ou biblioteca supabase não configuradas.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(url, key)
                print("[INFO] Cliente Supabase inicializado com sucesso.")
            except Exception as e:
                print(f"[ERRO] Erro ao inicializar o cliente Supabase: {e}")
                self.client = None

    # --- Métodos de Autenticação ---
    def login_user(self, email: str, password: str) -> Optional[Dict[str, str]]:
        """
        O que faz:
        Realiza login de um usuário utilizando e-mail e senha no Supabase Auth.

        Por que existe:
        Permite futura autenticação de usuários para salvar histórico individual.
        """
        if not self.client:
            return None
        try:
            response = self.client.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                return {'email': response.user.email, 'uid': response.user.id}
        except Exception as e:
            print(f"[ERRO] Falha ao fazer login: {e}")
        return None

    def register_user(self, email: str, password: str) -> Optional[Dict[str, str]]:
        """
        O que faz:
        Registra uma nova conta de usuário no Supabase Auth.

        Por que existe:
        Permite o cadastro de novos usuários na plataforma.
        """
        if not self.client:
            return None
        try:
            response = self.client.auth.sign_up({"email": email, "password": password})
            if response.user:
                return {'email': response.user.email, 'uid': response.user.id}
        except Exception as e:
            print(f"[ERRO] Falha ao registrar usuário: {e}")
        return None

    # --- Métodos de Banco de Dados ---
    def salvar_questao_no_banco(self, question_obj, bloco_tematico: str) -> Optional[str]:
        """
        O que faz:
        Calcula o hash SHA-256 do enunciado (para controle de duplicidade) e insere a questão
        gerada na tabela 'questoes' do Supabase.

        Por que existe:
        Persiste as questões geradas pela IA no banco de dados para permitir o reaproveitamento
        futuro e construir progressivamente um repositório rico de questões do CNPU.

        Retorna:
            str: O ID (UUID) da questão recém-salva ou None em caso de falha.
        """
        if not self.client:
            print("[AVISO] Conexão com Supabase inativa. A questão não foi salva.")
            return None

        try:
            import hashlib
            question_data = question_obj.to_dict()
            question_data['bloco_tematico'] = bloco_tematico

            enunciado_hash = hashlib.sha256(question_data['enunciado'].encode()).hexdigest()
            question_data['hash'] = enunciado_hash

            # Insere no Supabase e obtém o ID gerado
            response = self.client.table('questoes').insert(question_data).execute()
            if response.data:
                question_id = response.data[0]['id']
                print(f"✅ Pergunta (Bloco: {bloco_tematico}) salva no banco com ID: {question_id}")
                return str(question_id)
            return None
        except Exception as e:
            print(f"[ERRO] Erro ao salvar questão no Supabase: {e}")
            return None

    def buscar_questao_existente(self, disciplina: str, topico: str, subtopico: str = "", dificuldade: int = 1):
        """
        O que faz:
        Consulta a tabela 'questoes' buscando perguntas salvas que correspondam à disciplina,
        tópico e dificuldade selecionados. Sorteia aleatoriamente uma das opções encontradas.

        Por que existe:
        Reutiliza questões já armazenadas para acelerar o tempo de resposta do quiz e economizar
        chamadas à API do Gemini.

        Retorna:
            tuple[Question, str] | None: Tupla contendo o objeto Question e seu ID do banco, ou None.
        """
        if not self.client:
            return None

        try:
            from models.question import Question
            import random

            query = self.client.table('questoes').select('*').eq('disciplina', disciplina).eq('topico', topico)
            if dificuldade:
                query = query.eq('dificuldade', dificuldade)

            response = query.execute()

            if response.data and len(response.data) > 0:
                item = random.choice(response.data)
                question_obj = Question(
                    disciplina=item.get('disciplina', disciplina),
                    topico=item.get('topico', topico),
                    subtopico=item.get('subtopico', subtopico),
                    dificuldade=item.get('dificuldade', dificuldade),
                    enunciado=item.get('enunciado', ''),
                    alternativas=item.get('alternativas', []),
                    resposta_correta_idx=item.get('resposta_correta_idx', 0),
                    explicacao=item.get('explicacao', '')
                )
                question_id = str(item.get('id'))
                print(f"📦 Questão reutilizada do banco de dados (ID: {question_id})")
                return question_obj, question_id
        except Exception as e:
            print(f"[AVISO] Falha ao consultar questões reutilizáveis no Supabase: {e}")

        return None

    def salvar_resposta_usuario(self, session_id: str, question_id: str, user_answer_idx: int, is_correct: bool) -> bool:
        """
        O que faz:
        Grava o registro de resposta do candidato na tabela 'respostas_usuarios'. Possui fallback
        automático caso a tabela do banco não contenha a coluna 'session_id'.

        Por que existe:
        Permite manter o histórico de acertos e erros de cada questão para cômputo de estatísticas.

        Retorna:
            bool: True se gravado com sucesso, False caso contrário.
        """
        if not self.client or not question_id:
            if not question_id:
                print("[AVISO] ID da questão é nulo. A resposta não foi salva.")
            return False

        # Tenta salvar primeiro incluindo a session_id
        try:
            data = {
                "session_id": session_id,
                "question_id": question_id,
                "resposta_usuario_idx": user_answer_idx,
                "acertou": is_correct
            }
            self.client.table('respostas_usuarios').insert(data).execute()
            print(f"✅ Resposta do usuário para a questão {question_id} salva.")
            return True
        except Exception as e:
            err_str = str(e)
            # Se a coluna 'session_id' não existir no banco, tenta gravar sem ela
            if "session_id" in err_str or "PGRST204" in err_str:
                try:
                    data_sem_sessao = {
                        "question_id": question_id,
                        "resposta_usuario_idx": user_answer_idx,
                        "acertou": is_correct
                    }
                    self.client.table('respostas_usuarios').insert(data_sem_sessao).execute()
                    print(f"✅ Resposta do usuário para a questão {question_id} salva (sem session_id).")
                    return True
                except Exception as ex2:
                    print(f"[ERRO] Erro ao salvar resposta do usuário: {ex2}")
                    return False
            else:
                print(f"[ERRO] Erro ao salvar resposta do usuário no Supabase: {e}")
                return False


# Instância singleton do serviço Supabase para uso em toda a aplicação
supabase_service = SupabaseService()
