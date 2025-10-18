#!/usr/bin/env python3
"""
Script para monitorar o progresso do scraper de Santa Catarina
"""

import os
import json
import time
import sys
from datetime import datetime, timedelta

def clear_screen():
    """Limpa a tela"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_progress():
    """Obtém o progresso atual"""
    progress_file = 'output/progress.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'cells_processed': 0, 'establishments_found': 0, 'timestamp': None}

def get_grid_info():
    """Obtém informações do grid"""
    grid_file = 'output/grid_info.json'
    if os.path.exists(grid_file):
        with open(grid_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'total_cells': 7904}

def format_time_remaining(cells_processed, total_cells, start_time):
    """Calcula tempo restante estimado"""
    if cells_processed == 0:
        return "Calculando..."
    
    elapsed = datetime.now() - start_time
    cells_per_second = cells_processed / elapsed.total_seconds()
    
    if cells_per_second == 0:
        return "Calculando..."
    
    remaining_cells = total_cells - cells_processed
    remaining_seconds = remaining_cells / cells_per_second
    
    return str(timedelta(seconds=int(remaining_seconds)))

def monitor_continuous():
    """Monitora o progresso continuamente"""
    print("🔍 MONITOR DE PROGRESSO - SCRAPER SÃO PAULO")
    print("=" * 60)
    print("Pressione Ctrl+C para sair")
    print()
    
    start_time = datetime.now()
    last_cells = 0
    
    try:
        while True:
            clear_screen()
            
            progress = get_progress()
            grid_info = get_grid_info()
            
            total_cells = grid_info.get('total_cells', 7904)
            cells_processed = progress.get('cells_processed', 0)
            establishments_found = progress.get('establishments_found', 0)
            last_update = progress.get('timestamp', 'N/A')
            
            # Calcular estatísticas
            progress_percent = (cells_processed / total_cells) * 100
            
            # Velocidade
            if cells_processed > last_cells:
                last_cells = cells_processed
            
            # Estimativa de tempo
            time_remaining = format_time_remaining(cells_processed, total_cells, start_time)
            
            print("🔍 MONITOR DE PROGRESSO - SCRAPER SÃO PAULO")
            print("=" * 60)
            print(f"⏰ Monitoramento iniciado: {start_time.strftime('%H:%M:%S')}")
            print(f"🕐 Agora: {datetime.now().strftime('%H:%M:%S')}")
            print()
            
            print("📊 PROGRESSO GERAL:")
            print(f"   📍 Células processadas: {cells_processed:,} / {total_cells:,}")
            print(f"   📈 Progresso: {progress_percent:.2f}%")
            print(f"   🔧 Estabelecimentos: {establishments_found:,}")
            print()
            
            if cells_processed > 0:
                avg_per_cell = establishments_found / cells_processed
                estimated_total = avg_per_cell * total_cells
                print("📊 ESTATÍSTICAS:")
                print(f"   📊 Média por célula: {avg_per_cell:.2f}")
                print(f"   🎯 Estimativa total: {estimated_total:,.0f} estabelecimentos")
                print()
            
            print("⏱️ TEMPO:")
            print(f"   ⏰ Tempo decorrido: {datetime.now() - start_time}")
            print(f"   🕐 Tempo restante: {time_remaining}")
            print()
            
            print("📄 ÚLTIMA ATUALIZAÇÃO:")
            print(f"   🕐 {last_update}")
            print()
            
            # Barra de progresso
            bar_length = 50
            filled_length = int(bar_length * progress_percent / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            print(f"📊 [{bar}] {progress_percent:.1f}%")
            print()
            
            print("💡 Pressione Ctrl+C para sair do monitor")
            
            # Aguardar 30 segundos
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n👋 Monitor finalizado.")

def show_status():
    """Mostra status único"""
    progress = get_progress()
    grid_info = get_grid_info()
    
    total_cells = grid_info.get('total_cells', 7904)
    cells_processed = progress.get('cells_processed', 0)
    establishments_found = progress.get('establishments_found', 0)
    last_update = progress.get('timestamp', 'N/A')
    
    progress_percent = (cells_processed / total_cells) * 100
    
    print("📊 STATUS DO SCRAPER DE BORRACHARIAS - SANTA CATARINA")
    print("=" * 60)
    print(f"📍 Células processadas: {cells_processed:,} / {total_cells:,}")
    print(f"📈 Progresso: {progress_percent:.2f}%")
    print(f"🔧 Estabelecimentos encontrados: {establishments_found:,}")
    print(f"⏰ Última atualização: {last_update}")
    
    if cells_processed > 0:
        avg_per_cell = establishments_found / cells_processed
        estimated_total = avg_per_cell * total_cells
        print(f"📊 Média por célula: {avg_per_cell:.2f}")
        print(f"🎯 Estimativa total: {estimated_total:,.0f} estabelecimentos")

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python monitorar_progresso.py status    # Status único")
        print("  python monitorar_progresso.py monitor   # Monitor contínuo")
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
