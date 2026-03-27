"""
Legendary GUI - Manifest installer frontend for Legendary Epic Games client.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os
import webbrowser

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#0d0d12"
SURFACE  = "#13131c"
SURFACE2 = "#1c1c28"
SURFACE3 = "#242433"
ACCENT   = "#6c47ff"
ACCENT2  = "#8b6fff"
ACCENT3  = "#a990ff"
TEXT     = "#f0f0fa"
SUBTEXT  = "#7070a0"
MUTED    = "#3a3a55"
SUCCESS  = "#3ddc84"
DANGER   = "#ff4f4f"
WARNING  = "#ffb347"
BORDER   = "#252538"

FH1 = ("Segoe UI", 20, "bold")
FH2 = ("Segoe UI", 13, "bold")
FH3 = ("Segoe UI", 11, "bold")
FMD = ("Segoe UI", 10)
FSM = ("Segoe UI", 9)
FXS = ("Segoe UI", 8)
FMO = ("Consolas", 9)

# ── Helpers ───────────────────────────────────────────────────────────────────
def lbl(parent, text, font=FMD, fg=TEXT, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=parent["bg"], **kw)

def entry_widget(parent, var, width=44, show=None):
    f = tk.Frame(parent, bg=SURFACE3, highlightthickness=1,
                 highlightbackground=MUTED, highlightcolor=ACCENT)
    e = tk.Entry(f, textvariable=var, bg=SURFACE3, fg=TEXT,
                 insertbackground=ACCENT3, relief="flat", font=FMD,
                 width=width, show=show or "", bd=4)
    e.pack(fill="x")
    e.bind("<FocusIn>",  lambda ev: f.config(highlightbackground=ACCENT))
    e.bind("<FocusOut>", lambda ev: f.config(highlightbackground=MUTED))
    return f, e

def pill_btn(parent, text, command=None, style="accent", **kw):
    p = {
        "accent":  (ACCENT,    TEXT,    ACCENT2),
        "danger":  ("#3a1010", DANGER,  "#4a1515"),
        "ghost":   (SURFACE3,  SUBTEXT, SURFACE2),
        "success": ("#0d2e1a", SUCCESS, "#0f3820"),
    }.get(style, (ACCENT, TEXT, ACCENT2))
    btn = tk.Button(parent, text=text, command=command,
                    bg=p[0], fg=p[1], activebackground=p[2], activeforeground=p[1],
                    relief="flat", cursor="hand2", font=FMD, bd=0,
                    padx=16, pady=8, **kw)
    btn.bind("<Enter>", lambda e: btn.config(bg=p[2]))
    btn.bind("<Leave>", lambda e: btn.config(bg=p[0]))
    return btn

def card(parent, title=None, **kw):
    outer = tk.Frame(parent, bg=SURFACE, highlightthickness=1,
                     highlightbackground=BORDER, **kw)
    if title:
        hdr = tk.Frame(outer, bg=SURFACE2)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=FH3, fg=ACCENT3,
                 bg=SURFACE2, padx=16, pady=10).pack(anchor="w")
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x")
    body = tk.Frame(outer, bg=SURFACE, padx=16, pady=12)
    body.pack(fill="both", expand=True)
    return outer, body

def badge(parent, text, color=ACCENT):
    f = tk.Frame(parent, bg=color, padx=7, pady=2)
    tk.Label(f, text=text, font=FXS, fg=TEXT, bg=color).pack()
    return f

# ── Sidebar ───────────────────────────────────────────────────────────────────
class Sidebar(tk.Frame):
    ITEMS = [
        ("⬇", "Install", "Download builds"),
        ("🔑", "Auth",    "Epic account"),
    ]

    def __init__(self, master, on_select, **kw):
        super().__init__(master, bg=SURFACE, width=210, **kw)
        self.pack_propagate(False)
        self.on_select = on_select
        self._btns = {}
        self._inds = {}
        self._build()

    def _build(self):
        # accent top bar
        tk.Frame(self, bg=ACCENT, height=3).pack(fill="x")

        # logo
        logo = tk.Frame(self, bg=SURFACE, padx=18, pady=20)
        logo.pack(fill="x")
        icon_box = tk.Frame(logo, bg=ACCENT, width=40, height=40)
        icon_box.pack_propagate(False)
        icon_box.pack(side="left", padx=(0, 12))
        tk.Label(icon_box, text="⚡", font=("Segoe UI", 15),
                 fg=TEXT, bg=ACCENT).place(relx=.5, rely=.5, anchor="center")
        txt = tk.Frame(logo, bg=SURFACE)
        txt.pack(side="left")
        tk.Label(txt, text="Legendary", font=("Segoe UI", 13, "bold"),
                 fg=TEXT, bg=SURFACE).pack(anchor="w")
        tk.Label(txt, text="Manifest Installer", font=FXS,
                 fg=SUBTEXT, bg=SURFACE).pack(anchor="w")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # nav
        nav = tk.Frame(self, bg=SURFACE, pady=10)
        nav.pack(fill="x")
        for icon, name, sub in self.ITEMS:
            row = tk.Frame(nav, bg=SURFACE, cursor="hand2")
            row.pack(fill="x", padx=10, pady=2)

            ind = tk.Frame(row, bg=SURFACE, width=3)
            ind.pack(side="left", fill="y")
            self._inds[name] = ind

            inner = tk.Frame(row, bg=SURFACE, padx=10, pady=10)
            inner.pack(side="left", fill="x", expand=True)

            ic = tk.Label(inner, text=icon, font=("Segoe UI", 12),
                          fg=SUBTEXT, bg=SURFACE, width=2)
            ic.pack(side="left")

            col = tk.Frame(inner, bg=SURFACE)
            col.pack(side="left", padx=(8, 0))
            nl = tk.Label(col, text=name, font=FH3, fg=SUBTEXT, bg=SURFACE, anchor="w")
            nl.pack(anchor="w")
            sl = tk.Label(col, text=sub, font=FXS, fg=MUTED, bg=SURFACE, anchor="w")
            sl.pack(anchor="w")

            self._btns[name] = (row, inner, ic, nl, sl, col)
            for w in (row, inner, ic, nl, sl, col):
                w.bind("<Button-1>", lambda e, n=name: self._select(n))
                w.bind("<Enter>",    lambda e, n=name: self._hover(n, True))
                w.bind("<Leave>",    lambda e, n=name: self._hover(n, False))

        # bottom info
        tk.Frame(self, bg=BORDER, height=1).pack(side="bottom", fill="x")
        info = tk.Frame(self, bg=SURFACE2, padx=14, pady=12)
        info.pack(side="bottom", fill="x")
        tk.Label(info, text="Need more features?", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT3, bg=SURFACE2).pack(anchor="w")
        tk.Label(info, text="Use the full Legendary CLI\nfor library, saves & more.",
                 font=FXS, fg=SUBTEXT, bg=SURFACE2, justify="left").pack(anchor="w", pady=(3, 6))
        link = tk.Label(info, text="→ github.com/derrod/legendary",
                        font=("Segoe UI", 8, "underline"), fg=ACCENT2,
                        bg=SURFACE2, cursor="hand2")
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/derrod/legendary"))

    def _hover(self, name, on):
        row, inner, ic, nl, sl, col = self._btns[name]
        if nl["fg"] == TEXT and not on:
            return
        bg = SURFACE2 if on else SURFACE
        for w in (row, inner, ic, nl, sl, col):
            w.config(bg=bg)

    def _select(self, name):
        for n, (row, inner, ic, nl, sl, col) in self._btns.items():
            active = n == name
            bg = SURFACE2 if active else SURFACE
            self._inds[n].config(bg=ACCENT if active else SURFACE)
            for w in (row, inner, ic, nl, sl, col):
                w.config(bg=bg)
            nl.config(fg=TEXT if active else SUBTEXT)
            ic.config(fg=ACCENT2 if active else SUBTEXT)
        self.on_select(name)

    def select(self, name):
        self._select(name)

# ── SDL options ───────────────────────────────────────────────────────────────
SDL_OPTIONS = {
    "Fortnite": {
        "__required": ("Fortnite Core (required)", ["chunk0","chunk10"],         True),
        "stw":        ("Save the World",           ["chunk11","chunk11optional"],False),
        "hd_textures":("High Resolution Textures", ["chunk10optional"],          False),
        "lang_de":    ("Deutsch",                  ["chunk2"],                   False),
        "lang_fr":    ("français",                 ["chunk5"],                   False),
        "lang_pl":    ("polski",                   ["chunk7"],                   False),
        "lang_ru":    ("русский",                  ["chunk8"],                   False),
        "lang_cn":    ("中文（中国）",              ["chunk9"],                   False),
    }
}

# ── Install page ──────────────────────────────────────────────────────────────
class InstallPage(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, **kw)
        self._stopped = False
        self._dlm = None
        self._sdl_vars = {}
        self._build()

    def _build(self):
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=BG)
        wid = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # page header
        hdr = tk.Frame(inner, bg=SURFACE2)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=ACCENT, height=2).pack(fill="x")
        hi = tk.Frame(hdr, bg=SURFACE2, padx=28, pady=18)
        hi.pack(fill="x")
        tk.Label(hi, text="Manifest Install", font=FH1, fg=TEXT, bg=SURFACE2).pack(side="left")
        b = badge(hi, "BETA", color=ACCENT)
        b.pack(side="left", padx=(12, 0))
        tk.Label(hi, text="Download any Fortnite build using a .manifest file",
                 font=FMD, fg=SUBTEXT, bg=SURFACE2).pack(side="left", padx=(16, 0))

        # config card
        co, cb = card(inner, title="Configuration")
        co.pack(fill="x", padx=24, pady=(20, 0))

        def field(label_text, var, browse=None, width=40):
            r = tk.Frame(cb, bg=SURFACE)
            r.pack(fill="x", pady=6)
            tk.Label(r, text=label_text, font=FSM, fg=SUBTEXT,
                     bg=SURFACE, width=16, anchor="w").pack(side="left")
            ef, _ = entry_widget(r, var, width=width)
            ef.pack(side="left", padx=(0, 8))
            if browse:
                pill_btn(r, "Browse", command=browse,
                         style="ghost", padx=10, pady=5).pack(side="left")

        self.manifest_var = tk.StringVar()
        self.folder_var   = tk.StringVar()
        self.url_var      = tk.StringVar(
            value="https://epicgames-download1.akamaized.net/Builds/Fortnite/CloudDir")
        self.app_var = tk.StringVar(value="Fortnite")
        self.app_var.trace_add("write", lambda *_: self._refresh_sdl())

        field("Manifest file",  self.manifest_var, self._browse_manifest)
        field("Install folder", self.folder_var,   self._browse_folder)
        field("Base URL",       self.url_var,       width=48)
        field("App name",       self.app_var,       width=20)

        # download options card
        self.sdl_outer, self.sdl_body = card(inner, title="Download Options")
        self.sdl_outer.pack(fill="x", padx=24, pady=(12, 0))
        self._refresh_sdl()

        # action row
        act = tk.Frame(inner, bg=BG, padx=24)
        act.pack(fill="x", pady=(16, 0))
        self.start_btn = pill_btn(act, "⬇   Start Download", command=self._start)
        self.start_btn.pack(side="left")
        self.stop_btn = pill_btn(act, "■   Stop", command=self._stop, style="danger")
        self.stop_btn.pack(side="left", padx=(10, 0))
        self.stop_btn.config(state="disabled")
        self.eta_var = tk.StringVar(value="")
        tk.Label(act, textvariable=self.eta_var, font=FMD,
                 fg=ACCENT3, bg=BG).pack(side="right")

        # custom progress bar
        pf = tk.Frame(inner, bg=BG, padx=24)
        pf.pack(fill="x", pady=(10, 0))
        self.pct_var = tk.StringVar(value="")
        tk.Label(pf, textvariable=self.pct_var, font=FSM, fg=SUBTEXT, bg=BG).pack(anchor="e")
        bar_bg = tk.Frame(pf, bg=SURFACE3, height=8)
        bar_bg.pack(fill="x", pady=(2, 0))
        bar_bg.pack_propagate(False)
        self._bar_fill = tk.Frame(bar_bg, bg=ACCENT, height=8)
        self._bar_fill.place(x=0, y=0, relheight=1, relwidth=0)

        # output card
        oo, ob = card(inner, title="Output")
        oo.pack(fill="x", padx=24, pady=(16, 24))
        ob.config(pady=0, padx=0)
        log_wrap = tk.Frame(ob, bg=BG, height=200)
        log_wrap.pack(fill="x")
        log_wrap.pack_propagate(False)
        self.log_box = tk.Text(log_wrap, bg="#0a0a10", fg="#c8c8e8", font=FMO,
                               relief="flat", state="disabled", wrap="word",
                               insertbackground=ACCENT, padx=12, pady=10,
                               selectbackground=ACCENT, selectforeground=TEXT)
        lvsb = ttk.Scrollbar(log_wrap, orient="vertical", command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=lvsb.set)
        self.log_box.pack(side="left", fill="both", expand=True)
        lvsb.pack(side="right", fill="y")
        self.log_box.tag_config("ok",   foreground=SUCCESS)
        self.log_box.tag_config("err",  foreground=DANGER)
        self.log_box.tag_config("warn", foreground=WARNING)
        self.log_box.tag_config("dim",  foreground=SUBTEXT)

    def _refresh_sdl(self):
        for w in self.sdl_body.winfo_children():
            w.destroy()
        self._sdl_vars.clear()
        app = self.app_var.get().strip()
        opts = SDL_OPTIONS.get(app)
        if not opts:
            tk.Label(self.sdl_body, text="No selective download options for this app.",
                     font=FSM, fg=SUBTEXT, bg=SURFACE).pack(anchor="w")
            return
        cols_f = tk.Frame(self.sdl_body, bg=SURFACE)
        cols_f.pack(fill="x")
        col1 = tk.Frame(cols_f, bg=SURFACE)
        col2 = tk.Frame(cols_f, bg=SURFACE)
        col1.pack(side="left", anchor="n", padx=(0, 32))
        col2.pack(side="left", anchor="n")
        for i, (key, (name, tags, default)) in enumerate(opts.items()):
            var = tk.BooleanVar(value=default)
            self._sdl_vars[key] = (var, tags)
            col = col1 if i % 2 == 0 else col2
            state = "disabled" if key == "__required" else "normal"
            row = tk.Frame(col, bg=SURFACE)
            row.pack(anchor="w", pady=3)
            tk.Checkbutton(row, text=name, variable=var, state=state,
                           font=FMD, fg=SUBTEXT if key == "__required" else TEXT,
                           bg=SURFACE, activebackground=SURFACE, activeforeground=TEXT,
                           selectcolor=ACCENT, disabledforeground=MUTED,
                           relief="flat", bd=0, cursor="hand2").pack(side="left")
            if key == "__required":
                badge(row, "required", color=MUTED).pack(side="left", padx=(8, 0))
            elif key == "hd_textures":
                badge(row, "+15 GB", color="#2a1a00").pack(side="left", padx=(8, 0))

    def _browse_manifest(self):
        p = filedialog.askopenfilename(title="Select manifest",
            filetypes=[("Manifest files", "*.manifest"), ("All files", "*.*")])
        if p: self.manifest_var.set(p)

    def _browse_folder(self):
        p = filedialog.askdirectory(title="Select install folder")
        if p: self.folder_var.set(p)

    def _log(self, msg, tag=None):
        self.log_box.configure(state="normal")
        if tag:
            self.log_box.insert("end", msg + "\n", tag)
        else:
            self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_bar(self, pct):
        self._bar_fill.place(relwidth=max(0.0, min(pct / 100, 1.0)))

    def _update_progress(self, pct, eta, speed):
        self._set_bar(pct)
        parts = [f"{pct:.1f}%"]
        if speed: parts.append(speed)
        if eta:   parts.append(f"ETA {eta}")
        self.eta_var.set("  ·  ".join(parts))
        self.pct_var.set(f"{pct:.1f}%")

    def _start(self):
        manifest = self.manifest_var.get().strip()
        folder   = self.folder_var.get().strip()
        url      = self.url_var.get().strip()
        app      = self.app_var.get().strip()
        if not manifest:
            messagebox.showwarning("Missing", "Please select a manifest file.")
            return
        if not folder:
            messagebox.showwarning("Missing", "Please select an install folder.")
            return
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.eta_var.set("Preparing…")
        self._set_bar(0)
        self._stopped = False
        threading.Thread(target=self._run,
                         args=(manifest, folder, url, app), daemon=True).start()

    def _stop(self):
        self._stopped = True
        if hasattr(self, "_dlm") and self._dlm:
            try:
                self._dlm.running = False
                for child in getattr(self._dlm, "children", []):
                    child.terminate()
            except Exception:
                pass
        self._log("\n⚠  Stopped by user.", "warn")
        self._finish()

    def _finish(self):
        self._set_bar(0)
        self.eta_var.set("")
        self.pct_var.set("")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._dlm = None

    def _run(self, manifest, folder, url, app):
        from multiprocessing import Queue as MPQueue
        from legendary.core import LegendaryCore
        from legendary.models.downloading import UIUpdate

        self._stopped = False
        self._dlm = None
        try:
            core = LegendaryCore()
            self._log("Logging in…", "dim")
            if not core.login():
                self._log("✖  Login failed. Go to the Auth tab first.", "err")
                self.after(0, self._finish)
                return

            if core.is_installed(app):
                self._log(f"Clearing existing install record for {app}…", "dim")
                igame = core.get_installed_game(app)
                core.uninstall_game(igame, delete_files=False)

            self._log("Loading manifest…", "dim")
            game = core.get_game(app, update_meta=False)
            if not game:
                from legendary.models.game import Game
                game = Game(app_name=app, app_title=app)

            install_tags = []
            for key, (var, tag_list) in self._sdl_vars.items():
                if var.get():
                    install_tags.extend(tag_list)

            status_q = MPQueue()
            self._log("Preparing download…", "dim")
            dlm, analysis, igame = core.prepare_download(
                game=game,
                override_manifest=manifest,
                override_base_url=url,
                game_folder=folder,
                install_tag=install_tags if install_tags else None,
                status_queue=status_q,
                download_only=True,
            )

            total = analysis.dl_size
            self._log(f"Download size: {total / 1024**3:.2f} GiB", "dim")
            self._log("Starting download workers…", "dim")
            self._dlm = dlm

            dl_thread = threading.Thread(target=dlm.run, daemon=True)
            dl_thread.start()

            while dl_thread.is_alive() and not self._stopped:
                try:
                    update = status_q.get(timeout=1.0)
                    if isinstance(update, UIUpdate):
                        pct = update.progress
                        speed_str = f"{update.download_speed / 1024 / 1024:.1f} MiB/s"
                        if update.download_speed > 0 and total > 0:
                            remaining = total * (1 - pct / 100)
                            secs = int(remaining / update.download_speed)
                            eta_str = f"{secs//3600:02d}:{(secs%3600)//60:02d}:{secs%60:02d}"
                        else:
                            eta_str = ""
                        self.after(0, lambda p=pct, e=eta_str, s=speed_str:
                                   self._update_progress(p, e, s))
                except Exception:
                    pass

            if not self._stopped:
                dl_thread.join()
                core.install_game(igame)
                self._set_bar(100)
                self._log("\n✔  Download complete!", "ok")

        except Exception as e:
            self._log(f"\n✖  Error: {e}", "err")

        self.after(0, self._finish)

# ── Auth page ─────────────────────────────────────────────────────────────────
class AuthPage(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, **kw)
        self._build()

    def _build(self):
        # page header
        hdr = tk.Frame(self, bg=SURFACE2)
        hdr.pack(fill="x")
        tk.Frame(hdr, bg=ACCENT, height=2).pack(fill="x")
        hi = tk.Frame(hdr, bg=SURFACE2, padx=28, pady=18)
        hi.pack(fill="x")
        tk.Label(hi, text="Authentication", font=FH1, fg=TEXT, bg=SURFACE2).pack(side="left")
        tk.Label(hi, text="Connect your Epic Games account",
                 font=FMD, fg=SUBTEXT, bg=SURFACE2).pack(side="left", padx=(16, 0))

        # status card
        so, sb = card(self, title="Account Status")
        so.pack(fill="x", padx=24, pady=(20, 0))
        status_row = tk.Frame(sb, bg=SURFACE)
        status_row.pack(fill="x")
        self.status_dot = tk.Label(status_row, text="●", font=("Segoe UI", 14),
                                   fg=MUTED, bg=SURFACE)
        self.status_dot.pack(side="left", padx=(0, 8))
        self.status_var = tk.StringVar(value="Checking…")
        tk.Label(status_row, textvariable=self.status_var, font=FMD,
                 fg=TEXT, bg=SURFACE).pack(side="left")

        # login card
        lo, lb = card(self, title="Login with Authorization Code")
        lo.pack(fill="x", padx=24, pady=(12, 0))

        step1 = tk.Frame(lb, bg=SURFACE)
        step1.pack(fill="x", pady=(0, 10))
        tk.Label(step1, text="Step 1", font=("Segoe UI", 9, "bold"),
                 fg=ACCENT3, bg=SURFACE).pack(side="left", padx=(0, 10))
        tk.Label(step1, text="Open the Epic login page and copy your authorization code",
                 font=FSM, fg=SUBTEXT, bg=SURFACE).pack(side="left")
        pill_btn(step1, "🌐  Open Login Page", command=self._open_browser,
                 style="ghost", padx=10, pady=5).pack(side="right")

        tk.Frame(lb, bg=BORDER, height=1).pack(fill="x", pady=(0, 10))

        step2 = tk.Frame(lb, bg=SURFACE)
        step2.pack(fill="x")
        tk.Label(step2, text="Step 2", font=("Segoe UI", 9, "bold"),
                 fg=ACCENT3, bg=SURFACE).pack(side="left", padx=(0, 10))
        tk.Label(step2, text="Paste the authorizationCode value here:",
                 font=FSM, fg=SUBTEXT, bg=SURFACE).pack(side="left")

        code_row = tk.Frame(lb, bg=SURFACE)
        code_row.pack(fill="x", pady=(8, 0))
        self.code_var = tk.StringVar()
        ef, _ = entry_widget(code_row, self.code_var, width=36, show="*")
        ef.pack(side="left", padx=(0, 10))
        pill_btn(code_row, "Login", command=self._login_code).pack(side="left")

        tk.Label(lb,
                 text="Find the 'authorizationCode' field in the JSON response and paste just the value (no quotes).",
                 font=FXS, fg=MUTED, bg=SURFACE, wraplength=560, justify="left"
                 ).pack(anchor="w", pady=(10, 0))

        # logout
        lo2, lb2 = card(self, title="Session")
        lo2.pack(fill="x", padx=24, pady=(12, 24))
        pill_btn(lb2, "Logout", command=self._logout, style="danger").pack(anchor="w")

        self._check_status()

    def _set_status(self, text, ok=None):
        self.status_var.set(text)
        if ok is True:
            self.status_dot.config(fg=SUCCESS)
        elif ok is False:
            self.status_dot.config(fg=DANGER)
        else:
            self.status_dot.config(fg=WARNING)

    def _check_status(self):
        def _run():
            try:
                from legendary.core import LegendaryCore
                c = LegendaryCore()
                if c.login():
                    name = (c.lgd.userdata or {}).get("displayName", "Unknown")
                    self.after(0, lambda: self._set_status(f"Logged in as  {name}", True))
                else:
                    self.after(0, lambda: self._set_status("Not logged in", False))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"Error: {e}", False))
        threading.Thread(target=_run, daemon=True).start()

    def _login_code(self):
        code = self.code_var.get().strip()
        if not code:
            messagebox.showwarning("Missing", "Enter an authorization code.")
            return
        self._set_status("Logging in…", None)
        def _run():
            try:
                from legendary.core import LegendaryCore
                c = LegendaryCore()
                if c.auth_code(code):
                    name = (c.lgd.userdata or {}).get("displayName", "Unknown")
                    self.after(0, lambda: self._set_status(f"Logged in as  {name}", True))
                else:
                    self.after(0, lambda: self._set_status("Login failed — check your code", False))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"Error: {e}", False))
        threading.Thread(target=_run, daemon=True).start()

    def _open_browser(self):
        webbrowser.open(
            "https://www.epicgames.com/id/api/redirect"
            "?clientId=34a02cf8f4414e29b15921876da36f9a&responseType=code")

    def _logout(self):
        if not messagebox.askyesno("Logout", "Log out of Epic Games?"):
            return
        def _run():
            try:
                from legendary.core import LegendaryCore
                c = LegendaryCore()
                c.lgd.invalidate_userdata()
                self.after(0, lambda: self._set_status("Logged out", False))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"Error: {e}", False))
        threading.Thread(target=_run, daemon=True).start()


# ── Main app ──────────────────────────────────────────────────────────────────
class App(tk.Tk):
    PAGES = {"Install": InstallPage, "Auth": AuthPage}

    def __init__(self):
        super().__init__()
        self.title("Legendary — Manifest Installer")
        self.geometry("1000x680")
        self.minsize(860, 560)
        self.configure(bg=BG)
        self._apply_theme()
        self._build()

    def _apply_theme(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=BG, foreground=TEXT,
                    fieldbackground=SURFACE2, troughcolor=SURFACE,
                    bordercolor=BORDER, selectbackground=ACCENT, selectforeground=TEXT)
        s.configure("TScrollbar", background=SURFACE2, troughcolor=SURFACE,
                    arrowcolor=SUBTEXT, bordercolor=BORDER, relief="flat")
        s.configure("TSeparator", background=BORDER)

    def _build(self):
        self._pages = {}
        self.content = tk.Frame(self, bg=BG)

        for name, cls in self.PAGES.items():
            page = cls(self.content)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._pages[name] = page

        self.sidebar = Sidebar(self, on_select=self._show)
        self.sidebar.pack(side="left", fill="y")
        tk.Frame(self, bg=BORDER, width=1).pack(side="left", fill="y")
        self.content.pack(side="left", fill="both", expand=True)
        self.sidebar.select("Install")

    def _show(self, name):
        self._pages[name].lift()


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    App().mainloop()
