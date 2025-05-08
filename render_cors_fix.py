#!/usr/bin/env python
"""
Script para verificar e corrigir problemas CORS específicos do Render
"""

import requests
import json
import sys
import time
import os
import argparse

# URL do serviço no Render
RENDER_URL = "https://server-qx03.onrender.com"

def verificar_cors():
    """Verifica se os cabeçalhos CORS estão configurados corretamente"""
    print("\n[+] Verificando configuração CORS no servidor...")
    try:
        response = requests.options(f"{RENDER_URL}/ping", timeout=10)
        
        # Cabeçalhos CORS esperados
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept, Origin, X-Requested-With',
            'Access-Control-Allow-Credentials': 'true'
        }
        
        # Verificar presença e valor dos cabeçalhos
        problemas = []
        for header, expected_value in cors_headers.items():
            if header.lower() in [h.lower() for h in response.headers]:
                # Obter o cabeçalho independente da capitalização
                actual_header = next(h for h in response.headers if h.lower() == header.lower())
                actual_value = response.headers[actual_header]
                
                # Verificar se o valor contém o esperado
                if expected_value == '*' or expected_value in actual_value:
                    print(f"  ✓ {header}: {actual_value}")
                else:
                    print(f"  ✗ {header}: {actual_value}")
                    print(f"    Esperado: {expected_value}")
                    problemas.append(f"Valor incorreto para {header}")
            else:
                print(f"  ✗ {header} não encontrado nos cabeçalhos")
                problemas.append(f"Cabeçalho {header} ausente")
        
        if not problemas:
            print("\n[✓] Configuração CORS parece estar correta!")
        else:
            print("\n[✗] Problemas encontrados na configuração CORS:")
            for problema in problemas:
                print(f"  - {problema}")
                
        return not problemas
    
    except Exception as e:
        print(f"\n[✗] Erro ao verificar CORS: {e}")
        return False

def verificar_rotas_preflight():
    """Verifica se o servidor está respondendo a requisições OPTIONS para várias rotas"""
    print("\n[+] Verificando resposta a requisições preflight (OPTIONS)...")
    
    # Rotas para verificar
    rotas = ['/', '/ping', '/churches', '/tabelas']
    
    problemas = []
    for rota in rotas:
        try:
            print(f"  Verificando rota {rota}...")
            response = requests.options(f"{RENDER_URL}{rota}", timeout=10)
            
            if response.status_code in [200, 204]:
                print(f"  ✓ {rota}: Status {response.status_code}")
                if 'Access-Control-Allow-Origin' in response.headers:
                    print(f"    ✓ Cabeçalho CORS presente")
                else:
                    print(f"    ✗ Cabeçalho CORS ausente")
                    problemas.append(f"Rota {rota} não retorna cabeçalhos CORS")
            else:
                print(f"  ✗ {rota}: Status {response.status_code}")
                problemas.append(f"Rota {rota} retornou status {response.status_code}")
        except Exception as e:
            print(f"  ✗ Erro ao verificar rota {rota}: {e}")
            problemas.append(f"Erro ao verificar rota {rota}: {e}")
    
    if not problemas:
        print("\n[✓] Todas as rotas respondem corretamente a requisições OPTIONS!")
    else:
        print("\n[✗] Problemas encontrados nas respostas OPTIONS:")
        for problema in problemas:
            print(f"  - {problema}")
            
    return not problemas

