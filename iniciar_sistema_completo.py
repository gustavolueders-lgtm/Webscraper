#!/usr/bin/env python3
"""
Script para iniciar o sistema completo de scraping de borracharias
"""

import subprocess
import time
import os
from datetime import datetime

def iniciar_sistema_completo(start_cell=None):
    """Inicia o sistema completo: salvamento automático + spider"""
    
    print("🚀 INICIANDO SISTEMA COMPLETO DE BORRACHARIAS")
    print("=" * 60)
    print(f"⏰ Horário: {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Iniciar sistema de salvamento automático
    print("\n1️⃣ INICIANDO SISTEMA DE SALVAMENTO AUTOMÁTICO")
    print("-" * 50)
    
    try:
        salvamento_process = subprocess.Popen(
            ['python', 'salvamento_automatico_borracharias.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        print(f"✅ Sistema de salvamento iniciado (PID: {salvamento_process.pid})")
        
        # Aguardar um pouco para o sistema inicializar
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar sistema de salvamento: {e}")
        return False
    
    # 2. Iniciar spider
    print("\n2️⃣ INICIANDO SPIDER DE BORRACHARIAS")
    print("-" * 50)
    
    # Determinar célula de início
    if start_cell is None:
        # Tentar determinar automaticamente
        try:
            from controle_scraping import ControleScraping
            controle = ControleScraping()
            start_cell = controle.get_last_cell()
            print(f"📍 Célula de início detectada automaticamente: {start_cell}")
        except:
            start_cell = 0
            print(f"📍 Usando célula de início padrão: {start_cell}")
    else:
        print(f"📍 Célula de início especificada: {start_cell}")
    
    # Comando do spider
    spider_cmd = [
        'scrapy', 'crawl', 'borracharia_resumable',
        '-a', f'start_cell={start_cell}',
        '-s', 'DOWNLOAD_DELAY=3',
        '-s', 'CONCURRENT_REQUESTS=1',
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
        
        # Salvar PIDs para controle
        with open('output/sistema_pids.txt', 'w') as f:
            f.write(f"salvamento_pid={salvamento_process.pid}\n")
            f.write(f"spider_pid={spider_process.pid}\n")
        
    except Exception as e:
        print(f"❌ Erro ao iniciar spider: {e}")
        # Parar sistema de salvamento se spider falhou
        salvamento_process.terminate()
        return False
    
    # 3. Instruções finais
    print("\n✅ SISTEMA COMPLETO INICIADO COM SUCESSO!")
    print("=" * 60)
    print("📊 INFORMAÇÕES:")
    print(f"   🔧 Sistema de salvamento: PID {salvamento_process.pid}")
    print(f"   🕷️ Spider: PID {spider_process.pid}")
    print(f"   📍 Célula de início: {start_cell}")
    print()
    print("🔧 COMANDOS ÚTEIS:")
    print("   📊 Ver status: python controle_scraping.py status")
    print("   🛑 Parar tudo: python parar_sistema_completo.py")
    print("   📈 Ver progresso: python verificar_status_borracharias.py")
    print()
    print("⚠️ IMPORTANTE:")
    print("   - O sistema continuará rodando em background")
    print("   - Use Ctrl+C para parar este script (sistema continua)")
    print("   - Para parar completamente, use: python parar_sistema_completo.py")
    
    return True

def main():
    import sys
    
    start_cell = None
    
    if len(sys.argv) > 1:
        try:
            start_cell = int(sys.argv[1])
        except ValueError:
            print("❌ Célula deve ser um número")
            print("Uso: python iniciar_sistema_completo.py [célula_início]")
            print("Exemplo: python iniciar_sistema_completo.py 1488")
            return
    
    print("🔧 SISTEMA DE SCRAPING DE BORRACHARIAS")
    print("=" * 50)
    
    if start_cell:
        print(f"🎯 Iniciando da célula: {start_cell}")
    else:
        print("🎯 Detectando célula de início automaticamente...")
    
    print()
    
    if iniciar_sistema_completo(start_cell):
        print("\n🎉 Sistema iniciado com sucesso!")
        print("💡 Dica: Deixe este terminal aberto para ver as mensagens")
        
        try:
            # Manter script rodando para mostrar mensagens
            while True:
                time.sleep(60)
                print(f"⏰ Sistema rodando... {datetime.now().strftime('%H:%M:%S')}")
        except KeyboardInterrupt:
            print("\n👋 Script interrompido pelo usuário")
            print("⚠️ ATENÇÃO: O sistema de scraping continua rodando em background!")
            print("🛑 Para parar completamente: python parar_sistema_completo.py")
    else:
        print("\n❌ Falha ao iniciar sistema")

if __name__ == "__main__":
    main()
