from flask import Flask, jsonify, request, make_response, redirect
import sqlite3
import os
import json
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

# Configuração do banco de dados
# Se estiver no ambiente Render, o banco fica em /etc/secrets/
# Em ambiente de desenvolvimento, usamos o caminho local
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    # Caminho padrão para ambiente local
    if os.name == 'nt':  # Windows
        DATABASE_URL = 'C:\\sqlite\\meu_banco.db'
    else:  # Linux, Mac
        DATABASE_URL = '/etc/secrets/meu_banco.db'
    
print(f"Usando banco de dados em: {DATABASE_URL}")

# Função para obter conexão com o banco
def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

# Garantir que o banco de dados tenha a tabela 'churches'
def ensure_tables_exist():
    print(f"Inicializando banco de dados em: {DATABASE_URL}")
    try:
        conn = get_db_connection()
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
        
        # Verificar se há registros na tabela churches
        cursor.execute("SELECT COUNT(*) FROM churches")
        count = cursor.fetchone()[0]
        print(f"Encontrados {count} registros na tabela churches")
        
        # Se não houver registros, adicionar um exemplo
        if count == 0:
            print("Adicionando registro de exemplo na tabela churches")
            cursor.execute('''
            INSERT INTO churches (id, nome, morada, ano, agendamento, autorizadoFilippi, arquivada, dados)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'demo1', 
                'Igreja Exemplo', 
                'Rua de Exemplo, 123', 
                '2023', 
                'Sim', 
                'Sim', 
                0, 
                json.dumps({"info": "Dados de exemplo para teste"})
            ))
        
        conn.commit()
        conn.close()
        print(f"Banco de dados inicializado com sucesso em {DATABASE_URL}")
        return True
    except Exception as e:
        print(f"ERRO ao inicializar banco de dados: {str(e)}")
        return False

# Adicionar cabeçalhos CORS a todas as respostas
@app.after_request
def after_request(response):
    # Garantir que estes cabeçalhos estejam em todas as respostas
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept, Origin, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '86400')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    # Prevenir problema com cache
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')
    return response

# Rota OPTIONS global para preflight requests
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Origin, X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Max-Age'] = '86400'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# Verificar se o banco de dados está acessível
@app.route('/check-db')
def check_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar quais tabelas existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = [row['name'] for row in cursor.fetchall() if row['name'] != 'sqlite_sequence']
        
        # Testar a conexão com cada tabela
        resultados = {}
        for tabela in tabelas:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {tabela}")
                count = cursor.fetchone()['count']
                resultados[tabela] = {
                    "status": "ok",
                    "registros": count
                }
            except Exception as e:
                resultados[tabela] = {
                    "status": "erro",
                    "mensagem": str(e)
                }
        
        conn.close()
        
        return jsonify({
            "status": "ok",
            "mensagem": "Banco de dados acessível",
            "caminho": DATABASE_URL,
            "tabelas": tabelas,
            "detalhes": resultados
        })
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro ao acessar banco de dados: {str(e)}",
            "caminho": DATABASE_URL
        }), 500

# Redirecionar solicitações com caminho incorreto para a raiz
@app.route('/ping/<path:path>', methods=['GET'])
def redirect_ping(path):
    return redirect('/ping', code=302)

# Redirecionar solicitações com caminho incorreto para a raiz
@app.route('/health/<path:path>', methods=['GET'])
def redirect_health(path):
    return redirect('/health', code=302)

# Rota de health check para o Render
@app.route('/health')
@app.route('/ping')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Servidor ativo',
        'cors': 'habilitado',
        'version': '1.3.0'
    })

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
    return jsonify({
        'message': 'API do servidor funcionando!',
        'cors': 'habilitado',
        'version': '1.3.0'
    })

# Tratamento de erros 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Rota não encontrada',
        'status': 404,
        'message': 'A URL solicitada não existe neste servidor.'
    }), 404

# Tratamento de erros 500
@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'error': 'Erro interno do servidor',
        'status': 500,
        'message': str(e)
    }), 500

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
    # Se for uma das rotas especiais, redirecionar
    if tabela in ['ping', 'health', 'check-db']:
        return redirect(f'/{tabela}', code=302)
        
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
        return jsonify({
            'error': str(e),
            'message': f'Erro ao acessar tabela {tabela}. Verifique se a tabela existe.',
            'sugestão': 'Use a rota /tabelas para listar as tabelas disponíveis.'
        }), 500

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
    # Garantir que as tabelas existam antes de iniciar o servidor
    ensure_tables_exist()
    
    # Configuração para deploy no Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 