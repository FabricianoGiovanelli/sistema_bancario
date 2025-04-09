import datetime
import textwrap
import os

def tratar_cpf(cpf):
    # Se a entrada não for uma string, converte para string
    cpf = str(cpf) if cpf is not None else ""
    
    # Extrai apenas os dígitos
    cpf_numerico = ''.join(char for char in cpf if char.isdigit())
    
    # Verifica se tem exatamente 11 dígitos
    if len(cpf_numerico) == 11:
        return cpf_numerico
    else:
        return None

def solicitar_cpf():
    """
    Solicita o CPF ao usuário e trata a entrada até que seja válido.
    
    Returns:
        str: O CPF válido.
    """
    while True:
        cpf = input("Informe o CPF (somente números): ")
        cpf_tratado = tratar_cpf(cpf)
        if cpf_tratado:
            return cpf_tratado
        else:
            print("CPF inválido. Por favor, informe um CPF com 11 dígitos.")

def limpar_tela():
    # Limpa a tela do terminal (funciona em Windows e Unix)
    os.system('cls')

def menu(usuario_logado=None, conta_ativa=None, limites=None):
    cabecalho = ""
    limpar_tela()
    if usuario_logado and conta_ativa:
        cabecalho = f"""
        ============ USUÁRIO LOGADO ============
        Nome: {usuario_logado['nome']} \tCPF: {usuario_logado['cpf']}
        Agência: {conta_ativa['agencia']} \tConta: {conta_ativa['numero_conta']:04d}
        ============== LIMITES =================
        Valor por Saque: R$ {limites['valor_saque']:.2f}
        N° de saques Diários: {limites['saques_restantes']}/{limites['limite_saques']}
        N° de transações Diárias: {limites['transacoes_restantes']}/{limites['limite_transacoes']}
        """
    menu_opcoes = f"""{cabecalho if cabecalho else ""}
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNovo Usuário
    [5]\tNova Conta
    [6]\tListar Contas
    [7]\tTrocar de Conta
    [8]\tLogout
    [9]\tSair
    => """
    return input(textwrap.dedent(menu_opcoes))

def depositar(saldo, valor, extrato, /):
    limpar_tela()
    print("\n================ DEPÓSITO ================")
    if valor <= 0:
        print("\nOperação falhou! O valor informado é inválido.")
        return saldo, extrato

    saldo += valor
    extrato += f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\tDepósito:\tR$ {valor:.2f}\n"
    print(f"\nDepósito de R$ {valor:.2f} realizado com sucesso!")
    return saldo, extrato

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    limpar_tela()
    print("\n================ SAQUE ================")

    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print("\nOperação falhou! Você não tem saldo suficiente.")
        return saldo, extrato, numero_saques

    if excedeu_limite:
        print(f"\nOperação falhou! O valor do saque excede o limite de R$ {limite:.2f}.")
        return saldo, extrato, numero_saques

    if excedeu_saques:
        print(f"\nOperação falhou! Número máximo de saques excedido ({limite_saques} por dia).")
        return saldo, extrato, numero_saques

    if valor <= 0:
        print("\nOperação falhou! O valor informado é inválido.")
        return saldo, extrato, numero_saques

    saldo -= valor
    extrato += f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\tSaque:\t\tR$ {valor:.2f}\n"
    numero_saques += 1
    print(f"\nSaque de R$ {valor:.2f} realizado com sucesso!")
    return saldo, extrato, numero_saques

def exibir_extrato(usuario_logado, contas, extrato_atual, saldo_atual, conta_ativa):
    limpar_tela()
    print("\n================ EXTRATO ================")
    
    tipo_extrato = input("\nTipo de extrato:\n[1] Apenas conta atual\n[2] Todas as contas\nEscolha uma opção: ")
    
    if tipo_extrato == "1":
        print(f"\n=== EXTRATO CONTA: {conta_ativa['numero_conta']:04d} ===")
        print("Não foram realizadas movimentações." if not extrato_atual else extrato_atual)
        print(f"\nSaldo: R$ {saldo_atual:.2f}")
    
    elif tipo_extrato == "2":
        contas_usuario = [conta for conta in contas if conta["usuario"]["cpf"] == usuario_logado["cpf"]]
        
        for conta in contas_usuario:
            print(f"\n=== EXTRATO CONTA: {conta['numero_conta']:04d} ===")
            if conta['numero_conta'] == conta_ativa['numero_conta']:
                print("Não foram realizadas movimentações." if not extrato_atual else extrato_atual)
                print(f"\nSaldo: R$ {saldo_atual:.2f}")
            else:
                print("Extrato não disponível. Faça login nesta conta para visualizar.")
    
    else:
        print("\nOpção inválida.")
    
    print("==========================================")
    input("\nPressione Enter para continuar...")

