import requests
import json
import time
import sys

# URL da API Render
API_URL = 'https://server-qx03.onrender.com'

def verificar_conexao():
    """Verifica se o servidor está online e responde"""
    print("Verificando conexão com o servidor Render...")
    try:
        response = requests.get(f"{API_URL}/ping", timeout=10)
        if response.status_code == 200:
            print(f"✓ Servidor online! Status: {response.status_code}")
            dados = response.json()
            print(f"✓ Versão da API: {dados.get('version', 'desconhecida')}")
            return True
        else:
            print(f"✗ Servidor respondeu com status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Erro ao conectar com o servidor: {e}")
        return False

def listar_tabelas():
    """Lista as tabelas disponíveis no servidor"""
    print("\nListando tabelas no servidor Render...")
    try:
        response = requests.get(f"{API_URL}/tabelas", timeout=10)
        if response.status_code == 200:
            tabelas = response.json().get('tabelas', [])
            if tabelas:
                print(f"✓ Tabelas encontradas: {', '.join(tabelas)}")
                return tabelas
            else:
                print("✗ Nenhuma tabela encontrada no servidor")
                return []
        else:
            print(f"✗ Erro ao listar tabelas: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Erro ao listar tabelas: {e}")
        return []

def verificar_tabela_churches():
    """Verifica se a tabela churches existe e tem dados"""
    print("\nVerificando tabela 'churches'...")
    try:
        response = requests.get(f"{API_URL}/churches", timeout=10)
        if response.status_code == 200:
            dados = response.json()
            registros = len(dados)
            print(f"✓ Tabela 'churches' existe com {registros} registros")
            return dados
        else:
            print(f"✗ Erro ao acessar tabela 'churches': {response.status_code}")
            if response.status_code == 500:
                try:
                    erro = response.json()
                    print(f"  Mensagem: {erro.get('error', 'Erro desconhecido')}")
                except:
                    print(f"  Resposta: {response.text[:100]}")
            return None
    except Exception as e:
        print(f"✗ Erro ao verificar churches: {e}")
        return None

def criar_registro_exemplo(id_igreja, dados):
    """Cria um registro de exemplo na tabela churches"""
    print(f"\nCriando registro de exemplo com ID '{id_igreja}'...")
    try:
        response = requests.put(f"{API_URL}/churches/{id_igreja}", json=dados, timeout=15)
        if response.status_code in [200, 201]:
            print(f"✓ Registro '{id_igreja}' criado com sucesso!")
            return True
        else:
            print(f"✗ Erro ao criar registro: {response.status_code}")
            try:
                erro = response.json()
                print(f"  Mensagem: {erro}")
            except:
                print(f"  Resposta: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"✗ Erro ao criar registro: {e}")
        return False

def validar_cors():
    """Valida se os cabeçalhos CORS estão configurados corretamente"""
    print("\nVerificando configuração CORS...")
    try:
        response = requests.options(f"{API_URL}/ping", timeout=10)
        
        # Verificar cabeçalhos importantes
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept, Origin'
        }
        
        success = True
        for header, expected_value in cors_headers.items():
            if header.lower() in [h.lower() for h in response.headers]:
                actual_header = next(h for h in response.headers if h.lower() == header.lower())
                actual_value = response.headers[actual_header]
                if expected_value == '*' or expected_value in actual_value:
                    print(f"✓ {header}: {actual_value}")
                else:
                    print(f"✗ {header}: {actual_value} (esperado: {expected_value})")
                    success = False
            else:
                print(f"✗ {header} não encontrado nos cabeçalhos")
                success = False
        
        if success:
            print("✓ Configuração CORS parece estar correta!")
        else:
            print("✗ Problemas encontrados na configuração CORS")
        
        return success
    except Exception as e:
        print(f"✗ Erro ao verificar CORS: {e}")
        return False

def testar_proxy_access():
    """Testa acesso através de proxies CORS populares"""
    print("\nTestando acesso através de proxies CORS...")
    
    proxies = [
        {
            'nome': 'AllOrigins',
            'url': f"https://api.allorigins.win/raw?url={API_URL}/ping"
        },
        {
            'nome': 'corsproxy.io',
            'url': f"https://corsproxy.io/?{API_URL}/ping"
        }
    ]
    
    for proxy in proxies:
        print(f"\nTestando {proxy['nome']}...")
        try:
            response = requests.get(proxy['url'], timeout=15)
            if response.status_code == 200:
                print(f"✓ {proxy['nome']} funciona! Status: {response.status_code}")
                try:
                    dados = response.json()
                    print(f"  Resposta: {json.dumps(dados)[:100]}")
                except:
                    print(f"  Resposta: {response.text[:100]}")
            else:
                print(f"✗ {proxy['nome']} falhou. Status: {response.status_code}")
        except Exception as e:
            print(f"✗ Erro ao testar {proxy['nome']}: {e}")

