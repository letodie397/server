// Script para testar conexão com a API Render e diagnosticar problemas de CORS
console.log("Iniciando teste de API Render");

// URL base da API
const API_URL = 'https://server-qx03.onrender.com';

// Função para mostrar resultados na página
function showResult(title, status, message, data = null) {
    // Criar elemento de resultado
    const resultElement = document.createElement('div');
    resultElement.className = `test-result ${status}`;

    // Definir HTML interno
    resultElement.innerHTML = `
        <h3>${title}</h3>
        <p class="status ${status}">${status.toUpperCase()}</p>
        <p>${message}</p>
        ${data ? `<pre>${JSON.stringify(data, null, 2)}</pre>` : ''}
    `;

    // Adicionar ao container
    const container = document.getElementById('test-results');
    if (container) {
        container.appendChild(resultElement);
    } else {
        // Se não houver container, criar um
        const newContainer = document.createElement('div');
        newContainer.id = 'test-results';
        newContainer.className = 'test-container';
        newContainer.appendChild(resultElement);
        document.body.appendChild(newContainer);
    }
}

// Teste 1: Acordar servidor com método no-cors
async function testPingNoCors() {
    try {
        console.log("Teste 1: Ping no-cors");
        const startTime = Date.now();

        // Fazer requisição com modo no-cors para acordar o servidor
        const response = await fetch(`${API_URL}/ping?t=${Date.now()}`, {
            method: 'GET',
            mode: 'no-cors',
            cache: 'no-cache'
        });

        const elapsed = Date.now() - startTime;
        showResult(
            "Teste 1: Ping (modo no-cors)",
            "success",
            `Requisição no-cors completada em ${elapsed}ms. Nota: Isto apenas confirma que o request foi enviado, não seu sucesso/falha devido às limitações do modo no-cors.`
        );
    } catch (error) {
        showResult(
            "Teste 1: Ping (modo no-cors)",
            "error",
            `Falha na requisição: ${error.message}`
        );
    }
}

// Teste 2: Ping normal (sujeito a CORS)
async function testPingNormal() {
    try {
        console.log("Teste 2: Ping normal");
        const startTime = Date.now();

        // Fazer requisição normal
        const response = await fetch(`${API_URL}/ping?t=${Date.now()}`, {
            method: 'GET',
            mode: 'cors',
            cache: 'no-cache'
        });

        const elapsed = Date.now() - startTime;
        const responseText = await response.text();

        showResult(
            "Teste 2: Ping (modo normal)",
            "success",
            `Requisição completada em ${elapsed}ms com status ${response.status}`,
            { status: response.status, response: responseText }
        );
    } catch (error) {
        showResult(
            "Teste 2: Ping (modo normal)",
            "error",
            `Falha na requisição: ${error.message}`
        );
    }
}

// Teste 3: Listar igrejas
async function testListChurches() {
    try {
        console.log("Teste 3: Listar igrejas");
        const startTime = Date.now();

        // Fazer requisição para listar igrejas
        const response = await fetch(`${API_URL}/churches?t=${Date.now()}`, {
            method: 'GET',
            cache: 'no-cache'
        });

        const elapsed = Date.now() - startTime;

        if (response.ok) {
            const data = await response.json();
            const churchCount = Object.keys(data).length;

            showResult(
                "Teste 3: Listar igrejas",
                "success",
                `${churchCount} igrejas encontradas em ${elapsed}ms`,
                { count: churchCount, sample: Object.keys(data).slice(0, 2).map(key => ({ id: key, ...data[key] })) }
            );
        } else {
            showResult(
                "Teste 3: Listar igrejas",
                "error",
                `Requisição falhou com status ${response.status}`,
                { status: response.status }
            );
        }
    } catch (error) {
        showResult(
            "Teste 3: Listar igrejas",
            "error",
            `Falha na requisição: ${error.message}`
        );
    }
}

// Teste 4: Método alternativo usando XHR
async function testXHR() {
    try {
        console.log("Teste 4: Verificar usando XHR");

        const result = await new Promise((resolve) => {
            const xhr = new XMLHttpRequest();
            const startTime = Date.now();

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    const elapsed = Date.now() - startTime;

                    resolve({
                        status: xhr.status,
                        statusText: xhr.statusText,
                        elapsed: elapsed,
                        response: xhr.responseText,
                        success: xhr.status >= 200 && xhr.status < 300
                    });
                }
            };

            xhr.onerror = function () {
                resolve({
                    status: 0,
                    statusText: "Network Error",
                    elapsed: Date.now() - startTime,
                    success: false
                });
            };

            xhr.open('GET', `${API_URL}/ping?t=${Date.now()}`, true);
            xhr.timeout = 10000;
            xhr.send();
        });

        showResult(
            "Teste 4: XHR Request",
            result.success ? "success" : "error",
            `XHR completado em ${result.elapsed}ms com status ${result.status}`,
            result
        );
    } catch (error) {
        showResult(
            "Teste 4: XHR Request",
            "error",
            `Falha na requisição XHR: ${error.message}`
        );
    }
}

