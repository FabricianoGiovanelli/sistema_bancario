from abc import ABC, abstractmethod
from datetime import date, datetime
import os
import re

class Validacao:
    """Classe responsável pelas funções de validação e interação com o usuário"""
    
    @staticmethod
    def limpar_tela():
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def aguardar_tecla():
        """Aguarda que o usuário pressione Enter para continuar"""
        input("\nPressione Enter para continuar...")

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida o formato do CPF (apenas verificação básica de formato)"""
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        return True

    @staticmethod
    def validar_data(dia: int, mes: int, ano: int) -> bool:
        """Valida se a data fornecida é válida"""
        try:
            date(ano, mes, dia)
            return True
        except ValueError:
            return False

    @staticmethod
    def obter_numero_inteiro(mensagem: str) -> int:
        """Solicita um número inteiro do usuário com validação"""
        while True:
            try:
                valor = int(input(mensagem))
                return valor
            except ValueError:
                print("Erro: Digite um número inteiro válido.")

    @staticmethod
    def obter_numero_float(mensagem: str) -> float:
        """Solicita um número float do usuário com validação"""
        while True:
            try:
                entrada = input(mensagem)
                # Substitui vírgula por ponto para aceitar padrão brasileiro
                entrada = entrada.replace(',', '.')
                valor = float(entrada)
                if valor <= 0:
                    print("Erro: O valor deve ser maior que zero.")
                    continue
                return valor
            except ValueError:
                print("Erro: Digite um valor numérico válido.")

    @classmethod
    def obter_data_nascimento(cls) -> date:
        """Solicita e valida uma data de nascimento"""
        while True:
            try:
                print("\nData de nascimento")
                dia = cls.obter_numero_inteiro("Dia: ")
                mes = cls.obter_numero_inteiro("Mês: ")
                ano = cls.obter_numero_inteiro("Ano: ")
                
                if cls.validar_data(dia, mes, ano):
                    if date(ano, mes, dia) > date.today():
                        print("Erro: A data de nascimento não pode ser no futuro.")
                        continue
                    return date(ano, mes, dia)
                else:
                    print("Erro: Data inválida.")
            except ValueError as e:
                print(f"Erro: {e}")

    @classmethod
    def obter_cpf(cls) -> str:
        """Solicita e valida um CPF"""
        while True:
            cpf = input("CPF (apenas números): ")
            cpf_limpo = re.sub(r'[^0-9]', '', cpf)
            
            if cls.validar_cpf(cpf_limpo):
                return cpf_limpo
            else:
                print("Erro: CPF inválido. Um CPF válido deve ter 11 dígitos.")

class Transacao(ABC):
    """Interface para as transações"""
    
    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor: float):
        self.valor = valor
        self.data = datetime.now()
    
    def registrar(self, conta):
        return conta.depositar(self.valor)

class Saque(Transacao):
    def __init__(self, valor: float):
        self.valor = valor
        self.data = datetime.now()
    
    def registrar(self, conta):
        return conta.sacar(self.valor)

class Consulta(Transacao):
    def __init__(self):
        self.data = datetime.now()
    
    def registrar(self, conta):
        # Não altera o saldo, apenas registra a consulta
        return True

class Historico:
    def __init__(self):
        self.transacoes = []
    
    def adicionar_transacao(self, transacao: Transacao):
        self.transacoes.append(transacao)
    
    def obter_transacoes_hoje(self):
        """Retorna apenas as transações realizadas hoje"""
        hoje = datetime.now().date()
        return [t for t in self.transacoes if t.data.date() == hoje]

class Cliente:
    def __init__(self, endereco: str):
        self.endereco = str(endereco)
        self.contas = []
    
    def realizar_transacao(self, conta, transacao: Transacao):
        return transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco: str, cpf: str, nome: str, data_nascimento: date):
        super().__init__(endereco)
        self.cpf = str(cpf)
        self.nome = str(nome)
        self.data_nascimento = data_nascimento

class Conta:
    contador_contas = 1  # Contador para gerar números de conta automaticamente
    
    def __init__(self, cliente: Cliente, numero: int, agencia: str):
        self._saldo = 0.0
        self.numero = int(numero)
        self.agencia = str(agencia)
        self.cliente = cliente
        self.historico = Historico()
        cliente.adicionar_conta(self)
    
    @property
    def saldo(self) -> float:
        return self._saldo
    
    @classmethod
    def nova_conta(cls, cliente: Cliente) -> 'Conta':
        numero = cls.contador_contas
        cls.contador_contas += 1
        return cls(cliente, numero, "1001")
    
    def sacar(self, valor: float) -> bool:
        if valor > 0 and self._saldo >= valor:
            self._saldo -= valor
            self.historico.adicionar_transacao(Saque(valor))
            return True
        return False
    
    def depositar(self, valor: float) -> bool:
        if valor > 0:
            self._saldo += valor
            self.historico.adicionar_transacao(Deposito(valor))
            return True
        return False

class ContaCorrente(Conta):
    def __init__(self, cliente: Cliente, numero: int, agencia: str, limite: float = 500, limite_saques: int = 3):
        super().__init__(cliente, numero, agencia)
        self.limite = float(limite)
        self.limite_saques = int(limite_saques)
        self.limite_transacoes = 10
    
    def sacar(self, valor: float) -> bool:
        # Verificar limite de transações diárias
        transacoes_hoje = len(self.historico.obter_transacoes_hoje())
        if transacoes_hoje >= self.limite_transacoes:
            print(f"Operação falhou! Limite de {self.limite_transacoes} transações diárias atingido.")
            return False
        
        # Verificar limite de saques diários
        saques_hoje = len([t for t in self.historico.obter_transacoes_hoje() if isinstance(t, Saque)])
        if saques_hoje >= self.limite_saques:
            print(f"Operação falhou! Limite de {self.limite_saques} saques diários atingido.")
            return False
        
        # Verificar limite de valor por saque
        if valor > self.limite:
            print(f"Operação falhou! O valor excede o limite de R$ {self.limite:.2f} por saque.")
            return False
            
        return super().sacar(valor)
    
    def depositar(self, valor: float) -> bool:
        # Verificar limite de transações diárias
        transacoes_hoje = len(self.historico.obter_transacoes_hoje())
        if transacoes_hoje >= self.limite_transacoes:
            print(f"Operação falhou! Limite de {self.limite_transacoes} transações diárias atingido.")
            return False
            
        return super().depositar(valor)

class CaixaEletronico:
    def __init__(self):
        self.clientes = {}  # Dicionário para armazenar clientes (chave: CPF)
        self.contas = {}    # Dicionário para armazenar contas (chave: número da conta)
        self.cliente_logado = None
        self.conta_logada = None
                    
    def login(self) -> bool:
        """Realiza o login do cliente pelo CPF"""
        Validacao.limpar_tela()
        print("\n====== CAIXA ELETRÔNICO - LOGIN ======")
        
        cpf = Validacao.obter_cpf()
        
        if cpf in self.clientes:
            self.cliente_logado = self.clientes[cpf]
            
            # Se o cliente tem apenas uma conta, seleciona automaticamente
            if len(self.cliente_logado.contas) == 1:
                self.conta_logada = self.cliente_logado.contas[0]
                return True
            elif len(self.cliente_logado.contas) > 1:
                # Se tem múltiplas contas, permite escolher
                return self._selecionar_conta()
            else:
                print("Erro: Cliente não possui contas cadastradas.")
                Validacao.aguardar_tecla()
                return False
        else:
            print("Erro: CPF não cadastrado no sistema.")
            Validacao.aguardar_tecla()
            return False
    
    def _selecionar_conta(self) -> bool:
        """Permite ao cliente selecionar uma de suas contas"""
        Validacao.limpar_tela()
        print("\n====== SELECIONAR CONTA ======")
        
        print(f"Cliente: {self.cliente_logado.nome}")
        print("\nContas disponíveis:")
        
        for i, conta in enumerate(self.cliente_logado.contas, 1):
            print(f"{i}. Conta {conta.numero} - Agência {conta.agencia} - Saldo: R$ {conta.saldo:.2f}")
        
        try:
            opcao = Validacao.obter_numero_inteiro("\nSelecione uma conta (número): ")
            
            if 1 <= opcao <= len(self.cliente_logado.contas):
                self.conta_logada = self.cliente_logado.contas[opcao-1]
                return True
            else:
                print("Erro: Opção inválida.")
                Validacao.aguardar_tecla()
                return self._selecionar_conta()
        except Exception as e:
            print(f"Erro: {e}")
            Validacao.aguardar_tecla()
            return False
    
    def logout(self):
        """Realiza o logout do usuário"""
        self.cliente_logado = None
        self.conta_logada = None
    
    def exibir_informacoes_cliente(self):
        """Exibe as informações do cliente logado e sua conta"""
        if not self.cliente_logado or not self.conta_logada:
            return
            
        print(f"Cliente: {self.cliente_logado.nome}")
        print(f"CPF: {self.cliente_logado.cpf}")
        print(f"Conta: {self.conta_logada.numero}")
        print(f"Agência: {self.conta_logada.agencia}")
        print(f"Saldo: R$ {self.conta_logada.saldo:.2f}")
        
        # Exibir limites
        if isinstance(self.conta_logada, ContaCorrente):
            saques_hoje = len([t for t in self.conta_logada.historico.obter_transacoes_hoje() if isinstance(t, Saque)])
            transacoes_hoje = len(self.conta_logada.historico.obter_transacoes_hoje())
            
            print(f"Saques hoje: {saques_hoje}/{self.conta_logada.limite_saques}")
            print(f"Transações hoje: {transacoes_hoje}/{self.conta_logada.limite_transacoes}")
            print(f"Limite por saque: R$ {self.conta_logada.limite:.2f}")
    
    def criar_cliente(self) -> None:
        """Cria um novo cliente com validações"""
        Validacao.limpar_tela()
        print("\n====== CRIAR CLIENTE ======")
        
        try:
            # Validação de CPF
            cpf = Validacao.obter_cpf()
            
            # Verifica se o CPF já está cadastrado
            if cpf in self.clientes:
                print(f"Erro: Já existe um cliente cadastrado com o CPF {cpf}.")
                Validacao.aguardar_tecla()
                return
            
            # Coleta os dados do cliente com validações
            nome = input("Nome completo: ")
            while not nome.strip():
                print("Erro: O nome não pode ser vazio.")
                nome = input("Nome completo: ")
            
            endereco = input("Endereço: ")
            while not endereco.strip():
                print("Erro: O endereço não pode ser vazio.")
                endereco = input("Endereço: ")
            
            data_nascimento = Validacao.obter_data_nascimento()
            
            # Cria o cliente
            cliente = PessoaFisica(endereco, cpf, nome, data_nascimento)
            self.clientes[cpf] = cliente
            
            # Cria automaticamente uma conta para o cliente
            conta = ContaCorrente.nova_conta(cliente)
            self.contas[conta.numero] = conta
            
            print(f"\nCliente {nome} cadastrado com sucesso!")
            print(f"Conta {conta.numero} na agência {conta.agencia} criada automaticamente!")
            
        except Exception as e:
            print(f"Erro ao criar cliente: {e}")
        
        Validacao.aguardar_tecla()
    
    def realizar_deposito(self) -> None:
        """Realiza um depósito na conta logada"""
        if not self.verificar_login():
            return
            
        Validacao.limpar_tela()
        print("\n====== REALIZAR DEPÓSITO ======")
        self.exibir_informacoes_cliente()
        print("\n")
        
        try:
            # Solicita o valor do depósito
            valor = Validacao.obter_numero_float("Valor do depósito (R$): ")
            
            # Realiza o depósito
            transacao = Deposito(valor)
            
            if self.cliente_logado.realizar_transacao(self.conta_logada, transacao):
                print(f"\nDepósito de R$ {valor:.2f} realizado com sucesso!")
                print(f"Novo saldo: R$ {self.conta_logada.saldo:.2f}")
            else:
                print("\nNão foi possível realizar o depósito.")
                
        except Exception as e:
            print(f"Erro ao realizar depósito: {e}")
        
        Validacao.aguardar_tecla()
    
    def realizar_saque(self) -> None:
        """Realiza um saque na conta logada"""
        if not self.verificar_login():
            return
            
        Validacao.limpar_tela()
        print("\n====== REALIZAR SAQUE ======")
        self.exibir_informacoes_cliente()
        print("\n")
        
        try:
            # Solicita o valor do saque
            valor = Validacao.obter_numero_float("Valor do saque (R$): ")
            
            # Verifica se o valor é maior que o saldo
            if valor > self.conta_logada.saldo:
                print(f"Erro: Saldo insuficiente. Seu saldo atual é de R$ {self.conta_logada.saldo:.2f}")
                Validacao.aguardar_tecla()
                return
            
            # Realiza o saque
            transacao = Saque(valor)
            
            if self.cliente_logado.realizar_transacao(self.conta_logada, transacao):
                print(f"\nSaque de R$ {valor:.2f} realizado com sucesso!")
                print(f"Novo saldo: R$ {self.conta_logada.saldo:.2f}")
            
        except Exception as e:
            print(f"Erro ao realizar saque: {e}")
        
        Validacao.aguardar_tecla()
    
    def exibir_extrato(self) -> None:
        """Exibe o extrato da conta logada"""
        if not self.verificar_login():
            return
            
        Validacao.limpar_tela()
        print("\n====== EXTRATO ======")
        self.exibir_informacoes_cliente()
        
        # Verificar se a operação excede o limite de transações
        transacoes_hoje = len(self.conta_logada.historico.obter_transacoes_hoje())
        if transacoes_hoje >= self.conta_logada.limite_transacoes:
            print(f"\nOperação falhou! Limite de {self.conta_logada.limite_transacoes} transações diárias atingido.")
            Validacao.aguardar_tecla()
            return
        
        try:
            # Exibe o histórico de transações
            print("\n--- HISTÓRICO DE TRANSAÇÕES ---")
            
            if not self.conta_logada.historico.transacoes:
                print("Nenhuma transação realizada.")
            else:
                # Mostrar apenas as 10 últimas transações
                ultimas_transacoes = self.conta_logada.historico.transacoes[-10:]
                for i, transacao in enumerate(ultimas_transacoes, 1):
                    if isinstance(transacao, Deposito):
                        tipo = "Depósito"
                        valor = transacao.valor
                    elif isinstance(transacao, Saque):
                        tipo = "Saque"
                        valor = transacao.valor
                    elif isinstance(transacao, Consulta):
                        tipo = "Consulta de Extrato"
                        valor = 0
                    else:
                        tipo = "Desconhecida"
                        valor = 0
                    
                    data_formatada = transacao.data.strftime("%d/%m/%Y %H:%M:%S")
                    print(f"{i}. {data_formatada} - {tipo}: R$ {valor:.2f}")
            
        except Exception as e:
            print(f"Erro ao exibir extrato: {e}")
        
        Validacao.aguardar_tecla()
    
    def verificar_login(self) -> bool:
        """Verifica se há um cliente logado e uma conta selecionada"""
        if not self.cliente_logado or not self.conta_logada:
            print("Erro: É necessário fazer login primeiro.")
            Validacao.aguardar_tecla()
            return False
        return True
    
    def obter_opcao_menu(self) -> str:
        """Exibe o menu e retorna a opção escolhida pelo usuário"""
        Validacao.limpar_tela()
        print("\n====== CAIXA ELETRÔNICO ======")
        
        # Se houver cliente logado, mostra suas informações
        if self.cliente_logado and self.conta_logada:
            print("\n--- INFORMAÇÕES DO CLIENTE ---")
            self.exibir_informacoes_cliente()
        
        print("\n--- MENU ---")
        
        if not self.cliente_logado:
            print("1 - Login")
            print("2 - Criar Conta")
            print("0 - Sair")
        else:
            print("1 - Depositar")
            print("2 - Sacar")
            print("3 - Extrato")
            print("4 - Logout")
            print("0 - Sair")
        
        print("============================")
        
        return input("\nEscolha uma opção: ")

def main():
    caixa = CaixaEletronico()
    
    while True:
        opcao = caixa.obter_opcao_menu()
        
        try:
            if not caixa.cliente_logado:
                # Opções para usuário não logado
                if opcao == "1":
                    caixa.login()
                elif opcao == "2":
                    caixa.criar_cliente()
                elif opcao == "0":
                    Validacao.limpar_tela()
                    print("Obrigado por utilizar o Caixa Eletrônico!")
                    print("Saindo...")
                    break
                else:
                    print("\nOpção inválida! Por favor, escolha uma opção válida.")
                    Validacao.aguardar_tecla()
            else:
                # Opções para usuário logado
                if opcao == "1":
                    caixa.realizar_deposito()
                elif opcao == "2":
                    caixa.realizar_saque()
                elif opcao == "3":
                    caixa.exibir_extrato()
                elif opcao == "4":
                    caixa.logout()
                elif opcao == "0":
                    Validacao.limpar_tela()
                    print("Obrigado por utilizar o Caixa Eletrônico!")
                    print("Saindo...")
                    break
                else:
                    print("\nOpção inválida! Por favor, escolha uma opção válida.")
                    Validacao.aguardar_tecla()
                    
        except Exception as e:
            print(f"\nErro inesperado: {e}")
            Validacao.aguardar_tecla()

if __name__ == "__main__":
    main()
