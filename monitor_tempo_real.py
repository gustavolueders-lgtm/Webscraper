#!/usr/bin/env python3
"""
Monitor de progresso em tempo real
Atualiza a cada 30 segundos
"""

import json
import os
import time
import re
from datetime import datetime, timedelta

def extrair_progresso_logs():
    """Extrai progresso atual dos logs"""
    
    current_cell = 0
    pages_crawled = 0
    start_time = None
    
    try:
        if not os.path.exists('output/scrapy.log'):
            return current_cell, pages_crawled, start_time
        
        with open('output/scrapy.log', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procura por células processadas
        cell_matches = re.findall(r'cell_index["\']:\s*(\d+)', content)
        if cell_matches:
            current_cell = max(int(x) for x in cell_matches)
        
        # Conta páginas crawladas
        page_matches = re.findall(r'Crawled \(\d+\)', content)
        pages_crawled = len(page_matches)
        
        # Procura por tempo de início
        start_matches = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', content)
        if start_matches:
            start_time_str = start_matches[0]
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        
        return current_cell, pages_crawled, start_time
        
    except Exception as e:
        print(f"   ⚠️ Erro ao ler logs: {e}")
        return current_cell, pages_crawled, start_time

def carregar_dados_salvos():
    """Carrega dados salvos do JSON"""
    
    try:
        if os.path.exists('output/fuel_stations_monitored.json'):
            with open('output/fuel_stations_monitored.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        return []
    except Exception as e:
        print(f"   ⚠️ Erro ao ler JSON: {e}")
        return []

def extrair_ultimos_estabelecimentos():
    """Extrai últimos estabelecimentos dos logs"""
    
    try:
        if not os.path.exists('output/scrapy.log'):
            return []
        
        with open('output/scrapy.log', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procura por linhas com dados de estabelecimentos
        pattern = r'🏪 ESTABLISHMENT_DATA: ({.*?})'
        matches = re.findall(pattern, content)
        
        establishments = []
        for match in matches[-10:]:  # Últimos 10
            try:
                # Converte aspas simples para duplas para JSON válido
                json_str = match.replace("'", '"').replace('None', 'null').replace('True', 'true').replace('False', 'false')
                data = json.loads(json_str)
                establishments.append(data)
            except:
                continue
        
        return establishments[-3:]  # Últimos 3
        
    except Exception as e:
        print(f"   ⚠️ Erro ao extrair últimos: {e}")
        return []

def formatar_tempo(seconds):
    """Formata tempo em horas:minutos:segundos"""
    if seconds is None:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    elif minutes > 0:
        return f"{minutes}m{secs:02d}s"
    else:
        return f"{secs}s"

def main():
    """Função principal do monitor"""
    
    print("🚀 MONITOR DE PROGRESSO EM TEMPO REAL")
    print("=" * 60)
    print("📊 Atualizações a cada 30 segundos")
    print("🔄 Pressione Ctrl+C para parar")
    print("=" * 60)
    
    while True:
        try:
            # Limpa tela (funciona no Windows)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🚀 MONITOR DE PROGRESSO EM TEMPO REAL")
            print("=" * 60)
            
            # Extrai progresso dos logs
            current_cell, pages_crawled, start_time = extrair_progresso_logs()
            
            # Carrega dados salvos
            establishments = carregar_dados_salvos()
            
            # Calcula tempo decorrido
            elapsed_seconds = None
            if start_time:
                elapsed_seconds = (datetime.now() - start_time).total_seconds()
            
            elapsed_str = formatar_tempo(elapsed_seconds)
            
            # Conta telefones
            phones_count = sum(1 for est in establishments if est.get('phone'))
            phone_rate = (phones_count / len(establishments) * 100) if establishments else 0
            
            # Calcula taxa de páginas
            page_rate = 0
            if elapsed_seconds and elapsed_seconds > 0:
                page_rate = pages_crawled / (elapsed_seconds / 60)  # páginas por minuto
            
            # Mostra status principal
            print(f"⏰ Tempo: {elapsed_str}")
            print(f"🗺️ Célula: {current_cell + 1}/7904 ({(current_cell + 1)/7904*100:.1f}%)")
            print(f"🏪 Estabelecimentos: {len(establishments)}")
            print(f"📞 Telefones: {phones_count} ({phone_rate:.1f}%)")
            print(f"📄 Páginas: {pages_crawled} ({page_rate:.1f}/min)")
            
            print("\n" + "=" * 60)
            
            # Mostra últimos estabelecimentos
            ultimos = extrair_ultimos_estabelecimentos()
            if ultimos:
                print("🏪 ÚLTIMOS ESTABELECIMENTOS COLETADOS:")
                for i, est in enumerate(ultimos, 1):
                    name = est.get('name', 'N/A')
                    phone = est.get('phone', 'Sem telefone')
                    rating = est.get('rating', 'N/A')
                    cell_index = est.get('cell_index', 'N/A')
                    
                    print(f"   {i}. {name}")
                    print(f"      📞 {phone}")
                    print(f"      ⭐ {rating}")
                    print(f"      🗺️ Célula {cell_index}")
                    print()
            else:
                print("🏪 Aguardando dados...")
            
            print("=" * 60)
            print(f"🔄 Próxima atualização em 30 segundos...")
            print(f"📊 Status: Spider rodando | VPN ativo | Dados sendo coletados")
            
            # Aguarda 30 segundos
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor interrompido pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro no monitor: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
