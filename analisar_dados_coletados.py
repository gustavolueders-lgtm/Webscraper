#!/usr/bin/env python3
"""
Script para analisar os dados coletados e descobrir o problema
"""

import os
import json
import glob
from collections import defaultdict

def analisar_dados():
    print("🔍 ANÁLISE DOS DADOS COLETADOS")
    print("=" * 60)
    
    # Contar arquivos
    cell_files = glob.glob('output/cells/cell_*.json')
    print(f"📁 Total de arquivos: {len(cell_files)}")
    
    # Analisar por tipo de busca
    stats = defaultdict(lambda: {'files': 0, 'establishments': 0, 'cells': set()})
    
    total_establishments = 0
    cells_with_data = set()
    
    for file_path in cell_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            search_term = data.get('search_term', 'unknown')
            cell_index = data.get('cell_index', 0)
            establishments_count = data.get('establishments_found', 0)
            
            stats[search_term]['files'] += 1
            stats[search_term]['establishments'] += establishments_count
            stats[search_term]['cells'].add(cell_index)
            
            total_establishments += establishments_count
            
            if establishments_count > 0:
                cells_with_data.add(cell_index)
                
        except Exception as e:
            print(f"❌ Erro ao ler {file_path}: {e}")
    
    print(f"\n📊 ESTATÍSTICAS POR TERMO:")
    for term, data in stats.items():
        unique_cells = len(data['cells'])
        print(f"  🔍 {term}:")
        print(f"    📁 Arquivos: {data['files']}")
        print(f"    📍 Células únicas: {unique_cells}")
        print(f"    🏢 Estabelecimentos: {data['establishments']}")
        if unique_cells > 0:
            print(f"    📊 Média por célula: {data['establishments']/unique_cells:.2f}")
    
    print(f"\n🎯 RESUMO GERAL:")
    print(f"  📁 Total de arquivos: {len(cell_files)}")
    print(f"  🏢 Total de estabelecimentos: {total_establishments}")
    print(f"  📍 Células com dados: {len(cells_with_data)}")
    
    # Analisar células específicas
    print(f"\n🔍 ANÁLISE DE CÉLULAS:")
    
    # Encontrar maior número de célula
    max_cell = 0
    min_cell = float('inf')
    for term_data in stats.values():
        if term_data['cells']:
            max_cell = max(max_cell, max(term_data['cells']))
            min_cell = min(min_cell, min(term_data['cells']))
    
    print(f"  📍 Célula mínima: {min_cell}")
    print(f"  📍 Célula máxima: {max_cell}")
    print(f"  📊 Range de células: {max_cell - min_cell + 1}")
    
    # Verificar se realmente processamos 10.000 células
    all_cells = set()
    for term_data in stats.values():
        all_cells.update(term_data['cells'])
    
    print(f"  📍 Células únicas processadas: {len(all_cells)}")
    
    # Analisar algumas células específicas
    print(f"\n📋 AMOSTRAS DE CÉLULAS:")
    sample_cells = sorted(list(all_cells))[:5] + sorted(list(all_cells))[-5:]
    
    for cell_id in sample_cells:
        print(f"\n  📍 Célula {cell_id}:")
        for term in ['borracharia', 'pneus']:
            file_path = f'output/cells/cell_{cell_id}_{term}.json'
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    lat = data.get('cell_lat', 0)
                    lon = data.get('cell_lon', 0)
                    establishments = data.get('establishments_found', 0)
                    
                    print(f"    🔍 {term}: {establishments} estabelecimentos")
                    print(f"    📍 Coordenadas: {lat:.4f}, {lon:.4f}")
                    
                    # Mostrar alguns estabelecimentos se houver
                    if establishments > 0 and 'establishments' in data:
                        for i, est in enumerate(data['establishments'][:2]):
                            name = est.get('name', 'N/A')
                            print(f"      🏢 {i+1}: {name}")
                            
                except Exception as e:
                    print(f"    ❌ Erro: {e}")
    
    # Verificar progresso reportado vs real
    print(f"\n⚠️ VERIFICAÇÃO DE INCONSISTÊNCIAS:")
    
    try:
        with open('output/progress.json', 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        reported_cells = progress.get('cells_processed', 0)
        reported_establishments = progress.get('establishments_found', 0)
        
        print(f"  📊 Progresso reportado:")
        print(f"    📍 Células: {reported_cells}")
        print(f"    🏢 Estabelecimentos: {reported_establishments}")
        
        print(f"  📊 Dados reais:")
        print(f"    📍 Células: {len(all_cells)}")
        print(f"    🏢 Estabelecimentos: {total_establishments}")
        
        if reported_cells != len(all_cells):
            print(f"  ⚠️ INCONSISTÊNCIA: Células reportadas ({reported_cells}) != células reais ({len(all_cells)})")
        
        if reported_establishments != total_establishments:
            print(f"  ⚠️ INCONSISTÊNCIA: Estabelecimentos reportados ({reported_establishments}) != reais ({total_establishments})")
            
    except Exception as e:
        print(f"  ❌ Erro ao ler progress.json: {e}")

if __name__ == '__main__':
    analisar_dados()
