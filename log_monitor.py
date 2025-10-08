#!/usr/bin/env python3
"""
Monitor de logs que extrai dados em tempo real
"""

import json
import os
import time
import threading
from datetime import datetime
from typing import List, Dict, Optional

class LogMonitor:
    def __init__(self, log_file: str = "output/scrapy.log", output_file: str = "output/fuel_stations_monitored.json"):
        self.log_file = log_file
        self.output_file = output_file
        self.progress_file = "output/monitoring_progress.json"
        
        # Data storage
        self.establishments: List[Dict] = []
        self.seen_place_ids = set()
        self.stats = {
            'total_establishments': 0,
            'phones_collected': 0,
            'cells_processed': 0,
            'last_update': None,
            'spider_status': 'unknown',
            'start_time': datetime.now().isoformat(),
            'establishments_per_minute': 0
        }
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.monitor_thread = None
        
        # Cria diretório
        os.makedirs('output', exist_ok=True)
        
        # Carrega dados existentes
        self._load_existing_data()
        
        print(f"🔍 LogMonitor inicializado")
        print(f"📄 Log file: {self.log_file}")
        print(f"💾 Output file: {self.output_file}")
        print(f"📊 Dados existentes: {len(self.establishments)} estabelecimentos")

    def _load_existing_data(self):
        """Carrega dados existentes se houver"""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    self.establishments = json.load(f)
                
                # Reconstrói set de place_ids
                for est in self.establishments:
                    if 'place_id' in est:
                        self.seen_place_ids.add(est['place_id'])
                
                self.stats['total_establishments'] = len(self.establishments)
                print(f"✅ Carregados {len(self.establishments)} estabelecimentos existentes")
                
            except Exception as e:
                print(f"⚠️ Erro ao carregar dados existentes: {e}")

    def start_monitoring(self):
        """Inicia o monitoramento em thread separada"""
        if self.running:
            print("⚠️ Monitor já está rodando")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🚀 Monitor iniciado")

    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("🛑 Monitor parado")

    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        last_position = 0
        
        # Se arquivo existe, vai para o final
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                f.seek(0, 2)  # Vai para o final
                last_position = f.tell()
        
        print(f"📍 Iniciando monitoramento na posição {last_position}")
        
        while self.running:
            try:
                if os.path.exists(self.log_file):
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                        
                        for line in new_lines:
                            self._process_log_line(line.strip())
                
                time.sleep(1)  # Verifica a cada segundo
                
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
                time.sleep(5)

    def _process_log_line(self, line: str):
        """Processa uma linha do log"""
        try:
            # Procura por dados de estabelecimento
            if "🏪 ESTABLISHMENT_DATA:" in line:
                json_start = line.find("{")
                if json_start != -1:
                    json_data = line[json_start:]
                    establishment = json.loads(json_data)
                    self._add_establishment(establishment)
            
            # Procura por progresso de célula
            elif "📍 CELL_COMPLETED:" in line:
                json_start = line.find("{")
                if json_start != -1:
                    json_data = line[json_start:]
                    cell_data = json.loads(json_data)
                    self._update_cell_progress(cell_data)
            
            # Procura por estatísticas do spider
            elif "📊 SPIDER_STATS:" in line:
                json_start = line.find("{")
                if json_start != -1:
                    json_data = line[json_start:]
                    spider_stats = json.loads(json_data)
                    self._update_spider_stats(spider_stats)
            
            # Procura por finalização
            elif "🏁 SPIDER_FINISHED:" in line:
                json_start = line.find("{")
                if json_start != -1:
                    json_data = line[json_start:]
                    finish_data = json.loads(json_data)
                    self._handle_spider_finished(finish_data)
                    
        except Exception as e:
            # Ignora linhas que não são JSON válido
            pass

    def _add_establishment(self, establishment: Dict):
        """Adiciona um estabelecimento"""
        with self.lock:
            place_id = establishment.get('place_id')
            
            if place_id and place_id not in self.seen_place_ids:
                self.seen_place_ids.add(place_id)
                self.establishments.append(establishment)
                self.stats['total_establishments'] = len(self.establishments)

                # Conta telefones
                if establishment.get('phone'):
                    self.stats['phones_collected'] = self.stats.get('phones_collected', 0) + 1

                self.stats['last_update'] = datetime.now().isoformat()

                # Salva incrementalmente a cada 10 itens
                if len(self.establishments) % 10 == 0:
                    self._save_data()
                    phones = self.stats.get('phones_collected', 0)
                    print(f"💾 Salvos {len(self.establishments)} estabelecimentos (📞 {phones} telefones)")

    def _update_cell_progress(self, cell_data: Dict):
        """Atualiza progresso de células"""
        with self.lock:
            self.stats['cells_processed'] = cell_data.get('cells_processed', 0)
            self.stats['last_update'] = datetime.now().isoformat()
            
            # Calcula estabelecimentos por minuto
            start_time = datetime.fromisoformat(self.stats['start_time'])
            elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
            if elapsed_minutes > 0:
                self.stats['establishments_per_minute'] = self.stats['total_establishments'] / elapsed_minutes

    def _update_spider_stats(self, spider_stats: Dict):
        """Atualiza estatísticas do spider"""
        with self.lock:
            if 'status' in spider_stats:
                self.stats['spider_status'] = spider_stats['status']
            
            # Atualiza outros stats se presentes
            for key in ['total_cells', 'total_requests', 'search_terms']:
                if key in spider_stats:
                    self.stats[key] = spider_stats[key]

    def _handle_spider_finished(self, finish_data: Dict):
        """Lida com finalização do spider"""
        with self.lock:
            self.stats['spider_status'] = 'finished'
            self.stats['finish_reason'] = finish_data.get('reason', 'unknown')
            self.stats['finished_at'] = finish_data.get('finished_at')
            
            # Salva dados finais
            self._save_data()
            print(f"🏁 Spider finalizado: {finish_data.get('reason', 'unknown')}")

    def _save_data(self):
        """Salva dados no arquivo"""
        try:
            # Salva estabelecimentos
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.establishments, f, ensure_ascii=False, indent=2)
            
            # Salva progresso
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")

    def get_stats(self) -> Dict:
        """Retorna estatísticas atuais"""
        with self.lock:
            return self.stats.copy()

    def get_latest_establishments(self, count: int = 5) -> List[Dict]:
        """Retorna os últimos estabelecimentos encontrados"""
        with self.lock:
            return self.establishments[-count:] if self.establishments else []

    def force_save(self):
        """Força salvamento dos dados"""
        with self.lock:
            self._save_data()
            print(f"💾 Salvamento forçado: {len(self.establishments)} estabelecimentos")
