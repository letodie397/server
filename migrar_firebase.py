import json
import sqlite3
import os
import time

# Caminho para o arquivo JSON exportado do Firebase
firebase_json_path = 'appteste-dc435-default-rtdb-export.json'  # Caminho relativo na pasta atual

# Caminho para o banco de dados SQLite
sqlite_db_path = 'C:\\sqlite\\meu_banco.db'

# Função para criar tabelas no SQLite baseadas na estrutura do JSON
def criar_tabela_sqlite(cursor, nome_tabela, estrutura):
    # Caso especial para a tabela tokens onde os valores são strings e não dicionários
    if nome_tabela == 'tokens':
        query_criar_tabela = "CREATE TABLE IF NOT EXISTS tokens (id TEXT PRIMARY KEY, token TEXT)"
        cursor.execute(query_criar_tabela)
        print(f"Tabela {nome_tabela} criada com sucesso!")
        return
    
    # Para outras tabelas, seguimos o fluxo normal
    if not estrutura:
        print(f"Nenhum dado para criar a tabela {nome_tabela}")
        return
    
    # Pegamos o primeiro registro para determinar as colunas
    primeiro_id = list(estrutura.keys())[0]
    primeiro_registro = estrutura[primeiro_id]
    
    # Verificamos se o primeiro registro é um dicionário
    if not isinstance(primeiro_registro, dict):
        print(f"Aviso: O registro {primeiro_id} na tabela {nome_tabela} não é um dicionário válido. Valor: {primeiro_registro}")
        return
    
    # Criamos colunas para cada campo no registro
    colunas = ["id TEXT PRIMARY KEY"]
    for campo in primeiro_registro:
        # Define o tipo de dado para a coluna com base no tipo do valor
        valor = primeiro_registro[campo]
        tipo_sql = 'TEXT'  # padrão
        
        if isinstance(valor, int):
            tipo_sql = 'INTEGER'
        elif isinstance(valor, float):
            tipo_sql = 'REAL'
        elif isinstance(valor, bool):
            tipo_sql = 'INTEGER'  # SQLite não tem tipo booleano nativo
        elif isinstance(valor, (dict, list)):
            tipo_sql = 'TEXT'  # Armazenamos objetos complexos como JSON
            
        colunas.append(f"{campo} {tipo_sql}")
    
    # Criamos a tabela
    query_criar_tabela = f"CREATE TABLE IF NOT EXISTS {nome_tabela} ({', '.join(colunas)})"
    cursor.execute(query_criar_tabela)
    print(f"Tabela {nome_tabela} criada com sucesso!")

# Função para inserir dados nas tabelas
def inserir_dados_sqlite(cursor, nome_tabela, dados):
    registros_inseridos = 0
    registros_ignorados = 0
    
    # Caso especial para a tabela tokens
    if nome_tabela == 'tokens':
        for id_registro, valor in dados.items():
            # Para tokens, os valores são strings diretas
            try:
                cursor.execute("INSERT OR REPLACE INTO tokens (id, token) VALUES (?, ?)", 
                              (id_registro, str(valor)))
                registros_inseridos += 1
                if registros_inseridos % 100 == 0:
                    print(f"Tabela {nome_tabela}: {registros_inseridos} registros inseridos...")
            except Exception as e:
                print(f"Erro ao inserir token {id_registro}: {e}")
                registros_ignorados += 1
        
        print(f"Tabela {nome_tabela}: Total de {registros_inseridos} registros inseridos, {registros_ignorados} ignorados.")
        return registros_inseridos
    
    # Para outras tabelas, seguimos o fluxo normal para valores de dicionário
    for id_registro, valores in dados.items():
        # Verifica se valores é um dicionário
        if not isinstance(valores, dict):
            print(f"Aviso: O registro {id_registro} na tabela {nome_tabela} não é um dicionário válido. Pulando.")
            registros_ignorados += 1
            continue
            
        # Prepara os campos e valores para a inserção
        campos = ['id'] + list(valores.keys())
        valores_placeholder = ['?'] * (len(campos))
        
        # Prepara a query de inserção
        query = f"INSERT OR REPLACE INTO {nome_tabela} ({', '.join(campos)}) VALUES ({', '.join(valores_placeholder)})"
        
        # Prepara os valores para inserção
        valores_inserir = [id_registro]
        for campo in list(valores.keys()):
            valor = valores[campo]
            # Converte dicionários e listas para JSON string
            if isinstance(valor, (dict, list)):
                valor = json.dumps(valor)
            valores_inserir.append(valor)
        
        try:
            # Executa a inserção
            cursor.execute(query, valores_inserir)
            registros_inseridos += 1
            # Mostra progresso a cada 100 registros
            if registros_inseridos % 100 == 0:
                print(f"Tabela {nome_tabela}: {registros_inseridos} registros inseridos...")
        except Exception as e:
            print(f"Erro ao inserir registro {id_registro} na tabela {nome_tabela}: {e}")
            registros_ignorados += 1
            continue
    
    print(f"Tabela {nome_tabela}: Total de {registros_inseridos} registros inseridos, {registros_ignorados} ignorados.")
    return registros_inseridos

# Função principal
def migrar_firebase_para_sqlite():
    tempo_inicio = time.time()
    print("Iniciando migração dos dados do Firebase para SQLite...")
    print(f"Arquivo JSON: {os.path.abspath(firebase_json_path)}")
    print(f"Banco SQLite: {sqlite_db_path}")
    
    # Verifica se o arquivo JSON existe
    if not os.path.exists(firebase_json_path):
        print(f"Arquivo JSON não encontrado: {firebase_json_path}")
        return
    
    # Verifica se o diretório de destino existe
    diretorio_db = os.path.dirname(sqlite_db_path)
    if not os.path.exists(diretorio_db):
        os.makedirs(diretorio_db, exist_ok=True)
        print(f"Diretório criado: {diretorio_db}")
    
    print(f"Carregando arquivo JSON ({os.path.getsize(firebase_json_path)/1024/1024:.2f} MB)...")
    
    # Carrega os dados do JSON
    try:
        with open(firebase_json_path, 'r', encoding='utf-8') as file:
            firebase_data = json.load(file)
        
        if not firebase_data:
            print("O arquivo JSON está vazio ou inválido.")
            return
        
        print(f"JSON carregado com sucesso. {len(firebase_data)} tabelas encontradas.")
            
    except json.JSONDecodeError:
        print(f"Erro ao decodificar o JSON: {firebase_json_path}")
        return
    except Exception as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
        return
    
    # Conecta ao banco SQLite
    try:
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()
        
        total_registros = 0
        # Para cada nó de primeiro nível no JSON, criamos uma tabela
        for tabela, dados in firebase_data.items():
            try:
                print(f"\nProcessando tabela: {tabela} ({len(dados)} registros)")
                criar_tabela_sqlite(cursor, tabela, dados)
                registros_inseridos = inserir_dados_sqlite(cursor, tabela, dados)
                total_registros += registros_inseridos
                print(f"Dados inseridos na tabela {tabela} com sucesso!")
            except Exception as e:
                print(f"Erro ao processar a tabela {tabela}: {e}")
                continue
        
        # Confirma as alterações e fecha a conexão
        print("\nConfirmando transações...")
        conn.commit()
        conn.close()
        
        tempo_total = time.time() - tempo_inicio
        print(f"\nMigração concluída em {tempo_total:.2f} segundos!")
        print(f"Total de {total_registros} registros migrados para o banco SQLite: {sqlite_db_path}")
    except sqlite3.Error as e:
        print(f"Erro de SQLite: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    migrar_firebase_para_sqlite()