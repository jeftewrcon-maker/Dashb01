"""
Histograma de Mão de Obra — Streamlit
Requer: pip install streamlit pandas openpyxl
Executar: streamlit run main_streamlit.py
"""
import json
import streamlit as st
from pathlib import Path

from data_processor import load_excel
from html_generator import generate_html

# ── PAGE CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Histograma de Mão de Obra",
    page_icon="⚡",
    layout="wide",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0a0c10; }
  [data-testid="stHeader"] { background: transparent; }
  section[data-testid="stSidebar"] { background: #111418; border-right: 1px solid #1e2530; }
  .block-container { padding-top: 1.5rem; }

  /* Title area */
  .hmo-title { font-size: 22px; font-weight: 700; color: #e2e8f0;
    font-family: Verdana, sans-serif; letter-spacing: -.5px; }
  .hmo-sub { font-size: 12px; color: #64748b; font-family: Verdana, sans-serif;
    margin-top: 2px; }

  /* KPI cards */
  .kpi-row { display: flex; gap: 14px; margin-bottom: 20px; }
  .kpi-card { flex: 1; background: #111418; border: 1px solid #1e2530;
    border-radius: 12px; padding: 18px 20px; position: relative; overflow: hidden; }
  .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; background: linear-gradient(90deg,#00d4ff,#7c3aed); opacity: .6; }
  .kpi-label { font-size: 11px; color: #64748b; letter-spacing: .5px;
    text-transform: uppercase; margin-bottom: 8px; font-family: Verdana, sans-serif; }
  .kpi-value { font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 1; }
  .kpi-sub { font-size: 11px; color: #64748b; margin-top: 6px;
    font-family: Verdana, sans-serif; }
  .kpi-icon { position: absolute; right: 16px; top: 50%; transform: translateY(-50%);
    font-size: 28px; opacity: .08; }

  /* Info box */
  .info-box { background: #111418; border: 1px solid #1e2530; border-radius: 10px;
    padding: 14px 18px; font-family: 'Courier New', monospace; font-size: 12px;
    color: #94a3b8; line-height: 1.8; margin-bottom: 16px; }

  /* Buttons */
  div[data-testid="stDownloadButton"] button {
    background: #1e2530; color: #f59e0b; border: 1px solid #f59e0b;
    font-weight: 600; border-radius: 8px; padding: 6px 18px;
    font-family: Verdana, sans-serif; transition: all .2s;
  }
  div[data-testid="stDownloadButton"] button:hover {
    background: #f59e0b; color: #000;
  }
  stFileUploader { background: #111418; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hmo-title">⚡ Histograma</div>', unsafe_allow_html=True)
    st.markdown('<div class="hmo-sub">Mão de Obra · Sobreposição · Atrito</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    uploaded = st.file_uploader(
        "📂 Importar planilha Excel",
        type=["xlsx", "xls", "xlsm"],
        help="Colunas esperadas: OBRA · PERÍODO · QTD · FUNÇÃO (e opcionalmente CIDADE)"
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:10px;color:#374151;font-family:Verdana,sans-serif;'>"
        "Suporta: OBRA · PERÍODO · QTD · FUNÇÃO · CIDADE</div>",
        unsafe_allow_html=True
    )

# ── MAIN AREA ─────────────────────────────────────────────────────────
st.markdown('<div class="hmo-title">⚡ Histograma de Mão de Obra</div>', unsafe_allow_html=True)
st.markdown('<div class="hmo-sub">Sobreposição · Superlocação · Atrito entre Obras</div>',
            unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if uploaded is None:
    st.info("👈  Faça o upload de uma planilha Excel na barra lateral para começar.")
    st.stop()

# ── PROCESS FILE ──────────────────────────────────────────────────────
@st.cache_data(show_spinner="Processando planilha…")
def process(file_bytes: bytes, filename: str):
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        data = load_excel(tmp_path)
        html = generate_html(data)
    finally:
        os.unlink(tmp_path)
    return data, html

try:
    data, html = process(uploaded.read(), uploaded.name)
except Exception as e:
    st.error(f"❌ Erro ao processar o arquivo:\n\n{e}")
    st.stop()

# ── KPI CARDS ─────────────────────────────────────────────────────────
grand_fmt = f"{data['grand_total']:,}".replace(",", ".")
months_range = f"{data['months'][0]} → {data['months'][-1]}" if data['months'] else "—"

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">Pico Total</div>
    <div class="kpi-value" style="color:#00d4ff">{data['peak_total']}</div>
    <div class="kpi-sub">{data['peak_month']} — máximo histórico</div>
    <div class="kpi-icon">📈</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Obras no Portfolio</div>
    <div class="kpi-value" style="color:#f59e0b">{data['num_obras']}</div>
    <div class="kpi-sub">sobreposição ativa</div>
    <div class="kpi-icon">🏗️</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Func-Mês</div>
    <div class="kpi-value" style="color:#7c3aed">{grand_fmt}</div>
    <div class="kpi-sub">acumulado geral</div>
    <div class="kpi-icon">👷</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Duração</div>
    <div class="kpi-value" style="color:#10b981">{data['duration']}</div>
    <div class="kpi-sub">meses · {months_range}</div>
    <div class="kpi-icon">📅</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FILE INFO ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="info-box">
  &nbsp; Arquivo : {uploaded.name}<br>
  &nbsp; Obras   : {data['num_obras']} &nbsp;|&nbsp; Funções : {len(data['funcoes'])}<br>
  &nbsp; Período : {months_range} &nbsp;({data['duration']} meses)<br>
  &nbsp; Pico    : {data['peak_total']} trab. em {data['peak_month']}<br>
  &nbsp; Total   : {grand_fmt} func-mês
</div>
""", unsafe_allow_html=True)

# ── DASHBOARD EMBED ───────────────────────────────────────────────────
st.markdown("### 🌐 Dashboard Interativo")
st.markdown(
    "<div style='font-size:11px;color:#64748b;margin-bottom:8px;font-family:Verdana,sans-serif;'>"
    "O dashboard completo está incorporado abaixo — todos os filtros, Gantt, Mapa de Calor "
    "e exportação PDF funcionam normalmente.</div>",
    unsafe_allow_html=True
)

st.components.v1.html(html, height=2400, scrolling=True)

# ── DOWNLOAD BUTTONS ─────────────────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    st.download_button(
        label="💾  Salvar HTML",
        data=html.encode("utf-8"),
        file_name="histograma_mao_de_obra.html",
        mime="text/html",
    )

with col2:
    st.download_button(
        label="📋  Exportar JSON",
        data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="histograma_data.json",
        mime="application/json",
    )
