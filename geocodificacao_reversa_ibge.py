#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geocodificação Reversa usando dados do IBGE
============================================

Script para adicionar informações de município e estado a partir de coordenadas
usando os shapefiles oficiais do IBGE.

Autor: Assistente IA
Data: 2025-01-17
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import os
from tqdm import tqdm
import warnings

# Suprimir warnings do geopandas
warnings.filterwarnings('ignore')

class GeocodificadorReverso:
    """Classe para geocodificação reversa usando dados do IBGE"""
    
    def __init__(self, shapefile_path):
        """
        Inicializa o geocodificador
        
        Args:
            shapefile_path (str): Caminho para o shapefile dos municípios do IBGE
        """
        self.shapefile_path = shapefile_path
        self.municipios_gdf = None
        self.spatial_index = None
        
    def carregar_shapefile(self):
        """Carrega o shapefile do IBGE e cria o índice espacial"""
        print("📍 Carregando shapefile do IBGE...")
        
        try:
            # Carregar shapefile
            self.municipios_gdf = gpd.read_file(self.shapefile_path)
            
            # Verificar se tem as colunas necessárias
            colunas_necessarias = ['NM_MUN', 'SIGLA_UF', 'CD_MUN', 'geometry']
            for col in colunas_necessarias:
                if col not in self.municipios_gdf.columns:
                    raise ValueError(f"Coluna '{col}' não encontrada no shapefile")
            
            # Converter para WGS84 se necessário (para compatibilidade com lat/long)
            if self.municipios_gdf.crs != 'EPSG:4326':
                print("🔄 Convertendo CRS para WGS84...")
                self.municipios_gdf = self.municipios_gdf.to_crs('EPSG:4326')
            
            # Criar índice espacial para performance
            print("⚡ Criando índice espacial...")
            self.spatial_index = self.municipios_gdf.sindex
            
            print(f"✅ Shapefile carregado: {len(self.municipios_gdf)} municípios")
            
        except Exception as e:
            raise Exception(f"Erro ao carregar shapefile: {e}")
    
    def validar_coordenadas(self, lat, lon):
        """
        Valida se as coordenadas são válidas
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            bool: True se válidas, False caso contrário
        """
        try:
            lat = float(lat)
            lon = float(lon)
            
            # Verificar se estão dentro dos limites do Brasil
            # Brasil: lat entre -33.75 e 5.27, lon entre -73.98 e -28.84
            if not (-33.75 <= lat <= 5.27):
                return False
            if not (-73.98 <= lon <= -28.84):
                return False
                
            return True
            
        except (ValueError, TypeError):
            return False
    
    def encontrar_municipio(self, lat, lon):
        """
        Encontra o município para uma coordenada específica com sistema de fallback

        Args:
            lat (float): Latitude
            lon (float): Longitude

        Returns:
            dict: Informações do município com precisão
        """
        # Validar coordenadas
        if not self.validar_coordenadas(lat, lon):
            return {
                'cidade': 'Coordenada inválida',
                'estado': 'Coordenada inválida',
                'codigo_ibge': 'Coordenada inválida',
                'precisao': 'inválida'
            }

        try:
            # Criar ponto
            ponto = Point(float(lon), float(lat))

            # MÉTODO 1: Verificar se está exatamente dentro de algum município
            possible_matches_index = list(self.spatial_index.intersection(ponto.bounds))
            possible_matches = self.municipios_gdf.iloc[possible_matches_index]

            for idx, municipio in possible_matches.iterrows():
                if municipio.geometry.contains(ponto):
                    return {
                        'cidade': municipio['NM_MUN'],
                        'estado': municipio['SIGLA_UF'],
                        'codigo_ibge': municipio['CD_MUN'],
                        'precisao': 'exato'
                    }

            # MÉTODO 2: Sistema de fallback com buffer crescente
            buffers = [0.01, 0.05, 0.1, 0.25, 0.5]  # 1km, 5km, 10km, 25km, 50km aproximadamente
            precisoes = ['muito_próximo', 'próximo', 'próximo', 'distante', 'muito_distante']

            for buffer_size, precisao in zip(buffers, precisoes):
                buffer_area = ponto.buffer(buffer_size)
                municipios_proximos = self.municipios_gdf[self.municipios_gdf.geometry.intersects(buffer_area)]

                if len(municipios_proximos) > 0:
                    # Encontrar o município mais próximo
                    distancias = []
                    for idx, mun in municipios_proximos.iterrows():
                        # Calcular distância até o centroide do município
                        dist_centroide = ponto.distance(mun.geometry.centroid)
                        # Calcular distância até a borda do município
                        dist_borda = ponto.distance(mun.geometry.boundary)
                        # Usar a menor distância
                        dist_final = min(dist_centroide, dist_borda)
                        distancias.append((idx, dist_final, mun))

                    # Ordenar por distância e pegar o mais próximo
                    distancias.sort(key=lambda x: x[1])
                    idx_mais_proximo, dist_mais_proximo, mun_mais_proximo = distancias[0]

                    # Ajustar precisão baseada na distância real
                    km_distancia = dist_mais_proximo * 111  # Conversão aproximada para km

                    if km_distancia <= 1:
                        precisao_final = 'muito_próximo'
                    elif km_distancia <= 5:
                        precisao_final = 'próximo'
                    elif km_distancia <= 15:
                        precisao_final = 'distante'
                    else:
                        precisao_final = 'muito_distante'

                    # Verificar se é coordenada no oceano (muito longe da terra)
                    if km_distancia > 20:
                        precisao_final = 'oceano'

                    return {
                        'cidade': mun_mais_proximo['NM_MUN'],
                        'estado': mun_mais_proximo['SIGLA_UF'],
                        'codigo_ibge': mun_mais_proximo['CD_MUN'],
                        'precisao': precisao_final
                    }

            # MÉTODO 3: Se ainda não encontrou nada, pegar o município mais próximo do Brasil inteiro
            print(f"⚠️  Coordenada muito isolada: {lat}, {lon} - usando município mais próximo do país")

            # Calcular distância para todos os municípios (só centroides para performance)
            distancias_todas = []
            for idx, mun in self.municipios_gdf.iterrows():
                dist = ponto.distance(mun.geometry.centroid)
                distancias_todas.append((idx, dist, mun))

            # Pegar o mais próximo
            distancias_todas.sort(key=lambda x: x[1])
            idx_mais_proximo, dist_mais_proximo, mun_mais_proximo = distancias_todas[0]

            km_distancia = dist_mais_proximo * 111

            return {
                'cidade': mun_mais_proximo['NM_MUN'],
                'estado': mun_mais_proximo['SIGLA_UF'],
                'codigo_ibge': mun_mais_proximo['CD_MUN'],
                'precisao': 'extremamente_distante' if km_distancia > 100 else 'muito_distante'
            }

        except Exception as e:
            return {
                'cidade': f'Erro: {str(e)}',
                'estado': f'Erro: {str(e)}',
                'codigo_ibge': f'Erro: {str(e)}',
                'precisao': 'erro'
            }
    
    def processar_arquivo(self, arquivo_entrada, arquivo_saida, batch_size=100):
        """
        Processa o arquivo Excel/CSV adicionando informações de município
        
        Args:
            arquivo_entrada (str): Caminho do arquivo de entrada
            arquivo_saida (str): Caminho do arquivo de saída
            batch_size (int): Tamanho do lote para processamento
        """
        print(f"📂 Carregando arquivo: {arquivo_entrada}")
        
        # Detectar tipo de arquivo e carregar
        if arquivo_entrada.endswith('.xlsx'):
            df = pd.read_excel(arquivo_entrada)
        elif arquivo_entrada.endswith('.csv'):
            df = pd.read_csv(arquivo_entrada)
        else:
            raise ValueError("Formato de arquivo não suportado. Use .xlsx ou .csv")
        
        print(f"📊 Arquivo carregado: {len(df)} registros")
        
        # Verificar se tem as colunas de coordenadas
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            raise ValueError("Colunas 'latitude' e 'longitude' não encontradas no arquivo")
        
        # Inicializar colunas de resultado
        df['cidade'] = ''
        df['estado'] = ''
        df['codigo_ibge'] = ''
        df['precisao'] = ''
        
        # Processar em lotes com barra de progresso
        print("🔍 Iniciando geocodificação reversa...")
        
        with tqdm(total=len(df), desc="Processando", unit="registros") as pbar:
            for i in range(0, len(df), batch_size):
                batch_end = min(i + batch_size, len(df))
                batch = df.iloc[i:batch_end]
                
                for idx, row in batch.iterrows():
                    resultado = self.encontrar_municipio(row['latitude'], row['longitude'])

                    df.at[idx, 'cidade'] = resultado['cidade']
                    df.at[idx, 'estado'] = resultado['estado']
                    df.at[idx, 'codigo_ibge'] = resultado['codigo_ibge']
                    df.at[idx, 'precisao'] = resultado['precisao']
                
                pbar.update(batch_end - i)
        
        # Salvar resultado
        print(f"💾 Salvando resultado em: {arquivo_saida}")
        
        if arquivo_saida.endswith('.xlsx'):
            df.to_excel(arquivo_saida, index=False)
        elif arquivo_saida.endswith('.csv'):
            df.to_csv(arquivo_saida, index=False)
        else:
            # Default para Excel
            df.to_excel(arquivo_saida, index=False)
        
        # Estatísticas finais
        self.mostrar_estatisticas(df)
        
        print(f"✅ Processamento concluído! Arquivo salvo: {arquivo_saida}")
        
        return df
    
    def mostrar_estatisticas(self, df):
        """Mostra estatísticas do processamento"""
        print("\n📈 ESTATÍSTICAS DO PROCESSAMENTO:")
        print("=" * 50)

        total = len(df)

        # Contar por precisão
        precisao_counts = df['precisao'].value_counts()

        exatos = precisao_counts.get('exato', 0)
        muito_proximos = precisao_counts.get('muito_próximo', 0)
        proximos = precisao_counts.get('próximo', 0)
        distantes = precisao_counts.get('distante', 0)
        muito_distantes = precisao_counts.get('muito_distante', 0)
        oceano = precisao_counts.get('oceano', 0)
        extremamente_distantes = precisao_counts.get('extremamente_distante', 0)
        invalidos = precisao_counts.get('inválida', 0)
        erros = precisao_counts.get('erro', 0)

        # Calcular sucessos (todos exceto inválidos e erros)
        sucessos = total - invalidos - erros

        print(f"Total de registros: {total}")
        print(f"✅ SUCESSOS: {sucessos} ({sucessos/total*100:.1f}%)")
        print(f"   • Localização exata: {exatos} ({exatos/total*100:.1f}%)")
        print(f"   • Muito próximo (<1km): {muito_proximos} ({muito_proximos/total*100:.1f}%)")
        print(f"   • Próximo (1-5km): {proximos} ({proximos/total*100:.1f}%)")
        print(f"   • Distante (5-15km): {distantes} ({distantes/total*100:.1f}%)")
        print(f"   • Muito distante (15-20km): {muito_distantes} ({muito_distantes/total*100:.1f}%)")
        print(f"   • Oceano/Costa (>20km): {oceano} ({oceano/total*100:.1f}%)")
        print(f"   • Extremamente distante (>100km): {extremamente_distantes} ({extremamente_distantes/total*100:.1f}%)")
        print(f"❌ FALHAS: {invalidos + erros} ({(invalidos + erros)/total*100:.1f}%)")
        print(f"   • Coordenadas inválidas: {invalidos} ({invalidos/total*100:.1f}%)")
        print(f"   • Erros: {erros} ({erros/total*100:.1f}%)")

        # Top 10 cidades
        cidades_validas = df[~df['precisao'].isin(['inválida', 'erro'])]
        if len(cidades_validas) > 0:
            print(f"\n🏆 TOP 10 CIDADES:")
            top_cidades = cidades_validas['cidade'].value_counts().head(10)
            for cidade, count in top_cidades.items():
                print(f"  {cidade}: {count} estabelecimentos")

        # Estatísticas de precisão
        print(f"\n🎯 QUALIDADE DA LOCALIZAÇÃO:")
        alta_precisao = exatos + muito_proximos + proximos
        print(f"Alta precisão (≤5km): {alta_precisao} ({alta_precisao/total*100:.1f}%)")

        coordenadas_suspeitas = oceano + extremamente_distantes
        if coordenadas_suspeitas > 0:
            print(f"⚠️  Coordenadas suspeitas: {coordenadas_suspeitas} ({coordenadas_suspeitas/total*100:.1f}%)")
            print("   (Podem estar no oceano ou com erro de GPS)")


def main():
    """Função principal"""
    print("🌎 GEOCODIFICAÇÃO REVERSA - IBGE")
    print("=" * 50)
    
    # Caminhos dos arquivos
    arquivo_entrada = '../borracharias_santa_catarina_20251012_111703.xlsx'
    shapefile_path = '../IBGE/BR_Municipios_2024.shp'
    arquivo_saida = '../estabelecimentos_com_cidade_100_porcento.xlsx'
    
    try:
        # Verificar se os arquivos existem
        if not os.path.exists(arquivo_entrada):
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {arquivo_entrada}")
        
        if not os.path.exists(shapefile_path):
            raise FileNotFoundError(f"Shapefile não encontrado: {shapefile_path}")
        
        # Criar geocodificador
        geocodificador = GeocodificadorReverso(shapefile_path)
        
        # Carregar shapefile
        geocodificador.carregar_shapefile()
        
        # Processar arquivo
        resultado = geocodificador.processar_arquivo(arquivo_entrada, arquivo_saida)
        
        print(f"\n🎉 SUCESSO! Arquivo processado e salvo em: {arquivo_saida}")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()
