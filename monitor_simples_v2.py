#!/usr/bin/env python3
"""
Monitor simples que funciona
"""

import json
import os
import time
import re
from datetime import datetime

def main():
    print("🚀 MONITOR DE PROGRESSO - INICIANDO...")
    print("=" * 60)
    
    contador = 0
    
    while True:
        try:
            contador += 1
            
            print(f"\n📊 ATUALIZAÇÃO #{contador} - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            
            # 1. Dados salvos no JSON
            establishments = []
            try:
                if os.path.exists('output/fuel_stations_monitored.json'):
                    with open('output/fuel_stations_monitored.json', 'r', encoding='utf-8') as f:
                        establishments = json.load(f)
                
                phones_count = sum(1 for est in establishments if est.get('phone'))
                phone_rate = (phones_count / len(establishments) * 100) if establishments else 0
                
                print(f"💾 DADOS SALVOS:")
                print(f"   🏪 {len(establishments)} estabelecimentos")
                print(f"   📞 {phones_count} telefones ({phone_rate:.1f}%)")
                
            except Exception as e:
                print(f"💾 DADOS SALVOS: Erro - {e}")
            
            # 2. Progresso nos logs
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
                    
                    print(f"📄 PROGRESSO:")
                    print(f"   🗺️ Célula {current_cell + 1}/7904 ({(current_cell + 1)/7904*100:.1f}%)")
                    print(f"   📊 {log_count} estabelecimentos nos logs")
                    
                else:
                    print(f"📄 PROGRESSO: Log não encontrado")
                    
            except Exception as e:
                print(f"📄 PROGRESSO: Erro - {e}")
            
            # 3. Últimos estabelecimentos
            if establishments:
                print(f"\n🏪 ÚLTIMOS 3 ESTABELECIMENTOS:")
                for i, est in enumerate(establishments[-3:], 1):
                    name = est.get('name', 'N/A')
                    phone = est.get('phone', 'Sem telefone')
                    rating = est.get('rating', 'N/A')
                    print(f"   {i}. {name}")
                    print(f"      📞 {phone}")
                    print(f"      ⭐ {rating}")
            
            print(f"\n🔄 Próxima atualização em 30 segundos...")
            print("=" * 60)
            
            # Aguarda 30 segundos
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor interrompido")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
