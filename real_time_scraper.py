#!/usr/bin/env python3
"""
Sistema de scraping em tempo real com monitoramento
"""

import os
import subprocess
import time
import signal
import sys
from datetime import datetime
from log_monitor import LogMonitor

class RealTimeScraper:
    def __init__(self):
        self.monitor = LogMonitor()
        self.spider_process = None
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🚀 SISTEMA DE SCRAPING EM TEMPO REAL")
        print("=" * 50)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n🛑 Sinal recebido ({signum}). Parando sistema...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Inicia o sistema completo"""
        if self.running:
            print("⚠️ Sistema já está rodando")
            return
        
        print("🔧 Preparando sistema...")
        
        # Limpa log anterior
        log_file = "output/scrapy.log"
        if os.path.exists(log_file):
            os.remove(log_file)
            print(f"🗑️ Log anterior removido: {log_file}")
        
        # Inicia monitor
        print("🔍 Iniciando monitor de logs...")
        self.monitor.start_monitoring()
        
        # Inicia spider
        print("🕷️ Iniciando spider...")
        self._start_spider()
        
        # Inicia interface
        print("📊 Iniciando interface de monitoramento...")
        self._start_interface()

    def _start_spider(self):
        """Inicia o spider em background"""
        try:
            self.spider_process = subprocess.Popen(
                ['scrapy', 'crawl', 'stealth_fuel', '--set', 'SETTINGS_MODULE=business_scraper.settings_stealth'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running = True
            print(f"✅ Spider iniciado (PID: {self.spider_process.pid})")
            
        except Exception as e:
            print(f"❌ Erro ao iniciar spider: {e}")
            return False
        
        return True

    def _start_interface(self):
        """Inicia interface de monitoramento"""
        print("\n" + "="*60)
        print("🎯 MONITORAMENTO EM TEMPO REAL")
        print("="*60)
        print("💡 Pressione Ctrl+C para parar com segurança")
        print("="*60)
        
        last_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                # Verifica se spider ainda está rodando
                if self.spider_process and self.spider_process.poll() is not None:
                    print(f"\n🏁 Spider finalizado (código: {self.spider_process.returncode})")
                    break
                
                # Obtém estatísticas
                stats = self.monitor.get_stats()
                current_count = stats['total_establishments']
                
                # Calcula métricas
                elapsed_time = time.time() - start_time
                elapsed_minutes = elapsed_time / 60
                
                if elapsed_minutes > 0:
                    rate = current_count / elapsed_minutes
                else:
                    rate = 0
                
                # Mostra progresso
                if current_count != last_count or int(elapsed_time) % 10 == 0:
                    self._show_progress(stats, elapsed_time, rate)
                    last_count = current_count
                
                # Mostra últimos estabelecimentos
                if current_count > last_count:
                    latest = self.monitor.get_latest_establishments(3)
                    if latest:
                        print("\n📍 ÚLTIMOS ESTABELECIMENTOS:")
                        for est in latest[-3:]:
                            print(f"   🏪 {est.get('name', 'N/A')} - {est.get('address', 'N/A')}")
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Interrupção solicitada pelo usuário")
        
        finally:
            self.stop()

    def _show_progress(self, stats: dict, elapsed_time: float, rate: float):
        """Mostra progresso atual"""
        elapsed_str = f"{int(elapsed_time//3600):02d}:{int((elapsed_time%3600)//60):02d}:{int(elapsed_time%60):02d}"

        phones_collected = stats.get('phones_collected', 0)
        phone_rate = (phones_collected / stats['total_establishments'] * 100) if stats['total_establishments'] > 0 else 0

        print(f"\n⏰ {elapsed_str} | "
              f"🏪 {stats['total_establishments']:,} estabelecimentos | "
              f"📞 {phones_collected} telefones ({phone_rate:.1f}%) | "
              f"📍 {stats['cells_processed']} células | "
              f"⚡ {rate:.1f}/min")
        
        # Estimativa de conclusão
        total_cells = stats.get('total_cells', 8208)
        if stats['cells_processed'] > 0 and total_cells > 0:
            progress_pct = (stats['cells_processed'] / total_cells) * 100
            if rate > 0:
                remaining_cells = total_cells - stats['cells_processed']
                remaining_time = (remaining_cells * 2) / rate  # 2 termos por célula
                remaining_hours = remaining_time / 60
                print(f"📊 Progresso: {progress_pct:.1f}% | ⏳ Restam ~{remaining_hours:.1f}h")

    def stop(self):
        """Para o sistema"""
        if not self.running:
            return
        
        print("\n🛑 Parando sistema...")
        self.running = False
        
        # Para monitor
        print("🔍 Parando monitor...")
        self.monitor.stop_monitoring()
        
        # Força salvamento final
        print("💾 Salvando dados finais...")
        self.monitor.force_save()
        
        # Para spider
        if self.spider_process:
            print("🕷️ Parando spider...")
            try:
                self.spider_process.terminate()
                self.spider_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("⚠️ Spider não respondeu, forçando parada...")
                self.spider_process.kill()
            except Exception as e:
                print(f"⚠️ Erro ao parar spider: {e}")
        
        # Mostra resumo final
        self._show_final_summary()

    def _show_final_summary(self):
        """Mostra resumo final"""
        stats = self.monitor.get_stats()
        
        print("\n" + "="*50)
        print("📋 RESUMO FINAL")
        print("="*50)
        print(f"🏪 Total de estabelecimentos: {stats['total_establishments']:,}")
        print(f"📍 Células processadas: {stats['cells_processed']}")
        print(f"📄 Arquivo de dados: {self.monitor.output_file}")
        print(f"📊 Arquivo de progresso: {self.monitor.progress_file}")
        
        if os.path.exists(self.monitor.output_file):
            file_size = os.path.getsize(self.monitor.output_file) / 1024 / 1024
            print(f"💾 Tamanho do arquivo: {file_size:.2f} MB")
        
        print("="*50)
        print("✅ Sistema finalizado com segurança!")

def main():
    """Função principal"""
    scraper = RealTimeScraper()
    
    try:
        scraper.start()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        scraper.stop()

if __name__ == "__main__":
    main()
