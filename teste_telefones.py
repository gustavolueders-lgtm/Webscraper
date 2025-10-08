#!/usr/bin/env python3
"""
Teste do spider com coleta de telefones
"""

import os
import time
import subprocess
import signal
import sys
from log_monitor import LogMonitor

def test_phone_collection():
    """Testa coleta de telefones"""
    print("📞 TESTE DE COLETA DE TELEFONES")
    print("=" * 50)
    print("⚠️ ATENÇÃO: Este teste é mais lento")
    print("   🔍 Clica em cada estabelecimento")
    print("   📞 Extrai telefone e dados detalhados")
    print("   ⏰ ~30-60 segundos por estabelecimento")
    print("=" * 50)
    
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
    
    # Inicia spider
    print("📞 Iniciando spider com coleta de telefones...")
    spider_process = None
    
    try:
        spider_process = subprocess.Popen(
            ['scrapy', 'crawl', 'detailed_fuel'],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ Spider iniciado (PID: {spider_process.pid})")
        print("💡 Pressione Ctrl+C para parar com segurança")
        print("⏰ Aguarde... processo é lento mas coleta telefones!")
        print("-" * 50)
        
        start_time = time.time()
        last_count = 0
        
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
            else:
                rate = 0
            
            # Mostra progresso
            if current_count != last_count or int(elapsed_time) % 30 == 0:
                elapsed_str = f"{int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}"
                phone_rate = (phones_collected / current_count * 100) if current_count > 0 else 0
                
                print(f"\n⏰ {elapsed_str} | "
                      f"🏪 {current_count:,} estabelecimentos | "
                      f"📞 {phones_collected} telefones ({phone_rate:.1f}%) | "
                      f"⚡ {rate:.1f}/min")
                
                last_count = current_count
            
            # Mostra últimos estabelecimentos com telefones
            if current_count > last_count:
                latest = monitor.get_latest_establishments(3)
                if latest:
                    print("\n📍 ÚLTIMOS ESTABELECIMENTOS:")
                    for est in latest[-3:]:
                        name = est.get('name', 'N/A')
                        phone = est.get('phone', 'Sem telefone')
                        address = est.get('address', 'N/A')
                        print(f"   🏪 {name}")
                        print(f"      📞 {phone}")
                        print(f"      📍 {address[:50]}...")
            
            time.sleep(10)  # Verifica a cada 10 segundos
            
    except KeyboardInterrupt:
        print(f"\n🛑 Interrupção solicitada pelo usuário")
    
    finally:
        # Para spider
        if spider_process:
            print("🛑 Parando spider...")
            try:
                spider_process.terminate()
                spider_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("⚠️ Forçando parada do spider...")
                spider_process.kill()
        
        # Para monitor
        print("🔍 Parando monitor...")
        monitor.stop_monitoring()
        monitor.force_save()
        
        # Mostra resultados
        show_phone_results(monitor, start_time)

def show_phone_results(monitor, start_time):
    """Mostra resultados da coleta de telefones"""
    elapsed_total = time.time() - start_time
    stats = monitor.get_stats()
    
    print("\n" + "="*60)
    print("📞 RESULTADOS DA COLETA DE TELEFONES")
    print("="*60)
    
    total_establishments = stats['total_establishments']
    phones_collected = stats.get('phones_collected', 0)
    phone_success_rate = (phones_collected / total_establishments * 100) if total_establishments > 0 else 0
    
    print(f"🏪 Total de estabelecimentos: {total_establishments:,}")
    print(f"📞 Telefones coletados: {phones_collected}")
    print(f"📊 Taxa de sucesso: {phone_success_rate:.1f}%")
    print(f"⏰ Tempo total: {elapsed_total/60:.1f} minutos")
    
    if total_establishments > 0:
        avg_time_per_establishment = elapsed_total / total_establishments
        print(f"⚡ Tempo médio por estabelecimento: {avg_time_per_establishment:.1f}s")
    
    # Mostra exemplos com telefones
    if os.path.exists('output/fuel_stations_monitored.json'):
        try:
            import json
            with open('output/fuel_stations_monitored.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filtra estabelecimentos com telefone
            with_phones = [est for est in data if est.get('phone')]
            without_phones = [est for est in data if not est.get('phone')]
            
            print(f"\n📞 ESTABELECIMENTOS COM TELEFONE: {len(with_phones)}")
            for i, est in enumerate(with_phones[:5], 1):
                name = est.get('name', 'N/A')
                phone = est.get('phone', 'N/A')
                website = est.get('website', 'N/A')
                print(f"   {i}. {name}")
                print(f"      📞 {phone}")
                if website != 'N/A':
                    print(f"      🌐 {website}")
            
            if len(with_phones) > 5:
                print(f"   ... e mais {len(with_phones) - 5} com telefone")
            
            print(f"\n❌ ESTABELECIMENTOS SEM TELEFONE: {len(without_phones)}")
            if without_phones:
                for i, est in enumerate(without_phones[:3], 1):
                    name = est.get('name', 'N/A')
                    print(f"   {i}. {name}")
                
                if len(without_phones) > 3:
                    print(f"   ... e mais {len(without_phones) - 3} sem telefone")
            
        except Exception as e:
            print(f"❌ Erro ao analisar dados: {e}")
    
    print(f"\n💾 DADOS SALVOS EM:")
    print("   📄 output/fuel_stations_monitored.json")
    print("   📊 output/monitoring_progress.json")
    
    # Avaliação do resultado
    print(f"\n🎯 AVALIAÇÃO:")
    if phone_success_rate >= 70:
        print("✅ EXCELENTE! Alta taxa de coleta de telefones")
    elif phone_success_rate >= 50:
        print("✅ BOM! Taxa razoável de coleta de telefones")
    elif phone_success_rate >= 30:
        print("⚠️ REGULAR. Alguns telefones coletados")
    else:
        print("❌ BAIXA taxa de coleta. Verificar seletores")
    
    print("="*60)

def main():
    """Função principal"""
    print("📞 TESTE DE COLETA DE TELEFONES")
    print("⚠️ Este teste é mais lento mas coleta dados valiosos")
    print()
    
    choice = input("Deseja executar teste de coleta de telefones? (s/n): ").strip().lower()
    
    if choice == 's':
        test_phone_collection()
    else:
        print("👋 Use 'python real_time_scraper.py' para sistema completo!")

if __name__ == "__main__":
    main()