def criar_usuario(usuarios):
    limpar_tela()
    print("\n================ NOVO USUÁRIO ================\n")
    cpf = solicitar_cpf()
    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        print("\nJá existe usuário com esse CPF!")
        return None
    nome = input("Informe o nome completo: ").title()
    
    while True:
        data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
        try:
            datetime.datetime.strptime(data_nascimento, '%d/%m/%Y')
            break
        except ValueError:
            print("Data de nascimento inválida. Por favor, informe uma data no formato dd/mm/aaaa.")
    
    while True:
        try:
            logradouro = input("Informe o logradouro: ")
            numero = input("Informe o número: ")
            bairro = input("Informe o bairro: ")
            cidade = input("Informe a cidade: ")
            uf = input("Informe a UF: ").upper()
            if not all([logradouro, numero, bairro, cidade, uf]):
                print("Todos os campos do endereço são obrigatórios!")
                continue
            endereco = f"{logradouro}, {numero} - {bairro} - {cidade}/{uf}"
            break
        except:
            print("Dados de endereço inválidos. Por favor, tente novamente.")
    novo_usuario = {"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco}
    usuarios.append(novo_usuario)
    print(f"\nUsuário {nome} criado com sucesso!")
    return novo_usuario

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(agencia, numero_conta, usuario, contas):
    nova_conta = {"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario, "saldo": 0, "extrato": "", "saques": 0}
    contas.append(nova_conta)
    
    print(f"\nConta criada com sucesso!")
    print(f"Agência: {agencia}")
    print(f"Número da conta: {numero_conta:04d}")
    print(f"Titular: {usuario['nome']}")
    
    return nova_conta

def listar_contas(contas, usuario_logado=None):
    limpar_tela()
    print("\n================ LISTA DE CONTAS ================")
    if usuario_logado:
        contas_filtradas = [conta for conta in contas if conta["usuario"]["cpf"] == usuario_logado["cpf"]]
        if not contas_filtradas:
            print("\nUsuário não possui contas!")
            return
        
        print(f"\n=== CONTAS DE {usuario_logado['nome'].upper()} ===")
        for conta in contas_filtradas:
            print(f"\nAgência: {conta['agencia']}")
            print(f"Número da conta: {conta['numero_conta']:04d}")
    else:
        if not contas:
            print("\nNão há contas cadastradas!")
            return
        
        print("\n=== TODAS AS CONTAS ===")
        for conta in contas:
            print("\n============= DADOS DA CONTA =============")
            print(f"Agência: {conta['agencia']}")
            print(f"Número da conta: {conta['numero_conta']:04d}")
            print(f"Titular: {conta['usuario']['nome']}")
    
    input("\nPressione Enter para continuar...")

def tela_login(usuarios, contas, agencia, proximo_numero_conta):
    print("\n================ LOGIN ================\n")
    
    if not usuarios:
        print("\nNão há usuários cadastrados. Vamos criar um novo usuário!\n")
        novo_usuario = criar_usuario(usuarios)
        if novo_usuario:
            limpar_tela()
            print("\nCriando primeira conta automaticamente...\n")
            nova_conta = criar_conta(agencia, proximo_numero_conta, novo_usuario, contas)
            return novo_usuario, nova_conta
        else:
            return None, None

    cpf = solicitar_cpf()
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("\nUsuário não encontrado!\n")
        criar_nova_conta = input("\nDeseja criar um novo usuário? (s/n): ").lower()
        
        if criar_nova_conta == 's':
            limpar_tela()
            novo_usuario = criar_usuario(usuarios)
            if novo_usuario:
                print("\nCriando primeira conta automaticamente...\n")
                nova_conta = criar_conta(agencia, proximo_numero_conta, novo_usuario, contas)
                return novo_usuario, nova_conta
        return None, None

    contas_usuario = [conta for conta in contas if conta["usuario"]["cpf"] == cpf]

    if not contas_usuario:
        print(f"\nUsuário {usuario['nome']} não possui conta!\n")
        criar_nova_conta = input("Deseja criar uma nova conta? (s/n): ").lower()
        
        if criar_nova_conta == 's':
            nova_conta = criar_conta(agencia, proximo_numero_conta, usuario, contas)
            return usuario, nova_conta
        return None, None

    if len(contas_usuario) == 1:
        print(f"\nBem-vindo, {usuario['nome']}!\n")
        return usuario, contas_usuario[0]

    print(f"\nBem-vindo, {usuario['nome']}!\n")
    print("\nContas disponíveis:")
    for i, conta in enumerate(contas_usuario):
        print(f"{i+1}. Conta: {conta['numero_conta']:04d}")
    
    while True:
        try:
            opcao = input("Escolha o número da conta (ou 'n' para nova conta): ")
            
            if opcao.lower() == 'n':
                nova_conta = criar_conta(agencia, proximo_numero_conta, usuario, contas)
                return usuario, nova_conta
            
            opcao = int(opcao)
            if 1 <= opcao <= len(contas_usuario):
                return usuario, contas_usuario[opcao-1]
            
            print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")

def selecionar_conta(usuario_logado, contas):
    limpar_tela()
    print("\n================ SELECIONAR CONTA ================")
    contas_usuario = [conta for conta in contas if conta["usuario"]["cpf"] == usuario_logado["cpf"]]
    
    if not contas_usuario:
        print("\nUsuário não possui contas!")
        return None
    
    print("\nContas disponíveis:")
    for i, conta in enumerate(contas_usuario):
        print(f"{i+1}. Conta: {conta['numero_conta']:04d}")
    
    while True:
        try:
            opcao = input("Escolha o número da conta: ")
            opcao = int(opcao)
            if 1 <= opcao <= len(contas_usuario):
                return contas_usuario[opcao-1]
            print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")

def inicio():
    LIMITE_SAQUES = 3
    LIMITE_VALOR_SAQUE = 500
    LIMITE_TRANSACOES = 10
    AGENCIA = "001"

    usuarios = []
    contas = []
    proximo_numero_conta = 1
    
    usuario_logado = None
    conta_ativa = None

    while True:
        limpar_tela()
        if not usuario_logado or not conta_ativa:
            usuario_logado, conta_ativa = tela_login(usuarios, contas, AGENCIA, proximo_numero_conta)
            if conta_ativa:
                proximo_numero_conta = max([c["numero_conta"] for c in contas]) + 1 if contas else 1
            if not usuario_logado:
                opcao = input("\nDeseja:\n[1] Tentar novamente\n[2] Sair do sistema\nEscolha uma opção: ")
                if opcao == "2":
                    print("\nObrigado por utilizar nosso sistema bancário!")
                    break
                continue
        
        limites = {
            "valor_saque": LIMITE_VALOR_SAQUE,
            "limite_saques": LIMITE_SAQUES,
            "saques_restantes": LIMITE_SAQUES - conta_ativa.get("saques", 0),
            "limite_transacoes": LIMITE_TRANSACOES,
            "transacoes_restantes": LIMITE_TRANSACOES - (conta_ativa.get("saques", 0) + conta_ativa.get("depositos", 0))
        }
        
        opcao = menu(usuario_logado, conta_ativa, limites)

        if limites["transacoes_restantes"] <= 0 and opcao.lower() in ['d', 's']:
            print(f"\nLimite de {LIMITE_TRANSACOES} transações diárias atingido!")
            input("\nPressione Enter para continuar...")
            continue
            
        if opcao.lower() == "1":
            try:
                valor = float(input("Informe o valor do depósito: R$ "))
                conta_ativa["saldo"], conta_ativa["extrato"] = depositar(
                    conta_ativa.get("saldo", 0), 
                    valor, 
                    conta_ativa.get("extrato", "")
                )
                conta_ativa["depositos"] = conta_ativa.get("depositos", 0) + 1
                input("\nPressione Enter para continuar...")
            except ValueError:
                print("Por favor, informe um valor válido!")
                input("\nPressione Enter para continuar...")

        elif opcao.lower() == "2":
            try:
                valor = float(input("Informe o valor do saque: R$ "))
                conta_ativa["saldo"], conta_ativa["extrato"], conta_ativa["saques"] = sacar(
                    saldo=conta_ativa.get("saldo", 0),
                    valor=valor,
                    extrato=conta_ativa.get("extrato", ""),
                    limite=LIMITE_VALOR_SAQUE,
                    numero_saques=conta_ativa.get("saques", 0),
                    limite_saques=LIMITE_SAQUES
                )
                input("\nPressione Enter para continuar...")
            except ValueError:
                print("Por favor, informe um valor válido!")
                input("\nPressione Enter para continuar...")

        elif opcao.lower() == "3":
            exibir_extrato(
                usuario_logado, 
                contas, 
                conta_ativa.get("extrato", ""), 
                conta_ativa.get("saldo", 0),
                conta_ativa
            )

        elif opcao.lower() == "4":
            criar_usuario(usuarios)
            input("\nPressione Enter para continuar...")

        elif opcao.lower() == "5":
            nova_conta = criar_conta(AGENCIA, proximo_numero_conta, usuario_logado, contas)
            proximo_numero_conta += 1
            
            mudar_para_nova = input("\nDeseja mudar para essa conta? (s/n): ").lower()
            if mudar_para_nova == 's':
                conta_ativa = nova_conta
            
            input("\nPressione Enter para continuar...")

        elif opcao.lower() == "6":
            listar_contas(contas, usuario_logado)

        elif opcao.lower() == "7":
            nova_conta = selecionar_conta(usuario_logado, contas)
            if nova_conta:
                conta_ativa = nova_conta
                print(f"\nAgora você está usando a conta {conta_ativa['numero_conta']:04d}")
            input("\nPressione Enter para continuar...")
            
        elif opcao.lower() == "8":
            print("\nLogout realizado com sucesso!")
            usuario_logado = None
            conta_ativa = None
            input("\nPressione Enter para continuar...")

        elif opcao.lower() == "9":
            print("\nObrigado por utilizar nosso sistema bancário!")
            break

        else:
            print("\nOperação inválida, por favor selecione novamente a operação desejada.")
            input("\nPressione Enter para continuar...")

inicio()