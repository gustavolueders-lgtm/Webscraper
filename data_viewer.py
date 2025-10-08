#!/usr/bin/env python3
"""
Visualizador de dados coletados
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class DataViewer:
    def __init__(self, data_file: str = "output/fuel_stations_monitored.json", 
                 progress_file: str = "output/monitoring_progress.json"):
        self.data_file = data_file
        self.progress_file = progress_file

    def show_summary(self):
        """Mostra resumo dos dados"""
        print("📊 RESUMO DOS DADOS COLETADOS")
        print("=" * 50)
        
        # Verifica arquivos
        if not os.path.exists(self.data_file):
            print(f"❌ Arquivo de dados não encontrado: {self.data_file}")
            return
        
        try:
            # Carrega dados
            with open(self.data_file, 'r', encoding='utf-8') as f:
                establishments = json.load(f)
            
            print(f"🏪 Total de estabelecimentos: {len(establishments):,}")

            # Análise de telefones
            with_phones = [est for est in establishments if est.get('phone')]
            without_phones = [est for est in establishments if not est.get('phone')]
            phone_rate = (len(with_phones) / len(establishments) * 100) if establishments else 0

            print(f"📞 Com telefone: {len(with_phones):,} ({phone_rate:.1f}%)")
            print(f"❌ Sem telefone: {len(without_phones):,}")

            if establishments:
                # Análise por região
                regions = {}
                categories = {}
                
                for est in establishments:
                    # Por coordenadas (região aproximada)
                    lat = est.get('cell_lat', 0)
                    lon = est.get('cell_lon', 0)
                    region_key = f"{lat:.1f},{lon:.1f}"
                    regions[region_key] = regions.get(region_key, 0) + 1
                    
                    # Por categoria
                    category = est.get('category', 'Unknown')
                    categories[category] = categories.get(category, 0) + 1
                
                print(f"📍 Regiões cobertas: {len(regions)}")
                print(f"🏷️ Categorias: {len(categories)}")
                
                # Mostra top regiões
                top_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:5]
                print(f"\n🔝 TOP 5 REGIÕES:")
                for region, count in top_regions:
                    print(f"   📍 {region}: {count} estabelecimentos")
                
                # Primeiro e último
                first = establishments[0]
                last = establishments[-1]
                
                print(f"\n⏰ PERÍODO:")
                print(f"   🟢 Primeiro: {first.get('scraped_at', 'N/A')}")
                print(f"   🔴 Último: {last.get('scraped_at', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
        
        # Progresso
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                
                print(f"\n📈 PROGRESSO:")
                print(f"   📍 Células processadas: {progress.get('cells_processed', 0)}")
                print(f"   ⚡ Taxa: {progress.get('establishments_per_minute', 0):.1f}/min")
                print(f"   📊 Status: {progress.get('spider_status', 'unknown')}")
                
            except Exception as e:
                print(f"⚠️ Erro ao carregar progresso: {e}")

    def show_latest(self, count: int = 10):
        """Mostra os últimos estabelecimentos"""
        if not os.path.exists(self.data_file):
            print(f"❌ Arquivo de dados não encontrado: {self.data_file}")
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                establishments = json.load(f)
            
            if not establishments:
                print("📭 Nenhum estabelecimento encontrado")
                return
            
            latest = establishments[-count:] if len(establishments) >= count else establishments
            
            print(f"📍 ÚLTIMOS {len(latest)} ESTABELECIMENTOS:")
            print("-" * 60)
            
            for i, est in enumerate(latest, 1):
                print(f"{i:2d}. 🏪 {est.get('name', 'N/A')}")
                print(f"     📍 {est.get('address', 'N/A')}")
                print(f"     🆔 {est.get('place_id', 'N/A')}")
                print(f"     ⏰ {est.get('scraped_at', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")

    def search_establishments(self, query: str):
        """Busca estabelecimentos por nome"""
        if not os.path.exists(self.data_file):
            print(f"❌ Arquivo de dados não encontrado: {self.data_file}")
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                establishments = json.load(f)
            
            query_lower = query.lower()
            matches = []
            
            for est in establishments:
                name = est.get('name', '').lower()
                if query_lower in name:
                    matches.append(est)
            
            print(f"🔍 BUSCA POR: '{query}'")
            print(f"📊 Encontrados: {len(matches)} resultados")
            print("-" * 50)
            
            for i, est in enumerate(matches[:20], 1):  # Máximo 20 resultados
                print(f"{i:2d}. 🏪 {est.get('name', 'N/A')}")
                print(f"     📍 {est.get('address', 'N/A')}")
                print()
                
            if len(matches) > 20:
                print(f"... e mais {len(matches) - 20} resultados")
                
        except Exception as e:
            print(f"❌ Erro ao buscar: {e}")

    def export_csv(self, output_file: str = "output/establishments.csv"):
        """Exporta dados para CSV"""
        if not os.path.exists(self.data_file):
            print(f"❌ Arquivo de dados não encontrado: {self.data_file}")
            return
        
        try:
            import csv
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                establishments = json.load(f)
            
            if not establishments:
                print("📭 Nenhum dado para exportar")
                return
            
            # Cabeçalhos
            headers = ['name', 'address', 'category', 'place_id', 'cell_lat', 'cell_lon', 'scraped_at']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for est in establishments:
                    row = {header: est.get(header, '') for header in headers}
                    writer.writerow(row)
            
            print(f"✅ Dados exportados para: {output_file}")
            print(f"📊 Total de linhas: {len(establishments)}")
            
        except Exception as e:
            print(f"❌ Erro ao exportar: {e}")

def main():
    """Interface de linha de comando"""
    viewer = DataViewer()
    
    while True:
        print("\n" + "="*50)
        print("📊 VISUALIZADOR DE DADOS")
        print("="*50)
        print("1. 📋 Resumo geral")
        print("2. 📍 Últimos estabelecimentos")
        print("3. 🔍 Buscar por nome")
        print("4. 📤 Exportar para CSV")
        print("5. 🚪 Sair")
        print("-"*50)
        
        try:
            choice = input("Escolha uma opção (1-5): ").strip()
            
            if choice == '1':
                viewer.show_summary()
            
            elif choice == '2':
                count = input("Quantos mostrar? (padrão: 10): ").strip()
                count = int(count) if count.isdigit() else 10
                viewer.show_latest(count)
            
            elif choice == '3':
                query = input("Digite o termo de busca: ").strip()
                if query:
                    viewer.search_establishments(query)
                else:
                    print("⚠️ Digite um termo válido")
            
            elif choice == '4':
                filename = input("Nome do arquivo CSV (padrão: establishments.csv): ").strip()
                if not filename:
                    filename = "output/establishments.csv"
                viewer.export_csv(filename)
            
            elif choice == '5':
                print("👋 Até logo!")
                break
            
            else:
                print("⚠️ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
