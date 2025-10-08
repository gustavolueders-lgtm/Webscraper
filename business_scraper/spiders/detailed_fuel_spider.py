#!/usr/bin/env python3
"""
Spider que coleta dados detalhados incluindo telefones
"""

import scrapy
import json
import os
import asyncio
from datetime import datetime
from scrapy_playwright.page import PageMethod
from business_scraper.items import FuelStationItem

class DetailedFuelSpider(scrapy.Spider):
    name = 'detailed_fuel'
    allowed_domains = ['google.com']
    
    # Grid configuration (área menor para teste)
    GRID_SIZE_KM = 10
    LAT_MIN, LAT_MAX = -27.7, -27.5  # Florianópolis região
    LON_MIN, LON_MAX = -48.7, -48.4
    SEARCH_TERMS = ["posto de gasolina"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Contadores
        self.establishments_found = 0
        self.phones_collected = 0
        self.cells_processed = 0
        self.seen_place_ids = set()
        
        # Cria diretório
        os.makedirs('output', exist_ok=True)
        
        self.logger.info("📞 DETAILED SPIDER INICIADO - COLETA TELEFONES")
        self.logger.info(f"📊 SPIDER_STATS: {{\"status\": \"started\", \"timestamp\": \"{datetime.now().isoformat()}\"}}")

    def start_requests(self):
        """Generate requests for each grid cell and search term"""
        cells = self._generate_grid_cells()
        total_requests = len(cells) * len(self.SEARCH_TERMS)
        
        self.logger.info(f"📊 SPIDER_STATS: {{\"total_cells\": {len(cells)}, \"total_requests\": {total_requests}, \"search_terms\": {len(self.SEARCH_TERMS)}}}")
        
        for i, (lat, lon) in enumerate(cells):
            for term in self.SEARCH_TERMS:
                url = f"https://www.google.com/maps/search/{term}/@{lat},{lon},13z"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_search_results,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', 'div[role="feed"]', timeout=30000),
                        ],
                        'cell_index': i,
                        'cell_lat': lat,
                        'cell_lon': lon,
                        'search_term': term
                    }
                )

    def parse_search_results(self, response):
        """Parse search results and extract detailed data"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        self.logger.info(f"🔍 Processando célula {cell_index} - {search_term}")
        
        # Extrai dados detalhados usando JavaScript
        yield scrapy.Request(
            url=response.url,
            callback=self.extract_detailed_data,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_selector', 'div[role="feed"]', timeout=30000),
                    PageMethod('evaluate', self._get_detailed_extraction_script()),
                ],
                'cell_index': cell_index,
                'cell_lat': cell_lat,
                'cell_lon': cell_lon,
                'search_term': search_term
            }
        )

    def extract_detailed_data(self, response):
        """Extract detailed data including phones"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        # Obtém dados do JavaScript
        establishments_data = response.meta.get('playwright_page_result', [])
        
        if not establishments_data:
            self.logger.warning(f"❌ Nenhum dado extraído da célula {cell_index}")
            return
        
        establishments_found = 0
        
        for i, data in enumerate(establishments_data):
            if not data.get('name'):
                continue
                
            # Create establishment data
            place_id = f"detailed_{cell_index}_{i}_{hash(data['name']) % 10000}"
            
            # Skip if already seen
            if place_id in self.seen_place_ids:
                continue
                
            self.seen_place_ids.add(place_id)
            
            establishment = {
                'name': data.get('name', ''),
                'place_id': place_id,
                'phone': data.get('phone', ''),
                'website': data.get('website', ''),
                'rating': data.get('rating', None),
                'reviews_count': data.get('reviews_count', None),
                'category': 'Gas Station',
                'address': data.get('address', f"Santa Catarina, Brasil (lat: {cell_lat:.4f}, lon: {cell_lon:.4f})"),
                'hours': data.get('hours', ''),
                'link': data.get('link', ''),
                'scraped_at': datetime.now().isoformat(),
                'cell_lat': cell_lat,
                'cell_lon': cell_lon,
                'search_term': search_term,
                'cell_index': cell_index
            }
            
            establishments_found += 1
            self.establishments_found += 1
            
            # Conta telefones coletados
            if establishment['phone']:
                self.phones_collected += 1
            
            # LOG ESTRUTURADO PARA MONITORAMENTO
            self.logger.info(f"🏪 ESTABLISHMENT_DATA: {json.dumps(establishment, ensure_ascii=False)}")
            
            # Yield item
            item = FuelStationItem()
            for key, value in establishment.items():
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
            'phones_collected': self.phones_collected,
            'cells_processed': self.cells_processed,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"📍 CELL_COMPLETED: {json.dumps(progress_data, ensure_ascii=False)}")

    def _get_detailed_extraction_script(self):
        """JavaScript para extrair dados detalhados"""
        return """
        async () => {
            console.log('🔍 Iniciando extração detalhada...');
            
            const results = [];
            const maxResults = 10; // Limita para não demorar muito
            
            // Aguarda carregar
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Encontra cards de estabelecimentos
            const cards = document.querySelectorAll('div[role="feed"] > div');
            console.log(`📍 Encontrados ${cards.length} cards`);
            
            for (let i = 0; i < Math.min(cards.length, maxResults); i++) {
                const card = cards[i];
                
                try {
                    // Extrai nome do card
                    const nameElement = card.querySelector('div.fontHeadlineSmall, a.hfpxzc, div.qBF1Pd');
                    if (!nameElement || !nameElement.textContent) continue;
                    
                    const name = nameElement.textContent.trim();
                    console.log(`🏪 Processando: ${name}`);
                    
                    // Clica no estabelecimento
                    const clickable = card.querySelector('a, div[role="button"]') || card;
                    clickable.click();
                    
                    // Aguarda carregar detalhes
                    await new Promise(resolve => setTimeout(resolve, 5000));
                    
                    // Extrai dados detalhados
                    const data = {
                        name: name,
                        phone: '',
                        website: '',
                        address: '',
                        rating: null,
                        reviews_count: null,
                        hours: '',
                        link: window.location.href
                    };
                    
                    // Telefone
                    const phoneSelectors = [
                        'button[data-item-id*="phone"] span',
                        'div[data-item-id*="phone"] span',
                        'span[data-phone]',
                        'a[href^="tel:"]'
                    ];
                    
                    for (const selector of phoneSelectors) {
                        const phoneEl = document.querySelector(selector);
                        if (phoneEl && phoneEl.textContent) {
                            data.phone = phoneEl.textContent.trim();
                            break;
                        }
                    }
                    
                    // Website
                    const websiteEl = document.querySelector('a[data-item-id*="authority"], a[href^="http"]:not([href*="google"])');
                    if (websiteEl) {
                        data.website = websiteEl.href;
                    }
                    
                    // Endereço
                    const addressEl = document.querySelector('button[data-item-id*="address"] span, div[data-item-id*="address"] span');
                    if (addressEl) {
                        data.address = addressEl.textContent.trim();
                    }
                    
                    // Rating
                    const ratingEl = document.querySelector('span.MW4etd');
                    if (ratingEl) {
                        data.rating = parseFloat(ratingEl.textContent);
                    }
                    
                    // Reviews count
                    const reviewsEl = document.querySelector('span.UY7F9');
                    if (reviewsEl) {
                        const match = reviewsEl.textContent.match(/\\((\\d+)\\)/);
                        if (match) {
                            data.reviews_count = parseInt(match[1]);
                        }
                    }
                    
                    // Horários
                    const hoursEl = document.querySelector('div[data-item-id*="oh"] span');
                    if (hoursEl) {
                        data.hours = hoursEl.textContent.trim();
                    }
                    
                    results.push(data);
                    console.log(`✅ Dados coletados: ${data.name} - Tel: ${data.phone || 'N/A'}`);
                    
                    // Volta para a lista (pressiona ESC)
                    document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                } catch (error) {
                    console.error(`❌ Erro ao processar ${name}:`, error);
                    // Tenta voltar para lista
                    document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
            
            console.log(`🎯 Extração concluída: ${results.length} estabelecimentos`);
            return results;
        }
        """

    def _generate_grid_cells(self):
        """Generate grid cells covering test area"""
        cells = []
        
        # Approximate degrees per km
        lat_step = self.GRID_SIZE_KM / 111.0
        lon_step = self.GRID_SIZE_KM / (111.0 * 0.85)
        
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
            'phones_collected': self.phones_collected,
            'phone_success_rate': (self.phones_collected / self.establishments_found * 100) if self.establishments_found > 0 else 0,
            'cells_processed': self.cells_processed,
            'unique_place_ids': len(self.seen_place_ids),
            'finished_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"🏁 SPIDER_FINISHED: {json.dumps(summary, ensure_ascii=False)}")
        self.logger.info(f"📞 TELEFONES COLETADOS: {self.phones_collected}/{self.establishments_found} ({summary['phone_success_rate']:.1f}%)")
