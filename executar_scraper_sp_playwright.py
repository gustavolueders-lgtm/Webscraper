#!/usr/bin/env python3
"""
Script para executar o scraper de borracharias de São Paulo com Playwright
"""

import os
import json
import time
import subprocess
import sys
from datetime import datetime

class ScraperPlaywrightController:
    def __init__(self):
        self.output_dir = 'output'
        self.progress_file = os.path.join(self.output_dir, 'progress.json')
        self.grid_file = os.path.join(self.output_dir, 'grid_info.json')
        
        # Criar diretório se não existir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_progress(self):
        """Obtém o progresso atual"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'cells_processed': 0, 'establishments_found': 0, 'start_cell': 0}
    
    def get_grid_info(self):
        """Obtém informações do grid"""
        if os.path.exists(self.grid_file):
            with open(self.grid_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'total_cells': 20664}  # Valor padrão
    
    def run_batch(self, start_cell, batch_size=50):
        """Executa um lote de células"""
        print(f"Executando lote: celulas {start_cell} a {start_cell + batch_size - 1}")
        
        cmd = [
            sys.executable, 
            'scraper_borracharias_sp_playwright.py', 
            str(start_cell), 
            str(batch_size)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)  # 2 horas timeout
            
            if result.returncode == 0:
                print("Lote concluido com sucesso")
                print("Output:", result.stdout[-500:])  # Últimas 500 chars
                return True
            else:
                print(f"Erro no lote: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("Timeout do lote - continuando...")
            return True
        except Exception as e:
            print(f"Erro ao executar lote: {e}")
            return False
    
    def run_continuous(self, batch_size=50, max_batches=None):
        """Executa o scraper de forma contínua"""
        print("INICIANDO SCRAPER CONTINUO COM PLAYWRIGHT - SAO PAULO")
        print("=" * 70)
        
        progress = self.get_progress()
        grid_info = self.get_grid_info()
        
        start_cell = progress.get('cells_processed', 0)
        total_cells = grid_info.get('total_cells', 20664)
        
        print(f"Total de celulas: {total_cells:,}")
        print(f"Comecando da celula: {start_cell:,}")
        print(f"Tamanho do lote: {batch_size}")
        print(f"Progresso atual: {start_cell/total_cells*100:.2f}%")
        
        batch_count = 0
        
        while start_cell < total_cells:
            if max_batches and batch_count >= max_batches:
                print(f"Limite de lotes atingido: {max_batches}")
                break
            
            batch_count += 1
            remaining_cells = total_cells - start_cell
            current_batch_size = min(batch_size, remaining_cells)
            
            print(f"\nLOTE {batch_count}")
            print(f"Celulas: {start_cell:,} a {start_cell + current_batch_size - 1:,}")
            print(f"Progresso: {start_cell/total_cells*100:.2f}%")
            print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
            
            success = self.run_batch(start_cell, current_batch_size)
            
            if success:
                start_cell += current_batch_size
                
                # Atualizar progresso
                new_progress = self.get_progress()
                print(f"Estabelecimentos encontrados: {new_progress.get('establishments_found', 0)}")
                
                # Pausa entre lotes
                if start_cell < total_cells:
                    pause_time = 60  # 1 minuto
                    print(f"Pausa de {pause_time}s entre lotes...")
                    time.sleep(pause_time)
            else:
                print("Falha no lote - tentando novamente em 120s...")
                time.sleep(120)
        
        print("\nSCRAPING COMPLETO!")
        final_progress = self.get_progress()
        print(f"Total de estabelecimentos encontrados: {final_progress.get('establishments_found', 0)}")
    
    def status(self):
        """Mostra o status atual"""
        progress = self.get_progress()
        grid_info = self.get_grid_info()
        
        total_cells = grid_info.get('total_cells', 20664)
        cells_processed = progress.get('cells_processed', 0)
        establishments_found = progress.get('establishments_found', 0)
        
        print("STATUS DO SCRAPER PLAYWRIGHT - SAO PAULO")
        print("=" * 60)
        print(f"Celulas processadas: {cells_processed:,} / {total_cells:,}")
        print(f"Progresso: {cells_processed/total_cells*100:.2f}%")
        print(f"Estabelecimentos encontrados: {establishments_found:,}")
        print(f"Ultima atualizacao: {progress.get('timestamp', 'N/A')}")
        
        if cells_processed > 0:
            avg_establishments_per_cell = establishments_found / cells_processed
            estimated_total = avg_establishments_per_cell * total_cells
            print(f"Media por celula: {avg_establishments_per_cell:.2f}")
            print(f"Estimativa total: {estimated_total:,.0f} estabelecimentos")

def main():
    controller = ScraperPlaywrightController()
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python executar_scraper_sp_playwright.py status")
        print("  python executar_scraper_sp_playwright.py run [batch_size] [max_batches]")
        return
    
    command = sys.argv[1]
    
    if command == 'status':
        controller.status()
    elif command == 'run':
        batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        max_batches = int(sys.argv[3]) if len(sys.argv) > 3 else None
        controller.run_continuous(batch_size, max_batches)
    else:
        print(f"Comando desconhecido: {command}")

if __name__ == '__main__':
    main()
