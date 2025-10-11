#!/usr/bin/env python3
"""
Cria Excel completo com dados dos estabelecimentos
- Remove duplicatas por telefone
- Adiciona aniversários das cidades
- Permite filtrar por DDD
"""

import json
import pandas as pd
import re
from collections import defaultdict

def criar_dicionario_aniversarios():
    """Cria dicionário com aniversários das cidades de SC"""
    
    # Dados extraídos da Wikipedia e outras fontes
    aniversarios = {
        # Principais cidades
        'Florianópolis': '23/03',
        'Joinville': '09/03', 
        'Blumenau': '01/01',
        'São José': '01/03',
        'Chapecó': '25/08',
        'Criciúma': '04/11',
        'Itajaí': '15/06',
        'Lages': '22/11',
        'Palhoça': '24/04',
        'Balneário Camboriú': '08/04',
        
        # Outras cidades importantes
        'Tubarão': '27/05',
        'São Bento do Sul': '21/05',
        'Brusque': '23/03',
        'Jaraguá do Sul': '26/03',
        'Caçador': '25/03',
        'Concórdia': '12/07',
        'Rio do Sul': '10/10',
        'Laguna': '29/07',  # Estimativa baseada em fundação 1676
        'São Francisco do Sul': '12/08',  # Estimativa baseada em fundação 1658
        'Camboriú': '05/04',
        'Tijucas': '04/10',
        'Araquari': '05/04',
        'Araranguá': '03/04',
        'Campos Novos': '30/03',
        'São Joaquim': '28/08',
        'Imaruí': '27/08',
        'Jaguaruna': '06/01',
        'Nova Trento': '08/08',
        'Campo Alegre': '17/10',
        'Urussanga': '06/10',
        'Canoinhas': '03/09',
        'Orleans': '30/08',
        'Mafra': '25/08',
        'Porto União': '25/08',
        'Itaiópolis': '28/10',
        'Bom Retiro': '04/10',
        'Gaspar': '17/02',
        'Indaial': '28/02',
        'Timbó': '28/02',
        'Rodeio': '22/10',
        'Videira': '31/12',
        'Capinzal': '30/12',
        'Ituporanga': '30/12',
        'Massaranduba': '30/12',
        'Piratuba': '30/12',
        'Taió': '30/12',
        'Tangará': '30/12',
        'Turvo': '30/12',
        'Guaramirim': '18/08',
        'Herval d\'Oeste': '30/12',
        'Sombrio': '30/12',
        'Presidente Getúlio': '30/12',
        'Seara': '30/12',
        'Papanduva': '30/12',
        'Xanxerê': '30/12',
        'Xaxim': '30/12',
        'Dionísio Cerqueira': '30/12',
        'Mondaí': '30/12',
        'São Miguel do Oeste': '30/12',
        'São Carlos': '30/12',
        'Palmitos': '30/12',
        'Itapiranga': '30/12',
        'Rio Negrinho': '30/12',
        'Braço do Norte': '22/10',
        'Descanso': '12/09',
        'Itá': '13/11',
        'Vidal Ramos': '03/12',
        'Lauro Müller': '06/12',
        'Urubici': '06/12',
        'Santo Amaro da Imperatriz': '04/06',
        'Pomerode': '19/12',
        'Siderópolis': '19/12',
        'Lebon Régis': '19/12',
        'Armazém': '19/12',
        'Três Barras': '23/12',
        'Major Vieira': '23/12',
        'Anita Garibaldi': '17/07',
        'Campo Belo do Sul': '17/07',
        'Navegantes': '30/05',
        'Bombinhas': '30/03',
        'Porto Belo': '01/09',
        'Penha': '21/06',
        'Ilhota': '21/06',
        'Luiz Alves': '21/06',
        'Balneário Piçarras': '19/11',
        'Barra Velha': '07/12',
        'São João Batista': '21/06',
        'Angelina': '07/12',
        'Garopaba': '19/12',
        'Paulo Lopes': '20/12',
        'Águas Mornas': '19/12',
        'Anitápolis': '19/12',
        'São Bonifácio': '23/08',
        'Rancho Queimado': '08/11',
        'São Pedro de Alcântara': '16/04',
        'Governador Celso Ramos': '06/11',
        'Antônio Carlos': '06/11',
        'Biguaçu': '01/03',
        'Nova Veneza': '21/06',
        'Içara': '20/12',
        'Forquilhinha': '26/04',
        'Maracajá': '12/05',
        'Sangão': '30/03',
        'Morro da Fumaça': '30/03',
        'Cocal do Sul': '26/09',
        'Treviso': '08/07',
        'Jacinto Machado': '21/06',
        'Meleiro': '27/11',
        'Morro Grande': '30/03',
        'Ermo': '29/12',
        'Timbé do Sul': '11/05',
        'Praia Grande': '21/06',
        'São João do Sul': '20/12',
        'Passo de Torres': '26/09',
        'Santa Rosa do Sul': '04/01',
        'Balneário Gaivota': '29/12',
        'Balneário Arroio do Silva': '29/12',
        'Balneário Rincão': '03/10',
        'Pescaria Brava': '25/10'
    }
    
    return aniversarios

