#!/usr/bin/env python3
"""
Verifica o status atual do sistema
"""

import json
import os
from datetime import datetime

def verificar_status():
    """Verifica o status atual do sistema"""
    log_file = 'output/scrapy.log'
    json_file = 'output/fuel_stations_monitored.json'
    
    # Count establishments in logs
    log_count = 0
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '🏪 ESTABLISHMENT_DATA:' in line:
                    log_count += 1
    
    # Count establishments in JSON
    json_count = 0
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            json_count = len(data)
    
    print(f'📊 STATUS ATUAL - {datetime.now().strftime("%H:%M:%S")}')
    print(f'📖 Estabelecimentos nos logs: {log_count}')
    print(f'💾 Estabelecimentos salvos: {json_count}')
    print(f'📉 Diferença: {log_count - json_count}')
    
    if log_count > 0:
        taxa = (json_count/log_count*100)
        print(f'📈 Taxa de salvamento: {taxa:.1f}%')
        
        if taxa < 90:
            print(f'⚠️ ATENÇÃO: Taxa de salvamento baixa!')
            print(f'🔧 Recomendação: Execute recuperar_dados_perdidos.py')
        else:
            print(f'✅ Taxa de salvamento boa!')
    else:
        print(f'📈 Taxa de salvamento: 0%')
    
    # Show latest establishments
    if json_count > 0:
        print(f'\n🏪 ÚLTIMOS 3 ESTABELECIMENTOS SALVOS:')
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for i, est in enumerate(data[-3:], 1):
                name = est.get('name', 'N/A')
                phone = est.get('phone', 'Sem telefone')
                rating = est.get('rating', 'N/A')
                print(f'   {i}. {name}')
                print(f'      📞 {phone}')
                print(f'      ⭐ {rating}')

if __name__ == "__main__":
    verificar_status()
