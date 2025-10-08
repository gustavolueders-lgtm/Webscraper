# 📋 DOCUMENTAÇÃO TÉCNICA - SCRAPER GOOGLE MAPS

## 🎯 **VISÃO GERAL**

Sistema de scraping do Google Maps para coleta de postos de combustível em Santa Catarina usando Scrapy + Playwright.

**Status Atual:** ❌ **PROBLEMA CRÍTICO - DADOS NÃO SÃO SALVOS**

---

## 📁 **ESTRUTURA DO PROJETO**

```
autoscrap/
├── business_scraper/
│   ├── __init__.py
│   ├── settings.py              # Configurações do Scrapy
│   ├── items.py                 # Definição dos dados coletados
│   ├── pipelines.py             # Processamento e salvamento
│   ├── middlewares.py           # Middlewares customizados
│   ├── spiders/
│   │   ├── __init__.py
│   │   ├── fuel_stations_spider.py    # Spider original (complexo)
│   │   └── simple_fuel_spider.py      # Spider simplificado (ATIVO)
│   └── utils/
│       ├── __init__.py
│       └── performance_analyzer.py    # Análise de performance
├── output/                      # Arquivos de saída
│   ├── fuel_stations.json      # Dados coletados (SE PERDE!)
│   ├── scraping_progress.json  # Progresso em tempo real
│   └── scrapy.log              # Logs do sistema
├── app.py                      # Interface Streamlit
├── run_scraper.py              # Script de execução
├── restart_scraper.py          # Script de reinício
├── test_simple.py              # Script de teste
└── requirements.txt            # Dependências
```

---

## 🕷️ **SPIDER PRINCIPAL: simple_fuel_spider.py**

### **Classe: SimpleFuelSpider**

```python
class SimpleFuelSpider(scrapy.Spider):
    name = 'simple_fuel'
    allowed_domains = ['maps.google.com']
```

### **Parâmetros de Configuração:**

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `GRID_SIZE_KM` | 5 | Tamanho da célula do grid em km |
| `LAT_MIN` | -29.35 | Latitude mínima (Santa Catarina) |
| `LAT_MAX` | -25.95 | Latitude máxima (Santa Catarina) |
| `LON_MIN` | -53.83 | Longitude mínima (Santa Catarina) |
| `LON_MAX` | -48.35 | Longitude máxima (Santa Catarina) |
| `SEARCH_TERMS` | ["gas station", "posto de combustível"] | Termos de busca |

### **Métodos Principais:**

#### **1. start_requests()**
- **Função:** Gera requests iniciais para cada célula do grid
- **Retorna:** Generator de Request objects
- **Grid:** 8.208 células × 2 termos = 16.416 requests totais

#### **2. parse_search_results(response)**
- **Função:** Processa resultados da busca do Google Maps
- **Parâmetros:** 
  - `response`: Resposta HTTP da página
- **Extrai:** Cards de estabelecimentos da lista
- **Seletores CSS:**
  ```python
  selectors_to_try = [
      'div.fontHeadlineSmall::text',  # Nome principal
      'a.hfpxzc::text',               # Nome alternativo
      'div.qBF1Pd::text',             # Nome backup
  ]
  ```

#### **3. _extract_from_card(card_element, page)**
- **Função:** Extrai dados de um card individual
- **Parâmetros:**
  - `card_element`: Elemento HTML do card
  - `page`: Objeto Page do Playwright
- **Retorna:** Dict com dados do estabelecimento

#### **4. _generate_grid_cells()**
- **Função:** Gera coordenadas das células do grid
- **Algoritmo:** Divisão geográfica em células 5x5km
- **Retorna:** Lista de tuplas (lat, lon)

---

## ⚙️ **CONFIGURAÇÕES: settings.py**

### **Configurações de Performance:**

| Setting | Valor | Descrição |
|---------|-------|-----------|
| `CONCURRENT_REQUESTS` | 2 | Requests simultâneos |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | 2 | Requests por domínio |
| `DOWNLOAD_DELAY` | 4 | Delay entre requests (segundos) |
| `RANDOMIZE_DOWNLOAD_DELAY` | 2 | Randomização do delay |
| `AUTOTHROTTLE_ENABLED` | True | Throttling automático |
| `AUTOTHROTTLE_START_DELAY` | 4 | Delay inicial |
| `AUTOTHROTTLE_MAX_DELAY` | 15 | Delay máximo |
| `AUTOTHROTTLE_TARGET_CONCURRENCY` | 2.0 | Concorrência alvo |

### **Configurações do Playwright:**

```python
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = 'chromium'
PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,
    'args': ['--no-sandbox', '--disable-dev-shm-usage']
}
```

---

## 💾 **PIPELINE: pipelines.py**

### **Classe: JsonWriterPipeline**

#### **Atributos:**
- `self.items`: Lista de itens coletados
- `self.lock`: Threading.Lock para thread safety
- `self.save_interval`: 100 (salva a cada 100 itens)

#### **Métodos:**

##### **process_item(item, spider)**
```python
def process_item(self, item, spider):
    with self.lock:
        self.items.append(ItemAdapter(item).asdict())
        
        # Save incrementally every 100 items
        if len(self.items) % self.save_interval == 0:
            self._save_items(spider)
            
    return item
```

##### **_save_items(spider)**
```python
def _save_items(self, spider):
    with open('output/fuel_stations.json', 'w', encoding='utf-8') as f:
        json.dump(self.items, f, ensure_ascii=False, indent=2)
    spider.logger.info(f"💾 Saved {len(self.items)} items")
```

