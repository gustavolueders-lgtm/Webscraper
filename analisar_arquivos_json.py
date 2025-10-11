#!/usr/bin/env python3
"""
Analisa todos os arquivos JSON para explicar as diferenças
"""

import os
import json
from datetime import datetime

def analisar_arquivos():
    """Analisa todos os arquivos JSON"""
    
    files = [
        'fuel_stations.json',
        'fuel_stations_auto_backup.json', 
        'fuel_stations_auto_complete.json',
        'fuel_stations_backup.json',
        'fuel_stations_complete.json',
        'fuel_stations_complete_backup.json'
    ]

    print('📊 ANÁLISE DETALHADA DOS ARQUIVOS JSON')
    print('=' * 60)

    for filename in files:
        filepath = f'output/{filename}'
        if os.path.exists(filepath):
            try:
                # Get file info
                stat = os.stat(filepath)
                size_mb = stat.st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                # Get JSON info
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    count = len(data) if isinstance(data, list) else 'N/A'
                
                # Count establishments with phone
                phone_count = 0
                if isinstance(data, list):
                    phone_count = sum(1 for item in data if item.get('phone'))
                
                print(f'📁 {filename}')
                print(f'   📊 Estabelecimentos: {count}')
                print(f'   📞 Com telefone: {phone_count}')
                if count != 'N/A' and count > 0:
                    phone_pct = (phone_count / count) * 100
                    print(f'   📈 Taxa telefones: {phone_pct:.1f}%')
                print(f'   💾 Tamanho: {size_mb:.1f} MB')
                print(f'   ⏰ Modificado: {modified.strftime("%d/%m/%Y %H:%M:%S")}')
                
                # Show sample data
                if isinstance(data, list) and len(data) > 0:
                    sample = data[0]
                    print(f'   🏪 Exemplo: {sample.get("name", "N/A")}')
                    if sample.get('phone'):
                        print(f'   📞 Tel exemplo: {sample.get("phone")}')
                
                print()
                
            except Exception as e:
                print(f'❌ {filename}: Erro - {e}')
                print()
        else:
            print(f'❌ {filename}: Arquivo não encontrado')
            print()
    
    # Explain each file
    print('\n📋 EXPLICAÇÃO DE CADA ARQUIVO:')
    print('=' * 60)
    
    explanations = {
        'fuel_stations.json': '🏭 PIPELINE SCRAPY - Arquivo oficial do pipeline do Scrapy (pode estar desatualizado)',
        'fuel_stations_auto_backup.json': '💾 BACKUP AUTOMÁTICO - Backup do sistema de salvamento automático definitivo',
        'fuel_stations_auto_complete.json': '🚀 SALVAMENTO AUTOMÁTICO - Arquivo principal do sistema automático (MAIS ATUAL)',
        'fuel_stations_backup.json': '📦 BACKUP MANUAL - Backup criado durante recuperação manual de dados',
        'fuel_stations_complete.json': '🔍 RECUPERAÇÃO COMPLETA - Dados recuperados dos logs (versão agressiva)',
        'fuel_stations_complete_backup.json': '💾 BACKUP RECUPERAÇÃO - Backup da recuperação completa'
    }
    
    for filename, explanation in explanations.items():
        print(f'{explanation}')
        if os.path.exists(f'output/{filename}'):
            print(f'   ✅ Existe')
        else:
            print(f'   ❌ Não existe')
        print()

if __name__ == "__main__":
    analisar_arquivos()
