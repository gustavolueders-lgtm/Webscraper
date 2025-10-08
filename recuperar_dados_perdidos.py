#!/usr/bin/env python3
"""
Recupera todos os dados perdidos dos logs
Processa todo o arquivo de log para extrair estabelecimentos
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Set

def extract_establishment_from_log(line: str) -> Dict:
    """Extrai dados de estabelecimento de uma linha de log"""
    try:
        # Pattern for establishment data in logs: 🏪 ESTABLISHMENT_DATA: {python_dict}
        if '🏪 ESTABLISHMENT_DATA:' in line:
            # Extract data from log
            match = re.search(r'🏪 ESTABLISHMENT_DATA: (.+)', line)
            if match:
                data_str = match.group(1).strip()

                # Convert Python dict format to JSON format
                # Replace single quotes with double quotes, handle None values
                try:
                    # Replace None with null
                    data_str = data_str.replace('None', 'null')
                    # Replace True/False with true/false
                    data_str = data_str.replace('True', 'true').replace('False', 'false')
                    # Use ast.literal_eval to safely parse Python dict
                    import ast
                    data = ast.literal_eval(data_str.replace('null', 'None'))
                    return data
                except (ValueError, SyntaxError) as e:
                    # If ast fails, try manual conversion
                    try:
                        # Replace single quotes with double quotes for JSON
                        json_str = data_str.replace("'", '"')
                        data = json.loads(json_str)
                        return data
                    except json.JSONDecodeError:
                        print(f"❌ Erro ao fazer parse: {str(e)[:50]}...")
                        return None

    except Exception as e:
        print(f"❌ Erro ao extrair estabelecimento: {e}")

    return None

def is_duplicate(establishment: Dict, seen_place_ids: Set, existing_establishments: List) -> bool:
    """Verifica se é duplicado"""
    if not establishment:
        return True
        
    place_id = establishment.get('place_id')
    if place_id and place_id in seen_place_ids:
        return True
        
    # Check by name if no place_id
    name = establishment.get('name', '').strip().lower()
    if name:
        for existing in existing_establishments:
            existing_name = existing.get('name', '').strip().lower()
            if existing_name == name:
                return True
    
    return False

def recuperar_dados_perdidos():
    """Recupera todos os dados perdidos dos logs"""
    log_file = 'output/scrapy.log'
    output_file = 'output/fuel_stations_monitored.json'
    backup_file = 'output/fuel_stations_backup.json'
    
    print("🔍 Iniciando recuperação de dados perdidos...")
    print(f"📁 Processando: {log_file}")
    
    # Load existing data
    establishments = []
    seen_place_ids = set()
    
    try:
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                establishments = json.load(f)
            
            # Rebuild seen_place_ids
            for est in establishments:
                if 'place_id' in est and est['place_id']:
                    seen_place_ids.add(est['place_id'])
            
            print(f"📂 Dados existentes: {len(establishments)} estabelecimentos")
            
    except Exception as e:
        print(f"⚠️ Erro ao carregar dados existentes: {e}")
        establishments = []
    
    # Process log file
    if not os.path.exists(log_file):
        print(f"❌ Arquivo de log não encontrado: {log_file}")
        return
    
    print("📖 Processando arquivo de log...")
    
    new_establishments = 0
    total_processed = 0
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if '🏪 ESTABLISHMENT_DATA:' in line:
                    total_processed += 1
                    
                    establishment = extract_establishment_from_log(line)
                    if establishment and not is_duplicate(establishment, seen_place_ids, establishments):
                        establishments.append(establishment)
                        
                        # Add to seen set
                        place_id = establishment.get('place_id')
                        if place_id:
                            seen_place_ids.add(place_id)
                        
                        new_establishments += 1
                        
                        if new_establishments % 50 == 0:
                            print(f"✅ Recuperados {new_establishments} novos estabelecimentos...")
                
                # Progress indicator
                if line_num % 1000 == 0:
                    print(f"📄 Processadas {line_num} linhas...")
    
    except Exception as e:
        print(f"❌ Erro ao processar log: {e}")
        return
    
    print(f"\n📊 RESULTADO DA RECUPERAÇÃO:")
    print(f"   📖 Total de linhas processadas: {total_processed}")
    print(f"   ✅ Novos estabelecimentos recuperados: {new_establishments}")
    print(f"   💾 Total de estabelecimentos: {len(establishments)}")
    
    # Save data
    try:
        # Create backup
        if os.path.exists(output_file):
            import shutil
            shutil.copy2(output_file, backup_file)
            print(f"💾 Backup criado: {backup_file}")
        
        # Save main file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(establishments, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Dados salvos em: {output_file}")
        
        # Save summary
        summary = {
            'total_establishments': len(establishments),
            'new_establishments_recovered': new_establishments,
            'total_log_entries_processed': total_processed,
            'recovery_timestamp': datetime.now().isoformat(),
            'log_file': log_file,
            'output_file': output_file
        }
        
        summary_file = 'output/recovery_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Resumo salvo em: {summary_file}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
        return
    
    print("\n✅ RECUPERAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"🎯 Agora você tem {len(establishments)} estabelecimentos salvos")
    
    # Show some statistics
    establishments_with_phone = sum(1 for est in establishments if est.get('phone'))
    phone_percentage = (establishments_with_phone / len(establishments)) * 100 if establishments else 0
    
    print(f"\n📞 ESTATÍSTICAS:")
    print(f"   📞 Estabelecimentos com telefone: {establishments_with_phone} ({phone_percentage:.1f}%)")
    print(f"   🏪 Estabelecimentos sem telefone: {len(establishments) - establishments_with_phone}")
    
    # Show latest establishments
    print(f"\n🏪 ÚLTIMOS 5 ESTABELECIMENTOS RECUPERADOS:")
    for i, est in enumerate(establishments[-5:], 1):
        name = est.get('name', 'N/A')
        phone = est.get('phone', 'Sem telefone')
        rating = est.get('rating', 'N/A')
        print(f"   {i}. {name}")
        print(f"      📞 {phone}")
        print(f"      ⭐ {rating}")

if __name__ == "__main__":
    recuperar_dados_perdidos()
