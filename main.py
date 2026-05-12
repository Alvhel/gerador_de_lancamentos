import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os

# ─────────────────────────────────────────────
# Lógica dos scripts originais (internalizada)
# ─────────────────────────────────────────────

def extrair_extrato_de_pdf(pdf_path):
    import fitz
    import pandas as pd
    import re

    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    linhas = text.splitlines()
    registros = []
    cliente_atual = None
    data_ultimo_cred = None
    i = 0

    while i < len(linhas):
        linha = linhas[i].strip()

        cliente_match = re.match(r"^(\d+)\s+-\s+(.+)$", linha)
        if cliente_match:
            cliente_atual = cliente_match.group(2).strip()
            i += 1
            continue

        entrada_match = re.match(r"^(\d{4,5}) (.+?)\s*$", linha)
        if entrada_match and cliente_atual:
            descricao_completa = entrada_match.group(2).strip()
            try:
                data_cred = linhas[i + 4].strip()
                valor = linhas[i + 5].strip().replace("R$ ", "").replace(".", "").replace(",", ".")
                if re.match(r"^-?\d+\.\d{2}$", valor):
                    data_ultimo_cred = data_cred
                    registros.append({
                        "Data": data_cred,
                        "Descrição": f"{cliente_atual} - {descricao_completa}",
                        "Valor": float(valor)
                    })
                    i += 6
                    continue
            except IndexError:
                pass

        total_match = re.match(r"^R\$\s*([\d\.]+,\d{2})$", linha)
        if total_match and cliente_atual:
            valor_total = total_match.group(1).replace(".", "").replace(",", ".")
            registros.append({
                "Data": data_ultimo_cred,
                "Descrição": f"{cliente_atual} - pagamento",
                "Valor": float(valor_total)
            })

        i += 1

    df = pd.DataFrame(registros)
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    return df


def gerar_lancamentos_contabeis(df_extrato, plano_contas_path):
    import pandas as pd
    import re
    from difflib import get_close_matches

    df_plano = pd.read_excel(plano_contas_path)
    df_plano["Nome"] = df_plano["Nome"].str.strip().str.lower()

    mapa_clientes = {
        nome: codigo for codigo, nome in zip(df_plano["Código"], df_plano["Nome"])
    }
    nomes_clientes = list(mapa_clientes.keys())
    lancamentos = []

    for _, row in df_extrato.iterrows():
        descricao = str(row["Descrição"])
        data = row["Data"]
        valor = round(abs(row["Valor"]), 2)

        cliente_match = re.match(r"^(.*?)\s*-", descricao)
        nome_extraido = cliente_match.group(1).strip().lower() if cliente_match else ""

        nome_proximo = get_close_matches(nome_extraido, nomes_clientes, n=1, cutoff=1)
        conta_cliente = mapa_clientes.get(nome_proximo[0]) if nome_proximo else None
        desc_lower = descricao.lower()

        if "aluguel" in desc_lower:
            continue
        elif "bônus" in desc_lower:
            lancamentos.append({"Data": data, "Débito": 1155, "Crédito": conta_cliente or 3930, "Valor": valor, "Descrição": descricao})
        elif "taxa bancária" in desc_lower:
            lancamentos.append({"Data": data, "Débito": 1155, "Crédito": conta_cliente or 3930, "Valor": valor, "Descrição": descricao})
        elif "pagamento a maior" in desc_lower:
            lancamentos.append({"Data": data, "Débito": conta_cliente or 3930, "Crédito": 2836, "Valor": valor, "Descrição": descricao})
        elif "juros" in desc_lower:
            lancamentos.append({"Data": data, "Débito": conta_cliente or 3930, "Crédito": 2836, "Valor": valor, "Descrição": descricao})
        elif "multa" in desc_lower:
            lancamentos.append({"Data": data, "Débito": conta_cliente or 3930, "Crédito": 4499, "Valor": valor, "Descrição": descricao})
        elif "pagamento" in desc_lower:
            lancamentos.append({"Data": data, "Débito": 51, "Crédito": conta_cliente or 3930, "Valor": valor, "Descrição": descricao})

    df_lcto = pd.DataFrame(lancamentos)
    df_lcto["Data"] = pd.to_datetime(df_lcto["Data"])
    df_lcto.insert(0, "Sequência", 0)
    df_lcto["Histórico"] = 547
    df_lcto = df_lcto[["Sequência", "Data", "Débito", "Crédito", "Valor", "Histórico", "Descrição"]]
    return df_lcto


