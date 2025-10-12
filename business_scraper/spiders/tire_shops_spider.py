#!/usr/bin/env python3
"""
Spider para coletar borracharias em Santa Catarina
"""

import scrapy
import random
import time
from datetime import datetime
from scrapy_playwright.page import PageMethod

class TireShopsSpider(scrapy.Spider):
    name = 'tire_shops'
    
    # Configuração de grid - Santa Catarina COMPLETO
    GRID_SIZE_KM = 5
    LAT_MIN, LAT_MAX = -29.35, -25.95  # Santa Catarina completo
    LON_MIN, LON_MAX = -53.83, -48.35
    
    SEARCH_TERMS = ["borracharia"]
    
    # User agents simples
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    def start_requests(self):
        """Gera requisições para o grid"""
        self.logger.info("🔧 TIRE SHOPS SPIDER INICIADO - COLETANDO BORRACHARIAS")
        self.logger.info(f"📊 TIRE_SPIDER_STATS: {{'status': 'started', 'timestamp': '{datetime.now().isoformat()}'}}")
        
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
        
        total_requests = len(cells) * len(self.SEARCH_TERMS)
        self.logger.info(f"📊 TIRE_SPIDER_STATS: {{'total_cells': {len(cells)}, 'total_requests': {total_requests}, 'search_terms': {len(self.SEARCH_TERMS)}}}")
        
        # Gera requisições
        for i, (lat, lon) in enumerate(cells):
            for term in self.SEARCH_TERMS:
                url = f"https://www.google.com/maps/search/{term}/@{lat},{lon},15z"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_timeout', 3000),
                            PageMethod('wait_for_selector', '[data-value="Search results"]', timeout=10000),
                        ],
                        'cell_index': i,
                        'cell_lat': lat,
                        'cell_lon': lon,
                        'search_term': term,
                        'user_agent': random.choice(self.USER_AGENTS)
                    },
                    headers={
                        'User-Agent': random.choice(self.USER_AGENTS),
                        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                    }
                )
                
                # Delay entre requisições
                time.sleep(random.uniform(1, 3))

    def parse(self, response):
        """Parse da página de resultados"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        self.logger.info(f"🔧 Processando célula {cell_index} - {search_term} em ({cell_lat:.4f}, {cell_lon:.4f})")
        
        # Seletores para estabelecimentos
        establishments = response.css('[data-result-index]')
        
        if not establishments:
            self.logger.warning(f"⚠️ Nenhum estabelecimento encontrado na célula {cell_index}")
            return
        
        for establishment in establishments:
            try:
                # Extrair dados básicos
                name = establishment.css('[data-value="Search results"] h3::text').get()
                if not name:
                    name = establishment.css('h3::text').get()
                
                # Rating e reviews
                rating = establishment.css('[data-value] span[aria-label*="estrelas"]::attr(aria-label)').get()
                reviews_text = establishment.css('[data-value] span[aria-label*="avaliações"]::text').get()
                
                # Categoria
                category = establishment.css('[data-value] span:contains("Borracharia")::text').get()
                if not category:
                    category = establishment.css('[data-value] span:contains("Pneus")::text').get()
                
                # Endereço
                address = establishment.css('[data-value] div:contains("·") + div::text').get()
                
                # Link
                link_element = establishment.css('a[href*="/maps/place/"]::attr(href)').get()
                full_link = f"https://www.google.com{link_element}" if link_element else None
                
                # Place ID (extrair do link)
                place_id = None
                if link_element and '/place/' in link_element:
                    try:
                        place_id = link_element.split('/place/')[1].split('/')[0]
                    except:
                        pass
                
                # Processar rating
                rating_value = None
                if rating:
                    try:
                        rating_value = float(rating.split()[0].replace(',', '.'))
                    except:
                        pass
                
                # Processar reviews
                reviews_count = None
                if reviews_text:
                    try:
                        reviews_count = int(reviews_text.replace('(', '').replace(')', '').replace('.', ''))
                    except:
                        pass
                
                # Criar item
                item = {
                    'name': name,
                    'place_id': place_id,
                    'rating': rating_value,
                    'reviews_count': reviews_count,
                    'category': category or 'Borracharia',
                    'address': address,
                    'phone': None,  # Será coletado em detalhes se necessário
                    'website': None,
                    'hours': None,
                    'link': full_link,
                    'scraped_at': datetime.now().isoformat(),
                    'cell_lat': cell_lat,
                    'cell_lon': cell_lon,
                    'search_term': search_term,
                    'cell_index': cell_index,
                    'source': 'tire_shops_spider'
                }
                
                # Log do estabelecimento encontrado
                self.logger.info(f"🔧 TIRE_SHOP_DATA: {item}")
                
                yield item
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao processar estabelecimento: {e}")
                continue
        
        # Log de progresso
        self.logger.info(f"✅ Célula {cell_index} processada - {len(establishments)} borracharias encontradas")

    def closed(self, reason):
        """Callback quando spider termina"""
        self.logger.info(f"🔧 TIRE SHOPS SPIDER FINALIZADO - Motivo: {reason}")
        self.logger.info(f"📊 TIRE_SPIDER_STATS: {{'status': 'finished', 'reason': '{reason}', 'timestamp': '{datetime.now().isoformat()}'}}")
