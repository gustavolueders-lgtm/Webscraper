#!/usr/bin/env python3
"""
Debug do spider - testa uma URL específica
"""

import asyncio
from playwright.async_api import async_playwright

async def test_google_maps_url():
    """Testa uma URL específica do Google Maps"""
    
    # URL de teste - área de Florianópolis
    test_url = "https://www.google.com/maps/search/posto+de+combustível/@-27.5954,-48.5480,13z"
    
    print("🔍 TESTE DE DEBUG - GOOGLE MAPS")
    print("=" * 50)
    print(f"🌐 URL: {test_url}")
    print("⏰ Aguarde...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visível para debug
        page = await browser.new_page()
        
        # User agent
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        try:
            print("📡 Navegando para URL...")
            await page.goto(test_url, wait_until='networkidle', timeout=30000)
            
            print("⏰ Aguardando 5 segundos...")
            await page.wait_for_timeout(5000)
            
            print("🔍 Verificando seletores...")
            
            # Testa diferentes seletores
            selectors_to_test = [
                'div[role="feed"] > div',
                'div[data-value="Directions"]',
                'a[data-value="Directions"]',
                'div.Nv2PK',
                'div.hfpxzc',
                'div.fontHeadlineSmall',
                '[data-result-index]',
                'div[jsaction*="mouseover"]'
            ]
            
            for selector in selectors_to_test:
                elements = await page.query_selector_all(selector)
                print(f"   {selector}: {len(elements)} elementos")
            
            # Pega HTML da página
            print("\n📄 Salvando HTML para análise...")
            html_content = await page.content()
            
            with open('debug_google_maps.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("✅ HTML salvo em: debug_google_maps.html")
            
            # Verifica se há resultados visíveis
            print("\n🔍 Procurando por texto de estabelecimentos...")
            
            # Procura por palavras-chave
            keywords = ['posto', 'combustível', 'gasolina', 'Petrobras', 'Shell', 'BR']
            
            for keyword in keywords:
                try:
                    element = await page.query_selector(f'text="{keyword}"')
                    if element:
                        print(f"   ✅ Encontrado: '{keyword}'")
                    else:
                        print(f"   ❌ Não encontrado: '{keyword}'")
                except:
                    print(f"   ⚠️ Erro ao buscar: '{keyword}'")
            
            # Verifica se há bloqueio
            page_text = await page.text_content('body')
            
            if 'blocked' in page_text.lower() or 'captcha' in page_text.lower():
                print("🚨 POSSÍVEL BLOQUEIO DETECTADO!")
            
            if 'não foi possível' in page_text.lower() or 'try again' in page_text.lower():
                print("🚨 ERRO DE CARREGAMENTO DETECTADO!")
            
            print(f"\n📊 Tamanho da página: {len(page_text)} caracteres")
            
            # Aguarda para inspeção manual
            print("\n💡 Página aberta para inspeção manual...")
            print("🔍 Verifique se os resultados estão carregando")
            print("⏰ Aguardando 30 segundos...")
            
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        finally:
            await browser.close()

def main():
    """Função principal"""
    print("🐛 DEBUG DO SPIDER - TESTE MANUAL")
    print("⚠️ Este teste abrirá o navegador visível")
    print("🔍 Você poderá ver exatamente o que está acontecendo")
    
    choice = input("\nExecutar teste? (s/n): ").strip().lower()
    
    if choice == 's':
        asyncio.run(test_google_maps_url())
    else:
        print("👋 Teste disponível quando precisar!")

if __name__ == "__main__":
    main()
