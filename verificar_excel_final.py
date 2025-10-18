#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação do arquivo Excel final
"""

import pandas as pd

def verificar_excel_final():
    """Verifica se o arquivo Excel final está correto"""
    
    arquivo_excel = 'tire_shops_excel_final.xlsx'
    
    print("🔍 VERIFICAÇÃO DO ARQUIVO EXCEL FINAL:")
    print("=" * 60)
    
    try:
        # Carregar arquivo Excel
        df = pd.read_excel(arquivo_excel)
        
        print(f"📊 ESTATÍSTICAS GERAIS:")
        print(f"Total de registros: {len(df)}")
        print(f"Total de colunas: {len(df.columns)}")
        
        print(f"\n📋 ORDEM DAS COLUNAS:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Verificar colunas principais
        colunas_esperadas = ['Nome', 'rating', 'reviews_count', 'DDD', 'Phone', 'cidade', 'latitude', 'longitude']
        
        print(f"\n✅ VERIFICAÇÃO DAS COLUNAS PRINCIPAIS:")
        for i, col in enumerate(colunas_esperadas):
            if col in df.columns:
                posicao = list(df.columns).index(col) + 1
                print(f"  {col}: Posição {posicao} ✅")
            else:
                print(f"  {col}: AUSENTE ❌")
        
        # Verificar DDD como número
        print(f"\n📞 VERIFICAÇÃO DO DDD:")
        if 'DDD' in df.columns:
            ddd_tipo = df['DDD'].dtype
            ddd_nulos = df['DDD'].isnull().sum()
            ddd_unicos = df['DDD'].nunique()
            
            print(f"  Tipo de dados: {ddd_tipo}")
            print(f"  Valores nulos: {ddd_nulos}")
            print(f"  DDDs únicos: {ddd_unicos}")
            
            # Mostrar alguns exemplos
            ddds_validos = df[df['DDD'].notna()]['DDD'].head(10)
            print(f"  Exemplos: {list(ddds_validos)}")
        
        # Verificar telefones duplicados
        print(f"\n📱 VERIFICAÇÃO DE TELEFONES:")
        if 'Phone' in df.columns:
            telefones_com_valor = df[df['Phone'].notna() & (df['Phone'] != '')]
            telefones_unicos = telefones_com_valor['Phone'].nunique()
            total_com_telefone = len(telefones_com_valor)
            
            print(f"  Registros com telefone: {total_com_telefone}")
            print(f"  Telefones únicos: {telefones_unicos}")
            print(f"  Telefones duplicados: {total_com_telefone - telefones_unicos}")
            
            if total_com_telefone == telefones_unicos:
                print("  ✅ Nenhum telefone duplicado!")
            else:
                print("  ❌ Ainda há telefones duplicados!")
        
        # Verificar dados de rating e reviews
        print(f"\n⭐ VERIFICAÇÃO DE RATINGS E REVIEWS:")
        if 'rating' in df.columns:
            rating_medio = df['rating'].mean()
            rating_min = df['rating'].min()
            rating_max = df['rating'].max()
            rating_nulos = df['rating'].isnull().sum()
            
            print(f"  Rating médio: {rating_medio:.2f}")
            print(f"  Rating mín/máx: {rating_min}/{rating_max}")
            print(f"  Ratings nulos: {rating_nulos}")
        
        if 'reviews_count' in df.columns:
            reviews_media = df['reviews_count'].mean()
            reviews_max = df['reviews_count'].max()
            reviews_nulos = df['reviews_count'].isnull().sum()
            
            print(f"  Reviews média: {reviews_media:.1f}")
            print(f"  Reviews máximo: {reviews_max}")
            print(f"  Reviews nulos: {reviews_nulos}")
        
        # Verificar coordenadas
        print(f"\n🗺️  VERIFICAÇÃO DE COORDENADAS:")
        if 'latitude' in df.columns and 'longitude' in df.columns:
            lat_nulos = df['latitude'].isnull().sum()
            lon_nulos = df['longitude'].isnull().sum()
            
            print(f"  Latitudes nulas: {lat_nulos}")
            print(f"  Longitudes nulas: {lon_nulos}")
            
            if lat_nulos == 0 and lon_nulos == 0:
                lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
                lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
                
                print(f"  Latitude: {lat_min:.2f} a {lat_max:.2f}")
                print(f"  Longitude: {lon_min:.2f} a {lon_max:.2f}")
        
        # Mostrar alguns registros de exemplo
        print(f"\n📋 EXEMPLOS DE REGISTROS:")
        colunas_principais = ['Nome', 'rating', 'reviews_count', 'DDD', 'Phone', 'cidade']
        if all(col in df.columns for col in colunas_principais):
            exemplos = df[colunas_principais].head(5)
            print(exemplos.to_string(index=False))
        
        print(f"\n✅ ARQUIVO EXCEL VERIFICADO COM SUCESSO!")
        print(f"Arquivo: {arquivo_excel}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar arquivo: {e}")

if __name__ == "__main__":
    verificar_excel_final()
