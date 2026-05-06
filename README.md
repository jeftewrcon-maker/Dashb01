# ⚡ Histograma de Mão de Obra

Dashboard interativo dark para visualizar sobreposição, superlocação e atrito de mão de obra entre múltiplas obras.

---

## 📋 Requisitos

- Python 3.8 ou superior
- pip

---

## 🚀 Instalação

```bash
pip install -r requirements.txt
python main.py
```

---

## 🖥️ Uso

### Interface Gráfica (recomendado)
```bash
python main.py
```
1. Clique em **📂 Importar Excel** (ou clique na área de drop)
2. Selecione seu arquivo `.xlsx`
3. O dashboard abre automaticamente no navegador

### Linha de Comando
```bash
python main.py sua_base.xlsx
python main.py sua_base.xlsx dashboard_output.html
```

---

## 📊 Formato do Excel

| Coluna | Aceita também | Descrição |
|--------|---------------|-----------|
| `OBRA` | obra, empreendimento, projeto | Nome da obra/empreendimento |
| `PERÍODO` | período, data, mês | Data no formato mês/ano ou AAAA-MM-DD |
| `QTD` | quantidade, qtd, workers | Número de trabalhadores |
| `FUNÇÃO` | função, cargo, role | Especialidade/função |
| `CIDADE` | cidade, city, municipio *(opcional)* | Cidade da obra (ex: Ipatinga, GV) |

**Exemplo com CIDADE:**

| OBRA | PERÍODO | QTD | FUNÇÃO | CIDADE |
|------|---------|-----|--------|--------|
| Bom Retiro | 2026-01-01 | 17 | Armador | Ipatinga |
| Copenhagen | 2026-04-01 | 70 | Servente | GV |

---

## 📈 Funcionalidades do Dashboard

- **Filtro por Cidade** — Filtra todas as seções por Ipatinga, GV ou qualquer cidade na planilha
- **Histograma Empilhado** — Visão mensal de todos os trabalhadores por obra
- **Filtro por Obra** — Clique em qualquer obra para isolar no gráfico
- **Painel de Resumo** — Pico e total func-mês por obra
- **Gráfico por Função** — Demanda de cada especialidade ao longo do tempo
- **Tabela de Sobreposição** — Ranking de intensidade de alocação
- **Mapa de Calor** — Visão matricial Obras × Meses
- **Gantt com triplo filtro** — Filtre por cidade, obra e/ou função simultaneamente
- **Exportar PDF** — Exporta em exatamente 3 páginas com tema escuro preservado

---

## 📁 Estrutura do Projeto

```
histograma_project/
├── main.py              # Aplicativo principal (GUI + CLI)
├── data_processor.py    # Processamento do Excel (detecta CIDADE)
├── html_generator.py    # Geração do HTML do dashboard
├── requirements.txt     # Dependências Python
└── README.md
```
