#!/bin/bash
# Script de inicialização para o Render

# Instala todas as dependências
pip install -r requirements.txt

# Configuração da variável de ambiente para o banco de dados
export DATABASE_URL="/etc/secrets/meu_banco.db"

# Certifique-se que o banco de dados está na pasta correta
if [ -f "/etc/secrets/meu_banco.db" ]; then
  echo "Banco de dados encontrado em /etc/secrets/meu_banco.db"
else
  echo "AVISO: Banco de dados não encontrado em /etc/secrets/meu_banco.db"
  # Se o banco de dados não existir, vamos criar um novo
  echo "Criando um novo banco de dados..."
  sqlite3 /etc/secrets/meu_banco.db "VACUUM;"
  echo "Banco de dados criado em /etc/secrets/meu_banco.db"
fi

# Executar script para criar as tabelas necessárias
echo "Executando script para garantir que as tabelas existam..."
python -c "
from servidor import ensure_tables_exist
print('Inicializando tabelas...')
ensure_tables_exist()
print('Tabelas inicializadas com sucesso!')
"

# Inicia o servidor com gunicorn
gunicorn servidor:app --bind 0.0.0.0:$PORT 