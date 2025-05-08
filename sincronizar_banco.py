import sqlite3
import requests
import json
import time
import os
import sys
from datetime import datetime

# Configurações
BANCO_LOCAL = 'C:\\sqlite\\meu_banco.db'
API_URL = 'https://server-qx03.onrender.com'  # Substitua pelo seu URL do Render
INTERVALO_SYNC = 300  # Sincronizar a cada 5 minutos
PRIORIZAR_LOCAL = True  # Priorizar dados locais em caso de conflito

def obter_tabelas_local():
    """Obtém a lista de tabelas do banco de dados local"""
    conn = sqlite3.connect(BANCO_LOCAL)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    conn.close()
    return tabelas

def obter_tabelas_render():
    """Obtém a lista de tabelas do banco de dados no Render"""
    try:
        response = requests.get(f"{API_URL}/tabelas")
        if response.status_code == 200:
            return response.json().get('tabelas', [])
        print(f"Erro ao obter tabelas do Render: {response.status_code}")
        return []
    except Exception as e:
        print(f"Erro de conexão com o Render: {e}")
        return []

def obter_dados_tabela_local(tabela):
    """Obtém todos os dados de uma tabela local"""
    conn = sqlite3.connect(BANCO_LOCAL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {tabela}")
    
    registros = {}
    for row in cursor.fetchall():
        data = dict(row)
        id_registro = data.pop('id')
        registros[id_registro] = data
        
    conn.close()
    return registros

def obter_dados_tabela_render(tabela):
    """Obtém todos os dados de uma tabela no Render"""
    try:
        response = requests.get(f"{API_URL}/{tabela}")
        if response.status_code == 200:
            return response.json()
        print(f"Erro ao obter dados da tabela {tabela} do Render: {response.status_code}")
        return {}
    except Exception as e:
        print(f"Erro de conexão com o Render: {e}")
        return {}

def atualizar_registro_local(tabela, id_registro, dados):
    """Atualiza ou insere um registro no banco local"""
    conn = sqlite3.connect(BANCO_LOCAL)
    cursor = conn.cursor()
    
    # Verifica quais colunas existem na tabela
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [info[1] for info in cursor.fetchall() if info[1] != 'id']
    
    # Filtra os dados para incluir apenas colunas válidas
    valores = []
    campos = []
    for coluna in colunas:
        if coluna in dados:
            campos.append(coluna)
            # Converte objetos complexos para JSON
            valor = dados[coluna]
            if isinstance(valor, (dict, list)):
                valor = json.dumps(valor)
            valores.append(valor)
    
    if not campos:
        conn.close()
        return False
    
    # Verifica se o registro já existe
    cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE id = ?", (id_registro,))
    existe = cursor.fetchone()[0] > 0
    
    if existe:
        # Atualiza o registro
        placeholders = ', '.join([f'{campo} = ?' for campo in campos])
        query = f"UPDATE {tabela} SET {placeholders} WHERE id = ?"
        cursor.execute(query, valores + [id_registro])
    else:
        # Insere um novo registro
        placeholders = ', '.join(['?'] * len(campos))
        query = f"INSERT INTO {tabela} (id, {', '.join(campos)}) VALUES (?, {placeholders})"
        cursor.execute(query, [id_registro] + valores)
    
    conn.commit()
    conn.close()
    return True

def atualizar_registro_render(tabela, id_registro, dados):
    """Atualiza ou insere um registro no Render"""
    try:
        response = requests.put(f"{API_URL}/{tabela}/{id_registro}", json=dados)
        if response.status_code in [200, 201]:
            return True
        print(f"Erro ao atualizar registro {id_registro} na tabela {tabela} no Render: {response.status_code}")
        return False
    except Exception as e:
        print(f"Erro de conexão com o Render: {e}")
        return False

def criar_tabela_local(tabela, campos):
    """Cria uma tabela no banco local caso não exista"""
    conn = sqlite3.connect(BANCO_LOCAL)
    cursor = conn.cursor()
    
    # Cria os campos da tabela
    campo_sql = ["id TEXT PRIMARY KEY"]
    for campo in campos:
        campo_sql.append(f"{campo} TEXT")
    
    # Cria a tabela se não existir
    sql = f"CREATE TABLE IF NOT EXISTS {tabela} ({', '.join(campo_sql)})"
    cursor.execute(sql)
    
    conn.commit()
    conn.close()
    return True

def obter_ultima_modificacao_local(tabela, id_registro):
    """Simula a obtenção da data de última modificação local (não implementado ainda)"""
    # Em uma implementação real, você pode adicionar um campo de timestamp na tabela
    # Por enquanto, consideramos que local é sempre mais recente se a opção estiver ativa
    return PRIORIZAR_LOCAL

def sincronizar():
    """Sincroniza os bancos de dados local e Render"""
    print(f"[{datetime.now()}] Iniciando sincronização...")
    
    # Certifica-se de que o diretório do banco existe
    os.makedirs(os.path.dirname(BANCO_LOCAL), exist_ok=True)
    
    # Cria o banco se não existir
    if not os.path.exists(BANCO_LOCAL):
        print(f"Banco de dados local não encontrado. Criando em {BANCO_LOCAL}")
        conn = sqlite3.connect(BANCO_LOCAL)
        conn.close()
    
    # Obtém as tabelas de ambos os bancos
    tabelas_local = obter_tabelas_local()
    tabelas_render = obter_tabelas_render()
    
    # Para cada tabela no Render, sincroniza com o local
    for tabela in tabelas_render:
        print(f"Sincronizando tabela: {tabela}")
        
        # Obtém os dados de ambos os lados
        dados_render = obter_dados_tabela_render(tabela)
        
        # Cria a tabela localmente se não existir
        if tabela not in tabelas_local and dados_render:
            # Pega os campos do primeiro registro como modelo
            primeiro_id = list(dados_render.keys())[0]
            campos = list(dados_render[primeiro_id].keys())
            criar_tabela_local(tabela, campos)
            tabelas_local.append(tabela)  # Atualiza a lista local
        
        # Agora obtém os dados locais (após possível criação da tabela)
        dados_local = obter_dados_tabela_local(tabela) if tabela in tabelas_local else {}
        
        # Processa registros do local para o Render (PRIORIDADE)
        for id_registro, dados in dados_local.items():
            # Se não existe no Render ou os dados locais têm prioridade
            if id_registro not in dados_render or PRIORIZAR_LOCAL:
                atualizar_registro_render(tabela, id_registro, dados)
                print(f"  Enviado registro {id_registro} da tabela {tabela} para o Render")
        
        # Processa registros do Render para o local (APENAS NOVOS REGISTROS)
        for id_registro, dados in dados_render.items():
            # Apenas se não existir localmente (não sobrescreve dados locais)
            if id_registro not in dados_local:
                atualizar_registro_local(tabela, id_registro, dados)
                print(f"  Baixado novo registro {id_registro} da tabela {tabela} para o local")
    
    print(f"[{datetime.now()}] Sincronização concluída!")

def sincronizar_continuamente():
    """Executa a sincronização continuamente no intervalo definido"""
    while True:
        try:
            sincronizar()
        except Exception as e:
            print(f"Erro durante a sincronização: {e}")
        
        print(f"Próxima sincronização em {INTERVALO_SYNC} segundos...")
        time.sleep(INTERVALO_SYNC)

if __name__ == "__main__":
    # Exibe mensagem sobre priorização de dados
    if PRIORIZAR_LOCAL:
        print("MODO PRIORIDADE LOCAL: Os dados do seu PC terão prioridade sobre os dados no Render")
    
    # Verifica se é para sincronizar uma vez ou continuamente
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        sincronizar()
    else:
        print("Iniciando sincronização contínua. Pressione Ctrl+C para sair.")
        try:
            sincronizar_continuamente()
        except KeyboardInterrupt:
            print("Sincronização interrompida pelo usuário.") 