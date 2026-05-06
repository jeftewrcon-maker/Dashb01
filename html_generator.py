import json
from pathlib import Path

OBRA_COLORS = [
    '#00d4ff','#7c3aed','#f59e0b','#10b981','#ef4444',
    '#3b82f6','#ec4899','#8b5cf6','#06b6d4','#f97316',
    '#84cc16','#14b8a6','#a855f7','#eab308','#fb7185','#34d399'
]
FUNC_COLORS = [
    '#00d4ff','#f59e0b','#ef4444','#10b981','#8b5cf6',
    '#f97316','#3b82f6','#ec4899','#84cc16','#14b8a6',
    '#a855f7','#fb923c','#e879f9','#4ade80','#fbbf24','#60a5fa',
    '#f43f5e','#a3e635','#2dd4bf','#818cf8','#fb923c','#34d399',
    '#facc15','#c084fc','#38bdf8','#f87171',
]


def generate_html(data: dict) -> str:
    data_js = json.dumps(data, ensure_ascii=False)
    obra_colors_js = json.dumps(OBRA_COLORS)
    func_colors_js = json.dumps(FUNC_COLORS)
    grand_total_fmt = f"{data['grand_total']:,}".replace(',', '.')

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Histograma de Mão de Obra</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
:root {{
  --bg:#0a0c10; --surface:#111418; --surface2:#181d24; --border:#1e2530;
  --accent:#00d4ff; --accent2:#7c3aed; --accent3:#f59e0b;
  --danger:#ef4444; --success:#10b981; --text:#e2e8f0; --muted:#64748b;
}}
[data-theme="light"] {{
  --bg:#f0f4f8; --surface:#ffffff; --surface2:#e8edf3; --border:#cbd5e1;
  --accent:#0284c7; --accent2:#7c3aed; --accent3:#d97706;
  --danger:#ef4444; --success:#059669; --text:#0f172a; --muted:#64748b;
}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--text);font-family:Verdana,Geneva,Tahoma,sans-serif;min-height:100vh;padding:20px;transition:background .25s,color .25s;}}
.theme-toggle{{display:flex;align-items:center;gap:8px;padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:var(--surface2);cursor:pointer;font-size:12px;font-weight:600;color:var(--text);font-family:Verdana,Geneva,Tahoma,sans-serif;transition:all .2s;}}
.theme-toggle:hover{{border-color:var(--accent);color:var(--accent);}}
.theme-toggle .toggle-track{{width:34px;height:18px;border-radius:9px;background:var(--border);position:relative;transition:background .25s;flex-shrink:0;}}
.theme-toggle .toggle-thumb{{position:absolute;top:2px;left:2px;width:14px;height:14px;border-radius:50%;background:var(--muted);transition:transform .25s,background .25s;}}
[data-theme="light"] .theme-toggle .toggle-track{{background:var(--accent);}}
[data-theme="light"] .theme-toggle .toggle-thumb{{transform:translateX(16px);background:#fff;}}
.header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border);}}
.header h1{{font-size:20px;font-weight:700;letter-spacing:-.5px;}}
.header p{{font-size:12px;color:var(--muted);margin-top:2px;}}
.header-right{{display:flex;align-items:center;gap:12px;}}
.live-dot{{width:8px;height:8px;border-radius:50%;background:var(--success);box-shadow:0 0 8px var(--success);animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.4;}}}}
.badge{{font-size:11px;color:var(--muted);font-family:Verdana,Geneva,Tahoma,sans-serif;}}
.kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;}}
.kpi-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px 20px;position:relative;overflow:hidden;}}
.kpi-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--accent),var(--accent2));opacity:.6;}}
.kpi-label{{font-size:11px;color:var(--muted);letter-spacing:.5px;text-transform:uppercase;margin-bottom:8px;}}
.kpi-value{{font-size:32px;font-weight:700;letter-spacing:-1px;line-height:1;}}
.kpi-sub{{font-size:11px;color:var(--muted);margin-top:6px;font-family:Verdana,Geneva,Tahoma,sans-serif;}}
.kpi-icon{{position:absolute;right:16px;top:50%;transform:translateY(-50%);font-size:28px;opacity:.08;}}
.section-title{{font-size:12px;font-weight:600;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;display:flex;align-items:center;gap:8px;}}
.section-title::after{{content:'';flex:1;height:1px;background:var(--border);}}
.main-grid{{display:grid;grid-template-columns:1fr 320px;gap:16px;margin-bottom:20px;}}
.chart-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;}}
.chart-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px;}}
.chart-title{{font-size:14px;font-weight:600;color:var(--text);}}
.chart-subtitle{{font-size:11px;color:var(--muted);margin-top:2px;}}
.filter-tabs{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px;}}

