#!/usr/bin/env python3
"""
Monitor de progresso do spider VPN em tempo real
"""

import time
import json
import os
from datetime import datetime

def monitor_spider_progress():
    """Monitora progresso do spider VPN"""
    print("🌐 MONITOR DE PROGRESSO - SPIDER VPN")
    print("=" * 60)
    print("📊 Monitorando spider 'simple_vpn' em tempo real")
    print("📄 Log: output/scrapy.log")
    print("💾 Dados: output/fuel_stations_monitored.json")
    print("💡 Pressione Ctrl+C para parar")
    print("=" * 60)
    
    start_time = time.time()
    last_cell = -1
    last_check_time = 0
    
    try:
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # Lê progresso do log
            progress = read_log_progress()
            
            # Lê dados salvos
            saved_data = read_saved_data()
            
            # Mostra status a cada 30 segundos
            if current_time - last_check_time >= 30:
                elapsed_str = f"{int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}"
                
                print(f"\n⏰ {elapsed_str} | "
                      f"🗺️ Célula {progress['current_cell']}/{progress['total_cells']} | "
                      f"🏪 {len(saved_data)} estabelecimentos | "
                      f"📊 {progress['pages_crawled']} páginas")
                
                # Mostra coordenadas atuais
                if progress['current_lat'] and progress['current_lon']:
                    print(f"📍 Posição atual: {progress['current_lat']:.4f}, {progress['current_lon']:.4f}")
                    
                    # Estima quando chegará em áreas urbanas
                    estimate_urban_arrival(progress)
                
                # Mostra estatísticas
                if progress['pages_crawled'] > 0:
                    rate = progress['pages_crawled'] / (elapsed_time / 60) if elapsed_time > 0 else 0
                    print(f"⚡ Taxa: {rate:.1f} páginas/min")
                    
                    # Projeção de tempo
                    remaining_cells = progress['total_cells'] - progress['current_cell']
                    if rate > 0:
                        estimated_hours = remaining_cells / (rate * 60)
                        print(f"⏳ Tempo estimado restante: {estimated_hours:.1f} horas")
                
                last_check_time = current_time
            
            # Mostra novos estabelecimentos
            if len(saved_data) > 0:
                print(f"\n🎉 ESTABELECIMENTOS ENCONTRADOS:")
                for i, est in enumerate(saved_data[-3:], 1):
                    name = est.get('name', 'N/A')[:40]
                    phone = est.get('phone', 'Sem telefone')
                    address = est.get('address', 'N/A')[:30]
                    print(f"   {i}. {name}")
                    print(f"      📞 {phone}")
                    print(f"      📍 {address}")
            
            time.sleep(10)  # Verifica a cada 10 segundos
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitor interrompido pelo usuário")
        show_final_summary(start_time, progress, saved_data)

