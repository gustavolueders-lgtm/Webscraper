#!/usr/bin/env python3
"""
Spider simples com logging estruturado (sem Playwright)
"""

import scrapy
import json
import os
from datetime import datetime
from business_scraper.items import FuelStationItem

class SimpleMonitoredSpider(scrapy.Spider):
    name = 'simple_monitored'
    allowed_domains = ['google.com']
    
    # Grid configuration (reduzido para teste)
    GRID_SIZE_KM = 10  # Células maiores para teste
    LAT_MIN, LAT_MAX = -27.0, -26.0  # Área menor para teste
    LON_MIN, LON_MAX = -49.0, -48.0
    SEARCH_TERMS = ["gas station"]  # Apenas um termo para teste
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Contadores
        self.establishments_found = 0
        self.cells_processed = 0
        self.seen_place_ids = set()
        
        # Cria diretório
        os.makedirs('output', exist_ok=True)
        
        self.logger.info("🚀 SIMPLE MONITORED SPIDER INICIADO")
        self.logger.info(f"📊 SPIDER_STATS: {{\"status\": \"started\", \"timestamp\": \"{datetime.now().isoformat()}\"}}")

    def start_requests(self):
        """Generate requests for each grid cell and search term"""
        cells = self._generate_grid_cells()
        total_requests = len(cells) * len(self.SEARCH_TERMS)
        
        self.logger.info(f"📊 SPIDER_STATS: {{\"total_cells\": {len(cells)}, \"total_requests\": {total_requests}, \"search_terms\": {len(self.SEARCH_TERMS)}}}")
        
        for i, (lat, lon) in enumerate(cells):
            for term in self.SEARCH_TERMS:
                url = f"https://www.google.com/maps/search/{term}/@{lat},{lon},12z"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_search_results,
                    meta={
                        'cell_index': i,
                        'cell_lat': lat,
                        'cell_lon': lon,
                        'search_term': term
                    }
                )

    def parse_search_results(self, response):
        """Parse search results from Google Maps (simulado para teste)"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        # Simula encontrar estabelecimentos (para teste)
        fake_establishments = [
            f"Posto Shell {cell_index}",
            f"Posto BR {cell_index}",
            f"Posto Ipiranga {cell_index}",
            f"Auto Posto {cell_index}",
            f"Posto Petrobras {cell_index}"
        ]
        
        establishments_found = 0
        
        for i, name in enumerate(fake_establishments):
            # Create establishment data
            place_id = f"cell_{cell_index}_{i}_{hash(name) % 10000}"
            
            # Skip if already seen
            if place_id in self.seen_place_ids:
                continue
                
            self.seen_place_ids.add(place_id)
            
            data = {
                'name': name,
                'place_id': place_id,
                'rating': 4.2,
                'reviews_count': 150,
                'category': 'Gas Station',
                'address': f"Santa Catarina, Brasil (lat: {cell_lat:.4f}, lon: {cell_lon:.4f})",
                'link': f"https://maps.google.com/place/{place_id}",
                'scraped_at': datetime.now().isoformat(),
                'cell_lat': cell_lat,
                'cell_lon': cell_lon,
                'search_term': search_term,
                'cell_index': cell_index
            }
            
            establishments_found += 1
            self.establishments_found += 1
            
            # LOG ESTRUTURADO PARA MONITORAMENTO
            self.logger.info(f"🏪 ESTABLISHMENT_DATA: {json.dumps(data, ensure_ascii=False)}")
            
            # Yield item para compatibilidade
            item = FuelStationItem()
            for key, value in data.items():
                if key in item.fields:
                    item[key] = value
            yield item
        
        self.cells_processed += 1
        
        # Log de progresso da célula
        progress_data = {
            'cell_index': cell_index,
            'cell_lat': cell_lat,
            'cell_lon': cell_lon,
            'search_term': search_term,
            'establishments_found': establishments_found,
            'total_establishments': self.establishments_found,
            'cells_processed': self.cells_processed,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"📍 CELL_COMPLETED: {json.dumps(progress_data, ensure_ascii=False)}")

    def _generate_grid_cells(self):
        """Generate grid cells covering test area"""
        cells = []
        
        # Approximate degrees per km (rough calculation)
        lat_step = self.GRID_SIZE_KM / 111.0  # 1 degree ≈ 111 km
        lon_step = self.GRID_SIZE_KM / (111.0 * 0.85)  # Adjust for latitude
        
        lat = self.LAT_MIN
        while lat < self.LAT_MAX:
            lon = self.LON_MIN
            while lon < self.LON_MAX:
                cells.append((lat, lon))
                lon += lon_step
            lat += lat_step
        
        return cells

    def closed(self, reason):
        """Called when spider closes"""
        summary = {
            'status': 'finished',
            'reason': reason,
            'total_establishments': self.establishments_found,
            'cells_processed': self.cells_processed,
            'unique_place_ids': len(self.seen_place_ids),
            'finished_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"🏁 SPIDER_FINISHED: {json.dumps(summary, ensure_ascii=False)}")