def exportar_txt(df_lcto, saida_txt_path):
    import pandas as pd
    df = df_lcto.copy()
    if "Data" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Data"]):
        df["Data"] = df["Data"].dt.strftime("%d/%m/%Y")
    df.to_csv(saida_txt_path, sep=",", index=False)


# ─────────────────────────────────────────────
# Paleta
# ─────────────────────────────────────────────
BG         = "#0E1420"
CARD       = "#161E2E"
TEXT_MAIN  = "#EDF0F7"
TEXT_SEC   = "#7A8299"
ACCENT     = "#00C2D1"
ACCENT_DRK = "#1A3A4A"


# ─────────────────────────────────────────────
# GUI
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lançamentos Contábeis · Fênix")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._build_ui()

    def _build_ui(self):
        PAD = 20

        # ── cabeçalho
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=PAD, pady=(PAD, 0))
        tk.Label(header, text="LANÇAMENTOS CONTÁBEIS",
                 font=("Helvetica", 15, "bold"),
                 bg=BG, fg=ACCENT).pack(anchor="w")
        tk.Label(header, text="Fênix · Automação de Relatórios",
                 font=("Helvetica", 9), bg=BG, fg=TEXT_SEC).pack(anchor="w")

        # separador accent
        tk.Frame(self, bg=ACCENT, height=1).pack(fill="x", padx=PAD, pady=(10, 0))

        # ── card de inputs
        card = tk.Frame(self, bg=CARD, padx=PAD, pady=PAD)
        card.pack(padx=PAD, pady=PAD, fill="x")
        card.grid_columnconfigure(1, weight=1)

        self.var_pdf   = tk.StringVar()
        self.var_plano = tk.StringVar()
        self.var_saida = tk.StringVar()

        # seção ENTRADA
        self._section_label(card, "ENTRADA", row=0)
        self._field(card, "Arquivo de cobrança (.pdf)",  self.var_pdf,   self._browse_pdf,   row=1)
        self._field(card, "Plano de contas (.xlsx)",     self.var_plano, self._browse_plano, row=3)

        # seção SAÍDA
        self._section_label(card, "SAÍDA", row=5)
        self._field(card, "Salvar lançamento como (.txt)", self.var_saida, self._save_saida, row=6)

        # ── progress bar
        style = ttk.Style()
        style.theme_use("default")
        style.configure("F.Horizontal.TProgressbar",
                        troughcolor=CARD, background=ACCENT,
                        thickness=4, borderwidth=0)
        self.progress = ttk.Progressbar(self, style="F.Horizontal.TProgressbar",
                                        mode="indeterminate")
        self.progress.pack(fill="x", padx=PAD)

        # ── log
        log_wrap = tk.Frame(self, bg=CARD, padx=10, pady=8)
        log_wrap.pack(padx=PAD, pady=(PAD, 0), fill="x")
        self.log = tk.Text(log_wrap, height=6, bg=CARD, fg=TEXT_SEC,
                           font=("Courier", 8), relief="flat",
                           state="disabled", wrap="word",
                           insertbackground=ACCENT,
                           selectbackground=ACCENT_DRK)
        self.log.pack(fill="x")
        self.log.tag_configure("ok",  foreground=ACCENT)
        self.log.tag_configure("err", foreground="#FF6B6B")

        # ── botão executar
        tk.Button(self, text="▶   GERAR LANÇAMENTOS",
                  command=self._executar_thread,
                  bg=ACCENT, fg=BG,
                  font=("Helvetica", 10, "bold"),
                  relief="flat", padx=20, pady=11,
                  cursor="hand2",
                  activebackground="#00A8B5",
                  activeforeground=BG).pack(pady=PAD, ipadx=10)

    # ── helpers de layout ────────────────────────────
    def _section_label(self, parent, texto, row):
        tk.Label(parent, text=texto,
                 font=("Helvetica", 7, "bold"),
                 bg=CARD, fg=ACCENT).grid(
            row=row, column=0, columnspan=3,
            sticky="w", pady=(14, 2))

    def _field(self, parent, label, var, cmd, row):
        tk.Label(parent, text=label,
                 font=("Helvetica", 8),
                 bg=CARD, fg=TEXT_SEC, anchor="w").grid(
            row=row, column=0, columnspan=3, sticky="w", pady=(2, 1))

        tk.Entry(parent, textvariable=var,
                 font=("Courier", 9), width=50,
                 bg=ACCENT_DRK, fg=TEXT_MAIN,
                 insertbackground=ACCENT,
                 relief="flat", bd=6,
                 highlightthickness=1,
                 highlightcolor=ACCENT,
                 highlightbackground=CARD).grid(
            row=row+1, column=0, columnspan=2, sticky="ew", padx=(0, 6))

        tk.Button(parent, text="…", command=cmd,
                  bg=ACCENT_DRK, fg=ACCENT,
                  font=("Helvetica", 9, "bold"),
                  relief="flat", padx=10,
                  cursor="hand2",
                  activebackground=ACCENT,
                  activeforeground=BG).grid(row=row+1, column=2, sticky="ew")

    # ── browse helpers ───────────────────────────────
    def _browse_pdf(self):
        p = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if p: self.var_pdf.set(p)

    def _browse_plano(self):
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if p: self.var_plano.set(p)

    def _save_saida(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("Texto estruturado", "*.txt")])
        if p: self.var_saida.set(p)

    # ── log helper ───────────────────────────────────
    def _log(self, msg, tag=None):
        self.log.configure(state="normal")
        self.log.insert("end", f"› {msg}\n", tag or "")
        self.log.see("end")
        self.log.configure(state="disabled")

    # ── execução ─────────────────────────────────────
    def _executar_thread(self):
        threading.Thread(target=self._executar, daemon=True).start()

    def _executar(self):
        campos = {
            "Arquivo de cobrança (PDF)": self.var_pdf.get(),
            "Plano de contas":           self.var_plano.get(),
            "Arquivo de saída (.txt)":   self.var_saida.get(),
        }
        for nome, val in campos.items():
            if not val.strip():
                messagebox.showwarning("Campo obrigatório", f"Preencha: {nome}")
                return

        self.progress.start(8)
        try:
            self._log("Lendo PDF de cobrança...")
            df_extrato = extrair_extrato_de_pdf(self.var_pdf.get())
            self._log(f"{len(df_extrato)} registros extraídos.")

            self._log("Gerando lançamentos contábeis...")
            df_lcto = gerar_lancamentos_contabeis(df_extrato, self.var_plano.get())
            self._log(f"{len(df_lcto)} lançamentos gerados.")

            self._log("Exportando arquivo SCI/VSUC...")
            exportar_txt(df_lcto, self.var_saida.get())
            self._log(f"✓ Salvo em: {self.var_saida.get()}", "ok")

            messagebox.showinfo("Concluído",
                                f"{len(df_lcto)} lançamentos gerados com sucesso!\n\n"
                                f"→ {os.path.basename(self.var_saida.get())}")
        except Exception as e:
            self._log(f"ERRO: {e}", "err")
            messagebox.showerror("Erro", str(e))
        finally:
            self.progress.stop()


if __name__ == "__main__":
    app = App()
    app.mainloop()
