#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geocodificação Reversa Completa + Limpeza de Dados
==================================================

Script completo para:
1. Geocodificação reversa usando shapefile IBGE
2. Sistema de fallback para coordenadas no oceano
3. Preenchimento de DDD
4. Remoção de telefones duplicados

Autor: Assistente IA
Data: 2025-01-17
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import re
from tqdm import tqdm

class GeocodificacaoCompletaFinal:
    """Classe para geocodificação reversa completa com limpeza de dados"""
    
    def __init__(self, arquivo_excel, shapefile_path):
        """
        Inicializa o geocodificador
        
        Args:
            arquivo_excel (str): Caminho do arquivo Excel
            shapefile_path (str): Caminho do shapefile IBGE
        """
        self.arquivo_excel = arquivo_excel
        self.shapefile_path = shapefile_path
        self.df = None
        self.municipios_gdf = None
        self.spatial_index = None
        
    def carregar_dados(self):
        """Carrega dados do Excel e shapefile"""
        
        print("📂 CARREGANDO DADOS:")
        print("=" * 50)
        
        try:
            # Carregar Excel
            self.df = pd.read_excel(self.arquivo_excel)
            print(f"✅ Excel carregado: {len(self.df)} registros")
            print(f"Colunas: {list(self.df.columns)}")
            
            # Carregar shapefile IBGE
            self.municipios_gdf = gpd.read_file(self.shapefile_path)
            print(f"✅ Shapefile carregado: {len(self.municipios_gdf)} municípios")
            
            # Verificar CRS e converter se necessário
            if self.municipios_gdf.crs != 'EPSG:4326':
                print(f"Convertendo CRS de {self.municipios_gdf.crs} para EPSG:4326")
                self.municipios_gdf = self.municipios_gdf.to_crs('EPSG:4326')
            
            # Criar índice espacial
            print("Criando índice espacial...")
            self.spatial_index = self.municipios_gdf.sindex
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def validar_coordenadas(self, lat, lon):
        """Valida se as coordenadas estão dentro dos limites do Brasil"""
        
        # Limites aproximados do Brasil
        if not (-33.75 <= lat <= 5.27):
            return False
        if not (-73.98 <= lon <= -28.84):
            return False
        return True
    
    def encontrar_municipio(self, lat, lon):
        """
        Encontra município para coordenadas com sistema de fallback
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Informações do município encontrado
        """
        
        # Validar coordenadas
        if not self.validar_coordenadas(lat, lon):
            return {
                'cidade': 'Coordenada inválida',
                'estado': '',
                'codigo_ibge': '',
                'precisao': 'inválido'
            }
        
        ponto = Point(lon, lat)
        
        # MÉTODO 1: Verificação exata - ponto dentro do polígono
        candidatos_indices = list(self.spatial_index.intersection(ponto.bounds))
        candidatos = self.municipios_gdf.iloc[candidatos_indices]
        
        for idx, municipio in candidatos.iterrows():
            if municipio.geometry.contains(ponto):
                return {
                    'cidade': municipio['NM_MUN'],
                    'estado': municipio['SIGLA_UF'],
                    'codigo_ibge': municipio['CD_MUN'],
                    'precisao': 'exato'
                }
        
        # MÉTODO 2: Sistema de fallback com buffer crescente
        buffers = [0.01, 0.05, 0.1, 0.25, 0.5]  # ~1km, 5km, 10km, 25km, 50km
        precisoes = ['muito_próximo', 'próximo', 'próximo', 'distante', 'muito_distante']
        
        for buffer_size, precisao in zip(buffers, precisoes):
            buffer_area = ponto.buffer(buffer_size)
            municipios_proximos = self.municipios_gdf[self.municipios_gdf.geometry.intersects(buffer_area)]
            
            if len(municipios_proximos) > 0:
                # Encontrar o município mais próximo
                distancias = municipios_proximos.geometry.distance(ponto)
                municipio_mais_proximo = municipios_proximos.loc[distancias.idxmin()]
                
                # Verificar se está no oceano (muito longe da terra)
                distancia_km = distancias.min() * 111  # Conversão aproximada para km
                
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
        
        # MÉTODO 3: Último recurso - município mais próximo do Brasil inteiro
        distancias_todas = self.municipios_gdf.geometry.distance(ponto)
        municipio_mais_proximo = self.municipios_gdf.loc[distancias_todas.idxmin()]
        
        return {
            'cidade': municipio_mais_proximo['NM_MUN'],
            'estado': municipio_mais_proximo['SIGLA_UF'],
            'codigo_ibge': municipio_mais_proximo['CD_MUN'],
            'precisao': 'extremamente_distante'
        }
    
    def extrair_ddd(self, telefone):
        """
        Extrai DDD do telefone
        
        Args:
            telefone (str): Número de telefone
            
        Returns:
            str: DDD ou None
        """
        if not telefone or pd.isna(telefone):
            return None
        
        # Remover caracteres não numéricos e extrair primeiros 2 dígitos
        numeros = re.sub(r'[^\d]', '', str(telefone))
        
        if len(numeros) >= 2:
            return numeros[:2]
        
        return None
    
    def processar_geocodificacao(self):
        """Processa geocodificação reversa para todos os registros"""
        
        print("\n🗺️  PROCESSANDO GEOCODIFICAÇÃO REVERSA:")
        print("=" * 60)
        
        # Verificar se há colunas de coordenadas
        if 'latitude' not in self.df.columns or 'longitude' not in self.df.columns:
            print("❌ Colunas 'latitude' e 'longitude' não encontradas")
            return False
        
        # Inicializar colunas de resultado
        self.df['cidade'] = ''
        self.df['estado'] = ''
        self.df['codigo_ibge'] = ''
        self.df['precisao'] = ''
        
        # Processar em lotes para melhor performance
        batch_size = 100
        total_registros = len(self.df)
        
        print(f"Processando {total_registros} registros em lotes de {batch_size}...")
        
        for i in tqdm(range(0, total_registros, batch_size), desc="Geocodificando"):
            batch_end = min(i + batch_size, total_registros)
            
            for idx in range(i, batch_end):
                try:
                    lat = self.df.loc[idx, 'latitude']
                    lon = self.df.loc[idx, 'longitude']
                    
                    if pd.isna(lat) or pd.isna(lon):
                        resultado = {
                            'cidade': 'Coordenada ausente',
                            'estado': '',
                            'codigo_ibge': '',
                            'precisao': 'ausente'
                        }
                    else:
                        resultado = self.encontrar_municipio(lat, lon)
                    
                    # Atualizar DataFrame
                    self.df.loc[idx, 'cidade'] = resultado['cidade']
                    self.df.loc[idx, 'estado'] = resultado['estado']
                    self.df.loc[idx, 'codigo_ibge'] = resultado['codigo_ibge']
                    self.df.loc[idx, 'precisao'] = resultado['precisao']
                    
                except Exception as e:
                    print(f"⚠️  Erro no registro {idx}: {e}")
                    self.df.loc[idx, 'cidade'] = 'Erro'
                    self.df.loc[idx, 'estado'] = ''
                    self.df.loc[idx, 'codigo_ibge'] = ''
                    self.df.loc[idx, 'precisao'] = 'erro'
        
        # Estatísticas finais
        print(f"\n📊 RESULTADOS DA GEOCODIFICAÇÃO:")
        precisao_counts = self.df['precisao'].value_counts()
        for precisao, count in precisao_counts.items():
            print(f"  {precisao}: {count} registros")
        
        return True
    
    def preencher_ddd(self):
        """Preenche coluna DDD baseada no telefone"""
        
        print("\n📞 PREENCHENDO COLUNA DDD:")
        print("=" * 50)
        
        if 'Phone' not in self.df.columns:
            print("❌ Coluna 'Phone' não encontrada")
            return False
        
        # Criar ou atualizar coluna DDD
        self.df['DDD'] = self.df['Phone'].apply(self.extrair_ddd)
        
        # Estatísticas
        ddds_preenchidos = self.df['DDD'].notna().sum()
        ddds_unicos = self.df['DDD'].nunique()
        
        print(f"✅ DDDs preenchidos: {ddds_preenchidos}/{len(self.df)}")
        print(f"📊 DDDs únicos: {ddds_unicos}")
        
        # Mostrar DDDs mais comuns
        if ddds_preenchidos > 0:
            top_ddds = self.df['DDD'].value_counts().head(10)
            print(f"\n📈 TOP 10 DDDs:")
            for ddd, count in top_ddds.items():
                print(f"  {ddd}: {count} registros")
        
        return True

    def remover_telefones_duplicados(self):
        """Remove registros com telefones duplicados"""

        print("\n🔧 REMOVENDO TELEFONES DUPLICADOS:")
        print("=" * 50)

        if 'Phone' not in self.df.columns:
            print("❌ Coluna 'Phone' não encontrada")
            return False

        # Estatísticas antes
        total_antes = len(self.df)

        # Separar registros com e sem telefone
        df_com_telefone = self.df[self.df['Phone'].notna() & (self.df['Phone'] != '')]
        df_sem_telefone = self.df[self.df['Phone'].isna() | (self.df['Phone'] == '')]

        print(f"Registros com telefone: {len(df_com_telefone)}")
        print(f"Registros sem telefone: {len(df_sem_telefone)}")

        if len(df_com_telefone) == 0:
            print("⚠️  Nenhum registro com telefone para processar")
            return True

        # Verificar duplicatas
        telefones_unicos_antes = df_com_telefone['Phone'].nunique()
        duplicados = len(df_com_telefone) - telefones_unicos_antes

        print(f"Telefones únicos: {telefones_unicos_antes}")
        print(f"Telefones duplicados: {duplicados}")

        if duplicados == 0:
            print("✅ Nenhum telefone duplicado encontrado")
            return True

        # Aplicar critério de melhor registro
        print("Aplicando critério 'melhor registro' para duplicatas...")

        def calcular_score_completude(row):
            """Calcula score baseado na completude e qualidade dos dados"""
            score = 0

            # Campos importantes
            campos_importantes = ['Nome', 'rating', 'reviews_count', 'address', 'website', 'cidade', 'estado']

            for campo in campos_importantes:
                if campo in row and pd.notna(row[campo]) and str(row[campo]).strip() != '':
                    score += 1

            # Bonus para rating alto
            if pd.notna(row.get('rating')):
                try:
                    rating = float(row['rating'])
                    if rating >= 4.5:
                        score += 3
                    elif rating >= 4.0:
                        score += 2
                    elif rating >= 3.5:
                        score += 1
                except:
                    pass

            # Bonus para muitas reviews
            if pd.notna(row.get('reviews_count')):
                try:
                    reviews = int(row['reviews_count'])
                    if reviews >= 100:
                        score += 3
                    elif reviews >= 50:
                        score += 2
                    elif reviews >= 10:
                        score += 1
                except:
                    pass

            # Bonus para precisão da geocodificação
            precisao = row.get('precisao', '')
            if precisao == 'exato':
                score += 3
            elif precisao in ['muito_próximo', 'próximo']:
                score += 2
            elif precisao == 'distante':
                score += 1

            return score

        # Calcular score para cada registro
        df_com_telefone = df_com_telefone.copy()
        df_com_telefone['score_completude'] = df_com_telefone.apply(calcular_score_completude, axis=1)

        # Para cada telefone, manter o registro com maior score
        df_sem_duplicatas = df_com_telefone.loc[df_com_telefone.groupby('Phone')['score_completude'].idxmax()]

        # Remover coluna auxiliar
        df_sem_duplicatas = df_sem_duplicatas.drop('score_completude', axis=1)

        # Combinar com registros sem telefone
        self.df = pd.concat([df_sem_duplicatas, df_sem_telefone], ignore_index=True)

        # Estatísticas após
        total_depois = len(self.df)
        telefones_unicos_depois = self.df['Phone'].nunique()
        removidos = total_antes - total_depois

        print(f"\n📊 RESULTADOS:")
        print(f"Registros depois: {total_depois}")
        print(f"Telefones únicos depois: {telefones_unicos_depois}")
        print(f"Registros removidos: {removidos}")
        print(f"Taxa de remoção: {removidos/total_antes*100:.1f}%")

        return True

    def salvar_resultado(self, arquivo_saida):
        """Salva o resultado final"""

        print(f"\n💾 SALVANDO RESULTADO FINAL:")
        print("=" * 50)

        try:
            # Reorganizar colunas para melhor visualização
            colunas_principais = ['Nome', 'rating', 'reviews_count', 'DDD', 'Phone', 'cidade', 'estado', 'latitude', 'longitude', 'precisao']
            colunas_extras = [col for col in self.df.columns if col not in colunas_principais]

            colunas_finais = colunas_principais + colunas_extras
            colunas_existentes = [col for col in colunas_finais if col in self.df.columns]

            df_final = self.df[colunas_existentes]

            # Salvar arquivo
            df_final.to_excel(arquivo_saida, index=False)

            print(f"✅ Arquivo salvo: {arquivo_saida}")
            print(f"📊 Total de registros: {len(df_final)}")
            print(f"📋 Colunas: {len(df_final.columns)}")

            # Estatísticas finais
            print(f"\n📈 ESTATÍSTICAS FINAIS:")
            print(f"Registros com telefone: {df_final['Phone'].notna().sum()}")
            print(f"Registros com cidade: {(df_final['cidade'] != '').sum()}")
            print(f"Registros com estado: {(df_final['estado'] != '').sum()}")

            # Verificação de duplicatas
            duplicados_restantes = df_final[df_final['Phone'].notna() & df_final.duplicated(subset=['Phone'], keep=False)]
            if len(duplicados_restantes) == 0:
                print("✅ Confirmado: Nenhum telefone duplicado restante")
            else:
                print(f"⚠️  Ainda existem {len(duplicados_restantes)} telefones duplicados")

            return True

        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return False

    def processar_completo(self, arquivo_saida):
        """Executa todo o processo completo"""

        print("🚀 GEOCODIFICAÇÃO COMPLETA + LIMPEZA DE DADOS")
        print("=" * 70)

        try:
            # 1. Carregar dados
            if not self.carregar_dados():
                return False

            # 2. Processar geocodificação reversa
            if not self.processar_geocodificacao():
                return False

            # 3. Preencher DDD
            if not self.preencher_ddd():
                return False

            # 4. Remover telefones duplicados
            if not self.remover_telefones_duplicados():
                return False

            # 5. Salvar resultado
            if not self.salvar_resultado(arquivo_saida):
                return False

            print(f"\n🎉 PROCESSO COMPLETO FINALIZADO COM SUCESSO!")
            print(f"Arquivo de entrada: {self.arquivo_excel}")
            print(f"Arquivo de saída: {arquivo_saida}")
            print("Todas as tarefas foram concluídas!")

            return True

        except Exception as e:
            print(f"❌ ERRO GERAL: {e}")
            return False

def main():
    """Função principal"""

    # Configurações
    arquivo_excel = '../tire_shops_excel_final.xlsx'
    shapefile_path = '../IBGE/BR_Municipios_2024.shp'
    arquivo_saida = '../estabelecimentos_geocodificados_final.xlsx'

    # Criar processador e executar
    processador = GeocodificacaoCompletaFinal(arquivo_excel, shapefile_path)
    sucesso = processador.processar_completo(arquivo_saida)

    if sucesso:
        print("\n✅ Todas as tarefas foram concluídas com sucesso!")
    else:
        print("\n❌ Falha no processamento!")

if __name__ == "__main__":
    main()
