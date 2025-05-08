# Sistema de Gerenciamento de Igrejas - Servidor

Este é o servidor Flask para o Sistema de Gerenciamento de Igrejas. Ele fornece uma API REST para acesso aos dados de igrejas armazenados em um banco de dados SQLite.

## Arquivos Principais

- `servidor.py`: Servidor Flask principal que fornece a API REST
- `sincronizar_banco.py`: Script para sincronizar o banco de dados local com o servidor Render
- `create_churches_table.py`: Script para criar a tabela `churches` no banco de dados local
- `visualizar-igrejas.html`: Interface para visualizar os dados das igrejas
- `test-api.html` e `test-api.js`: Ferramentas para testar a conexão com a API
- `cross-origin.html`: Ferramenta para testar diferentes soluções de CORS
- `config.js`: Configurações centralizadas do sistema
- `database-service.js`: Serviço para interagir com o banco de dados

## Configuração Inicial

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure o banco de dados local:
   ```
   python create_churches_table.py
   ```

3. Inicie o servidor:
   ```
   python servidor.py
   ```

## Resolução de Problemas CORS

Este projeto implementa várias soluções para lidar com problemas de CORS (Cross-Origin Resource Sharing) que podem ocorrer ao acessar a API do servidor a partir de um navegador.

### Soluções Implementadas no Servidor

1. **Configuração CORS no Flask**:
   - Utiliza Flask-CORS para permitir acesso de qualquer origem
   - Configura cabeçalhos CORS adequados para todas as respostas
   - Implementa rota OPTIONS para lidar com solicitações preflight

2. **Cabeçalhos CORS Personalizados**:
   - Access-Control-Allow-Origin: *
   - Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
   - Access-Control-Allow-Headers: Content-Type, Authorization, Accept, Origin, X-Requested-With
   - Access-Control-Allow-Credentials: true

### Soluções Implementadas no Cliente

1. **Uso de Proxies CORS**:
   - AllOrigins: `https://api.allorigins.win/raw?url=URL_DA_API`
   - corsproxy.io: `https://corsproxy.io/?URL_DA_API`
   - CORS Anywhere: `https://cors-anywhere.herokuapp.com/URL_DA_API`

2. **Estratégia de Fallback**:
   - Tentativa de conexão direta primeiro
   - Uso de proxy CORS em caso de falha da conexão direta
   - Cache local como último recurso

3. **Sistema de Cache**:
   - Armazena dados em localStorage
   - Utiliza cache de memória para acesso rápido
   - Registro de timestamp para controle de validade de cache

## Ferramentas de Diagnóstico

- `test-api.html`: Teste básico de API com suporte a CORS
- `cross-origin.html`: Teste abrangente de diferentes proxies CORS
- `deploy_render.py`: Utilitário para diagnóstico e configuração do servidor Render

## Sincronização de Banco de Dados

O sistema inclui um mecanismo de sincronização entre o banco de dados local (SQLite) e o servidor no Render, permitindo que o sistema funcione mesmo offline.

Para iniciar a sincronização automaticamente com o Windows:
1. Edite o arquivo `iniciar_sincronizacao.bat` se necessário
2. Crie um atalho para este arquivo na pasta de inicialização do Windows

## Proxies CORS Recomendados

Testes realizados indicam que os seguintes proxies CORS funcionam melhor com este sistema:

1. **AllOrigins** - Funciona bem na maioria dos casos
   - `https://api.allorigins.win/raw?url=URL_ENCODED`
   - Limitações: Pode ter limite de taxa

2. **corsproxy.io** - Alternativa confiável
   - `https://corsproxy.io/?URL_ENCODED`
   - Limitações: Algumas vezes mais lento

3. **Conexão Direta** - Recomendada quando possível
   - Para o servidor local não há problemas de CORS

## Solução de Problemas

Se você enfrentar problemas de CORS:

1. Verifique se o servidor está online usando a ferramenta `test-api.html`
2. Teste diferentes proxies CORS usando `cross-origin.html`
3. Verifique se a tabela `churches` existe no banco de dados remoto usando `deploy_render.py`
4. Limpe o cache do navegador e tente novamente

Para problemas de sincronização:
1. Verifique se o serviço `sincronizar_banco.py` está em execução
2. Verifique as permissões de arquivo para o banco de dados local
3. Verifique se os diretórios necessários existem 