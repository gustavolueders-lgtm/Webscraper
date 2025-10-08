#!/usr/bin/env python3
"""
Teste específico para verificar se o salvamento incremental está funcionando
"""

import os
import subprocess
import json
import time
import signal
from datetime import datetime

def monitor_file():
    """Monitora o arquivo de saída em tempo real"""
    output_file = 'output/fuel_stations.json'
    
    print("📊 MONITORANDO ARQUIVO DE SAÍDA...")
    print("=" * 50)
    
    last_count = 0
    start_time = time.time()
    
    while True:
        try:
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    current_count = len(data)
                    
                if current_count != last_count:
                    elapsed = time.time() - start_time
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | "
                          f"📄 {current_count:,} itens | "
                          f"⚡ +{current_count - last_count} novos | "
                          f"🕐 {elapsed:.0f}s")
                    last_count = current_count
                    
                    # Se chegou a 100 itens, teste o Ctrl+C
                    if current_count >= 100:
                        print("\n🧪 TESTE: Chegou a 100 itens!")
                        print("⚠️ Pressione Ctrl+C para testar salvamento...")
                        
            else:
                print(f"⏳ {datetime.now().strftime('%H:%M:%S')} | Aguardando arquivo...")
                
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n🛑 Ctrl+C detectado!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(2)

def clear_output():
    """Limpa arquivos de saída"""
    files_to_remove = [
        'output/fuel_stations.json',
        'output/fuel_stations_backup.json',
        'output/scraping_progress.json'
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removido: {file_path}")

def test_incremental_save():
    """Testa o salvamento incremental"""
    print("🧪 TESTE DE SALVAMENTO INCREMENTAL")
    print("=" * 50)
    
    # Limpa arquivos anteriores
    clear_output()
    
    # Inicia o scraper em background
    print("🚀 Iniciando scraper...")
    process = subprocess.Popen(
        ['scrapy', 'crawl', 'simple_fuel'],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Monitora o arquivo
        monitor_file()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrompendo teste...")
        
    finally:
        # Termina o processo
        if process.poll() is None:
            print("🔄 Terminando scraper...")
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Verifica resultado final
        check_final_result()

def check_final_result():
    """Verifica o resultado final após interrupção"""
    print("\n📋 VERIFICANDO RESULTADO FINAL...")
    print("=" * 40)
    
    files_to_check = [
        'output/fuel_stations.json',
        'output/fuel_stations_backup.json',
        'output/scraping_progress.json'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        count = len(data)
                        print(f"✅ {file_path}: {count:,} itens")
                        
                        # Mostra primeiro item como exemplo
                        if count > 0:
                            first_item = data[0]
                            print(f"   📝 Exemplo: {first_item.get('name', 'N/A')}")
                    else:
                        print(f"✅ {file_path}: Dados de progresso")
                        
            except Exception as e:
                print(f"❌ {file_path}: Erro ao ler - {e}")
        else:
            print(f"❌ {file_path}: Arquivo não encontrado")

def main():
    print("🔬 TESTE DE SALVAMENTO INCREMENTAL")
    print("=" * 60)
    print("Este teste vai:")
    print("1. Limpar arquivos anteriores")
    print("2. Iniciar o scraper")
    print("3. Monitorar salvamento em tempo real")
    print("4. Testar interrupção com Ctrl+C")
    print("5. Verificar se dados foram preservados")
    print("\n⚠️ Pressione Enter para continuar ou Ctrl+C para cancelar...")
    
    try:
        input()
        test_incremental_save()
    except KeyboardInterrupt:
        print("\n❌ Teste cancelado pelo usuário")

if __name__ == "__main__":
    main()
