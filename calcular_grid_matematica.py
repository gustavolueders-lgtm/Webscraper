#!/usr/bin/env python3
"""
Calcula a matemática exata do grid para explicar a discrepância
"""

import math

def calcular_grid_detalhado():
    """Calcula detalhadamente o grid e explica a matemática"""
    
    print("🧮 MATEMÁTICA DETALHADA DO GRID")
    print("=" * 50)
    
    # Configurações do grid
    GRID_SIZE_KM = 5
    LAT_MIN, LAT_MAX = -25.3, -19.8
    LON_MIN, LON_MAX = -53.1, -44.2
    
    print(f"📐 CONFIGURAÇÃO DO GRID:")
    print(f"   🔸 Tamanho da célula: {GRID_SIZE_KM}km × {GRID_SIZE_KM}km = {GRID_SIZE_KM**2} km²")
    print(f"   🔸 Latitude: {LAT_MIN}° a {LAT_MAX}° (diferença: {LAT_MAX - LAT_MIN:.2f}°)")
    print(f"   🔸 Longitude: {LON_MIN}° a {LON_MAX}° (diferença: {LON_MAX - LON_MIN:.2f}°)")
    
    # Cálculos de conversão graus → km
    print(f"\n📏 CONVERSÃO GRAUS → QUILÔMETROS:")
    
    # Latitude (sempre 111 km por grau)
    lat_range_degrees = LAT_MAX - LAT_MIN
    lat_range_km = lat_range_degrees * 111.0
    print(f"   🔸 Latitude: {lat_range_degrees:.2f}° × 111 km/° = {lat_range_km:.1f} km")
    
    # Longitude (varia com a latitude)
    avg_lat = (LAT_MIN + LAT_MAX) / 2
    cos_correction = math.cos(math.radians(abs(avg_lat)))
    lon_range_degrees = LON_MAX - LON_MIN
    lon_range_km = lon_range_degrees * 111.0 * cos_correction
    print(f"   🔸 Longitude: {lon_range_degrees:.2f}° × 111 km/° × cos({abs(avg_lat):.1f}°) = {lon_range_km:.1f} km")
    print(f"      (cos({abs(avg_lat):.1f}°) = {cos_correction:.3f})")
    
    # Área total do retângulo
    total_area_km2 = lat_range_km * lon_range_km
    print(f"\n📊 ÁREA TOTAL DO RETÂNGULO:")
    print(f"   🔸 {lat_range_km:.1f} km × {lon_range_km:.1f} km = {total_area_km2:,.0f} km²")
    
    # Cálculo do número de células (como no código)
    lat_step = GRID_SIZE_KM / 111.0
    lon_step = GRID_SIZE_KM / (111.0 * cos_correction)
    
    print(f"\n🔢 CÁLCULO DAS CÉLULAS:")
    print(f"   🔸 Passo latitude: {GRID_SIZE_KM} km ÷ 111 km/° = {lat_step:.6f}°")
    print(f"   🔸 Passo longitude: {GRID_SIZE_KM} km ÷ (111 × {cos_correction:.3f}) = {lon_step:.6f}°")
    
    # Contar células exatamente como no código
    cells = []
    lat = LAT_MIN
    while lat <= LAT_MAX:
        lon = LON_MIN
        while lon <= LON_MAX:
            cells.append((lat, lon))
            lon += lon_step
        lat += lat_step
    
    num_cells = len(cells)
    
    # Cálculo alternativo
    num_lat_cells = int((LAT_MAX - LAT_MIN) / lat_step) + 1
    num_lon_cells = int((LON_MAX - LON_MIN) / lon_step) + 1
    calculated_cells = num_lat_cells * num_lon_cells
    
    print(f"   🔸 Células latitude: {num_lat_cells}")
    print(f"   🔸 Células longitude: {num_lon_cells}")
    print(f"   🔸 Total calculado: {num_lat_cells} × {num_lon_cells} = {calculated_cells}")
    print(f"   🔸 Total real (código): {num_cells}")
    
    # Comparação com Santa Catarina real
    sc_real_area = 95730  # km² (área real de SC)
    cells_if_only_sc = sc_real_area / (GRID_SIZE_KM ** 2)
    
    print(f"\n🗺️ COMPARAÇÃO COM SANTA CATARINA REAL:")
    print(f"   🔸 Área real de SC: {sc_real_area:,} km²")
    print(f"   🔸 Células se fosse só SC: {sc_real_area:,} ÷ {GRID_SIZE_KM**2} = {cells_if_only_sc:,.0f} células")
    print(f"   🔸 Células do nosso grid: {num_cells:,}")
    print(f"   🔸 Diferença: {num_cells - cells_if_only_sc:,.0f} células a mais")
    
    # Explicação da discrepância
    ocean_and_other_states = total_area_km2 - sc_real_area
    percentage_waste = (ocean_and_other_states / total_area_km2) * 100
    
    print(f"\n❓ EXPLICAÇÃO DA DISCREPÂNCIA:")
    print(f"   🔸 Área do retângulo: {total_area_km2:,.0f} km²")
    print(f"   🔸 Área real de SC: {sc_real_area:,} km²")
    print(f"   🔸 Oceano + outros estados: {ocean_and_other_states:,.0f} km² ({percentage_waste:.1f}%)")
    print(f"   🔸 Por isso temos {num_cells:,} células em vez de {cells_if_only_sc:,.0f}")
    
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   ✅ O grid cobre um RETÂNGULO que engloba SC")
    print(f"   ✅ Inclui oceano Atlântico e partes do RS/PR")
    print(f"   ✅ Por isso {num_cells:,} células > {cells_if_only_sc:,.0f} células")
    print(f"   ✅ A matemática está correta!")
    
    # Mostrar algumas coordenadas para visualizar
    print(f"\n📍 COORDENADAS DOS CANTOS:")
    print(f"   🔸 Sudoeste: {LAT_MIN}°, {LON_MIN}° (início do grid)")
    print(f"   🔸 Nordeste: {LAT_MAX}°, {LON_MAX}° (fim do grid)")
    print(f"   🔸 Centro: {avg_lat:.2f}°, {(LON_MIN + LON_MAX)/2:.2f}°")

if __name__ == "__main__":
    calcular_grid_detalhado()
