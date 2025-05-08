// Serviço para interagir com o banco de dados SQLite no servidor Render
class DatabaseService {
    constructor() {
        // Usar configuração do config.js se disponível
        if (typeof CONFIG !== 'undefined') {
            this.serverUrl = CONFIG.RENDER_URL;
            this.config = CONFIG;
            console.log(`DatabaseService inicializado com configuração centralizada: ${this.serverUrl}`);
        } else {
            this.serverUrl = 'https://server-qx03.onrender.com';
            console.log(`DatabaseService inicializado com URL padrão: ${this.serverUrl}`);

            // Configuração interna caso config.js não esteja disponível
            this.config = {
                PROXIES: {
                    ALLORIGINS: {
                        buildUrl: function (url) {
                            return `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
                        }
                    },
                    CORSPROXY_IO: {
                        buildUrl: function (url) {
                            return `https://corsproxy.io/?${encodeURIComponent(url)}`;
                        }
                    }
                },
                CACHE: {
                    KEYS: {
                        CHURCHES_DATA: 'churchesData',
                        LAST_SYNC: 'lastSync'
                    }
                }
            };
        }

        this.localCache = new Map();
        this.initLocalStorage();
    }

    // Inicializa armazenamento local
    initLocalStorage() {
        try {
            const cacheKey = this.config?.CACHE?.KEYS?.CHURCHES_DATA || 'churchesData';

            // Verificar dados em cache
            if (localStorage.getItem(cacheKey)) {
                console.log('Dados encontrados no localStorage');
            } else {
                console.log('Nenhum dado encontrado no localStorage');
                localStorage.setItem(cacheKey, JSON.stringify({}));
            }
        } catch (error) {
            console.error('Erro ao inicializar localStorage:', error);
        }
    }

    // Busca todas as igrejas do servidor
    async fetchChurches() {
        try {
            // Se config.js estiver disponível, usar getWithFallback
            if (this.config && this.config.getWithFallback) {
                console.log('Usando método getWithFallback para buscar igrejas');
                const data = await this.config.getWithFallback('/churches');
                console.log(`Igrejas carregadas: ${Object.keys(data).length}`);

                // Armazenar no cache local
                this.cacheChurchesData(data);
                return data;
            }

            // Método tradicional com fallbacks manuais
            return await this._fetchChurchesWithFallback();
        } catch (error) {
            console.error('Erro final ao buscar igrejas:', error);

            // Em caso de falha, tentar obter do cache
            const cachedData = this.getChurchesFromCache();
            if (cachedData && Object.keys(cachedData).length > 0) {
                console.log('Usando dados em cache devido a erro de conexão');
                return cachedData;
            }

            throw error;
        }
    }

