#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executar Geocodificação Completa
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import re
from tqdm import tqdm

def main():
    """Executa geocodificação completa"""
    
    print("🚀 INICIANDO GEOCODIFICAÇÃO COMPLETA")
    print("=" * 60)
    
    # Configurações
    arquivo_excel = '../tire_shops_excel_final.xlsx'
    shapefile_path = '../IBGE/BR_Municipios_2024.shp'
    arquivo_saida = '../estabelecimentos_geocodificados_final.xlsx'
    
    try:
        # 1. Carregar dados
        print("📂 Carregando dados...")
        df = pd.read_excel(arquivo_excel)
        print(f"✅ Excel carregado: {len(df)} registros")
        
        municipios_gdf = gpd.read_file(shapefile_path)
        print(f"✅ Shapefile carregado: {len(municipios_gdf)} municípios")
        
        # Converter CRS se necessário
        if municipios_gdf.crs != 'EPSG:4326':
            municipios_gdf = municipios_gdf.to_crs('EPSG:4326')
        
        # Criar índice espacial
        spatial_index = municipios_gdf.sindex
        
        # 2. Função para encontrar município
        def encontrar_municipio(lat, lon):
            if pd.isna(lat) or pd.isna(lon):
                return {'cidade': 'Coordenada ausente', 'estado': '', 'codigo_ibge': '', 'precisao': 'ausente'}
            
            # Validar coordenadas do Brasil
            if not (-33.75 <= lat <= 5.27) or not (-73.98 <= lon <= -28.84):
                return {'cidade': 'Coordenada inválida', 'estado': '', 'codigo_ibge': '', 'precisao': 'inválido'}
            
            ponto = Point(lon, lat)
            
            # Verificação exata
            candidatos_indices = list(spatial_index.intersection(ponto.bounds))
            candidatos = municipios_gdf.iloc[candidatos_indices]
            
            for idx, municipio in candidatos.iterrows():
                if municipio.geometry.contains(ponto):
                    return {
                        'cidade': municipio['NM_MUN'],
                        'estado': municipio['SIGLA_UF'],
                        'codigo_ibge': municipio['CD_MUN'],
                        'precisao': 'exato'
                    }
            
            # Sistema de fallback
            buffers = [0.01, 0.05, 0.1, 0.25, 0.5]
            precisoes = ['muito_próximo', 'próximo', 'próximo', 'distante', 'muito_distante']
            
            for buffer_size, precisao in zip(buffers, precisoes):
                buffer_area = ponto.buffer(buffer_size)
                municipios_proximos = municipios_gdf[municipios_gdf.geometry.intersects(buffer_area)]
                
                if len(municipios_proximos) > 0:
                    distancias = municipios_proximos.geometry.distance(ponto)
                    municipio_mais_proximo = municipios_proximos.loc[distancias.idxmin()]
                    
                    distancia_km = distancias.min() * 111
                    if distancia_km > 20:
                        precisao = 'oceano'
                    elif distancia_km > 100:
                        precisao = 'extremamente_distante'
                    
                    return {
                        'cidade': municipio_mais_proximo['NM_MUN'],
                        'estado': municipio_mais_proximo['SIGLA_UF'],
                        'codigo_ibge': municipio_mais_proximo['CD_MUN'],
                        'precisao': precisao
                    }
            
            # Último recurso
            distancias_todas = municipios_gdf.geometry.distance(ponto)
            municipio_mais_proximo = municipios_gdf.loc[distancias_todas.idxmin()]
            
            return {
                'cidade': municipio_mais_proximo['NM_MUN'],
                'estado': municipio_mais_proximo['SIGLA_UF'],
                'codigo_ibge': municipio_mais_proximo['CD_MUN'],
                'precisao': 'extremamente_distante'
            }
        
        # 3. Processar geocodificação
        print("🗺️  Processando geocodificação...")
        
        df['cidade'] = ''
        df['estado'] = ''
        df['codigo_ibge'] = ''
        df['precisao'] = ''
        
        for idx in tqdm(range(len(df)), desc="Geocodificando"):
            try:
                lat = df.loc[idx, 'latitude']
                lon = df.loc[idx, 'longitude']
                
                resultado = encontrar_municipio(lat, lon)
                
                df.loc[idx, 'cidade'] = resultado['cidade']
                df.loc[idx, 'estado'] = resultado['estado']
                df.loc[idx, 'codigo_ibge'] = resultado['codigo_ibge']
                df.loc[idx, 'precisao'] = resultado['precisao']
                
            except Exception as e:
                print(f"Erro no registro {idx}: {e}")
                df.loc[idx, 'cidade'] = 'Erro'
                df.loc[idx, 'estado'] = ''
                df.loc[idx, 'codigo_ibge'] = ''
                df.loc[idx, 'precisao'] = 'erro'
        
        # 4. Preencher DDD
        print("📞 Preenchendo DDD...")
        
        def extrair_ddd(telefone):
            if not telefone or pd.isna(telefone):
                return None
            numeros = re.sub(r'[^\d]', '', str(telefone))
            return numeros[:2] if len(numeros) >= 2 else None
        
        df['DDD'] = df['Phone'].apply(extrair_ddd)
        
        # 5. Remover telefones duplicados
        print("🔧 Removendo telefones duplicados...")
        
        total_antes = len(df)
        df_com_telefone = df[df['Phone'].notna() & (df['Phone'] != '')]
        df_sem_telefone = df[df['Phone'].isna() | (df['Phone'] == '')]
        
        if len(df_com_telefone) > 0:
            telefones_unicos = df_com_telefone['Phone'].nunique()
            duplicados = len(df_com_telefone) - telefones_unicos
            
            if duplicados > 0:
                print(f"Encontrados {duplicados} telefones duplicados")
                
                def calcular_score(row):
                    score = 0
                    campos = ['Nome', 'rating', 'reviews_count', 'address', 'website', 'cidade', 'estado']
                    
                    for campo in campos:
                        if campo in row and pd.notna(row[campo]) and str(row[campo]).strip() != '':
                            score += 1
                    
                    if pd.notna(row.get('rating')):
                        try:
                            rating = float(row['rating'])
                            if rating >= 4.5: score += 3
                            elif rating >= 4.0: score += 2
                            elif rating >= 3.5: score += 1
                        except: pass
                    
                    if pd.notna(row.get('reviews_count')):
                        try:
                            reviews = int(row['reviews_count'])
                            if reviews >= 100: score += 3
                            elif reviews >= 50: score += 2
                            elif reviews >= 10: score += 1
                        except: pass
                    
                    precisao = row.get('precisao', '')
                    if precisao == 'exato': score += 3
                    elif precisao in ['muito_próximo', 'próximo']: score += 2
                    elif precisao == 'distante': score += 1
                    
                    return score
                
                df_com_telefone = df_com_telefone.copy()
                df_com_telefone['score'] = df_com_telefone.apply(calcular_score, axis=1)
                df_sem_duplicatas = df_com_telefone.loc[df_com_telefone.groupby('Phone')['score'].idxmax()]
                df_sem_duplicatas = df_sem_duplicatas.drop('score', axis=1)
                
                df = pd.concat([df_sem_duplicatas, df_sem_telefone], ignore_index=True)
        
        # 6. Salvar resultado
        print("💾 Salvando resultado...")
        
        colunas_principais = ['Nome', 'rating', 'reviews_count', 'DDD', 'Phone', 'cidade', 'estado', 'latitude', 'longitude', 'precisao']
        colunas_extras = [col for col in df.columns if col not in colunas_principais]
        colunas_finais = colunas_principais + colunas_extras
        colunas_existentes = [col for col in colunas_finais if col in df.columns]
        
        df_final = df[colunas_existentes]
        df_final.to_excel(arquivo_saida, index=False)
        
        print(f"✅ Arquivo salvo: {arquivo_saida}")
        print(f"📊 Total de registros: {len(df_final)}")
        
        # Estatísticas finais
        print("\n📈 ESTATÍSTICAS FINAIS:")
        print(f"Registros com telefone: {df_final['Phone'].notna().sum()}")
        print(f"Registros com cidade: {(df_final['cidade'] != '').sum()}")
        print(f"Registros com estado: {(df_final['estado'] != '').sum()}")
        
        precisao_counts = df_final['precisao'].value_counts()
        print("\n🎯 PRECISÃO DA GEOCODIFICAÇÃO:")
        for precisao, count in precisao_counts.items():
            print(f"  {precisao}: {count} registros")
        
        duplicados_restantes = df_final[df_final['Phone'].notna() & df_final.duplicated(subset=['Phone'], keep=False)]
        if len(duplicados_restantes) == 0:
            print("✅ Confirmado: Nenhum telefone duplicado restante")
        else:
            print(f"⚠️  Ainda existem {len(duplicados_restantes)} telefones duplicados")
        
        print("\n🎉 PROCESSO COMPLETO FINALIZADO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
