#!/usr/bin/env python3
"""
Spider de teste para borracharias com Playwright
"""

import scrapy
from scrapy_playwright.page import PageMethod

class TesteBorrachariaSpider(scrapy.Spider):
    name = 'teste_borracharia'
    
    def start_requests(self):
        """Teste com uma única coordenada de São Paulo"""
        self.logger.info("🚀 TESTE BORRACHARIA SPIDER INICIADO")
        
        # Coordenada do centro de São Paulo
        lat, lon = -23.5505, -46.6333
        url = f"https://www.google.com/maps/search/borracharia/@{lat},{lon},15z"
        
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_timeout', 3000),
                    PageMethod('wait_for_selector', 'div[role="feed"]', timeout=10000),
                ],
            }
        )
    
    def parse(self, response):
        """Parse simples para testar"""
        self.logger.info(f"✅ Resposta recebida: {response.status}")
        self.logger.info(f"📄 URL: {response.url}")
        
        # Tentar extrair alguns resultados
        results = response.css('div[role="feed"] div[data-result-index]')
        self.logger.info(f"🔍 Encontrados {len(results)} resultados")
        
        for i, result in enumerate(results[:5]):  # Apenas os primeiros 5
            name = result.css('div[class*="fontHeadlineSmall"] span::text').get()
            if name:
                self.logger.info(f"🔧 Borracharia {i+1}: {name}")
                yield {
                    'name': name,
                    'index': i+1
                }
        
        return {'total_results': len(results)}
