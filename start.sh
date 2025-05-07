#!/bin/bash
# Script de inicialização para o Render

# Instala todas as dependências
pip install -r requirements.txt

# Configuração da variável de ambiente para o banco de dados
export DATABASE_URL="C:\\sqlite\\meu_banco.db"

# Certifique-se que o banco de dados está na pasta correta
if [ -f "C:/sqlite/meu_banco.db" ]; then
  echo "Banco de dados encontrado em C:/sqlite/meu_banco.db"
else
  echo "AVISO: Banco de dados não encontrado em C:/sqlite/meu_banco.db"
  # Tenta copiar se estiver em /etc/secrets (para ambiente Render)
  if [ -f "/etc/secrets/meu_banco.db" ]; then
    mkdir -p C:/sqlite/
    cp /etc/secrets/meu_banco.db C:/sqlite/
    echo "Banco de dados copiado para C:/sqlite/meu_banco.db"
  fi
fi

# Inicia o servidor com gunicorn
gunicorn servidor:app --bind 0.0.0.0:$PORT 