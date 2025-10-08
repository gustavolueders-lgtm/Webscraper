#!/usr/bin/env python3
"""
Script para reiniciar o scraper do Google Maps com salvamento incremental
"""

import os
import subprocess
import json
from datetime import datetime

def clear_cache():
    """Limpa cache e arquivos temporários"""
    print("🧹 Limpando cache...")
    
    # Remove arquivos de cache
    cache_dirs = [
        '.scrapy',
        '__pycache__',
        'business_scraper/__pycache__',
        'business_scraper/spiders/__pycache__',
        'business_scraper/utils/__pycache__'
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"   ✅ Removido: {cache_dir}")
            except Exception as e:
                print(f"   ⚠️ Erro ao remover {cache_dir}: {e}")
    
    print("✅ Cache limpo!")

def backup_existing_data():
    """Faz backup dos dados existentes se houver"""
    if os.path.exists('output/fuel_stations.json'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'output/fuel_stations_backup_{timestamp}.json'
        
        try:
            import shutil
            shutil.copy2('output/fuel_stations.json', backup_file)
            print(f"📦 Backup criado: {backup_file}")
        except Exception as e:
            print(f"⚠️ Erro ao criar backup: {e}")

def show_progress():
    """Mostra o progresso atual"""
    if os.path.exists('output/scraping_progress.json'):
        try:
            with open('output/scraping_progress.json', 'r', encoding='utf-8') as f:
                progress = json.load(f)
            
            print("\n📊 PROGRESSO ANTERIOR:")
            print(f"   🔢 Células processadas: {progress.get('cells_processed', 0):,}")
            print(f"   🏪 Estabelecimentos encontrados: {progress.get('establishments_found', 0):,}")
            print(f"   📈 Taxa de sucesso: {progress.get('success_rate', 0):.1f}%")
            print(f"   ⚡ Velocidade: {progress.get('processing_speed', 0):.0f} células/hora")
            
        except Exception as e:
            print(f"⚠️ Erro ao ler progresso: {e}")

def main():
    print("🚀 REINICIANDO SCRAPER DO GOOGLE MAPS")
    print("=" * 50)
    
    # Mostra progresso anterior
    show_progress()
    
    # Faz backup se necessário
    backup_existing_data()
    
    # Limpa cache
    clear_cache()
    
    print("\n🔄 Iniciando scraper com salvamento incremental...")
    print("💾 Dados serão salvos a cada 100 estabelecimentos")
    print("⚠️ Use Ctrl+C para parar (dados não serão perdidos)")
    
    try:
        # Executa o scraper
        result = subprocess.run(
            ['scrapy', 'crawl', 'simple_fuel'], 
            cwd=os.getcwd(),
            check=True
        )
        
        print("\n✅ Scraper concluído com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Scraper interrompido pelo usuário")
        print("💾 Dados salvos até o momento da interrupção")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro ao executar scraper: {e}")
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    # Mostra resultado final
    if os.path.exists('output/fuel_stations.json'):
        try:
            with open('output/fuel_stations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"\n📄 Resultado final: {len(data):,} estabelecimentos salvos")
        except Exception as e:
            print(f"⚠️ Erro ao ler resultado: {e}")

if __name__ == "__main__":
    main()
