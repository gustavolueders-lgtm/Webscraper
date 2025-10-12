#!/usr/bin/env python3
"""
Sistema de salvamento automático para borracharias
"""

import json
import os
import time
import threading
import ast
from datetime import datetime
from collections import defaultdict

class SalvamentoAutomaticoBorracharias:
    def __init__(self):
        self.log_file = 'output/scrapy.log'
        self.output_file = 'output/tire_shops_auto_complete.json'
        self.backup_file = 'output/tire_shops_auto_backup.json'
        self.running = True
        self.establishments = {}
        self.last_position = 0
        self.save_lock = threading.Lock()

        # Sistema de deduplicação eficiente
        self.unique_keys = set()  # Cache de chaves únicas para verificação rápida
        self.duplicates_blocked = 0  # Contador de duplicatas bloqueadas

        # Carregar dados existentes
        self._load_existing_data()
        
        print(f"🔧 SISTEMA DE SALVAMENTO AUTOMÁTICO PARA BORRACHARIAS INICIADO")
        print(f"📁 Arquivo principal: {self.output_file}")
        print(f"💾 Arquivo backup: {self.backup_file}")
        print(f"📊 Borracharias já salvas: {len(self.establishments)}")
    
    def _load_existing_data(self):
        """Carrega dados existentes e popula cache de deduplicação"""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Verificar se é lista ou dicionário
                if isinstance(data, list):
                    print("🔄 Convertendo formato de lista para dicionário...")
                    # Converter lista para dicionário
                    for item in data:
                        key = self._create_unique_key(item)
                        self.establishments[key] = item
                        self.unique_keys.add(key)
                elif isinstance(data, dict):
                    # Já é dicionário
                    for key, item in data.items():
                        self.establishments[key] = item
                        self.unique_keys.add(key)
                else:
                    print(f"⚠️ Formato de dados desconhecido: {type(data)}")

                print(f"✅ Carregados {len(self.establishments)} borracharias existentes")
                print(f"🔧 Cache de deduplicação inicializado com {len(self.unique_keys)} chaves")
            except Exception as e:
                print(f"⚠️ Erro ao carregar dados existentes: {e}")
    
    def _create_unique_key(self, item):
        """Cria chave única otimizada para evitar duplicatas"""
        # Verificar se item é válido
        if not item or not isinstance(item, dict):
            return f"invalid_{hash(str(item)) % 10000}"

        name = str(item.get('name', '')).strip().lower()
        phone = str(item.get('phone', '')).strip()

        # Usar apenas nome + telefone para deduplicação mais eficiente
        # Se não tiver telefone, usar nome + primeiras palavras do endereço
        if phone and phone != 'none':
            return f"{name}|{phone}"
        else:
            address = str(item.get('address', '')).strip().lower()
            # Pegar primeiras 3 palavras do endereço para comparação
            address_words = address.split()[:3]
            address_key = ' '.join(address_words) if address_words else ''
            return f"{name}|{address_key}"
    
    def _process_log_file(self):
        """Processa arquivo de log em busca de novos dados"""
        if not os.path.exists(self.log_file):
            return
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
            
            new_establishments = 0
            
            for line in new_lines:
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
                        
                        # Criar chave única para deduplicação eficiente
                        key = self._create_unique_key(establishment_data)

                        # Verificação rápida de duplicata usando set
                        if key in self.unique_keys:
                            self.duplicates_blocked += 1
                            continue  # Pula duplicata sem processamento adicional

                        # Adicionar novo estabelecimento
                        self.unique_keys.add(key)
                        self.establishments[key] = establishment_data
                        new_establishments += 1
                    
                    except Exception as e:
                        print(f"⚠️ Erro ao processar linha do log: {e}")
                        continue
            
            if new_establishments > 0:
                self._save_data()
                print(f"💾 Salvos {new_establishments} novas borracharias (Total: {len(self.establishments)}) | 🚫 Duplicatas bloqueadas: {self.duplicates_blocked}")
        
        except Exception as e:
            print(f"❌ Erro ao processar log: {e}")
    
    def _save_data(self):
        """Salva dados nos arquivos"""
        with self.save_lock:
            try:
                # Converter para lista
                data_list = list(self.establishments.values())
                
                # Salvar arquivo principal
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(data_list, f, ensure_ascii=False, indent=2)
                
                # Criar backup
                with open(self.backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data_list, f, ensure_ascii=False, indent=2)
                
            except Exception as e:
                print(f"❌ Erro ao salvar dados: {e}")
    
    def _monitor_logs_continuously(self):
        """Monitora logs continuamente"""
        print("🔄 Monitoramento contínuo iniciado...")
        
        while self.running:
            try:
                self._process_log_file()
                time.sleep(2)  # Verifica a cada 2 segundos
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(5)
    
    def _get_grid_progress(self):
        """Calcula progresso do grid baseado nos logs do spider"""
        # Calcular total de células (mesmo cálculo do spider)
        GRID_SIZE_KM = 5
        LAT_MIN, LAT_MAX = -29.35, -25.95
        LON_MIN, LON_MAX = -53.83, -48.35

        lat_step = GRID_SIZE_KM / 111.0
        lon_step = GRID_SIZE_KM / (111.0 * 0.85)

        lat_cells = int((LAT_MAX - LAT_MIN) / lat_step) + 1
        lon_cells = int((LON_MAX - LON_MIN) / lon_step) + 1
        total_cells = lat_cells * lon_cells

        # Ler progresso real dos logs do spider
        max_cell_index = 0
        try:
            with open('output/scrapy.log', 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Procurar por linhas que indicam progresso do spider
                    if 'cell_index' in line and ('TIRE_SHOP_DATA:' in line or 'Processando célula' in line):
                        try:
                            # Extrair cell_index da linha
                            if 'cell_index' in line:
                                import re
                                match = re.search(r"'cell_index':\s*(\d+)", line)
                                if match:
                                    cell_index = int(match.group(1))
                                    max_cell_index = max(max_cell_index, cell_index)
                        except:
                            continue
        except:
            # Se não conseguir ler logs, usar dados salvos como fallback
            cell_indices = set()
            for item in self.establishments.values():
                cell_index = item.get('cell_index')
                if cell_index is not None:
                    cell_indices.add(cell_index)
            max_cell_index = max(cell_indices) if cell_indices else 0

        processed_cells = max_cell_index + 1  # +1 porque cell_index começa em 0
        progress_percent = (processed_cells / total_cells * 100) if total_cells > 0 else 0

        return processed_cells, total_cells, progress_percent

    def _status_updates(self):
        """Atualiza status periodicamente"""
        while self.running:
            try:
                time.sleep(30)  # Status a cada 30 segundos
                if self.running:
                    processed, total, percent = self._get_grid_progress()
                    print(f"📊 Status: {len(self.establishments)} borracharias | Grid: {processed}/{total} células ({percent:.1f}%) | 🚫 Duplicatas: {self.duplicates_blocked:,} - {datetime.now().strftime('%H:%M:%S')}")
            except:
                pass
    
    def start(self):
        """Inicia o sistema de monitoramento"""
        # Thread para monitoramento contínuo
        monitor_thread = threading.Thread(target=self._monitor_logs_continuously)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Thread para status updates
        status_thread = threading.Thread(target=self._status_updates)
        status_thread.daemon = True
        status_thread.start()
        
        try:
            print("🔧 Sistema rodando... Pressione Ctrl+C para parar")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando sistema...")
            self.running = False
            self._save_data()
            print("✅ Sistema parado e dados salvos")
    
    def get_stats(self):
        """Retorna estatísticas"""
        return {
            'total_establishments': len(self.establishments),
            'output_file': self.output_file,
            'backup_file': self.backup_file,
            'last_update': datetime.now().isoformat()
        }

def main():
    """Função principal"""
    sistema = SalvamentoAutomaticoBorracharias()
    sistema.start()

if __name__ == "__main__":
    main()
