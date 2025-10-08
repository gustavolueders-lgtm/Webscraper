#!/usr/bin/env python3
"""
Script para executar o scraper de postos de combustível
Otimizado para reduzir tempo de 54h para 2,5-3h
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def setup_environment():
    """Setup inicial do ambiente"""
    print("🔧 Configurando ambiente...")
    
    # Criar diretórios necessários
    os.makedirs('output', exist_ok=True)
    
    # Instalar dependências do Playwright
    try:
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], 
                      check=True, capture_output=True)
        print("✅ Playwright configurado")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro ao configurar Playwright: {e}")
        print("Execute manualmente: python -m playwright install chromium")

def clear_cache():
    """Limpar cache e arquivos anteriores"""
    print("🧹 Limpando cache anterior...")
    
    files_to_remove = [
        'output/fuel_stations.json',
        'output/scraping_progress.json',
        'output/grid_checkpoint.json',
        'output/scrapy.log',
        'output/metrics.json'
    ]
    
    removed_count = 0
    for file_path in files_to_remove:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                removed_count += 1
                print(f"  ❌ Removido: {file_path}")
        except Exception as e:
            print(f"  ⚠️ Erro ao remover {file_path}: {e}")
    
    # Limpar cache do Scrapy
    try:
        import shutil
        if os.path.exists('.scrapy'):
            shutil.rmtree('.scrapy')
            removed_count += 1
            print("  ❌ Removido: .scrapy/")
    except Exception as e:
        print(f"  ⚠️ Erro ao remover cache Scrapy: {e}")
    
    print(f"✅ Cache limpo! {removed_count} arquivos/diretórios removidos")

def run_scraper():
    """Executar o scraper"""
    print("🚀 Iniciando scraper otimizado...")
    print("📊 Configurações:")
    print("  - Grid: 5x5km em Santa Catarina")
    print("  - Termos: 'gas station' + 'posto de combustível'")
    print("  - Extração: Direta dos cards (sem visitar páginas)")
    print("  - Paralelização: 2 requests simultâneos")
    print("  - Tempo estimado: 2,5-3 horas")
    print()
    
    try:
        # Executar scrapy
        result = subprocess.run(['scrapy', 'crawl', 'simple_fuel'],
                              cwd=os.getcwd(), check=True)
        print("✅ Scraper concluído com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar scraper: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Scraper interrompido pelo usuário")
        return False

def show_results():
    """Mostrar resultados finais"""
    try:
        if os.path.exists('output/fuel_stations.json'):
            with open('output/fuel_stations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = len(data) if isinstance(data, list) else 0
                print(f"📊 Total de estabelecimentos coletados: {count}")
        
        if os.path.exists('output/scraping_progress.json'):
            with open('output/scraping_progress.json', 'r', encoding='utf-8') as f:
                progress = json.load(f)
                print(f"📈 Células processadas: {progress.get('cells_processed', 0)}")
                print(f"✅ Taxa de sucesso: {progress.get('success_rate', 0):.1f}%")
                print(f"⚡ Velocidade: {progress.get('processing_speed', 0):.1f} células/hora")
                print(f"🎯 Score de qualidade: {progress.get('data_quality_score', 0):.1f}%")
        
    except Exception as e:
        print(f"⚠️ Erro ao mostrar resultados: {e}")

def main():
    """Função principal"""
    print("=" * 60)
    print("⛽ GOOGLE MAPS FUEL STATIONS SCRAPER - OTIMIZADO")
    print("=" * 60)
    print(f"🕐 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Setup
    setup_environment()
    print()
    
    # Limpar cache
    clear_cache()
    print()
    
    # Executar scraper
    success = run_scraper()
    print()
    
    # Mostrar resultados
    if success:
        print("=" * 60)
        print("📊 RESULTADOS FINAIS")
        print("=" * 60)
        show_results()
    
    print()
    print(f"🕐 Finalizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
