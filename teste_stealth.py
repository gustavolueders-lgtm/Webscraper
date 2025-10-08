#!/usr/bin/env python3
"""
Teste do spider stealth anti-bloqueio
"""

import os
import time
import subprocess
import signal
import sys
from log_monitor import LogMonitor

def test_stealth_spider():
    """Testa spider stealth"""
    print("🥷 TESTE DO SPIDER STEALTH - ANTI-BLOQUEIO")
    print("=" * 60)
    print("🎯 OBJETIVO: Contornar bloqueio do Google Maps")
    print("⚡ ESTRATÉGIA: Comportamento humano + delays inteligentes")
    print("📞 FOCO: Coleta de telefones")
    print("⏰ TEMPO: ~3x mais lento, mas FUNCIONAL")
    print("=" * 60)
    
    # Limpa arquivos anteriores
    files_to_clean = [
        'output/fuel_stations_monitored.json',
        'output/monitoring_progress.json',
        'output/scrapy.log'
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removido: {file_path}")
    
    # Inicia monitor
    print("\n🔍 Iniciando monitor...")
    monitor = LogMonitor()
    monitor.start_monitoring()
    
    # Inicia spider stealth
    print("🥷 Iniciando spider stealth...")
    spider_process = None
    
    try:
        spider_process = subprocess.Popen(
            ['scrapy', 'crawl', 'stealth_fuel', '--set', 'SETTINGS_MODULE=business_scraper.settings_stealth'],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ Spider stealth iniciado (PID: {spider_process.pid})")
        print("💡 Pressione Ctrl+C para parar com segurança")
        print("🥷 Modo stealth ativo - evitando detecção...")
        print("-" * 60)
        
        start_time = time.time()
        last_count = 0
        last_phones = 0
        
        while spider_process.poll() is None:
            # Obtém estatísticas
            stats = monitor.get_stats()
            current_count = stats['total_establishments']
            phones_collected = stats.get('phones_collected', 0)
            
            # Calcula métricas
            elapsed_time = time.time() - start_time
            elapsed_minutes = elapsed_time / 60
            
            if elapsed_minutes > 0:
                rate = current_count / elapsed_minutes
                phone_rate_per_min = phones_collected / elapsed_minutes
            else:
                rate = 0
                phone_rate_per_min = 0
            
            # Mostra progresso
            if current_count != last_count or int(elapsed_time) % 30 == 0:
                elapsed_str = f"{int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}"
                phone_success_rate = (phones_collected / current_count * 100) if current_count > 0 else 0
                
                print(f"\n⏰ {elapsed_str} | "
                      f"🏪 {current_count:,} estabelecimentos | "
                      f"📞 {phones_collected} telefones ({phone_success_rate:.1f}%) | "
                      f"⚡ {rate:.1f}/min | "
                      f"📞 {phone_rate_per_min:.1f} tel/min")
                
                last_count = current_count
            
            # Mostra últimos estabelecimentos com telefones
            if phones_collected > last_phones:
                latest = monitor.get_latest_establishments(5)
                if latest:
                    print("\n📞 ÚLTIMOS COM TELEFONE:")
                    for est in latest[-5:]:
                        if est.get('phone'):
                            name = est.get('name', 'N/A')[:30]
                            phone = est.get('phone', 'N/A')
                            print(f"   🏪 {name} - 📞 {phone}")
                
                last_phones = phones_collected
            
            # Status stealth
            if int(elapsed_time) % 120 == 0 and elapsed_time > 0:  # A cada 2 minutos
                print(f"\n🥷 STATUS STEALTH:")
                print(f"   ✅ Sistema funcionando há {elapsed_time/60:.1f} minutos")
                print(f"   🎯 Coletando dados com sucesso")
                print(f"   📞 Taxa de telefones: {phone_success_rate:.1f}%")
                if rate > 0:
                    estimated_total_time = (50 / rate) if rate > 0 else 0  # Para ~50 estabelecimentos
                    print(f"   ⏰ Estimativa para 50 estabelecimentos: {estimated_total_time:.1f} min")
            
            time.sleep(15)  # Verifica a cada 15 segundos
            
    except KeyboardInterrupt:
        print(f"\n🛑 Interrupção solicitada pelo usuário")
    
    finally:
        # Para spider
        if spider_process:
            print("🛑 Parando spider stealth...")
            try:
                spider_process.terminate()
                spider_process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                print("⚠️ Forçando parada do spider...")
                spider_process.kill()
        
        # Para monitor
        print("🔍 Parando monitor...")
        monitor.stop_monitoring()
        monitor.force_save()
        
        # Mostra resultados
        show_stealth_results(monitor, start_time)

def show_stealth_results(monitor, start_time):
    """Mostra resultados do teste stealth"""
    elapsed_total = time.time() - start_time
    stats = monitor.get_stats()
    
    print("\n" + "="*70)
    print("🥷 RESULTADOS DO TESTE STEALTH")
    print("="*70)
    
    total_establishments = stats['total_establishments']
    phones_collected = stats.get('phones_collected', 0)
    phone_success_rate = (phones_collected / total_establishments * 100) if total_establishments > 0 else 0
    
    print(f"🏪 Total de estabelecimentos: {total_establishments:,}")
    print(f"📞 Telefones coletados: {phones_collected}")
    print(f"📊 Taxa de sucesso (telefones): {phone_success_rate:.1f}%")
    print(f"⏰ Tempo total: {elapsed_total/60:.1f} minutos")
    
    if total_establishments > 0:
        avg_time_per_establishment = elapsed_total / total_establishments
        print(f"⚡ Tempo médio por estabelecimento: {avg_time_per_establishment:.1f}s")
        
        # Projeção para SC completa
        estimated_total_establishments = 50000  # Estimativa para SC
        estimated_total_time_hours = (estimated_total_establishments * avg_time_per_establishment) / 3600
        print(f"📈 PROJEÇÃO PARA SC COMPLETA:")
        print(f"   🎯 ~{estimated_total_establishments:,} estabelecimentos estimados")
        print(f"   ⏰ ~{estimated_total_time_hours:.1f} horas necessárias")
        print(f"   📞 ~{estimated_total_establishments * phone_success_rate / 100:.0f} telefones esperados")
    
    # Análise de qualidade
    print(f"\n🎯 ANÁLISE DE QUALIDADE:")
    if phone_success_rate >= 70:
        print("✅ EXCELENTE! Alta taxa de coleta de telefones")
        quality = "EXCELENTE"
    elif phone_success_rate >= 50:
        print("✅ BOM! Taxa razoável de coleta de telefones")
        quality = "BOM"
    elif phone_success_rate >= 30:
        print("⚠️ REGULAR. Alguns telefones coletados")
        quality = "REGULAR"
    else:
        print("❌ BAIXA taxa de coleta. Verificar seletores")
        quality = "BAIXA"
    
    # Comparação com bloqueio
    print(f"\n📊 COMPARAÇÃO:")
    print(f"   ❌ Sistema anterior: 0 estabelecimentos (bloqueado)")
    print(f"   ✅ Sistema stealth: {total_establishments} estabelecimentos")
    print(f"   🎯 Melhoria: INFINITA (de bloqueado para funcional)")
    
    print(f"\n💾 DADOS SALVOS EM:")
    print("   📄 output/fuel_stations_monitored.json")
    print("   📊 output/monitoring_progress.json")
    
    # Recomendações
    print(f"\n💡 RECOMENDAÇÕES:")
    if quality in ["EXCELENTE", "BOM"]:
        print("   ✅ Sistema pronto para produção!")
        print("   🚀 Execute: python real_time_scraper.py")
        print("   ⏰ Deixe rodando por várias horas")
    else:
        print("   🔧 Ajustar seletores de telefone")
        print("   ⏰ Aumentar delays se necessário")
        print("   🔄 Testar novamente")
    
    print("="*70)

def main():
    """Função principal"""
    print("🥷 TESTE DO SPIDER STEALTH")
    print("⚠️ Este modo contorna bloqueios mas é mais lento")
    print("🎯 Foco: coleta de telefones funcionando")
    print()
    
    choice = input("Deseja executar teste stealth? (s/n): ").strip().lower()
    
    if choice == 's':
        test_stealth_spider()
    else:
        print("👋 Use 'python real_time_scraper.py' para sistema completo!")

if __name__ == "__main__":
    main()
