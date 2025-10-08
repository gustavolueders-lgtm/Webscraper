#!/usr/bin/env python3
"""
Spider simples para VPN - apenas dados REAIS
"""

import scrapy
import random
import time
from datetime import datetime
from scrapy_playwright.page import PageMethod

class SimpleVpnSpider(scrapy.Spider):
    name = 'simple_vpn'
    
    # Configuração de grid - Santa Catarina COMPLETO
    GRID_SIZE_KM = 5
    LAT_MIN, LAT_MAX = -29.35, -25.95  # Santa Catarina completo
    LON_MIN, LON_MAX = -53.83, -48.35
    
    SEARCH_TERMS = ["posto de combustível"]
    
    # User agents simples
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    def start_requests(self):
        """Gera requisições para o grid"""
        self.logger.info("🌐 VPN SPIDER INICIADO - APENAS DADOS REAIS")
        self.logger.info(f"📊 SPIDER_STATS: {{'status': 'started', 'timestamp': '{datetime.now().isoformat()}'}}")
        
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
        self.logger.info(f"📊 SPIDER_STATS: {{'total_cells': {len(cells)}, 'total_requests': {total_requests}, 'search_terms': {len(self.SEARCH_TERMS)}}}")
        
        # Gera requisições
        for i, (lat, lon) in enumerate(cells):
            for term in self.SEARCH_TERMS:
                # Delay progressivo
                delay = random.uniform(15, 25)  # 15-25 segundos
                
                url = f"https://www.google.com/maps/search/{term}/@{lat},{lon},13z"
                user_agent = random.choice(self.USER_AGENTS)
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_simple,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_timeout', 3000),  # Aguarda 3 segundos
                        ],
                        'cell_index': i,
                        'cell_lat': lat,
                        'cell_lon': lon,
                        'search_term': term,
                        'user_agent': user_agent
                    },
                    dont_filter=True
                )
                
                # Pausa estratégica a cada 10 requisições
                if i % 10 == 0 and i > 0:
                    pause_time = random.uniform(60, 120)  # 1-2 minutos
                    self.logger.info(f"⏸️ Pausa estratégica: {pause_time:.1f}s")
                    time.sleep(pause_time)

    def parse_simple(self, response):
        """Parse simples sem complexidade"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        self.logger.info(f"🔍 Processando célula {cell_index}: {cell_lat:.4f}, {cell_lon:.4f}")
        
        # Extração simples de estabelecimentos
        establishments = []
        
        # Seletores básicos para cards do Google Maps
        cards = response.css('div[role="feed"] > div')
        
        for i, card in enumerate(cards):
            try:
                # Nome do estabelecimento - SELETORES CORRIGIDOS
                name_selectors = [
                    'div[class*="fontHeadline"]::text',
                    'div[class*="qBF1Pd"]::text',
                    'a span::text'
                ]

                name = None
                for selector in name_selectors:
                    name = card.css(selector).get()
                    if name and name.strip():
                        name = name.strip()
                        break

                # Pula cards que não são estabelecimentos
                if not name or name in ['Horas', 'Resultados', 'Alguns desses']:
                    continue

                # Extrai telefone do texto completo
                card_text = ' '.join(card.css('::text').getall())
                phone = self.extract_phone(card_text)
                
                # Extrai avaliação
                rating = self.extract_rating(card_text)

                # Extrai endereço
                address = self.extract_address(card_text)

                # Dados básicos
                establishment = {
                    'name': name,
                    'place_id': f"vpn_{cell_index}_{i}_{hash(name) % 10000}",
                    'rating': rating,
                    'reviews_count': None,
                    'category': 'Gas Station',
                    'address': address or f"Santa Catarina, Brasil (lat: {cell_lat:.4f}, lon: {cell_lon:.4f})",
                    'phone': phone,  # TELEFONE EXTRAÍDO!
                    'website': None,
                    'hours': None,
                    'link': response.url,
                    'scraped_at': datetime.now().isoformat(),
                    'cell_lat': cell_lat,
                    'cell_lon': cell_lon,
                    'search_term': search_term,
                    'cell_index': cell_index,
                    'source': 'google_maps_vpn'
                }
                
                establishments.append(establishment)
                
                # Log estruturado para monitor
                self.logger.info(f"🏪 ESTABLISHMENT_DATA: {establishment}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao processar card {i}: {e}")
                continue
        
        # Log de progresso
        self.logger.info(f"📍 CELL_COMPLETED: {{'cell_index': {cell_index}, 'establishments_found': {len(establishments)}, 'lat': {cell_lat}, 'lon': {cell_lon}}}")
        
        # Retorna estabelecimentos
        for establishment in establishments:
            yield establishment
        
        # Delay entre requisições
        delay = random.uniform(20, 30)
        self.logger.info(f"⏰ Aguardando {delay:.1f}s antes da próxima requisição")
        time.sleep(delay)

    def extract_phone(self, text):
        """Extrai telefone do texto"""
        import re

        # Padrões de telefone brasileiros
        patterns = [
            r'\(\d{2}\)\s*\d{4,5}-?\d{4}',  # (47) 3447-7100
            r'\d{2}\s*\d{4,5}-?\d{4}',      # 47 3447-7100
            r'\(\d{2}\)\s*\d{8,9}',         # (47) 34477100
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()

        return None

    def extract_rating(self, text):
        """Extrai avaliação do texto"""
        import re

        # Padrão: 4,4(498) ou 4.4(498)
        pattern = r'(\d+[,\.]\d+)\s*\(\d+\)'
        match = re.search(pattern, text)

        if match:
            rating = match.group(1).replace(',', '.')
            try:
                return float(rating)
            except:
                pass

        return None

    def extract_address(self, text):
        """Extrai endereço do texto"""
        import re

        # Procura por padrões de endereço
        patterns = [
            r'[A-Z][a-z]+\.?\s+[A-Z][a-z\s]+,\s*\d+',  # Av. Paulo Fontes, 1136
            r'R\.\s+[A-Z][a-z\s]+,\s*\d+',             # R. Nome da Rua, 123
            r'Rua\s+[A-Z][a-z\s]+,\s*\d+',             # Rua Nome da Rua, 123
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()

        return None

    def closed(self, reason):
        """Callback quando spider termina"""
        self.logger.info(f"🏁 SPIDER_FINISHED: {{'reason': '{reason}', 'timestamp': '{datetime.now().isoformat()}'}}")
