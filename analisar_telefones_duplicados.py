#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise e Remoção de Telefones Duplicados
==========================================

Script para identificar e remover telefones duplicados do arquivo Excel,
mantendo apenas um registro único por telefone.

Autor: Assistente IA
Data: 2025-01-17
"""

import pandas as pd
import numpy as np

def analisar_telefones_duplicados():
    """Analisa telefones duplicados no arquivo"""
    
    # Carregar o arquivo Excel
    arquivo = '../estabelecimentos_com_cidade_100_porcento.xlsx'
    df = pd.read_excel(arquivo)
    
    print("📊 ESTRUTURA DO ARQUIVO:")
    print("=" * 50)
    print(f"Total de registros: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    
    # Verificar se há coluna de telefone
    if 'telefone' in df.columns:
        print(f"\n📞 ANÁLISE DE TELEFONES:")
        print(f"Total de telefones: {len(df)}")
        print(f"Telefones únicos: {df['telefone'].nunique()}")
        print(f"Telefones duplicados: {len(df) - df['telefone'].nunique()}")
        
        # Verificar telefones vazios/nulos
        telefones_vazios = df['telefone'].isnull().sum()
        telefones_em_branco = (df['telefone'] == '').sum()
        print(f"Telefones vazios/nulos: {telefones_vazios}")
        print(f"Telefones em branco: {telefones_em_branco}")
        
        # Mostrar alguns exemplos de telefones duplicados
        duplicados = df[df.duplicated(subset=['telefone'], keep=False)]
        if len(duplicados) > 0:
            print(f"\n🔍 EXEMPLOS DE TELEFONES DUPLICADOS:")
            print(duplicados[['nome', 'telefone', 'cidade', 'estado']].head(10).to_string())
            
            # Agrupar por telefone para ver quantas vezes cada um se repete
            print(f"\n📈 TOP 10 TELEFONES MAIS REPETIDOS:")
            contagem_telefones = df['telefone'].value_counts().head(10)
            for telefone, count in contagem_telefones.items():
                if count > 1:
                    print(f"  {telefone}: {count} vezes")
        else:
            print("\n✅ Nenhum telefone duplicado encontrado")
    else:
        print("\n❌ Coluna 'telefone' não encontrada")
    
    return df

def remover_telefones_duplicados(df, criterio='primeiro'):
    """
    Remove telefones duplicados do DataFrame
    
    Args:
        df (DataFrame): DataFrame com os dados
        criterio (str): Critério para manter registro ('primeiro', 'ultimo', 'melhor')
    
    Returns:
        DataFrame: DataFrame sem duplicatas
    """
    
    print(f"\n🔧 REMOVENDO TELEFONES DUPLICADOS:")
    print("=" * 50)
    
    # Estatísticas antes da remoção
    total_antes = len(df)
    telefones_unicos_antes = df['telefone'].nunique()
    
    print(f"Registros antes: {total_antes}")
    print(f"Telefones únicos antes: {telefones_unicos_antes}")
    
    # Remover registros com telefones vazios/nulos primeiro
    df_limpo = df.dropna(subset=['telefone'])
    df_limpo = df_limpo[df_limpo['telefone'] != '']
    
    print(f"Após remover telefones vazios: {len(df_limpo)} registros")
    
    if criterio == 'primeiro':
        # Manter o primeiro registro de cada telefone
        df_sem_duplicatas = df_limpo.drop_duplicates(subset=['telefone'], keep='first')
        
    elif criterio == 'ultimo':
        # Manter o último registro de cada telefone
        df_sem_duplicatas = df_limpo.drop_duplicates(subset=['telefone'], keep='last')
        
    elif criterio == 'melhor':
        # Manter o registro com mais informações preenchidas
        print("Aplicando critério 'melhor' - mantendo registro com mais informações...")
        
        # Calcular score de completude para cada registro
        colunas_importantes = ['nome', 'endereco', 'cidade', 'estado', 'website', 'avaliacao']
        
        def calcular_score_completude(row):
            score = 0
            for col in colunas_importantes:
                if col in df_limpo.columns:
                    if pd.notna(row[col]) and str(row[col]).strip() != '':
                        score += 1
            return score
        
        df_limpo['score_completude'] = df_limpo.apply(calcular_score_completude, axis=1)
        
        # Para cada telefone, manter o registro com maior score
        df_sem_duplicatas = df_limpo.loc[df_limpo.groupby('telefone')['score_completude'].idxmax()]
        
        # Remover coluna auxiliar
        df_sem_duplicatas = df_sem_duplicatas.drop('score_completude', axis=1)
    
    # Estatísticas após a remoção
    total_depois = len(df_sem_duplicatas)
    telefones_unicos_depois = df_sem_duplicatas['telefone'].nunique()
    removidos = total_antes - total_depois
    
    print(f"\n📊 RESULTADOS:")
    print(f"Registros depois: {total_depois}")
    print(f"Telefones únicos depois: {telefones_unicos_depois}")
    print(f"Registros removidos: {removidos}")
    print(f"Taxa de remoção: {removidos/total_antes*100:.1f}%")
    
    return df_sem_duplicatas

def salvar_arquivo_limpo(df, nome_arquivo):
    """Salva o DataFrame limpo em um novo arquivo"""
    
    print(f"\n💾 SALVANDO ARQUIVO LIMPO:")
    print("=" * 50)
    
    # Salvar arquivo
    df.to_excel(nome_arquivo, index=False)
    
    print(f"✅ Arquivo salvo: {nome_arquivo}")
    print(f"Total de registros únicos: {len(df)}")
    
    # Verificação final
    duplicados_restantes = df[df.duplicated(subset=['telefone'], keep=False)]
    if len(duplicados_restantes) == 0:
        print("✅ Confirmado: Nenhum telefone duplicado restante")
    else:
        print(f"⚠️  Ainda existem {len(duplicados_restantes)} telefones duplicados")

def main():
    """Função principal"""
    
    print("🔍 ANÁLISE E REMOÇÃO DE TELEFONES DUPLICADOS")
    print("=" * 60)
    
    try:
        # 1. Analisar telefones duplicados
        df = analisar_telefones_duplicados()
        
        if 'telefone' not in df.columns:
            print("❌ Não é possível continuar sem a coluna 'telefone'")
            return
        
        # 2. Remover duplicatas usando critério 'melhor'
        df_limpo = remover_telefones_duplicados(df, criterio='melhor')
        
        # 3. Salvar arquivo limpo
        arquivo_saida = '../estabelecimentos_sem_telefones_duplicados.xlsx'
        salvar_arquivo_limpo(df_limpo, arquivo_saida)
        
        print(f"\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"Arquivo original: estabelecimentos_com_cidade_100_porcento.xlsx")
        print(f"Arquivo limpo: estabelecimentos_sem_telefones_duplicados.xlsx")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
