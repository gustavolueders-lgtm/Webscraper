#!/usr/bin/env python3
"""
Scraper conservador para evitar bloqueio do Google Maps
"""

import os
import subprocess
import time
import signal
import sys
from datetime import datetime
from log_monitor import LogMonitor

class ConservativeScraper:
    def __init__(self):
        self.monitor = LogMonitor()
        self.spider_process = None
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🐌 SCRAPER CONSERVADOR - ANTI-BLOQUEIO")
        print("=" * 50)
        print("⚠️ CONFIGURAÇÕES ULTRA-CONSERVADORAS:")
        print("   🐌 1 requisição por vez")
        print("   ⏰ 15-25 segundos entre requisições")
        print("   🔄 User-Agent rotativo")
        print("   ⏳ Timeout de 2 minutos")
        print("   🛡️ Retry automático")
        print("=" * 50)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n🛑 Sinal recebido ({signum}). Parando sistema...")
        self.stop()
        sys.exit(0)

    def start(self):
        """Inicia o sistema conservador"""
        if self.running:
            print("⚠️ Sistema já está rodando")
            return
        
        print("🔧 Preparando sistema conservador...")
        
        # Limpa log anterior
        log_file = "output/scrapy.log"
        if os.path.exists(log_file):
            os.remove(log_file)
            print(f"🗑️ Log anterior removido: {log_file}")
        
        # Inicia monitor
        print("🔍 Iniciando monitor de logs...")
        self.monitor.start_monitoring()
        
        # Inicia spider conservador
        print("🐌 Iniciando spider conservador...")
        self._start_conservative_spider()
        
        # Inicia interface
        print("📊 Iniciando interface de monitoramento...")
        self._start_interface()

    def _start_conservative_spider(self):
        """Inicia o spider com configurações conservadoras"""
        try:
            # Usa configurações conservadoras
            self.spider_process = subprocess.Popen(
                ['scrapy', 'crawl', 'simple_fuel', '--set', 'SETTINGS_MODULE=business_scraper.settings_conservative'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running = True
            print(f"✅ Spider conservador iniciado (PID: {self.spider_process.pid})")
            print("⚠️ ATENÇÃO: Processo será MUITO LENTO para evitar bloqueio")
            
        except Exception as e:
            print(f"❌ Erro ao iniciar spider: {e}")
            return False
        
        return True

    def _start_interface(self):
        """Inicia interface de monitoramento conservadora"""
        print("\n" + "="*60)
        print("🐌 MONITORAMENTO CONSERVADOR")
        print("="*60)
        print("💡 Pressione Ctrl+C para parar com segurança")
        print("⚠️ Processo será lento (15-25s por requisição)")
        print("🎯 Objetivo: Evitar bloqueio do Google Maps")
        print("="*60)
        
        last_count = 0
        start_time = time.time()
        last_warning_time = 0
        
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
                if current_count != last_count or int(elapsed_time) % 30 == 0:
                    self._show_conservative_progress(stats, elapsed_time, rate)
                    last_count = current_count
                
                # Mostra últimos estabelecimentos
                if current_count > last_count:
                    latest = self.monitor.get_latest_establishments(2)
                    if latest:
                        print("\n📍 ÚLTIMOS ESTABELECIMENTOS:")
                        for est in latest[-2:]:
                            print(f"   🏪 {est.get('name', 'N/A')} - {est.get('address', 'N/A')}")
                
                # Aviso periódico sobre lentidão
                if elapsed_time - last_warning_time > 300:  # A cada 5 minutos
                    print(f"\n💡 LEMBRETE: Sistema rodando em modo conservador")
                    print(f"   🐌 Velocidade esperada: ~2-4 estabelecimentos/min")
                    print(f"   🛡️ Objetivo: Evitar bloqueio do Google Maps")
                    last_warning_time = elapsed_time
                
                time.sleep(5)  # Verifica a cada 5 segundos
                
        except KeyboardInterrupt:
            print(f"\n🛑 Interrupção solicitada pelo usuário")
        
        finally:
            self.stop()

    def _show_conservative_progress(self, stats: dict, elapsed_time: float, rate: float):
        """Mostra progresso conservador"""
        elapsed_str = f"{int(elapsed_time//3600):02d}:{int((elapsed_time%3600)//60):02d}:{int(elapsed_time%60):02d}"
        
        print(f"\n⏰ {elapsed_str} | "
              f"🏪 {stats['total_establishments']:,} estabelecimentos | "
              f"📍 {stats['cells_processed']} células | "
              f"🐌 {rate:.1f}/min")
        
        # Estimativa conservadora
        total_cells = stats.get('total_cells', 8208)
        if stats['cells_processed'] > 0 and total_cells > 0:
            progress_pct = (stats['cells_processed'] / total_cells) * 100
            if rate > 0:
                remaining_cells = total_cells - stats['cells_processed']
                # Estimativa conservadora: 2 termos por célula, 20s por requisição
                remaining_time_hours = (remaining_cells * 2 * 20) / 3600
                print(f"📊 Progresso: {progress_pct:.1f}% | ⏳ Estimativa: ~{remaining_time_hours:.1f}h restantes")
                
                if remaining_time_hours > 24:
                    print(f"⚠️ ATENÇÃO: Tempo estimado muito alto. Considere:")
                    print(f"   💡 Usar VPN para mudar IP")
                    print(f"   💡 Aguardar algumas horas")
                    print(f"   💡 Usar Google Places API")

    def stop(self):
        """Para o sistema conservador"""
        if not self.running:
            return
        
        print("\n🛑 Parando sistema conservador...")
        self.running = False
        
        # Para monitor
        print("🔍 Parando monitor...")
        self.monitor.stop_monitoring()
        
        # Força salvamento final
        print("💾 Salvando dados finais...")
        self.monitor.force_save()
        
        # Para spider
        if self.spider_process:
            print("🐌 Parando spider conservador...")
            try:
                self.spider_process.terminate()
                self.spider_process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                print("⚠️ Spider não respondeu, forçando parada...")
                self.spider_process.kill()
            except Exception as e:
                print(f"⚠️ Erro ao parar spider: {e}")
        
        # Mostra resumo final
        self._show_final_summary()

    def _show_final_summary(self):
        """Mostra resumo final conservador"""
        stats = self.monitor.get_stats()
        
        print("\n" + "="*50)
        print("📋 RESUMO FINAL - MODO CONSERVADOR")
        print("="*50)
        print(f"🏪 Total de estabelecimentos: {stats['total_establishments']:,}")
        print(f"📍 Células processadas: {stats['cells_processed']}")
        print(f"📄 Arquivo de dados: {self.monitor.output_file}")
        print(f"📊 Arquivo de progresso: {self.monitor.progress_file}")
        
        if os.path.exists(self.monitor.output_file):
            file_size = os.path.getsize(self.monitor.output_file) / 1024 / 1024
            print(f"💾 Tamanho do arquivo: {file_size:.2f} MB")
        
        print("\n💡 DICAS PARA PRÓXIMA EXECUÇÃO:")
        print("   🔄 Aguarde 2-6 horas antes de tentar novamente")
        print("   🌐 Use VPN para mudar IP")
        print("   ⏰ Execute durante madrugada (menos tráfego)")
        print("   🔑 Considere Google Places API para dados oficiais")
        
        print("="*50)
        print("✅ Sistema finalizado com segurança!")

def main():
    """Função principal"""
    scraper = ConservativeScraper()
    
    print("⚠️ AVISO IMPORTANTE:")
    print("Este modo é MUITO LENTO mas evita bloqueio")
    print("Estimativa: ~2-4 estabelecimentos por minuto")
    print("Para SC completa: ~30-60 horas")
    print()
    
    choice = input("Deseja continuar com modo conservador? (s/n): ").strip().lower()
    
    if choice == 's':
        try:
            scraper.start()
        except Exception as e:
            print(f"❌ Erro fatal: {e}")
            scraper.stop()
    else:
        print("👋 Use 'python solucao_final.py' para simulação com dados reais!")

if __name__ == "__main__":
    main()
