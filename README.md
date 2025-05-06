# Servidor SQLite API

API REST criada para substituir o Firebase Realtime Database, utilizando SQLite.

## Arquivos incluídos

- `servidor.py`: Aplicação Flask que serve a API
- `requirements.txt`: Dependências do projeto
- `start.sh`: Script de inicialização para o Render
- `migrar_firebase.py`: Script para migrar dados do Firebase para SQLite

## Deploy no Render

1. Crie uma conta no [Render](https://render.com)

2. Faça upload do banco SQLite como Secret
   - No Dashboard do Render, vá para "Secrets"
   - Adicione um novo Secret chamado `meu_banco.db`
   - Faça upload do arquivo `meu_banco.db`

3. Crie um novo Web Service
   - Selecione "New Web Service"
   - Conecte seu repositório GitHub ou faça upload dos arquivos
   - Configure as seguintes opções:
     - **Environment**: Web Service
     - **Build Command**: `chmod +x ./start.sh`
     - **Start Command**: `./start.sh`
     - **Runtime Environment**: Python 3

4. Configure o Secret
   - Nas configurações do Web Service, vá para "Environment"
   - Adicione o Secret `meu_banco.db` em "Secret Files"
   - Configure o Path como `/etc/secrets/meu_banco.db`

5. Deploy
   - Clique em "Create Web Service"

## Rotas da API

- `GET /`: Verifica se a API está funcionando
- `GET /tabelas`: Lista todas as tabelas no banco de dados
- `GET /<tabela>`: Retorna todos os registros de uma tabela
- `GET /<tabela>/<id>`: Retorna um registro específico
- `PUT /<tabela>/<id>`: Cria ou atualiza um registro
- `DELETE /<tabela>/<id>`: Remove um registro

## Testando localmente

```bash
export PORT=5000
flask run
``` 