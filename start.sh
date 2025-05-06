#!/bin/bash
# Script de inicialização para o Render

# Certifique-se que o banco de dados está na pasta correta
if [ -f "meu_banco.db" ]; then
  echo "Banco de dados já existe"
else
  echo "Copiando banco de dados..."
  if [ -f "/etc/secrets/meu_banco.db" ]; then
    cp /etc/secrets/meu_banco.db .
  else
    echo "AVISO: Banco de dados não encontrado em /etc/secrets/meu_banco.db"
  fi
fi

# Inicia o servidor com gunicorn usando o caminho completo
python -m pip install gunicorn
python -m gunicorn --bind 0.0.0.0:$PORT servidor:app 