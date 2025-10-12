#!/usr/bin/env python3
"""
Sistema de controle do scraping de borracharias
Permite iniciar, parar e retomar o scraping
"""

import os
import json
import subprocess
import signal
import psutil
import time
from datetime import datetime

class ControleScraping:
    def __init__(self):
        self.spider_name = 'borracharia_resumable'
        self.output_file = 'output/tire_shops_auto_complete.json'
        self.pid_file = 'output/scraping.pid'
        self.status_file = 'output/scraping_status.json'
        
    def get_last_cell(self):
        """Obtém a última célula processada"""
        if not os.path.exists(self.output_file):
            return 0
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                return 0
            
            # Encontrar a maior cell_index
            max_cell = 0
            for item in data:
                cell_index = item.get('cell_index', 0)
                if cell_index > max_cell:
                    max_cell = cell_index
            
            return max_cell + 1  # Próxima célula a processar
            
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return 0
    
    def save_status(self, status, cell=None, pid=None):
        """Salva status atual"""
        status_data = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'current_cell': cell,
            'pid': pid
        }
        
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar status: {e}")
    
    def get_status(self):
        """Obtém status atual"""
        if not os.path.exists(self.status_file):
            return None
        
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def is_running(self):
        """Verifica se o scraping está rodando"""
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Verificar se o processo ainda existe
            return psutil.pid_exists(pid)
        except:
            return False
    
    def start_scraping(self, start_cell=None):
        """Inicia o scraping"""
        if self.is_running():
            print("⚠️ Scraping já está rodando!")
            return False
        
        if start_cell is None:
            start_cell = self.get_last_cell()
        
        print(f"🚀 INICIANDO SCRAPING DE BORRACHARIAS")
        print(f"📊 Célula de início: {start_cell}")
        print(f"⏰ Horário: {datetime.now().strftime('%H:%M:%S')}")
        
        # Comando para executar o spider com configurações otimizadas
        cmd = [
            'scrapy', 'crawl', self.spider_name,
            '-a', f'start_cell={start_cell}',
            '-s', 'DOWNLOAD_DELAY=1',  # Reduzido de 3 para 1
            '-s', 'RANDOMIZE_DOWNLOAD_DELAY=0.5',  # Variação de 0.5-1.5s
            '-s', 'CONCURRENT_REQUESTS=2',  # Aumentado de 1 para 2
            '-s', 'CONCURRENT_REQUESTS_PER_DOMAIN=2',
            '-s', 'AUTOTHROTTLE_ENABLED=True',
            '-s', 'AUTOTHROTTLE_START_DELAY=1',
            '-s', 'AUTOTHROTTLE_MAX_DELAY=5',
            '-s', 'AUTOTHROTTLE_TARGET_CONCURRENCY=2.0',
            '-L', 'INFO'
        ]
        
        try:
            # Iniciar processo em background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Salvar PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Salvar status
            self.save_status('running', start_cell, process.pid)
            
            print(f"✅ Scraping iniciado com PID: {process.pid}")
            print(f"📝 Para parar: python controle_scraping.py stop")
            print(f"📊 Para status: python controle_scraping.py status")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar scraping: {e}")
            return False
    
    def stop_scraping(self):
        """Para o scraping"""
        if not self.is_running():
            print("⚠️ Scraping não está rodando!")
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            print(f"🛑 PARANDO SCRAPING (PID: {pid})")
            
            # Tentar parar graciosamente
            os.kill(pid, signal.SIGTERM)
            
            # Aguardar um pouco
            time.sleep(5)
            
            # Se ainda estiver rodando, forçar parada
            if psutil.pid_exists(pid):
                print("🔨 Forçando parada...")
                os.kill(pid, signal.SIGKILL)
            
            # Limpar arquivos
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            
            # Atualizar status
            last_cell = self.get_last_cell()
            self.save_status('stopped', last_cell)
            
            print(f"✅ Scraping parado")
            print(f"📊 Última célula processada: {last_cell}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao parar scraping: {e}")
            return False
    
    def show_status(self):
        """Mostra status atual"""
        print("📊 STATUS DO SCRAPING DE BORRACHARIAS")
        print("=" * 60)
        
        # Status do processo
        if self.is_running():
            print("🟢 Status: RODANDO")
            
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                print(f"🔧 PID: {pid}")
            except:
                print("🔧 PID: Não encontrado")
        else:
            print("🔴 Status: PARADO")
        
        # Última célula processada
        last_cell = self.get_last_cell()
        print(f"📍 Última célula: {last_cell}")
        
        # Progresso
        total_cells = 7904
        progress = (last_cell / total_cells) * 100
        print(f"📈 Progresso: {progress:.2f}% ({last_cell:,}/{total_cells:,})")
        
        # Status salvo
        status_data = self.get_status()
        if status_data:
            print(f"⏰ Último update: {status_data.get('timestamp', 'N/A')}")
        
        # Dados coletados
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"🔧 Borracharias coletadas: {len(data):,}")
            except:
                print("🔧 Borracharias coletadas: Erro ao ler arquivo")
        else:
            print("🔧 Borracharias coletadas: 0")
    
    def resume_scraping(self):
        """Retoma o scraping do ponto onde parou"""
        if self.is_running():
            print("⚠️ Scraping já está rodando!")
            return False
        
        last_cell = self.get_last_cell()
        print(f"🔄 RETOMANDO SCRAPING")
        print(f"📍 Retomando da célula: {last_cell}")
        
        return self.start_scraping(last_cell)

def main():
    import sys
    
    controle = ControleScraping()
    
    if len(sys.argv) < 2:
        print("🔧 CONTROLE DE SCRAPING DE BORRACHARIAS")
        print("=" * 50)
        print("Uso:")
        print("  python controle_scraping.py start [célula]  - Iniciar scraping")
        print("  python controle_scraping.py stop           - Parar scraping")
        print("  python controle_scraping.py resume         - Retomar scraping")
        print("  python controle_scraping.py status         - Ver status")
        print()
        print("Exemplos:")
        print("  python controle_scraping.py start          - Iniciar do início")
        print("  python controle_scraping.py start 1488     - Iniciar da célula 1488")
        print("  python controle_scraping.py resume         - Retomar onde parou")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_cell = None
        if len(sys.argv) > 2:
            try:
                start_cell = int(sys.argv[2])
            except ValueError:
                print("❌ Célula deve ser um número")
                return
        
        controle.start_scraping(start_cell)
    
    elif command == 'stop':
        controle.stop_scraping()
    
    elif command == 'resume':
        controle.resume_scraping()
    
    elif command == 'status':
        controle.show_status()
    
    else:
        print(f"❌ Comando desconhecido: {command}")

if __name__ == "__main__":
    main()
