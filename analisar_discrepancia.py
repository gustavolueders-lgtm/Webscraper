#!/usr/bin/env python3
"""
Analisa a discrepância entre logs e dados salvos
"""

import json
import re
import os

def analisar_discrepancia():
    print("🔍 ANÁLISE DA DISCREPÂNCIA ENTRE LOGS E JSON")
    print("=" * 60)
    
    # 1. Conta estabelecimentos nos logs
    try:
        if not os.path.exists('output/scrapy.log'):
            print("❌ Arquivo de log não encontrado!")
            return
        
        with open('output/scrapy.log', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procura por linhas com dados de estabelecimentos
        pattern = r'🏪 ESTABLISHMENT_DATA: ({.*?})'
        matches = re.findall(pattern, content)
        
        print(f"📄 LOGS:")
        print(f"   📊 {len(matches)} linhas de estabelecimentos encontradas")
        
        # 2. Tenta parsear cada linha
        establishments = []
        parse_errors = 0
        
        for i, match in enumerate(matches):
            try:
                # Converte aspas simples para duplas para JSON válido
                json_str = match.replace("'", '"').replace('None', 'null').replace('True', 'true').replace('False', 'false')
                data = json.loads(json_str)
                establishments.append(data)
            except json.JSONDecodeError as e:
                parse_errors += 1
                if parse_errors <= 3:  # Mostra apenas os primeiros 3 erros
                    print(f"   ⚠️ Erro de parsing na linha {i + 1}: {str(e)[:50]}...")
        
        print(f"   ✅ {len(establishments)} estabelecimentos parseados com sucesso")
        print(f"   ❌ {parse_errors} erros de parsing")
        
        # 3. Remove duplicatas baseado no place_id
        unique_establishments = {}
        duplicates_count = 0
        
        for est in establishments:
            place_id = est.get('place_id')
            if place_id:
                if place_id not in unique_establishments:
                    unique_establishments[place_id] = est
                else:
                    duplicates_count += 1
        
        final_establishments = list(unique_establishments.values())
        
        print(f"   🔄 {duplicates_count} duplicatas removidas")
        print(f"   🎯 {len(final_establishments)} estabelecimentos únicos")
        
        # 4. Compara com JSON salvo
        try:
            if os.path.exists('output/fuel_stations_monitored.json'):
                with open('output/fuel_stations_monitored.json', 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                print(f"\n💾 JSON SALVO:")
                print(f"   📊 {len(saved_data)} estabelecimentos salvos")
                
                # Verifica se os dados batem
                if len(saved_data) == len(final_establishments):
                    print(f"   ✅ Dados batem perfeitamente!")
                else:
                    print(f"   ⚠️ Diferença de {abs(len(saved_data) - len(final_establishments))} estabelecimentos")
                    
                    # Analisa place_ids
                    saved_place_ids = set(est.get('place_id') for est in saved_data if est.get('place_id'))
                    log_place_ids = set(est.get('place_id') for est in final_establishments if est.get('place_id'))
                    
                    only_in_saved = saved_place_ids - log_place_ids
                    only_in_logs = log_place_ids - saved_place_ids
                    
                    if only_in_saved:
                        print(f"   📝 {len(only_in_saved)} place_ids apenas no JSON salvo")
                    if only_in_logs:
                        print(f"   📄 {len(only_in_logs)} place_ids apenas nos logs")
            else:
                print(f"\n💾 JSON SALVO: Arquivo não encontrado")
                
        except Exception as e:
            print(f"\n💾 JSON SALVO: Erro ao ler - {e}")
        
        # 5. Resumo da análise
        print(f"\n" + "=" * 60)
        print(f"📋 RESUMO DA ANÁLISE:")
        print(f"   📄 Linhas nos logs: {len(matches)}")
        print(f"   ✅ Parseadas com sucesso: {len(establishments)}")
        print(f"   ❌ Erros de parsing: {parse_errors}")
        print(f"   🔄 Duplicatas removidas: {duplicates_count}")
        print(f"   🎯 Estabelecimentos únicos: {len(final_establishments)}")
        
        # 6. Explicação
        print(f"\n💡 EXPLICAÇÃO DA DISCREPÂNCIA:")
        if parse_errors > 0:
            print(f"   • {parse_errors} linhas não puderam ser parseadas (JSON malformado)")
        if duplicates_count > 0:
            print(f"   • {duplicates_count} duplicatas foram removidas (mesmo place_id)")
        print(f"   • Estabelecimentos podem aparecer em múltiplas células geográficas")
        print(f"   • O sistema remove duplicatas para evitar dados repetidos")
        
        # 7. Mostra alguns exemplos de duplicatas
        if duplicates_count > 0:
            print(f"\n🔍 EXEMPLOS DE DUPLICATAS ENCONTRADAS:")
            place_id_counts = {}
            for est in establishments:
                place_id = est.get('place_id')
                if place_id:
                    place_id_counts[place_id] = place_id_counts.get(place_id, 0) + 1
            
            duplicated_places = {pid: count for pid, count in place_id_counts.items() if count > 1}
            
            for i, (place_id, count) in enumerate(list(duplicated_places.items())[:3]):
                # Encontra o estabelecimento
                for est in establishments:
                    if est.get('place_id') == place_id:
                        name = est.get('name', 'N/A')
                        print(f"   {i+1}. {name} (place_id: {place_id}) - {count} vezes")
                        break
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")

if __name__ == "__main__":
    analisar_discrepancia()
