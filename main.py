"""
Histograma de Mão de Obra — Streamlit App
Requer: pip install streamlit pandas openpyxl
"""
import streamlit as st
import tempfile
import os
import json
import webbrowser

from data_processor import load_excel
from html_generator import generate_html

# ── CONFIGURAÇÃO DA PÁGINA ──────────────────────────────────────────
st.set_page_config(
    page_title="Histograma de Mão de Obra",
    page_icon="⚡",
    layout="wide"
)

# ── CABEÇALHO ───────────────────────────────────────────────────────
st.title("⚡ Histograma de Mão de Obra")
st.markdown("**Sobreposição · Superlocação · Atrito entre Obras**")
st.caption("Suporta colunas: OBRA · PERÍODO · QTD · FUNÇÃO")

# ── ÁREA DE UPLOAD ──────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📂 Arraste um arquivo Excel aqui ou clique para selecionar", 
    type=["xlsx", "xls", "xlsm"]
)

if uploaded_file is not None:
    with st.spinner("Processando dados e gerando dashboard..."):
        # 1. Salva o arquivo de forma segura para evitar bloqueios do Windows
        temp_dir = tempfile.gettempdir()
        tmp_excel_path = os.path.join(temp_dir, "temp_histograma_upload.xlsx")
        
        with open(tmp_excel_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # 2. Carrega dados e gera HTML usando a sua lógica original definida
            data = load_excel(tmp_excel_path)
            html = generate_html(data)

            st.success(f"✅ Arquivo `{uploaded_file.name}` processado com sucesso!")

            # ── MÉTRICAS (INFO CARD) ────────────────────────────────
            st.markdown("### Resumo do Projeto")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            months_range = f"{data['months'][0]} → {data['months'][-1]}" if data.get('months') else '—'
            grand = f"{data['grand_total']:,}".replace(',', '.')

            col1.metric("Obras", data['num_obras'])
            col2.metric("Funções", len(data['funcoes']))
            col3.metric("Duração", f"{data['duration']} meses", help=months_range)
            col4.metric("Pico de Trab.", f"{data['peak_total']}", help=f"Ocorreu em: {data['peak_month']}")
            col5.metric("Total Func-mês", grand)

            st.divider()

            # ── AÇÕES / EXPORTAÇÃO ──────────────────────────────────
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            
            with col_btn1:
                # Restaura o comportamento original do seu código: abrir fora do iframe
                if st.button("🌐 Abrir no Navegador (Tela Cheia)", use_container_width=True):
                    tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
                    tmp_html.write(html)
                    tmp_html.close()
                    webbrowser.open(f"file://{tmp_html.name}")
                    
            with col_btn2:
                st.download_button(
                    label="💾 Salvar HTML",
                    data=html,
                    file_name="histograma_mao_de_obra.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col_btn3:
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📋 Exportar JSON",
                    data=json_str,
                    file_name="histograma_data.json",
                    mime="application/json",
                    use_container_width=True
                )

            st.divider()

            # ── PREVIEW DO DASHBOARD ───────────────────────────────
            st.markdown("### 🔍 Preview do Dashboard")
            st.info("Caso os gráficos não apareçam no preview abaixo (devido a bloqueios do Streamlit), utilize o botão **'🌐 Abrir no Navegador'** acima para visualizar perfeitamente.")
            
            # Tenta renderizar o HTML gerado dentro do Streamlit
            st.components.v1.html(html, height=800, scrolling=True)

        except Exception as exc:
            st.error(f"❌ Erro ao processar o arquivo:\n\n{exc}")
        finally:
            # Garante a limpeza do arquivo Excel temporário
            if os.path.exists(tmp_excel_path):
                try:
                    os.remove(tmp_excel_path)
                except Exception:
                    pass
