#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converter JSON para Excel
=========================

Converte o arquivo tire_shops_auto_complete.json para Excel com colunas específicas
e remove telefones duplicados.

Autor: Assistente IA
Data: 2025-01-17
"""

import json
import pandas as pd
import re

class ConversorJSONParaExcel:
    """Classe para converter JSON para Excel"""
    
    def __init__(self, arquivo_json):
        """
        Inicializa o conversor
        
        Args:
            arquivo_json (str): Caminho do arquivo JSON
        """
        self.arquivo_json = arquivo_json
        self.dados = []
        
    def carregar_json(self):
        """Carrega os dados do arquivo JSON"""
        
        print("📂 CARREGANDO ARQUIVO JSON:")
        print("=" * 50)
        
        try:
            with open(self.arquivo_json, 'r', encoding='utf-8') as f:
                self.dados = json.load(f)
            
            print(f"✅ Arquivo carregado: {self.arquivo_json}")
            print(f"📊 Total de registros: {len(self.dados)}")
            
            # Verificar quantos têm telefone
            com_telefone = sum(1 for r in self.dados if r.get('phone'))
            print(f"📞 Registros com telefone: {com_telefone}/{len(self.dados)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar JSON: {e}")
            return False
    
    def extrair_ddd(self, telefone):
        """
        Extrai o DDD do telefone
        
        Args:
            telefone (str): Número de telefone
            
        Returns:
            int: DDD como número ou None
        """
        if not telefone:
            return None
        
        # Padrão: "XX XXXXX-XXXX" ou similar
        match = re.match(r'^(\d{2})', telefone.strip())
        if match:
            return int(match.group(1))
        
        return None
    
    def extrair_cidade_do_endereco(self, endereco):
        """
        Tenta extrair cidade do endereço (básico)
        
        Args:
            endereco (str): Endereço completo
            
        Returns:
            str: Cidade extraída ou vazio
        """
        if not endereco:
            return ""
        
        # Procurar por padrões comuns de cidade
        # Exemplo: "Santa Catarina, Brasil"
        if "Santa Catarina" in endereco:
            return "Santa Catarina"
        elif "Brasil" in endereco:
            # Tentar extrair antes de "Brasil"
            parts = endereco.split("Brasil")[0].strip()
            if "," in parts:
                return parts.split(",")[-1].strip()
        
        # Se não encontrar padrão, deixar vazio
        return ""
    
    def converter_para_dataframe(self):
        """Converte os dados JSON para DataFrame do pandas"""
        
        print("\n🔄 CONVERTENDO DADOS:")
        print("=" * 50)
        
        registros_convertidos = []
        
        for i, record in enumerate(self.dados):
            try:
                # Extrair DDD
                ddd = self.extrair_ddd(record.get('phone'))
                
                # Extrair cidade (básico)
                cidade = self.extrair_cidade_do_endereco(record.get('address', ''))
                
                # Criar registro convertido com colunas na ordem solicitada
                registro_convertido = {
                    # Colunas principais na ordem solicitada
                    'Nome': record.get('name', ''),
                    'rating': record.get('rating'),
                    'reviews_count': record.get('reviews_count'),
                    'DDD': ddd,
                    'Phone': record.get('phone'),
                    'cidade': cidade,
                    'latitude': record.get('cell_lat'),
                    'longitude': record.get('cell_lon'),
                    
                    # Resto dos dados após longitude
                    'place_id': record.get('place_id'),
                    'category': record.get('category'),
                    'address': record.get('address'),
                    'website': record.get('website'),
                    'hours': record.get('hours'),
                    'link': record.get('link'),
                    'scraped_at': record.get('scraped_at'),
                    'search_term': record.get('search_term'),
                    'cell_index': record.get('cell_index'),
                    'source': record.get('source')
                }
                
                registros_convertidos.append(registro_convertido)
                
            except Exception as e:
                print(f"⚠️  Erro no registro {i+1}: {e}")
                continue
        
        # Criar DataFrame
        df = pd.DataFrame(registros_convertidos)
        
        print(f"✅ Conversão concluída: {len(df)} registros")
        print(f"📊 Colunas: {list(df.columns)}")
        
        return df
    
    def remover_telefones_duplicados(self, df):
        """Remove registros com telefones duplicados"""
        
        print("\n🔧 REMOVENDO TELEFONES DUPLICADOS:")
        print("=" * 50)
        
        # Estatísticas antes
        total_antes = len(df)
        
        # Filtrar apenas registros com telefone
        df_com_telefone = df[df['Phone'].notna() & (df['Phone'] != '')]
        df_sem_telefone = df[df['Phone'].isna() | (df['Phone'] == '')]
        
        print(f"Registros com telefone: {len(df_com_telefone)}")
        print(f"Registros sem telefone: {len(df_sem_telefone)}")
        
        if len(df_com_telefone) == 0:
            print("⚠️  Nenhum registro com telefone para processar")
            return df
        
        # Verificar duplicatas
        telefones_unicos_antes = df_com_telefone['Phone'].nunique()
        duplicados = len(df_com_telefone) - telefones_unicos_antes
        
        print(f"Telefones únicos: {telefones_unicos_antes}")
        print(f"Telefones duplicados: {duplicados}")
        
        if duplicados == 0:
            print("✅ Nenhum telefone duplicado encontrado")
            return df
        
        # Aplicar critério de melhor registro para duplicatas
        print("Aplicando critério 'melhor registro' para duplicatas...")
        
        def calcular_score_completude(row):
            """Calcula score baseado na completude dos dados"""
            score = 0
            
            # Campos importantes
            campos_importantes = ['Nome', 'rating', 'reviews_count', 'address', 'website']
            
            for campo in campos_importantes:
                if campo in row and pd.notna(row[campo]) and str(row[campo]).strip() != '':
                    score += 1
            
            # Bonus para rating alto
            if pd.notna(row['rating']):
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
            if pd.notna(row['reviews_count']):
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
            
            return score
        
        # Calcular score para registros com telefone
        df_com_telefone['score_completude'] = df_com_telefone.apply(calcular_score_completude, axis=1)
        
        # Para cada telefone, manter o registro com maior score
        df_sem_duplicatas = df_com_telefone.loc[df_com_telefone.groupby('Phone')['score_completude'].idxmax()]
        
        # Remover coluna auxiliar
        df_sem_duplicatas = df_sem_duplicatas.drop('score_completude', axis=1)
        
        # Combinar com registros sem telefone
        df_final = pd.concat([df_sem_duplicatas, df_sem_telefone], ignore_index=True)
        
        # Estatísticas após
        total_depois = len(df_final)
        telefones_unicos_depois = df_final['Phone'].nunique()
        removidos = total_antes - total_depois
        
        print(f"\n📊 RESULTADOS:")
        print(f"Registros depois: {total_depois}")
        print(f"Telefones únicos depois: {telefones_unicos_depois}")
        print(f"Registros removidos: {removidos}")
        print(f"Taxa de remoção: {removidos/total_antes*100:.1f}%")
        
        return df_final
    
    def salvar_excel(self, df, arquivo_saida):
        """Salva o DataFrame em arquivo Excel"""
        
        print(f"\n💾 SALVANDO ARQUIVO EXCEL:")
        print("=" * 50)
        
        try:
            # Salvar arquivo
            df.to_excel(arquivo_saida, index=False)
            
            print(f"✅ Arquivo salvo: {arquivo_saida}")
            print(f"📊 Total de registros: {len(df)}")
            print(f"📞 Registros com telefone: {df['Phone'].notna().sum()}")
            
            # Verificação final de duplicatas
            duplicados_restantes = df[df['Phone'].notna() & df.duplicated(subset=['Phone'], keep=False)]
            if len(duplicados_restantes) == 0:
                print("✅ Confirmado: Nenhum telefone duplicado restante")
            else:
                print(f"⚠️  Ainda existem {len(duplicados_restantes)} telefones duplicados")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return False
    
    def processar(self, arquivo_saida):
        """Processa todo o fluxo de conversão"""
        
        print("🔄 CONVERSÃO JSON PARA EXCEL")
        print("=" * 60)
        
        try:
            # 1. Carregar JSON
            if not self.carregar_json():
                return False
            
            # 2. Converter para DataFrame
            df = self.converter_para_dataframe()
            
            if df.empty:
                print("❌ Nenhum dado para processar")
                return False
            
            # 3. Remover telefones duplicados
            df_limpo = self.remover_telefones_duplicados(df)
            
            # 4. Salvar Excel
            if not self.salvar_excel(df_limpo, arquivo_saida):
                return False
            
            print(f"\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
            print(f"Arquivo JSON: {self.arquivo_json}")
            print(f"Arquivo Excel: {arquivo_saida}")
            
            return True
            
        except Exception as e:
            print(f"❌ ERRO GERAL: {e}")
            return False

def main():
    """Função principal"""
    
    # Configurações
    arquivo_json = 'output/tire_shops_auto_complete.json'
    arquivo_excel = 'tire_shops_excel_final.xlsx'
    
    # Criar conversor e processar
    conversor = ConversorJSONParaExcel(arquivo_json)
    sucesso = conversor.processar(arquivo_excel)
    
    if sucesso:
        print("\n✅ Conversão realizada com sucesso!")
    else:
        print("\n❌ Falha na conversão!")

if __name__ == "__main__":
    main()
