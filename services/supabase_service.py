import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        # Prioriza a chave secreta (service role) para operações do servidor
        key = os.getenv("supabase_sec") or os.getenv("SUPABASE_KEY")
        
        if url:
            url = url.strip()
            if url.endswith("/rest/v1/"):
                url = url.replace("/rest/v1/", "")
            elif url.endswith("/rest/v1"):
                url = url.replace("/rest/v1", "")

        if not url or not key:
            print("[AVISO] SUPABASE_URL ou chaves de autenticação não configuradas no arquivo .env.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(url, key)
                print("[INFO] Cliente Supabase inicializado com sucesso.")
            except Exception as e:

                print(f"[ERRO] Erro ao inicializar o cliente Supabase: {e}")
                self.client = None


    # --- Autenticação (Substitutos de Pyrebase/Firebase Auth) ---
    def login_user(self, email, password):
        if not self.client:
            return None
        try:
            response = self.client.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                return {'email': response.user.email, 'uid': response.user.id}
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
            return None

    def register_user(self, email, password):
        if not self.client:
            return None
        try:
            response = self.client.auth.sign_up({"email": email, "password": password})
            if response.user:
                return {'email': response.user.email, 'uid': response.user.id}
        except Exception as e:
            print(f"Erro ao registrar: {e}")
            return None

    # --- Métodos de Banco de Dados (Substitutos do Firestore) ---
    def salvar_questao_no_banco(self, question_obj, bloco_tematico: str) -> str:
        """
        Salva uma pergunta na tabela 'questoes', incluindo o bloco temático e o hash do enunciado.
        """
        if not self.client:
            print("🔥 AVISO: Conexão com Supabase falhou. A questão não foi salva.")
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
            print(f"❌ Erro ao salvar questão no Supabase: {e}")
            return None

    def salvar_resposta_usuario(self, session_id: str, question_id: str, user_answer_idx: int, is_correct: bool):
        """
        Salva a resposta associada a uma session_id específica na tabela 'respostas_usuarios'.
        """
        if not self.client or not question_id:
            if not question_id:
                print("🔥 AVISO: ID da questão é nulo. A resposta do usuário não foi salva.")
            else:
                print("🔥 AVISO: Conexão com Supabase falhou. A resposta do usuário não foi salva.")
            return False
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
            print(f"❌ Erro ao salvar resposta do usuário no Supabase: {e}")
            return False


supabase_service = SupabaseService()

