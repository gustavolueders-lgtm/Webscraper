#!/usr/bin/env python3
"""
Sistema de Salvamento Automático e Contínuo
Monitora logs em tempo real e salva dados automaticamente
"""

import json
import os
import re
import time
import threading
from datetime import datetime
from typing import Dict, List, Set
import signal
import sys

class SalvamentoAutomatico:
    def __init__(self):
        self.log_file = 'output/scrapy.log'
        self.output_file = 'output/fuel_stations_monitored.json'
        self.backup_file = 'output/fuel_stations_backup.json'
        self.progress_file = 'output/monitoring_progress.json'
        
        # Data storage
        self.establishments = []
        self.seen_place_ids = set()
        self.last_position = 0
        self.running = True
        self.lock = threading.Lock()
        
        # Stats
        self.stats = {
            'total_found': 0,
            'total_saved': 0,
            'last_update': None,
            'started_at': datetime.now().isoformat(),
            'auto_saves': 0
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Load existing data
        self._load_existing_data()
        
        print("🚀 Sistema de Salvamento Automático iniciado!")
        print(f"📁 Monitorando: {self.log_file}")
        print(f"💾 Salvando em: {self.output_file}")
        print(f"📊 Dados existentes: {len(self.establishments)} estabelecimentos")

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n🛑 Recebido sinal {signum}. Salvando dados finais...")
        self.running = False
        self._save_data()
        print("💾 Dados salvos com sucesso!")
        sys.exit(0)

    def _load_existing_data(self):
        """Carrega dados existentes"""
        try:
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    self.establishments = json.load(f)
                
                # Rebuild seen_place_ids
                for est in self.establishments:
                    if 'place_id' in est and est['place_id']:
                        self.seen_place_ids.add(est['place_id'])
                
                self.stats['total_saved'] = len(self.establishments)
                print(f"📂 Carregados {len(self.establishments)} estabelecimentos existentes")
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados existentes: {e}")
            self.establishments = []

    def _extract_establishment_from_log(self, line: str) -> Dict:
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

    def _parse_establishment_manually(self, data_str: str) -> Dict:
        """Parse establishment data manually from string"""
        try:
            data = {}
            
            # Extract name
            name_match = re.search(r'["\']?name["\']?\s*:\s*["\']([^"\']+)["\']', data_str)
            if name_match:
                data['name'] = name_match.group(1)
            
            # Extract phone
            phone_match = re.search(r'["\']?phone["\']?\s*:\s*["\']([^"\']+)["\']', data_str)
            if phone_match:
                data['phone'] = phone_match.group(1)
            
            # Extract rating
            rating_match = re.search(r'["\']?rating["\']?\s*:\s*([0-9.]+)', data_str)
            if rating_match:
                data['rating'] = float(rating_match.group(1))
            
            # Extract place_id
            place_id_match = re.search(r'["\']?place_id["\']?\s*:\s*["\']([^"\']+)["\']', data_str)
            if place_id_match:
                data['place_id'] = place_id_match.group(1)
            
            # Extract address
            address_match = re.search(r'["\']?address["\']?\s*:\s*["\']([^"\']+)["\']', data_str)
            if address_match:
                data['address'] = address_match.group(1)
            
            # Add timestamp
            data['extracted_at'] = datetime.now().isoformat()
            
            return data if data else None
            
        except Exception as e:
            print(f"❌ Erro no parse manual: {e}")
            return None

    def _is_duplicate(self, establishment: Dict) -> bool:
        """Verifica se é duplicado"""
        if not establishment:
            return True
            
        place_id = establishment.get('place_id')
        if place_id and place_id in self.seen_place_ids:
            return True
            
        # Check by name if no place_id
        name = establishment.get('name', '').strip().lower()
        if name:
            for existing in self.establishments:
                existing_name = existing.get('name', '').strip().lower()
                if existing_name == name:
                    return True
        
        return False

    def _add_establishment(self, establishment: Dict):
        """Adiciona estabelecimento se não for duplicado"""
        if self._is_duplicate(establishment):
            return False
            
        with self.lock:
            self.establishments.append(establishment)
            
            # Add to seen set
            place_id = establishment.get('place_id')
            if place_id:
                self.seen_place_ids.add(place_id)
            
            self.stats['total_saved'] = len(self.establishments)
            self.stats['last_update'] = datetime.now().isoformat()
            
            # Auto-save every 5 new establishments
            if len(self.establishments) % 5 == 0:
                self._save_data()
                self.stats['auto_saves'] += 1
                print(f"💾 AUTO-SAVE: {len(self.establishments)} estabelecimentos salvos")
            
            return True

    def _save_data(self):
        """Salva dados com backup"""
        try:
            with self.lock:
                # Create backup
                if os.path.exists(self.output_file):
                    import shutil
                    shutil.copy2(self.output_file, self.backup_file)
                
                # Save main file
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.establishments, f, ensure_ascii=False, indent=2)
                
                # Save progress
                with open(self.progress_file, 'w', encoding='utf-8') as f:
                    json.dump(self.stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

    def _monitor_logs(self):
        """Monitora logs continuamente"""
        print("👀 Iniciando monitoramento de logs...")
        
        while self.running:
            try:
                if not os.path.exists(self.log_file):
                    time.sleep(1)
                    continue
                
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    # Go to last position
                    f.seek(self.last_position)
                    
                    # Read new lines
                    new_lines = f.readlines()
                    self.last_position = f.tell()
                
                # Process new lines
                for line in new_lines:
                    if self.running:
                        establishment = self._extract_establishment_from_log(line)
                        if establishment:
                            if self._add_establishment(establishment):
                                self.stats['total_found'] += 1
                                print(f"✅ Novo estabelecimento salvo: {establishment.get('name', 'N/A')}")
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(5)

    def start(self):
        """Inicia o sistema de salvamento automático"""
        try:
            # Start monitoring in background thread
            monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
            monitor_thread.start()
            
            # Main loop with status updates
            while self.running:
                time.sleep(30)  # Status update every 30 seconds
                
                with self.lock:
                    print(f"\n📊 STATUS - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"💾 Estabelecimentos salvos: {len(self.establishments)}")
                    print(f"🔍 Total encontrados: {self.stats['total_found']}")
                    print(f"🔄 Auto-saves realizados: {self.stats['auto_saves']}")
                    print(f"⏰ Última atualização: {self.stats.get('last_update', 'N/A')}")
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        finally:
            self.running = False
            self._save_data()
            print("💾 Salvamento final concluído!")

if __name__ == "__main__":
    salvamento = SalvamentoAutomatico()
    salvamento.start()