def extrair_ddd(telefone):
    """Extrai DDD do telefone"""
    if not telefone:
        return None
    
    # Remove caracteres não numéricos
    numeros = re.sub(r'[^\d]', '', telefone)
    
    # Se tem pelo menos 10 dígitos, pega os 2 primeiros como DDD
    if len(numeros) >= 10:
        return numeros[:2]
    
    return None

def extrair_cidade(endereco):
    """Extrai nome da cidade do endereço"""
    if not endereco:
        return "Não identificado"

    endereco = endereco.strip()

    # Se é formato de coordenadas, retorna "Santa Catarina"
    if 'lat:' in endereco and 'lon:' in endereco:
        return "Santa Catarina (coordenadas)"

    # Se contém "Santa Catarina, Brasil", retorna isso
    if 'Santa Catarina, Brasil' in endereco:
        return "Santa Catarina"

    # Padrões específicos para endereços reais
    # Formato: "Endereço, Cidade - SC" ou "Endereço, Cidade, SC"

    # Remove "SC" e "Santa Catarina" do final
    endereco_limpo = re.sub(r',?\s*(SC|Santa Catarina)\s*$', '', endereco, flags=re.IGNORECASE)

    # Divide por vírgulas e pega a última parte (geralmente a cidade)
    partes = [p.strip() for p in endereco_limpo.split(',') if p.strip()]

    if len(partes) >= 2:
        # Pega a última parte como cidade
        cidade = partes[-1].strip()
    elif len(partes) == 1:
        # Se só tem uma parte, pode ser só a cidade
        cidade = partes[0].strip()
    else:
        return "Não identificado"

    # Remove números, CEPs e caracteres especiais
    cidade = re.sub(r'\d{5}-?\d{3}', '', cidade)  # Remove CEP
    cidade = re.sub(r'^\d+\s*', '', cidade)       # Remove números do início
    cidade = re.sub(r'\s*-\s*$', '', cidade)      # Remove hífen do final
    cidade = cidade.strip()

    # Se ficou muito pequeno ou tem muitos números, provavelmente não é cidade
    if len(cidade) < 3 or re.search(r'\d{3,}', cidade):
        return "Não identificado"

    return cidade if cidade else "Não identificado"

