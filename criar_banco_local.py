import sqlite3
import os
import json

# Configuração
BANCO_LOCAL = 'C:\\sqlite\\meu_banco.db'

def criar_diretorio_se_nao_existir():
    """Cria o diretório do banco de dados se não existir"""
    diretorio = os.path.dirname(BANCO_LOCAL)
    if not os.path.exists(diretorio):
        try:
            os.makedirs(diretorio)
            print(f"Diretório {diretorio} criado com sucesso.")
        except Exception as e:
            print(f"Erro ao criar diretório {diretorio}: {e}")
            return False
    return True

def criar_banco_dados():
    """Cria o banco de dados SQLite se não existir"""
    try:
        conn = sqlite3.connect(BANCO_LOCAL)
        cursor = conn.cursor()
        
        # Tabela de exemplo
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            descricao TEXT,
            concluida INTEGER DEFAULT 0,
            data_criacao TEXT,
            data_conclusao TEXT
        )
        ''')
        
        # Inserir alguns dados de exemplo
        tarefas_exemplo = [
            ('1', 'Configurar servidor', 'Configurar servidor Flask no Render', 1, '2023-06-01', '2023-06-05'),
            ('2', 'Implementar banco de dados', 'Criar banco SQLite e APIs', 1, '2023-06-06', '2023-06-10'),
            ('3', 'Desenvolver frontend', 'Criar interface para testar APIs', 0, '2023-06-11', None)
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO tarefas (id, titulo, descricao, concluida, data_criacao, data_conclusao) VALUES (?, ?, ?, ?, ?, ?)',
            tarefas_exemplo
        )
        
        # Criar uma tabela para dados mais complexos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            dados_json TEXT,
            data_criacao TEXT
        )
        ''')
        
        # Inserir dados JSON de exemplo
        projetos_exemplo = [
            ('1', 'Projeto Web', 'Desenvolvimento web completo', 
             json.dumps({
                 'tecnologias': ['Flask', 'SQLite', 'JavaScript'],
                 'membros': [
                     {'nome': 'João', 'papel': 'Desenvolvedor'},
                     {'nome': 'Maria', 'papel': 'Designer'}
                 ],
                 'prazos': {
                     'inicio': '2023-06-01',
                     'fim': '2023-08-31'
                 }
             }), 
             '2023-06-01'
            ),
            ('2', 'App Mobile', 'Aplicativo para Android e iOS', 
             json.dumps({
                 'tecnologias': ['React Native', 'Firebase'],
                 'membros': [
                     {'nome': 'Pedro', 'papel': 'Desenvolvedor Mobile'},
                     {'nome': 'Ana', 'papel': 'UX/UI'}
                 ],
                 'prazos': {
                     'inicio': '2023-07-15',
                     'fim': '2023-10-31'
                 }
             }),
             '2023-07-15'
            )
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO projetos (id, nome, descricao, dados_json, data_criacao) VALUES (?, ?, ?, ?, ?)',
            projetos_exemplo
        )
        
        conn.commit()
        conn.close()
        print(f"Banco de dados {BANCO_LOCAL} criado/atualizado com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")
        return False

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    try:
        conn = sqlite3.connect(BANCO_LOCAL)
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        print(f"Tabelas encontradas: {', '.join(tabelas)}")
        
        # Verificar contagem de registros em cada tabela
        for tabela in tabelas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            contagem = cursor.fetchone()[0]
            print(f"Tabela '{tabela}': {contagem} registro(s)")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao testar conexão com o banco: {e}")
        return False

if __name__ == "__main__":
    print("Configurando banco de dados SQLite local...")
    if criar_diretorio_se_nao_existir():
        if criar_banco_dados():
            testar_conexao()
    
    print("\nPróximos passos:")
    print("1. Execute 'python servidor.py' para iniciar o servidor local")
    print("2. Abra o arquivo 'teste-banco.html' no navegador")
    print("3. Clique em 'Usar Servidor Local' e teste a conexão") 