/* ── MULTI-SELECT TAB BUTTONS ── */
.tab-btn{{padding:5px 12px;border-radius:20px;font-size:11px;font-weight:500;border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;transition:all .15s;font-family:Verdana,Geneva,Tahoma,sans-serif;}}
.tab-btn:hover{{border-color:var(--accent);color:var(--accent);}}
.tab-btn.active{{background:var(--accent);border-color:var(--accent);color:#000;font-weight:600;}}
.tab-btn.all-btn.active{{background:var(--accent2);border-color:var(--accent2);color:#fff;}}
.tab-btn.multi-active{{color:#000;font-weight:600;}}

.multi-hint{{font-size:10px;color:var(--muted);margin-bottom:8px;font-style:italic;}}

.obra-list{{display:flex;flex-direction:column;gap:8px;max-height:440px;overflow-y:auto;padding-right:4px;}}
.obra-list::-webkit-scrollbar{{width:4px;}}
.obra-list::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px;}}
.obra-item{{background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:12px 14px;cursor:pointer;transition:all .15s;display:flex;align-items:center;gap:10px;}}
.obra-item:hover,.obra-item.active{{border-color:var(--accent);background:var(--surface2);}}
.obra-dot{{width:10px;height:10px;border-radius:50%;flex-shrink:0;}}
.obra-info{{flex:1;min-width:0;}}
.obra-name{{font-size:12px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.obra-meta{{font-size:10px;color:var(--muted);margin-top:2px;font-family:Verdana,Geneva,Tahoma,sans-serif;}}
.obra-peak{{font-size:16px;font-weight:700;color:var(--accent3);flex-shrink:0;}}
.bottom-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;}}
.func-pills{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;}}
.func-pill{{padding:4px 10px;border-radius:16px;font-size:10px;font-weight:500;border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;transition:all .15s;font-family:Verdana,Geneva,Tahoma,sans-serif;}}
.func-pill:hover{{border-color:var(--accent);color:var(--accent);}}
.func-pill.active{{color:#000;font-weight:600;}}
.overlap-table{{width:100%;border-collapse:collapse;font-size:11px;}}
.overlap-table th{{text-align:left;padding:8px 12px;color:var(--muted);border-bottom:1px solid var(--border);font-size:10px;letter-spacing:.5px;text-transform:uppercase;font-weight:600;}}
.overlap-table td{{padding:8px 12px;border-bottom:1px solid rgba(30,37,48,.5);}}
.overlap-table tr:last-child td{{border-bottom:none;}}
.overlap-table tr:hover td{{background:var(--surface2);}}
.bar-mini{{display:flex;align-items:center;gap:8px;}}
.bar-track{{flex:1;height:4px;background:var(--border);border-radius:2px;overflow:hidden;}}
.bar-fill{{height:100%;border-radius:2px;transition:width .3s;}}
.interval-selector{{display:flex;align-items:center;gap:8px;}}
.interval-btn{{padding:3px 9px;border-radius:12px;font-size:10px;font-weight:600;border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;transition:all .15s;font-family:Verdana,Geneva,Tahoma,sans-serif;}}
.interval-btn:hover{{border-color:var(--accent3);color:var(--accent3);}}
.interval-btn.active{{background:var(--accent3);border-color:var(--accent3);color:#000;}}
.pdf-btn{{padding:6px 16px;border-radius:8px;font-size:11px;font-weight:600;border:1px solid var(--accent2);background:rgba(124,58,237,.15);color:#c4b5fd;cursor:pointer;transition:all .2s;font-family:Verdana,Geneva,Tahoma,sans-serif;display:flex;align-items:center;gap:6px;}}
.pdf-btn:hover{{background:var(--accent2);color:#fff;}}
.pdf-btn:disabled{{opacity:0.5;cursor:not-allowed;}}
.city-filter-bar{{display:flex;align-items:center;gap:8px;margin-bottom:16px;padding:10px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;flex-wrap:wrap;}}
.city-filter-label{{font-size:11px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-right:4px;}}
.city-btn{{padding:4px 14px;border-radius:20px;font-size:11px;font-weight:600;border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;transition:all .15s;font-family:Verdana,Geneva,Tahoma,sans-serif;}}
.city-btn:hover{{border-color:var(--accent);color:var(--accent);}}
.city-btn.active{{background:var(--accent);border-color:var(--accent);color:#000;}}
.gantt-container{{overflow-x:auto;overflow-y:auto;max-height:600px;position:relative;}}
.gantt-table{{border-collapse:collapse;font-size:11px;min-width:100%;table-layout:fixed;}}
.gantt-table .obra-col{{position:sticky;left:0;background:var(--surface);z-index:2;padding:4px 6px;font-size:10px;font-weight:600;color:var(--text);border-right:1px solid var(--border);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.gantt-table .func-col{{position:sticky;background:var(--surface);z-index:2;padding:4px 6px;font-size:9px;color:var(--muted);border-right:1px solid var(--border);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.gantt-table .header-obra-col{{position:sticky;left:0;background:var(--surface2);z-index:3;padding:6px 6px;font-size:10px;font-weight:700;color:var(--accent);letter-spacing:.5px;text-transform:uppercase;border-bottom:2px solid var(--border);border-right:1px solid var(--border);overflow:hidden;white-space:nowrap;}}
.gantt-table .header-func-col{{position:sticky;background:var(--surface2);z-index:3;padding:6px 6px;font-size:10px;font-weight:700;color:var(--accent);letter-spacing:.5px;text-transform:uppercase;border-bottom:2px solid var(--border);border-right:1px solid var(--border);overflow:hidden;white-space:nowrap;}}
/* resize handle */
.col-resizer{{position:absolute;right:0;top:0;bottom:0;width:5px;cursor:col-resize;background:transparent;z-index:10;}}
.col-resizer:hover,.col-resizer.dragging{{background:var(--accent);opacity:.5;}}
.gantt-table th.month-th{{padding:2px 0;font-size:10px;color:var(--muted);font-family:Verdana,Geneva,Tahoma,sans-serif;text-align:center;border-bottom:2px solid var(--border);border-left:1px solid var(--border);min-width:28px;max-width:28px;width:28px;font-weight:600;background:var(--surface2);position:sticky;top:0;z-index:1;height:80px;vertical-align:bottom;overflow:hidden;}}
.gantt-table th.month-th .month-label{{display:block;writing-mode:vertical-rl;text-orientation:mixed;transform:rotate(180deg);white-space:nowrap;font-size:10px;font-weight:600;color:var(--muted);line-height:28px;margin:0 auto;}}
.gantt-table th.month-th.interval-hidden{{display:none;}}
.gantt-table td.gantt-cell{{width:28px;min-width:28px;max-width:28px;height:20px;padding:1px;border-left:1px solid rgba(30,37,48,.4);vertical-align:middle;}}
.gantt-table td.gantt-cell.interval-hidden{{display:none;}}
.gantt-cell-inner{{width:100%;height:16px;border-radius:2px;display:flex;align-items:center;justify-content:center;font-size:7px;font-weight:700;color:rgba(255,255,255,0.85);overflow:hidden;transition:opacity .15s;}}
[data-theme="light"] .gantt-cell-inner{{color:rgba(0,0,0,0.75);}}
.gantt-cell-inner:hover{{filter:brightness(1.3);}}
.gantt-table tr.obra-group-header td{{background:var(--surface2);padding:3px 8px;font-size:10px;font-weight:700;color:var(--text);border-top:2px solid var(--border);}}
.gantt-table tr:hover .gantt-cell-inner{{opacity:0.85;}}
.gantt-legend{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}}
.gantt-legend-item{{display:flex;align-items:center;gap:5px;font-size:10px;color:var(--muted);}}
.gantt-legend-dot{{width:10px;height:10px;border-radius:2px;flex-shrink:0;}}
.gantt-filter-bar{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;padding:10px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;align-items:center;}}
.gantt-filter-label{{font-size:10px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-right:4px;white-space:nowrap;}}

/* ── MULTI-SELECT GANTT PILLS ── */
.gantt-filter-pill{{padding:3px 10px;border-radius:14px;font-size:10px;font-weight:500;border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;transition:all .15s;font-family:Verdana,Geneva,Tahoma,sans-serif;}}
.gantt-filter-pill:hover{{border-color:var(--accent);color:var(--accent);}}
.gantt-filter-pill.active{{background:var(--accent);border-color:var(--accent);color:#000;font-weight:600;}}
.gantt-filter-pill.all-pill.active{{background:#7c3aed;border-color:#7c3aed;color:#fff;}}
.gantt-filter-pill.multi-active{{color:#000;font-weight:600;}}
.gantt-filter-sep{{width:1px;height:20px;background:var(--border);margin:0 4px;}}

/* selection counter badges */
.sel-badge{{display:inline-flex;align-items:center;justify-content:center;min-width:18px;height:18px;border-radius:9px;background:var(--accent3);color:#000;font-size:9px;font-weight:700;padding:0 5px;margin-left:4px;font-family:Verdana,Geneva,Tahoma,sans-serif;}}

@media(max-width:1100px){{.kpi-grid{{grid-template-columns:repeat(2,1fr);}} .main-grid{{grid-template-columns:1fr;}} .bottom-grid{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>⚡ Histograma de Mão de Obra</h1>
    <p>Sobreposição · Superlocação · Atrito entre Obras</p>
  </div>
  <div class="header-right">
    <button class="theme-toggle" id="theme-toggle-btn" onclick="toggleTheme()">
      <span id="theme-icon">☀️</span>
      <span id="theme-label">Modo Claro</span>
      <div class="toggle-track"><div class="toggle-thumb"></div></div>
    </button>
    <button class="pdf-btn" id="pdf-export-btn" onclick="exportPDF()">📄 Exportar PDF</button>
    <div class="live-dot"></div>
    <span class="badge" id="header-badge"></span>
  </div>
</div>

<!-- CITY FILTER BAR -->
<div class="city-filter-bar" id="city-filter-bar">
  <span class="city-filter-label">🏙️ Cidade:</span>
  <button class="city-btn active" data-city="ALL">Todas</button>
</div>

<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Pico Total</div>
    <div class="kpi-value" style="color:var(--accent)" id="kpi-peak">{data['peak_total']}</div>
    <div class="kpi-sub" id="kpi-peak-sub">{data['peak_month']} — máximo histórico</div>
    <div class="kpi-icon">📈</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Obras no Portfolio</div>
    <div class="kpi-value" style="color:var(--accent3)" id="kpi-obras">{data['num_obras']}</div>
    <div class="kpi-sub">sobreposição ativa</div>
    <div class="kpi-icon">🏗️</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Func-Mês</div>
    <div class="kpi-value" style="color:var(--accent2)" id="kpi-total">{grand_total_fmt}</div>
    <div class="kpi-sub">acumulado geral</div>
    <div class="kpi-icon">👷</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Duração</div>
    <div class="kpi-value" style="color:var(--success)">{data['duration']}</div>
    <div class="kpi-sub">meses · {data['months'][0] if data['months'] else ''} → {data['months'][-1] if data['months'] else ''}</div>
    <div class="kpi-icon">📅</div>
  </div>
</div>

<!-- INTERVAL SELECTOR -->
<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;padding:12px 16px;background:var(--surface);border:1px solid var(--border);border-radius:10px;">
  <span style="font-size:11px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Intervalo do Eixo X:</span>
  <div class="interval-selector" id="global-interval-btns">
    <button class="interval-btn" data-interval="1">1 mês</button>
    <button class="interval-btn" data-interval="2">2 meses</button>
    <button class="interval-btn active" data-interval="3">3 meses</button>
    <button class="interval-btn" data-interval="4">4 meses</button>
    <button class="interval-btn" data-interval="5">5 meses</button>
  </div>
  <span style="margin-left:auto;font-size:10px;color:var(--muted);font-family:Verdana,Geneva,Tahoma,sans-serif;" id="interval-hint">mostrando a cada 3 meses</span>
</div>

<div class="main-grid">
  <div class="chart-card">
    <div class="chart-header">
      <div>
        <div class="chart-title">Histograma Geral — Trabalhadores por Mês</div>
        <div class="chart-subtitle">Empilhamento por obra · <strong style="color:var(--accent3)">clique para selecionar · Ctrl+clique para múltiplas</strong></div>
      </div>
      <span id="peak-indicator" style="font-size:11px;color:var(--accent);font-family:Verdana,Geneva,Tahoma,sans-serif;"></span>
    </div>
    <div class="multi-hint" id="obra-multi-hint"></div>
    <div class="filter-tabs" id="obra-filter-tabs">
      <button class="tab-btn all-btn active" data-obra="ALL">Todas as Obras</button>
    </div>
    <div style="position:relative;height:300px;"><canvas id="mainChart"></canvas></div>
  </div>

  <div class="chart-card">
    <div class="chart-header">
      <div>
        <div class="chart-title">Obras — Resumo</div>
        <div class="chart-subtitle">Pico · Total func-mês</div>
      </div>
    </div>
    <div class="obra-list" id="obra-list"></div>
  </div>
</div>

<div class="bottom-grid">
  <div class="chart-card">
    <div class="chart-header">
      <div>
        <div class="chart-title">Função ao Longo do Tempo</div>
        <div class="chart-subtitle">Demanda mensal por especialidade</div>
      </div>
    </div>
    <div class="func-pills" id="func-pills"></div>
    <div style="position:relative;height:200px;"><canvas id="funcChart"></canvas></div>
  </div>

  <div class="chart-card">
    <div class="chart-header">
      <div>
        <div class="chart-title">Sobreposição por Obra</div>
        <div class="chart-subtitle">Intensidade relativa · atrito e superlocação</div>
      </div>
    </div>
    <div style="overflow-y:auto;max-height:280px;">
      <table class="overlap-table" id="overlap-table">
        <thead><tr><th>Obra</th><th>Pico</th><th>Total</th><th style="width:120px">Intensidade</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
</div>

<!-- GANTT CHART -->
<div class="chart-card" style="margin-bottom:20px;" id="gantt-card">
  <div class="chart-header">
    <div>
      <div class="chart-title">Gantt de Mão de Obra — Obras × Funções × Tempo</div>
      <div class="chart-subtitle">Filtros por cidade, obra e função · <strong style="color:var(--accent3)">Ctrl+clique para selecionar múltiplos</strong> · cor por especialidade · intensidade por quantidade</div>
    </div>
  </div>
  <!-- GANTT FILTERS -->
  <div class="gantt-filter-bar" id="gantt-filter-bar">
    <span class="gantt-filter-label">🏙️ Cidade:</span>
    <button class="gantt-filter-pill all-pill active" data-gantt-city="ALL">Todas</button>
    <div class="gantt-filter-sep" id="gantt-city-sep"></div>
    <span class="gantt-filter-label" id="gantt-obra-label">🏗️ Obra: <span class="sel-badge" id="gantt-obra-badge" style="display:none"></span></span>
    <div id="gantt-obra-pills" style="display:flex;flex-wrap:wrap;gap:6px;"></div>
    <div class="gantt-filter-sep"></div>
    <span class="gantt-filter-label">👷 Função: <span class="sel-badge" id="gantt-func-badge" style="display:none"></span></span>
    <button class="gantt-filter-pill all-pill active" data-gantt-func="ALL">Todas</button>
    <div id="gantt-func-pills" style="display:flex;flex-wrap:wrap;gap:6px;"></div>
  </div>
  <div class="gantt-container" id="gantt-container">
    <table class="gantt-table" id="gantt-table"></table>
  </div>
  <div class="gantt-legend" id="gantt-legend"></div>
</div>

<!-- HEATMAP -->
<div class="chart-card" style="margin-bottom:20px;" id="heatmap-card">
  <div class="chart-header">
    <div>
      <div class="chart-title">Mapa de Calor — Obras × Meses</div>
      <div class="chart-subtitle">Densidade de alocação · identifica sobreposições críticas</div>
    </div>
  </div>
  <div style="overflow-x:auto;"><div id="heatmap-container"></div></div>
</div>

<!-- PDF OVERLAY -->
<div id="pdf-overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:9999;align-items:center;justify-content:center;flex-direction:column;gap:12px;">
  <div style="background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:32px 40px;text-align:center;">
    <div style="font-size:32px;margin-bottom:12px;">📄</div>
    <div style="font-size:16px;font-weight:600;color:var(--text);">Gerando PDF...</div>
    <div style="font-size:12px;color:var(--muted);margin-top:6px;">Capturando dashboard completo</div>
    <div id="pdf-progress" style="font-size:11px;color:var(--accent);margin-top:10px;font-family:Verdana,Geneva,Tahoma,sans-serif;"></div>
  </div>
</div>

<script>
const DATA = {data_js};
const OBRA_COLORS = {obra_colors_js};
const FUNC_COLORS = {func_colors_js};

// ── THEME TOGGLE ──────────────────────────────────────────────────────
function toggleTheme() {{
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  const newTheme = isLight ? 'dark' : 'light';
  applyTheme(newTheme);
  localStorage.setItem('hmo-theme', newTheme);
}}
function applyTheme(theme) {{
  if (theme === 'light') {{
    document.documentElement.setAttribute('data-theme','light');
    document.getElementById('theme-icon').textContent = '🌙';
    document.getElementById('theme-label').textContent = 'Modo Escuro';
  }} else {{
    document.documentElement.removeAttribute('data-theme');
    document.getElementById('theme-icon').textContent = '☀️';
    document.getElementById('theme-label').textContent = 'Modo Claro';
  }}
  // update chart colors
  const gridColor = theme === 'light' ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.06)';
  const tickColor = theme === 'light' ? '#64748b' : '#64748b';
  const updateChartTheme = (chart) => {{
    if (!chart) return;
    chart.options.scales.x.grid.color = gridColor;
    chart.options.scales.y.grid.color = gridColor;
    chart.options.scales.x.ticks.color = tickColor;
    chart.options.scales.y.ticks.color = tickColor;
    chart.update();
  }};
  updateChartTheme(mainChart);
  updateChartTheme(funcChart);
}}
// restore saved theme on load
(function() {{
  const saved = localStorage.getItem('hmo-theme');
  if (saved === 'light') applyTheme('light');
}})();

let mainChart, funcChart;
let currentInterval = 3;
let activeCityGlobal = 'ALL';

// ── MULTI-SELECT STATE ────────────────────────────────────────────────
// Set() of selected obras for histogram; empty = ALL
let selectedObras = new Set();
// Set() of selected obras/funcs for Gantt
let ganttSelectedObras = new Set();
let ganttSelectedFuncs = new Set();
let ganttFilterCity = 'ALL';

document.getElementById('header-badge').textContent =
  DATA.months[0] + ' → ' + DATA.months[DATA.months.length - 1] + ' · ' + DATA.num_obras + ' obras';

// ── UTILITY ──────────────────────────────────────────────────────────
function getFilteredObras(city) {{
  if (city === 'ALL') return DATA.obras;
  return DATA.obras.filter(o => (DATA.obra_cidade[o] || '') === city);
}}

function getActiveObras() {{
  const cityObras = getFilteredObras(activeCityGlobal);
  if (selectedObras.size === 0) return cityObras;
  return cityObras.filter(o => selectedObras.has(o));
}}

// ── CITY FILTER BAR ──────────────────────────────────────────────────
function buildCityFilterBar() {{
  const bar = document.getElementById('city-filter-bar');
  if (!DATA.cidades || DATA.cidades.length <= 1) {{
    bar.style.display = 'none';
    return;
  }}
  DATA.cidades.forEach(city => {{
    const btn = document.createElement('button');
    btn.className = 'city-btn';
    btn.dataset.city = city;
    btn.textContent = city;
    bar.appendChild(btn);
  }});
  bar.addEventListener('click', e => {{
    const btn = e.target.closest('[data-city]');
    if (!btn) return;
    bar.querySelectorAll('.city-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    onCityChange(btn.dataset.city);
  }});
}}

function onCityChange(city) {{
  activeCityGlobal = city;
  selectedObras.clear();
  buildFilterTabs();
  buildObraList();
  buildOverlapTable();
  updateMainChart();
  updateKPIs();
}}

function updateKPIs() {{
  const obras = getActiveObras();
  let peak = 0, peakMonth = '', total = 0;
  DATA.months.forEach((m, mi) => {{
    const v = obras.reduce((s, o) => s + (DATA.obra_data[o][mi] || 0), 0);
    total += v;
    if (v > peak) {{ peak = v; peakMonth = m; }}
  }});
  document.getElementById('kpi-peak').textContent = peak;
  document.getElementById('kpi-peak-sub').textContent = peakMonth + ' — máximo';
  document.getElementById('kpi-obras').textContent = obras.length;
  document.getElementById('kpi-total').textContent = total.toLocaleString('pt-BR');
}}

// ── INTERVAL CONTROLS ────────────────────────────────────────────────
function applyInterval(interval) {{
  currentInterval = interval;
  document.querySelectorAll('#global-interval-btns .interval-btn').forEach(b => {{
    b.classList.toggle('active', parseInt(b.dataset.interval) === interval);
  }});
  document.getElementById('interval-hint').textContent =
    interval === 1 ? 'mostrando todos os meses' : `mostrando a cada ${{interval}} meses`;
  const approxTicks = Math.ceil(DATA.months.length / interval);
  if (mainChart) {{ mainChart.options.scales.x.ticks.maxTicksLimit = approxTicks; mainChart.update(); }}
  if (funcChart) {{ funcChart.options.scales.x.ticks.maxTicksLimit = approxTicks; funcChart.update(); }}
  document.querySelectorAll('.interval-hidden').forEach(el => el.classList.remove('interval-hidden'));
  if (interval > 1) {{
    document.querySelectorAll('[data-month-idx]').forEach(el => {{
      const idx = parseInt(el.dataset.monthIdx);
      if (idx % interval !== 0) el.classList.add('interval-hidden');
    }});
  }}
}}

document.getElementById('global-interval-btns').addEventListener('click', e => {{
  const btn = e.target.closest('.interval-btn');
  if (btn) applyInterval(parseInt(btn.dataset.interval));
}});

// ── MAIN CHART (multi-select) ─────────────────────────────────────────
function buildMainDatasets() {{
  const obras = getActiveObras();
  return obras.map(obra => {{
    const idx = DATA.obras.indexOf(obra);
    return {{
      label: obra, data: DATA.obra_data[obra],
      backgroundColor: OBRA_COLORS[idx % OBRA_COLORS.length] + 'cc',
      borderColor: OBRA_COLORS[idx % OBRA_COLORS.length],
      borderWidth: 0, borderRadius: 1
    }};
  }});
}}

function initMainChart() {{
  const ctx = document.getElementById('mainChart').getContext('2d');
  mainChart = new Chart(ctx, {{
    type: 'bar',
    data: {{ labels: DATA.months, datasets: buildMainDatasets() }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#0f1318ee', borderColor: '#1e2530', borderWidth: 1,
          titleColor: '#e2e8f0', bodyColor: '#94a3b8', padding: 12,
          callbacks: {{ afterBody: items => ['─────────', 'Total: ' + items.reduce((s, i) => s + i.raw, 0) + ' trabalhadores'] }}
        }}
      }},
      scales: {{
        x: {{ stacked: true, grid: {{ color: '#1e2530' }}, ticks: {{ color: '#64748b', font: {{ size: 9 }}, maxTicksLimit: Math.ceil(DATA.months.length / currentInterval) }} }},
        y: {{ stacked: true, grid: {{ color: '#1e2530' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }} }} }}
      }}
    }}
  }});
}}

function updateMainChart() {{
  if (!mainChart) return;
  mainChart.data.datasets = buildMainDatasets();
  mainChart.update('active');
  const obras = getActiveObras();
  const totals = DATA.months.map((_, mi) => obras.reduce((s, o) => s + (DATA.obra_data[o][mi] || 0), 0));
  const peak = Math.max(...totals);
  const peakMonth = DATA.months[totals.indexOf(peak)];
  document.getElementById('peak-indicator').textContent = 'Pico: ' + peak + ' · ' + peakMonth;
  updateKPIs();
}}

// ── FILTER TABS (multi-select) ───────────────────────────────────────
function buildFilterTabs() {{
  const container = document.getElementById('obra-filter-tabs');
  container.innerHTML = '';

  // ALL button
  const allBtn = document.createElement('button');
  allBtn.className = 'tab-btn all-btn' + (selectedObras.size === 0 ? ' active' : '');
  allBtn.dataset.obra = 'ALL';
  allBtn.textContent = 'Todas as Obras';
  allBtn.addEventListener('click', () => {{
    selectedObras.clear();
    refreshFilterTabs();
    updateMainChart();
    buildObraList();
  }});
  container.appendChild(allBtn);

  getFilteredObras(activeCityGlobal).forEach((obra) => {{
    const idx = DATA.obras.indexOf(obra);
    const color = OBRA_COLORS[idx % OBRA_COLORS.length];
    const btn = document.createElement('button');
    btn.className = 'tab-btn' + (selectedObras.has(obra) ? ' multi-active' : '');
    btn.style.borderColor = color + '66';
    if (selectedObras.has(obra)) {{
      btn.style.background = color;
      btn.style.color = '#000';
    }}
    btn.dataset.obra = obra;
    btn.textContent = obra;
    btn.addEventListener('click', (e) => {{
      if (e.ctrlKey || e.metaKey) {{
        // Multi-select: toggle this obra
        if (selectedObras.has(obra)) {{
          selectedObras.delete(obra);
        }} else {{
          selectedObras.add(obra);
        }}
      }} else {{
        // Single select (or deselect if only this one is selected)
        if (selectedObras.size === 1 && selectedObras.has(obra)) {{
          selectedObras.clear();
        }} else {{
          selectedObras.clear();
          selectedObras.add(obra);
        }}
      }}
      refreshFilterTabs();
      updateMainChart();
      buildObraList();
    }});
    container.appendChild(btn);
  }});
  updateObraMultiHint();
}}

function refreshFilterTabs() {{
  const container = document.getElementById('obra-filter-tabs');
  const allBtn = container.querySelector('[data-obra="ALL"]');
  if (allBtn) allBtn.classList.toggle('active', selectedObras.size === 0);
  getFilteredObras(activeCityGlobal).forEach(obra => {{
    const idx = DATA.obras.indexOf(obra);
    const color = OBRA_COLORS[idx % OBRA_COLORS.length];
    const btn = container.querySelector(`[data-obra="${{obra}}"]`);
    if (!btn) return;
    const isActive = selectedObras.has(obra);
    btn.classList.toggle('multi-active', isActive);
    btn.style.background = isActive ? color : '';
    btn.style.color = isActive ? '#000' : '';
    btn.style.borderColor = isActive ? color : color + '66';
  }});
  updateObraMultiHint();
}}

function updateObraMultiHint() {{
  const hint = document.getElementById('obra-multi-hint');
  if (selectedObras.size > 1) {{
    hint.textContent = `✦ ${{selectedObras.size}} obras selecionadas · Ctrl+clique para adicionar/remover · clique simples para isolar`;
  }} else if (selectedObras.size === 1) {{
    hint.textContent = `✦ 1 obra selecionada · Ctrl+clique para adicionar mais`;
  }} else {{
    hint.textContent = '';
  }}
}}

// ── OBRA LIST ────────────────────────────────────────────────────────
function buildObraList() {{
  const container = document.getElementById('obra-list');
  container.innerHTML = '';
  getFilteredObras(activeCityGlobal).forEach((obra) => {{
    const i = DATA.obras.indexOf(obra);
    const div = document.createElement('div');
    const isActive = selectedObras.has(obra);
    div.className = 'obra-item' + (isActive ? ' active' : '');
    const total = (DATA.obra_totals[obra] || 0).toLocaleString('pt-BR');
    const peak = DATA.obra_peaks[obra];
    const cidade = DATA.obra_cidade[obra] || '';
    div.innerHTML = `<div class="obra-dot" style="background:${{OBRA_COLORS[i % OBRA_COLORS.length]}}"></div>
      <div class="obra-info">
        <div class="obra-name">${{obra}}</div>
        <div class="obra-meta">${{cidade ? cidade + ' · ' : ''}}Pico: ${{peak?.month || ''}} · Total: ${{total}} func-mês</div>
      </div>
      <div class="obra-peak">${{peak?.peak || 0}}</div>`;
    div.addEventListener('click', (e) => {{
      if (e.ctrlKey || e.metaKey) {{
        if (selectedObras.has(obra)) selectedObras.delete(obra);
        else selectedObras.add(obra);
      }} else {{
        if (selectedObras.size === 1 && selectedObras.has(obra)) selectedObras.clear();
        else {{ selectedObras.clear(); selectedObras.add(obra); }}
      }}
      refreshFilterTabs();
      updateMainChart();
      buildObraList();
    }});
    container.appendChild(div);
  }});
}}

// ── FUNC CHART ───────────────────────────────────────────────────────
let activeFunc = DATA.funcoes[0];

function initFuncChart() {{
  const ctx = document.getElementById('funcChart').getContext('2d');
  funcChart = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: DATA.months,
      datasets: [{{ label: activeFunc, data: DATA.func_data[activeFunc], backgroundColor: FUNC_COLORS[0] + 'bb', borderColor: FUNC_COLORS[0], borderWidth: 0, borderRadius: 2 }}]
    }},
    options: {{
      responsive: true, maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{ backgroundColor: '#0f1318ee', borderColor: '#1e2530', borderWidth: 1, titleColor: '#e2e8f0', bodyColor: '#94a3b8' }}
      }},
      scales: {{
        x: {{ grid: {{ color: '#1e2530' }}, ticks: {{ color: '#64748b', font: {{ size: 8 }}, maxTicksLimit: Math.ceil(DATA.months.length / currentInterval) }} }},
        y: {{ grid: {{ color: '#1e2530' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }} }} }}
      }}
    }}
  }});
}}

function updateFuncChart(func) {{
  const idx = DATA.funcoes.indexOf(func);
  const color = FUNC_COLORS[idx % FUNC_COLORS.length];
  funcChart.data.datasets[0] = {{ label: func, data: DATA.func_data[func], backgroundColor: color + 'bb', borderColor: color, borderWidth: 0, borderRadius: 2 }};
  funcChart.update('active');
}}

// ── FUNC PILLS ───────────────────────────────────────────────────────
function buildFuncPills() {{
  const container = document.getElementById('func-pills');
  DATA.funcoes.forEach((func, i) => {{
    const btn = document.createElement('button');
    btn.className = 'func-pill' + (i === 0 ? ' active' : '');
    btn.style.borderColor = FUNC_COLORS[i % FUNC_COLORS.length] + '66';
    if (i === 0) {{ btn.style.background = FUNC_COLORS[0]; btn.style.color = '#000'; }}
    const shortName = func.length > 22 ? func.substring(0, 20) + '…' : func;
    btn.textContent = shortName; btn.title = func;
    btn.addEventListener('click', () => {{
      document.querySelectorAll('.func-pill').forEach(p => {{ p.classList.remove('active'); p.style.background = ''; p.style.color = ''; }});
      btn.classList.add('active');
      btn.style.background = FUNC_COLORS[i % FUNC_COLORS.length]; btn.style.color = '#000';
      activeFunc = func; updateFuncChart(func);
    }});
    container.appendChild(btn);
  }});
}}

// ── OVERLAP TABLE ────────────────────────────────────────────────────
function buildOverlapTable() {{
  const tbody = document.querySelector('#overlap-table tbody');
  tbody.innerHTML = '';
  const obras = getFilteredObras(activeCityGlobal);
  const maxTotal = Math.max(...obras.map(o => DATA.obra_totals[o] || 0));
  [...obras].sort((a, b) => (DATA.obra_totals[b] || 0) - (DATA.obra_totals[a] || 0)).forEach((obra) => {{
    const idx = DATA.obras.indexOf(obra);
    const color = OBRA_COLORS[idx % OBRA_COLORS.length];
    const pct = maxTotal > 0 ? ((DATA.obra_totals[obra] || 0) / maxTotal * 100).toFixed(0) : 0;
    const tr = document.createElement('tr');
    tr.innerHTML = `<td style="display:flex;align-items:center;gap:7px;">
      <div style="width:8px;height:8px;border-radius:50%;background:${{color}};flex-shrink:0"></div>
      <span style="font-size:11px">${{obra}}</span></td>
      <td style="font-family:Verdana,Geneva,Tahoma,sans-serif;color:var(--accent3)">${{DATA.obra_peaks[obra]?.peak || 0}}</td>
      <td style="font-family:Verdana,Geneva,Tahoma,sans-serif;color:var(--muted)">${{(DATA.obra_totals[obra] || 0).toLocaleString('pt-BR')}}</td>
      <td><div class="bar-mini"><div class="bar-track"><div class="bar-fill" style="width:${{pct}}%;background:${{color}}"></div></div>
      <span style="font-size:9px;color:var(--muted);font-family:Verdana,Geneva,Tahoma,sans-serif;width:28px">${{pct}}%</span></div></td>`;
    tbody.appendChild(tr);
  }});
}}

// ── HEATMAP ──────────────────────────────────────────────────────────
function buildHeatmap() {{
  const container = document.getElementById('heatmap-container');
  const allVals = DATA.obras.flatMap(o => DATA.obra_data[o]);
  const maxVal = Math.max(...allVals) || 1;
  const headerRow = document.createElement('div');
  headerRow.style.cssText = 'display:flex;align-items:center;gap:1px;margin-bottom:4px;';
  const labelSpacer = document.createElement('div');
  labelSpacer.style.cssText = 'width:80px;flex-shrink:0;';
  headerRow.appendChild(labelSpacer);
  DATA.months.forEach((m, mi) => {{
    const mh = document.createElement('div');
    mh.style.cssText = 'width:20px;height:80px;flex-shrink:0;color:var(--muted);text-align:center;overflow:hidden;font-family:Verdana,Geneva,Tahoma,sans-serif;display:flex;align-items:flex-end;justify-content:center;padding-bottom:2px;';
    mh.dataset.monthIdx = mi;
    if (mi % currentInterval !== 0) mh.classList.add('interval-hidden');
    const span = document.createElement('span');
    span.style.cssText = 'display:block;writing-mode:vertical-rl;text-orientation:mixed;transform:rotate(180deg);white-space:nowrap;font-size:11px;font-weight:600;line-height:20px;';
    span.textContent = m;
    mh.appendChild(span);
    headerRow.appendChild(mh);
  }});
  container.appendChild(headerRow);
  DATA.obras.forEach((obra, oi) => {{
    const row = document.createElement('div');
    row.style.cssText = 'display:flex;align-items:center;gap:1px;margin-bottom:2px;';
    const label = document.createElement('div');
    label.style.cssText = 'width:80px;font-size:10px;color:var(--muted);text-align:right;padding-right:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex-shrink:0;';
    label.textContent = obra; label.title = obra;
    row.appendChild(label);
    DATA.months.forEach((m, mi) => {{
      const v = (DATA.obra_data[obra][mi] || 0);
      const cell = document.createElement('div');
      cell.style.cssText = 'width:20px;height:18px;border-radius:2px;flex-shrink:0;';
      cell.dataset.monthIdx = mi;
      if (mi % currentInterval !== 0) cell.classList.add('interval-hidden');
      if (v === 0) {{ cell.style.background = '#1a2030'; }}
      else {{ const alpha = (0.15 + (v / maxVal) * 0.85).toFixed(2); cell.style.background = OBRA_COLORS[oi % OBRA_COLORS.length]; cell.style.opacity = alpha; }}
      cell.title = obra + ' · ' + m + ': ' + v + ' trabalhadores';
      row.appendChild(cell);
    }});
    container.appendChild(row);
  }});
}}

// ── GANTT COLUMN WIDTHS (resizable) ──────────────────────────────────
const ganttColWidths = {{ obra: 120, func: 150 }};

function initGanttResize() {{
  document.getElementById('gantt-container').addEventListener('mousedown', e => {{
    const resizer = e.target.closest('.col-resizer');
    if (!resizer) return;
    e.preventDefault();
    const col = resizer.dataset.col; // 'obra' or 'func'
    const startX = e.clientX;
    const startW = ganttColWidths[col];
    resizer.classList.add('dragging');

    function onMove(e) {{
      const delta = e.clientX - startX;
      const newW = Math.max(60, startW + delta);
      ganttColWidths[col] = newW;
      // Update all header and body cells for this column live
      const selector = col === 'obra' ? '.obra-col, .header-obra-col' : '.func-col, .header-func-col';
      document.querySelectorAll(selector).forEach(el => {{
        el.style.width = newW + 'px';
        el.style.minWidth = newW + 'px';
      }});
      // Update func-col left offset when obra changes
      if (col === 'obra') {{
        document.querySelectorAll('.func-col, .header-func-col').forEach(el => {{
          el.style.left = newW + 'px';
        }});
      }}
    }}

    function onUp() {{
      resizer.classList.remove('dragging');
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }}

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }});
}}

// ── GANTT FILTERS (multi-select) ──────────────────────────────────────
function buildGanttFilters() {{
  // City pills
  const cityAllPill = document.querySelector('[data-gantt-city="ALL"]');
  const filterBar = document.getElementById('gantt-filter-bar');
  const citySep = document.getElementById('gantt-city-sep');

  if (DATA.cidades && DATA.cidades.length > 1) {{
    DATA.cidades.forEach(city => {{
      const btn = document.createElement('button');
      btn.className = 'gantt-filter-pill';
      btn.dataset.ganttCity = city;
      btn.textContent = city;
      // insert before the city separator
      filterBar.insertBefore(btn, citySep);
    }});
  }} else {{
    cityAllPill.style.display = 'none';
    citySep.style.display = 'none';
    filterBar.querySelector('.gantt-filter-label').style.display = 'none';
  }}

  // Obra pills
  const obraPillsContainer = document.getElementById('gantt-obra-pills');
  const obraAllPill = document.createElement('button');
  obraAllPill.className = 'gantt-filter-pill all-pill active';
  obraAllPill.dataset.ganttObra = 'ALL';
  obraAllPill.textContent = 'Todas';
  obraPillsContainer.appendChild(obraAllPill);
  DATA.obras.forEach((obra, i) => {{
    const btn = document.createElement('button');
    btn.className = 'gantt-filter-pill';
    btn.dataset.ganttObra = obra;
    btn.textContent = obra.length > 18 ? obra.substring(0, 17) + '…' : obra;
    btn.title = obra;
    btn.style.borderColor = OBRA_COLORS[i % OBRA_COLORS.length] + '66';
    obraPillsContainer.appendChild(btn);
  }});

  // Func pills
  const funcPillsContainer = document.getElementById('gantt-func-pills');
  DATA.funcoes.forEach((func, i) => {{
    const btn = document.createElement('button');
    btn.className = 'gantt-filter-pill';
    btn.dataset.ganttFunc = func;
    btn.textContent = func.length > 18 ? func.substring(0, 17) + '…' : func;
    btn.title = func;
    btn.style.borderColor = FUNC_COLORS[i % FUNC_COLORS.length] + '66';
    funcPillsContainer.appendChild(btn);
  }});

  // ── Event listeners ──
  filterBar.addEventListener('click', e => {{
    const btn = e.target.closest('[data-gantt-city],[data-gantt-obra],[data-gantt-func]');
    if (!btn) return;

    if (btn.dataset.ganttCity !== undefined) {{
      // City: single select (resets obra selection)
      filterBar.querySelectorAll('[data-gantt-city]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      ganttFilterCity = btn.dataset.ganttCity;
      ganttSelectedObras.clear();
      refreshGanttObraPills();
      buildGantt();

    }} else if (btn.dataset.ganttObra !== undefined) {{
      const obra = btn.dataset.ganttObra;
      if (obra === 'ALL') {{
        ganttSelectedObras.clear();
      }} else if (e.ctrlKey || e.metaKey) {{
        // Multi-select toggle
        if (ganttSelectedObras.has(obra)) ganttSelectedObras.delete(obra);
        else ganttSelectedObras.add(obra);
      }} else {{
        // Single select / deselect
        if (ganttSelectedObras.size === 1 && ganttSelectedObras.has(obra)) ganttSelectedObras.clear();
        else {{ ganttSelectedObras.clear(); ganttSelectedObras.add(obra); }}
      }}
      refreshGanttObraPills();
      buildGantt();

    }} else if (btn.dataset.ganttFunc !== undefined) {{
      const func = btn.dataset.ganttFunc;
      if (func === 'ALL') {{
        ganttSelectedFuncs.clear();
      }} else if (e.ctrlKey || e.metaKey) {{
        if (ganttSelectedFuncs.has(func)) ganttSelectedFuncs.delete(func);
        else ganttSelectedFuncs.add(func);
      }} else {{
        if (ganttSelectedFuncs.size === 1 && ganttSelectedFuncs.has(func)) ganttSelectedFuncs.clear();
        else {{ ganttSelectedFuncs.clear(); ganttSelectedFuncs.add(func); }}
      }}
      refreshGanttFuncPills();
      buildGantt();
    }}
  }});
}}

function refreshGanttObraPills() {{
  const allPill = document.querySelector('[data-gantt-obra="ALL"]');
  if (allPill) allPill.classList.toggle('active', ganttSelectedObras.size === 0);
  DATA.obras.forEach((obra, i) => {{
    const btn = document.querySelector(`[data-gantt-obra="${{obra}}"]`);
    if (!btn) return;
    const isActive = ganttSelectedObras.has(obra);
    const color = OBRA_COLORS[i % OBRA_COLORS.length];
    btn.classList.toggle('multi-active', isActive);
    btn.classList.toggle('active', isActive);
    btn.style.background = isActive ? color : '';
    btn.style.color = isActive ? '#000' : '';
    btn.style.borderColor = isActive ? color : color + '66';
  }});
  // badge
  const badge = document.getElementById('gantt-obra-badge');
  if (ganttSelectedObras.size > 1) {{
    badge.textContent = ganttSelectedObras.size;
    badge.style.display = 'inline-flex';
  }} else {{
    badge.style.display = 'none';
  }}
}}

function refreshGanttFuncPills() {{
  const allPill = document.querySelector('[data-gantt-func="ALL"]');
  if (allPill) allPill.classList.toggle('active', ganttSelectedFuncs.size === 0);
  DATA.funcoes.forEach((func, i) => {{
    const btn = document.querySelector(`[data-gantt-func="${{func}}"]`);
    if (!btn) return;
    const isActive = ganttSelectedFuncs.has(func);
    const color = FUNC_COLORS[i % FUNC_COLORS.length];
    btn.classList.toggle('multi-active', isActive);
    btn.classList.toggle('active', isActive);
    btn.style.background = isActive ? color : '';
    btn.style.color = isActive ? '#000' : '';
    btn.style.borderColor = isActive ? color : color + '66';
  }});
  // badge
  const badge = document.getElementById('gantt-func-badge');
  if (ganttSelectedFuncs.size > 1) {{
    badge.textContent = ganttSelectedFuncs.size;
    badge.style.display = 'inline-flex';
  }} else {{
    badge.style.display = 'none';
  }}
}}

// ── GANTT CHART ──────────────────────────────────────────────────────
function buildGantt() {{
  const table = document.getElementById('gantt-table');
  table.innerHTML = '';

  // Determine which obras to show
  let filteredObras = DATA.obras;
  if (ganttFilterCity !== 'ALL') {{
    filteredObras = filteredObras.filter(o => (DATA.obra_cidade[o] || '') === ganttFilterCity);
  }}
  if (ganttSelectedObras.size > 0) {{
    filteredObras = filteredObras.filter(o => ganttSelectedObras.has(o));
  }}

  let globalMax = 0;
  filteredObras.forEach(obra => {{
    DATA.funcoes.forEach(func => {{
      const row = DATA.obra_func_data[obra]?.[func] || [];
      row.forEach(v => {{ if (v > globalMax) globalMax = v; }});
    }});
  }});
  if (globalMax === 0) globalMax = 1;

  const thead = document.createElement('thead');
  const headerTr = document.createElement('tr');

  const thObra = document.createElement('th');
  thObra.className = 'header-obra-col';
  thObra.style.width = ganttColWidths.obra + 'px';
  thObra.style.minWidth = ganttColWidths.obra + 'px';
  thObra.style.position = 'sticky';
  thObra.style.left = '0';
  thObra.innerHTML = 'Obra<div class="col-resizer" data-col="obra"></div>';
  headerTr.appendChild(thObra);

  const thFunc = document.createElement('th');
  thFunc.className = 'header-func-col';
  thFunc.style.width = ganttColWidths.func + 'px';
  thFunc.style.minWidth = ganttColWidths.func + 'px';
  thFunc.style.left = ganttColWidths.obra + 'px';
  thFunc.innerHTML = 'Função<div class="col-resizer" data-col="func"></div>';
  headerTr.appendChild(thFunc);
  DATA.months.forEach((m, mi) => {{
    const th = document.createElement('th');
    th.className = 'month-th'; th.dataset.monthIdx = mi;
    if (mi % currentInterval !== 0) th.classList.add('interval-hidden');
    const span = document.createElement('span');
    span.className = 'month-label';
    span.textContent = m;
    th.appendChild(span);
    headerTr.appendChild(th);
  }});
  thead.appendChild(headerTr);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');

  filteredObras.forEach((obra, oi) => {{
    const obraColor = OBRA_COLORS[DATA.obras.indexOf(obra) % OBRA_COLORS.length];
    let activeFuncs = DATA.funcoes.filter(func => {{
      const row = DATA.obra_func_data[obra]?.[func] || [];
      return row.some(v => v > 0);
    }});
    // Apply function filter (multi-select)
    if (ganttSelectedFuncs.size > 0) {{
      activeFuncs = activeFuncs.filter(f => ganttSelectedFuncs.has(f));
    }}
    if (activeFuncs.length === 0) return;

    activeFuncs.forEach((func, fi) => {{
      const funcIdx = DATA.funcoes.indexOf(func);
      const funcColor = FUNC_COLORS[funcIdx % FUNC_COLORS.length];
      const funcRow = DATA.obra_func_data[obra]?.[func] || new Array(DATA.months.length).fill(0);
      const tr = document.createElement('tr');

      if (fi === 0) {{
        const tdObra = document.createElement('td');
        tdObra.className = 'obra-col';
        tdObra.textContent = obra;
        tdObra.style.borderLeft = `3px solid ${{obraColor}}`;
        tdObra.style.width = ganttColWidths.obra + 'px';
        tdObra.style.minWidth = ganttColWidths.obra + 'px';
        tdObra.style.left = '0';
        tdObra.rowSpan = activeFuncs.length;
        tr.appendChild(tdObra);
      }}

      const tdFunc = document.createElement('td');
      tdFunc.className = 'func-col';
      const shortFunc = func.length > 22 ? func.substring(0, 21) + '…' : func;
      tdFunc.textContent = shortFunc; tdFunc.title = func;
      tdFunc.style.borderLeft = `2px solid ${{funcColor}}44`;
      tdFunc.style.width = ganttColWidths.func + 'px';
      tdFunc.style.minWidth = ganttColWidths.func + 'px';
      tdFunc.style.left = ganttColWidths.obra + 'px';
      tr.appendChild(tdFunc);

      DATA.months.forEach((m, mi) => {{
        const v = funcRow[mi] || 0;
        const td = document.createElement('td');
        td.className = 'gantt-cell'; td.dataset.monthIdx = mi;
        if (mi % currentInterval !== 0) td.classList.add('interval-hidden');
        if (v > 0) {{
          const alpha = 0.2 + (v / globalMax) * 0.8;
          const inner = document.createElement('div');
          inner.className = 'gantt-cell-inner';
          inner.style.background = funcColor;
          inner.style.opacity = alpha.toFixed(2);
          inner.title = `${{obra}} · ${{func}} · ${{m}}: ${{v}} trab.`;
          if (v >= 5) inner.textContent = v;
          td.appendChild(inner);
          td.title = `${{obra}} · ${{func}} · ${{m}}: ${{v}} trabalhadores`;
        }}
        tr.appendChild(td);
      }});
      tbody.appendChild(tr);
    }});

    const sepTr = document.createElement('tr');
    const sepTd = document.createElement('td');
    sepTd.colSpan = DATA.months.length + 2;
    sepTd.style.cssText = 'height:4px;background:var(--border);padding:0;';
    sepTr.appendChild(sepTd);
    tbody.appendChild(sepTr);
  }});
  table.appendChild(tbody);
  buildGanttLegend(filteredObras);
}}

function buildGanttLegend(filteredObras) {{
  const container = document.getElementById('gantt-legend');
  container.innerHTML = '';
  const obras = filteredObras || DATA.obras;
  const usedFuncs = new Set();
  obras.forEach(obra => {{
    DATA.funcoes.forEach(func => {{
      if (ganttSelectedFuncs.size > 0 && !ganttSelectedFuncs.has(func)) return;
      const row = DATA.obra_func_data[obra]?.[func] || [];
      if (row.some(v => v > 0)) usedFuncs.add(func);
    }});
  }});
  [...usedFuncs].forEach(func => {{
    const idx = DATA.funcoes.indexOf(func);
    const color = FUNC_COLORS[idx % FUNC_COLORS.length];
    const item = document.createElement('div');
    item.className = 'gantt-legend-item';
    item.innerHTML = `<div class="gantt-legend-dot" style="background:${{color}}"></div><span>${{func}}</span>`;
    container.appendChild(item);
  }});
}}

// ── PDF EXPORT — MAX 3 PAGES, DARK BG ────────────────────────────────
async function exportPDF() {{
  const btn = document.getElementById('pdf-export-btn');
  const overlay = document.getElementById('pdf-overlay');
  const progress = document.getElementById('pdf-progress');
  btn.disabled = true;
  overlay.style.display = 'flex';
  btn.style.visibility = 'hidden';

  try {{
    const {{ jsPDF }} = window.jspdf;
    const pdf = new jsPDF({{ orientation: 'landscape', unit: 'mm', format: 'a3' }});
    const pageW = pdf.internal.pageSize.getWidth();
    const pageH = pdf.internal.pageSize.getHeight();
    const margin = 8;

    const html2canvasOpts = {{
      scale: 1.6, backgroundColor: '#0a0c10',
      useCORS: true, logging: false, allowTaint: true,
    }};

    progress.textContent = 'Capturando página 1 — KPIs e Histograma...';
    const page1El = document.createElement('div');
    page1El.style.cssText = 'background:#0a0c10;padding:16px;';
    page1El.appendChild(document.getElementById('city-filter-bar').cloneNode(true));
    page1El.appendChild(document.querySelector('.kpi-grid').cloneNode(true));
    page1El.appendChild(document.querySelector('.main-grid').cloneNode(true));
    document.body.appendChild(page1El);
    const c1 = await html2canvas(page1El, html2canvasOpts);
    document.body.removeChild(page1El);
    const img1 = c1.toDataURL('image/jpeg', 0.93);
    const w1 = pageW - margin * 2;
    const h1 = Math.min((c1.height * w1) / c1.width, pageH - margin * 2);
    pdf.setFillColor(10, 12, 16); pdf.rect(0, 0, pageW, pageH, 'F');
    pdf.addImage(img1, 'JPEG', margin, margin, w1, h1);

    progress.textContent = 'Capturando página 2 — Funções, Sobreposição e Mapa de Calor...';
    pdf.addPage();
    const page2El = document.createElement('div');
    page2El.style.cssText = 'background:#0a0c10;padding:16px;';
    page2El.appendChild(document.querySelector('.bottom-grid').cloneNode(true));
    page2El.appendChild(document.getElementById('heatmap-card').cloneNode(true));
    document.body.appendChild(page2El);
    const c2 = await html2canvas(page2El, html2canvasOpts);
    document.body.removeChild(page2El);
    const img2 = c2.toDataURL('image/jpeg', 0.93);
    const w2 = pageW - margin * 2;
    const h2 = Math.min((c2.height * w2) / c2.width, pageH - margin * 2);
    pdf.setFillColor(10, 12, 16); pdf.rect(0, 0, pageW, pageH, 'F');
    pdf.addImage(img2, 'JPEG', margin, margin, w2, h2);

    progress.textContent = 'Capturando página 3 — Gantt de Mão de Obra...';
    pdf.addPage();
    const ganttCard = document.getElementById('gantt-card');
    const ganttContainerEl = document.getElementById('gantt-container');
    const origMaxH = ganttContainerEl.style.maxHeight;
    const origOvY = ganttContainerEl.style.overflowY;
    ganttContainerEl.style.maxHeight = 'none';
    ganttContainerEl.style.overflowY = 'visible';
    const c3 = await html2canvas(ganttCard, {{ ...html2canvasOpts, scale: 1.2 }});
    ganttContainerEl.style.maxHeight = origMaxH;
    ganttContainerEl.style.overflowY = origOvY;
    const img3 = c3.toDataURL('image/jpeg', 0.93);
    const w3 = pageW - margin * 2;
    const h3 = Math.min((c3.height * w3) / c3.width, pageH - margin * 2);
    pdf.setFillColor(10, 12, 16); pdf.rect(0, 0, pageW, pageH, 'F');
    pdf.addImage(img3, 'JPEG', margin, margin, w3, h3);

    progress.textContent = 'Salvando PDF...';
    pdf.save('histograma_mao_de_obra.pdf');
  }} catch (err) {{
    alert('Erro ao gerar PDF: ' + err.message);
    console.error(err);
  }} finally {{
    btn.disabled = false;
    btn.style.visibility = 'visible';
    overlay.style.display = 'none';
  }}
}}

// ── INIT ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {{
  buildCityFilterBar();
  buildFilterTabs(); buildObraList(); buildFuncPills();
  buildOverlapTable(); buildHeatmap();
  buildGanttFilters(); buildGantt(); initGanttResize();
  initMainChart(); initFuncChart();
  updateMainChart();
  applyInterval(3);
}});
</script>
</body>
</html>"""
    return html
