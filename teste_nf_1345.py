#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para a NF 1345-2.pdf
"""

import pdfplumber
import pandas as pd
import os
import re
from tqdm import tqdm

def extract_nf_basic_data(text):
    """Extrai dados básicos da nota fiscal"""
    data = {
        'numero_nf': '',
        'natureza_operacao': '',
        'destinatario': '',
        'cnpj_destinatario': '',
        'data_emissao': ''
    }
    
    # Extrai número da NF
    nf_match = re.search(r'Nº\s*(\d{3}\.\d{3}\.\d{3})', text)
    if nf_match:
        data['numero_nf'] = nf_match.group(1)
    
    # Extrai natureza da operação - melhorado
    # Procura por linha que vem após "NATUREZA DA OPERAÇÃO" e contém palavras-chave
    natureza_patterns = [
        r'NATUREZA DA OPERAÇÃO\s*\n([^\n]+)',
        r'NATUREZA DA OPERAÇÃO.*?\n([A-Z][^\n]*(?:VENDA|REMESSA|INDUSTRIALIZ|CONSERTO|DEVOLUÇÃO)[^\n]*)',
        r'(VENDA DE MERCADORIA INDUSTRIALIZADA)',
        r'(REMESSA PARA [^\n]+)',
        r'(DEVOLUÇÃO [^\n]+)'
    ]
    
    for pattern in natureza_patterns:
        natureza_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if natureza_match:
            natureza = natureza_match.group(1).strip()
            # Remove números e códigos do início e fim
            natureza = re.sub(r'^\d+\s*-?\s*', '', natureza)
            # Remove códigos de protocolo no final (números longos)
            natureza = re.sub(r'\s+\d{12,}.*$', '', natureza)
            if len(natureza) > 5:  # Só aceita se tiver conteúdo significativo
                data['natureza_operacao'] = natureza
                break
    
    # Extrai destinatário e CNPJ do destinatário - melhorado
    # Padrão 1: Nome e CNPJ na mesma linha (mais específico)
    dest_pattern1 = r'([A-Z][A-Z\s&\.\-]{10,}?)\s+(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})\s+\d{2}/\d{2}/\d{4}'
    dest_match1 = re.search(dest_pattern1, text)
    if dest_match1:
        nome = dest_match1.group(1).strip()
        # Remove palavras de controle que podem aparecer no início
        nome = re.sub(r'^(NOME/RAZÃO SOCIAL|DESTINATÁRIO|O\s+)', '', nome).strip()
        data['destinatario'] = nome
        data['cnpj_destinatario'] = dest_match1.group(2)
    else:
        # Padrão 2: Procura na seção DESTINATÁRIO/REMETENTE
        dest_section = re.search(r'DESTINATÁRIO/REMETENTE.*?(?:FATURA|CÁLCULO)', text, re.DOTALL)
        if dest_section:
            section_text = dest_section.group(0)
            
            # Procura nome do destinatário
            nome_patterns = [
                r'NOME/RAZÃO SOCIAL\s*\n([^\n]+)',
                r'([A-Z][A-Z\s&\.\-]{5,})\s+\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
            ]
            
            for pattern in nome_patterns:
                nome_match = re.search(pattern, section_text)
                if nome_match:
                    nome = nome_match.group(1).strip()
                    # Remove CNPJ se estiver junto
                    nome = re.sub(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', '', nome).strip()
                    # Remove prefixos
                    nome = re.sub(r'^(NOME/RAZÃO SOCIAL|O\s+)', '', nome).strip()
                    if len(nome) > 5:
                        data['destinatario'] = nome
                        break
            
            # Procura CNPJ do destinatário (não do emitente)
            cnpj_patterns = [
                r'CNPJ/CPF\s*\n.*?(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
                r'([A-Z\s&\.\-]+)\s+(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})\s+\d{2}/\d{2}/\d{4}'
            ]
            
            for pattern in cnpj_patterns:
                cnpj_match = re.search(pattern, section_text, re.DOTALL)
                if cnpj_match:
                    if len(cnpj_match.groups()) == 2:
                        data['cnpj_destinatario'] = cnpj_match.group(2)
                    else:
                        data['cnpj_destinatario'] = cnpj_match.group(1)
                    break
    
    # Extrai data de emissão
    data_patterns = [
        r'DATA DA EMISSÃO.*?\n.*?(\d{2}/\d{2}/\d{4})',
        r'(\d{2}/\d{2}/\d{4})'
    ]
    
    for pattern in data_patterns:
        data_match = re.search(pattern, text, re.DOTALL)
        if data_match:
            data['data_emissao'] = data_match.group(1)
            break
    
    return data

def extract_products_from_tables(tables):
    """Extrai produtos das tabelas da nota fiscal"""
    products = []
    
    for table in tables:
        if not table or len(table) < 2:
            continue
            
        # Procura pela tabela de produtos (tem cabeçalho com CÓDIGO, DESCRIÇÃO, etc.)
        header_row = None
        for i, row in enumerate(table):
            if row and any(cell and 'CÓDIGO' in str(cell).upper() for cell in row):
                header_row = i
                break
        
        if header_row is None:
            continue
            
        # Processa as linhas de produtos após o cabeçalho
        for row in table[header_row + 1:]:
            if not row or len(row) < 6:
                continue
                
            # Verifica se é uma linha de produto válida (tem código)
            codigo_cell = str(row[0]).strip() if row[0] else ''
            if not codigo_cell:
                continue
            
            # Extrai dados das células (podem ter múltiplos valores separados por \n)
            codigos = [c.strip() for c in codigo_cell.split('\n') if c.strip()]
            descricoes = []
            quantidades = []
            valores_unit = []
            valores_total = []
            
            # Descrição (coluna 1)
            if len(row) > 1 and row[1]:
                descricoes = [d.strip() for d in str(row[1]).split('\n') if d.strip()]
            
            # Quantidade (coluna 6)
            if len(row) > 6 and row[6]:
                qtd_text = str(row[6]).strip()
                quantidades = [q.strip().replace(',', '.') for q in qtd_text.split('\n') if q.strip()]
            
            # Valor unitário (coluna 7)
            if len(row) > 7 and row[7]:
                unit_text = str(row[7]).strip()
                valores_unit = [v.strip().replace(',', '.') for v in unit_text.split('\n') if v.strip()]
            
            # Valor total (coluna 8)
            if len(row) > 8 and row[8]:
                total_text = str(row[8]).strip()
                valores_total = [v.strip().replace(',', '.') for v in total_text.split('\n') if v.strip()]
            
            # Cria um produto para cada código (linha separada)
            max_items = max(len(codigos), len(descricoes), len(quantidades), len(valores_unit), len(valores_total))
            
            for i in range(max_items):
                # Verifica se o código é válido (numérico ou alfanumérico)
                codigo = codigos[i] if i < len(codigos) else ''
                if not codigo or not re.match(r'^[A-Z0-9]+', codigo):
                    continue
                
                product = {
                    'codigo_item': codigo,
                    'descricao_produto': descricoes[i] if i < len(descricoes) else '',
                    'quantidade': quantidades[i] if i < len(quantidades) and re.match(r'^\d+([.,]\d+)?$', quantidades[i]) else '',
                    'valor_unitario': valores_unit[i] if i < len(valores_unit) and re.match(r'^\d+([.,]\d+)?$', valores_unit[i]) else '',
                    'valor_total': valores_total[i] if i < len(valores_total) and re.match(r'^\d+([.,]\d+)?$', valores_total[i]) else ''
                }
                
                products.append(product)
    
    return products

def extract_nf_data(pdf_path):
    """Extrai dados completos de uma nota fiscal"""
    all_rows = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                page = pdf.pages[0]
                text = page.extract_text()
                
                if not text:
                    return all_rows
                
                # Extrai dados básicos da NF
                basic_data = extract_nf_basic_data(text)
                
                # Extrai produtos das tabelas
                tables = page.extract_tables()
                products = extract_products_from_tables(tables)
                
                # Se não encontrou produtos, cria uma linha com dados básicos
                if not products:
                    row = {
                        'arquivo': os.path.basename(pdf_path),
                        **basic_data,
                        'codigo_item': '',
                        'descricao_produto': '',
                        'quantidade': '',
                        'valor_unitario': '',
                        'valor_total': ''
                    }
                    all_rows.append(row)
                else:
                    # Cria uma linha para cada produto
                    for product in products:
                        row = {
                            'arquivo': os.path.basename(pdf_path),
                            **basic_data,
                            **product
                        }
                        all_rows.append(row)
                        
    except Exception as e:
        print(f'Erro ao processar {pdf_path}: {e}')
        # Cria linha com erro
        row = {
            'arquivo': os.path.basename(pdf_path),
            'numero_nf': f'ERRO: {e}',
            'natureza_operacao': '',
            'destinatario': '',
            'cnpj_destinatario': '',
            'data_emissao': '',
            'codigo_item': '',
            'descricao_produto': '',
            'quantidade': '',
            'valor_unitario': '',
            'valor_total': ''
        }
        all_rows.append(row)
    
    return all_rows

def main():
    """Teste específico da NF 1345"""
    print("Testando especificamente a NF 1345-2.pdf...")
    
    # Configurações
    pdf_path = r"C:\Users\Sony\Downloads\Relatório NFs\NFs\1345-2.pdf"
    output_file = r"C:\Users\Sony\Downloads\Relatório NFs\teste_nf_1345.xlsx"
    
    # Processa a NF
    nf_rows = extract_nf_data(pdf_path)
    
    # Cria DataFrame final
    df = pd.DataFrame(nf_rows)
    
    # Define ordem das colunas
    columns_order = [
        'arquivo', 'numero_nf', 'natureza_operacao', 'destinatario', 
        'cnpj_destinatario', 'data_emissao', 'codigo_item', 'descricao_produto', 
        'quantidade', 'valor_unitario', 'valor_total'
    ]
    
    # Renomeia coluna para manter compatibilidade
    df = df.rename(columns={'cnpj_destinatario': 'cnpj'})
    columns_order[4] = 'cnpj'
    
    df = df[columns_order]
    
    # Salva arquivo de teste
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    # Mostra resultados
    print(f"\nTeste salvo em: {output_file}")
    print(f"Total de linhas extraídas: {len(df)}")
    print()
    print("=== RESULTADOS ===")
    for i, row in df.iterrows():
        print(f"LINHA {i+1}:")
        print(f"  Código: {row['codigo_item']}")
        print(f"  Produto: {row['descricao_produto']}")
        print(f"  Qtd: {row['quantidade']} | Unit: {row['valor_unitario']} | Total: {row['valor_total']}")
        print()

if __name__ == "__main__":
    main()