def verificar_e_corrigir_tabela_churches():
    """Verifica se a tabela churches existe e cria se necessário"""
    tabelas = listar_tabelas()
    
    if not tabelas or 'churches' not in tabelas:
        print("\n! Tabela 'churches' não encontrada.")
        
        # Tenta criar alguns registros de exemplo para forçar a criação da tabela
        exemplo1 = {
            'nome': 'Igreja Exemplo Render 1',
            'morada': 'Rua de Exemplo, 123',
            'ano': '2023',
            'agendamento': 'Sim',
            'autorizadoFilippi': 'Sim',
            'arquivada': 0,
            'dados': {'info': 'Dados de exemplo para teste no Render'}
        }
        
        exemplo2 = {
            'nome': 'Igreja Exemplo Render 2',
            'morada': 'Avenida Principal, 456',
            'ano': '2022',
            'agendamento': 'Não',
            'autorizadoFilippi': 'Sim',
            'arquivada': 0,
            'dados': {'info': 'Segunda igreja de exemplo no Render'}
        }
        
        criar_registro_exemplo('demo1', exemplo1)
        time.sleep(1)  # Pequena pausa para não sobrecarregar o servidor
        criar_registro_exemplo('demo2', exemplo2)
        
        # Verifica novamente se a tabela foi criada
        time.sleep(2)
        verificar_tabela_churches()
    else:
        dados = verificar_tabela_churches()
        
        if not dados or len(dados) == 0:
            print("! Tabela 'churches' existe mas está vazia. Criando registros de exemplo...")
            
            exemplo = {
                'nome': 'Igreja Exemplo Auto-criada',
                'morada': 'Rua de Teste, 999',
                'ano': '2023',
                'agendamento': 'Sim',
                'autorizadoFilippi': 'Sim',
                'arquivada': 0,
                'dados': {'info': 'Registro criado automaticamente', 'timestamp': time.time()}
            }
            
            criar_registro_exemplo(f'auto{int(time.time())}', exemplo)
            time.sleep(1)
            verificar_tabela_churches()

def verificar_detalhes_render():
    """Verifica detalhes do servidor Render"""
    print("\nVerificando detalhes do servidor Render...")
    try:
        response = requests.get(f"{API_URL}/check-db", timeout=15)
        if response.status_code == 200:
            dados = response.json()
            print(f"✓ Status do banco: {dados.get('status', 'desconhecido')}")
            print(f"✓ Mensagem: {dados.get('mensagem', 'N/A')}")
            print(f"✓ Caminho do banco: {dados.get('caminho', 'N/A')}")
            
            tabelas = dados.get('tabelas', [])
            print(f"✓ Tabelas encontradas: {', '.join(tabelas)}")
            
            detalhes = dados.get('detalhes', {})
            for tabela, info in detalhes.items():
                status = info.get('status', 'desconhecido')
                if status == 'ok':
                    print(f"  - {tabela}: {info.get('registros', 0)} registros")
                else:
                    print(f"  - {tabela}: ERRO - {info.get('mensagem', 'Erro desconhecido')}")
                    
            return True
        else:
            print(f"✗ Erro ao verificar detalhes: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Erro ao verificar detalhes: {e}")
        return False

def menu_principal():
    """Exibe o menu principal e processa a escolha do usuário"""
    while True:
        print("\n" + "="*50)
        print(" DIAGNÓSTICO E DEPLOY PARA RENDER ".center(50, "="))
        print("="*50)
        print("1. Verificar conexão com servidor")
        print("2. Listar tabelas")
        print("3. Verificar tabela 'churches'")
        print("4. Criar registros de exemplo em 'churches'")
        print("5. Verificar configuração CORS")
        print("6. Testar proxies CORS")
        print("7. Verificar detalhes do servidor")
        print("8. Executar verificação completa")
        print("0. Sair")
        
        try:
            escolha = input("\nEscolha uma opção: ")
            
            if escolha == "1":
                verificar_conexao()
            elif escolha == "2":
                listar_tabelas()
            elif escolha == "3":
                verificar_tabela_churches()
            elif escolha == "4":
                verificar_e_corrigir_tabela_churches()
            elif escolha == "5":
                validar_cors()
            elif escolha == "6":
                testar_proxy_access()
            elif escolha == "7":
                verificar_detalhes_render()
            elif escolha == "8":
                print("\n" + "="*50)
                print(" INICIANDO VERIFICAÇÃO COMPLETA ".center(50, "="))
                print("="*50)
                if verificar_conexao():
                    listar_tabelas()
                    verificar_tabela_churches()
                    validar_cors()
                    testar_proxy_access()
                    verificar_detalhes_render()
                print("\n" + "="*50)
                print(" VERIFICAÇÃO COMPLETA FINALIZADA ".center(50, "="))
                print("="*50)
            elif escolha == "0":
                print("Saindo...")
                break
            else:
                print("Opção inválida!")
                
            input("\nPressione Enter para continuar...")
        except KeyboardInterrupt:
            print("\nOperação cancelada!")
            break
        except Exception as e:
            print(f"\nErro: {e}")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Modo automático para verificação completa
        if verificar_conexao():
            listar_tabelas()
            verificar_e_corrigir_tabela_churches()
            validar_cors()
            testar_proxy_access()
            verificar_detalhes_render()
    else:
        # Modo interativo
        menu_principal() 