#!/usr/bin/env python3
"""
Sistema de Salvamento Automático DEFINITIVO
Monitora logs em tempo real e salva TODOS os dados automaticamente
Versão final que resolve o problema de uma vez por todas
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

class SalvamentoAutomaticoDefinitivo:
    def __init__(self):
        self.log_file = 'output/scrapy.log'
        self.output_file = 'output/fuel_stations_auto_complete.json'
        self.backup_file = 'output/fuel_stations_auto_backup.json'
        self.progress_file = 'output/auto_monitoring_progress.json'
        
        # Data storage
        self.establishments = []
        self.seen_keys = set()
        self.last_position = 0
        self.running = True
        self.lock = threading.Lock()
        
        # Stats
        self.stats = {
            'total_found': 0,
            'total_saved': 0,
            'last_update': None,
            'started_at': datetime.now().isoformat(),
            'auto_saves': 0,
            'last_log_size': 0
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Load existing data
        self._load_existing_data()
        
        print("🚀 SISTEMA DE SALVAMENTO AUTOMÁTICO DEFINITIVO")
        print(f"📁 Monitorando: {self.log_file}")
        print(f"💾 Salvando em: {self.output_file}")
        print(f"📊 Dados existentes: {len(self.establishments)} estabelecimentos")
        print("🔄 Salvamento automático a cada 2 segundos")

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
                
                # Rebuild seen_keys
                for est in self.establishments:
                    key = self._create_unique_key(est)
                    self.seen_keys.add(key)
                
                self.stats['total_saved'] = len(self.establishments)
                print(f"📂 Carregados {len(self.establishments)} estabelecimentos existentes")
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados existentes: {e}")
            self.establishments = []

    def _create_unique_key(self, establishment: Dict) -> str:
        """Cria chave única baseada em nome + telefone + endereço"""
        name = str(establishment.get('name', '')).strip().lower()
        phone = str(establishment.get('phone', '') or '').strip()
        address = str(establishment.get('address', '')).strip().lower()
        
        # Remove common words from address for better matching
        address_clean = address.replace('brasil', '').replace('santa catarina', '').replace('lat:', '').replace('lon:', '').strip()
        
        return f"{name}|{phone}|{address_clean[:50]}"

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
                    except (ValueError, SyntaxError):
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

    def _add_establishment(self, establishment: Dict):
        """Adiciona estabelecimento se não for duplicado"""
        if not establishment:
            return False
            
        unique_key = self._create_unique_key(establishment)
        
        if unique_key in self.seen_keys:
            return False
            
        with self.lock:
            self.establishments.append(establishment)
            self.seen_keys.add(unique_key)
            
            self.stats['total_saved'] = len(self.establishments)
            self.stats['total_found'] += 1
            self.stats['last_update'] = datetime.now().isoformat()
            
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
                
                self.stats['auto_saves'] += 1
                
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

    def _process_log_file(self):
        """Processa todo o arquivo de log desde o início"""
        if not os.path.exists(self.log_file):
            return
            
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                # Go to last position
                f.seek(self.last_position)
                
                # Read new lines
                new_lines = f.readlines()
                self.last_position = f.tell()
            
            # Process new lines
            new_establishments = 0
            for line in new_lines:
                if self.running:
                    establishment = self._extract_establishment_from_log(line)
                    if establishment:
                        if self._add_establishment(establishment):
                            new_establishments += 1
            
            # Save if new data found
            if new_establishments > 0:
                self._save_data()
                print(f"✅ {new_establishments} novos estabelecimentos salvos automaticamente")
                
        except Exception as e:
            print(f"❌ Erro no processamento: {e}")

    def _monitor_logs_continuously(self):
        """Monitora logs continuamente"""
        print("👀 Monitoramento contínuo iniciado...")
        
        while self.running:
            try:
                self._process_log_file()
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(5)

    def _status_reporter(self):
        """Reporta status a cada 30 segundos"""
        while self.running:
            try:
                time.sleep(30)
                
                if self.running:
                    with self.lock:
                        print(f"\n📊 STATUS AUTOMÁTICO - {datetime.now().strftime('%H:%M:%S')}")
                        print(f"💾 Estabelecimentos salvos: {len(self.establishments)}")
                        print(f"🔍 Total encontrados: {self.stats['total_found']}")
                        print(f"🔄 Auto-saves realizados: {self.stats['auto_saves']}")
                        print(f"⏰ Última atualização: {self.stats.get('last_update', 'N/A')}")
                        
                        # Check log file size
                        if os.path.exists(self.log_file):
                            current_size = os.path.getsize(self.log_file)
                            if current_size != self.stats['last_log_size']:
                                print(f"📈 Log crescendo: {current_size} bytes")
                                self.stats['last_log_size'] = current_size
                
            except Exception as e:
                print(f"❌ Erro no status: {e}")

    def start(self):
        """Inicia o sistema de salvamento automático definitivo"""
        try:
            # Process existing log file first
            print("🔄 Processando arquivo de log existente...")
            self._process_log_file()
            
            # Start monitoring in background thread
            monitor_thread = threading.Thread(target=self._monitor_logs_continuously, daemon=True)
            monitor_thread.start()
            
            # Start status reporter
            status_thread = threading.Thread(target=self._status_reporter, daemon=True)
            status_thread.start()
            
            print("✅ Sistema de salvamento automático ativo!")
            print("🔄 Monitorando logs a cada 2 segundos")
            print("📊 Status a cada 30 segundos")
            print("💾 Salvamento automático quando novos dados são encontrados")
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        finally:
            self.running = False
            self._save_data()
            print("💾 Salvamento final concluído!")

if __name__ == "__main__":
    salvamento = SalvamentoAutomaticoDefinitivo()
    salvamento.start()
