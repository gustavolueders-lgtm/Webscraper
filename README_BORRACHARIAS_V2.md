# 🔧 Sistema de Scraping de Borracharias - Santa Catarina v2

Sistema completo e otimizado para coleta de dados de borracharias em todo o estado de Santa Catarina usando Scrapy + Playwright.

## 🎯 Resultados Obtidos

- **✅ Cobertura**: 100% do estado de Santa Catarina (7.904 células de 5km x 5km)
- **🔧 Borracharias**: 2.405 estabelecimentos únicos coletados
- **📞 Contatos**: 1.885 com telefone (78.4%)
- **🚫 Deduplicação**: 96.8% de duplicatas removidas (72.215 de 74.620)
- **📊 Formato**: Excel organizado com múltiplas abas

## 🚀 Principais Melhorias da V2

### **⚡ Performance Otimizada**
- Remoção de sleeps desnecessários entre requisições
- Configurações otimizadas (DOWNLOAD_DELAY=1, CONCURRENT_REQUESTS=2)
- Pausas estratégicas apenas a cada 10 células

### **🔄 Sistema de Resume**
- Capacidade de continuar de qualquer célula específica
- Recuperação automática após interrupções
- Controle de progresso em tempo real

### **💾 Salvamento Automático**
- Deduplicação em tempo real (O(1) lookup)
- Salvamento contínuo a cada 2 segundos
- Sistema de backup automático

### **🎛️ Controle de Processos**
- Scripts de start/stop/status
- Monitoramento de progresso
- Gerenciamento de PIDs

## 📁 Estrutura dos Arquivos

### **🕷️ Spiders**
- `borracharia_resumable.py` - Spider principal com resume
- `borracharia_vpn_spider.py` - Spider baseado no VPN funcionando
- `simple_tire_spider.py` - Spider simplificado
- `tire_shops_spider.py` - Spider original

### **🎛️ Controle**
- `controle_scraping.py` - Controle principal (start/stop/status)
- `iniciar_rapido.py` - Inicialização rápida otimizada
- `iniciar_sistema_completo.py` - Inicialização completa
- `parar_sistema_completo.py` - Parada segura de todos os processos

### **💾 Salvamento**
- `salvamento_automatico_borracharias.py` - Sistema de salvamento automático
- `verificar_status_borracharias.py` - Verificação de status e progresso

### **📊 Processamento**
- `gerar_excel_borracharias.py` - Geração de Excel dos dados salvos
- `processar_todos_logs.py` - Processamento completo dos logs

## 🚀 Como Usar

### **1. Iniciar Sistema Completo**
```bash
# Inicialização rápida (recomendado)
python iniciar_rapido.py

# Ou especificar célula inicial
python iniciar_rapido.py 1500

# Ou inicialização completa
python iniciar_sistema_completo.py
```

### **2. Monitorar Progresso**
```bash
# Status do scraping
python controle_scraping.py status

# Status detalhado
python verificar_status_borracharias.py
```

### **3. Controlar Execução**
```bash
# Parar tudo
python parar_sistema_completo.py

# Ou controle individual
python controle_scraping.py stop
```

### **4. Gerar Excel**
```bash
# Excel dos dados salvos
python gerar_excel_borracharias.py

# Excel completo dos logs
python processar_todos_logs.py
```

## 📊 Estrutura do Excel Gerado

### **📋 Aba "Borracharias"**
- **nome**: Nome da borracharia
- **cidade**: Cidade extraída do endereço
- **endereco**: Endereço completo
- **telefone**: Telefone formatado
- **ddd**: DDD extraído
- **link**: Link do Google Maps
- **avaliacao**: Nota de avaliação
- **num_avaliacoes**: Número de avaliações
- **categoria**: Categoria do estabelecimento
- **website**: Site da empresa
- **horario**: Horário de funcionamento
- **place_id**: ID único do Google Maps
- **latitude/longitude**: Coordenadas
- **data_coleta**: Data e hora da coleta

### **📊 Aba "Estatísticas"**
- Resumo completo dos dados
- Métricas de qualidade
- Data de geração

### **🏙️ Aba "Por Cidade"**
- Distribuição por cidade
- Quantidade por localidade

## 🔧 Configurações Técnicas

### **Grid de Cobertura**
- **Tamanho**: 5km x 5km por célula
- **Área**: Santa Catarina completo
- **Coordenadas**: LAT -29.35 a -25.95, LON -53.83 a -48.35
- **Total**: 7.904 células

### **Deduplicação**
- **Chave única**: nome + telefone (ou nome + endereço se sem telefone)
- **Algoritmo**: O(1) lookup com Python set()
- **Cache**: Populado na inicialização
- **Eficiência**: 96.8% de duplicatas removidas

### **Performance**
- **DOWNLOAD_DELAY**: 1 segundo
- **CONCURRENT_REQUESTS**: 2
- **AUTOTHROTTLE**: Habilitado
- **Pausas estratégicas**: 30-60s a cada 10 células

## 📈 Monitoramento

### **Status em Tempo Real**
```
📊 Status: 2405 borracharias | Grid: 7904/7904 células (100.0%) | 🚫 Duplicatas: 72,215 - 12:22:15
```

### **Arquivos de Controle**
- `output/scraping.pid` - PID do processo
- `output/scraping_status.json` - Status atual
- `output/tire_shops_auto_complete.json` - Dados principais
- `output/tire_shops_auto_backup.json` - Backup automático

## 🎉 Resultados Finais

- **📊 Total coletado**: 74.620 registros nos logs
- **✅ Únicos salvos**: 2.405 borracharias
- **🚫 Duplicatas removidas**: 72.215 (96.8%)
- **📞 Com telefone**: 1.885 (78.4%)
- **🌐 Com link Google**: 2.405 (100%)
- **📁 Arquivo final**: `borracharias_santa_catarina_COMPLETO_*.xlsx`

## 🔄 Diferenças da V1

- **Performance**: 10x mais rápido (remoção de sleeps)
- **Resume**: Capacidade de continuar de qualquer ponto
- **Deduplicação**: Sistema em tempo real vs pós-processamento
- **Controle**: Scripts automatizados vs manual
- **Monitoramento**: Progresso em tempo real
- **Excel**: Formatação profissional com múltiplas abas
- **Cobertura**: 100% do estado vs parcial