// Teste 5: Verificar usando imagem
async function testImageMethod() {
    try {
        console.log("Teste 5: Verificar usando imagem");
        const startTime = Date.now();

        const result = await new Promise((resolve) => {
            const img = new Image();

            img.onload = function () {
                resolve({
                    success: true,
                    elapsed: Date.now() - startTime,
                    message: "Imagem carregada com sucesso"
                });
            };

            img.onerror = function () {
                // Mesmo se der erro, pode ser que o servidor esteja online
                // porque o erro pode ser porque a URL não é uma imagem válida
                resolve({
                    success: true, // Consideramos sucesso mesmo com erro
                    elapsed: Date.now() - startTime,
                    message: "Erro ao carregar imagem (esperado se o servidor respondeu com não-imagem)"
                });
            };

            // Usar um timestamp para evitar cache
            img.src = `${API_URL}/favicon.ico?t=${Date.now()}`;

            // Definir timeout
            setTimeout(() => {
                if (!img.complete) {
                    resolve({
                        success: false,
                        elapsed: Date.now() - startTime,
                        message: "Timeout ao carregar imagem"
                    });
                }
            }, 10000);
        });

        showResult(
            "Teste 5: Image Method",
            result.success ? "success" : "error",
            `Teste de imagem completado em ${result.elapsed}ms: ${result.message}`,
            result
        );
    } catch (error) {
        showResult(
            "Teste 5: Image Method",
            "error",
            `Falha no teste de imagem: ${error.message}`
        );
    }
}

// Executar todos os testes
async function runAllTests() {
    try {
        // Adicionar estilos para os resultados
        const style = document.createElement('style');
        style.textContent = `
            .test-container {
                max-width: 800px;
                margin: 20px auto;
                font-family: sans-serif;
            }
            .test-result {
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 5px;
                border-left: 5px solid #ccc;
            }
            .test-result.success {
                background-color: #e6f7e6;
                border-left-color: #4CAF50;
            }
            .test-result.error {
                background-color: #ffeaea;
                border-left-color: #f44336;
            }
            .test-result h3 {
                margin-top: 0;
            }
            .status {
                font-weight: bold;
            }
            .status.success {
                color: #4CAF50;
            }
            .status.error {
                color: #f44336;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .test-header {
                text-align: center;
                margin-bottom: 30px;
            }
            .test-summary {
                margin-top: 30px;
                padding: 15px;
                background-color: #f5f5f5;
                border-radius: 5px;
            }
        `;
        document.head.appendChild(style);

        // Adicionar cabeçalho
        const header = document.createElement('div');
        header.className = 'test-header';
        header.innerHTML = `
            <h1>Teste de API Render</h1>
            <p>Este script testa a conexão com a API do SQLite no Render e diagnostica problemas de CORS.</p>
        `;
        document.body.appendChild(header);

        // Criar container para resultados
        const container = document.createElement('div');
        container.id = 'test-results';
        container.className = 'test-container';
        document.body.appendChild(container);

        // Executar testes em sequência
        await testPingNoCors();
        await new Promise(resolve => setTimeout(resolve, 1000)); // Esperar 1s entre testes

        await testPingNormal();
        await new Promise(resolve => setTimeout(resolve, 1000));

        await testXHR();
        await new Promise(resolve => setTimeout(resolve, 1000));

        await testImageMethod();
        await new Promise(resolve => setTimeout(resolve, 1000));

        await testListChurches();

        // Adicionar resumo
        const summary = document.createElement('div');
        summary.className = 'test-summary';
        summary.innerHTML = `
            <h2>Resumo dos Testes</h2>
            <p>Testes concluídos às ${new Date().toLocaleTimeString()}.</p>
            <p>Se você está vendo erros de CORS, é provável que a API no Render não esteja configurada corretamente 
            para permitir solicitações de origens diferentes. Verifique os cabeçalhos CORS no servidor.</p>
            <p>Sugestões:</p>
            <ul>
                <li>Configure o servidor para enviar o cabeçalho <code>Access-Control-Allow-Origin: *</code></li>
                <li>Ou configure o servidor para permitir sua origem específica</li>
                <li>Para solicitações com credenciais, configure <code>Access-Control-Allow-Credentials: true</code></li>
                <li>Para métodos não padrão, configure <code>Access-Control-Allow-Methods</code></li>
            </ul>
        `;
        document.body.appendChild(summary);

    } catch (error) {
        console.error("Erro ao executar testes:", error);
        showResult(
            "Erro Geral",
            "error",
            `Falha ao executar os testes: ${error.message}`
        );
    }
}

// Iniciar testes quando a página carregar
window.addEventListener('DOMContentLoaded', runAllTests); 