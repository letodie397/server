#!/bin/bash
# Script de inicialização para o Render

# Instala todas as dependências
pip install -r requirements.txt

# Criação do diretório para o banco de dados
mkdir -p /tmp/sqlite
echo "Criando diretório para o banco de dados em /tmp/sqlite"

# Configuração da variável de ambiente para o banco de dados
export DATABASE_URL="/tmp/sqlite/meu_banco.db"
echo "DATABASE_URL configurado para $DATABASE_URL"

# Certifique-se que o banco de dados pode ser criado
if [ -f "$DATABASE_URL" ]; then
  echo "Banco de dados encontrado em $DATABASE_URL"
else
  echo "Criando um novo banco de dados em $DATABASE_URL"
  touch "$DATABASE_URL"
  chmod 666 "$DATABASE_URL"
  echo "Banco de dados criado com permissões 666"
fi

# Executar script para criar as tabelas necessárias
echo "Executando script para garantir que as tabelas existam..."
python -c "
from servidor import ensure_tables_exist
print('Inicializando tabelas...')
resultado = ensure_tables_exist()
if resultado:
    print('Tabelas inicializadas com sucesso!')
else:
    print('ERRO ao inicializar tabelas! Verifique os logs.')
"

# Exibir informações para debug
echo "Listando arquivos no diretório do banco de dados:"
ls -la /tmp/sqlite/

echo "Verificando permissões do banco de dados:"
ls -la $DATABASE_URL

# Inicia o servidor com gunicorn
echo "Iniciando servidor gunicorn..."
gunicorn servidor:app --bind 0.0.0.0:$PORT 