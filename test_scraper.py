#!/usr/bin/env python3
"""
Script de teste para validar o scraper antes da execução completa
Testa com apenas 1 célula do grid (2 buscas)
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime

def clear_test_files():
    """Limpar arquivos de teste"""
    test_files = [
        'output/fuel_stations.json',
        'output/scraping_progress.json',
        'output/grid_checkpoint.json',
        'output/scrapy.log'
    ]
    
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

def create_test_spider():
    """Criar versão de teste do spider (apenas 1 célula)"""
    test_spider_content = '''
import scrapy
from business_scraper.spiders.fuel_stations_spider import FuelStationsSpider

class TestFuelStationsSpider(FuelStationsSpider):
    name = 'test_fuel_stations'
    
    def _generate_grid_cells(self):
        """Generate only 1 test cell"""
        # Florianópolis center coordinates
        test_lat = -27.5954
        test_lon = -48.5480
        
        cells = []
        for term in self.search_terms:
            cells.append((test_lat, test_lon, term))
        
        self.logger.info(f"TEST MODE: Generated {len(cells)} test searches")
        return cells
'''
    
    with open('business_scraper/spiders/test_fuel_stations_spider.py', 'w', encoding='utf-8') as f:
        f.write(test_spider_content)

def run_test():
    """Executar teste"""
    print("🧪 TESTE DO SCRAPER - 1 CÉLULA")
    print("=" * 50)
    
    # Limpar arquivos anteriores
    clear_test_files()
    print("✅ Arquivos de teste limpos")
    
    # Criar spider de teste
    create_test_spider()
    print("✅ Spider de teste criado")
    
    # Executar teste
    print("🚀 Iniciando teste...")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'test_fuel_stations'],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Teste concluído em {elapsed_time:.1f} segundos")
            
            # Verificar resultados
            check_test_results()
            
        else:
            print(f"❌ Teste falhou:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Teste expirou (timeout de 5 minutos)")
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")

def check_test_results():
    """Verificar resultados do teste"""
    print("\n📊 RESULTADOS DO TESTE")
    print("=" * 30)
    
    # Verificar arquivo de resultados
    if os.path.exists('output/fuel_stations.json'):
        try:
            with open('output/fuel_stations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = len(data) if isinstance(data, list) else 0
                print(f"📄 Estabelecimentos coletados: {count}")
                
                if count > 0:
                    print("✅ Extração de dados funcionando")
                    
                    # Mostrar exemplo
                    example = data[0]
                    print(f"📝 Exemplo de dados:")
                    print(f"   Nome: {example.get('name', 'N/A')}")
                    print(f"   Rating: {example.get('rating', 'N/A')}")
                    print(f"   Endereço: {example.get('address', 'N/A')}")
                    print(f"   Place ID: {example.get('place_id', 'N/A')}")
                else:
                    print("⚠️ Nenhum estabelecimento coletado")
                    
        except Exception as e:
            print(f"❌ Erro ao ler resultados: {e}")
    else:
        print("❌ Arquivo de resultados não encontrado")
    
    # Verificar progresso
    if os.path.exists('output/scraping_progress.json'):
        try:
            with open('output/scraping_progress.json', 'r', encoding='utf-8') as f:
                progress = json.load(f)
                print(f"📈 Células processadas: {progress.get('cells_processed', 0)}")
                print(f"✅ Taxa de sucesso: {progress.get('success_rate', 0):.1f}%")
                print(f"🎯 Score de qualidade: {progress.get('data_quality_score', 0):.1f}%")
        except Exception as e:
            print(f"❌ Erro ao ler progresso: {e}")
    
    # Verificar logs
    if os.path.exists('output/scrapy.log'):
        print("📋 Log criado com sucesso")
    
    print("\n🎯 VALIDAÇÕES:")
    
    # Validação 1: Dados extraídos
    if os.path.exists('output/fuel_stations.json'):
        print("✅ Extração de dados dos cards funcionando")
    else:
        print("❌ Falha na extração de dados")
    
    # Validação 2: Deduplicação
    try:
        with open('output/fuel_stations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            place_ids = [item.get('place_id') for item in data if item.get('place_id')]
            unique_ids = set(place_ids)
            if len(place_ids) == len(unique_ids):
                print("✅ Deduplicação por Place ID funcionando")
            else:
                print(f"⚠️ Duplicatas encontradas: {len(place_ids) - len(unique_ids)}")
    except:
        print("❌ Não foi possível verificar deduplicação")
    
    # Validação 3: Campos obrigatórios
    try:
        with open('output/fuel_stations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                required_fields = ['name', 'place_id']
                valid_items = all(
                    all(item.get(field) for field in required_fields)
                    for item in data
                )
                if valid_items:
                    print("✅ Campos obrigatórios presentes")
                else:
                    print("⚠️ Alguns itens sem campos obrigatórios")
    except:
        print("❌ Não foi possível verificar campos")

def cleanup_test():
    """Limpar arquivos de teste"""
    try:
        os.remove('business_scraper/spiders/test_fuel_stations_spider.py')
        print("🧹 Arquivos de teste removidos")
    except:
        pass

def main():
    print("🧪 SISTEMA DE TESTE DO SCRAPER")
    print("Testando com 1 célula do grid (Florianópolis)")
    print("=" * 60)
    
    try:
        run_test()
    finally:
        cleanup_test()
    
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Se o teste passou, execute: python run_scraper.py")
    print("2. Ou use a interface: streamlit run app.py")
    print("3. Monitore o progresso em tempo real")
    print("=" * 60)

if __name__ == "__main__":
    main()
