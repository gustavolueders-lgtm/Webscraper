# Configurações stealth para contornar bloqueio do Google Maps

BOT_NAME = 'business_scraper'

SPIDER_MODULES = ['business_scraper.spiders']
NEWSPIDER_MODULE = 'business_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configurações anti-detecção (VPN ativa)
CONCURRENT_REQUESTS = 1  # UMA requisição por vez - OBRIGATÓRIO
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 12  # 12 segundos base
RANDOMIZE_DOWNLOAD_DELAY = 8  # Varia 4-20 segundos

# AutoThrottle mais agressivo
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 10
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
AUTOTHROTTLE_DEBUG = True

# Cookies habilitados para sessões
COOKIES_ENABLED = True

# Headers realistas
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}

# Middlewares
SPIDER_MIDDLEWARES = {
    'business_scraper.middlewares.UserAgentRotationMiddleware': 400,
}

# Pipelines
ITEM_PIPELINES = {
    'business_scraper.pipelines.JsonWriterPipeline': 300,
}

# Playwright configurações stealth
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = 'chromium'
PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,  # Pode mudar para False se necessário
    'timeout': 60000,
    'args': [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-features=TranslateUI',
        '--disable-ipc-flooding-protection',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
    ]
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000

# Retry mais agressivo
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403, 400]

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'output/scrapy.log'

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Twisted reactor
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Cache desabilitado
HTTPCACHE_ENABLED = False

# Telnet desabilitado
TELNETCONSOLE_ENABLED = False
