#!/usr/bin/env python3
"""
Spider final com salvamento direto garantido
"""

import scrapy
import json
import os
import threading
from datetime import datetime
from scrapy_playwright.page import PageMethod
from business_scraper.items import FuelStationItem

class FuelFinalSpider(scrapy.Spider):
    name = 'fuel_final'
    allowed_domains = ['maps.google.com']
    
    # Grid configuration
    GRID_SIZE_KM = 5
    LAT_MIN, LAT_MAX = -29.35, -25.95
    LON_MIN, LON_MAX = -53.83, -48.35
    SEARCH_TERMS = ["gas station", "posto de combustível"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Data storage
        self.results = []
        self.seen_place_ids = set()
        self.establishments_processed = 0
        self.save_interval = 10  # Salva a cada 10 itens
        self.output_file = 'output/fuel_stations_final.json'
        self.lock = threading.Lock()
        
        # Cria diretório
        os.makedirs('output', exist_ok=True)
        
        # Limpa arquivo anterior
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            self.logger.info(f"🗑️ Arquivo anterior removido: {self.output_file}")
        
        self.logger.info(f"🚀 Spider iniciado - salvamento a cada {self.save_interval} itens")

    def start_requests(self):
        """Generate requests for each grid cell and search term"""
        cells = self._generate_grid_cells()
        total_requests = len(cells) * len(self.SEARCH_TERMS)
        
        self.logger.info(f"Generated {total_requests} total searches ({len(cells)} cells × {len(self.SEARCH_TERMS)} terms)")
        
        for i, (lat, lon) in enumerate(cells):
            for term in self.SEARCH_TERMS:
                url = f"https://www.google.com/maps/search/{term}/@{lat},{lon},12z"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_search_results,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', 'div[role="feed"]', timeout=15000),
                        ],
                        'cell_index': i,
                        'cell_lat': lat,
                        'cell_lon': lon,
                        'search_term': term
                    }
                )

    def parse_search_results(self, response):
        """Parse search results from Google Maps"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        # Extract business cards
        selectors_to_try = [
            'div.fontHeadlineSmall::text',
            'a.hfpxzc::text',
            'div.qBF1Pd::text',
        ]
        
        business_names = []
        for selector in selectors_to_try:
            names = response.css(selector).getall()
            business_names.extend(names)
            if len(business_names) >= 8:
                break
        
        # Remove duplicates while preserving order
        unique_names = []
        seen = set()
        for name in business_names:
            if name and name not in seen:
                unique_names.append(name)
                seen.add(name)
        
        self.logger.info(f"Cell {cell_index}: Found {len(unique_names)} unique business names")
        
        establishments_found = 0
        
        for i, name in enumerate(unique_names):
            # Create establishment data
            place_id = f"cell_{cell_index}_{i}_{hash(name) % 10000}"
            
            data = {
                'name': name,
                'place_id': place_id,
                'rating': None,
                'reviews_count': None,
                'category': 'Gas Station',
                'address': f"Santa Catarina, Brasil (lat: {cell_lat:.4f}, lon: {cell_lon:.4f})",
                'link': None,
                'scraped_at': datetime.now().isoformat(),
                'cell_lat': cell_lat,
                'cell_lon': cell_lon,
                'search_term': search_term
            }
            
            # Add if unique
            if self._add_unique_establishment(data):
                establishments_found += 1
                
                # Salva diretamente
                self._save_direct(data)
                
                # Yield item para compatibilidade
                item = FuelStationItem()
                for key, value in data.items():
                    if key in item.fields:
                        item[key] = value
                yield item
        
        self.logger.info(f"Cell {cell_index} completed: {establishments_found} fuel stations found")

    def _generate_grid_cells(self):
        """Generate grid cells covering Santa Catarina"""
        cells = []
        
        # Calculate number of cells
        lat_range = self.LAT_MAX - self.LAT_MIN
        lon_range = self.LON_MAX - self.LON_MIN
        
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

    def _add_unique_establishment(self, data):
        """Add establishment if unique"""
        with self.lock:
            place_id = data['place_id']
            if place_id not in self.seen_place_ids:
                self.seen_place_ids.add(place_id)
                self.results.append(data)
                self.establishments_processed += 1
                return True
            return False

    def _save_direct(self, data):
        """Salva item diretamente no arquivo"""
        try:
            with self.lock:
                # Lê arquivo existente
                if os.path.exists(self.output_file):
                    with open(self.output_file, 'r', encoding='utf-8') as f:
                        try:
                            existing_data = json.load(f)
                        except json.JSONDecodeError:
                            existing_data = []
                else:
                    existing_data = []
                
                # Adiciona novo item
                existing_data.append(data)
                
                # Salva arquivo
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
                # Log periódico
                if len(existing_data) % self.save_interval == 0:
                    self.logger.info(f"💾 SALVAMENTO DIRETO: {len(existing_data)} itens em {self.output_file}")
                    
        except Exception as e:
            self.logger.error(f"❌ Erro no salvamento: {e}")

    def closed(self, reason):
        """Called when spider closes"""
        with self.lock:
            total_items = len(self.results)
            self.logger.info(f"✅ Spider finalizado: {total_items} estabelecimentos únicos coletados")
            self.logger.info(f"📄 Arquivo final: {self.output_file}")
            
            # Salva resumo
            summary = {
                'total_establishments': total_items,
                'unique_place_ids': len(self.seen_place_ids),
                'finished_at': datetime.now().isoformat(),
                'reason': reason
            }
            
            summary_file = 'output/scraping_summary.json'
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"📊 Resumo salvo em: {summary_file}")
