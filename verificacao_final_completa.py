#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação Final Completa
"""

import pandas as pd

def verificacao_final():
    """Verifica o arquivo final geocodificado"""
    
    arquivo_final = '../estabelecimentos_geocodificados_final.xlsx'
    
    print("🔍 VERIFICAÇÃO FINAL COMPLETA:")
    print("=" * 60)
    
    try:
        # Carregar arquivo
        df = pd.read_excel(arquivo_final)
        
        print(f"📊 ESTATÍSTICAS GERAIS:")
        print(f"Total de registros: {len(df)}")
        print(f"Total de colunas: {len(df.columns)}")
        
        print(f"\n📋 COLUNAS DO ARQUIVO:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # Verificar geocodificação
        print(f"\n🗺️  VERIFICAÇÃO DA GEOCODIFICAÇÃO:")
        if 'cidade' in df.columns and 'estado' in df.columns:
            cidades_preenchidas = (df['cidade'] != '').sum()
            estados_preenchidos = (df['estado'] != '').sum()
            
            print(f"Cidades preenchidas: {cidades_preenchidas}/{len(df)}")
            print(f"Estados preenchidos: {estados_preenchidos}/{len(df)}")
            
            if 'precisao' in df.columns:
                print(f"\n🎯 PRECISÃO DA GEOCODIFICAÇÃO:")
                precisao_counts = df['precisao'].value_counts()
                for precisao, count in precisao_counts.items():
                    porcentagem = count/len(df)*100
                    print(f"  {precisao}: {count} registros ({porcentagem:.1f}%)")
        
        # Verificar DDD
        print(f"\n📞 VERIFICAÇÃO DO DDD:")
        if 'DDD' in df.columns:
            ddds_preenchidos = df['DDD'].notna().sum()
            ddds_unicos = df['DDD'].nunique()
            
            print(f"DDDs preenchidos: {ddds_preenchidos}/{len(df)}")
            print(f"DDDs únicos: {ddds_unicos}")
            
            if ddds_preenchidos > 0:
                top_ddds = df['DDD'].value_counts().head(5)
                print(f"\nTOP 5 DDDs:")
                for ddd, count in top_ddds.items():
                    print(f"  {ddd}: {count} registros")
        
        # Verificar telefones duplicados
        print(f"\n📱 VERIFICAÇÃO DE TELEFONES:")
        if 'Phone' in df.columns:
            telefones_com_valor = df[df['Phone'].notna() & (df['Phone'] != '')]
            telefones_unicos = telefones_com_valor['Phone'].nunique()
            total_com_telefone = len(telefones_com_valor)
            
            print(f"Registros com telefone: {total_com_telefone}")
            print(f"Telefones únicos: {telefones_unicos}")
            print(f"Telefones duplicados: {total_com_telefone - telefones_unicos}")
            
            if total_com_telefone == telefones_unicos:
                print("✅ Nenhum telefone duplicado!")
            else:
                print("❌ Ainda há telefones duplicados!")
        
        # Verificar coordenadas
        print(f"\n🌍 VERIFICAÇÃO DE COORDENADAS:")
        if 'latitude' in df.columns and 'longitude' in df.columns:
            lat_nulos = df['latitude'].isnull().sum()
            lon_nulos = df['longitude'].isnull().sum()
            
            print(f"Latitudes nulas: {lat_nulos}")
            print(f"Longitudes nulas: {lon_nulos}")
            
            if lat_nulos == 0 and lon_nulos == 0:
                lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
                lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
                
                print(f"Latitude: {lat_min:.2f} a {lat_max:.2f}")
                print(f"Longitude: {lon_min:.2f} a {lon_max:.2f}")
        
        # Mostrar exemplos de registros
        print(f"\n📋 EXEMPLOS DE REGISTROS FINAIS:")
        colunas_exemplo = ['Nome', 'rating', 'DDD', 'Phone', 'cidade', 'estado', 'precisao']
        colunas_existentes = [col for col in colunas_exemplo if col in df.columns]
        
        if colunas_existentes:
            exemplos = df[colunas_existentes].head(5)
            print(exemplos.to_string(index=False))
        
        # Verificar qualidade dos dados
        print(f"\n⭐ QUALIDADE DOS DADOS:")
        if 'rating' in df.columns:
            rating_medio = df['rating'].mean()
            rating_nulos = df['rating'].isnull().sum()
            print(f"Rating médio: {rating_medio:.2f}")
            print(f"Ratings nulos: {rating_nulos}")
        
        if 'reviews_count' in df.columns:
            reviews_media = df['reviews_count'].mean()
            reviews_nulos = df['reviews_count'].isnull().sum()
            print(f"Reviews média: {reviews_media:.1f}")
            print(f"Reviews nulos: {reviews_nulos}")
        
        print(f"\n✅ VERIFICAÇÃO CONCLUÍDA!")
        print(f"Arquivo: {arquivo_final}")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

if __name__ == "__main__":
    verificacao_final()
