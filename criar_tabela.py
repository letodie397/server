import sqlite3

# Cria a conexão com o banco de dados
conn = sqlite3.connect('meu_banco.db')
cursor = conn.cursor()

# Cria a tabela de usuários se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id TEXT PRIMARY KEY,
    nome TEXT,
    email TEXT
)
''')

# Insere um registro de teste
cursor.execute('''
INSERT OR REPLACE INTO usuarios (id, nome, email)
VALUES ('1', 'Usuário Teste', 'teste@example.com')
''')

# Commit e fechamento da conexão
conn.commit()
conn.close()

print('Tabela criada e dados inseridos com sucesso!') 