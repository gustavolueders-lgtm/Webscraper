#!/usr/bin/env python3
"""
Teste simples do spider para verificar se está funcionando
"""

import scrapy
from scrapy.crawler import CrawlerProcess

class TesteSpider(scrapy.Spider):
    name = 'teste'
    
    def start_requests(self):
        print("🚀 SPIDER TESTE INICIADO")
        yield scrapy.Request(
            url='https://www.google.com/search?q=borracharia+sao+paulo',
            callback=self.parse
        )
    
    def parse(self, response):
        print(f"✅ Resposta recebida: {response.status}")
        print(f"📄 Título: {response.css('title::text').get()}")
        return {'status': 'ok', 'title': response.css('title::text').get()}

if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'CONCURRENT_REQUESTS': 1,
    })
    
    process.crawl(TesteSpider)
    process.start()
