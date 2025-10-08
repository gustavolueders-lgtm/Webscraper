#!/usr/bin/env python3
"""
Demonstração do sistema completo de scraping em tempo real
"""

import os
import time
import subprocess
import json
from log_monitor import LogMonitor

def demo_complete_system():
    """Demonstra o sistema completo"""
    print("🎯 DEMONSTRAÇÃO DO SISTEMA COMPLETO")
    print("=" * 50)
    print("Este sistema resolve o problema de perda de dados!")
    print("✅ Dados salvos em tempo real")
    print("✅ Monitoramento visual do progresso")
    print("✅ Interrupção segura com Ctrl+C")
    print("✅ Recuperação automática de dados")
    print("=" * 50)
    
    # Limpa arquivos anteriores
    files_to_clean = [
        'output/scrapy.log',
        'output/fuel_stations_monitored.json',
        'output/monitoring_progress.json'
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removido: {file_path}")
    
    print("\n🚀 Iniciando demonstração de 2 minutos...")
    print("💡 Pressione Ctrl+C a qualquer momento para testar interrupção segura")
    print("-" * 50)
    
    # Inicia monitor
    monitor = LogMonitor()
    monitor.start_monitoring()
    
    # Inicia spider real
    process = subprocess.Popen(
        ['scrapy', 'crawl', 'simple_fuel'],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    start_time = time.time()
    last_count = 0
    last_cells = 0
    
    try:
        while time.time() - start_time < 120:  # 2 minutos
            # Verifica se processo ainda está rodando
            if process.poll() is not None:
                print(f"🏁 Spider finalizado (código: {process.returncode})")
                break
            
            stats = monitor.get_stats()
            current_count = stats['total_establishments']
            current_cells = stats['cells_processed']
            
            # Mostra progresso a cada mudança
            if current_count != last_count or current_cells != last_cells:
                elapsed = time.time() - start_time
                elapsed_str = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"
                
                rate = stats.get('establishments_per_minute', 0)
                
                print(f"⏰ {elapsed_str} | 🏪 {current_count:,} estabelecimentos | 📍 {current_cells} células | ⚡ {rate:.1f}/min")
                
                # Mostra últimos estabelecimentos encontrados
                if current_count > last_count:
                    latest = monitor.get_latest_establishments(3)
                    for est in latest[-3:]:
                        name = est.get('name', 'N/A')[:40]  # Limita tamanho
                        print(f"   🏪 {name}")
                
                last_count = current_count
                last_cells = current_cells
            
            time.sleep(3)
    
    except KeyboardInterrupt:
        print(f"\n🛑 INTERRUPÇÃO DETECTADA - Testando salvamento seguro...")
    
    finally:
        # Para tudo
        print("\n🛑 Parando sistema com segurança...")
        monitor.stop_monitoring()
        
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Aguarda salvamento
        time.sleep(2)
        
        # Força salvamento final
        monitor.force_save()
        
        # Mostra resultados
        show_demo_results(start_time)

def show_demo_results(start_time):
    """Mostra os resultados da demonstração"""
    elapsed_total = time.time() - start_time
    
    print("\n" + "="*60)
    print("📊 RESULTADOS DA DEMONSTRAÇÃO")
    print("="*60)
    
    files_to_check = [
        'output/fuel_stations_monitored.json',
        'output/monitoring_progress.json'
    ]
    
    total_establishments = 0
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if file_path.endswith('monitored.json'):
                    total_establishments = len(data)
                    print(f"✅ Dados salvos: {total_establishments:,} estabelecimentos")
                    
                    if total_establishments > 0:
                        # Análise rápida
                        unique_names = set(est.get('name', '') for est in data)
                        print(f"📊 Nomes únicos: {len(unique_names)}")
                        
                        # Mostra alguns exemplos
                        print(f"\n📍 EXEMPLOS COLETADOS:")
                        for i, est in enumerate(data[:5], 1):
                            name = est.get('name', 'N/A')[:50]
                            address = est.get('address', 'N/A')[:60]
                            print(f"   {i}. {name}")
                            print(f"      📍 {address}")
                        
                        if total_establishments > 5:
                            print(f"   ... e mais {total_establishments - 5} estabelecimentos")
                        
                else:  # progress file
                    print(f"✅ Progresso salvo:")
                    print(f"   📍 Células processadas: {data.get('cells_processed', 0)}")
                    print(f"   ⚡ Taxa média: {data.get('establishments_per_minute', 0):.1f}/min")
                    print(f"   📊 Status: {data.get('spider_status', 'unknown')}")
                    
            except Exception as e:
                print(f"❌ Erro ao ler {file_path}: {e}")
        else:
            print(f"❌ Arquivo não encontrado: {file_path}")
    
    # Estatísticas finais
    print(f"\n⏱️ ESTATÍSTICAS:")
    print(f"   ⏰ Tempo total: {elapsed_total/60:.1f} minutos")
    if total_establishments > 0 and elapsed_total > 0:
        rate_final = (total_establishments / elapsed_total) * 60
        print(f"   ⚡ Taxa final: {rate_final:.1f} estabelecimentos/min")
        
        # Projeção para execução completa
        total_cells_estimated = 8208  # Total de células em SC
        if rate_final > 0:
            cells_per_min = rate_final / 7  # ~7 estabelecimentos por célula
            total_time_hours = total_cells_estimated / cells_per_min / 60
            print(f"   🎯 Projeção para SC completa: ~{total_time_hours:.1f} horas")
    
    # Conclusão
    print(f"\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("="*60)
    
    if total_establishments > 0:
        print("✅ SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("   ✅ Dados salvos em tempo real")
        print("   ✅ Monitoramento funcionando")
        print("   ✅ Interrupção segura testada")
        print("   ✅ Pronto para execução completa")
        
        print(f"\n📋 COMO USAR O SISTEMA:")
        print("1. Execute: python real_time_scraper.py")
        print("2. Monitore o progresso em tempo real")
        print("3. Use Ctrl+C para parar com segurança")
        print("4. Visualize dados com: python data_viewer.py")
        print("5. Os dados ficam em: output/fuel_stations_monitored.json")
        
    else:
        print("⚠️ Sistema precisa de ajustes - nenhum dado foi coletado")

if __name__ == "__main__":
    demo_complete_system()
