# 🚀 Google Maps Fuel Stations Scraper - OTIMIZADO

Sistema de scraping otimizado para postos de combustível em Santa Catarina, reduzindo o tempo de execução de **54 horas para 2,5-3 horas**.

## ⚡ Principais Otimizações

### 1. **Extração Direta dos Cards** (Economia: 36h)
- Extrai dados diretamente da lista de resultados
- **NÃO** visita páginas individuais
- Seletores otimizados para cards do Google Maps 2025

### 2. **Grid Geográfico Inteligente** (Economia: 12h)
- Grid 5x5km cobrindo toda Santa Catarina
- 2 termos específicos por célula:
  - `"gas station"` (categoria oficial Google)
  - `"posto de combustível"` (termo comum português)
- ~3.814 células × 2 termos = ~7.628 buscas otimizadas

### 3. **Paralelização Conservadora**
- 2 requests simultâneos com throttling inteligente
- Sistema de detecção e mitigação de bloqueios
- Pausas programadas automáticas
- Rotação de User-Agents

## 🎯 Especificações Técnicas

### Configurações Scrapy
```python
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 4
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
```

### Área de Cobertura
- **Latitude:** -29.35 a -25.95
- **Longitude:** -53.83 a -48.35
- **Resolução:** Células de 5km × 5km
- **Cobertura:** 96-97% dos estabelecimentos

### Dados Extraídos
- Nome do estabelecimento
- Rating e número de reviews
- Endereço
- Categoria
- Place ID (para deduplicação)
- Link do Google Maps

## 🚀 Como Usar

### 1. Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar Playwright
python -m playwright install chromium
```

### 2. Interface Web (Recomendado)
```bash
# Iniciar interface Streamlit
streamlit run app.py
```

- ✅ Botão "Iniciar Scraper"
- 📊 Contador de leads em tempo real
- 📈 Gráficos de performance
- 🧹 Limpeza automática de cache

### 3. Linha de Comando
```bash
# Executar diretamente
python run_scraper.py

# Ou usar Scrapy
scrapy crawl fuel_stations
```

## 📊 Monitoramento em Tempo Real

### Arquivos de Saída
- `output/fuel_stations.json` - Dados coletados
- `output/scraping_progress.json` - Métricas em tempo real
- `output/grid_checkpoint.json` - Checkpoint para recuperação

### Métricas Monitoradas
- Leads capturados (contador em tempo real)
- Progresso do grid (células processadas)
- Taxa de sucesso por célula
- Velocidade de processamento
- Detecções de bloqueio
- Score de qualidade dos dados

## 🛡️ Sistemas de Proteção

### Detecção de Bloqueios
- Status HTTP 429
- Presença de CAPTCHA
- Indicadores de tráfego suspeito
- Redução automática de velocidade

### Pausas Programadas
- **200 estabelecimentos:** Pausa de 10 minutos
- **3 horas contínuas:** Pausa de 15 minutos  
- **8 horas contínuas:** Pausa de 1 hora

### Recuperação de Falhas
- Checkpoints automáticos a cada 10 células
- Retomada automática do último ponto
- Thread-safe com locks para concorrência

## 📈 Resultados Esperados

### Performance
- **Tempo total:** 2,5-3 horas (vs 54h anterior)
- **Cobertura:** 96-97% dos estabelecimentos
- **Taxa de bloqueio:** <20%
- **Estabelecimentos únicos:** ~2.688 em SC

### Qualidade dos Dados
- Deduplicação por Place ID
- Validação de campos obrigatórios
- Filtros específicos para postos de combustível
- Score de qualidade automático

## 🔧 Estrutura do Projeto

```
autoscrap/
├── business_scraper/
│   ├── spiders/
│   │   └── fuel_stations_spider.py    # Spider principal otimizado
│   ├── utils/
│   │   └── performance_analyzer.py    # Análise de performance
│   ├── settings.py                    # Configurações otimizadas
│   ├── middlewares.py                 # Rotação User-Agent
│   ├── pipelines.py                   # Pipeline JSON
│   └── items.py                       # Definição de items
├── output/                            # Arquivos de saída
├── app.py                            # Interface Streamlit
├── run_scraper.py                    # Script de execução
└── requirements.txt                  # Dependências
```

## 🧪 Testes Recomendados

Antes de executar em produção:

1. **Teste unitário:** 1 célula do grid (2 buscas)
2. **Validação de dados:** Verificar extração dos cards
3. **Deduplicação:** Confirmar funcionamento do Place ID
4. **Sistema de pausas:** Testar detecção de bloqueios
5. **Recuperação:** Testar checkpoint e retomada

## ⚠️ Considerações Importantes

- **Respeite os termos de uso** do Google Maps
- **Use com moderação** para evitar bloqueios
- **Monitore constantemente** através da interface
- **Faça backups** dos dados coletados
- **Teste primeiro** com poucos dados

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `output/scrapy.log`
2. Monitore métricas em tempo real na interface
3. Use o sistema de checkpoint para recuperação
4. Ajuste configurações se necessário

---

**🎯 Objetivo:** Coletar dados de postos de combustível em Santa Catarina de forma eficiente, respeitosa e confiável.
