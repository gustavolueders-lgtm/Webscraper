#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação de Abas do Excel
"""

import pandas as pd

def verificar_abas():
    """Verifica quantas abas tem o arquivo Excel"""
    
    arquivo = '../estabelecimentos_com_cidade_100_porcento.xlsx'
    
    try:
        # Ler todas as abas
        excel_file = pd.ExcelFile(arquivo)
        abas = excel_file.sheet_names
        
        print(f'Arquivo: {arquivo}')
        print(f'Número de abas: {len(abas)}')
        print(f'Nomes das abas: {abas}')
        
        # Verificar cada aba
        for aba in abas:
            df = pd.read_excel(arquivo, sheet_name=aba)
            print(f'\nAba "{aba}": {len(df)} registros')
            if 'telefone' in df.columns:
                duplicados = len(df) - df['telefone'].nunique()
                print(f'  Telefones duplicados: {duplicados}')
            
    except Exception as e:
        print(f'Erro: {e}')

if __name__ == "__main__":
    verificar_abas()
