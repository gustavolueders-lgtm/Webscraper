import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

class PerformanceAnalyzer:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'start_time': datetime.now().isoformat(),
            'cells_processed': 0,
            'total_cells': 0,
            'establishments_found': 0,
            'unique_establishments': 0,
            'duplicates_filtered': 0,
            'cells_with_results': 0,
            'cells_empty': 0,
            'average_establishments_per_cell': 0,
            'success_rate': 0,
            'blocks_detected': 0,
            'errors_count': 0,
            'current_cell_index': 0,
            'estimated_completion_time': None,
            'processing_speed': 0,  # cells per hour
            'data_quality_score': 0,
            'cells_details': []
        }
        self.lock = threading.Lock()
        self.output_dir = 'output'
        os.makedirs(self.output_dir, exist_ok=True)

    def update_total_cells(self, total: int):
        with self.lock:
            self.metrics['total_cells'] = total

    def start_cell_processing(self, cell_index: int, lat: float, lon: float, term: str):
        with self.lock:
            self.metrics['current_cell_index'] = cell_index
            cell_data = {
                'index': cell_index,
                'lat': lat,
                'lon': lon,
                'term': term,
                'start_time': datetime.now().isoformat(),
                'establishments_found': 0,
                'success': False,
                'error': None,
                'processing_time': 0
            }
            self.metrics['cells_details'].append(cell_data)

    def complete_cell_processing(self, cell_index: int, establishments_count: int, 
                                success: bool = True, error: str = None):
        with self.lock:
            self.metrics['cells_processed'] += 1
            
            # Update cell details
            for cell in self.metrics['cells_details']:
                if cell['index'] == cell_index:
                    cell['establishments_found'] = establishments_count
                    cell['success'] = success
                    cell['error'] = error
                    start_time = datetime.fromisoformat(cell['start_time'])
                    cell['processing_time'] = (datetime.now() - start_time).total_seconds()
                    break
            
            # Update global metrics
            self.metrics['establishments_found'] += establishments_count
            
            if establishments_count > 0:
                self.metrics['cells_with_results'] += 1
            else:
                self.metrics['cells_empty'] += 1
            
            if not success:
                self.metrics['errors_count'] += 1
            
            # Calculate derived metrics
            self._calculate_derived_metrics()
            
            # Save progress
            self._save_progress()

    def add_unique_establishment(self):
        with self.lock:
            self.metrics['unique_establishments'] += 1

    def add_duplicate_filtered(self):
        with self.lock:
            self.metrics['duplicates_filtered'] += 1

    def report_block_detected(self):
        with self.lock:
            self.metrics['blocks_detected'] += 1

    def _calculate_derived_metrics(self):
        if self.metrics['cells_processed'] > 0:
            self.metrics['average_establishments_per_cell'] = (
                self.metrics['establishments_found'] / self.metrics['cells_processed']
            )
            self.metrics['success_rate'] = (
                (self.metrics['cells_processed'] - self.metrics['errors_count']) / 
                self.metrics['cells_processed'] * 100
            )
            
            # Calculate processing speed (cells per hour)
            elapsed_hours = (time.time() - self.start_time) / 3600
            if elapsed_hours > 0:
                self.metrics['processing_speed'] = self.metrics['cells_processed'] / elapsed_hours
                
                # Estimate completion time
                remaining_cells = self.metrics['total_cells'] - self.metrics['cells_processed']
                if self.metrics['processing_speed'] > 0:
                    remaining_hours = remaining_cells / self.metrics['processing_speed']
                    completion_time = datetime.now() + timedelta(hours=remaining_hours)
                    self.metrics['estimated_completion_time'] = completion_time.isoformat()
            
            # Calculate data quality score
            if self.metrics['establishments_found'] > 0:
                quality_factors = [
                    min(1.0, self.metrics['success_rate'] / 100),  # Success rate factor
                    min(1.0, self.metrics['unique_establishments'] / max(1, self.metrics['establishments_found'])),  # Uniqueness factor
                    min(1.0, self.metrics['cells_with_results'] / max(1, self.metrics['cells_processed']))  # Coverage factor
                ]
                self.metrics['data_quality_score'] = sum(quality_factors) / len(quality_factors) * 100

    def _save_progress(self):
        progress_file = os.path.join(self.output_dir, 'scraping_progress.json')
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def save_checkpoint(self, cell_index: int):
        checkpoint_data = {
            'last_cell_index': cell_index,
            'cells_completed': self.metrics['cells_processed'],
            'total_cells': self.metrics['total_cells'],
            'establishments_found': self.metrics['unique_establishments'],
            'timestamp': datetime.now().isoformat()
        }
        
        checkpoint_file = os.path.join(self.output_dir, 'grid_checkpoint.json')
        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving checkpoint: {e}")

    def load_checkpoint(self) -> Dict[str, Any]:
        checkpoint_file = os.path.join(self.output_dir, 'grid_checkpoint.json')
        try:
            if os.path.exists(checkpoint_file):
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
        return {}

    def get_summary(self) -> Dict[str, Any]:
        with self.lock:
            elapsed_time = time.time() - self.start_time
            return {
                'elapsed_time_hours': elapsed_time / 3600,
                'cells_processed': self.metrics['cells_processed'],
                'total_cells': self.metrics['total_cells'],
                'progress_percentage': (self.metrics['cells_processed'] / max(1, self.metrics['total_cells'])) * 100,
                'unique_establishments': self.metrics['unique_establishments'],
                'processing_speed': self.metrics['processing_speed'],
                'estimated_completion': self.metrics['estimated_completion_time'],
                'success_rate': self.metrics['success_rate'],
                'data_quality_score': self.metrics['data_quality_score']
            }
