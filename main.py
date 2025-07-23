import random
from models.question import Question
from utils.parser import carregar_topico_aleatorio
from services.gemini import gerar_pergunta  # ATUALIZADO
from services.firebase import salvar_resultado_simulado

def main():
    """
    Função principal que orquestra a execução do aplicativo de estudos.
    """
    print("Bem-vindo ao Estuda+ CPNU!")

    # Mapeamento dos blocos para os nomes dos arquivos CSV
    blocos = {
        "1": {"nome": "Bloco 1 - Infraestrutura, Exatas e Engenharias", "arquivo": "csv/bloco_1.txt"},
        "3": {"nome": "Bloco 3 - Ambiental, Agrário e Biológicas", "arquivo": "csv/bloco_3.txt"},
        "5": {"nome": "Bloco 5 - Educação, Saúde, Desenvolvimento Social e Direitos Humanos", "arquivo": "csv/bloco_5.txt"}
    }

    # Seleção do Bloco pelo usuário
    while True:
        print("\nEscolha um bloco:")
        for key, value in blocos.items():
            print(f"[{key}] {value['nome']}")
        
        escolha_bloco = input(">> ")
        if escolha_bloco in blocos:
            arquivo_csv = blocos[escolha_bloco]['arquivo']
            nome_bloco = blocos[escolha_bloco]['nome']
            break
        else:
            print("Opção inválida. Tente novamente.")

    print("\nCarregando tópico...")
    
    # Carrega um tópico aleatório do CSV selecionado
    topico_selecionado = carregar_topico_aleatorio(arquivo_csv)
    
    if topico_selecionado is None:
        print("Não foi possível carregar um tópico. Verifique o arquivo CSV.")
        return

    # Gera uma dificuldade aleatória
    dificuldade = random.randint(1, 5)
    
    # Gera a pergunta usando o serviço do Gemini (que pode recorrer à simulação)
    pergunta_obj = gerar_pergunta(  # ATUALIZADO
        disciplina=topico_selecionado['Disciplina'],
        topico=topico_selecionado['Tópico'],
        subtopico=topico_selecionado.get('Subtópico', ''),
        dificuldade=dificuldade
    )

    # Exibe a pergunta para o usuário
    print(f"\n[BLOCO: {nome_bloco}]")
    print(f"[DIFICULDADE: {'★' * pergunta_obj.dificuldade}{'☆' * (5 - pergunta_obj.dificuldade)}]")
    print(f"[DISCIPLINA: {pergunta_obj.disciplina}]")
    print(f"[TÓPICO: {pergunta_obj.topico}]\n")
    print(f"Pergunta: {pergunta_obj.enunciado}\n")

    for i, alt in enumerate(pergunta_obj.alternativas):
        print(f"{chr(65 + i)}) {alt}")

    # Coleta a resposta do usuário
    mapa_respostas = {chr(65 + i): i for i in range(len(pergunta_obj.alternativas))}
    while True:
        resposta_usuario_letra = input("\nEscolha a alternativa: >> ").upper()
        if resposta_usuario_letra in mapa_respostas:
            resposta_usuario_idx = mapa_respostas[resposta_usuario_letra]
            break
        else:
            print("Alternativa inválida. Escolha entre A, B, C, D, E.")

    # Verifica a resposta e exibe o feedback
    if resposta_usuario_idx == pergunta_obj.resposta_correta_idx:
        print("\n✅ Resposta correta!")
    else:
        letra_correta = chr(65 + pergunta_obj.resposta_correta_idx)
        print(f"\n❌ Resposta incorreta! A resposta certa era a {letra_correta}.")
    
    print(f"\nExplicação: {pergunta_obj.explicacao}\n")

    # Salva o resultado no Firebase
    resultado = {
        "bloco_tematico": nome_bloco,
        "pergunta_completa": pergunta_obj.to_dict(),
        "resposta_usuario_idx": resposta_usuario_idx,
        "acertou": resposta_usuario_idx == pergunta_obj.resposta_correta_idx
    }
    
    # Simula o salvamento dos dados
    salvar_resultado_simulado(resultado)

if __name__ == "__main__":
    main()