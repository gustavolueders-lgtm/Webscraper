#!/usr/bin/env python3
"""
Verifica status da coleta de borracharias
"""

import json
import os
from datetime import datetime

def verificar_status():
    """Verifica status da coleta"""
    
    print("🔧 STATUS DA COLETA DE BORRACHARIAS")
    print("=" * 60)
    
    # Arquivos para verificar
    arquivos = {
        'tire_shops_auto_complete.json': 'Arquivo principal (salvamento automático)',
        'tire_shops_auto_backup.json': 'Arquivo de backup',
        'scrapy.log': 'Log do scraper'
    }
    
    # Verificar arquivos
    for arquivo, descricao in arquivos.items():
        caminho = f'output/{arquivo}'
        
        if os.path.exists(caminho):
            stat = os.stat(caminho)
            size_mb = stat.st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"✅ {arquivo}")
            print(f"   📝 {descricao}")
            print(f"   💾 Tamanho: {size_mb:.1f} MB")
            print(f"   ⏰ Modificado: {modified.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Se é arquivo JSON, contar estabelecimentos
            if arquivo.endswith('.json'):
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        count = len(data) if isinstance(data, list) else 0
                        
                        # Contar com telefone
                        with_phone = sum(1 for item in data if item.get('phone')) if isinstance(data, list) else 0
                        
                        print(f"   📊 Borracharias: {count:,}")
                        print(f"   📞 Com telefone: {with_phone:,}")
                        if count > 0:
                            print(f"   📈 Taxa telefones: {(with_phone/count)*100:.1f}%")
                        
                        # Mostrar amostra
                        if isinstance(data, list) and len(data) > 0:
                            sample = data[0]
                            print(f"   🏪 Exemplo: {sample.get('name', 'N/A')}")
                
                except Exception as e:
                    print(f"   ❌ Erro ao ler JSON: {e}")
            
            print()
        else:
            print(f"❌ {arquivo}")
            print(f"   📝 {descricao}")
            print(f"   ⚠️ Arquivo não encontrado")
            print()
    
    # Verificar logs para estatísticas
    log_file = 'output/scrapy.log'
    if os.path.exists(log_file):
        print("📊 ESTATÍSTICAS DOS LOGS:")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Contar linhas relevantes
            tire_shop_data_lines = sum(1 for line in lines if 'TIRE_SHOP_DATA:' in line)
            spider_stats_lines = sum(1 for line in lines if 'TIRE_SPIDER_STATS:' in line)
            error_lines = sum(1 for line in lines if 'ERROR' in line.upper())
            
            print(f"   📝 Total de linhas: {len(lines):,}")
            print(f"   🔧 Borracharias nos logs: {tire_shop_data_lines:,}")
            print(f"   📊 Estatísticas do spider: {spider_stats_lines}")
            print(f"   ❌ Linhas de erro: {error_lines}")
            
            # Verificar se spider está rodando
            recent_lines = lines[-50:] if len(lines) > 50 else lines
            recent_activity = any('TIRE_SHOP_DATA:' in line for line in recent_lines)
            
            if recent_activity:
                print(f"   ✅ Spider aparenta estar ativo")
            else:
                print(f"   ⚠️ Nenhuma atividade recente detectada")
            
        except Exception as e:
            print(f"   ❌ Erro ao analisar logs: {e}")
        
        print()
    
    # Comparar dados salvos vs logs e calcular progresso do grid
    json_file = 'output/tire_shops_auto_complete.json'
    if os.path.exists(json_file) and os.path.exists(log_file):
        try:
            # Contar no JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                json_count = len(json_data) if isinstance(json_data, list) else 0

            # Contar nos logs
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                log_count = log_content.count('TIRE_SHOP_DATA:')

            print("🔄 COMPARAÇÃO LOGS vs DADOS SALVOS:")
            print(f"   📊 Borracharias nos logs: {log_count:,}")
            print(f"   💾 Borracharias salvas: {json_count:,}")

            if log_count > 0:
                save_rate = (json_count / log_count) * 100
                print(f"   📈 Taxa de salvamento: {save_rate:.1f}%")

                if save_rate < 90:
                    print(f"   ⚠️ Taxa de salvamento baixa - verificar sistema automático")
                else:
                    print(f"   ✅ Taxa de salvamento boa")

            # Calcular progresso do grid
            if isinstance(json_data, list) and len(json_data) > 0:
                print()
                print("📍 PROGRESSO DO GRID:")

                # Extrair cell_index dos dados
                cell_indices = set()
                for item in json_data:
                    cell_index = item.get('cell_index')
                    if cell_index is not None:
                        cell_indices.add(cell_index)

                # Calcular total de células (mesmo cálculo do spider)
                GRID_SIZE_KM = 5
                LAT_MIN, LAT_MAX = -29.35, -25.95
                LON_MIN, LON_MAX = -53.83, -48.35

                lat_step = GRID_SIZE_KM / 111.0
                lon_step = GRID_SIZE_KM / (111.0 * 0.85)

                lat_cells = int((LAT_MAX - LAT_MIN) / lat_step) + 1
                lon_cells = int((LON_MAX - LON_MIN) / lon_step) + 1
                total_cells = lat_cells * lon_cells

                processed_cells = len(cell_indices)
                progress_percent = (processed_cells / total_cells * 100) if total_cells > 0 else 0

                print(f"   🗺️ Células processadas: {processed_cells:,}")
                print(f"   📊 Total de células: {total_cells:,}")
                print(f"   📈 Progresso: {progress_percent:.2f}%")

                if processed_cells > 0:
                    max_cell = max(cell_indices)
                    min_cell = min(cell_indices)
                    print(f"   🔢 Células: {min_cell} a {max_cell}")

        except Exception as e:
            print(f"   ❌ Erro na comparação: {e}")

if __name__ == "__main__":
    verificar_status()
