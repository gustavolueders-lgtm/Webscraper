import streamlit as st
import subprocess
import json
import os
import time
import threading
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Google Maps Fuel Stations Scraper",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variables
PROGRESS_FILE = 'output/scraping_progress.json'
RESULTS_FILE = 'output/fuel_stations.json'
CHECKPOINT_FILE = 'output/grid_checkpoint.json'

def load_progress():
    """Load scraping progress from file"""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def load_results_count():
    """Load current results count"""
    try:
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data) if isinstance(data, list) else 0
    except:
        pass
    return 0

def is_scraper_running():
    """Check if scraper is currently running"""
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        return 'scrapy' in result.stdout.lower()
    except:
        return False

def start_scraper():
    """Start the scraper in background"""
    try:
        # Change to project directory and run scrapy
        cmd = ['scrapy', 'crawl', 'simple_fuel']
        subprocess.Popen(cmd, cwd=os.getcwd(), shell=True)
        return True
    except Exception as e:
        st.error(f"Error starting scraper: {str(e)}")
        return False

def stop_scraper():
    """Stop the scraper"""
    try:
        # Kill python processes running scrapy
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], shell=True)
        return True
    except Exception as e:
        st.error(f"Error stopping scraper: {str(e)}")
        return False

def clear_cache():
    """Clear all cache and output files"""
    files_to_remove = [
        PROGRESS_FILE,
        RESULTS_FILE,
        CHECKPOINT_FILE,
        'output/scrapy.log',
        'output/metrics.json'
    ]
    
    removed_count = 0
    for file_path in files_to_remove:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                removed_count += 1
        except:
            pass
    
    # Clear scrapy cache
    try:
        import shutil
        if os.path.exists('.scrapy'):
            shutil.rmtree('.scrapy')
            removed_count += 1
    except:
        pass
    
    return removed_count

# Main interface
def main():
    st.title("⛽ Google Maps Fuel Stations Scraper")
    st.markdown("**Otimizado para Santa Catarina - Grid 5x5km**")
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎛️ Controles")
        
        # Clear cache button
        if st.button("🧹 Limpar Cache", type="secondary", use_container_width=True):
            removed = clear_cache()
            st.success(f"Cache limpo! {removed} arquivos removidos.")
            time.sleep(1)
            st.rerun()
        
        st.divider()
        
        # Scraper controls
        scraper_running = is_scraper_running()
        
        if not scraper_running:
            if st.button("🚀 Iniciar Scraper", type="primary", use_container_width=True):
                if start_scraper():
                    st.success("Scraper iniciado!")
                    time.sleep(2)
                    st.rerun()
        else:
            st.success("✅ Scraper em execução")
            if st.button("⏹️ Parar Scraper", type="secondary", use_container_width=True):
                if stop_scraper():
                    st.success("Scraper parado!")
                    time.sleep(2)
                    st.rerun()
        
        st.divider()
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh (5s)", value=True)
        
        if auto_refresh:
            time.sleep(5)
            st.rerun()
    
    # Main content
    progress_data = load_progress()
    results_count = load_results_count()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Leads Capturados",
            value=results_count,
            delta=f"+{results_count}" if results_count > 0 else None
        )
    
    with col2:
        cells_processed = progress_data.get('cells_processed', 0)
        total_cells = progress_data.get('total_cells', 0)
        progress_pct = (cells_processed / max(total_cells, 1)) * 100
        st.metric(
            label="🗺️ Progresso Grid",
            value=f"{cells_processed}/{total_cells}",
            delta=f"{progress_pct:.1f}%" if total_cells > 0 else None
        )
    
    with col3:
        success_rate = progress_data.get('success_rate', 0)
        st.metric(
            label="✅ Taxa de Sucesso",
            value=f"{success_rate:.1f}%",
            delta="Boa" if success_rate > 80 else "Atenção" if success_rate > 60 else "Baixa"
        )
    
    with col4:
        processing_speed = progress_data.get('processing_speed', 0)
        st.metric(
            label="⚡ Velocidade",
            value=f"{processing_speed:.1f} células/h",
            delta="Rápido" if processing_speed > 50 else "Normal" if processing_speed > 20 else "Lento"
        )
    
    # Progress bar
    if total_cells > 0:
        st.progress(progress_pct / 100, text=f"Progresso geral: {progress_pct:.1f}%")
    
    # Detailed information
    if progress_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Estatísticas Detalhadas")
            
            stats_data = {
                "Estabelecimentos únicos": progress_data.get('unique_establishments', 0),
                "Duplicatas filtradas": progress_data.get('duplicates_filtered', 0),
                "Células com resultados": progress_data.get('cells_with_results', 0),
                "Células vazias": progress_data.get('cells_empty', 0),
                "Média por célula": f"{progress_data.get('average_establishments_per_cell', 0):.1f}",
                "Bloqueios detectados": progress_data.get('blocks_detected', 0),
                "Erros": progress_data.get('errors_count', 0),
                "Score de qualidade": f"{progress_data.get('data_quality_score', 0):.1f}%"
            }
            
            for key, value in stats_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("⏱️ Informações de Tempo")
            
            start_time = progress_data.get('start_time')
            if start_time:
                start_dt = datetime.fromisoformat(start_time)
                elapsed = datetime.now() - start_dt
                st.write(f"**Iniciado em:** {start_dt.strftime('%d/%m/%Y %H:%M:%S')}")
                st.write(f"**Tempo decorrido:** {str(elapsed).split('.')[0]}")
            
            estimated_completion = progress_data.get('estimated_completion_time')
            if estimated_completion:
                completion_dt = datetime.fromisoformat(estimated_completion)
                remaining = completion_dt - datetime.now()
                if remaining.total_seconds() > 0:
                    st.write(f"**Conclusão estimada:** {completion_dt.strftime('%d/%m/%Y %H:%M:%S')}")
                    st.write(f"**Tempo restante:** {str(remaining).split('.')[0]}")
                else:
                    st.write("**Status:** Concluído!")
    
    # Charts section
    if progress_data and progress_data.get('cells_details'):
        st.subheader("📊 Gráficos de Performance")
        
        # Create charts from cells details
        cells_df = pd.DataFrame(progress_data['cells_details'])
        
        if not cells_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Success rate over time
                cells_df['success_numeric'] = cells_df['success'].astype(int)
                fig1 = px.line(cells_df, x='index', y='success_numeric', 
                              title='Taxa de Sucesso por Célula')
                fig1.update_yaxis(title='Sucesso (1=Sim, 0=Não)')
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Establishments found per cell
                fig2 = px.bar(cells_df.head(50), x='index', y='establishments_found',
                             title='Estabelecimentos por Célula (Primeiras 50)')
                fig2.update_yaxis(title='Estabelecimentos Encontrados')
                st.plotly_chart(fig2, use_container_width=True)
    
    # Footer
    st.divider()
    st.markdown("""
    **🎯 Configurações Otimizadas:**
    - Grid 5x5km em Santa Catarina
    - 2 termos por célula: "gas station" + "posto de combustível"  
    - Extração direta dos cards (sem visitar páginas individuais)
    - Paralelização conservadora (2 requests simultâneos)
    - Sistema de pausas programadas
    - Detecção automática de bloqueios
    - Salvamento incremental a cada 50 itens
    """)

if __name__ == "__main__":
    main()