---

## 📊 **ANÁLISE DE PERFORMANCE: performance_analyzer.py**

### **Classe: PerformanceAnalyzer**

#### **Métricas Coletadas:**
- `cells_processed`: Células processadas
- `establishments_found`: Estabelecimentos encontrados
- `unique_establishments`: Estabelecimentos únicos
- `duplicates_filtered`: Duplicatas filtradas
- `success_rate`: Taxa de sucesso (%)
- `processing_speed`: Velocidade (células/hora)
- `data_quality_score`: Score de qualidade dos dados

#### **Métodos Principais:**

##### **update_cell_progress(cell_data)**
- Atualiza progresso de uma célula
- Thread-safe com locks
- Salva em `output/scraping_progress.json`

##### **calculate_metrics()**
- Calcula métricas em tempo real
- Estima tempo de conclusão
- Avalia qualidade dos dados

---

## 🖥️ **INTERFACE: app.py**

### **Funcionalidades:**
- Dashboard em tempo real
- Botão "Iniciar Scraper"
- Contador de leads
- Gráficos de progresso
- Métricas detalhadas

### **Componentes Streamlit:**
- `st.metric()`: Métricas principais
- `st.progress()`: Barra de progresso
- `st.line_chart()`: Gráfico de velocidade
- `st.json()`: Dados em tempo real

---

## 🚨 **PROBLEMA CRÍTICO IDENTIFICADO**

### **❌ Perda de Dados ao Interromper:**

**Causa Raiz:**
1. Pipeline salva dados apenas no `close_spider()`
2. Ctrl+C mata o processo antes do `close_spider()` executar
3. Dados em memória se perdem

**Evidência:**
- Arquivo `output/fuel_stations.json` não existe após Ctrl+C
- Arquivo `output/scraping_progress.json` também se perde
- Apenas `output/scrapy.log` permanece

### **🔧 Tentativas de Solução:**

#### **1. Salvamento Incremental (IMPLEMENTADO)**
```python
# A cada 100 itens
if len(self.items) % self.save_interval == 0:
    self._save_items(spider)
```

#### **2. Thread Safety (IMPLEMENTADO)**
```python
with self.lock:
    self.items.append(item)
```

#### **3. Script de Restart (IMPLEMENTADO)**
- `restart_scraper.py` com backup automático
- Limpeza de cache
- Recuperação de progresso

### **❌ Status: PROBLEMA IDENTIFICADO**
- Spider está funcionando e coletando dados (logs mostram "scraped 837 items")
- Pipeline não está salvando os dados no arquivo
- Salvamento incremental e direto não funcionam
- Necessária correção urgente do sistema de salvamento

---

## 📋 **ESTRUTURA DOS DADOS**

### **Item Coletado:**
```json
{
  "name": "Posto Petrobras",
  "place_id": "cell_0_0_4881",
  "rating": null,
  "reviews_count": null,
  "category": "Gas Station",
  "address": "Santa Catarina, Brasil (lat: -29.3500, lon: -53.8300)",
  "link": null,
  "scraped_at": "2025-10-07T08:36:37.697333",
  "cell_lat": -29.35,
  "cell_lon": -53.83,
  "search_term": "gas station"
}
```

### **Progresso:**
```json
{
  "start_time": "2025-10-06T21:00:56.914255",
  "cells_processed": 8474,
  "total_cells": 16416,
  "establishments_found": 56542,
  "success_rate": 100.0,
  "processing_speed": 737.077467775421
}
```

---

## 🚀 **SCRIPTS DE EXECUÇÃO**

### **1. Execução Normal:**
```bash
python run_scraper.py
```

### **2. Execução com Restart:**
```bash
python restart_scraper.py
```

### **3. Teste Rápido:**
```bash
python test_simple.py
```

### **4. Interface Web:**
```bash
streamlit run app.py
```

### **5. Scrapy Direto:**
```bash
scrapy crawl simple_fuel
```

---

## 📈 **MÉTRICAS DE PERFORMANCE**

### **Resultados Anteriores:**
- **Células processadas:** 8.474 / 16.416 (51%)
- **Estabelecimentos:** 56.542 únicos
- **Taxa de sucesso:** 100%
- **Velocidade:** 737 células/hora
- **Tempo total:** ~10 horas de execução
- **Resultado:** ❌ DADOS PERDIDOS

### **Performance Esperada:**
- **Tempo total estimado:** 22-24 horas
- **Estabelecimentos esperados:** ~100.000+
- **Cobertura:** Santa Catarina completa
- **Qualidade:** >95% de dados válidos

---

## ⚠️ **PRÓXIMOS PASSOS CRÍTICOS**

### **1. RESOLVER PERDA DE DADOS (URGENTE)**
- Investigar por que salvamento incremental falha
- Implementar salvamento em arquivo separado
- Adicionar signal handlers para Ctrl+C

### **2. Melhorar Robustez**
- Checkpoint system mais robusto
- Recuperação automática de falhas
- Validação de dados em tempo real

### **3. Otimizações**
- Deduplicação mais eficiente
- Paralelização melhorada
- Cache de resultados

---

**📅 Última atualização:** 2025-10-07  
**🔧 Status:** SISTEMA FUNCIONAL MAS COM PERDA DE DADOS CRÍTICA  
**⚠️ Prioridade:** RESOLVER SALVAMENTO ANTES DE EXECUÇÃO LONGA
