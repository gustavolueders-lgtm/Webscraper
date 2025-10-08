#!/usr/bin/env python3
"""
Teste simples do sistema de monitoramento
"""

import os
import time
import subprocess
import json
from log_monitor import LogMonitor

def test_simple_system():
    """Testa o sistema com spider simples"""
    print("🧪 TESTE SIMPLES DO SISTEMA")
    print("=" * 40)
    
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
    
    print("\n🚀 Iniciando teste de 30 segundos...")
    
    # Inicia monitor
    monitor = LogMonitor()
    monitor.start_monitoring()
    
    # Inicia spider simples
    process = subprocess.Popen(
        ['scrapy', 'crawl', 'simple_monitored'],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    start_time = time.time()
    last_count = 0
    
    try:
        while time.time() - start_time < 30:  # 30 segundos
            # Verifica se processo ainda está rodando
            if process.poll() is not None:
                print(f"🏁 Spider finalizado (código: {process.returncode})")
                break
            
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
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido")
    
    finally:
        # Para tudo
        print("\n🛑 Parando sistema...")
        monitor.stop_monitoring()
        
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Aguarda um pouco
        time.sleep(2)
        
        # Força salvamento
        monitor.force_save()
        
        # Verifica resultados
        check_simple_results()

def check_simple_results():
    """Verifica os resultados do teste simples"""
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
                        print(f"   ⭐ Rating: {first.get('rating', 'N/A')}")
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
    
    # Verifica log também
    if os.path.exists('output/scrapy.log'):
        print(f"\n📄 Verificando log...")
        with open('output/scrapy.log', 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        if "🏪 ESTABLISHMENT_DATA:" in log_content:
            print("✅ Log contém dados de estabelecimentos")
        else:
            print("❌ Log não contém dados de estabelecimentos")
            success = False
    
    # Conclusão
    print(f"\n🎯 RESULTADO DO TESTE:")
    if success:
        print("🎉 SUCESSO! Sistema funcionando!")
        print("   ✅ Dados salvos corretamente")
        print("   ✅ Monitoramento funcionando")
        print("   ✅ Sistema pronto para uso")
        
        print(f"\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python real_time_scraper.py")
        print("2. Ou use o spider real: scrapy crawl simple_fuel")
        print("3. Monitore com: python data_viewer.py")
        
    else:
        print("😔 FALHA! Sistema precisa de ajustes")

if __name__ == "__main__":
    test_simple_system()
