#!/usr/bin/env python3
"""
Teste simples do Playwright
"""

import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    print("🚀 Testando Playwright...")
    
    async with async_playwright() as p:
        print("✅ Playwright iniciado")
        
        browser = await p.chromium.launch(headless=True)
        print("✅ Browser iniciado")
        
        page = await browser.new_page()
        print("✅ Página criada")
        
        await page.goto("https://www.google.com/search?q=borracharia+sao+paulo")
        print("✅ Página carregada")
        
        title = await page.title()
        print(f"📄 Título: {title}")
        
        await browser.close()
        print("✅ Browser fechado")

if __name__ == '__main__':
    asyncio.run(test_playwright())
