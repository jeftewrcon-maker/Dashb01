"""
Histograma de Mão de Obra — Aplicativo Web (Streamlit)
"""
import os
import json
import tempfile
import streamlit as st
import streamlit.components.v1 as components

from data_processor import load_excel
from html_generator import generate_html

# ── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────
st.set_page_config(page_title="Histograma de Mão de Obra", layout="wide")

# ── ESTILIZAÇÃO (Mantendo sua paleta de cores original) ──────────────
st.markdown("""
    <style>
    .stApp { background-color: #0a0c10; color: #e2e8f0; }
    .info-card {
        background-color: #111418;
        padding: 14px 20px;
        border-radius: 4px;
        font-family: "Courier New", Courier, monospace;
        color: #94a3b8;
        margin-bottom: 20px;
        border-left: 4px solid #00d4ff;
    }
    .highlight { color: #00d4ff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ── CABEÇALHO ────────────────────────────────────────────────────────
st.markdown("<h1 style='color: #e2e8f0; font-family: Helvetica;'>⚡ Histograma de Mão de Obra</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-family: Helvetica;'>Sobreposição · Superlocação · Atrito entre Obras</p>", unsafe_allow_html=True)
st.markdown("<p style='color: #374151; font-size: 12px; font-family: Helvetica;'>Suporta colunas: OBRA · PERÍODO · QTD · FUNÇÃO</p>", unsafe_allow_html=True)
st.markdown("---")

# ── ÁREA DE UPLOAD ───────────────────────────────────────────────────
uploaded_file = st.file_uploader("📂 Arraste um arquivo Excel aqui ou clique para selecionar", type=["xlsx", "xls", "xlsm"])

if uploaded_file is not None:
    with st.spinner(f"Carregando: {uploaded_file.name} ..."):
        try:
            # 1. Salva o arquivo em disco temporariamente para que o load_excel() consiga ler o path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            # 2. Executa a sua lógica original
            data = load_excel(tmp_path)
            html_content = generate_html(data)

            # 3. Limpa o arquivo temporário do servidor
            os.unlink(tmp_path)

            st.success(f"✅ {uploaded_file.name} carregado com sucesso")

            # 4. Painel de Informações (Info Card) mantendo as suas formatações
            months_range = f"{data['months'][0]} → {data['months'][-1]}" if data.get('months') else '—'
            grand = f"{data['grand_total']:,}".replace(',', '.')

            st.markdown(f"""
            <div class="info-card">
                <b>Arquivo :</b> <span class="highlight">{uploaded_file.name}</span><br>
                <b>Obras   :</b> {data['num_obras']}   |   <b>Funções:</b> {len(data['funcoes'])}<br>
                <b>Período :</b> {months_range}   ({data['duration']} meses)<br>
                <b>Pico    :</b> {data['peak_total']} trab. em {data['peak_month']}<br>
                <b>Total   :</b> {grand} func-mês
            </div>
            """, unsafe_allow_html=True)

            # 5. Botões de Ação (Download HTML e Exportação JSON)
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                st.download_button(
                    label="💾 Salvar HTML",
                    data=html_content,
                    file_name="histograma_mao_de_obra.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col2:
                json_data = json.dumps(data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📋 Exportar JSON",
                    data=json_data,
                    file_name="histograma_data.json",
                    mime="application/json",
                    use_container_width=True
                )

            # 6. Exibição do Dashboard (Substitui a abertura em nova aba pelo navegador nativo)
            st.markdown("### 🌐 Visualização do Dashboard")
            components.html(html_content, height=800, scrolling=True)

        except Exception as e:
            st.error(f"❌ Não foi possível processar o arquivo:\n\n{str(e)}")
else:
    st.info("Nenhum arquivo carregado. Aguardando Excel...")
