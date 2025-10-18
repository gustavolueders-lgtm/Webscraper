#!/usr/bin/env python3
"""
Script para iniciar o scraping de forma rápida e otimizada
"""

import subprocess
import time
import os
from datetime import datetime

def iniciar_rapido(start_cell=None):
    """Inicia o sistema de forma rápida"""
    
    print("🚀 INICIANDO SISTEMA RÁPIDO DE BORRACHARIAS")
    print("=" * 60)
    print(f"⏰ Horário: {datetime.now().strftime('%H:%M:%S')}")
    
    # Determinar célula de início
    if start_cell is None:
        try:
            from controle_scraping import ControleScraping
            controle = ControleScraping()
            start_cell = controle.get_last_cell()
            print(f"📍 Retomando da célula: {start_cell}")
        except:
            start_cell = 0
            print(f"📍 Iniciando da célula: {start_cell}")
    else:
        print(f"📍 Célula especificada: {start_cell}")
    
    # 1. Iniciar sistema de salvamento automático
    print("\n💾 INICIANDO SISTEMA DE SALVAMENTO...")
    try:
        salvamento_process = subprocess.Popen(
            ['python', 'salvamento_automatico_borracharias.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        print(f"✅ Sistema de salvamento iniciado (PID: {salvamento_process.pid})")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Erro ao iniciar salvamento: {e}")
        return False
    
    # 2. Iniciar spider com configurações otimizadas
    print("\n🕷️ INICIANDO SPIDER OTIMIZADO...")
    
    spider_cmd = [
        'scrapy', 'crawl', 'borracharia_resumable',
        '-a', f'start_cell={start_cell}',
        '-s', 'DOWNLOAD_DELAY=1',  # Rápido
        '-s', 'RANDOMIZE_DOWNLOAD_DELAY=True',
        '-s', 'CONCURRENT_REQUESTS=3',  # Mais concorrência
        '-s', 'CONCURRENT_REQUESTS_PER_DOMAIN=3',
        '-s', 'AUTOTHROTTLE_ENABLED=True',
        '-s', 'AUTOTHROTTLE_START_DELAY=0.5',
        '-s', 'AUTOTHROTTLE_MAX_DELAY=3',
        '-s', 'AUTOTHROTTLE_TARGET_CONCURRENCY=3.0',
        '-L', 'INFO'
    ]
    
    try:
        spider_process = subprocess.Popen(
            spider_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        print(f"✅ Spider iniciado (PID: {spider_process.pid})")
        
        # Salvar PIDs
        with open('output/sistema_pids.txt', 'w') as f:
            f.write(f"salvamento_pid={salvamento_process.pid}\n")
            f.write(f"spider_pid={spider_process.pid}\n")
        
    except Exception as e:
        print(f"❌ Erro ao iniciar spider: {e}")
        salvamento_process.terminate()
        return False
    
    print("\n✅ SISTEMA RÁPIDO INICIADO!")
    print("=" * 60)
    print("⚡ CONFIGURAÇÕES OTIMIZADAS:")
    print("   🔧 Download delay: 1s (era 3s)")
    print("   🔄 Concurrent requests: 3 (era 1)")
    print("   ⏸️ Pausas estratégicas: 30-60s a cada 10 células")
    print("   🚀 AutoThrottle: Ativo para ajuste automático")
    print()
    print("📊 COMANDOS:")
    print("   📈 Status: python controle_scraping.py status")
    print("   🛑 Parar: python parar_sistema_completo.py")
    print("   📊 Progresso: python verificar_status_borracharias.py")
    
    return True

def main():
    import sys
    
    start_cell = None
    if len(sys.argv) > 1:
        try:
            start_cell = int(sys.argv[1])
        except ValueError:
            print("❌ Célula deve ser um número")
            return
    
    if iniciar_rapido(start_cell):
        print("\n🎯 Sistema iniciado com sucesso!")
        print("💡 O sistema está rodando em background")
        print("🔍 Use os comandos acima para monitorar")
    else:
        print("\n❌ Falha ao iniciar sistema")

if __name__ == "__main__":
    main()
