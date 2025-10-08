#!/usr/bin/env python3
"""
Monitor simples de progresso - atualiza a cada 30 segundos
"""

import time
import json
import os
from datetime import datetime

def monitor_progress():
    """Monitor simples de progresso"""
    print("🌐 MONITOR DE PROGRESSO - SPIDER VPN")
    print("=" * 60)
    print("📊 Atualizações a cada 30 segundos")
    print("💡 Pressione Ctrl+C para parar")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            elapsed_str = f"{int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}"
            
            # Lê dados salvos
            establishments = []
            try:
                if os.path.exists('output/fuel_stations_monitored.json'):
                    with open('output/fuel_stations_monitored.json', 'r', encoding='utf-8') as f:
                        establishments = json.load(f)
            except:
                pass
            
            # Lê progresso do log
            current_cell = 0
            pages_crawled = 0
            
            try:
                if os.path.exists('output/scrapy.log'):
                    with open('output/scrapy.log', 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Última célula processada
                        lines = content.split('\n')
                        for line in reversed(lines):
                            if '🔍 Processando célula' in line:
                                try:
                                    cell_num = int(line.split('célula ')[1].split(':')[0])
                                    current_cell = cell_num
                                    break
                                except:
                                    pass
                        
                        # Páginas processadas
                        for line in reversed(lines):
                            if 'Crawled' in line and 'pages' in line:
                                try:
                                    import re
                                    match = re.search(r'Crawled (\d+) pages', line)
                                    if match:
                                        pages_crawled = int(match.group(1))
                                        break
                                except:
                                    pass
            except:
                pass
            
            # Conta telefones
            phones_count = 0
            for est in establishments:
                if est.get('phone'):
                    phones_count += 1
            
            # Calcula taxa de telefones
            phone_rate = (phones_count / len(establishments) * 100) if establishments else 0
            
            # Calcula taxa de páginas
            page_rate = pages_crawled / (elapsed_time / 60) if elapsed_time > 0 else 0
            
            # Mostra status
            print(f"\n⏰ {elapsed_str} | "
                  f"🗺️ Célula {current_cell}/7904 | "
                  f"🏪 {len(establishments)} estabelecimentos | "
                  f"📞 {phones_count} telefones ({phone_rate:.1f}%)")
            
            print(f"📊 {pages_crawled} páginas | "
                  f"⚡ {page_rate:.1f} pág/min | "
                  f"🌐 VPN ativo")
            
            # Mostra últimos estabelecimentos
            if len(establishments) > 0:
                print("📋 Últimos coletados:")
                for est in establishments[-3:]:
                    name = est.get('name', 'N/A')[:25]
                    phone = est.get('phone', 'Sem telefone')
                    rating = est.get('rating', 'N/A')
                    print(f"   🏪 {name} | 📞 {phone} | ⭐ {rating}")
            
            time.sleep(30)  # Aguarda 30 segundos
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitor interrompido")
        print(f"📊 Total coletado: {len(establishments)} estabelecimentos")
        print(f"📞 Total telefones: {phones_count}")

if __name__ == "__main__":
    monitor_progress()