def read_log_progress():
    """Lê progresso do arquivo de log"""
    progress = {
        'current_cell': 0,
        'total_cells': 7904,
        'pages_crawled': 0,
        'current_lat': None,
        'current_lon': None,
        'last_activity': None
    }
    
    try:
        if os.path.exists('output/scrapy.log'):
            with open('output/scrapy.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for line in lines:
                    # Extrai número da célula atual
                    if '🔍 Processando célula' in line:
                        try:
                            parts = line.split('célula ')[1].split(':')
                            cell_num = int(parts[0])
                            coords = parts[1].strip().split(', ')
                            lat = float(coords[0])
                            lon = float(coords[1])
                            
                            progress['current_cell'] = cell_num
                            progress['current_lat'] = lat
                            progress['current_lon'] = lon
                        except:
                            pass
                    
                    # Extrai total de células
                    elif 'total_cells' in line and 'total_requests' in line:
                        try:
                            import re
                            match = re.search(r"'total_cells': (\d+)", line)
                            if match:
                                progress['total_cells'] = int(match.group(1))
                        except:
                            pass
                    
                    # Extrai páginas processadas
                    elif 'Crawled' in line and 'pages' in line:
                        try:
                            import re
                            match = re.search(r'Crawled (\d+) pages', line)
                            if match:
                                progress['pages_crawled'] = int(match.group(1))
                        except:
                            pass
                    
                    # Última atividade
                    if line.strip():
                        progress['last_activity'] = line.strip()[-50:]
    
    except Exception as e:
        print(f"⚠️ Erro ao ler log: {e}")
    
    return progress

def read_saved_data():
    """Lê dados salvos"""
    try:
        if os.path.exists('output/fuel_stations_monitored.json'):
            with open('output/fuel_stations_monitored.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
    except:
        pass
    
    return []

def estimate_urban_arrival(progress):
    """Estima quando chegará em áreas urbanas"""
    current_lat = progress.get('current_lat', -29.35)
    current_lon = progress.get('current_lon', -53.83)
    
    # Coordenadas de cidades principais
    cities = [
        {'name': 'Chapecó', 'lat': -27.1009, 'lon': -52.6156},
        {'name': 'Florianópolis', 'lat': -27.5954, 'lon': -48.5480},
        {'name': 'Joinville', 'lat': -26.3044, 'lon': -48.8487},
        {'name': 'Blumenau', 'lat': -26.9194, 'lon': -49.0661},
    ]
    
    # Encontra cidade mais próxima na direção do grid
    closest_city = None
    min_distance = float('inf')
    
    for city in cities:
        # Verifica se a cidade está na direção do grid (leste/norte)
        if city['lat'] >= current_lat and city['lon'] >= current_lon:
            distance = ((city['lat'] - current_lat) ** 2 + (city['lon'] - current_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_city = city
    
    if closest_city:
        # Estima células até a cidade
        lat_diff = closest_city['lat'] - current_lat
        lon_diff = closest_city['lon'] - current_lon
        
        lat_step = 0.045  # ~5km
        lon_step = 0.062  # ~5km ajustado
        
        cells_to_city = int((lat_diff / lat_step) * (lon_diff / lon_step))
        
        if cells_to_city > 0:
            current_rate = progress['pages_crawled'] / max(1, progress['current_cell'])
            estimated_time = cells_to_city / max(0.1, current_rate)
            
            print(f"🏙️ Próxima cidade: {closest_city['name']}")
            print(f"📏 ~{cells_to_city} células até lá")
            print(f"⏰ ~{estimated_time:.1f} minutos estimados")

def show_final_summary(start_time, progress, saved_data):
    """Mostra resumo final"""
    elapsed_total = time.time() - start_time
    
    print("\n" + "="*60)
    print("📊 RESUMO FINAL DO MONITORAMENTO")
    print("="*60)
    
    print(f"⏰ Tempo total de monitoramento: {elapsed_total/60:.1f} minutos")
    print(f"🗺️ Células processadas: {progress['current_cell']}/{progress['total_cells']}")
    print(f"📊 Páginas processadas: {progress['pages_crawled']}")
    print(f"🏪 Estabelecimentos encontrados: {len(saved_data)}")
    
    if progress['current_lat'] and progress['current_lon']:
        print(f"📍 Última posição: {progress['current_lat']:.4f}, {progress['current_lon']:.4f}")
    
    if len(saved_data) > 0:
        print(f"\n🎉 DADOS COLETADOS:")
        for est in saved_data:
            print(f"   🏪 {est.get('name', 'N/A')}")
            if est.get('phone'):
                print(f"      📞 {est['phone']}")
    else:
        print(f"\n⚠️ Nenhum estabelecimento encontrado ainda")
        print("💡 Spider ainda está em áreas rurais/remotas")
        print("🏙️ Aguarde chegar em áreas urbanas")
    
    print("="*60)

def main():
    """Função principal"""
    print("🌐 MONITOR DE PROGRESSO DO SPIDER VPN")
    print("⚠️ Certifique-se que o spider está rodando:")
    print("   scrapy crawl simple_vpn --set SETTINGS_MODULE=business_scraper.settings_stealth")
    print()
    
    choice = input("Iniciar monitoramento? (s/n): ").strip().lower()
    
    if choice == 's':
        monitor_spider_progress()
    else:
        print("👋 Monitor disponível quando precisar!")

if __name__ == "__main__":
    main()
