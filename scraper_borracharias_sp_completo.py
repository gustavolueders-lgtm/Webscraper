#!/usr/bin/env python3
"""
Scraper completo de borracharias para São Paulo
"""

import scrapy
import json
import os
import re
import random
import time
from datetime import datetime
from scrapy.crawler import CrawlerProcess

class BorrachariaSaoPauloCompleto(scrapy.Spider):
    name = 'borracharia_sp_completo'
    
    # Configuração de grid - São Paulo COMPLETO
    GRID_SIZE_KM = 5
    LAT_MIN, LAT_MAX = -25.3, -19.8  # São Paulo completo
    LON_MIN, LON_MAX = -53.1, -44.2
    
    SEARCH_TERMS = ["borracharia", "pneus", "auto center"]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    def __init__(self, start_cell=None, max_cells=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.start_cell = int(start_cell) if start_cell else 0
        self.max_cells = int(max_cells) if max_cells else 50  # Limite para teste
        self.establishments_found = 0
        self.cells_processed = 0
        self.seen_establishments = set()
        
        # Criar diretórios
        os.makedirs('output', exist_ok=True)
        os.makedirs('output/cells', exist_ok=True)
        
        print(f"SCRAPER BORRACHARIAS SP COMPLETO INICIADO")
        print(f"Comecando da celula: {self.start_cell}")
        print(f"Maximo de celulas: {self.max_cells}")
    
    def start_requests(self):
        """Gera requisições para o grid"""
        print("Calculando grid de Sao Paulo...")

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
        
        total_cells = len(cells)
        end_cell = min(self.start_cell + self.max_cells, total_cells)
        
        print(f"Total de celulas em SP: {total_cells}")
        print(f"Processando celulas {self.start_cell} a {end_cell-1}")
        
        # Salvar informações do grid
        grid_info = {
            'timestamp': datetime.now().isoformat(),
            'total_cells': total_cells,
            'start_cell': self.start_cell,
            'end_cell': end_cell,
            'max_cells': self.max_cells,
            'grid_config': {
                'lat_min': self.LAT_MIN,
                'lat_max': self.LAT_MAX,
                'lon_min': self.LON_MIN,
                'lon_max': self.LON_MAX,
                'grid_size_km': self.GRID_SIZE_KM
            }
        }
        
        with open('output/grid_info.json', 'w', encoding='utf-8') as f:
            json.dump(grid_info, f, ensure_ascii=False, indent=2)
        
        # Gera requisições
        for i, (lat, lon) in enumerate(cells[self.start_cell:end_cell], start=self.start_cell):
            for term in self.SEARCH_TERMS:
                # Usar Google Maps em vez de Google Search
                url = f"https://www.google.com/maps/search/{term}/@{lat},{lon},15z"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_maps,
                    meta={
                        'cell_index': i,
                        'cell_lat': lat,
                        'cell_lon': lon,
                        'search_term': term,
                    },
                    headers={
                        'User-Agent': random.choice(self.USER_AGENTS),
                        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                    },
                    dont_filter=True
                )
                
                # Pausa entre requisições
                time.sleep(random.uniform(1, 3))

    def parse_maps(self, response):
        """Parse do Google Maps"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        print(f"Celula {cell_index} ({search_term}): {cell_lat:.4f}, {cell_lon:.4f}")
        
        establishments = []
        
        # Extrair estabelecimentos do Google Maps
        # Tentar diferentes seletores
        selectors = [
            'div[data-result-index]',
            'div[role="article"]',
            'div[class*="result"]',
            'a[data-cid]'
        ]
        
        for selector in selectors:
            results = response.css(selector)
            if results:
                print(f"Encontrados {len(results)} resultados com seletor: {selector}")
                break

        if not results:
            # Fallback: procurar por texto que contenha palavras-chave
            text_content = response.text
            borracharia_mentions = len(re.findall(r'borracharia|pneu|auto center', text_content, re.IGNORECASE))
            print(f"Mencoes encontradas no texto: {borracharia_mentions}")
        
        # Processar resultados encontrados
        for i, result in enumerate(results[:20]):  # Máximo 20 por célula
            try:
                # Tentar extrair informações básicas
                name_selectors = [
                    'div[class*="fontHeadlineSmall"] span::text',
                    'h3::text',
                    'div[class*="title"]::text',
                    'span[class*="name"]::text'
                ]
                
                name = None
                for name_sel in name_selectors:
                    name = result.css(name_sel).get()
                    if name:
                        break
                
                if not name:
                    name = f"Estabelecimento_{cell_index}_{i}"
                
                # Criar chave única
                establishment_key = f"{name}_{cell_lat:.4f}_{cell_lon:.4f}"
                
                if establishment_key not in self.seen_establishments:
                    self.seen_establishments.add(establishment_key)
                    
                    establishment = {
                        'name': name.strip() if name else f"Estabelecimento_{i}",
                        'cell_index': cell_index,
                        'cell_lat': cell_lat,
                        'cell_lon': cell_lon,
                        'search_term': search_term,
                        'found_at': datetime.now().isoformat(),
                        'source_url': response.url,
                        'establishment_index': i
                    }
                    
                    establishments.append(establishment)
                    self.establishments_found += 1
            
            except Exception as e:
                print(f"Erro ao processar resultado {i}: {e}")
        
        # Salvar resultados da célula
        cell_result = {
            'timestamp': datetime.now().isoformat(),
            'cell_index': cell_index,
            'cell_lat': cell_lat,
            'cell_lon': cell_lon,
            'search_term': search_term,
            'url': response.url,
            'status': response.status,
            'establishments_found': len(establishments),
            'establishments': establishments
        }
        
        # Salvar arquivo da célula
        filename = f'output/cells/cell_{cell_index}_{search_term}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cell_result, f, ensure_ascii=False, indent=2)
        
        self.cells_processed += 1
        
        print(f"Celula {cell_index} processada: {len(establishments)} estabelecimentos")
        print(f"Total encontrado ate agora: {self.establishments_found}")
        
        # Salvar progresso geral
        self.save_progress()
        
        return cell_result
    
    def save_progress(self):
        """Salva progresso geral"""
        progress = {
            'timestamp': datetime.now().isoformat(),
            'cells_processed': self.cells_processed,
            'establishments_found': self.establishments_found,
            'start_cell': self.start_cell,
            'max_cells': self.max_cells
        }
        
        with open('output/progress.json', 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    import sys

    print("INICIANDO SCRAPER COMPLETO DE BORRACHARIAS - SAO PAULO")
    print("=" * 70)
    
    # Parâmetros da linha de comando
    start_cell = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    max_cells = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    print(f"Celula inicial: {start_cell}")
    print(f"Maximo de celulas: {max_cells}")
    
    # Configurações otimizadas
    settings = {
        'BOT_NAME': 'borracharia_sp_completo',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': False,
        'TELNETCONSOLE_ENABLED': False,
        'LOG_LEVEL': 'INFO',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    }
    
    # Inicializar processo
    process = CrawlerProcess(settings)
    process.crawl(BorrachariaSaoPauloCompleto, start_cell=start_cell, max_cells=max_cells)
    
    try:
        print("Iniciando processo...")
        process.start()
        print("Processo concluido!")
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
