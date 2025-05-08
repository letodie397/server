/**
 * Configuração centralizada para acessar a API
 */

// Configuração do servidor
const CONFIG = {
    // URL do servidor Render
    RENDER_URL: 'https://server-qx03.onrender.com',

    // URL do servidor local
    LOCAL_URL: 'http://localhost:5000',

    // Proxies CORS para contornar restrições
    PROXIES: {
        // AllOrigins - geralmente o mais confiável
        ALLORIGINS: {
            name: 'AllOrigins',
            // Função para construir a URL com o proxy
            buildUrl: function (url) {
                return `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
            }
        },

        // corsproxy.io - alternativa para AllOrigins
        CORSPROXY_IO: {
            name: 'corsproxy.io',
            buildUrl: function (url) {
                return `https://corsproxy.io/?${encodeURIComponent(url)}`;
            }
        },

        // CORS Anywhere - exige verificação captcha, menos recomendado
        CORS_ANYWHERE: {
            name: 'CORS Anywhere',
            buildUrl: function (url) {
                return `https://cors-anywhere.herokuapp.com/${url}`;
            }
        }
    },

    // Opções para fetch com CORS
    FETCH_OPTIONS: {
        DEFAULT: {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            mode: 'cors',
            cache: 'no-store'
        },

        // Opções para fetch sem CORS (modo no-cors)
        NO_CORS: {
            method: 'GET',
            mode: 'no-cors',
            cache: 'no-store'
        }
    },

    // Tabelas do banco de dados
    TABLES: {
        CHURCHES: 'churches'
    },

    // Configurações para cache local
    CACHE: {
        // Chaves para localStorage
        KEYS: {
            CHURCHES_DATA: 'churchesData',
            LAST_SYNC: 'lastSync'
        },

        // Tempo de expiração do cache em milissegundos (1 hora)
        EXPIRATION: 60 * 60 * 1000
    }
};

// Função para obter URL atual (local ou render)
CONFIG.getCurrentServerUrl = function (useLocal = false) {
    return useLocal ? this.LOCAL_URL : this.RENDER_URL;
};

// Função para construir URL de API
CONFIG.buildApiUrl = function (endpoint, useLocal = false) {
    const baseUrl = this.getCurrentServerUrl(useLocal);
    const timestamp = Date.now();
    return `${baseUrl}${endpoint}?t=${timestamp}`;
};

// Função para tentar conexão usando vários métodos
CONFIG.getWithFallback = async function (endpoint, useLocal = false) {
    const apiUrl = this.buildApiUrl(endpoint, useLocal);

    // Tentar método direto primeiro
    try {
        const response = await fetch(apiUrl, this.FETCH_OPTIONS.DEFAULT);
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.warn('Direct fetch failed:', error);
    }

    // Tentar AllOrigins
    try {
        const proxyUrl = this.PROXIES.ALLORIGINS.buildUrl(apiUrl);
        const response = await fetch(proxyUrl, this.FETCH_OPTIONS.DEFAULT);
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.warn('AllOrigins fetch failed:', error);
    }

    // Tentar corsproxy.io
    try {
        const proxyUrl = this.PROXIES.CORSPROXY_IO.buildUrl(apiUrl);
        const response = await fetch(proxyUrl, this.FETCH_OPTIONS.DEFAULT);
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.warn('corsproxy.io fetch failed:', error);
    }

    // Se tudo falhar, tenta recuperar do cache local
    const cachedData = localStorage.getItem(this.CACHE.KEYS.CHURCHES_DATA);
    if (cachedData) {
        try {
            return JSON.parse(cachedData);
        } catch (e) {
            console.error('Error parsing cached data:', e);
        }
    }

    // Se tudo falhar, lança erro
    throw new Error('Não foi possível conectar com o servidor por nenhum método');
};

// Exportar configuração
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} 