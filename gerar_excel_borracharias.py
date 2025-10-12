#!/usr/bin/env python3
"""
Gera arquivo Excel com dados das borracharias coletadas
"""

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

def process_tire_shops():
    """Processa dados das borracharias e gera Excel"""
    print("🔧 GERANDO EXCEL DAS BORRACHARIAS")
    print("=" * 50)
    
    # Carregar dados
    try:
        with open('output/tire_shops_auto_complete.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Dados carregados: {len(data)} registros")
        
        # Verificar se é lista ou dicionário
        if isinstance(data, dict):
            tire_shops = list(data.values())
        else:
            tire_shops = data
            
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    # Processar dados
    processed_data = []
    
    for shop in tire_shops:
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
            print(f"⚠️ Erro ao processar registro: {e}")
            continue
    
    # Criar DataFrame
    df = pd.DataFrame(processed_data)
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   📝 Total de registros: {len(df):,}")
    print(f"   📞 Com telefone: {len(df[df['telefone'] != '']):,}")
    print(f"   🏪 Com website: {len(df[df['website'] != '']):,}")
    print(f"   🌐 Com link Google: {len(df[df['link'] != '']):,}")
    print(f"   🏙️ Cidades únicas: {df['cidade'].nunique():,}")
    
    # Mostrar cidades mais comuns
    print(f"\n🏙️ CIDADES MAIS COMUNS:")
    top_cities = df['cidade'].value_counts().head(10)
    for city, count in top_cities.items():
        if city:
            print(f"   {city}: {count:,} borracharias")
    
    # Gerar arquivo Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f"output/borracharias_santa_catarina_{timestamp}.xlsx"
    
    try:
        # Criar Excel com formatação
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
                    'Data de Geração'
                ],
                'Valor': [
                    len(df),
                    len(df[df['telefone'] != '']),
                    len(df[df['website'] != '']),
                    len(df[df['link'] != '']),
                    df['cidade'].nunique(),
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
            
            # Aba de cidades
            cities_df = df['cidade'].value_counts().reset_index()
            cities_df.columns = ['Cidade', 'Quantidade']
            cities_df.to_excel(writer, sheet_name='Por Cidade', index=False)
        
        print(f"\n✅ EXCEL GERADO COM SUCESSO!")
        print(f"📁 Arquivo: {excel_file}")
        print(f"📊 {len(df):,} borracharias exportadas")
        
        return excel_file
        
    except Exception as e:
        print(f"❌ Erro ao gerar Excel: {e}")
        return None

if __name__ == "__main__":
    process_tire_shops()
