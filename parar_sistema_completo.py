#!/usr/bin/env python3
"""
Script para parar o sistema completo de scraping de borracharias
"""

import os
import signal
import psutil
import time
from datetime import datetime

def parar_sistema_completo():
    """Para o sistema completo: spider + salvamento automático"""
    
    print("🛑 PARANDO SISTEMA COMPLETO DE BORRACHARIAS")
    print("=" * 60)
    print(f"⏰ Horário: {datetime.now().strftime('%H:%M:%S')}")
    
    pids_parados = []
    
    # 1. Ler PIDs salvos
    pids_file = 'output/sistema_pids.txt'
    spider_pid = None
    salvamento_pid = None
    
    if os.path.exists(pids_file):
        try:
            with open(pids_file, 'r') as f:
                for line in f:
                    if line.startswith('spider_pid='):
                        spider_pid = int(line.split('=')[1].strip())
                    elif line.startswith('salvamento_pid='):
                        salvamento_pid = int(line.split('=')[1].strip())
        except Exception as e:
            print(f"⚠️ Erro ao ler PIDs: {e}")
    
    # 2. Parar spider
    print("\n1️⃣ PARANDO SPIDER")
    print("-" * 30)
    
    if spider_pid and psutil.pid_exists(spider_pid):
        try:
            print(f"🛑 Parando spider (PID: {spider_pid})")
            os.kill(spider_pid, signal.SIGTERM)
            time.sleep(3)
            
            # Verificar se parou
            if psutil.pid_exists(spider_pid):
                print("🔨 Forçando parada do spider...")
                os.kill(spider_pid, signal.SIGKILL)
            
            pids_parados.append(spider_pid)
            print("✅ Spider parado")
            
        except Exception as e:
            print(f"❌ Erro ao parar spider: {e}")
    else:
        print("⚠️ Spider não encontrado ou já parado")
    
    # 3. Parar sistema de salvamento
    print("\n2️⃣ PARANDO SISTEMA DE SALVAMENTO")
    print("-" * 40)
    
    if salvamento_pid and psutil.pid_exists(salvamento_pid):
        try:
            print(f"🛑 Parando sistema de salvamento (PID: {salvamento_pid})")
            os.kill(salvamento_pid, signal.SIGTERM)
            time.sleep(2)
            
            # Verificar se parou
            if psutil.pid_exists(salvamento_pid):
                print("🔨 Forçando parada do sistema de salvamento...")
                os.kill(salvamento_pid, signal.SIGKILL)
            
            pids_parados.append(salvamento_pid)
            print("✅ Sistema de salvamento parado")
            
        except Exception as e:
            print(f"❌ Erro ao parar sistema de salvamento: {e}")
    else:
        print("⚠️ Sistema de salvamento não encontrado ou já parado")
    
    # 4. Buscar outros processos relacionados
    print("\n3️⃣ VERIFICANDO OUTROS PROCESSOS")
    print("-" * 40)
    
    processos_encontrados = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            
            # Procurar por processos relacionados
            if any(keyword in cmdline.lower() for keyword in [
                'borracharia', 'tire_shops', 'salvamento_automatico_borracharias',
                'scrapy crawl borracharia', 'scrapy crawl tire'
            ]):
                processos_encontrados.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if processos_encontrados:
        print(f"🔍 Encontrados {len(processos_encontrados)} processos relacionados:")
        for proc in processos_encontrados:
            pid = proc['pid']
            if pid not in pids_parados:
                try:
                    print(f"   🛑 Parando PID {pid}: {proc['name']}")
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)
                    
                    if psutil.pid_exists(pid):
                        os.kill(pid, signal.SIGKILL)
                    
                    pids_parados.append(pid)
                except Exception as e:
                    print(f"   ❌ Erro ao parar PID {pid}: {e}")
    else:
        print("✅ Nenhum processo adicional encontrado")
    
    # 5. Limpar arquivos de controle
    print("\n4️⃣ LIMPANDO ARQUIVOS DE CONTROLE")
    print("-" * 40)
    
    arquivos_controle = [
        'output/sistema_pids.txt',
        'output/scraping.pid',
        'output/scraping_status.json'
    ]
    
    for arquivo in arquivos_controle:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                print(f"🗑️ Removido: {arquivo}")
            except Exception as e:
                print(f"⚠️ Erro ao remover {arquivo}: {e}")
    
    # 6. Status final
    print("\n✅ SISTEMA COMPLETO PARADO")
    print("=" * 60)
    
    if pids_parados:
        print(f"🛑 PIDs parados: {', '.join(map(str, pids_parados))}")
    
    # Mostrar última célula processada
    try:
        from controle_scraping import ControleScraping
        controle = ControleScraping()
        last_cell = controle.get_last_cell()
        print(f"📍 Última célula processada: {last_cell}")
        
        total_cells = 7904
        progress = (last_cell / total_cells) * 100
        print(f"📈 Progresso total: {progress:.2f}% ({last_cell:,}/{total_cells:,})")
    except Exception as e:
        print(f"⚠️ Erro ao obter progresso: {e}")
    
    print()
    print("🔄 PARA RETOMAR:")
    print("   python iniciar_sistema_completo.py")
    print("   (Retomará automaticamente do ponto onde parou)")

def main():
    print("🔧 CONTROLE DO SISTEMA DE BORRACHARIAS")
    print("=" * 50)
    print("⚠️ ATENÇÃO: Isso irá parar TODOS os processos de scraping!")
    print()
    
    resposta = input("Tem certeza que deseja parar o sistema? (s/N): ").lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        parar_sistema_completo()
    else:
        print("❌ Operação cancelada")

if __name__ == "__main__":
    main()
