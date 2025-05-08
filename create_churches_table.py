import sqlite3
import json
import os

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL', 'C:\\sqlite\\meu_banco.db')

def criar_e_popular_tabela_churches():
    print(f"Verificando banco de dados em {DATABASE_URL}")
    
    # Garantir que o diretório exista
    os.makedirs(os.path.dirname(DATABASE_URL), exist_ok=True)
    
    # Conectar ao banco
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Criar tabela churches se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS churches (
        id TEXT PRIMARY KEY,
        nome TEXT,
        morada TEXT,
        ano TEXT,
        agendamento TEXT,
        autorizadoFilippi TEXT,
        arquivada INTEGER DEFAULT 0,
        dados TEXT
    )
    ''')
    
    print("Tabela 'churches' verificada/criada.")
    
    # Verificar se há registros na tabela
    cursor.execute("SELECT COUNT(*) FROM churches")
    count = cursor.fetchone()[0]
    print(f"Registros encontrados: {count}")
    
    # Se não houver registros, adicionar alguns exemplos
    if count == 0:
        print("Adicionando registros de exemplo...")
        
        exemplos = [
            {
                'id': 'demo1',
                'nome': 'Igreja Exemplo 1',
                'morada': 'Rua de Exemplo, 123',
                'ano': '2023',
                'agendamento': 'Sim',
                'autorizadoFilippi': 'Sim',
                'arquivada': 0,
                'dados': json.dumps({"info": "Dados de exemplo para teste"})
            },
            {
                'id': 'demo2',
                'nome': 'Igreja Exemplo 2',
                'morada': 'Avenida Principal, 456',
                'ano': '2022',
                'agendamento': 'Não',
                'autorizadoFilippi': 'Sim',
                'arquivada': 0,
                'dados': json.dumps({"info": "Segunda igreja de exemplo"})
            }
        ]
        
        for exemplo in exemplos:
            cursor.execute('''
            INSERT INTO churches (id, nome, morada, ano, agendamento, autorizadoFilippi, arquivada, dados)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exemplo['id'],
                exemplo['nome'],
                exemplo['morada'],
                exemplo['ano'],
                exemplo['agendamento'],
                exemplo['autorizadoFilippi'],
                exemplo['arquivada'],
                exemplo['dados']
            ))
            print(f"Adicionado registro com ID: {exemplo['id']}")
        
        conn.commit()
        print("Registros inseridos com sucesso!")
    
    # Listar todas as tabelas no banco de dados
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    print("Tabelas no banco de dados:")
    for tabela in tabelas:
        print(f"- {tabela[0]}")
    
    # Listar todos os registros na tabela churches
    cursor.execute("SELECT id, nome FROM churches")
    igrejas = cursor.fetchall()
    print("Registros na tabela churches:")
    for igreja in igrejas:
        print(f"- ID: {igreja[0]}, Nome: {igreja[1]}")
    
    conn.close()
    print("Operação concluída com sucesso!")

if __name__ == "__main__":
    criar_e_popular_tabela_churches() 