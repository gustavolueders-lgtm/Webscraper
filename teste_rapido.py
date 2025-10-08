#!/usr/bin/env python3
"""
Teste rápido para verificar salvamento direto
"""

import os
import subprocess
import json
import time
import signal

def clear_files():
    """Limpa arquivos de teste"""
    files = [
        'output/fuel_stations_direct.json',
        'output/fuel_stations.json',
        'output/scraping_progress.json'
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removido: {file_path}")

def run_quick_test():
    """Executa teste rápido com limite de itens"""
    print("🧪 TESTE RÁPIDO - SALVAMENTO DIRETO")
    print("=" * 50)
    
    # Limpa arquivos
    clear_files()
    
    # Executa scraper por tempo limitado
    print("🚀 Iniciando scraper por 60 segundos...")
    
    process = subprocess.Popen(
        ['scrapy', 'crawl', 'simple_fuel'],
        cwd=os.getcwd()
    )
    
    start_time = time.time()
    
    try:
        # Monitora por 60 segundos
        while time.time() - start_time < 60:
            # Verifica arquivo direto
            if os.path.exists('output/fuel_stations_direct.json'):
                try:
                    with open('output/fuel_stations_direct.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"📄 Arquivo direto: {len(data)} itens")
                    
                    if len(data) >= 50:  # Para quando chegar a 50 itens
                        print("✅ Chegou a 50 itens! Parando teste...")
                        break
                        
                except Exception as e:
                    print(f"⚠️ Erro ao ler arquivo: {e}")
            
            time.sleep(5)
        
        print("\n🛑 Interrompendo scraper...")
        
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    
    finally:
        # Para o processo
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Verifica resultado
        check_results()

def check_results():
    """Verifica os resultados do teste"""
    print("\n📋 RESULTADO DO TESTE:")
    print("=" * 30)
    
    files_to_check = [
        'output/fuel_stations_direct.json',
        'output/fuel_stations.json'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"✅ {file_path}: {len(data)} itens")
                
                if len(data) > 0:
                    first_item = data[0]
                    print(f"   📝 Exemplo: {first_item.get('name', 'N/A')}")
                    print(f"   📍 Local: {first_item.get('address', 'N/A')}")
                    
            except Exception as e:
                print(f"❌ {file_path}: Erro - {e}")
        else:
            print(f"❌ {file_path}: Não encontrado")
    
    # Conclusão
    direct_exists = os.path.exists('output/fuel_stations_direct.json')
    pipeline_exists = os.path.exists('output/fuel_stations.json')
    
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   Salvamento direto: {'✅ FUNCIONOU' if direct_exists else '❌ FALHOU'}")
    print(f"   Pipeline padrão: {'✅ FUNCIONOU' if pipeline_exists else '❌ FALHOU'}")
    
    if direct_exists:
        print("\n🎉 SALVAMENTO DIRETO ESTÁ FUNCIONANDO!")
        print("   Os dados agora são preservados mesmo com Ctrl+C")
    else:
        print("\n😔 Salvamento direto ainda não está funcionando")

if __name__ == "__main__":
    run_quick_test()
