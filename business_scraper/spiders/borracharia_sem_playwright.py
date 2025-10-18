#!/usr/bin/env python3
"""
Spider para borracharias SEM Playwright (apenas HTTP)
"""

import scrapy
import random
import time
import re
from datetime import datetime

class BorrachariaSemPlaywrightSpider(scrapy.Spider):
    name = 'borracharia_sem_playwright'
    
    # Configuração de grid - São Paulo COMPLETO
    GRID_SIZE_KM = 5
    LAT_MIN, LAT_MAX = -25.3, -19.8  # São Paulo completo
    LON_MIN, LON_MAX = -53.1, -44.2
    
    SEARCH_TERMS = ["borracharia"]
    
    # User agents simples
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    def __init__(self, start_cell=None, *args, **kwargs):
        super(BorrachariaSemPlaywrightSpider, self).__init__(*args, **kwargs)
        
        # Célula de início (pode ser passada como parâmetro)
        self.start_cell = int(start_cell) if start_cell else 0
        
        self.logger.info(f"🔧 BORRACHARIA SEM PLAYWRIGHT SPIDER INICIADO")
        self.logger.info(f"🎯 Começando da célula: {self.start_cell}")
    
    def start_requests(self):
        """Gera requisições para o grid a partir da célula especificada"""
        self.logger.info(f"📊 BORRACHARIA_SEM_PLAYWRIGHT_STATS: {{'status': 'started', 'start_cell': {self.start_cell}, 'timestamp': '{datetime.now().isoformat()}'}}")
        
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
        remaining_cells = total_cells - self.start_cell
        total_requests = remaining_cells * len(self.SEARCH_TERMS)
        
        self.logger.info(f"📊 BORRACHARIA_SEM_PLAYWRIGHT_STATS: {{'total_cells': {total_cells}, 'start_cell': {self.start_cell}, 'remaining_cells': {remaining_cells}, 'total_requests': {total_requests}, 'search_terms': {len(self.SEARCH_TERMS)}}}")
        
        # Gera apenas as primeiras 5 células para teste
        for i, (lat, lon) in enumerate(cells[self.start_cell:self.start_cell+5], start=self.start_cell):
            for term in self.SEARCH_TERMS:
                url = f"https://www.google.com/search?q={term}+{lat},{lon}"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_simple,
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
                    }
                )

    def parse_simple(self, response):
        """Parse simples sem complexidade"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        self.logger.info(f"📍 Processando célula {cell_index}: {cell_lat:.4f}, {cell_lon:.4f}")
        self.logger.info(f"✅ Resposta recebida: {response.status}")
        
        # Tentar extrair alguns resultados básicos
        title = response.css('title::text').get()
        self.logger.info(f"📄 Título: {title}")
        
        # Contar links que podem ser borracharias
        links = response.css('a[href*="borracharia"]')
        self.logger.info(f"🔍 Links com 'borracharia': {len(links)}")
        
        return {
            'cell_index': cell_index,
            'cell_lat': cell_lat,
            'cell_lon': cell_lon,
            'search_term': search_term,
            'status': response.status,
            'title': title,
            'links_count': len(links)
        }
