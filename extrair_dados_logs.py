#!/usr/bin/env python3
"""
Extrai dados dos logs e salva no JSON
"""

import json
import re
import os
from datetime import datetime

def extrair_dados_dos_logs():
    """Extrai dados dos logs e salva no JSON"""
    
    print("🔍 EXTRAINDO DADOS DOS LOGS")
    print("=" * 50)
    
    establishments = []
    
    try:
        if not os.path.exists('output/scrapy.log'):
            print("❌ Arquivo de log não encontrado!")
            return
        
        with open('output/scrapy.log', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procura por linhas com dados de estabelecimentos
        pattern = r'🏪 ESTABLISHMENT_DATA: ({.*?})'
        matches = re.findall(pattern, content)
        
        print(f"📊 Encontradas {len(matches)} linhas de dados")
        
        for i, match in enumerate(matches):
            try:
                # Converte aspas simples para duplas para JSON válido
                json_str = match.replace("'", '"').replace('None', 'null').replace('True', 'true').replace('False', 'false')
                # Converte string JSON para dict
                data = json.loads(json_str)
                establishments.append(data)
                
                if (i + 1) % 50 == 0:
                    print(f"   ✅ Processados {i + 1} estabelecimentos")
                    
            except json.JSONDecodeError as e:
                print(f"   ⚠️ Erro ao processar linha {i + 1}: {e}")
                continue
        
        # Remove duplicatas baseado no place_id
        unique_establishments = {}
        for est in establishments:
            place_id = est.get('place_id')
            if place_id and place_id not in unique_establishments:
                unique_establishments[place_id] = est
        
        final_establishments = list(unique_establishments.values())
        
        # Salva no arquivo JSON
        os.makedirs('output', exist_ok=True)
        
        with open('output/fuel_stations_monitored.json', 'w', encoding='utf-8') as f:
            json.dump(final_establishments, f, ensure_ascii=False, indent=2)
        
        print(f"✅ DADOS EXTRAÍDOS COM SUCESSO!")
        print(f"📊 Total de estabelecimentos únicos: {len(final_establishments)}")
        print(f"💾 Salvos em: output/fuel_stations_monitored.json")
        
        # Estatísticas
        phones_count = sum(1 for est in final_establishments if est.get('phone'))
        ratings_count = sum(1 for est in final_establishments if est.get('rating'))
        
        print(f"📞 Estabelecimentos com telefone: {phones_count} ({phones_count/len(final_establishments)*100:.1f}%)")
        print(f"⭐ Estabelecimentos com avaliação: {ratings_count} ({ratings_count/len(final_establishments)*100:.1f}%)")
        
        # Mostra alguns exemplos
        print(f"\n🏪 EXEMPLOS DE DADOS COLETADOS:")
        for i, est in enumerate(final_establishments[:5]):
            name = est.get('name', 'N/A')
            phone = est.get('phone', 'Sem telefone')
            rating = est.get('rating', 'N/A')
            print(f"   {i+1}. {name}")
            print(f"      📞 {phone}")
            print(f"      ⭐ {rating}")
        
        return final_establishments
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    establishments = extrair_dados_dos_logs()
    
    if establishments:
        print(f"\n🎉 SUCESSO! {len(establishments)} estabelecimentos extraídos e salvos!")
    else:
        print(f"\n❌ Nenhum dado foi extraído.")

if __name__ == "__main__":
    main()
