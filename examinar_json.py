#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Examinar estrutura do JSON
"""

import json

def examinar_json():
    """Examina a estrutura do arquivo JSON"""
    
    # Carregar o JSON e examinar alguns registros
    with open('output/tire_shops_auto_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'Total de registros: {len(data)}')
    print()
    
    # Examinar primeiros 5 registros
    for i in range(min(5, len(data))):
        record = data[i]
        print(f'Registro {i+1}:')
        print(f'  Nome: {record.get("name")}')
        print(f'  Rating: {record.get("rating")}')
        print(f'  Reviews: {record.get("reviews_count")}')
        print(f'  Phone: {record.get("phone")}')
        print(f'  Address: {record.get("address")}')
        print(f'  Latitude: {record.get("cell_lat")}')
        print(f'  Longitude: {record.get("cell_lon")}')
        print()
    
    # Verificar quantos têm telefone
    com_telefone = sum(1 for r in data if r.get('phone'))
    print(f'Registros com telefone: {com_telefone}/{len(data)}')
    
    # Verificar padrões de telefone
    telefones = [r.get('phone') for r in data if r.get('phone')]
    print(f'\\nExemplos de telefones:')
    for i, tel in enumerate(telefones[:10]):
        print(f'  {tel}')

if __name__ == "__main__":
    examinar_json()
