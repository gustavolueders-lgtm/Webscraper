#!/usr/bin/env python3
"""
Script para iniciar o scraper completo de São Paulo
"""

import os
import subprocess
import sys
from datetime import datetime

def main():
    print("🚀 INICIANDO SCRAPER COMPLETO DE BORRACHARIAS - SÃO PAULO")
    print("=" * 70)
    print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Configurações
    batch_size = 200  # Células por lote
    max_batches = None  # Sem limite (processar tudo)
    
    print("📊 CONFIGURAÇÕES:")
    print(f"   🎯 Tamanho do lote: {batch_size} células")
    print(f"   📈 Total estimado: ~20.664 células")
    print(f"   ⏱️ Tempo estimado: 40-60 horas")
    print(f"   🔄 Execução: Contínua até completar")
    print()
    
    # Confirmar execução
    resposta = input("Deseja iniciar o scraper completo? (s/N): ").lower().strip()
    
    if resposta != 's':
        print("❌ Operação cancelada.")
        return
    
    print()
    print("🔄 INICIANDO SCRAPER...")
    print("=" * 70)
    
    try:
        # Executar o scraper
        cmd = [sys.executable, 'executar_scraper_sp.py', 'run', str(batch_size)]
        if max_batches:
            cmd.append(str(max_batches))
        
        # Executar em modo interativo
        subprocess.run(cmd)
        
        print()
        print("✅ SCRAPER FINALIZADO!")
        print(f"⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print()
        print("⚠️ SCRAPER INTERROMPIDO PELO USUÁRIO")
        print("💡 O progresso foi salvo e pode ser retomado posteriormente.")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")

if __name__ == '__main__':
    main()
