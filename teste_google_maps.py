#!/usr/bin/env python3
"""
Teste de acesso ao Google Maps
"""

import asyncio
from playwright.async_api import async_playwright

async def test_google_maps():
    """Testa acesso ao Google Maps"""
    print("🧪 TESTANDO ACESSO AO GOOGLE MAPS")
    print("=" * 40)
    
    async with async_playwright() as p:
        # Lança browser
        print("🚀 Iniciando browser...")
        browser = await p.chromium.launch(headless=False)  # Visível para debug
        page = await browser.new_page()
        
        # Configura user agent
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        try:
            # Testa URL simples do Google Maps
            url = "https://www.google.com/maps/search/posto+de+gasolina/@-27.5954,-48.5480,12z"
            print(f"🌐 Acessando: {url}")
            
            # Aumenta timeout e tenta carregar
            response = await page.goto(url, timeout=60000, wait_until='domcontentloaded')
            
            print(f"✅ Página carregada! Status: {response.status}")
            
            # Aguarda um pouco para carregar conteúdo
            await asyncio.sleep(5)
            
            # Verifica se encontrou elementos
            cards = await page.query_selector_all('div[role="feed"] > div')
            print(f"📍 Encontrados {len(cards)} elementos no feed")
            
            # Tenta extrair alguns nomes
            names = await page.evaluate('''
                () => {
                    const selectors = [
                        'div.fontHeadlineSmall',
                        'a.hfpxzc',
                        'div.qBF1Pd'
                    ];
                    
                    let names = [];
                    for (let selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (let el of elements) {
                            if (el.textContent && el.textContent.trim()) {
                                names.push(el.textContent.trim());
                            }
                        }
                        if (names.length >= 5) break;
                    }
                    return names.slice(0, 10);
                }
            ''')
            
            print(f"🏪 Nomes encontrados: {len(names)}")
            for i, name in enumerate(names[:5], 1):
                print(f"   {i}. {name}")
            
            if len(names) > 0:
                print("🎉 SUCESSO! Google Maps está acessível")
                return True
            else:
                print("⚠️ Página carregou mas não encontrou estabelecimentos")
                return False
                
        except Exception as e:
            print(f"❌ ERRO: {e}")
            return False
            
        finally:
            await browser.close()

async def main():
    """Função principal"""
    success = await test_google_maps()
    
    if success:
        print("\n✅ DIAGNÓSTICO: Google Maps funciona!")
        print("💡 O problema pode ser:")
        print("   - Timeout muito baixo no Scrapy")
        print("   - Muitas requisições simultâneas")
        print("   - Necessidade de delays maiores")
        print("   - User-Agent inadequado")
    else:
        print("\n❌ DIAGNÓSTICO: Google Maps não está acessível")
        print("💡 Possíveis soluções:")
        print("   - Usar VPN")
        print("   - Aguardar um tempo")
        print("   - Usar dados simulados para teste")

if __name__ == "__main__":
    asyncio.run(main())
