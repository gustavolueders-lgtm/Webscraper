#!/usr/bin/env python3
"""
Mostra status atual do scraping
"""

import json
import os
import re
from datetime import datetime

def main():
    print("📊 STATUS ATUAL DO SCRAPING")
    print("=" * 50)
    
    # 1. Verifica dados salvos
    try:
        if os.path.exists('output/fuel_stations_monitored.json'):
            with open('output/fuel_stations_monitored.json', 'r', encoding='utf-8') as f:
                establishments = json.load(f)
            
            phones_count = sum(1 for est in establishments if est.get('phone'))
            phone_rate = (phones_count / len(establishments) * 100) if establishments else 0
            
            print(f"💾 DADOS SALVOS NO JSON:")
            print(f"   🏪 {len(establishments)} estabelecimentos")
            print(f"   📞 {phones_count} telefones ({phone_rate:.1f}%)")
            
            # Mostra últimos 3
            if establishments:
                print(f"\n🏪 ÚLTIMOS 3 ESTABELECIMENTOS:")
                for i, est in enumerate(establishments[-3:], 1):
                    name = est.get('name', 'N/A')
                    phone = est.get('phone', 'Sem telefone')
                    rating = est.get('rating', 'N/A')
                    print(f"   {i}. {name}")
                    print(f"      📞 {phone}")
                    print(f"      ⭐ {rating}")
        else:
            print("💾 DADOS SALVOS: Arquivo JSON não encontrado")
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}")
    
    print("\n" + "=" * 50)
    
    # 2. Verifica progresso nos logs
    try:
        if os.path.exists('output/scrapy.log'):
            with open('output/scrapy.log', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Conta estabelecimentos nos logs
            establishment_matches = re.findall(r'🏪 ESTABLISHMENT_DATA:', content)
            log_count = len(establishment_matches)
            
            # Procura por células processadas
            cell_matches = re.findall(r'cell_index["\']:\s*(\d+)', content)
            current_cell = max(int(x) for x in cell_matches) if cell_matches else 0
            
            # Conta páginas crawladas
            page_matches = re.findall(r'Crawled \(\d+\)', content)
            pages_crawled = len(page_matches)
            
            print(f"📄 PROGRESSO NOS LOGS:")
            print(f"   🏪 {log_count} estabelecimentos extraídos")
            print(f"   🗺️ Célula {current_cell + 1}/7904 ({(current_cell + 1)/7904*100:.1f}%)")
            print(f"   📄 {pages_crawled} páginas processadas")
            
        else:
            print("📄 LOGS: Arquivo de log não encontrado")
    except Exception as e:
        print(f"❌ Erro ao ler logs: {e}")
    
    print("\n" + "=" * 50)
    
    # 3. Status dos processos
    print(f"🔄 PROCESSOS ATIVOS:")
    print(f"   🕷️ Spider: Terminal 49 (verificar se ainda está rodando)")
    print(f"   📊 Monitor: Terminal 54 (monitor em tempo real)")
    
    print(f"\n📍 ARQUIVOS IMPORTANTES:")
    print(f"   💾 Dados: output/fuel_stations_monitored.json")
    print(f"   📄 Logs: output/scrapy.log")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"   1. Verificar se spider ainda está rodando")
    print(f"   2. Aguardar mais dados serem coletados")
    print(f"   3. Monitor deve atualizar a cada 30 segundos")

if __name__ == "__main__":
    main()
