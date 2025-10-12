#!/usr/bin/env python3
"""
Processa TODOS os dados dos logs e gera Excel completo
"""

import ast
import json
import pandas as pd
import re
from datetime import datetime

def extract_city_from_address(address):
    """Extrai cidade do endereço"""
    if not address:
        return ""
    
    # Padrões comuns: "Cidade - SC" ou "Cidade, SC"
    patterns = [
        r',\s*([^,\-]+)\s*-\s*SC',  # ", Cidade - SC"
        r'-\s*([^,\-]+)\s*-\s*SC',  # "- Cidade - SC"
        r',\s*([^,\-]+)\s*,\s*SC',  # ", Cidade, SC"
        r'-\s*([^,\-]+)\s*,\s*SC',  # "- Cidade, SC"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, address)
        if match:
            return match.group(1).strip()
    
    # Se não encontrar padrão, tentar pegar última parte antes de SC
    if 'SC' in address:
        parts = address.split('-')
        for part in reversed(parts):
            if 'SC' not in part and part.strip():
                return part.strip()
    
    return ""

def extract_ddd_from_phone(phone):
    """Extrai DDD do telefone"""
    if not phone:
        return ""
    
    # Procurar por padrões (XX) ou XX
    match = re.search(r'\(?(\d{2})\)?', phone)
    if match:
        return match.group(1)
    
    return ""

def clean_phone(phone):
    """Limpa e formata telefone"""
    if not phone:
        return ""
    
    # Remove caracteres especiais, mantém apenas números
    clean = re.sub(r'[^\d]', '', phone)
    
    # Formatar se tiver 10 ou 11 dígitos
    if len(clean) == 10:
        return f"({clean[:2]}) {clean[2:6]}-{clean[6:]}"
    elif len(clean) == 11:
        return f"({clean[:2]}) {clean[2:7]}-{clean[7:]}"
    
    return phone

def create_unique_key(item):
    """Cria chave única para deduplicação"""
    if not item or not isinstance(item, dict):
        return f"invalid_{hash(str(item)) % 10000}"
    
    name = str(item.get('name', '')).strip().lower()
    phone = str(item.get('phone', '')).strip()

    if phone and phone != 'none':
        return f"{name}|{phone}"
    else:
        address = str(item.get('address', '')).strip().lower()
        address_words = address.split()[:3]
        address_key = ' '.join(address_words) if address_words else ''
        return f"{name}|{address_key}"

def process_all_logs():
    """Processa TODOS os dados dos logs"""
    print("🔧 PROCESSANDO TODOS OS LOGS")
    print("=" * 50)
    
    unique_establishments = {}
    unique_keys = set()
    processed_lines = 0
    errors = 0
    duplicates_blocked = 0
    
    try:
        with open('output/scrapy.log', 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if 'TIRE_SHOP_DATA:' in line:
                    try:
                        # Extrair dados do log
                        data_start = line.find('{')
                        if data_start == -1:
                            continue
                        
                        data_str = line[data_start:]
                        if not data_str or data_str.strip() == '':
                            continue
                        
                        data_str = data_str.strip()
                        
                        # Converter string Python para dict
                        establishment_data = ast.literal_eval(data_str)
                        
                        # Criar chave única para deduplicação
                        key = create_unique_key(establishment_data)
                        
                        # Verificar duplicata
                        if key in unique_keys:
                            duplicates_blocked += 1
                            continue
                        
                        # Adicionar novo estabelecimento
                        unique_keys.add(key)
                        unique_establishments[key] = establishment_data
                        processed_lines += 1
                        
                        if processed_lines % 1000 == 0:
                            print(f"   📊 Processadas: {processed_lines:,} | Duplicatas: {duplicates_blocked:,}")
                        
                    except Exception as e:
                        errors += 1
                        continue
    
    except Exception as e:
        print(f"❌ Erro ao ler logs: {e}")
        return
    
    print(f"\n📊 PROCESSAMENTO COMPLETO:")
    print(f"   ✅ Borracharias únicas: {len(unique_establishments):,}")
    print(f"   🚫 Duplicatas bloqueadas: {duplicates_blocked:,}")
    print(f"   ❌ Erros: {errors:,}")
    
    # Processar dados para Excel
    processed_data = []
    
    for shop in unique_establishments.values():
        try:
            address = shop.get('address', '')
            phone = shop.get('phone', '')
            
            processed_shop = {
                'nome': shop.get('name', ''),
                'cidade': extract_city_from_address(address),
                'endereco': address,
                'telefone': clean_phone(phone),
                'ddd': extract_ddd_from_phone(phone),
                'link': shop.get('link', ''),
                'avaliacao': shop.get('rating', ''),
                'num_avaliacoes': shop.get('reviews_count', ''),
                'categoria': shop.get('category', ''),
                'website': shop.get('website', ''),
                'horario': shop.get('hours', ''),
                'place_id': shop.get('place_id', ''),
                'latitude': shop.get('cell_lat', ''),
                'longitude': shop.get('cell_lon', ''),
                'termo_busca': shop.get('search_term', ''),
                'celula_grid': shop.get('cell_index', ''),
                'data_coleta': shop.get('scraped_at', ''),
                'fonte': shop.get('source', '')
            }
            
            processed_data.append(processed_shop)
            
        except Exception as e:
            continue
    
    # Criar DataFrame
    df = pd.DataFrame(processed_data)
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   📝 Total de registros: {len(df):,}")
    print(f"   📞 Com telefone: {len(df[df['telefone'] != '']):,}")
    print(f"   🏪 Com website: {len(df[df['website'] != '']):,}")
    print(f"   🌐 Com link Google: {len(df[df['link'] != '']):,}")
    print(f"   🏙️ Cidades únicas: {df['cidade'].nunique():,}")
    
    # Mostrar cidades mais comuns
    print(f"\n🏙️ TOP 15 CIDADES:")
    top_cities = df['cidade'].value_counts().head(15)
    for city, count in top_cities.items():
        if city:
            print(f"   {city}: {count:,} borracharias")
    
    # Gerar arquivo Excel COMPLETO
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f"output/borracharias_santa_catarina_COMPLETO_{timestamp}.xlsx"
    
    try:
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Aba principal
            df.to_excel(writer, sheet_name='Borracharias', index=False)
            
            # Aba de estatísticas
            stats_data = {
                'Métrica': [
                    'Total de Borracharias',
                    'Com Telefone',
                    'Com Website',
                    'Com Link Google Maps',
                    'Cidades Únicas',
                    'Duplicatas Removidas',
                    'Data de Geração'
                ],
                'Valor': [
                    len(df),
                    len(df[df['telefone'] != '']),
                    len(df[df['website'] != '']),
                    len(df[df['link'] != '']),
                    df['cidade'].nunique(),
                    duplicates_blocked,
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
            
            # Aba de cidades
            cities_df = df['cidade'].value_counts().reset_index()
            cities_df.columns = ['Cidade', 'Quantidade']
            cities_df.to_excel(writer, sheet_name='Por Cidade', index=False)
        
        print(f"\n✅ EXCEL COMPLETO GERADO!")
        print(f"📁 Arquivo: {excel_file}")
        print(f"📊 {len(df):,} borracharias exportadas")
        
        return excel_file
        
    except Exception as e:
        print(f"❌ Erro ao gerar Excel: {e}")
        return None

if __name__ == "__main__":
    process_all_logs()
