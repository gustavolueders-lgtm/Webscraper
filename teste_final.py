#!/usr/bin/env python3
"""
Teste final do spider com salvamento garantido
"""

import os
import subprocess
import json
import time
import signal

def clear_files():
    """Limpa arquivos de teste"""
    files = [
        'output/fuel_stations_final.json',
        'output/scraping_summary.json'
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removido: {file_path}")

def run_final_test():
    """Executa teste final"""
    print("🔬 TESTE FINAL - SPIDER COM SALVAMENTO GARANTIDO")
    print("=" * 60)
    
    # Limpa arquivos
    clear_files()
    
    # Executa spider por tempo limitado
    print("🚀 Iniciando spider final por 90 segundos...")
    
    process = subprocess.Popen(
        ['scrapy', 'crawl', 'fuel_final'],
        cwd=os.getcwd()
    )
    
    start_time = time.time()
    last_count = 0
    
    try:
        # Monitora por 90 segundos
        while time.time() - start_time < 90:
            # Verifica arquivo
            if os.path.exists('output/fuel_stations_final.json'):
                try:
                    with open('output/fuel_stations_final.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    current_count = len(data)
                    if current_count != last_count:
                        elapsed = time.time() - start_time
                        print(f"⏰ {elapsed:.0f}s | 📄 {current_count} itens | ⚡ +{current_count - last_count} novos")
                        last_count = current_count
                    
                    # Para quando chegar a 50 itens
                    if current_count >= 50:
                        print("✅ Chegou a 50 itens! Testando interrupção...")
                        break
                        
                except Exception as e:
                    print(f"⚠️ Erro ao ler arquivo: {e}")
            else:
                elapsed = time.time() - start_time
                print(f"⏳ {elapsed:.0f}s | Aguardando primeiro salvamento...")
            
            time.sleep(3)
        
        print("\n🛑 Interrompendo spider com Ctrl+C simulado...")
        
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    
    finally:
        # Para o processo
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Aguarda um pouco para garantir salvamento
        time.sleep(2)
        
        # Verifica resultado
        check_final_results()

def check_final_results():
    """Verifica os resultados finais"""
    print("\n📋 RESULTADO FINAL:")
    print("=" * 40)
    
    files_to_check = [
        'output/fuel_stations_final.json',
        'output/scraping_summary.json'
    ]
    
    success = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if file_path.endswith('final.json'):
                    count = len(data)
                    print(f"✅ {file_path}: {count} estabelecimentos")
                    
                    if count > 0:
                        first_item = data[0]
                        print(f"   📝 Exemplo: {first_item.get('name', 'N/A')}")
                        print(f"   📍 Local: {first_item.get('address', 'N/A')}")
                        print(f"   🆔 Place ID: {first_item.get('place_id', 'N/A')}")
                    else:
                        success = False
                        
                else:
                    print(f"✅ {file_path}: Resumo criado")
                    print(f"   📊 Total: {data.get('total_establishments', 0)}")
                    
            except Exception as e:
                print(f"❌ {file_path}: Erro - {e}")
                success = False
        else:
            print(f"❌ {file_path}: Não encontrado")
            success = False
    
    # Conclusão final
    print(f"\n🎯 CONCLUSÃO FINAL:")
    if success:
        print("🎉 SUCESSO! O sistema de salvamento está funcionando!")
        print("   ✅ Dados são salvos automaticamente")
        print("   ✅ Arquivos preservados após interrupção")
        print("   ✅ Sistema pronto para execução completa")
        
        # Instruções finais
        print(f"\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: scrapy crawl fuel_final")
        print("2. Monitore: output/fuel_stations_final.json")
        print("3. Interrompa com Ctrl+C quando necessário")
        print("4. Dados estarão salvos e seguros!")
        
    else:
        print("😔 FALHA! Sistema ainda não está funcionando corretamente")
        print("   ❌ Necessária investigação adicional")

if __name__ == "__main__":
    run_final_test()
