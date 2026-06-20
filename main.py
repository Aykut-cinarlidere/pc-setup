import tkinter as tk
from tkinter import ttk, messagebox
import threading
import urllib.request
import os
import subprocess
import sys
import tempfile

PROGRAMS = [
    {
        "name": "Revo Uninstaller",
        "url": "https://download.revouninstaller.com/download/revosetup.exe",
        "filename": "revosetup.exe",
        "args": ["/verysilent", "/norestart"],
    },
    {
        "name": "Everything",
        "url": "https://www.voidtools.com/Everything-1.4.1.1026.x64-Setup.exe",
        "filename": "everything-setup.exe",
        "args": ["/S"],
    },
    {
        "name": "WizTree",
        "url": "https://antibody-software.com/files/wiztree_4_21_setup.exe",
        "filename": "wiztree-setup.exe",
        "args": ["/VERYSILENT", "/NORESTART"],
    },
    {
        "name": "WinRAR",
        "url": "https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-701.exe",
        "filename": "winrar-setup.exe",
        "args": ["/S"],
    },
    {
        "name": "Google Chrome",
        "url": "https://dl.google.com/chrome/install/ChromeStandaloneSetup64.exe",
        "filename": "chrome-setup.exe",
        "args": ["/silent", "/install"],
    },
]

class SetupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PC Setup")
        self.geometry("520x700")
        self.resizable(False, True)
        self.configure(bg="#1a1a2e")
        self.checks = []
        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg="#16213e", pady=16)
        header.pack(fill="x")
        tk.Label(header, text="🖥️  PC Setup", font=("Segoe UI", 20, "bold"),
                 bg="#16213e", fg="#e0e0e0").pack()
        tk.Label(header, text="Kurmak istediğin programları seç ve başlat",
                 font=("Segoe UI", 10), bg="#16213e", fg="#888").pack(pady=(2,0))

        # Program list
        list_frame = tk.Frame(self, bg="#1a1a2e", padx=30, pady=20)
        list_frame.pack(fill="x")

        tk.Label(list_frame, text="Programlar", font=("Segoe UI", 12, "bold"),
                 bg="#1a1a2e", fg="#e0e0e0").pack(anchor="w", pady=(0,10))

        self.check_vars = []
        for prog in PROGRAMS:
            var = tk.BooleanVar(value=True)
            self.check_vars.append(var)
            row = tk.Frame(list_frame, bg="#0f3460", padx=12, pady=10)
            row.pack(fill="x", pady=3)
            cb = tk.Checkbutton(row, text=f"  {prog['name']}", variable=var,
                                bg="#0f3460", fg="#e0e0e0", selectcolor="#16213e",
                                activebackground="#0f3460", activeforeground="#e0e0e0",
                                font=("Segoe UI", 11), anchor="w", cursor="hand2")
            cb.pack(fill="x")

        # Select all / none
        btn_row = tk.Frame(self, bg="#1a1a2e")
        btn_row.pack(pady=(0, 10))
        tk.Button(btn_row, text="Tümünü Seç", command=self.select_all,
                  bg="#0f3460", fg="#aaa", relief="flat", padx=10, pady=4,
                  font=("Segoe UI", 9), cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_row, text="Hiçbirini Seçme", command=self.select_none,
                  bg="#0f3460", fg="#aaa", relief="flat", padx=10, pady=4,
                  font=("Segoe UI", 9), cursor="hand2").pack(side="left", padx=5)

        # Log area
        log_frame = tk.Frame(self, bg="#1a1a2e", padx=30)
        log_frame.pack(fill="both", expand=True)
        self.log_box = tk.Text(log_frame, height=5, bg="#0d0d1a", fg="#00ff88",
                               font=("Consolas", 9), relief="flat",
                               state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True)

        # Progress bar
        prog_frame = tk.Frame(self, bg="#1a1a2e", padx=30, pady=8)
        prog_frame.pack(fill="x")
        self.progress = ttk.Progressbar(prog_frame, length=460, mode="determinate")
        self.progress.pack(fill="x")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#0f3460",
                        background="#00ff88", thickness=8)

        # Start button
        self.start_btn = tk.Button(self, text="▶  Kurulumu Başlat",
                                   command=self.start_install,
                                   bg="#e94560", fg="white", relief="flat",
                                   font=("Segoe UI", 13, "bold"),
                                   padx=20, pady=14, cursor="hand2",
                                   width=30)
        self.start_btn.pack(pady=(8, 24), side="bottom")

    def select_all(self):
        for v in self.check_vars: v.set(True)

    def select_none(self):
        for v in self.check_vars: v.set(False)

    def log(self, msg, color="#00ff88"):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def start_install(self):
        selected = [PROGRAMS[i] for i, v in enumerate(self.check_vars) if v.get()]
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen en az bir program seç.")
            return
        self.start_btn.config(state="disabled", text="Kuruluyor...")
        threading.Thread(target=self.install_all, args=(selected,), daemon=True).start()

    def install_all(self, programs):
        total = len(programs)
        tmpdir = tempfile.mkdtemp()
        for idx, prog in enumerate(programs):
            self.log(f"⬇  {prog['name']} indiriliyor...")
            dest = os.path.join(tmpdir, prog["filename"])
            try:
                urllib.request.urlretrieve(prog["url"], dest)
                self.log(f"🔧 {prog['name']} kuruluyor...")
                subprocess.run([dest] + prog["args"], check=False)
                self.log(f"✅ {prog['name']} kuruldu.")
            except Exception as e:
                self.log(f"❌ {prog['name']} başarısız: {e}")
            self.progress["value"] = int((idx + 1) / total * 100)
            self.update_idletasks()

        self.log("🎉 Tüm kurulumlar tamamlandı!")
        self.start_btn.config(state="normal", text="▶  Kurulumu Başlat")
        messagebox.showinfo("Bitti", "Tüm seçilen programlar kuruldu!")

if __name__ == "__main__":
    app = SetupApp()
    app.mainloop()
