#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigação dos casos "Não encontrado"
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def investigar_casos_nao_encontrados():
    """Investiga por que alguns casos retornam 'Não encontrado'"""
    
    # Carregar dados
    df = pd.read_excel('../estabelecimentos_com_cidade.xlsx')
    gdf = gpd.read_file('../IBGE/BR_Municipios_2024.shp')
    gdf = gdf.to_crs('EPSG:4326')
    
    # Filtrar casos não encontrados
    nao_encontrados = df[df['cidade'] == 'Não encontrado']
    
    print("🔍 INVESTIGAÇÃO DOS CASOS 'NÃO ENCONTRADO'")
    print("=" * 60)
    print(f"Total de casos não encontrados: {len(nao_encontrados)}")
    
    # Analisar alguns casos específicos
    casos_teste = nao_encontrados.head(5)
    
    for idx, row in casos_teste.iterrows():
        nome = row['nome']
        lat = row['latitude']
        lon = row['longitude']
        
        print(f"\n📍 CASO: {nome}")
        print(f"   Coordenadas: {lat}, {lon}")
        
        # Criar ponto
        ponto = Point(lon, lat)
        
        # Verificar se está dentro dos limites do Brasil
        lat_ok = -33.75 <= lat <= 5.27
        lon_ok = -73.98 <= lon <= -28.84
        print(f"   Dentro dos limites do Brasil: Lat={lat_ok}, Lon={lon_ok}")
        
        if lat_ok and lon_ok:
            # Procurar municípios próximos (buffer de 0.05 graus ~ 5.5km)
            buffer_area = ponto.buffer(0.05)
            municipios_proximos = gdf[gdf.geometry.intersects(buffer_area)]
            
            print(f"   Municípios próximos (raio ~5.5km): {len(municipios_proximos)}")
            
            if len(municipios_proximos) > 0:
                # Mostrar os 3 mais próximos
                distancias = []
                for _, mun in municipios_proximos.iterrows():
                    dist = ponto.distance(mun.geometry.centroid)
                    distancias.append((mun['NM_MUN'], mun['SIGLA_UF'], dist))
                
                distancias.sort(key=lambda x: x[2])
                
                print("   Os 3 mais próximos:")
                for i, (cidade, uf, dist) in enumerate(distancias[:3]):
                    km_aprox = dist * 111  # Conversão aproximada para km
                    print(f"     {i+1}. {cidade}-{uf} (~{km_aprox:.1f}km)")
                
                # Verificar se algum contém o ponto exato
                municipio_exato = gdf[gdf.geometry.contains(ponto)]
                if len(municipio_exato) > 0:
                    print("   ✅ ENCONTRADO município que contém o ponto!")
                    for _, mun in municipio_exato.iterrows():
                        print(f"      {mun['NM_MUN']} - {mun['SIGLA_UF']}")
                else:
                    print("   ❌ Nenhum município contém este ponto exato")
                    print("   Possíveis causas:")
                    print("     - Ponto no oceano/água")
                    print("     - Área não mapeada")
                    print("     - Fronteira entre municípios")
                    print("     - Imprecisão nas coordenadas")
            else:
                print("   ❌ Nenhum município encontrado próximo")
        else:
            print("   ❌ Coordenadas fora dos limites do Brasil")

def verificar_borracharia_kiko():
    """Verifica especificamente a Borracharia do Kiko"""
    
    print("\n🎯 ANÁLISE ESPECÍFICA: BORRACHARIA DO KIKO")
    print("=" * 60)
    
    # Coordenadas da Borracharia do Kiko
    lat_kiko = -26.016667
    lon_kiko = -48.477589
    
    print(f"Coordenadas: {lat_kiko}, {lon_kiko}")
    
    # Carregar shapefile
    gdf = gpd.read_file('../IBGE/BR_Municipios_2024.shp')
    gdf = gdf.to_crs('EPSG:4326')
    
    # Criar ponto
    ponto_kiko = Point(lon_kiko, lat_kiko)
    
    # Verificar limites
    lat_ok = -33.75 <= lat_kiko <= 5.27
    lon_ok = -73.98 <= lon_kiko <= -28.84
    print(f"Dentro dos limites do Brasil: Lat={lat_ok}, Lon={lon_ok}")
    
    # Procurar municípios próximos
    buffer_area = ponto_kiko.buffer(0.1)  # ~11km
    municipios_proximos = gdf[gdf.geometry.intersects(buffer_area)]
    
    print(f"Municípios próximos (raio ~11km): {len(municipios_proximos)}")
    
    if len(municipios_proximos) > 0:
        print("Municípios encontrados:")
        for _, mun in municipios_proximos.iterrows():
            dist = ponto_kiko.distance(mun.geometry.centroid)
            km_aprox = dist * 111
            print(f"  {mun['NM_MUN']} - {mun['SIGLA_UF']} (~{km_aprox:.1f}km)")
    
    # Verificar se está dentro de algum polígono
    municipio_exato = gdf[gdf.geometry.contains(ponto_kiko)]
    
    if len(municipio_exato) > 0:
        print("✅ MUNICÍPIO QUE CONTÉM O PONTO:")
        for _, mun in municipio_exato.iterrows():
            print(f"  {mun['NM_MUN']} - {mun['SIGLA_UF']}")
    else:
        print("❌ NENHUM município contém este ponto exato!")
        
        # Verificar o município mais próximo
        if len(municipios_proximos) > 0:
            distancias = []
            for _, mun in municipios_proximos.iterrows():
                dist = ponto_kiko.distance(mun.geometry.centroid)
                distancias.append((mun['NM_MUN'], mun['SIGLA_UF'], dist, mun.name))
            
            distancias.sort(key=lambda x: x[2])
            mais_proximo = distancias[0]
            
            print(f"Município mais próximo: {mais_proximo[0]} - {mais_proximo[1]}")
            
            # Verificar a geometria do município mais próximo
            mun_mais_proximo = gdf.iloc[mais_proximo[3]]
            
            # Calcular distância até a borda do polígono
            dist_borda = ponto_kiko.distance(mun_mais_proximo.geometry.boundary)
            km_borda = dist_borda * 111
            
            print(f"Distância até a borda do município: ~{km_borda:.1f}km")
            
            if km_borda < 1.0:  # Menos de 1km da borda
                print("🔍 DIAGNÓSTICO: Ponto muito próximo da borda!")
                print("   Possível solução: Usar buffer ou município mais próximo")

if __name__ == "__main__":
    investigar_casos_nao_encontrados()
    verificar_borracharia_kiko()
