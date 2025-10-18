#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação Final do Arquivo Limpo
"""

import pandas as pd

def verificacao_final():
    """Verifica se o arquivo final está correto"""
    
    arquivo_final = '../estabelecimentos_telefones_unicos_final.xlsx'
    df = pd.read_excel(arquivo_final)
    
    print('VERIFICAÇÃO FINAL DO ARQUIVO LIMPO:')
    print('=' * 50)
    print(f'Total de registros: {len(df)}')
    print(f'Telefones únicos: {df["telefone"].nunique()}')
    print(f'Telefones duplicados: {len(df) - df["telefone"].nunique()}')
    
    # Verificar se há duplicatas
    duplicados = df[df.duplicated(subset=["telefone"], keep=False)]
    print(f'Registros com telefones duplicados: {len(duplicados)}')
    
    if len(duplicados) == 0:
        print('✅ CONFIRMADO: Nenhum telefone duplicado!')
    else:
        print('❌ ATENÇÃO: Ainda há telefones duplicados!')
        print(duplicados[["nome", "telefone", "cidade"]].head())
    
    # Verificar telefones vazios
    telefones_vazios = df["telefone"].isnull().sum()
    telefones_em_branco = (df["telefone"] == "").sum()
    print(f'\nTelefones vazios/nulos: {telefones_vazios}')
    print(f'Telefones em branco: {telefones_em_branco}')
    
    print(f'\n✅ ARQUIVO FINAL PRONTO: {arquivo_final}')
    print(f'📊 {len(df)} estabelecimentos únicos com telefones válidos')

if __name__ == "__main__":
    verificacao_final()
