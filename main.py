"""
Histograma de Mão de Obra — Aplicativo Principal
Requer: pip install pandas openpyxl
"""
import sys
import os
import json
import threading
import webbrowser
import tempfile
from pathlib import Path

# Check dependencies before importing tkinter (so error is clear)
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("ERRO: tkinter não encontrado. Instale o Python com suporte a tkinter.")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERRO: pandas não instalado. Execute: pip install pandas openpyxl")
    sys.exit(1)

from data_processor import load_excel
from html_generator import generate_html


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Histograma de Mão de Obra")
        self.geometry("680x480")
        self.resizable(False, False)
        self.configure(bg="#0a0c10")

        self._current_data = None
        self._current_html = None
        self._temp_html = None

        self._build_ui()
        self._center_window()

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Title bar area
        header = tk.Frame(self, bg="#111418", pady=20)
        header.pack(fill="x")
        tk.Label(header, text="⚡  Histograma de Mão de Obra",
                 font=("Helvetica", 16, "bold"), bg="#111418", fg="#e2e8f0").pack()
        tk.Label(header, text="Sobreposição · Superlocação · Atrito entre Obras",
                 font=("Helvetica", 10), bg="#111418", fg="#64748b").pack(pady=(4, 0))

        # Drop zone
        self.drop_frame = tk.Frame(self, bg="#0a0c10", pady=30)
        self.drop_frame.pack(fill="x", padx=40)

        self.drop_label = tk.Label(
            self.drop_frame,
            text="📂  Arraste um arquivo Excel aqui\nou clique em Importar para selecionar",
            font=("Helvetica", 12), bg="#1a1f28",
            fg="#64748b", pady=40, relief="flat",
            cursor="hand2"
        )
        self.drop_label.pack(fill="x")
        self.drop_label.bind("<Button-1>", lambda e: self._browse_file())

        # Status bar
        self.status_var = tk.StringVar(value="Nenhum arquivo carregado")
        status_bar = tk.Label(self, textvariable=self.status_var,
                              font=("Courier", 10), bg="#0a0c10", fg="#64748b",
                              anchor="w", padx=40)
        status_bar.pack(fill="x")

        # Progress
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=600)
        self.progress.pack(pady=(8, 0), padx=40)

        # File info card
        self.info_frame = tk.Frame(self, bg="#111418", pady=14, padx=20)
        self.info_frame.pack(fill="x", padx=40, pady=12)
        self.info_text = tk.Label(self.info_frame, text="", font=("Courier", 10),
                                  bg="#111418", fg="#94a3b8", justify="left", anchor="w")
        self.info_text.pack(fill="x")

        # Buttons
        btn_frame = tk.Frame(self, bg="#0a0c10")
        btn_frame.pack(pady=10)

        self._btn_import = self._btn(btn_frame, "📂  Importar Excel", self._browse_file,
                                     "#1e2530", "#00d4ff")
        self._btn_import.pack(side="left", padx=6)

        self._btn_view = self._btn(btn_frame, "🌐  Abrir Dashboard", self._open_dashboard,
                                   "#7c3aed", "#fff")
        self._btn_view.pack(side="left", padx=6)
        self._btn_view.config(state="disabled")

        self._btn_save = self._btn(btn_frame, "💾  Salvar HTML", self._save_html,
                                   "#1e2530", "#f59e0b")
        self._btn_save.pack(side="left", padx=6)
        self._btn_save.config(state="disabled")

        self._btn_json = self._btn(btn_frame, "📋  Exportar JSON", self._save_json,
                                   "#1e2530", "#10b981")
        self._btn_json.pack(side="left", padx=6)
        self._btn_json.config(state="disabled")

        # Footer
        tk.Label(self, text="Suporta colunas: OBRA · PERÍODO · QTD · FUNÇÃO",
                 font=("Helvetica", 9), bg="#0a0c10", fg="#374151").pack(pady=(0, 8))

    def _btn(self, parent, text, command, bg, fg):
        return tk.Button(parent, text=text, command=command,
                         font=("Helvetica", 11, "bold"), bg=bg, fg=fg,
                         relief="flat", padx=16, pady=10, cursor="hand2",
                         activebackground=bg, activeforeground=fg)

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── ACTIONS ───────────────────────────────────────────────────────
    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar Base Excel",
            filetypes=[("Excel files", "*.xlsx *.xls *.xlsm"), ("All files", "*.*")]
        )
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        self.status_var.set(f"Carregando: {Path(path).name} …")
        self.progress.start(12)
        self._btn_view.config(state="disabled")
        self._btn_save.config(state="disabled")
        self._btn_json.config(state="disabled")

        def worker():
            try:
                data = load_excel(path)
                html = generate_html(data)
                self.after(0, lambda: self._on_load_success(path, data, html))
            except Exception as exc:
                self.after(0, lambda: self._on_load_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_load_success(self, path, data, html):
        self.progress.stop()
        self._current_data = data
        self._current_html = html

        # Info card
        months_range = f"{data['months'][0]} → {data['months'][-1]}" if data['months'] else '—'
        grand = f"{data['grand_total']:,}".replace(',', '.')
        info = (
            f"  Arquivo : {Path(path).name}\n"
            f"  Obras   : {data['num_obras']}   |   Funções: {len(data['funcoes'])}\n"
            f"  Período : {months_range}   ({data['duration']} meses)\n"
            f"  Pico    : {data['peak_total']} trab. em {data['peak_month']}\n"
            f"  Total   : {grand} func-mês"
        )
        self.info_text.config(text=info)
        self.drop_label.config(fg="#00d4ff", text=f"✅  {Path(path).name} carregado com sucesso")

        self.status_var.set("✅  Dashboard pronto!")
        self._btn_view.config(state="normal")
        self._btn_save.config(state="normal")
        self._btn_json.config(state="normal")

        # Auto-open
        self._open_dashboard()

    def _on_load_error(self, msg):
        self.progress.stop()
        self.status_var.set("❌  Erro ao carregar arquivo")
        messagebox.showerror("Erro ao Importar", f"Não foi possível processar o arquivo:\n\n{msg}")

    def _open_dashboard(self):
        if not self._current_html:
            return
        # Write to temp file and open
        if self._temp_html and Path(self._temp_html).exists():
            try:
                os.unlink(self._temp_html)
            except Exception:
                pass
        tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False,
                                          mode="w", encoding="utf-8")
        tmp.write(self._current_html)
        tmp.close()
        self._temp_html = tmp.name
        webbrowser.open(f"file://{self._temp_html}")
        self.status_var.set(f"🌐  Dashboard aberto no navegador")

    def _save_html(self):
        if not self._current_html:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            initialfile="histograma_mao_de_obra.html"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._current_html)
            self.status_var.set(f"💾  Salvo: {Path(path).name}")
            messagebox.showinfo("Salvo", f"Dashboard HTML salvo em:\n{path}")

    def _save_json(self):
        if not self._current_data:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="histograma_data.json"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._current_data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"📋  JSON salvo: {Path(path).name}")

    def destroy(self):
        if self._temp_html and Path(self._temp_html).exists():
            try:
                os.unlink(self._temp_html)
            except Exception:
                pass
        super().destroy()


# ── CLI MODE (sem GUI) ────────────────────────────────────────────────
def cli_mode(excel_path: str, output_path: str = None):
    """Run without GUI: python main.py arquivo.xlsx [saida.html]"""
    print(f"Processando: {excel_path}")
    data = load_excel(excel_path)
    html = generate_html(data)
    out = output_path or excel_path.replace(".xlsx", "_dashboard.html").replace(".xls", "_dashboard.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard gerado: {out}")
    print(f"Obras: {data['num_obras']} | Pico: {data['peak_total']} ({data['peak_month']}) | Total: {data['grand_total']} func-mês")
    webbrowser.open(f"file://{Path(out).resolve()}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode
        excel = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else None
        cli_mode(excel, output)
    else:
        # GUI mode
        app = App()
        app.mainloop()
