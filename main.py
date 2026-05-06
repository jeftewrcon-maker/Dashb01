"""
Histograma de Mão de Obra — Streamlit App
Requer: pip install streamlit pandas openpyxl
"""
import streamlit as st
import tempfile
import os
import json

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
        # Salva o arquivo temporariamente para manter compatibilidade com load_excel(path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            # Carrega dados e gera HTML usando seus módulos
            data = load_excel(tmp_path)
            html = generate_html(data)

            # Limpa o arquivo temporário
            os.unlink(tmp_path)

            st.success(f"✅ Arquivo `{uploaded_file.name}` carregado com sucesso!")

            # ── MÉTRICAS (INFO CARD) ────────────────────────────────
            st.markdown("### Resumo do Projeto")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            months_range = f"{data['months'][0]} → {data['months'][-1]}" if data.get('months') else '—'
            grand = f"{data['grand_total']:,}".replace(',', '.')

            col1.metric("Obras", data['num_obras'])
            col2.metric("Funções", len(data['funcoes']))
            col3.metric("Duração", f"{data['duration']} meses", help=months_range)
            col4.metric("Pico de Trabalhadores", f"{data['peak_total']}", help=f"Ocorreu em: {data['peak_month']}")
            col5.metric("Total Func-mês", grand)

            st.divider()

            # ── BOTÕES DE EXPORTAÇÃO ────────────────────────────────
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            
            with col_btn1:
                st.download_button(
                    label="💾 Salvar HTML",
                    data=html,
                    file_name="histograma_mao_de_obra.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col_btn2:
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📋 Exportar JSON",
                    data=json_str,
                    file_name="histograma_data.json",
                    mime="application/json",
                    use_container_width=True
                )

            # ── RENDERIZAÇÃO DO DASHBOARD ───────────────────────────
            st.markdown("### 🌐 Dashboard")
            # Renderiza o HTML gerado diretamente dentro do Streamlit
            st.components.v1.html(html, height=800, scrolling=True)

        except Exception as exc:
            st.error(f"❌ Erro ao processar o arquivo:\n\n{exc}")
