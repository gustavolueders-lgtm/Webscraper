#!/usr/bin/env python3
"""
Monitor em tempo real do progresso do scraper
"""

import os
import json
import time
import glob
from datetime import datetime

def clear_screen():
    """Limpa a tela"""
    os.system('cls' if os.name == 'nt' else 'clear')

def count_unique_establishments():
    """Conta estabelecimentos únicos nos arquivos"""
    try:
        cell_files = glob.glob('output/cells/cell_*.json')
        seen_keys = set()
        total_establishments = 0
        
        for file_path in cell_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                establishments = data.get('establishments', [])
                for est in establishments:
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
                        total_establishments += 1
                        
            except Exception:
                continue
        
        return total_establishments, len(cell_files)
    except Exception:
        return 0, 0

def get_progress_info():
    """Obtém informações de progresso"""
    try:
        with open('output/progress.json', 'r', encoding='utf-8') as f:
            progress = json.load(f)
        return progress
    except Exception:
        return {'cells_processed': 0, 'establishments_found': 0, 'timestamp': 'N/A'}

def show_status():
    """Mostra status único"""
    now = datetime.now()
    progress = get_progress_info()
    unique_establishments, total_files = count_unique_establishments()
    
    total_cells = 7904
    cells_processed = progress.get('cells_processed', 0)
    progress_percent = (cells_processed / total_cells) * 100
    
    print("STATUS ATUAL - SCRAPER BORRACHARIAS SC")
    print("=" * 60)
    print(f"Horario: {now.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Celulas: {cells_processed:,} / {total_cells:,} ({progress_percent:.2f}%)")
    print(f"Contatos unicos: {unique_establishments:,}")
    print(f"Arquivos: {total_files:,}")
    print(f"Saida: output/tire_shops_auto_complete.json")
    
    if unique_establishments > 0 and cells_processed > 0:
        avg_per_cell = unique_establishments / cells_processed
        estimated_total = avg_per_cell * total_cells
        print(f"Media: {avg_per_cell:.2f} por celula")
        print(f"Estimativa: {estimated_total:,.0f} total")

def monitor_continuous():
    """Monitor contínuo"""
    print("MONITOR TEMPO REAL - SCRAPER BORRACHARIAS SP")
    print("Pressione Ctrl+C para sair")
    print()
    
    start_time = datetime.now()
    
    try:
        while True:
            clear_screen()
            
            now = datetime.now()
            progress = get_progress_info()
            unique_establishments, total_files = count_unique_establishments()
            
            # Dados básicos
            total_cells = 7904
            cells_processed = progress.get('cells_processed', 0)
            progress_percent = (cells_processed / total_cells) * 100
            last_update = progress.get('timestamp', 'N/A')
            
            # Calcular velocidade
            elapsed = now - start_time
            if elapsed.total_seconds() > 0 and cells_processed > 0:
                cells_per_hour = (cells_processed / elapsed.total_seconds()) * 3600
                remaining_cells = total_cells - cells_processed
                if cells_per_hour > 0:
                    hours_remaining = remaining_cells / cells_per_hour
                else:
                    hours_remaining = 0
            else:
                cells_per_hour = 0
                hours_remaining = 0
            
            # Display
            print("MONITOR TEMPO REAL - SCRAPER BORRACHARIAS SP")
            print("=" * 70)
            print(f"Agora: {now.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"Monitorando desde: {start_time.strftime('%H:%M:%S')}")
            print()
            
            print("PROGRESSO PRINCIPAL:")
            print(f"   Celulas processadas: {cells_processed:,} / {total_cells:,}")
            print(f"   Progresso: {progress_percent:.2f}%")
            print(f"   Contatos unicos: {unique_establishments:,}")
            print(f"   Arquivos gerados: {total_files:,}")
            print()
            
            print("VELOCIDADE:")
            print(f"   Celulas/hora: {cells_per_hour:.1f}")
            if hours_remaining > 0:
                print(f"   Tempo restante: {hours_remaining:.1f} horas")
            print()
            
            print("ARQUIVOS DE SAIDA:")
            print(f"   Principal: output/tire_shops_auto_complete.json")
            print(f"   Backup: output/tire_shops_auto_backup.json")
            print(f"   Progresso: output/progress.json")
            print(f"   Celulas: output/cells/ ({total_files:,} arquivos)")
            print()
            
            if unique_establishments > 0 and cells_processed > 0:
                avg_per_cell = unique_establishments / cells_processed
                estimated_total = avg_per_cell * total_cells
                print("ESTIMATIVAS:")
                print(f"   Media por celula: {avg_per_cell:.2f}")
                print(f"   Total estimado: {estimated_total:,.0f} estabelecimentos")
                print()
            
            print("ULTIMA ATUALIZACAO:")
            print(f"   {last_update}")
            print()
            
            # Barra de progresso
            bar_length = 50
            filled_length = int(bar_length * progress_percent / 100)
            bar = '#' * filled_length + '.' * (bar_length - filled_length)
            print(f"[{bar}] {progress_percent:.1f}%")
            print()
            
            print("Pressione Ctrl+C para sair do monitor")
            
            # Aguardar 30 segundos
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nMonitor finalizado.")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python monitor_tempo_real.py status    # Status unico")
        print("  python monitor_tempo_real.py monitor   # Monitor continuo")
        return
    
    command = sys.argv[1]
    
    if command == 'status':
        show_status()
    elif command == 'monitor':
        monitor_continuous()
    else:
        print(f"Comando desconhecido: {command}")

if __name__ == '__main__':
    main()
