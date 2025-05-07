from flask import Flask, jsonify, request
import sqlite3
import os
import json
from flask_cors import CORS  # Importando a extensão Flask-CORS

app = Flask(__name__)
CORS(app)  # Habilitando CORS para todas as rotas

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL', 'C:\\sqlite\\meu_banco.db')

# Função para obter conexão com o banco
def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

# Função para converter objetos JSON armazenados como string de volta para objetos Python
def parse_json_fields(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    data[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
    return data

# Rota principal
@app.route('/')
def index():
    return jsonify({'message': 'API do servidor funcionando!'})

# Listar todas as tabelas
@app.route('/tabelas')
def list_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Consulta para listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = [row['name'] for row in cursor.fetchall() if row['name'] != 'sqlite_sequence']
    
    conn.close()
    return jsonify({'tabelas': tabelas})

# Obter todos os registros de uma tabela
@app.route('/<tabela>', methods=['GET'])
def get_all(tabela):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {tabela}")
        registros = cursor.fetchall()
        
        # Converter os resultados para um dicionário
        resultado = {}
        for registro in registros:
            dados = dict(registro)
            id_registro = dados.pop('id')
            # Parse JSON strings back to objects
            resultado[id_registro] = parse_json_fields(dados)
            
        conn.close()
        return jsonify(resultado)
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# Obter um registro específico
@app.route('/<tabela>/<id>', methods=['GET'])
def get_one(tabela, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {tabela} WHERE id = ?", (id,))
        registro = cursor.fetchone()
        
        if registro:
            dados = dict(registro)
            id_registro = dados.pop('id')
            # Parse JSON strings back to objects
            resultado = parse_json_fields(dados)
            conn.close()
            return jsonify({id_registro: resultado})
        else:
            conn.close()
            return jsonify({'error': 'Registro não encontrado'}), 404
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# Inserir um novo registro
@app.route('/<tabela>/<id>', methods=['PUT'])
def insert_or_update(tabela, id):
    dados = request.json
    
    if not dados:
        return jsonify({'error': 'Dados não fornecidos'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtém as colunas da tabela
        cursor.execute(f"PRAGMA table_info({tabela})")
        columns = [row['name'] for row in cursor.fetchall() if row['name'] != 'id']
        
        # Prepara os valores e campos para inserção/atualização
        valores = []
        campos_atualizados = []
        
        for column in columns:
            if column in dados:
                valor = dados[column]
                # Converte objetos complexos para JSON
                if isinstance(valor, (dict, list)):
                    valor = json.dumps(valor)
                valores.append(valor)
                campos_atualizados.append(column)
        
        if not campos_atualizados:
            conn.close()
            return jsonify({'error': 'Nenhum campo válido fornecido'}), 400
            
        # Verifica se o registro já existe
        cursor.execute(f"SELECT id FROM {tabela} WHERE id = ?", (id,))
        existe = cursor.fetchone()
        
        if existe:
            # Atualiza o registro existente
            query = f"UPDATE {tabela} SET {', '.join([f'{campo} = ?' for campo in campos_atualizados])} WHERE id = ?"
            cursor.execute(query, valores + [id])
            message = 'Registro atualizado com sucesso'
        else:
            # Insere um novo registro
            query = f"INSERT INTO {tabela} (id, {', '.join(campos_atualizados)}) VALUES (?, {', '.join(['?'] * len(campos_atualizados))})"
            cursor.execute(query, [id] + valores)
            message = 'Registro inserido com sucesso'
            
        conn.commit()
        conn.close()
        return jsonify({'message': message})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# Excluir um registro
@app.route('/<tabela>/<id>', methods=['DELETE'])
def delete(tabela, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DELETE FROM {tabela} WHERE id = ?", (id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            conn.close()
            return jsonify({'message': 'Registro excluído com sucesso'})
        else:
            conn.close()
            return jsonify({'error': 'Registro não encontrado'}), 404
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Configuração para deploy no Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 