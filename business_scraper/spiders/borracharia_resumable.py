#!/usr/bin/env python3
"""
Spider para borracharias com capacidade de retomar do ponto onde parou
"""

import scrapy
import random
import time
import re
from datetime import datetime
from scrapy_playwright.page import PageMethod

class BorrachariaResumableSpider(scrapy.Spider):
    name = 'borracharia_resumable'

    # Configuração de grid - Santa Catarina COMPLETO
    GRID_SIZE_KM = 5
    LAT_MIN, LAT_MAX = -29.35, -25.95  # Santa Catarina
    LON_MIN, LON_MAX = -53.83, -48.35

    SEARCH_TERMS = ["borracharia"]

    # User agents simples
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]

    def __init__(self, start_cell=None, *args, **kwargs):
        super(BorrachariaResumableSpider, self).__init__(*args, **kwargs)

        # Célula de início (pode ser passada como parâmetro)
        self.start_cell = int(start_cell) if start_cell else 0

        self.logger.info(f"🔧 BORRACHARIA RESUMABLE SPIDER INICIADO")
        self.logger.info(f"🎯 Começando da célula: {self.start_cell}")

    def start_requests(self):
        """Gera requisições para o grid a partir da célula especificada"""
        self.logger.info(f"📊 BORRACHARIA_RESUMABLE_STATS: {{'status': 'started', 'start_cell': {self.start_cell}, 'timestamp': '{datetime.now().isoformat()}'}}")

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

        self.logger.info(f"📊 BORRACHARIA_RESUMABLE_STATS: {{'total_cells': {total_cells}, 'start_cell': {self.start_cell}, 'remaining_cells': {remaining_cells}, 'total_requests': {total_requests}, 'search_terms': {len(self.SEARCH_TERMS)}}}")

        # Gera requisições a partir da célula de início
        for i, (lat, lon) in enumerate(cells[self.start_cell:], start=self.start_cell):
            for term in self.SEARCH_TERMS:
                url = f"https://www.google.com/maps/search/{term}/@{lat},{lon},15z"

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_simple,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_timeout', 3000),
                            PageMethod('wait_for_selector', 'div[role="feed"]', timeout=10000),
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

                # Pausa estratégica a cada 10 requisições (como no spider original)
                if i % 10 == 0 and i > 0:
                    pause_time = random.uniform(30, 60)  # 30-60 segundos
                    self.logger.info(f"⏸️ Pausa estratégica: {pause_time:.1f}s")
                    time.sleep(pause_time)

    def parse_simple(self, response):
        """Parse simples sem complexidade"""
        cell_index = response.meta['cell_index']
        cell_lat = response.meta['cell_lat']
        cell_lon = response.meta['cell_lon']
        search_term = response.meta['search_term']
        
        self.logger.info(f"🔧 Processando célula {cell_index}: {cell_lat:.4f}, {cell_lon:.4f}")
        
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

                # Verificar se é realmente uma borracharia
                name_lower = name.lower()
                card_text = ' '.join(card.css('::text').getall()).lower()
                
                # Palavras-chave para borracharias
                tire_keywords = ['borracharia', 'pneu', 'tire', 'roda', 'vulcanização', 'recauchutagem', 'calibragem']
                
                if not any(keyword in name_lower or keyword in card_text for keyword in tire_keywords):
                    continue

                # Extrai telefone do texto completo
                phone = self.extract_phone(card_text)

                # Extrai avaliação
                rating = self.extract_rating(card_text)

                # Extrai número de avaliações
                reviews_count = self.extract_reviews_count(card_text)

                # Extrai endereço
                address = self.extract_address(card_text)

                # Dados básicos
                establishment = {
                    'name': name,
                    'place_id': f"borracharia_resumable_{cell_index}_{i}_{hash(name) % 10000}",
                    'rating': rating,
                    'reviews_count': reviews_count,
                    'category': 'Borracharia',
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
                    'source': 'borracharia_resumable_spider'
                }
                
                establishments.append(establishment)
                
                # Log estruturado para monitor
                self.logger.info(f"🔧 TIRE_SHOP_DATA: {establishment}")
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao processar card {i}: {e}")
                continue
        
        # Log de progresso
        self.logger.info(f"✅ Célula {cell_index} processada - {len(establishments)} borracharias encontradas")
        
        # Yield dos estabelecimentos
        for establishment in establishments:
            yield establishment

    def extract_phone(self, text):
        """Extrai telefone do texto"""
        # Padrões de telefone brasileiros
        phone_patterns = [
            r'\(\d{2}\)\s*\d{4,5}-?\d{4}',  # (XX) XXXXX-XXXX
            r'\d{2}\s*\d{4,5}-?\d{4}',      # XX XXXXX-XXXX
            r'\(\d{2}\)\s*\d{8,9}',         # (XX) XXXXXXXX
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return None

    def extract_rating(self, text):
        """Extrai avaliação do texto"""
        # Procura por padrões de avaliação mais abrangentes
        rating_patterns = [
            r'(\d,\d)\s*estrelas?',
            r'(\d\.\d)\s*estrelas?',
            r'(\d,\d)\s*de\s*5',
            r'(\d\.\d)\s*de\s*5',
            r'(\d,\d)\s*★',
            r'(\d\.\d)\s*★',
            r'★\s*(\d,\d)',
            r'★\s*(\d\.\d)',
            r'(\d,\d)\s*\(\d+\)',  # 4,5 (123)
            r'(\d\.\d)\s*\(\d+\)',  # 4.5 (123)
            r'(\d)\s*estrelas?',    # 5 estrelas
            r'(\d)\s*★',            # 5 ★
            r'★\s*(\d)',            # ★ 5
        ]

        for pattern in rating_patterns:
            match = re.search(pattern, text)
            if match:
                rating_str = match.group(1).replace(',', '.')
                try:
                    rating = float(rating_str)
                    if 0 <= rating <= 5:  # Validação básica
                        return rating
                except:
                    pass

        return None

    def extract_reviews_count(self, text):
        """Extrai número de avaliações do texto"""
        # Procura por padrões de número de avaliações
        reviews_patterns = [
            r'\((\d+)\)\s*avaliações?',
            r'\((\d+)\)\s*reviews?',
            r'(\d+)\s*avaliações?',
            r'(\d+)\s*reviews?',
            r'\((\d+)\)',  # Número entre parênteses após rating
            r'(\d+)\s*opiniões?',
            r'(\d+)\s*comentários?',
        ]

        for pattern in reviews_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    count = int(match.group(1))
                    if count > 0:  # Validação básica
                        return count
                except:
                    pass

        return None

    def extract_address(self, text):
        """Extrai endereço do texto com mais detalhes"""
        # Procura por padrões de endereço mais abrangentes
        address_patterns = [
            # Endereços completos com estado
            r'([A-Z][^,]+,\s*[^,]+,\s*[^,]+\s*-\s*SC)',
            r'([A-Z][^,]+,\s*[^,]+\s*-\s*SC)',
            r'([A-Z][^,]+,\s*[^,]+\s*-\s*Santa\s+Catarina)',

            # Ruas e avenidas
            r'(Rua\s+[^,\n]+(?:,\s*[^,\n]+)*)',
            r'(R\.\s+[^,\n]+(?:,\s*[^,\n]+)*)',
            r'(Av\.\s+[^,\n]+(?:,\s*[^,\n]+)*)',
            r'(Avenida\s+[^,\n]+(?:,\s*[^,\n]+)*)',
            r'(Alameda\s+[^,\n]+(?:,\s*[^,\n]+)*)',
            r'(Travessa\s+[^,\n]+(?:,\s*[^,\n]+)*)',
            r'(Praça\s+[^,\n]+(?:,\s*[^,\n]+)*)',

            # Bairros conhecidos de SC
            r'([^,\n]*(?:Centro|Trindade|Lagoa\s+da\s+Conceição|Canasvieiras|Ingleses|Jurerê|Barra\s+da\s+Lagoa|Campeche|Ribeirão\s+da\s+Ilha|Santo\s+Antônio\s+de\s+Lisboa|Ratones|Cachoeira\s+do\s+Bom\s+Jesus|Sambaqui|Daniela|Ponta\s+das\s+Canas|Lagoinha|Bom\s+Abrigo|Vargem\s+do\s+Bom\s+Jesus|Vargem\s+Grande|Vargem\s+Pequena|Saco\s+Grande|Saco\s+dos\s+Limões|Pantanal|Córrego\s+Grande|Santa\s+Mônica|Itacorubi|João\s+Paulo|Monte\s+Verde|Agronômica|Capoeiras|Cacupé|Balneário|Estreito|Coqueiros|Continente|Kobrasol|Campinas|São\s+Pedro|Barreiros|Abraão|Coloninha|Fazenda|Serraria|Bom\s+Retiro|Joinville|Blumenau|Chapecó|Criciúma|Itajaí|Lages|Balneário\s+Camboriú|São\s+José|Palhoça|Biguaçu|Tijucas|Governador\s+Celso\s+Ramos|Águas\s+Mornas|Santo\s+Amaro\s+da\s+Imperatriz|São\s+Pedro\s+de\s+Alcântara|Antônio\s+Carlos|Angelina|Rancho\s+Queimado|Anitápolis|São\s+Bonifácio|Paulo\s+Lopes|Garopaba|Imbituba|Laguna|Tubarão|Braço\s+do\s+Norte|Orleans|Urussanga|Cocal\s+do\s+Sul|Morro\s+da\s+Fumaça|Forquilhinha|Nova\s+Veneza|Siderópolis|Treviso|Içara|Araranguá|Turvo|Meleiro|Maracajá|Ermo|Jacinto\s+Machado|Morro\s+Grande|Timbé\s+do\s+Sul|Balneário\s+Arroio\s+do\s+Silva|Balneário\s+Gaivota|Passo\s+de\s+Torres|Santa\s+Rosa\s+do\s+Sul|São\s+João\s+do\s+Sul)[^,\n]*)',

            # CEP
            r'([0-9]{5}-?[0-9]{3})',

            # Qualquer coisa que pareça endereço
            r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*\d+)',
        ]

        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                # Remove caracteres indesejados
                address = re.sub(r'[^\w\s,.-]', '', address)
                if len(address) > 10:  # Filtro básico de tamanho
                    return address

        return None

    def closed(self, reason):
        """Callback quando spider termina"""
        self.logger.info(f"🔧 BORRACHARIA RESUMABLE SPIDER FINALIZADO - Motivo: {reason}")
        self.logger.info(f"📊 BORRACHARIA_RESUMABLE_STATS: {{'status': 'finished', 'reason': '{reason}', 'timestamp': '{datetime.now().isoformat()}'}}")
