#!/usr/bin/env python3
"""
Teste do sistema completo de monitoramento
"""

import os
import time
import subprocess
import json
from log_monitor import LogMonitor

def test_system():
    """Testa o sistema completo"""
    print("🧪 TESTE DO SISTEMA COMPLETO")
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
    
    print("\n🚀 Iniciando teste de 60 segundos...")
    
    # Inicia monitor
    monitor = LogMonitor()
    monitor.start_monitoring()
    
    # Inicia spider
    process = subprocess.Popen(
        ['scrapy', 'crawl', 'monitored'],
        cwd=os.getcwd()
    )
    
    start_time = time.time()
    last_count = 0
    
    try:
        while time.time() - start_time < 60:  # 60 segundos
            stats = monitor.get_stats()
            current_count = stats['total_establishments']
            
            if current_count != last_count:
                elapsed = time.time() - start_time
                print(f"⏰ {elapsed:.0f}s | 🏪 {current_count} estabelecimentos | 📍 {stats['cells_processed']} células")
                
                # Mostra últimos estabelecimentos
                latest = monitor.get_latest_establishments(2)
                for est in latest:
                    print(f"   📍 {est.get('name', 'N/A')} - {est.get('address', 'N/A')}")
                
                last_count = current_count
            
            time.sleep(3)
    
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido")
    
    finally:
        # Para tudo
        print("\n🛑 Parando sistema...")
        monitor.stop_monitoring()
        
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Força salvamento
        monitor.force_save()
        
        # Verifica resultados
        check_results()

def check_results():
    """Verifica os resultados do teste"""
    print("\n📋 VERIFICANDO RESULTADOS:")
    print("-" * 30)
    
    files_to_check = [
        'output/fuel_stations_monitored.json',
        'output/monitoring_progress.json'
    ]
    
    success = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if file_path.endswith('monitored.json'):
                    count = len(data)
                    print(f"✅ {file_path}: {count} estabelecimentos")
                    
                    if count > 0:
                        first = data[0]
                        print(f"   📝 Exemplo: {first.get('name', 'N/A')}")
                        print(f"   📍 Local: {first.get('address', 'N/A')}")
                        print(f"   🆔 Place ID: {first.get('place_id', 'N/A')}")
                    else:
                        success = False
                        
                else:  # progress file
                    print(f"✅ {file_path}: Progresso salvo")
                    print(f"   📊 Total: {data.get('total_establishments', 0)}")
                    print(f"   📍 Células: {data.get('cells_processed', 0)}")
                    print(f"   ⚡ Taxa: {data.get('establishments_per_minute', 0):.1f}/min")
                    
            except Exception as e:
                print(f"❌ {file_path}: Erro - {e}")
                success = False
        else:
            print(f"❌ {file_path}: Não encontrado")
            success = False
    
    # Conclusão
    print(f"\n🎯 RESULTADO DO TESTE:")
    if success:
        print("🎉 SUCESSO! Sistema funcionando perfeitamente!")
        print("   ✅ Dados salvos corretamente")
        print("   ✅ Monitoramento em tempo real funcionando")
        print("   ✅ Sistema pronto para uso completo")
        
        print(f"\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python real_time_scraper.py")
        print("2. Monitore o progresso em tempo real")
        print("3. Use Ctrl+C para parar com segurança")
        print("4. Visualize dados com: python data_viewer.py")
        
    else:
        print("😔 FALHA! Sistema ainda precisa de ajustes")

if __name__ == "__main__":
    test_system()
