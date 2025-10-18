#!/usr/bin/env python3
"""
Executa o spider diretamente sem usar o comando scrapy
"""

import scrapy
import json
import os
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class BorrachariaSaoPauloSpider(scrapy.Spider):
    name = 'borracharia_sp_direto'
    
    # Configuração de grid - São Paulo (área menor para teste)
    GRID_SIZE_KM = 10  # Células maiores para teste
    LAT_MIN, LAT_MAX = -23.7, -23.4  # Região metropolitana de SP
    LON_MIN, LON_MAX = -46.8, -46.4
    
    SEARCH_TERMS = ["borracharia"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.establishments_found = 0
        self.cells_processed = 0
        
        # Criar diretório de saída
        os.makedirs('output', exist_ok=True)
        
        print("🚀 SPIDER BORRACHARIA SP INICIADO")
        print(f"📍 Área: {self.LAT_MIN} a {self.LAT_MAX}, {self.LON_MIN} a {self.LON_MAX}")
    
    def start_requests(self):
        """Gera requisições para o grid"""
        print("📊 Gerando grid de células...")
        
        # Calcula grid
        lat_step = self.GRID_SIZE_KM / 111.0  # 1° lat ≈ 111km
        lon_step = self.GRID_SIZE_KM / (111.0 * 0.85)  # Ajuste para longitude
        
        cells = []
        lat = self.LAT_MIN
        while lat <= self.LAT_MAX:
            lon = self.LON_MIN
            while lon <= self.LON_MAX:
                cells.append((lat, lon))
                lon += lon_step
            lat += lat_step
        
        print(f"📊 Total de células: {len(cells)}")
        
        # Gera requisições para as primeiras 3 células
        for i, (lat, lon) in enumerate(cells[:3]):
            for term in self.SEARCH_TERMS:
                url = f"https://www.google.com/search?q={term}+{lat},{lon}"
                
                print(f"🔍 Célula {i+1}: {lat:.4f}, {lon:.4f} - {term}")
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_cell,
                    meta={
                        'cell_index': i,
                        'cell_lat': lat,
                        'cell_lon': lon,
                        'search_term': term,
                    },
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    }
                )

    def parse_cell(self, response):
        """Parse de uma célula"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        print(f"✅ Processando célula {cell_index}: {response.status}")
        
        # Extrair informações básicas
        title = response.css('title::text').get()
        
        # Procurar por links relacionados a borracharias
        links = response.css('a[href*="borracharia"], a[href*="pneu"]')
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'cell_index': cell_index,
            'cell_lat': cell_lat,
            'cell_lon': cell_lon,
            'search_term': search_term,
            'url': response.url,
            'status': response.status,
            'title': title,
            'links_found': len(links),
            'links': [link.attrib.get('href', '') for link in links[:5]]  # Primeiros 5 links
        }
        
        # Salvar resultado
        filename = f'output/cell_{cell_index}_{search_term}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self.cells_processed += 1
        print(f"📄 Célula {cell_index} processada: {len(links)} links encontrados")
        
        return result

if __name__ == '__main__':
    print("🚀 INICIANDO SCRAPER DE BORRACHARIAS - SÃO PAULO")
    print("=" * 60)
    
    # Configurações mínimas
    settings = {
        'BOT_NAME': 'borracharia_sp',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'COOKIES_ENABLED': False,
        'TELNETCONSOLE_ENABLED': False,
        'LOG_LEVEL': 'INFO',
    }
    
    # Inicializar processo
    process = CrawlerProcess(settings)
    process.crawl(BorrachariaSaoPauloSpider)
    
    try:
        print("🔄 Iniciando processo...")
        process.start()
        print("✅ Processo concluído!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
