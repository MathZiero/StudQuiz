import firebase_admin
from firebase_admin import credentials, firestore
import os
import hashlib
from dotenv import load_dotenv

class FirebaseService:
    def __init__(self):
        self.db = None

    def _get_db(self):
        if self.db:
            return self.db
        if not firebase_admin._apps:
            try:
                load_dotenv()
                cred_path = "serviceAccountKey.json"
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase inicializado com sucesso!")
                else:
                    print("🔥 AVISO: Arquivo serviceAccountKey.json não encontrado.")
                    return None
            except Exception as e:
                print(f"❌ Erro ao inicializar Firebase: {e}")
                return None
        self.db = firestore.client()
        return self.db

    def salvar_questao_no_banco(self, question_obj, bloco_tematico: str) -> str:
        """Salva uma pergunta na coleção 'questoes', incluindo o bloco temático."""
        db = self._get_db()
        if not db:
            print("🔥 AVISO: Conexão com Firebase falhou. A questão não foi salva.")
            return None
        
        try:
            question_data = question_obj.to_dict()
            # 1. Adiciona o bloco temático aos dados da questão
            question_data['bloco_tematico'] = bloco_tematico
            
            enunciado_hash = hashlib.sha256(question_data['enunciado'].encode()).hexdigest()
            question_data['hash'] = enunciado_hash
            question_data['criado_em'] = firestore.SERVER_TIMESTAMP

            doc_ref = db.collection('questoes').add(question_data)
            question_id = doc_ref[1].id
            print(f"✅ Pergunta (Bloco: {bloco_tematico}) salva no banco de dados com ID: {question_id}")
            return question_id
        except Exception as e:
            print(f"❌ Erro ao salvar questão no Firestore: {e}")
            return None

    def salvar_resposta_usuario(self, session_id: str, question_id: str, user_answer_idx: int, is_correct: bool):
        """Salva a resposta de um usuário na coleção 'respostas_usuarios'."""
        db = self._get_db()
        if not db or not question_id:
            if not question_id:
                print("🔥 AVISO: ID da questão é nulo. A resposta do usuário não foi salva.")
            else:
                print("🔥 AVISO: Conexão com Firebase falhou. A resposta do usuário não foi salva.")
            return False
        
        try:
            resposta_data = {
                "session_id": session_id,
                "question_id": question_id,
                "resposta_usuario_idx": user_answer_idx,
                "acertou": is_correct,
                "respondido_em": firestore.SERVER_TIMESTAMP
            }
            db.collection('respostas_usuarios').add(resposta_data)
            print(f"✅ Resposta do usuário para a questão {question_id} salva.")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar resposta do usuário: {e}")
            return False

firebase_service = FirebaseService()
