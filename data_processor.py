import pandas as pd
import json
from pathlib import Path


def load_excel(filepath: str) -> dict:
    """Load and process Excel file into dashboard data structure."""
    df = pd.read_excel(filepath)

    col_map = _detect_columns(df)
    df = df.rename(columns=col_map)

    required = ['OBRA', 'PERÍODO', 'QTD', 'FUNÇÃO']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória não encontrada: '{col}'. "
                             f"Colunas disponíveis: {list(df.columns)}")

    has_cidade = 'CIDADE' in df.columns
    cols = required + (['CIDADE'] if has_cidade else [])
    df = df[cols].dropna(subset=['OBRA', 'PERÍODO', 'QTD'])
    df['PERÍODO'] = pd.to_datetime(df['PERÍODO'])
    df['PERÍODO'] = df['PERÍODO'].values.astype('datetime64[M]').astype('datetime64[ns]')
    df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
    df['FUNÇÃO'] = df['FUNÇÃO'].astype(str).str.strip()
    df['OBRA'] = df['OBRA'].astype(str).str.strip()
    df['CIDADE'] = df['CIDADE'].astype(str).str.strip() if has_cidade else 'Todas'

    return _build_dashboard_data(df)


def _detect_columns(df: pd.DataFrame) -> dict:
    mapping = {}
    candidates = {
        'OBRA': ['obra', 'empreendimento', 'projeto', 'building', 'canteiro'],
        'PERÍODO': ['período', 'periodo', 'mes', 'mês', 'data', 'month', 'date', 'competencia', 'competência'],
        'QTD': ['qtd', 'quantidade', 'qty', 'workers', 'trabalhadores', 'funcionarios', 'funcionários', 'headcount'],
        'FUNÇÃO': ['função', 'funcao', 'cargo', 'role', 'especialidade', 'ofício', 'oficio', 'trade'],
        'CIDADE': ['cidade', 'city', 'municipio', 'município', 'localidade', 'local', 'regiao', 'região'],
    }
    for target, synonyms in candidates.items():
        for col in df.columns:
            if col.lower().strip() in synonyms or col.upper().strip() == target:
                mapping[col] = target
                break
    return mapping


def _build_dashboard_data(df: pd.DataFrame) -> dict:
    months_raw = sorted(df['PERÍODO'].unique())
    months = [pd.Timestamp(m).strftime('%b/%y') for m in months_raw]
    months_iso = [pd.Timestamp(m).strftime('%Y-%m') for m in months_raw]

    obras = sorted(df['OBRA'].unique().tolist())
    funcoes = sorted(df['FUNÇÃO'].unique().tolist())
    cidades = sorted(df['CIDADE'].unique().tolist())
    obra_cidade = df.drop_duplicates('OBRA').set_index('OBRA')['CIDADE'].to_dict()

    pivot_obra = df.groupby(['PERÍODO', 'OBRA'])['QTD'].sum().unstack(fill_value=0)
    pivot_obra = pivot_obra.reindex(months_raw, fill_value=0)
    obra_data = {}
    for obra in obras:
        obra_data[obra] = [int(pivot_obra[obra].get(m, 0)) for m in months_raw] if obra in pivot_obra.columns else [0]*len(months_raw)

    pivot_func = df.groupby(['PERÍODO', 'FUNÇÃO'])['QTD'].sum().unstack(fill_value=0)
    pivot_func = pivot_func.reindex(months_raw, fill_value=0)
    func_data = {}
    for func in funcoes:
        func_data[func] = [int(pivot_func[func].get(m, 0)) for m in months_raw] if func in pivot_func.columns else [0]*len(months_raw)

    total = [sum(obra_data[o][i] for o in obras) for i in range(len(months_raw))]

    obra_by_month = df.groupby(['OBRA', 'PERÍODO'])['QTD'].sum().reset_index()
    obra_peaks = {}
    for obra in obras:
        sub = obra_by_month[obra_by_month['OBRA'] == obra]
        if not sub.empty:
            idx = sub['QTD'].idxmax()
            obra_peaks[obra] = {
                'peak': int(sub.loc[idx, 'QTD']),
                'month': pd.Timestamp(sub.loc[idx, 'PERÍODO']).strftime('%b/%y')
            }

    func_by_month = df.groupby(['FUNÇÃO', 'PERÍODO'])['QTD'].sum().reset_index()
    func_peaks = {}
    for func in funcoes:
        sub = func_by_month[func_by_month['FUNÇÃO'] == func]
        if not sub.empty:
            idx = sub['QTD'].idxmax()
            func_peaks[func] = {
                'v': int(sub.loc[idx, 'QTD']),
                'm': pd.Timestamp(sub.loc[idx, 'PERÍODO']).strftime('%b/%y')
            }

    obra_totals = df.groupby('OBRA')['QTD'].sum().astype(int).to_dict()

    obra_func_data = {}
    for obra in obras:
        obra_func_data[obra] = {}
        sub = df[df['OBRA'] == obra]
        piv = sub.groupby(['PERÍODO', 'FUNÇÃO'])['QTD'].sum().unstack(fill_value=0)
        piv = piv.reindex(months_raw, fill_value=0)
        for func in funcoes:
            if func in piv.columns:
                obra_func_data[obra][func] = [int(piv[func].get(m, 0)) for m in months_raw]
            else:
                obra_func_data[obra][func] = [0]*len(months_raw)

    peak_total = max(total) if total else 0
    peak_month = months[total.index(peak_total)] if total else ''
    grand_total = sum(total)
    duration = len(months)
    num_obras = len(obras)

    return {
        'months': months,
        'months_iso': months_iso,
        'obras': obras,
        'funcoes': funcoes,
        'cidades': cidades,
        'obra_cidade': obra_cidade,
        'obra_data': obra_data,
        'func_data': func_data,
        'obra_func_data': obra_func_data,
        'total': total,
        'peak_total': peak_total,
        'peak_month': peak_month,
        'grand_total': grand_total,
        'duration': duration,
        'num_obras': num_obras,
        'obra_peaks': obra_peaks,
        'obra_totals': obra_totals,
        'func_peaks': func_peaks,
    }
