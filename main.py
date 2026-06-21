import tkinter as tk
from tkinter import ttk, messagebox
import threading
import urllib.request
import os
import subprocess
import json
import sys

EXE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
DOWNLOAD_DIR = os.path.join(EXE_DIR, "downloads")
CONFIG_FILE = os.path.join(EXE_DIR, "programs.json")

DEFAULT_PROGRAMS = [
    {
        "name": "Revo Uninstaller",
        "url": "https://download.revouninstaller.com/download/revosetup.exe",
        "filename": "revosetup.exe",
        # /VERYSILENT sessiz kurar, masaüstü simgesi oluşturur
        "args": ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"]
    },
    {
        "name": "Everything",
        "url": "https://www.voidtools.com/Everything-1.4.1.1026.x64-Setup.exe",
        "filename": "everything-setup.exe",
        # Everything NSIS tabanlı, /S sessiz kurar
        "args": ["/S", "/desktop-shortcut=yes"]
    },
    {
        "name": "WizTree",
        "url": "https://www.diskanalyzer.com/files/wiztree_4_30_setup.exe",
        "filename": "wiztree-setup.exe",
        # Inno Setup, VERYSILENT + desktopicon görevi
        "args": ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/TASKS=desktopicon"]
    },
    {
        "name": "WinRAR",
        "url": "https://www.rarlab.com/rar/winrar-x64-701.exe",
        "filename": "winrar-setup.exe",
        # WinRAR /S ile sessiz kurulur, otomatik masaüstü simgesi ekler
        "args": ["/S"]
    },
    {
        "name": "Google Chrome",
        "url": "https://dl.google.com/chrome/install/ChromeStandaloneSetup64.exe",
        "filename": "chrome-setup.exe",
        # Chrome standalone /silent /install ile sessiz kurulur
        "args": ["/silent", "/install"]
    },
]

def load_programs():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_PROGRAMS[:]

def save_programs(programs):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(programs, f, ensure_ascii=False, indent=2)

class AddProgramDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Program Ekle")
        self.geometry("460x300")
        self.minsize(460, 300)
        self.configure(bg="#1a1a2e")
        self.resizable(False, False)
        self.result = None
        self.grab_set()
        self.build()

    def build(self):
        tk.Label(self, text="Program Ekle", font=("Segoe UI", 13, "bold"),
                 bg="#1a1a2e", fg="#e0e0e0").pack(pady=(18, 4))

        form = tk.Frame(self, bg="#1a1a2e", padx=24)
        form.pack(fill="x", pady=8)
        form.columnconfigure(0, weight=1)

        tk.Label(form, text="Program Adı", font=("Segoe UI", 10),
                 bg="#1a1a2e", fg="#aaa").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.name_entry = tk.Entry(form, font=("Segoe UI", 11), bg="#0f3460",
                                   fg="#e0e0e0", insertbackground="white",
                                   relief="flat", width=38)
        self.name_entry.grid(row=1, column=0, sticky="ew", ipady=7, pady=(0, 14))

        tk.Label(form, text="İndirme Linki (.exe)", font=("Segoe UI", 10),
                 bg="#1a1a2e", fg="#aaa").grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.url_entry = tk.Entry(form, font=("Segoe UI", 11), bg="#0f3460",
                                  fg="#e0e0e0", insertbackground="white",
                                  relief="flat", width=38)
        self.url_entry.grid(row=3, column=0, sticky="ew", ipady=7)

        btn_row = tk.Frame(self, bg="#1a1a2e")
        btn_row.pack(pady=20)
        tk.Button(btn_row, text="İptal", command=self.destroy,
                  bg="#0f3460", fg="#aaa", relief="flat",
                  font=("Segoe UI", 10), padx=18, pady=8, cursor="hand2").pack(side="left", padx=8)
        tk.Button(btn_row, text="  Ekle  ", command=self.on_add,
                  bg="#e94560", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=24, pady=8, cursor="hand2").pack(side="left", padx=8)

        self.name_entry.focus()

    def on_add(self):
        name = self.name_entry.get().strip()
        url  = self.url_entry.get().strip()
        if not name or not url:
            messagebox.showwarning("Eksik bilgi", "Lütfen ad ve link gir.", parent=self)
            return
        if not url.lower().startswith("http"):
            messagebox.showwarning("Hatalı link", "Link http:// ile başlamalı.", parent=self)
            return
        filename = url.split("/")[-1].split("?")[0]
        if not filename.endswith(".exe"):
            filename = name.replace(" ", "_") + ".exe"
        self.result = {"name": name, "url": url, "filename": filename, "args": ["/S"]}
        self.destroy()

class SetupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PC Setup")
        self.geometry("520x700")
        self.resizable(False, True)
        self.configure(bg="#1a1a2e")
        self.programs = load_programs()
        self.check_vars = []
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg="#16213e", pady=16)
        header.pack(fill="x")
        tk.Label(header, text="🖥️  PC Setup", font=("Segoe UI", 20, "bold"),
                 bg="#16213e", fg="#e0e0e0").pack()
        tk.Label(header, text="Kurmak istediğin programları seç ve başlat",
                 font=("Segoe UI", 10), bg="#16213e", fg="#888").pack(pady=(2, 0))

        list_outer = tk.Frame(self, bg="#1a1a2e", padx=30, pady=16)
        list_outer.pack(fill="both", expand=True)

        header_row = tk.Frame(list_outer, bg="#1a1a2e")
        header_row.pack(fill="x", pady=(0, 10))
        tk.Label(header_row, text="Programlar", font=("Segoe UI", 12, "bold"),
                 bg="#1a1a2e", fg="#e0e0e0").pack(side="left")
        tk.Button(header_row, text="＋ Program Ekle", command=self.add_program,
                  bg="#00b894", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=4,
                  cursor="hand2").pack(side="right")

        self.list_frame = tk.Frame(list_outer, bg="#1a1a2e")
        self.list_frame.pack(fill="both", expand=True)
        self.render_program_list()

        btn_row = tk.Frame(self, bg="#1a1a2e")
        btn_row.pack(pady=(0, 6))
        tk.Button(btn_row, text="Tümünü Seç", command=self.select_all,
                  bg="#0f3460", fg="#aaa", relief="flat", padx=10, pady=4,
                  font=("Segoe UI", 9), cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_row, text="Hiçbirini Seçme", command=self.select_none,
                  bg="#0f3460", fg="#aaa", relief="flat", padx=10, pady=4,
                  font=("Segoe UI", 9), cursor="hand2").pack(side="left", padx=5)

        log_frame = tk.Frame(self, bg="#1a1a2e", padx=30)
        log_frame.pack(fill="x")
        self.log_box = tk.Text(log_frame, height=5, bg="#0d0d1a", fg="#00ff88",
                               font=("Consolas", 9), relief="flat",
                               state="disabled", wrap="word")
        self.log_box.pack(fill="x")

        path_frame = tk.Frame(self, bg="#1a1a2e", padx=30)
        path_frame.pack(fill="x", pady=(4, 0))
        tk.Label(path_frame, text=f"📁  İndirme klasörü: .\\downloads\\",
                 font=("Segoe UI", 8), bg="#1a1a2e", fg="#555").pack(anchor="w")

        prog_frame = tk.Frame(self, bg="#1a1a2e", padx=30, pady=6)
        prog_frame.pack(fill="x")
        self.progress = ttk.Progressbar(prog_frame, length=460, mode="determinate")
        self.progress.pack(fill="x")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#0f3460", background="#00ff88", thickness=8)

        self.start_btn = tk.Button(self, text="▶  Kurulumu Başlat",
                                   command=self.start_install,
                                   bg="#e94560", fg="white", relief="flat",
                                   font=("Segoe UI", 13, "bold"),
                                   padx=20, pady=14, cursor="hand2", width=30)
        self.start_btn.pack(pady=(6, 20))

    def render_program_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.check_vars = []
        for i, prog in enumerate(self.programs):
            var = tk.BooleanVar(value=True)
            self.check_vars.append(var)
            row = tk.Frame(self.list_frame, bg="#0f3460", padx=12, pady=8)
            row.pack(fill="x", pady=3)
            tk.Checkbutton(row, text=f"  {prog['name']}", variable=var,
                           bg="#0f3460", fg="#e0e0e0", selectcolor="#16213e",
                           activebackground="#0f3460", activeforeground="#e0e0e0",
                           font=("Segoe UI", 11), anchor="w", cursor="hand2").pack(side="left", fill="x", expand=True)
            tk.Button(row, text="✕", command=lambda idx=i: self.remove_program(idx),
                      bg="#0f3460", fg="#e94560", relief="flat",
                      font=("Segoe UI", 10, "bold"), cursor="hand2", padx=6).pack(side="right")

    def add_program(self):
        dlg = AddProgramDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.programs.append(dlg.result)
            save_programs(self.programs)
            self.render_program_list()

    def remove_program(self, idx):
        name = self.programs[idx]["name"]
        if messagebox.askyesno("Sil", f'"{name}" listeden kaldırılsın mı?'):
            self.programs.pop(idx)
            save_programs(self.programs)
            self.render_program_list()

    def select_all(self):
        for v in self.check_vars: v.set(True)

    def select_none(self):
        for v in self.check_vars: v.set(False)

    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def start_install(self):
        selected = [self.programs[i] for i, v in enumerate(self.check_vars) if v.get()]
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen en az bir program seç.")
            return
        self.start_btn.config(state="disabled", text="Kuruluyor...")
        threading.Thread(target=self.install_all, args=(selected,), daemon=True).start()

    def install_all(self, programs):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        total = len(programs)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        }

        for idx, prog in enumerate(programs):
            filename = prog.get("filename") or (prog["url"].split("/")[-1].split("?")[0]) or f"{prog['name'].replace(' ','_')}.exe"
            dest = os.path.join(DOWNLOAD_DIR, filename)

            self.log(f"⬇  {prog['name']} indiriliyor...")
            try:
                req = urllib.request.Request(prog["url"], headers=headers)
                with urllib.request.urlopen(req, timeout=60) as response:
                    with open(dest, 'wb') as f:
                        f.write(response.read())

                self.log(f"🔧 {prog['name']} kuruluyor...")
                result = subprocess.run(
                    [dest] + prog.get("args", ["/S"]),
                    timeout=300,
                    check=False
                )
                if result.returncode in (0, 3010):  # 3010 = reboot required ama kuruldu
                    self.log(f"✅ {prog['name']} kuruldu.")
                else:
                    self.log(f"⚠️  {prog['name']} kuruldu (kod: {result.returncode})")

            except subprocess.TimeoutExpired:
                self.log(f"⚠️  {prog['name']} zaman aşımı — muhtemelen kuruldu.")
            except Exception as e:
                self.log(f"❌ {prog['name']} hata: {e}")

            self.progress["value"] = int((idx + 1) / total * 100)
            self.update_idletasks()

        self.log(f"🎉 Tamamlandı! Dosyalar: {DOWNLOAD_DIR}")
        self.start_btn.config(state="normal", text="▶  Kurulumu Başlat")
        messagebox.showinfo("Bitti", f"Tüm seçilen programlar kuruldu!\n\nDosyalar: {DOWNLOAD_DIR}")

if __name__ == "__main__":
    app = SetupApp()
    app.mainloop()
