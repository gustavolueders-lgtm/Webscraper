import scrapy
import json
import threading
import time
import re
import math
import os
from datetime import datetime
from urllib.parse import quote_plus
from business_scraper.utils.performance_analyzer import PerformanceAnalyzer
from business_scraper.items import FuelStationItem

class SimpleFuelSpider(scrapy.Spider):
    name = 'simple_fuel'
    allowed_domains = ['google.com']

    # Search terms
    SEARCH_TERMS = ["gas station", "posto de combustível"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Thread safety locks
        self.results_lock = threading.Lock()
        self.file_lock = threading.Lock()
        
        # Data storage
        self.seen_place_ids = set()
        self.results = []
        self.establishments_processed = 0
        self.save_interval = 25  # Salva a cada 25 itens
        self.output_file = 'output/fuel_stations_direct.json'
        
        # Performance tracking
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Grid configuration for Santa Catarina
        self.lat_min = -29.35
        self.lat_max = -25.95
        self.lon_min = -53.83
        self.lon_max = -48.35
        self.grid_size_km = 5
        
        # Search terms
        self.search_terms = [
            "gas station",
            "posto de combustível"
        ]
        
        # Create output directory
        os.makedirs('output', exist_ok=True)

    def start_requests(self):
        """Generate initial requests for the grid search"""
        grid_cells = self._generate_grid_cells()
        self.performance_analyzer.update_total_cells(len(grid_cells))
        
        self.logger.info(f"Generated {len(grid_cells)} grid cells for scraping")

        # Log de estatísticas para monitoramento
        total_requests = len(grid_cells)
        self.logger.info(f"📊 SPIDER_STATS: {{\"total_cells\": {len(grid_cells)}, \"total_requests\": {total_requests}, \"search_terms\": {len(self.SEARCH_TERMS)}}}")
        
        for i, (lat, lon, term) in enumerate(grid_cells):
            url = f"https://www.google.com/maps/search/{quote_plus(term)}/@{lat},{lon},14z"
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_search_results,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        {'method': 'wait_for_selector', 'selector': 'div[role="feed"]', 'timeout': 15000},
                    ],
                    'cell_index': i,
                    'lat': lat,
                    'lon': lon,
                    'term': term
                },
                dont_filter=True
            )

    def _generate_grid_cells(self):
        """Generate grid cells for Santa Catarina with 5km spacing"""
        cells = []
        
        # Calculate grid steps
        lat_step = self.grid_size_km / 111.0  # 1 degree lat ≈ 111 km
        
        # Longitude step adjusted for latitude (cos correction)
        avg_lat = (self.lat_min + self.lat_max) / 2
        lon_step = self.grid_size_km / (111.0 * math.cos(math.radians(avg_lat)))
        
        # Generate grid points
        lat = self.lat_min
        while lat <= self.lat_max:
            lon = self.lon_min
            while lon <= self.lon_max:
                # Add both search terms for each cell
                for term in self.search_terms:
                    cells.append((lat, lon, term))
                lon += lon_step
            lat += lat_step
        
        self.logger.info(f"Generated {len(cells)} total searches ({len(cells)//2} cells × 2 terms)")
        return cells

    def parse_search_results(self, response):
        """Parse search results from Google Maps"""
        cell_index = response.meta['cell_index']
        lat = response.meta['lat']
        lon = response.meta['lon']
        term = response.meta['term']
        
        self.performance_analyzer.start_cell_processing(cell_index, lat, lon, term)
        establishments_found = 0
        
        try:
            # Extract business names from the page
            # Try multiple selectors that Google Maps commonly uses
            selectors_to_try = [
                'div.fontHeadlineSmall::text',
                'a.hfpxzc::text',
                'div.qBF1Pd::text',
                'h3.fontHeadlineSmall::text',
                'span.fontHeadlineSmall::text'
            ]
            
            all_names = []
            for selector in selectors_to_try:
                names = response.css(selector).getall()
                all_names.extend(names)
            
            # Remove duplicates while preserving order
            unique_names = []
            seen = set()
            for name in all_names:
                if name and name.strip() and name.strip() not in seen:
                    unique_names.append(name.strip())
                    seen.add(name.strip())
            
            self.logger.info(f"Cell {cell_index}: Found {len(unique_names)} unique business names")
            
            # Process each business name
            for i, name in enumerate(unique_names[:20]):  # Limit to 20 per cell
                if self._is_fuel_station(name):
                    data = {
                        'name': name,
                        'place_id': f"cell_{cell_index}_{i}_{hash(name) % 10000}",
                        'rating': None,
                        'reviews_count': None,
                        'category': 'Gas Station',
                        'address': f"Santa Catarina, Brasil (lat: {lat:.4f}, lon: {lon:.4f})",
                        'link': None,
                        'scraped_at': datetime.now().isoformat(),
                        'source': 'google_maps_simple'
                    }
                    
                    if self._add_unique_establishment(data):
                        establishments_found += 1

                        # LOG ESTRUTURADO PARA MONITORAMENTO
                        self.logger.info(f"🏪 ESTABLISHMENT_DATA: {json.dumps(data, ensure_ascii=False)}")

                        # Salva diretamente no arquivo
                        self._save_item_direct(data)

                        # Create and yield item (para compatibilidade)
                        item = FuelStationItem()
                        for key, value in data.items():
                            if key in item.fields:
                                item[key] = value
                        yield item
            
            self.performance_analyzer.complete_cell_processing(cell_index, establishments_found, True)

            # Log de progresso da célula para monitoramento
            progress_data = {
                'cell_index': cell_index,
                'cell_lat': lat,
                'cell_lon': lon,
                'search_term': search_term,
                'establishments_found': establishments_found,
                'total_establishments': len(self.results),
                'cells_processed': len([c for c in self.performance_analyzer.cell_results if c['success']]),
                'timestamp': datetime.now().isoformat()
            }
            self.logger.info(f"📍 CELL_COMPLETED: {json.dumps(progress_data, ensure_ascii=False)}")

            self.logger.info(f"Cell {cell_index} completed: {establishments_found} fuel stations found")
            
        except Exception as e:
            self.logger.error(f"Error processing cell {cell_index}: {str(e)}")
            self.performance_analyzer.complete_cell_processing(cell_index, 0, False, str(e))

    def _is_fuel_station(self, name):
        """Check if business name indicates a fuel station"""
        if not name:
            return False
            
        name_lower = name.lower()
        fuel_keywords = [
            'posto', 'gas', 'petrol', 'combustível', 'gasolina', 
            'shell', 'br', 'ipiranga', 'esso', 'texaco', 'ale',
            'station', 'fuel', 'diesel', 'etanol', 'gnv',
            'distribuidora', 'combustíveis'
        ]
        
        return any(keyword in name_lower for keyword in fuel_keywords)

    def _add_unique_establishment(self, data):
        """Add establishment if not duplicate (thread-safe)"""
        with self.results_lock:
            place_id = data['place_id']
            if place_id not in self.seen_place_ids:
                self.seen_place_ids.add(place_id)
                self.results.append(data)
                self.establishments_processed += 1
                self.performance_analyzer.add_unique_establishment()
                return True
            else:
                self.performance_analyzer.add_duplicate_filtered()
                return False

    def _save_item_direct(self, data):
        """Salva item diretamente no arquivo JSON"""
        try:
            with self.file_lock:
                # Lê arquivo existente ou cria lista vazia
                if os.path.exists(self.output_file):
                    with open(self.output_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                else:
                    existing_data = []

                # Adiciona novo item
                existing_data.append(data)

                # Salva de volta
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)

                # Log a cada intervalo
                if len(existing_data) % self.save_interval == 0:
                    self.logger.info(f"💾 SALVAMENTO DIRETO: {len(existing_data)} itens salvos em {self.output_file}")

        except Exception as e:
            self.logger.error(f"❌ Erro no salvamento direto: {e}")

    def _save_incremental_results(self):
        """Save results incrementally (thread-safe)"""
        with self.file_lock:
            try:
                output_file = 'output/fuel_stations.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"Saved {len(self.results)} establishments to {output_file}")
                
            except Exception as e:
                self.logger.error(f"Error saving incremental results: {str(e)}")

    def closed(self, reason):
        """Called when spider closes"""
        # Save final metrics
        summary = self.performance_analyzer.get_summary()

        # Log de finalização para monitoramento
        finish_data = {
            'status': 'finished',
            'reason': reason,
            'total_establishments': summary['unique_establishments'],
            'cells_processed': summary['cells_processed'],
            'unique_place_ids': len(self.seen_place_ids),
            'finished_at': datetime.now().isoformat()
        }
        self.logger.info(f"🏁 SPIDER_FINISHED: {json.dumps(finish_data, ensure_ascii=False)}")

        self.logger.info("=" * 50)
        self.logger.info("SCRAPING COMPLETED")
        self.logger.info("=" * 50)
        self.logger.info(f"Total establishments found: {summary['unique_establishments']}")
        self.logger.info(f"Cells processed: {summary['cells_processed']}/{summary['total_cells']}")
        self.logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"Total time: {summary['elapsed_time_hours']:.2f} hours")
        self.logger.info("=" * 50)
