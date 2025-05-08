import sqlite3
import os
import json
from datetime import datetime

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL', 'C:\\sqlite\\meu_banco.db')

def criar_tabela_churches():
    print(f"Criando tabela churches no banco {DATABASE_URL}...")
    
    # Verificar se o diretório existe
    db_dir = os.path.dirname(DATABASE_URL)
    if not os.path.exists(db_dir):
        print(f"Criando diretório {db_dir}...")
        os.makedirs(db_dir, exist_ok=True)
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Verificar se a tabela já existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='churches'")
    if cursor.fetchone():
        print("A tabela churches já existe. Deseja recriá-la? (s/n)")
        resposta = input().lower()
        if resposta != 's':
            print("Operação cancelada.")
            conn.close()
            return
        
        # Excluir a tabela existente
        cursor.execute("DROP TABLE churches")
        print("Tabela anterior excluída.")
    
    # Criar a tabela
    cursor.execute("""
    CREATE TABLE churches (
        id TEXT PRIMARY KEY,
        nome TEXT,
        morada TEXT,
        ano TEXT,
        autorizadoFilippi TEXT,
        agendamento TEXT,
        arquivada INTEGER DEFAULT 0,
        dados_extras TEXT
    )
    """)
    
    # Criar alguns registros de exemplo
    igrejas_exemplo = [
        {
            "id": "demo1",
            "nome": "Igreja Exemplo 1",
            "morada": "Rua Exemplo, 123",
            "ano": "2023",
            "autorizadoFilippi": "Sim",
            "agendamento": "2023-12-15",
            "arquivada": 0,
            "dados_extras": json.dumps({
                "telefone": "123456789",
                "email": "igreja1@exemplo.com",
                "responsavel": "João Silva"
            })
        },
        {
            "id": "demo2",
            "nome": "Igreja Exemplo 2",
            "morada": "Avenida Teste, 456",
            "ano": "2022",
            "autorizadoFilippi": "Não",
            "agendamento": "2023-11-20",
            "arquivada": 0,
            "dados_extras": json.dumps({
                "telefone": "987654321",
                "email": "igreja2@exemplo.com",
                "responsavel": "Maria Santos"
            })
        },
        {
            "id": "demo3",
            "nome": "Igreja Exemplo Arquivada",
            "morada": "Praça Central, 789",
            "ano": "2021",
            "autorizadoFilippi": "Sim",
            "agendamento": "2022-10-05",
            "arquivada": 1,
            "dados_extras": json.dumps({
                "telefone": "555666777",
                "email": "igreja3@exemplo.com",
                "responsavel": "Pedro Oliveira",
                "motivo_arquivamento": "Mudança de endereço"
            })
        }
    ]
    
    # Inserir registros de exemplo
    for igreja in igrejas_exemplo:
        cursor.execute("""
        INSERT INTO churches (id, nome, morada, ano, autorizadoFilippi, agendamento, arquivada, dados_extras)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            igreja["id"],
            igreja["nome"],
            igreja["morada"],
            igreja["ano"],
            igreja["autorizadoFilippi"],
            igreja["agendamento"],
            igreja["arquivada"],
            igreja["dados_extras"]
        ))
    
    # Commit e fechar conexão
    conn.commit()
    print(f"Tabela churches criada com sucesso com {len(igrejas_exemplo)} registros de exemplo!")
    
    # Verificar se foi criada corretamente
    cursor.execute("SELECT COUNT(*) FROM churches")
    count = cursor.fetchone()[0]
    print(f"Número de registros na tabela: {count}")
    
    # Listar registros criados
    cursor.execute("SELECT id, nome FROM churches")
    registros = cursor.fetchall()
    print("\nRegistros criados:")
    for registro in registros:
        print(f"ID: {registro[0]}, Nome: {registro[1]}")
    
    conn.close()

if __name__ == "__main__":
    criar_tabela_churches() 