#!/usr/bin/env python3
"""
Analisa diferença de tamanho entre arquivos JSON
"""

import os
import json

def analisar_tamanhos():
    """Analisa tamanho dos arquivos"""
    
    files = ['output/fuel_stations.json', 'output/fuel_stations_auto_complete.json']

    print('📊 ANÁLISE DE TAMANHO DOS ARQUIVOS')
    print('=' * 50)

    for filepath in files:
        if os.path.exists(filepath):
            size_bytes = os.path.getsize(filepath)
            size_kb = size_bytes / 1024
            size_mb = size_bytes / (1024 * 1024)
            
            # Load and analyze data
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = len(data)
            
            # Calculate average size per record
            avg_bytes_per_record = size_bytes / count if count > 0 else 0
            
            print(f'📁 {os.path.basename(filepath)}')
            print(f'   📊 Estabelecimentos: {count:,}')
            print(f'   💾 Tamanho: {size_kb:,.0f} KB ({size_mb:.1f} MB)')
            print(f'   📏 Bytes por registro: {avg_bytes_per_record:.0f}')
            
            # Sample first record to see structure
            if data:
                sample = data[0]
                print(f'   🔍 Campos no primeiro registro: {len(sample)}')
                print(f'   📝 Campos: {list(sample.keys())}')
                
                # Check for large fields
                large_fields = []
                for key, value in sample.items():
                    if isinstance(value, str) and len(value) > 100:
                        large_fields.append(f'{key}: {len(value)} chars')
                
                if large_fields:
                    print(f'   📏 Campos grandes: {large_fields}')
            print()

if __name__ == "__main__":
    analisar_tamanhos()
