
"""
Serviço Firebase consolidado
Baseado no seu código atual, mas melhorado e organizado
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from dotenv import load_dotenv

class FirebaseService:
    def __init__(self):
        self.db = None
        self._inicializar()
    
    def _inicializar(self):
        """Inicializa Firebase uma única vez"""
        if not firebase_admin._apps:
            try:
                load_dotenv()
                
                # Caminho para credenciais
                cred_path = "serviceAccountKey.json"
                
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase inicializado com sucesso!")
                    return True
                else:
                    print("❌ Arquivo serviceAccountKey.json não encontrado!")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro ao inicializar Firebase: {e}")
                return False
        else:
            print("✅ Firebase já estava inicializado")
            return True
    
    def obter_db(self):
        """Retorna instância do Firestore"""
        if self._inicializar():
            if not self.db:
                self.db = firestore.client()
            return self.db
        return None
    
    def salvar_resultado(self, resultado: dict, colecao: str = "quiz_resultados"):
        """
        Salva resultado no Firestore
        Baseado na sua função original, mas melhorada
        
        Args:
            resultado: Um dicionário contendo os dados a serem salvos
            colecao: Nome da coleção (padrão: "quiz_resultados")
        
        Returns:
            str: ID do documento criado, ou False em caso de erro
        """
        try:
            # Obter instância do banco
            db = self.obter_db()
            if not db:
                print("❌ Não foi possível conectar ao Firebase")
                return False
            
            # Adicionar timestamp automático (igual ao seu código)
            resultado_completo = {
                **resultado,
                "timestamp": datetime.now(),
                "data_criacao": firestore.SERVER_TIMESTAMP
            }
            
            # Salvar na coleção "quiz_resultados" (igual ao seu código)
            doc_ref = db.collection(colecao).add(resultado_completo)
            doc_id = doc_ref[1].id
            
            print(f"✅ Resultado salvo com sucesso! ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            print(f"❌ Erro ao salvar resultado: {e}")
            return False
    
    def buscar_resultados(self, colecao: str = "quiz_resultados", limite: int = None):
        """
        Busca resultados salvos no Firebase
        
        Args:
            colecao: Nome da coleção
            limite: Número máximo de resultados
            
        Returns:
            list: Lista de resultados
        """
        try:
            db = self.obter_db()
            if not db:
                return []
            
            query = db.collection(colecao)
            
            if limite:
                query = query.limit(limite)
            
            # Ordenar por timestamp (mais recentes primeiro)
            query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)
            
            docs = query.stream()
            resultados = []
            
            for doc in docs:
                dados = doc.to_dict()
                dados['id'] = doc.id
                resultados.append(dados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados: {e}")
            return []
    
    def buscar_por_usuario(self, usuario_id: str, colecao: str = "quiz_resultados"):
        """
        Busca resultados de um usuário específico
        
        Args:
            usuario_id: ID do usuário
            colecao: Nome da coleção
            
        Returns:
            list: Resultados do usuário
        """
        try:
            db = self.obter_db()
            if not db:
                return []
            
            docs = db.collection(colecao).where("usuario_id", "==", usuario_id).stream()
            resultados = []
            
            for doc in docs:
                dados = doc.to_dict()
                dados['id'] = doc.id
                resultados.append(dados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Erro ao buscar por usuário: {e}")
            return []

# Instância global (singleton)
firebase_service = FirebaseService()

# Suas funções originais (para manter compatibilidade)
def inicializar_firebase():
    """Wrapper para manter compatibilidade com seu código atual"""
    return firebase_service._inicializar()

def obter_db():
    """Wrapper para manter compatibilidade com seu código atual"""
    return firebase_service.obter_db()

def salvar_resultado(resultado: dict):
    """
    Sua função original - mantida para compatibilidade
    Agora usa a classe internamente
    """
    return firebase_service.salvar_resultado(resultado)