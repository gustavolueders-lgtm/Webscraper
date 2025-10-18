#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remoção Completa de Telefones Duplicados
=========================================

Script para processar todas as abas do arquivo Excel e remover telefones duplicados,
garantindo que cada contato seja único.

Autor: Assistente IA
Data: 2025-01-17
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook

class RemoverTelefonesDuplicados:
    """Classe para remover telefones duplicados de arquivos Excel"""
    
    def __init__(self, arquivo_entrada):
        """
        Inicializa o removedor de duplicatas
        
        Args:
            arquivo_entrada (str): Caminho do arquivo Excel de entrada
        """
        self.arquivo_entrada = arquivo_entrada
        self.dados_processados = {}
        
    def analisar_arquivo(self):
        """Analisa a estrutura do arquivo Excel"""
        
        print("📊 ANÁLISE DO ARQUIVO:")
        print("=" * 50)
        
        try:
            # Ler informações do arquivo
            excel_file = pd.ExcelFile(self.arquivo_entrada)
            abas = excel_file.sheet_names
            
            print(f"Arquivo: {self.arquivo_entrada}")
            print(f"Número de abas: {len(abas)}")
            print(f"Nomes das abas: {abas}")
            
            # Analisar cada aba
            for aba in abas:
                df = pd.read_excel(self.arquivo_entrada, sheet_name=aba)
                
                print(f"\n📋 ABA '{aba}':")
                print(f"  Total de registros: {len(df)}")
                print(f"  Colunas: {list(df.columns)}")
                
                if 'telefone' in df.columns:
                    telefones_unicos = df['telefone'].nunique()
                    telefones_vazios = df['telefone'].isnull().sum()
                    telefones_em_branco = (df['telefone'] == '').sum()
                    duplicados = len(df) - telefones_unicos
                    
                    print(f"  📞 Telefones únicos: {telefones_unicos}")
                    print(f"  📞 Telefones vazios/nulos: {telefones_vazios}")
                    print(f"  📞 Telefones em branco: {telefones_em_branco}")
                    print(f"  📞 Telefones duplicados: {duplicados}")
                    
                    if duplicados > 0:
                        print(f"  ⚠️  Taxa de duplicação: {duplicados/len(df)*100:.1f}%")
                else:
                    print("  ❌ Coluna 'telefone' não encontrada")
            
            return abas
            
        except Exception as e:
            print(f"❌ Erro ao analisar arquivo: {e}")
            return []
    
    def processar_aba(self, nome_aba):
        """
        Processa uma aba específica removendo duplicatas
        
        Args:
            nome_aba (str): Nome da aba a processar
            
        Returns:
            DataFrame: DataFrame sem duplicatas
        """
        
        print(f"\n🔧 PROCESSANDO ABA '{nome_aba}':")
        print("=" * 50)
        
        # Carregar dados da aba
        df = pd.read_excel(self.arquivo_entrada, sheet_name=nome_aba)
        
        if 'telefone' not in df.columns:
            print(f"❌ Aba '{nome_aba}' não possui coluna 'telefone'")
            return df
        
        # Estatísticas antes
        total_antes = len(df)
        telefones_unicos_antes = df['telefone'].nunique()
        
        print(f"Registros antes: {total_antes}")
        print(f"Telefones únicos antes: {telefones_unicos_antes}")
        
        # Remover registros com telefones vazios/nulos
        df_limpo = df.dropna(subset=['telefone'])
        df_limpo = df_limpo[df_limpo['telefone'] != '']
        df_limpo = df_limpo[df_limpo['telefone'].str.strip() != '']
        
        print(f"Após remover telefones vazios: {len(df_limpo)} registros")
        
        if len(df_limpo) == 0:
            print("⚠️  Nenhum registro com telefone válido encontrado")
            return df_limpo
        
        # Aplicar critério de melhor registro
        print("Aplicando critério 'melhor registro' para duplicatas...")
        
        # Definir colunas importantes para calcular score
        colunas_importantes = ['nome', 'endereco', 'cidade', 'estado', 'website', 'avaliacao', 'horario']
        
        def calcular_score_completude(row):
            """Calcula score baseado na completude dos dados"""
            score = 0
            for col in colunas_importantes:
                if col in df_limpo.columns:
                    valor = row[col]
                    if pd.notna(valor) and str(valor).strip() != '' and str(valor).lower() != 'nan':
                        score += 1
            
            # Bonus para avaliação alta
            if 'avaliacao' in df_limpo.columns and pd.notna(row['avaliacao']):
                try:
                    avaliacao = float(row['avaliacao'])
                    if avaliacao >= 4.0:
                        score += 2
                    elif avaliacao >= 3.0:
                        score += 1
                except:
                    pass
            
            # Bonus para mais avaliações
            if 'num_avaliacoes' in df_limpo.columns and pd.notna(row['num_avaliacoes']):
                try:
                    num_aval = int(row['num_avaliacoes'])
                    if num_aval >= 10:
                        score += 2
                    elif num_aval >= 5:
                        score += 1
                except:
                    pass
            
            return score
        
        # Calcular score para cada registro
        df_limpo['score_completude'] = df_limpo.apply(calcular_score_completude, axis=1)
        
        # Para cada telefone, manter o registro com maior score
        # Em caso de empate, manter o primeiro
        df_sem_duplicatas = df_limpo.loc[df_limpo.groupby('telefone')['score_completude'].idxmax()]
        
        # Remover coluna auxiliar
        df_sem_duplicatas = df_sem_duplicatas.drop('score_completude', axis=1)
        
        # Estatísticas após
        total_depois = len(df_sem_duplicatas)
        telefones_unicos_depois = df_sem_duplicatas['telefone'].nunique()
        removidos = total_antes - total_depois
        
        print(f"\n📊 RESULTADOS DA ABA '{nome_aba}':")
        print(f"Registros depois: {total_depois}")
        print(f"Telefones únicos depois: {telefones_unicos_depois}")
        print(f"Registros removidos: {removidos}")
        print(f"Taxa de remoção: {removidos/total_antes*100:.1f}%")
        
        # Verificação final
        duplicados_restantes = df_sem_duplicatas[df_sem_duplicatas.duplicated(subset=['telefone'], keep=False)]
        if len(duplicados_restantes) == 0:
            print("✅ Confirmado: Nenhum telefone duplicado restante")
        else:
            print(f"⚠️  Ainda existem {len(duplicados_restantes)} telefones duplicados")
        
        return df_sem_duplicatas
    
    def processar_todas_abas(self):
        """Processa todas as abas do arquivo"""
        
        print("\n🔄 PROCESSANDO TODAS AS ABAS:")
        print("=" * 60)
        
        # Analisar arquivo
        abas = self.analisar_arquivo()
        
        if not abas:
            return False
        
        # Processar cada aba
        for aba in abas:
            df_processado = self.processar_aba(aba)
            self.dados_processados[aba] = df_processado
        
        return True
    
    def salvar_arquivo_limpo(self, arquivo_saida):
        """Salva o arquivo limpo com todas as abas processadas"""
        
        print(f"\n💾 SALVANDO ARQUIVO LIMPO:")
        print("=" * 50)
        
        try:
            if len(self.dados_processados) == 1:
                # Se há apenas uma aba, salvar diretamente
                aba_nome = list(self.dados_processados.keys())[0]
                df = self.dados_processados[aba_nome]
                df.to_excel(arquivo_saida, index=False)
                
                print(f"✅ Arquivo salvo: {arquivo_saida}")
                print(f"Total de registros únicos: {len(df)}")
                
            else:
                # Se há múltiplas abas, manter estrutura
                with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
                    total_registros = 0
                    
                    for aba_nome, df in self.dados_processados.items():
                        df.to_excel(writer, sheet_name=aba_nome, index=False)
                        total_registros += len(df)
                        print(f"  Aba '{aba_nome}': {len(df)} registros")
                    
                    print(f"✅ Arquivo salvo: {arquivo_saida}")
                    print(f"Total de registros únicos: {total_registros}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return False
    
    def gerar_relatorio_final(self):
        """Gera relatório final do processamento"""
        
        print(f"\n📈 RELATÓRIO FINAL:")
        print("=" * 50)
        
        total_registros_finais = 0
        total_telefones_unicos = 0
        
        for aba_nome, df in self.dados_processados.items():
            registros = len(df)
            telefones_unicos = df['telefone'].nunique() if 'telefone' in df.columns else 0
            
            total_registros_finais += registros
            total_telefones_unicos += telefones_unicos
            
            print(f"Aba '{aba_nome}':")
            print(f"  📊 Registros finais: {registros}")
            print(f"  📞 Telefones únicos: {telefones_unicos}")
            
            if telefones_unicos > 0 and telefones_unicos == registros:
                print(f"  ✅ 100% únicos")
            elif telefones_unicos > 0:
                print(f"  ⚠️  {registros - telefones_unicos} duplicatas restantes")
        
        print(f"\n🎯 TOTAIS GERAIS:")
        print(f"Total de registros: {total_registros_finais}")
        print(f"Total de telefones únicos: {total_telefones_unicos}")
        
        if total_telefones_unicos == total_registros_finais:
            print("✅ SUCESSO: 100% dos contatos são únicos!")
        else:
            print(f"⚠️  {total_registros_finais - total_telefones_unicos} duplicatas ainda existem")

def main():
    """Função principal"""
    
    print("🔍 REMOÇÃO COMPLETA DE TELEFONES DUPLICADOS")
    print("=" * 70)
    
    # Configurações
    arquivo_entrada = '../estabelecimentos_com_cidade_100_porcento.xlsx'
    arquivo_saida = '../estabelecimentos_telefones_unicos_final.xlsx'
    
    try:
        # Criar instância do removedor
        removedor = RemoverTelefonesDuplicados(arquivo_entrada)
        
        # Processar todas as abas
        if not removedor.processar_todas_abas():
            print("❌ Falha no processamento")
            return False
        
        # Salvar arquivo limpo
        if not removedor.salvar_arquivo_limpo(arquivo_saida):
            print("❌ Falha ao salvar arquivo")
            return False
        
        # Gerar relatório final
        removedor.gerar_relatorio_final()
        
        print(f"\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"Arquivo original: {arquivo_entrada}")
        print(f"Arquivo final: {arquivo_saida}")
        print("Todos os telefones duplicados foram removidos!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

if __name__ == "__main__":
    main()
