#!/usr/bin/env python3
"""
Corrige os seletores do spider baseado no debug
"""

import asyncio
from playwright.async_api import async_playwright

async def analyze_google_maps_structure():
    """Analisa a estrutura real do Google Maps"""
    
    test_url = "https://www.google.com/maps/search/posto+de+combustível/@-27.5954,-48.5480,13z"
    
    print("🔍 ANÁLISE DE SELETORES - GOOGLE MAPS")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        try:
            await page.goto(test_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(5000)
            
            # Analisa estrutura dos cards
            print("🔍 Analisando estrutura dos cards...")
            
            # Pega todos os cards
            cards = await page.query_selector_all('div[role="feed"] > div')
            print(f"📊 Total de cards encontrados: {len(cards)}")
            
            # Analisa os primeiros 3 cards
            for i, card in enumerate(cards[:3]):
                print(f"\n📋 CARD {i+1}:")
                
                # Tenta diferentes seletores para nome
                name_selectors = [
                    'div[class*="fontHeadline"] span',
                    'div[class*="fontHeadline"]',
                    'span[class*="fontHeadline"]',
                    'a span',
                    'div span',
                    '[data-value="Name"]',
                    'h3',
                    'h2',
                    'div[role="button"] span'
                ]
                
                for selector in name_selectors:
                    try:
                        element = await card.query_selector(selector)
                        if element:
                            text = await element.text_content()
                            if text and text.strip():
                                print(f"   ✅ {selector}: '{text.strip()}'")
                            else:
                                print(f"   ⚪ {selector}: (vazio)")
                        else:
                            print(f"   ❌ {selector}: (não encontrado)")
                    except:
                        print(f"   ⚠️ {selector}: (erro)")
                
                # Pega todo o texto do card para análise
                try:
                    card_text = await card.text_content()
                    if card_text:
                        lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                        print(f"   📝 Texto completo: {lines[:3]}")  # Primeiras 3 linhas
                except:
                    print("   ⚠️ Erro ao obter texto do card")
            
            # Testa seletores mais específicos
            print(f"\n🎯 TESTANDO SELETORES ESPECÍFICOS:")
            
            specific_selectors = [
                'div[role="feed"] div[data-result-index] span',
                'div[role="feed"] a span',
                'div[role="feed"] div[jsaction] span',
                'div[role="feed"] div span[class*="fontHeadline"]',
                'div[role="feed"] div span[class*="DUwDvf"]',
                'div[role="feed"] div div[class*="qBF1Pd"]'
            ]
            
            for selector in specific_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    first_text = await elements[0].text_content() if elements else ""
                    print(f"   {selector}: {len(elements)} elementos - '{first_text[:30]}'")
                else:
                    print(f"   {selector}: 0 elementos")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        finally:
            await browser.close()

def main():
    """Função principal"""
    print("🔧 ANÁLISE DE SELETORES DO GOOGLE MAPS")
    print("🎯 Objetivo: Encontrar seletores corretos para extrair nomes")
    
    choice = input("\nExecutar análise? (s/n): ").strip().lower()
    
    if choice == 's':
        asyncio.run(analyze_google_maps_structure())
    else:
        print("👋 Análise disponível quando precisar!")

if __name__ == "__main__":
    main()