def processar_dados():
    """Processa dados e cria Excel"""
    
    print('📊 CRIANDO EXCEL COMPLETO DOS ESTABELECIMENTOS')
    print('=' * 60)
    
    # Carregar dados do arquivo principal
    arquivo_principal = 'output/fuel_stations_auto_complete.json'
    
    try:
        with open(arquivo_principal, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        print(f'✅ Carregados {len(dados):,} estabelecimentos do arquivo principal')
        
    except Exception as e:
        print(f'❌ Erro ao carregar dados: {e}')
        return
    
    # Dicionário de aniversários
    aniversarios = criar_dicionario_aniversarios()
    print(f'📅 Carregados aniversários de {len(aniversarios)} cidades')
    
    # Processar dados
    dados_processados = []
    telefones_vistos = set()
    duplicatas_removidas = 0
    
    for item in dados:
        # Verificar se item é válido
        if not item or not isinstance(item, dict):
            continue

        telefone = item.get('phone') or ''
        if isinstance(telefone, str):
            telefone = telefone.strip()
        else:
            telefone = str(telefone).strip() if telefone else ''

        # Pular se não tem telefone
        if not telefone:
            continue

        # Verificar duplicata por telefone
        if telefone in telefones_vistos:
            duplicatas_removidas += 1
            continue

        telefones_vistos.add(telefone)

        # Extrair informações com verificação de tipo
        nome = item.get('name') or ''
        if isinstance(nome, str):
            nome = nome.strip()
        else:
            nome = str(nome).strip() if nome else ''

        endereco = item.get('address') or ''
        if isinstance(endereco, str):
            endereco = endereco.strip()
        else:
            endereco = str(endereco).strip() if endereco else ''

        cidade = extrair_cidade(endereco)
        ddd = extrair_ddd(telefone)

        link = item.get('link') or ''
        if isinstance(link, str):
            link = link.strip()
        else:
            link = str(link).strip() if link else ''
        
        # Buscar aniversário da cidade
        aniversario = aniversarios.get(cidade, 'Não encontrado')
        
        dados_processados.append({
            'Nome': nome,
            'Cidade': cidade,
            'Endereço': endereco,
            'Telefone': telefone,
            'DDD': ddd,
            'Link': link,
            'Aniversário da Cidade': aniversario,
            'Rating': item.get('rating', ''),
            'Reviews': item.get('reviews_count', ''),
            'Website': item.get('website', ''),
            'Categoria': item.get('category', ''),
            'Horário': item.get('hours', ''),
            'Place ID': item.get('place_id', ''),
            'Coletado em': item.get('scraped_at', ''),
            'Coordenadas': f"{item.get('cell_lat', '')}, {item.get('cell_lon', '')}"
        })
    
    print(f'🔄 Processados {len(dados_processados):,} estabelecimentos únicos')
    print(f'🗑️ Removidas {duplicatas_removidas:,} duplicatas por telefone')
    
    # Criar DataFrame
    df = pd.DataFrame(dados_processados)
    
    # Estatísticas por DDD
    ddd_stats = df['DDD'].value_counts().head(10)
    print(f'\n📞 TOP 10 DDDs:')
    for ddd, count in ddd_stats.items():
        print(f'   {ddd}: {count:,} estabelecimentos')
    
    # Estatísticas por cidade
    cidade_stats = df['Cidade'].value_counts().head(10)
    print(f'\n🏙️ TOP 10 CIDADES:')
    for cidade, count in cidade_stats.items():
        print(f'   {cidade}: {count:,} estabelecimentos')
    
    # Salvar Excel
    arquivo_excel = 'output/estabelecimentos_completo.xlsx'
    
    with pd.ExcelWriter(arquivo_excel, engine='openpyxl') as writer:
        # Planilha principal
        df.to_excel(writer, sheet_name='Estabelecimentos', index=False)
        
        # Planilha de estatísticas
        stats_data = {
            'Métrica': [
                'Total de estabelecimentos únicos',
                'Duplicatas removidas por telefone',
                'Estabelecimentos com cidade identificada',
                'Estabelecimentos com DDD identificado',
                'Cidades com aniversário conhecido',
                'DDDs únicos encontrados'
            ],
            'Valor': [
                len(dados_processados),
                duplicatas_removidas,
                len(df[df['Cidade'].notna()]),
                len(df[df['DDD'].notna()]),
                len(df[df['Aniversário da Cidade'] != 'Não encontrado']),
                len(df['DDD'].unique())
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
        
        # Planilha de DDDs
        ddd_df = pd.DataFrame({
            'DDD': ddd_stats.index,
            'Quantidade': ddd_stats.values
        })
        ddd_df.to_excel(writer, sheet_name='Por DDD', index=False)
        
        # Planilha de cidades
        cidade_df = pd.DataFrame({
            'Cidade': cidade_stats.index,
            'Quantidade': cidade_stats.values
        })
        cidade_df.to_excel(writer, sheet_name='Por Cidade', index=False)
    
    print(f'\n✅ Excel criado: {arquivo_excel}')
    print(f'📊 {len(dados_processados):,} estabelecimentos únicos')
    print(f'🗑️ {duplicatas_removidas:,} duplicatas removidas')
    print(f'📞 {len(df["DDD"].unique())} DDDs diferentes')
    print(f'🏙️ {len(df["Cidade"].unique())} cidades diferentes')
    
    return arquivo_excel, len(dados_processados), duplicatas_removidas

if __name__ == "__main__":
    processar_dados()
