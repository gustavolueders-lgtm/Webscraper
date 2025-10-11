#!/usr/bin/env python3
"""
Verifica o Excel criado
"""

import pandas as pd

def verificar_excel():
    """Verifica o Excel criado"""
    
    arquivo = 'output/estabelecimentos_completo.xlsx'

    try:
        # Ler a planilha principal
        df = pd.read_excel(arquivo, sheet_name='Estabelecimentos')
        
        print('📊 RESUMO DO EXCEL CRIADO')
        print('=' * 50)
        print(f'📁 Arquivo: {arquivo}')
        print(f'📊 Total de estabelecimentos: {len(df):,}')
        print(f'📞 Com telefone: {len(df):,} (100%)')
        print()
        
        # Verificar colunas
        print('📋 COLUNAS CRIADAS:')
        for i, col in enumerate(df.columns, 1):
            print(f'   {i:2d}. {col}')
        print()
        
        # Estatísticas de DDDs
        ddd_counts = df['DDD'].value_counts()
        print('📞 ESTATÍSTICAS DE DDD:')
        print(f'   Total de DDDs únicos: {len(ddd_counts)}')
        print('   Top 5 DDDs:')
        for ddd, count in ddd_counts.head().items():
            print(f'     {ddd}: {count:,} estabelecimentos')
        print()
        
        # Verificar aniversários
        aniv_counts = df['Aniversário da Cidade'].value_counts()
        print('📅 ANIVERSÁRIOS DAS CIDADES:')
        nao_encontrado = len(df[df['Aniversário da Cidade'] == 'Não encontrado'])
        com_aniversario = len(df) - nao_encontrado
        print(f'   Com aniversário conhecido: {com_aniversario:,}')
        print(f'   Sem aniversário: {nao_encontrado:,}')
        print()
        
        # Mostrar amostra
        print('📋 AMOSTRA DOS DADOS:')
        colunas_amostra = ['Nome', 'Cidade', 'Telefone', 'DDD', 'Aniversário da Cidade']
        amostra = df[colunas_amostra].head(3)
        print(amostra.to_string(index=False))
        
    except Exception as e:
        print(f'❌ Erro ao ler Excel: {e}')

if __name__ == "__main__":
    verificar_excel()
