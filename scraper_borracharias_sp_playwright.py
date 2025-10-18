#!/usr/bin/env python3
"""
Scraper de borracharias para São Paulo usando Playwright
"""

import asyncio
import json
import os
import re
import random
import time
import glob
from datetime import datetime
from playwright.async_api import async_playwright

class BorrachariaSaoPauloPlaywright:
    def __init__(self, start_cell=0, max_cells=50):
        self.start_cell = start_cell
        self.max_cells = max_cells
        self.establishments_found = 0
        self.cells_processed = 0
        self.seen_establishments = set()
        
        # Configuração de grid - São Paulo COMPLETO
        self.GRID_SIZE_KM = 5
        self.LAT_MIN, self.LAT_MAX = -25.3, -19.8
        self.LON_MIN, self.LON_MAX = -53.1, -44.2
        self.SEARCH_TERMS = ["borracharia", "pneus"]
        
        # Criar diretórios
        os.makedirs('output', exist_ok=True)
        os.makedirs('output/cells', exist_ok=True)
        
        print(f"SCRAPER BORRACHARIAS SP PLAYWRIGHT INICIADO")
        print(f"Comecando da celula: {self.start_cell}")
        print(f"Maximo de celulas: {self.max_cells}")
    
    def calculate_grid(self):
        """Calcula o grid de células"""
        lat_step = self.GRID_SIZE_KM / 111.0
        lon_step = self.GRID_SIZE_KM / (111.0 * 0.85)
        
        cells = []
        lat = self.LAT_MIN
        while lat <= self.LAT_MAX:
            lon = self.LON_MIN
            while lon <= self.LON_MAX:
                cells.append((lat, lon))
                lon += lon_step
            lat += lat_step
        
        return cells
    
    async def extract_establishments(self, page, cell_index, cell_lat, cell_lon, search_term):
        """Extrai estabelecimentos de uma página do Google Maps"""
        establishments = []
        
        try:
            # Aguardar carregamento
            await page.wait_for_timeout(3000)
            
            # Tentar aguardar pelos resultados
            try:
                await page.wait_for_selector('div[role="feed"]', timeout=10000)
            except:
                print(f"  Timeout aguardando resultados para {search_term}")
            
            # Aguardar mais um pouco para garantir carregamento
            await page.wait_for_timeout(2000)
            
            # Extrair estabelecimentos usando diferentes estratégias
            selectors = [
                'div[role="feed"] div[data-result-index]',
                'div[role="feed"] > div > div[role="article"]',
                'div[data-result-index]',
                'div[role="article"]',
                'a[data-cid]'
            ]

            results = []
            for selector in selectors:
                try:
                    results = await page.query_selector_all(selector)
                    if results and len(results) > 2:  # Filtrar resultados muito poucos
                        print(f"  Encontrados {len(results)} elementos com seletor: {selector}")
                        break
                except:
                    continue
            
            # Se não encontrou com seletores, tentar extrair do HTML
            if not results:
                content = await page.content()
                # Procurar por padrões no HTML que indiquem estabelecimentos
                name_patterns = [
                    r'"([^"]*(?:borracharia|pneu|auto center)[^"]*)"',
                    r'aria-label="([^"]*(?:borracharia|pneu|auto center)[^"]*)"'
                ]
                
                found_names = set()
                for pattern in name_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    found_names.update(matches)
                
                if found_names:
                    print(f"  Encontrados {len(found_names)} nomes no HTML")
                    for i, name in enumerate(list(found_names)[:10]):  # Máximo 10
                        establishments.append({
                            'name': name.strip(),
                            'cell_index': cell_index,
                            'cell_lat': cell_lat,
                            'cell_lon': cell_lon,
                            'search_term': search_term,
                            'found_at': datetime.now().isoformat(),
                            'source': 'html_pattern',
                            'establishment_index': i
                        })
            else:
                # Processar resultados encontrados com seletores
                for i, result in enumerate(results[:20]):  # Máximo 20
                    try:
                        # Tentar extrair nome e telefone
                        name_selectors = [
                            'div[class*="fontHeadlineSmall"]',
                            'div[class*="fontBodyMedium"]',
                            'h3',
                            'a[data-cid] div',
                            'div[class*="title"]',
                            'span[class*="name"]',
                            '[aria-label*="borracharia"]',
                            '[aria-label*="pneu"]'
                        ]

                        phone_selectors = [
                            'span[class*="fontBodyMedium"]',
                            'div[class*="fontBodyMedium"]',
                            'span[class*="fontCaption"]',
                            'div[class*="fontCaption"]',
                            '[data-value*="tel:"]',
                            'a[href*="tel:"]',
                            'span',
                            'div'
                        ]
                        
                        name = None
                        phone = None

                        # Extrair nome
                        for name_sel in name_selectors:
                            try:
                                name_element = await result.query_selector(name_sel)
                                if name_element:
                                    name = await name_element.inner_text()
                                    if name and name.strip():
                                        break
                            except:
                                continue

                        if not name:
                            # Tentar pegar aria-label
                            try:
                                name = await result.get_attribute('aria-label')
                            except:
                                pass

                        # Extrair telefone - buscar em todo o elemento
                        try:
                            element_html = await result.inner_html()
                            element_text = await result.inner_text()

                            # Buscar padrões de telefone no texto e HTML
                            phone_patterns = [
                                r'\(\d{2}\)\s*\d{4,5}-?\d{4}',  # (11) 99999-9999
                                r'\d{2}\s*\d{4,5}-?\d{4}',      # 11 99999-9999
                                r'\(\d{2}\)\s*\d{8,9}',        # (11) 999999999
                                r'\d{10,11}'                   # 11999999999
                            ]

                            for pattern in phone_patterns:
                                phone_match = re.search(pattern, element_text)
                                if phone_match:
                                    phone = phone_match.group()
                                    break

                            if not phone:
                                for pattern in phone_patterns:
                                    phone_match = re.search(pattern, element_html)
                                    if phone_match:
                                        phone = phone_match.group()
                                        break
                        except:
                            pass



                        if name and name.strip():
                            establishment = {
                                'name': name.strip(),
                                'phone': phone.strip() if phone else None,
                                'cell_index': cell_index,
                                'cell_lat': cell_lat,
                                'cell_lon': cell_lon,
                                'search_term': search_term,
                                'found_at': datetime.now().isoformat(),
                                'source': 'selector',
                                'establishment_index': i
                            }
                            establishments.append(establishment)
                    
                    except Exception as e:
                        print(f"  Erro ao processar resultado {i}: {e}")
            
        except Exception as e:
            print(f"  Erro geral na extração: {e}")
        
        return establishments
    
    async def process_cell(self, browser, cell_index, cell_lat, cell_lon):
        """Processa uma célula do grid"""
        print(f"Processando celula {cell_index}: {cell_lat:.4f}, {cell_lon:.4f}")
        
        all_establishments = []
        
        for search_term in self.SEARCH_TERMS:
            try:
                print(f"  Buscando: {search_term}")
                
                # Criar nova página
                page = await browser.new_page()
                
                # Configurar user agent
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # URL do Google Maps
                url = f"https://www.google.com/maps/search/{search_term}/@{cell_lat},{cell_lon},15z"
                
                # Navegar para a página
                await page.goto(url, wait_until='networkidle')
                
                # Extrair estabelecimentos
                establishments = await self.extract_establishments(page, cell_index, cell_lat, cell_lon, search_term)
                
                # Filtrar duplicatas
                for est in establishments:
                    est_key = f"{est['name']}_{cell_lat:.4f}_{cell_lon:.4f}"
                    if est_key not in self.seen_establishments:
                        self.seen_establishments.add(est_key)
                        all_establishments.append(est)
                        self.establishments_found += 1
                
                print(f"  Encontrados: {len(establishments)} estabelecimentos")
                
                # Salvar resultado da célula/termo
                cell_result = {
                    'timestamp': datetime.now().isoformat(),
                    'cell_index': cell_index,
                    'cell_lat': cell_lat,
                    'cell_lon': cell_lon,
                    'search_term': search_term,
                    'url': url,
                    'establishments_found': len(establishments),
                    'establishments': establishments
                }
                
                filename = f'output/cells/cell_{cell_index}_{search_term}.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(cell_result, f, ensure_ascii=False, indent=2)
                
                # Fechar página
                await page.close()
                
                # Pausa entre termos
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"  Erro ao processar {search_term}: {e}")
        
        self.cells_processed += 1
        print(f"Celula {cell_index} concluida: {len(all_establishments)} estabelecimentos")
        print(f"Total encontrado ate agora: {self.establishments_found}")
        
        # Salvar progresso
        self.save_progress()
        
        return all_establishments
    
    def save_progress(self):
        """Salva progresso geral"""
        now = datetime.now()
        progress = {
            'timestamp': now.isoformat(),
            'cells_processed': self.cells_processed,  # Apenas células realmente processadas
            'establishments_found': len(self.seen_establishments),  # Usar contagem real
            'start_cell': self.start_cell,
            'max_cells': self.max_cells,
            'current_cell': self.cells_processed + self.start_cell
        }

        with open('output/progress.json', 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

        # Salvar dados consolidados
        self.save_consolidated_data()

        # Indicador periódico no terminal
        total_cells = 20664  # Total de células em SP
        current_cell = self.cells_processed + self.start_cell
        progress_percent = (self.cells_processed / total_cells) * 100  # Usar apenas células realmente processadas

        print(f"\n{'='*60}")
        print(f"📊 PROGRESSO AUTOMATICO - {now.strftime('%H:%M:%S')}")
        print(f"📍 Celulas processadas: {self.cells_processed:,} / {total_cells:,} ({progress_percent:.2f}%)")
        print(f"📍 Celula atual: {current_cell:,}")
        print(f"🏢 Contatos unicos: {len(self.seen_establishments):,}")
        print(f"💾 Salvamento: output/tire_shops_auto_complete.json")
        print(f"{'='*60}\n")

    def save_consolidated_data(self):
        """Salva dados consolidados em formato compatível com sistema anterior"""
        try:
            # Coletar todos os estabelecimentos únicos
            all_establishments = []

            # Ler todos os arquivos de células
            cell_files = glob.glob('output/cells/cell_*.json')

            seen_keys = set()
            for file_path in cell_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    establishments = data.get('establishments', [])
                    for est in establishments:
                        # Criar chave única
                        name = est.get('name', '').strip()
                        if not name or len(name) < 3:
                            continue

                        # Filtrar HTML mal extraído
                        if any(x in name.lower() for x in ['<title>', '<meta', 'google maps', 'acessar o site']):
                            continue

                        lat = est.get('cell_lat', 0)
                        lon = est.get('cell_lon', 0)

                        unique_key = f"{name}_{lat:.4f}_{lon:.4f}"

                        if unique_key not in seen_keys:
                            seen_keys.add(unique_key)

                            # Formato compatível
                            establishment = {
                                'name': name,
                                'phone': est.get('phone', None),
                                'latitude': lat,
                                'longitude': lon,
                                'search_term': est.get('search_term', ''),
                                'cell_index': est.get('cell_index', 0),
                                'found_at': est.get('found_at', ''),
                                'source': 'playwright_scraper'
                            }
                            all_establishments.append(establishment)

                except Exception as e:
                    continue

            # Salvar arquivo consolidado
            output_file = 'output/tire_shops_auto_complete.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_establishments, f, ensure_ascii=False, indent=2)

            # Backup
            backup_file = 'output/tire_shops_auto_backup.json'
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(all_establishments, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Erro ao salvar dados consolidados: {e}")

    async def run(self):
        """Executa o scraper"""
        print("Calculando grid de Sao Paulo...")
        
        cells = self.calculate_grid()
        total_cells = len(cells)
        end_cell = min(self.start_cell + self.max_cells, total_cells)
        
        print(f"Total de celulas em SP: {total_cells}")
        print(f"Processando celulas {self.start_cell} a {end_cell-1}")
        
        async with async_playwright() as p:
            # Iniciar browser
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                # Processar células
                for i, (lat, lon) in enumerate(cells[self.start_cell:end_cell], start=self.start_cell):
                    await self.process_cell(browser, i, lat, lon)
                    
                    # Pausa entre células
                    if i < end_cell - 1:
                        pause_time = random.uniform(5, 10)
                        print(f"Pausa de {pause_time:.1f}s...")
                        await asyncio.sleep(pause_time)
                
            finally:
                await browser.close()
        
        print("Processo concluido!")
        print(f"Total de estabelecimentos encontrados: {self.establishments_found}")

async def main():
    import sys
    
    start_cell = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    max_cells = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    scraper = BorrachariaSaoPauloPlaywright(start_cell, max_cells)
    await scraper.run()

if __name__ == '__main__':
    asyncio.run(main())
