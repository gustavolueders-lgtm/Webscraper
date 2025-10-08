# Configurações conservadoras para evitar bloqueio do Google Maps

# Scrapy settings for business_scraper project
BOT_NAME = 'business_scraper'

SPIDER_MODULES = ['business_scraper.spiders']
NEWSPIDER_MODULE = 'business_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure delays and concurrency (MUITO CONSERVADOR)
CONCURRENT_REQUESTS = 1  # Apenas 1 requisição simultânea
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 15  # 15 segundos entre requisições
RANDOMIZE_DOWNLOAD_DELAY = 10  # Varia entre 5-25 segundos

# AutoThrottle (ajuste automático)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 15
AUTOTHROTTLE_MAX_DELAY = 60  # Até 1 minuto entre requisições
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
AUTOTHROTTLE_DEBUG = True

# Disable cookies
COOKIES_ENABLED = False

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# User Agent rotation
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# Enable and configure the AutoThrottle extension
SPIDER_MIDDLEWARES = {
    'business_scraper.middlewares.UserAgentRotationMiddleware': 400,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'business_scraper.pipelines.JsonWriterPipeline': 300,
}

# Playwright settings (CONSERVADOR)
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = 'chromium'
PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,
    'timeout': 120000,  # 2 minutos timeout
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 120000  # 2 minutos

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403]

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'output/scrapy.log'

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Twisted reactor
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
