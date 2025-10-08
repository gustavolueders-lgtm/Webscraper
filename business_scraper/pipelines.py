import json
import os
import threading
import signal
import sys
from itemadapter import ItemAdapter

class JsonWriterPipeline:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()
        self.save_interval = 50  # Save every 50 items (mais frequente)
        self.output_file = 'output/fuel_stations.json'
        self.backup_file = 'output/fuel_stations_backup.json'

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n🛑 Recebido sinal {signum}. Salvando dados...")
        self._force_save()
        print("💾 Dados salvos com sucesso!")
        sys.exit(0)

    def open_spider(self, spider):
        os.makedirs('output', exist_ok=True)
        self.items = []
        spider.logger.info("🚀 Pipeline iniciado com salvamento a cada 50 itens")

    def close_spider(self, spider):
        # Final save when spider closes
        with self.lock:
            self._save_items(spider)
            spider.logger.info("✅ Pipeline finalizado")

    def _force_save(self):
        """Force save without spider context"""
        try:
            with self.lock:
                if self.items:
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        json.dump(self.items, f, ensure_ascii=False, indent=2)
                    print(f"💾 {len(self.items)} itens salvos em {self.output_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

    def _save_items(self, spider):
        """Save items to file with backup"""
        try:
            # Create backup first
            if os.path.exists(self.output_file):
                import shutil
                shutil.copy2(self.output_file, self.backup_file)

            # Save main file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)

            spider.logger.info(f"💾 Saved {len(self.items)} items to {self.output_file}")

        except Exception as e:
            spider.logger.error(f"❌ Erro ao salvar: {e}")

    def process_item(self, item, spider):
        with self.lock:
            self.items.append(ItemAdapter(item).asdict())

            # Save incrementally every 50 items
            if len(self.items) % self.save_interval == 0:
                self._save_items(spider)

        return item
