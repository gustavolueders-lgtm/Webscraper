#!/usr/bin/env python3
"""
Recupera TODOS os dados dos logs - versão agressiva
Ignora duplicatas por place_id e foca em dados únicos por nome+telefone
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
                try:
                    # Use ast.literal_eval to safely parse Python dict
                    import ast
                    data = ast.literal_eval(data_str.replace('null', 'None'))
                    return data
                except (ValueError, SyntaxError) as e:
                    # If ast fails, try manual conversion
                    try:
                        # Replace single quotes with double quotes for JSON
                        json_str = data_str.replace("'", '"').replace('None', 'null').replace('True', 'true').replace('False', 'false')
                        data = json.loads(json_str)
                        return data
                    except json.JSONDecodeError:
                        return None
                
    except Exception as e:
        print(f"❌ Erro ao extrair estabelecimento: {e}")
    
    return None

def create_unique_key(establishment: Dict) -> str:
    """Cria chave única baseada em nome + telefone + endereço"""
    name = str(establishment.get('name', '')).strip().lower()
    phone = str(establishment.get('phone', '') or '').strip()
    address = str(establishment.get('address', '')).strip().lower()

    # Remove common words from address for better matching
    address_clean = address.replace('brasil', '').replace('santa catarina', '').replace('lat:', '').replace('lon:', '').strip()

    return f"{name}|{phone}|{address_clean[:50]}"

def recuperar_todos_dados():
    """Recupera TODOS os dados dos logs - versão agressiva"""
    log_file = 'output/scrapy.log'
    output_file = 'output/fuel_stations_complete.json'
    backup_file = 'output/fuel_stations_complete_backup.json'
    
    print("🔍 RECUPERAÇÃO AGRESSIVA - Todos os dados dos logs")
    print(f"📁 Processando: {log_file}")
    
    # Process log file
    if not os.path.exists(log_file):
        print(f"❌ Arquivo de log não encontrado: {log_file}")
        return
    
    print("📖 Processando arquivo de log...")
    
    establishments = []
    seen_keys = set()
    total_processed = 0
    duplicates_skipped = 0
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if '🏪 ESTABLISHMENT_DATA:' in line:
                    total_processed += 1
                    
                    establishment = extract_establishment_from_log(line)
                    if establishment:
                        # Create unique key
                        unique_key = create_unique_key(establishment)
                        
                        if unique_key not in seen_keys:
                            establishments.append(establishment)
                            seen_keys.add(unique_key)
                            
                            if len(establishments) % 100 == 0:
                                print(f"✅ Coletados {len(establishments)} estabelecimentos únicos...")
                        else:
                            duplicates_skipped += 1
                
                # Progress indicator
                if line_num % 1000 == 0:
                    print(f"📄 Processadas {line_num} linhas...")
    
    except Exception as e:
        print(f"❌ Erro ao processar log: {e}")
        return
    
    print(f"\n📊 RESULTADO DA RECUPERAÇÃO AGRESSIVA:")
    print(f"   📖 Total de linhas processadas: {total_processed}")
    print(f"   ✅ Estabelecimentos únicos coletados: {len(establishments)}")
    print(f"   🔄 Duplicatas ignoradas: {duplicates_skipped}")
    print(f"   📈 Taxa de aproveitamento: {(len(establishments)/total_processed*100):.1f}%")
    
    # Save data
    try:
        # Create backup if file exists
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
            'total_log_entries_processed': total_processed,
            'duplicates_skipped': duplicates_skipped,
            'recovery_timestamp': datetime.now().isoformat(),
            'log_file': log_file,
            'output_file': output_file,
            'method': 'aggressive_recovery'
        }
        
        summary_file = 'output/complete_recovery_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Resumo salvo em: {summary_file}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
        return
    
    print("\n✅ RECUPERAÇÃO AGRESSIVA CONCLUÍDA!")
    print(f"🎯 Total de estabelecimentos únicos: {len(establishments)}")
    
    # Show some statistics
    establishments_with_phone = sum(1 for est in establishments if est.get('phone'))
    phone_percentage = (establishments_with_phone / len(establishments)) * 100 if establishments else 0
    
    print(f"\n📞 ESTATÍSTICAS FINAIS:")
    print(f"   📞 Estabelecimentos com telefone: {establishments_with_phone} ({phone_percentage:.1f}%)")
    print(f"   🏪 Estabelecimentos sem telefone: {len(establishments) - establishments_with_phone}")
    
    # Show latest establishments
    print(f"\n🏪 ÚLTIMOS 5 ESTABELECIMENTOS COLETADOS:")
    for i, est in enumerate(establishments[-5:], 1):
        name = est.get('name', 'N/A')
        phone = est.get('phone', 'Sem telefone')
        rating = est.get('rating', 'N/A')
        cell_index = est.get('cell_index', 'N/A')
        print(f"   {i}. {name}")
        print(f"      📞 {phone}")
        print(f"      ⭐ {rating}")
        print(f"      🗺️ Célula {cell_index}")

if __name__ == "__main__":
    recuperar_todos_dados()
