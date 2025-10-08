#!/usr/bin/env python3
"""
Spider stealth para contornar bloqueio do Google Maps
"""

import scrapy
import json
import os
import random
import time
from datetime import datetime
from scrapy_playwright.page import PageMethod
from business_scraper.items import FuelStationItem

class StealthFuelSpider(scrapy.Spider):
    name = 'stealth_fuel'
    allowed_domains = ['google.com']
    
    # Configuração de grid - Santa Catarina COMPLETO
    GRID_SIZE_KM = 5
    LAT_MIN, LAT_MAX = -29.35, -25.95  # Santa Catarina completo
    LON_MIN, LON_MAX = -53.83, -48.35
    SEARCH_TERMS = ["posto de combustível"]
    
    # Configurações anti-detecção
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    
    VIEWPORTS = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1440, 'height': 900},
        {'width': 1536, 'height': 864},
        {'width': 1280, 'height': 720}
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Contadores
        self.establishments_found = 0
        self.phones_collected = 0
        self.cells_processed = 0
        self.blocked_requests = 0
        self.successful_requests = 0
        self.seen_place_ids = set()
        
        # Controle de sessão
        self.requests_in_session = 0
        self.session_start_time = time.time()
        
        os.makedirs('output', exist_ok=True)
        
        self.logger.info("🥷 STEALTH SPIDER INICIADO - ANTI-BLOQUEIO")
        self.logger.info(f"📊 SPIDER_STATS: {{\"status\": \"started\", \"timestamp\": \"{datetime.now().isoformat()}\"}}")

    def start_requests(self):
        """Generate stealth requests"""
        cells = self._generate_grid_cells()
        total_requests = len(cells) * len(self.SEARCH_TERMS)
        
        self.logger.info(f"📊 SPIDER_STATS: {{\"total_cells\": {len(cells)}, \"total_requests\": {total_requests}, \"search_terms\": {len(self.SEARCH_TERMS)}}}")
        
        for i, (lat, lon) in enumerate(cells):
            for term in self.SEARCH_TERMS:
                url = f"https://www.google.com/maps/search/{term}/@{lat},{lon},13z"
                
                # Configurações stealth
                viewport = random.choice(self.VIEWPORTS)
                user_agent = random.choice(self.USER_AGENTS)
                
                # Delay inteligente
                base_delay = random.uniform(8, 15)  # 8-15 segundos base
                if self.requests_in_session > 0:
                    base_delay += random.uniform(2, 5)  # Delay adicional
                
                # Pausa estratégica a cada 15 requisições
                if self.requests_in_session > 0 and self.requests_in_session % 15 == 0:
                    strategic_pause = random.uniform(60, 120)  # 1-2 minutos
                    self.logger.info(f"⏸️ Pausa estratégica: {strategic_pause:.1f}s")
                    time.sleep(strategic_pause)
                    self.session_start_time = time.time()  # Reset session
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_with_stealth,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('set_viewport_size', viewport['width'], viewport['height']),
                            PageMethod('set_extra_http_headers', {
                                'User-Agent': user_agent,
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'DNT': '1',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1',
                                'Sec-Fetch-Dest': 'document',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'none',
                                'Cache-Control': 'max-age=0'
                            }),
                            PageMethod('wait_for_timeout', int(base_delay * 1000)),
                            PageMethod('wait_for_selector', 'div[role="feed"]', timeout=45000),
                            PageMethod('evaluate', self._get_stealth_script()),
                        ],
                        'cell_index': i,
                        'cell_lat': lat,
                        'cell_lon': lon,
                        'search_term': term,
                        'user_agent': user_agent,
                        'viewport': viewport
                    },
                    dont_filter=True
                )
                
                self.requests_in_session += 1

    def parse_with_stealth(self, response):
        """Parse com técnicas stealth"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        # Verifica se foi bloqueado
        if response.status == 429 or "blocked" in response.text.lower():
            self.blocked_requests += 1
            self.logger.warning(f"🚫 Bloqueio detectado na célula {cell_index}")
            
            # Estratégia de recovery
            if self.blocked_requests > 3:
                self.logger.warning("🚨 Muitos bloqueios - aumentando delays")
                time.sleep(random.uniform(300, 600))  # 5-10 minutos
            
            return
        
        self.successful_requests += 1
        self.logger.info(f"✅ Célula {cell_index} processada - {search_term}")
        
        # Extrai dados do JavaScript
        establishments_data = response.meta.get('playwright_page_result', [])
        
        if not establishments_data:
            self.logger.warning(f"❌ Nenhum dado extraído da célula {cell_index}")
            return
        
        establishments_found = 0
        
        for i, data in enumerate(establishments_data):
            if not data.get('name'):
                continue
                
            place_id = f"stealth_{cell_index}_{i}_{hash(data['name']) % 10000}"
            
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
                'address': data.get('address', f"Santa Catarina, Brasil"),
                'hours': data.get('hours', ''),
                'link': data.get('link', ''),
                'scraped_at': datetime.now().isoformat(),
                'cell_lat': cell_lat,
                'cell_lon': cell_lon,
                'search_term': search_term,
                'cell_index': cell_index,
                'stealth_mode': True
            }
            
            establishments_found += 1
            self.establishments_found += 1
            
            if establishment['phone']:
                self.phones_collected += 1
            
            # LOG ESTRUTURADO
            self.logger.info(f"🏪 ESTABLISHMENT_DATA: {json.dumps(establishment, ensure_ascii=False)}")
            
            # Yield item
            item = FuelStationItem()
            for key, value in establishment.items():
                if key in item.fields:
                    item[key] = value
            yield item
        
        self.cells_processed += 1
        
        # Log de progresso
        success_rate = (self.successful_requests / (self.successful_requests + self.blocked_requests) * 100) if (self.successful_requests + self.blocked_requests) > 0 else 0
        
        progress_data = {
            'cell_index': cell_index,
            'cell_lat': cell_lat,
            'cell_lon': cell_lon,
            'search_term': search_term,
            'establishments_found': establishments_found,
            'total_establishments': self.establishments_found,
            'phones_collected': self.phones_collected,
            'cells_processed': self.cells_processed,
            'success_rate': success_rate,
            'blocked_requests': self.blocked_requests,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"📍 CELL_COMPLETED: {json.dumps(progress_data, ensure_ascii=False)}")

    def _get_stealth_script(self):
        """JavaScript stealth para extração"""
        return """
        async () => {
            console.log('🥷 Iniciando extração stealth...');
            
            // Simula comportamento humano
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Scroll suave para simular leitura
            window.scrollTo({top: 300, behavior: 'smooth'});
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            const results = [];
            const maxResults = 15;
            
            // Encontra estabelecimentos
            const cards = document.querySelectorAll('div[role="feed"] > div');
            console.log(`🔍 Encontrados ${cards.length} cards`);
            
            for (let i = 0; i < Math.min(cards.length, maxResults); i++) {
                const card = cards[i];
                
                try {
                    const nameElement = card.querySelector('div.fontHeadlineSmall, a.hfpxzc, div.qBF1Pd');
                    if (!nameElement || !nameElement.textContent) continue;
                    
                    const name = nameElement.textContent.trim();
                    
                    // Simula clique humano
                    const clickable = card.querySelector('a, div[role="button"]') || card;
                    
                    // Scroll até o elemento
                    clickable.scrollIntoView({behavior: 'smooth', block: 'center'});
                    await new Promise(resolve => setTimeout(resolve, 800));
                    
                    clickable.click();
                    
                    // Aguarda carregar com timeout
                    await new Promise(resolve => setTimeout(resolve, 4000));
                    
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
                    
                    // Extrai telefone com múltiplos seletores
                    const phoneSelectors = [
                        'button[data-item-id*="phone"] span',
                        'div[data-item-id*="phone"] span',
                        'a[href^="tel:"]',
                        'span[aria-label*="telefone"]',
                        'span[aria-label*="phone"]'
                    ];
                    
                    for (const selector of phoneSelectors) {
                        const phoneEl = document.querySelector(selector);
                        if (phoneEl && phoneEl.textContent && phoneEl.textContent.match(/\\d/)) {
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
                    
                    // Rating e reviews
                    const ratingEl = document.querySelector('span.MW4etd');
                    if (ratingEl) {
                        data.rating = parseFloat(ratingEl.textContent);
                    }
                    
                    const reviewsEl = document.querySelector('span.UY7F9');
                    if (reviewsEl) {
                        const match = reviewsEl.textContent.match(/\\((\\d+)\\)/);
                        if (match) {
                            data.reviews_count = parseInt(match[1]);
                        }
                    }
                    
                    results.push(data);
                    console.log(`✅ ${name} - Tel: ${data.phone || 'N/A'}`);
                    
                    // Volta para lista (ESC)
                    document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                } catch (error) {
                    console.error(`❌ Erro:`, error);
                    document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
                    await new Promise(resolve => setTimeout(resolve, 1500));
                }
            }
            
            // Scroll final para simular leitura completa
            window.scrollTo({top: 0, behavior: 'smooth'});
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            console.log(`🎯 Extração concluída: ${results.length} estabelecimentos`);
            return results;
        }
        """

    def _generate_grid_cells(self):
        """Generate grid cells"""
        cells = []
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
        """Spider finalizado"""
        success_rate = (self.successful_requests / (self.successful_requests + self.blocked_requests) * 100) if (self.successful_requests + self.blocked_requests) > 0 else 0
        phone_rate = (self.phones_collected / self.establishments_found * 100) if self.establishments_found > 0 else 0
        
        summary = {
            'status': 'finished',
            'reason': reason,
            'total_establishments': self.establishments_found,
            'phones_collected': self.phones_collected,
            'phone_success_rate': phone_rate,
            'cells_processed': self.cells_processed,
            'success_rate': success_rate,
            'blocked_requests': self.blocked_requests,
            'successful_requests': self.successful_requests,
            'finished_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"🏁 SPIDER_FINISHED: {json.dumps(summary, ensure_ascii=False)}")
        self.logger.info(f"🥷 STEALTH STATS: {self.successful_requests} sucessos, {self.blocked_requests} bloqueios ({success_rate:.1f}% sucesso)")
        self.logger.info(f"📞 TELEFONES: {self.phones_collected}/{self.establishments_found} ({phone_rate:.1f}%)")