    // Método privado para buscar igrejas com fallbacks
    async _fetchChurchesWithFallback() {
        const timestamp = Date.now();
        const endpoint = `/churches?t=${timestamp}`;

        // 1. Tentar conexão direta
        try {
            console.log(`Tentando conexão direta com ${this.serverUrl}${endpoint}`);
            const response = await fetch(`${this.serverUrl}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log(`Igrejas carregadas via conexão direta: ${Object.keys(data).length}`);
                this.cacheChurchesData(data);
                return data;
            } else {
                console.warn(`Conexão direta falhou com status ${response.status}`);
            }
        } catch (error) {
            console.warn('Conexão direta falhou:', error);
        }

        // 2. Tentar via AllOrigins
        try {
            const proxyUrl = this.config.PROXIES.ALLORIGINS.buildUrl(`${this.serverUrl}${endpoint}`);
            console.log(`Tentando via AllOrigins: ${proxyUrl}`);

            const response = await fetch(proxyUrl);
            if (response.ok) {
                const data = await response.json();
                console.log(`Igrejas carregadas via AllOrigins: ${Object.keys(data).length}`);
                this.cacheChurchesData(data);
                return data;
            } else {
                console.warn(`AllOrigins falhou com status ${response.status}`);
            }
        } catch (error) {
            console.warn('AllOrigins falhou:', error);
        }

        // 3. Tentar via corsproxy.io
        try {
            const proxyUrl = this.config.PROXIES.CORSPROXY_IO.buildUrl(`${this.serverUrl}${endpoint}`);
            console.log(`Tentando via corsproxy.io: ${proxyUrl}`);

            const response = await fetch(proxyUrl);
            if (response.ok) {
                const data = await response.json();
                console.log(`Igrejas carregadas via corsproxy.io: ${Object.keys(data).length}`);
                this.cacheChurchesData(data);
                return data;
            } else {
                console.warn(`corsproxy.io falhou com status ${response.status}`);
            }
        } catch (error) {
            console.warn('corsproxy.io falhou:', error);
        }

        // 4. Verificar cache como último recurso
        const cachedData = this.getChurchesFromCache();
        if (cachedData && Object.keys(cachedData).length > 0) {
            console.log('Todos os métodos falharam, usando dados em cache');
            return cachedData;
        }

        // Se chegou aqui, todos os métodos falharam
        throw new Error('Não foi possível conectar ao servidor por nenhum método');
    }

    // Busca uma igreja específica
    async fetchChurch(churchId) {
        try {
            // Tentar obter do cache primeiro
            const cachedChurch = this.getChurchFromCache(churchId);
            if (cachedChurch) {
                console.log(`Igreja ${churchId} encontrada no cache`);
                return { [churchId]: cachedChurch };
            }

            const timestamp = Date.now();
            const response = await fetch(`${this.serverUrl}/churches/${churchId}?t=${timestamp}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            if (!response.ok) {
                throw new Error(`Erro ao buscar igreja ${churchId}: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`Igreja ${churchId} carregada do servidor`);

            // Atualizar igreja no cache
            if (data[churchId]) {
                this.updateChurchInCache(churchId, data[churchId]);
            }

            return data;
        } catch (error) {
            console.error(`Erro ao buscar igreja ${churchId}:`, error);

            // Se falhar, tentar via proxy
            try {
                if (this.config && this.config.PROXIES) {
                    const proxyUrl = this.config.PROXIES.ALLORIGINS.buildUrl(
                        `${this.serverUrl}/churches/${churchId}?t=${Date.now()}`
                    );

                    const proxyResponse = await fetch(proxyUrl);
                    if (proxyResponse.ok) {
                        const data = await proxyResponse.json();
                        return data;
                    }
                }
            } catch (proxyError) {
                console.error(`Erro ao buscar igreja ${churchId} via proxy:`, proxyError);
            }

            throw error;
        }
    }

    // Armazena os dados das igrejas no cache
    cacheChurchesData(data) {
        try {
            // Armazenar no cache de memória
            this.localCache.clear();
            for (const [id, church] of Object.entries(data)) {
                this.localCache.set(id, church);
            }

            // Armazenar no localStorage
            const cacheKey = this.config?.CACHE?.KEYS?.CHURCHES_DATA || 'churchesData';
            localStorage.setItem(cacheKey, JSON.stringify(data));

            // Armazenar timestamp da última sincronização
            const lastSyncKey = this.config?.CACHE?.KEYS?.LAST_SYNC || 'lastSync';
            localStorage.setItem(lastSyncKey, Date.now().toString());

            console.log(`${Object.keys(data).length} igrejas armazenadas no cache`);
        } catch (error) {
            console.error('Erro ao armazenar dados no cache:', error);
        }
    }

    // Atualiza uma igreja específica no cache
    updateChurchInCache(churchId, churchData) {
        try {
            // Atualizar no cache de memória
            this.localCache.set(churchId, churchData);

            // Atualizar no localStorage
            const cacheKey = this.config?.CACHE?.KEYS?.CHURCHES_DATA || 'churchesData';
            const cachedData = JSON.parse(localStorage.getItem(cacheKey) || '{}');
            cachedData[churchId] = churchData;
            localStorage.setItem(cacheKey, JSON.stringify(cachedData));
            console.log(`Igreja ${churchId} atualizada no cache`);
        } catch (error) {
            console.error(`Erro ao atualizar igreja ${churchId} no cache:`, error);
        }
    }

    // Obtém todas as igrejas do cache
    getChurchesFromCache() {
        try {
            // Tentar primeiro o cache de memória
            if (this.localCache.size > 0) {
                console.log(`Obtendo ${this.localCache.size} igrejas do cache de memória`);
                const result = {};
                for (const [id, church] of this.localCache.entries()) {
                    result[id] = church;
                }
                return result;
            }

            // Cair para o localStorage
            const cacheKey = this.config?.CACHE?.KEYS?.CHURCHES_DATA || 'churchesData';
            const cachedData = JSON.parse(localStorage.getItem(cacheKey) || '{}');
            console.log(`Obtendo ${Object.keys(cachedData).length} igrejas do localStorage`);
            return cachedData;
        } catch (error) {
            console.error('Erro ao obter igrejas do cache:', error);
            return {};
        }
    }

    // Obtém uma igreja específica do cache
    getChurchFromCache(churchId) {
        try {
            // Tentar primeiro o cache de memória
            if (this.localCache.has(churchId)) {
                return this.localCache.get(churchId);
            }

            // Cair para o localStorage
            const cacheKey = this.config?.CACHE?.KEYS?.CHURCHES_DATA || 'churchesData';
            const cachedData = JSON.parse(localStorage.getItem(cacheKey) || '{}');
            return cachedData[churchId];
        } catch (error) {
            console.error(`Erro ao obter igreja ${churchId} do cache:`, error);
            return null;
        }
    }

    // Verifica se o servidor está online
    async checkServerStatus() {
        try {
            const timestamp = Date.now();

            // Tentar conexão direta
            try {
                const response = await fetch(`${this.serverUrl}/ping?t=${timestamp}`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    return {
                        online: true,
                        status: response.status,
                        message: data.message || 'Servidor ativo',
                        method: 'direct'
                    };
                }
            } catch (directError) {
                console.warn('Verificação direta falhou:', directError);
            }

            // Tentar via proxy
            if (this.config && this.config.PROXIES) {
                try {
                    const proxyUrl = this.config.PROXIES.ALLORIGINS.buildUrl(
                        `${this.serverUrl}/ping?t=${timestamp}`
                    );

                    const proxyResponse = await fetch(proxyUrl);
                    if (proxyResponse.ok) {
                        const data = await proxyResponse.json();
                        return {
                            online: true,
                            status: proxyResponse.status,
                            message: data.message || 'Servidor ativo (via proxy)',
                            method: 'proxy'
                        };
                    }
                } catch (proxyError) {
                    console.warn('Verificação via proxy falhou:', proxyError);
                }
            }

            // Se todas as tentativas falharem
            return {
                online: false,
                status: 0,
                message: 'Não foi possível conectar ao servidor',
                method: 'all_failed'
            };
        } catch (error) {
            return {
                online: false,
                status: 0,
                message: error.message || 'Erro de conexão com o servidor',
                method: 'error'
            };
        }
    }

    // Lista todas as tabelas disponíveis no servidor
    async listTables() {
        try {
            const timestamp = Date.now();

            // Tentar conexão direta
            try {
                const response = await fetch(`${this.serverUrl}/tabelas?t=${timestamp}`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    return data.tabelas || [];
                }
            } catch (directError) {
                console.warn('Listagem direta de tabelas falhou:', directError);
            }

            // Tentar via proxy
            if (this.config && this.config.PROXIES) {
                try {
                    const proxyUrl = this.config.PROXIES.ALLORIGINS.buildUrl(
                        `${this.serverUrl}/tabelas?t=${timestamp}`
                    );

                    const proxyResponse = await fetch(proxyUrl);
                    if (proxyResponse.ok) {
                        const data = await proxyResponse.json();
                        return data.tabelas || [];
                    }
                } catch (proxyError) {
                    console.warn('Listagem de tabelas via proxy falhou:', proxyError);
                }
            }

            throw new Error('Não foi possível listar tabelas');
        } catch (error) {
            console.error('Erro ao listar tabelas:', error);
            throw error;
        }
    }
}

// Exportar instância do serviço
const dbService = new DatabaseService(); 