#!/usr/bin/env python3
"""
Teste simples do spider simplificado
"""

import os
import subprocess
import json
import time

def clear_files():
    """Limpar arquivos de teste"""
    files = ['output/fuel_stations.json', 'output/scraping_progress.json', 'output/scrapy.log']
    for f in files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except:
            pass

def test_simple_spider():
    """Testar spider simples"""
    print("🧪 TESTE DO SPIDER SIMPLES")
    print("=" * 40)
    
    clear_files()
    print("✅ Arquivos limpos")
    
    print("🚀 Executando spider simples...")
    start_time = time.time()
    
    try:
        # Executar apenas 1 request para teste
        result = subprocess.run([
            'scrapy', 'crawl', 'simple_fuel', 
            '-s', 'CLOSESPIDER_ITEMCOUNT=10',  # Parar após 10 itens
            '-s', 'CLOSESPIDER_PAGECOUNT=2'    # Parar após 2 páginas
        ], capture_output=True, text=True, timeout=120)
        
        elapsed = time.time() - start_time
        
        print(f"⏱️ Tempo: {elapsed:.1f}s")
        print(f"📊 Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Spider executou sem erros")
        else:
            print("❌ Spider teve erros:")
            print("STDOUT:", result.stdout[-500:])  # Últimas 500 chars
            print("STDERR:", result.stderr[-500:])
        
        # Verificar resultados
        if os.path.exists('output/fuel_stations.json'):
            with open('output/fuel_stations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📄 Estabelecimentos coletados: {len(data)}")
                
                if data:
                    print("📝 Primeiro resultado:")
                    first = data[0]
                    print(f"   Nome: {first.get('name')}")
                    print(f"   Place ID: {first.get('place_id')}")
                    print(f"   Endereço: {first.get('address')}")
        else:
            print("❌ Nenhum arquivo de resultado criado")
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - spider demorou muito")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_simple_spider()