def verificar_tabela_churches():
    """Verifica se a tabela churches existe e tem dados"""
    print("\n[+] Verificando tabela 'churches'...")
    try:
        # Tenta acessar diretamente primeiro
        response = requests.get(f"{RENDER_URL}/churches", timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            if dados:
                print(f"  ✓ Tabela 'churches' encontrada com {len(dados)} registros")
                print("  ✓ Acessível sem proxy CORS")
                return True
            else:
                print("  ! Tabela 'churches' existe mas está vazia")
        else:
            print(f"  ✗ Erro ao acessar tabela 'churches': {response.status_code}")
            
        # Se falhou, tentar via proxy CORS
        print("  Tentando acessar via proxy CORS (AllOrigins)...")
        
        proxy_url = f"https://api.allorigins.win/raw?url={RENDER_URL}/churches"
        proxy_response = requests.get(proxy_url, timeout=15)
        
        if proxy_response.status_code == 200:
            dados_proxy = proxy_response.json()
            if dados_proxy:
                print(f"  ✓ Tabela 'churches' acessível via proxy com {len(dados_proxy)} registros")
                print("  ! Acessível apenas via proxy CORS (possível problema de CORS)")
                return True
            else:
                print("  ! Tabela 'churches' existe mas está vazia (via proxy)")
                return False
        else:
            print(f"  ✗ Erro ao acessar via proxy: {proxy_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Erro ao verificar tabela: {e}")
        return False

def sugerir_correcoes():
    """Sugere correções para problemas comuns"""
    print("\n[+] Sugestões de correção para problemas comuns:")
    
    print("""
1. Garantir que o Flask-CORS esteja instalado:
   ```
   pip install Flask-CORS
   ```

2. Verificar a configuração CORS no servidor.py:
   ```python
   from flask_cors import CORS
   
   app = Flask(__name__)
   
   # Configuração CORS para permitir acesso de qualquer origem
   CORS(app, resources={r"/*": {
       "origins": "*",
       "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
       "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
       "expose_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
       "max_age": 86400
   }}, supports_credentials=True)
   ```

3. Adicionar decorador @after_request para garantir cabeçalhos CORS:
   ```python
   @app.after_request
   def after_request(response):
       response.headers.add('Access-Control-Allow-Origin', '*')
       response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
       response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
       response.headers.add('Access-Control-Max-Age', '86400')
       return response
   ```

4. Implementar rota OPTIONS explícita:
   ```python
   @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
   @app.route('/<path:path>', methods=['OPTIONS'])
   def options_handler(path):
       response = make_response()
       response.headers['Access-Control-Allow-Origin'] = '*'
       response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
       response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
       return response
   ```

5. No cliente, usar fallbacks de proxy CORS:
   - AllOrigins: https://api.allorigins.win/raw?url=URL_ENCODED
   - corsproxy.io: https://corsproxy.io/?URL_ENCODED
    """)

def testar_proxies_cors():
    """Testa diferentes proxies CORS"""
    print("\n[+] Testando proxies CORS populares...")
    
    proxies = [
        {
            'nome': 'AllOrigins',
            'url': f"https://api.allorigins.win/raw?url={RENDER_URL}/ping"
        },
        {
            'nome': 'corsproxy.io',
            'url': f"https://corsproxy.io/?{RENDER_URL}/ping"
        },
        {
            'nome': 'CORS Anywhere',
            'url': f"https://cors-anywhere.herokuapp.com/{RENDER_URL}/ping"
        }
    ]
    
    for proxy in proxies:
        print(f"\n  Testando {proxy['nome']}...")
        try:
            inicio = time.time()
            response = requests.get(proxy['url'], timeout=15)
            duracao = time.time() - inicio
            
            if response.status_code == 200:
                print(f"  ✓ {proxy['nome']} funciona! Status: {response.status_code}")
                print(f"    Tempo de resposta: {duracao:.2f} segundos")
                
                try:
                    dados = response.json()
                    print(f"    Conteúdo: {json.dumps(dados)[:100]}...")
                except:
                    print(f"    Conteúdo: {response.text[:100]}...")
            else:
                print(f"  ✗ {proxy['nome']} falhou. Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Erro ao testar {proxy['nome']}: {e}")

def verificar_status_deploy():
    """Verifica o status do deploy no Render"""
    print("\n[+] Verificando status do deploy no Render...")
    
    try:
        response = requests.get(f"{RENDER_URL}/ping", timeout=10)
        if response.status_code == 200:
            dados = response.json()
            print(f"  ✓ Servidor online! Status: {response.status_code}")
            print(f"  ✓ Versão da API: {dados.get('version', 'desconhecida')}")
            
            # Verificar banco de dados
            try:
                db_response = requests.get(f"{RENDER_URL}/check-db", timeout=10)
                if db_response.status_code == 200:
                    db_dados = db_response.json()
                    print(f"  ✓ Banco de dados: {db_dados.get('status', 'desconhecido')}")
                    print(f"  ✓ Caminho: {db_dados.get('caminho', 'desconhecido')}")
                    
                    tabelas = db_dados.get('tabelas', [])
                    if tabelas:
                        print(f"  ✓ Tabelas disponíveis: {', '.join(tabelas)}")
                    else:
                        print(f"  ! Nenhuma tabela encontrada no banco de dados")
                else:
                    print(f"  ✗ Erro ao verificar banco de dados: {db_response.status_code}")
            except Exception as e:
                print(f"  ✗ Erro ao verificar banco de dados: {e}")
            
            return True
        else:
            print(f"  ✗ Servidor respondeu com status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Erro ao conectar com o servidor: {e}")
        return False

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description='Verifica e corrige problemas CORS no Render')
    parser.add_argument('--check-only', action='store_true', help='Apenas verifica, sem sugerir correções')
    parser.add_argument('--test-proxies', action='store_true', help='Testa proxies CORS')
    parser.add_argument('--check-deploy', action='store_true', help='Verifica status do deploy')
    parser.add_argument('--url', type=str, help=f'URL do servidor (padrão: {RENDER_URL})')
    
    args = parser.parse_args()
    
    # Permitir alterar a URL via argumento
    global RENDER_URL
    if args.url:
        RENDER_URL = args.url
        print(f"[i] Usando URL alternativa: {RENDER_URL}")
    
    print("=" * 70)
    print("           DIAGNÓSTICO DE PROBLEMAS CORS NO RENDER           ")
    print("=" * 70)
    
    if args.check_deploy:
        verificar_status_deploy()
    
    # Verifica configuração CORS
    cors_ok = verificar_cors()
    
    # Verifica rotas preflight
    preflight_ok = verificar_rotas_preflight()
    
    # Verifica tabela churches
    tabela_ok = verificar_tabela_churches()
    
    # Testa proxies CORS se solicitado
    if args.test_proxies:
        testar_proxies_cors()
    
    # Sugere correções se solicitado
    if not args.check_only:
        sugerir_correcoes()
    
    # Resumo final
    print("\n" + "=" * 70)
    print("                         RESUMO                             ")
    print("=" * 70)
    print(f"Configuração CORS: {'✓ OK' if cors_ok else '✗ Problemas encontrados'}")
    print(f"Rotas preflight:   {'✓ OK' if preflight_ok else '✗ Problemas encontrados'}")
    print(f"Tabela churches:   {'✓ OK' if tabela_ok else '✗ Problemas encontrados'}")
    
    if not (cors_ok and preflight_ok and tabela_ok):
        print("\nRecomendação: Execute este script com a opção --test-proxies para testar")
        print("alternativas de acesso via proxy CORS.")
    else:
        print("\n[✓] Tudo parece estar corretamente configurado!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1) 