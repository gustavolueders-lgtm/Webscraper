#!/usr/bin/env python3
"""
Spider de teste muito simples para diagnosticar problemas
"""

import scrapy
import json
import os
from datetime import datetime

class TesteSpider(scrapy.Spider):
    name = 'teste_simples'
    
    def start_requests(self):
        print("🚀 SPIDER TESTE SIMPLES INICIADO")
        self.logger.info("🚀 SPIDER TESTE SIMPLES INICIADO")
        
        # Teste com Google Search simples
        yield scrapy.Request(
            url='https://www.google.com/search?q=borracharia+sao+paulo',
            callback=self.parse,
            dont_filter=True
        )
    
    def parse(self, response):
        print(f"✅ Resposta recebida: {response.status}")
        self.logger.info(f"✅ Resposta recebida: {response.status}")
        
        # Salvar resultado simples
        result = {
            'timestamp': datetime.now().isoformat(),
            'url': response.url,
            'status': response.status,
            'title': response.css('title::text').get(),
            'test': 'success'
        }
        
        # Salvar em arquivo
        os.makedirs('output', exist_ok=True)
        with open('output/teste_simples.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Título: {result['title']}")
        print("✅ Teste concluído com sucesso!")
        
        return result
