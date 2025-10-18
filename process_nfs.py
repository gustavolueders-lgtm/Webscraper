#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar notas fiscais em PDF e gerar relatório Excel
"""

import pdfplumber
import pandas as pd
import os
import re
from tqdm import tqdm

def extract_nf_data(pdf_path):
    """Extrai dados básicos de uma nota fiscal em PDF"""
    data = {
        'arquivo': os.path.basename(pdf_path),
        'numero_nf': '',
        'natureza_operacao': '',
        'destinatario': '',
        'cnpj': '',
        'data_emissao': '',
        'codigo_item': '',
        'descricao_produto': '',
        'quantidade': '',
        'valor_unitario': '',
        'valor_total': ''
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                if text:
                    # Extrai número da NF
                    nf_match = re.search(r'Nº\s*(\d{3}\.\d{3}\.\d{3})', text)
                    if nf_match:
                        data['numero_nf'] = nf_match.group(1)
                    
                    # Extrai natureza da operação
                    natureza_match = re.search(r'NATUREZA DA OPERAÇÃO\s*\n([^\n]+)', text)
                    if natureza_match:
                        data['natureza_operacao'] = natureza_match.group(1).strip()
                    
                    # Extrai destinatário
                    dest_match = re.search(r'NOME/RAZÃO SOCIAL.*?\n([^\n]+)', text, re.DOTALL)
                    if dest_match:
                        destinatario = dest_match.group(1).strip()
                        # Remove CNPJ se estiver junto
                        destinatario = re.sub(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', '', destinatario).strip()
                        if destinatario:
                            data['destinatario'] = destinatario
                    
                    # Extrai CNPJ
                    cnpj_match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', text)
                    if cnpj_match:
                        data['cnpj'] = cnpj_match.group(1)
                    
                    # Extrai data de emissão
                    data_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
                    if data_match:
                        data['data_emissao'] = data_match.group(1)
                    
                    # Extrai valor total
                    valor_match = re.search(r'VALOR TOTAL DA NOTA.*?([\d.,]+)', text, re.DOTALL)
                    if valor_match:
                        data['valor_total'] = valor_match.group(1)
                    
                    # Tenta extrair dados de produtos das tabelas
                    try:
                        tables = pdf.pages[0].extract_tables()
                        if tables:
                            for table in tables:
                                for row in table:
                                    if row and len(row) >= 3:
                                        # Verifica se a linha contém dados de produto
                                        if any(cell and str(cell).strip() for cell in row[:3]):
                                            data['codigo_item'] = str(row[0]).strip() if row[0] else ''
                                            data['descricao_produto'] = str(row[1]).strip() if len(row) > 1 and row[1] else ''
                                            
                                            # Procura por quantidade e valor nas colunas restantes
                                            for i, cell in enumerate(row[2:], 2):
                                                if cell and re.match(r'^\d+([.,]\d+)?$', str(cell).strip()):
                                                    if not data['quantidade']:
                                                        data['quantidade'] = str(cell).strip()
                                                    elif not data['valor_unitario']:
                                                        data['valor_unitario'] = str(cell).strip()
                                            break
                    except:
                        pass  # Ignora erros na extração de tabelas
                        
    except Exception as e:
        print(f'Erro ao processar {pdf_path}: {e}')
    
    return data

def main():
    """Função principal"""
    print("Iniciando processamento das notas fiscais...")
    
    # Configurações
    pdf_folder = r"C:\Users\Sony\Downloads\Relatório NFs\NFs"
    output_file = r"C:\Users\Sony\Downloads\Relatório NFs\relatorio_notas_fiscais.xlsx"
    
    # Lista todos os PDFs
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    print(f"Encontrados {len(pdf_files)} arquivos PDF")
    
    # Processa todos os PDFs
    all_data = []
    batch_size = 500  # Salva backup a cada 500 arquivos
    
    for i, pdf_file in enumerate(tqdm(pdf_files, desc="Processando PDFs")):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        nf_data = extract_nf_data(pdf_path)
        all_data.append(nf_data)
        
        # Salva backup periodicamente
        if (i + 1) % batch_size == 0:
            df_temp = pd.DataFrame(all_data)
            backup_file = f"backup_{i+1}_arquivos.xlsx"
            df_temp.to_excel(backup_file, index=False, engine='openpyxl')
            print(f"\nBackup salvo: {backup_file}")
    
    # Cria DataFrame final
    df = pd.DataFrame(all_data)
    
    # Define ordem das colunas
    columns_order = [
        'arquivo', 'numero_nf', 'natureza_operacao', 'destinatario', 
        'cnpj', 'data_emissao', 'codigo_item', 'descricao_produto', 
        'quantidade', 'valor_unitario', 'valor_total'
    ]
    df = df[columns_order]
    
    # Salva arquivo final
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    # Estatísticas
    print(f"\nRelatório salvo em: {output_file}")
    print(f"Total de notas processadas: {len(df)}")
    print(f"Notas com número extraído: {df['numero_nf'].notna().sum()}")
    print(f"Notas com destinatário extraído: {df['destinatario'].notna().sum()}")
    print(f"Notas com CNPJ extraído: {df['cnpj'].notna().sum()}")
    print(f"Notas com valor total extraído: {df['valor_total'].notna().sum()}")

if __name__ == "__main__":
    main()
