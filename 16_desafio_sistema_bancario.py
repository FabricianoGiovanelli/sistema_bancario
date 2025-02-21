#SISTEMA BANCÁRIO
'''REGRAS:
1 - NÃO PERMITIR SAQUE NEGATIVO
2 - NÃO PERMITIR MAIS DE 3 SAQUES POR DIA COM LIMITE DE 500 REAIS POR SAQUE
3 - TER OPÇÃO DE SAQUE, DEPÓSITO E EXTRATO
4 - EXTRATO MOSTRAR TODAS AS TRANSAÇÕES EFETUADAS
5 - EXIBIR NO FINAL DO EXTRATO O SALDO EM R$ 000,00
6 - APENAS UM USUÁRIO, NÃO SE PREOCUPAR COM AGENCIA E CONTA
'''
import time #inserir pausas para leituras e facilitar o uso do programa
import os #usado para limpar o terminal e facilitar leitura das informações

os.system('cls') #limpa terminal

def pausa(segundos): #função para pausar o programa em segundos
    time.sleep(segundos)
#Mensagem de boas vindas e logo do banco
print("_".center(100,"_"))
print(" ")
print("""
    Seja bem vindo ao      
          ____        _   _                 
         |  _ \ _   _| |_| |__   ___  _ __  
         | |_) | | | | __| '_ \ / _ \| '_ \ 
         |  __/| |_| | |_| | | | (_) | | | |
         |_|    \__, |\__|_| |_|\___/|_| |_|
                |___/                       
          ____              _    
         | __ )  __ _ _ __ | | __
         |  _ \ / _` | '_ \| |/ /
         | |_) | (_| | | | |   < 
         |____/ \__,_|_| |_|_|\_\                                    Aqui seus dígitos viram códigos!
      
""")
print("_".center(100,"_"))
print(" ")
pausa(5)
os.system('cls')

saldo = 0 #variavel armazena o saldo da conta
contador_saque = 0 #variavel que controla quantos saques foram realizados, não foi inserido reset pois é apenas um sistema sem banco de dados
limite_saque = 500 #variavel que armazena o limite por saque
extrato = [] #lista que armazena as movimentações da conta

def print_real(valor): #função para formatar os valores em real
    return f'R$ {valor:.2f}'.rjust(15,".")

def obter_valor(valor):
    # Remover espaços em branco
    valor = valor.replace(" ", "")
    # Substituir vírgula por ponto
    valor = valor.replace(",", ".")
    # Verificar se o valor é numérico e tem no máximo 1 ponto
    while True:
        if valor.count(".") > 1:
            print("O valor só pode ter no máximo 1 ponto.")
            valor = input("Digite um valor novamente: ")
            valor = valor.replace(" ", "").replace(",", ".")
            continue
        
        # Verificar se o valor é numérico
        if valor.replace(".", "").isdigit():  # Verifica se o valor é numérico (ignorando o ponto)
            return float(valor)  # Retorna o valor como número decimal
        else:
            print(f"{valor} não é um valor válido, insira um número válido.")
            valor = input("Digite um valor novamente: ")
            valor = valor.replace(" ", "").replace(",", ".")

def funcao_saque(): #função para executar os saques
    global saldo, contador_saque #define saldo e contador de saque como variaveis globais para poder alterar seus valores
    valor = input("\nInsira o valor do saque: ")
    valor = obter_valor(valor)
    if valor > 0:
        if valor <= limite_saque and contador_saque < 3 and saldo >= valor and valor > 0:
            os.system('cls')
            print(f'Saque de R$ {valor:.2f} está sendo processado, por favor aguarde a contagem das cédulas')
            contador_saque += 1
            saldo -= valor
            extrato.append ("Saque")
            extrato.append (-valor)  
            pausa(2)
            print(f'\nPor favor retire as cédulas, seu saldo atual é de R$ {saldo:.2f}.\n')
            pausa(2)
        elif valor > limite_saque:
            print("\nLimite de saque excedido, seu limite é de R$ 500,00 reais por saque.\n")
            pausa(2)
        elif valor > saldo:
            print("\nSaldo insuficiente.\n")
            pausa(2)
        elif contador_saque>=3:
            print("\nLimite de 3 saques diário atingido, tente novamente amanhã.\n")
            pausa(2)
    else:
        print(f"\n{valor} é inválido, insira um valor válido maior que zero\n")
        pausa(3)

def funcao_extrato():
    if not extrato:
        print(f"\nNão houve movimentações na sua conta, seu saldo atual é de R$ {saldo:.2f}.")
        pausa(3)
    else:
        os.system('cls')
        print("\nExtrato Bank Python\n")
        for x in range(0, len(extrato),2): #Cria um range iniciando em 0 até o último, pulando de 2 em 2
            movimento = extrato[x]
            valor = extrato[x+1]
            print(f'{movimento.capitalize().ljust(10,".")}{print_real(valor)}')
        print("-".ljust(25,"-"))
        print(f"{'Saldo'.ljust(10,'.')}{print_real(saldo)}\n")
        pausa(3)

def funcao_deposito():
    global saldo
    valor = input("\nQual valor quer depositar? R$ ")
    valor = obter_valor(valor)
    if valor > 0:
        saldo += valor
        extrato.append ("Depósito")
        extrato.append (valor)
        os.system('cls')
        print(f"Seu novo saldo após o depósito é de R$ {saldo:.2f}\n")
        pausa(3)
    else:
        print(f"\n{valor} é inválido, insira um valor válido maior que zero\n")

while True:
    opcao = input(f'Digite a opção desejada e pressione enter: \n\n [1] Saque \n [2] Depósito \n [3] Extrato \n [4] Sair \n\n Sua opção: ').strip()
    if opcao == "1":
        if saldo <= 0:
            os.system('cls')
            print(f'\nSeu saldo está zerado, faça um depósito para poder sacar.\n')
            pausa(3)
        elif contador_saque>=3:
            print("\nLimite de 3 saques diário atingido, tente novamente amanhã.\n")
            pausa(2)
        else:
            funcao_saque()
    elif opcao == "2":
        funcao_deposito()
    elif opcao == "3":
        funcao_extrato()
    elif opcao == "4":
        os.system('cls')
        print("""
                  
Obrigado por utilizar o
                  
          ____        _   _                 
         |  _ \ _   _| |_| |__   ___  _ __  
         | |_) | | | | __| '_ \ / _ \| '_ \ 
         |  __/| |_| | |_| | | | (_) | | | |
         |_|    \__, |\__|_| |_|\___/|_| |_|
                |___/                       
          ____              _    
         | __ )  __ _ _ __ | | __
         |  _ \ / _` | '_ \| |/ /
         | |_) | (_| | | | |   < 
         |____/ \__,_|_| |_|_|\_\                                   
                                                 __      __
                                                ( _\    /_ )
                                                \ _\  /_ / 
                                                \ _\/_ /_ _
                                                |_____/_/ /|
                                                (  (_)__)J-)
                                                (  /`.,   /
                                                \/  ;   /
                                                 | === |
                                                                    Até mais!
      
            """)
        pausa(5)
        break
    else:
        os.system('cls')
        print("\n MENSAGEM DE ERRO DE SISTEMA:")
        print(f"\n ERRO: Opção '{opcao}' é inválida. Tente novamente.\n")
        pausa(3)