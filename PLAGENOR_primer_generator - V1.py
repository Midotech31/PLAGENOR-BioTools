import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ================= CONSTANTS =================
COMMON_PREFIX = "TGCATC"
BG_COLOR = "#f5f5f5"          # Modern light grayish background
PRIMARY_COLOR = "#2c3e50"     # Dark blue text
ACCENT_COLOR = "#3498db"      # Blue accent for buttons and highlights
FONT = ("Segoe UI", 10)
DEFAULT_CONCENTRATION = 500   # nM

enzyme_linkers = {
    "NdeI": "CATAT",    "XhoI": "CTCGAG",   "EcoRI": "GAATTC",
    "BamHI": "GGATCC",  "HindIII": "AAGCTT",  "SalI": "GTCGAC",
    "NotI": "GCGGCCGC", "KpnI": "GGTACC",    "SmaI": "CCCGGG",
    "PstI": "CTGCAG",   "ApaI": "GGGCCC",    "SacI": "GAGCTC",
    "XbaI": "TCTAGA",   "SphI": "GCATGC"
}

# ---------------- Primer Designer Class ----------------
class PrimerDesigner:
    def __init__(self, root):
        self.root = root
        self.setup_main_window()
        self.create_widgets()
        self.setup_layout()

    def setup_main_window(self):
        self.root.title("PLAGENOR Cloning Primer Designer")
        self.root.geometry("1000x680")
        self.root.configure(bg=BG_COLOR)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.create_menubar()

    def create_menubar(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_all)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copy Forward", command=lambda: self.copy_to_clipboard(self.txt_forward["text_widget"]))
        edit_menu.add_command(label="Copy Reverse", command=lambda: self.copy_to_clipboard(self.txt_reverse["text_widget"]))
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_widgets(self):
        # Main container frame with padding
        self.main_frame = ttk.Frame(self.root, padding=20)
        
        # Title Section
        self.title_frame = ttk.Frame(self.main_frame)
        self.title_label = ttk.Label(
            self.title_frame,
            text="PLAGENOR Cloning Primer Designer",
            font=("Segoe UI", 16, "bold"),
            foreground=ACCENT_COLOR,
            background=BG_COLOR
        )
        self.title_label.pack(side=tk.LEFT, anchor="w")
        
        # Input Section
        self.input_frame = ttk.LabelFrame(self.main_frame, text=" Primer Input ", padding=15)
        
        # Primer Input Fields
        self.lbl_forward = ttk.Label(self.input_frame, text="Ordinary Forward Primer:")
        self.ent_forward = ttk.Entry(self.input_frame, width=50)
        self.btn_paste_forward = ttk.Button(self.input_frame, text="Paste", command=lambda: self.paste_to_entry(self.ent_forward))
        
        self.lbl_reverse = ttk.Label(self.input_frame, text="Ordinary Reverse Primer:")
        self.ent_reverse = ttk.Entry(self.input_frame, width=50)
        self.btn_paste_reverse = ttk.Button(self.input_frame, text="Paste", command=lambda: self.paste_to_entry(self.ent_reverse))
        
        # Enzyme Selection
        self.lbl_forward_enzyme = ttk.Label(self.input_frame, text="Forward Enzyme:")
        self.cmb_forward_enzyme = ttk.Combobox(self.input_frame, values=list(enzyme_linkers.keys()), state="readonly", width=22)
        self.cmb_forward_enzyme.current(0)
        
        self.lbl_reverse_enzyme = ttk.Label(self.input_frame, text="Reverse Enzyme:")
        self.cmb_reverse_enzyme = ttk.Combobox(self.input_frame, values=list(enzyme_linkers.keys()), state="readonly", width=22)
        self.cmb_reverse_enzyme.current(1)
        
        # Concentration Input
        self.lbl_concentration = ttk.Label(self.input_frame, text="Primer Concentration (nM):")
        self.ent_concentration = ttk.Entry(self.input_frame, width=10)
        self.ent_concentration.insert(0, str(DEFAULT_CONCENTRATION))
        
        # Generate and Clear Buttons
        self.btn_generate = ttk.Button(self.input_frame, text="Generate Primers", command=self.generate_primers)
        self.btn_clear = ttk.Button(self.input_frame, text="Clear", command=self.clear_all)
        
        # Results Section
        self.results_frame = ttk.LabelFrame(self.main_frame, text=" Results ", padding=15)
        
        # Result Fields (each with a text widget and metrics labels)
        self.txt_forward = self.create_result_field("Forward Primer:")
        self.txt_reverse = self.create_result_field("Reverse Primer:")
        
        # Copyright label (bottom)
        self.copyright_label = ttk.Label(
            self.main_frame, 
            text="Copyright 2025 Dr. Mohamed Merzoug\nPLAGENOR, ESSBO - Algeria | All rights reserved",
            font=("Segoe UI", 8), 
            foreground="#666666",
            background=BG_COLOR
        )

    def create_result_field(self, label_text):
        frame = ttk.Frame(self.results_frame)
        frame.pack(fill=tk.X, pady=5)
        
        lbl = ttk.Label(frame, text=label_text, font=(FONT[0], FONT[1], "bold"))
        lbl.pack(anchor="w")
        
        txt = tk.Text(frame, height=2, wrap="word", state="disabled", background="white")
        txt.pack(fill=tk.X)
        
        metrics = ttk.Frame(frame)
        metrics.pack(fill=tk.X, pady=5)
        
        lbl_length = ttk.Label(metrics, text="Length: - bp")
        lbl_length.pack(side=tk.LEFT, padx=10)
        
        lbl_tm = ttk.Label(metrics, text="Tm: - degC")
        lbl_tm.pack(side=tk.LEFT, padx=10)
        
        btn_copy = ttk.Button(metrics, text="Copy", command=lambda: self.copy_to_clipboard(txt))
        btn_copy.pack(side=tk.RIGHT)
        
        return {"text_widget": txt, "length": lbl_length, "tm": lbl_tm}

    def setup_layout(self):
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.title_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        self.input_frame.grid(row=1, column=0, sticky="ew", pady=10)
        
        # Arrange input fields in a grid
        fields = [
            (self.lbl_forward, self.ent_forward, self.btn_paste_forward),
            (self.lbl_reverse, self.ent_reverse, self.btn_paste_reverse),
            (self.lbl_forward_enzyme, self.cmb_forward_enzyme, ttk.Frame(self.input_frame)),
            (self.lbl_reverse_enzyme, self.cmb_reverse_enzyme, ttk.Frame(self.input_frame)),
            (self.lbl_concentration, self.ent_concentration, ttk.Frame(self.input_frame))
        ]
        for idx, (lbl, entry, btn) in enumerate(fields):
            lbl.grid(row=idx, column=0, sticky="w", padx=5, pady=5)
            entry.grid(row=idx, column=1, sticky="w", padx=5, pady=5)
            btn.grid(row=idx, column=2, padx=5)
        
        # Generate and Clear buttons in the next row
        self.btn_generate.grid(row=len(fields), column=0, columnspan=2, pady=10)
        self.btn_clear.grid(row=len(fields), column=2, padx=5, pady=10)
        
        self.results_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Copyright at the bottom
        self.copyright_label.grid(row=3, column=0, pady=10)

    def calculate_tm(self, sequence, concentration):
        a = sequence.count('A')
        t = sequence.count('T')
        c = sequence.count('C')
        g = sequence.count('G')
        total = a + t + c + g
        if total == 0:
            return 0.0
        gc_percent = ((g + c) / total) * 100
        try:
            concentration = float(concentration)
            if concentration <= 0:
                raise ValueError("Concentration must be positive")
        except:
            concentration = DEFAULT_CONCENTRATION
        tm = 81.5 + (0.41 * gc_percent) - (675 / concentration)
        return round(tm, 1)

    def generate_primers(self):
        try:
            f_primer = self.ent_forward.get().strip().upper()
            r_primer = self.ent_reverse.get().strip().upper()
            concentration = self.ent_concentration.get().strip() or DEFAULT_CONCENTRATION
            if not f_primer or not r_primer:
                messagebox.showerror("Input Error", "Please enter both primers")
                return
            f_enzyme = self.cmb_forward_enzyme.get()
            r_enzyme = self.cmb_reverse_enzyme.get()
            if f_enzyme not in enzyme_linkers or r_enzyme not in enzyme_linkers:
                messagebox.showerror("Error", "Invalid enzyme selection")
                return
            if f_enzyme == "NdeI" and f_primer.startswith("ATG"):
                f_primer = f_primer[2:]
            cloning_f = COMMON_PREFIX + enzyme_linkers[f_enzyme] + f_primer
            cloning_r = COMMON_PREFIX + enzyme_linkers[r_enzyme] + r_primer
            f_len = len(cloning_f)
            r_len = len(cloning_r)
            f_tm = self.calculate_tm(cloning_f, concentration)
            r_tm = self.calculate_tm(cloning_r, concentration)
            self.update_result(self.txt_forward, cloning_f, f_len, f_tm)
            self.update_result(self.txt_reverse, cloning_r, r_len, r_tm)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_result(self, result_field, sequence, length, tm):
        result_field["text_widget"].config(state="normal")
        result_field["text_widget"].delete("1.0", tk.END)
        result_field["text_widget"].insert(tk.END, sequence)
        result_field["text_widget"].config(state="disabled")
        result_field["length"].config(text=f"Length: {length} bp")
        result_field["tm"].config(text=f"Tm: {tm} degC")

    def copy_to_clipboard(self, text_widget):
        text = text_widget.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Sequence copied to clipboard")

    def paste_to_entry(self, entry_widget):
        try:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, self.root.clipboard_get().strip())
        except:
            messagebox.showerror("Error", "Clipboard is empty")

    def clear_all(self):
        self.ent_forward.delete(0, tk.END)
        self.ent_reverse.delete(0, tk.END)
        self.ent_concentration.delete(0, tk.END)
        self.ent_concentration.insert(0, str(DEFAULT_CONCENTRATION))
        for result in [self.txt_forward, self.txt_reverse]:
            result["text_widget"].config(state="normal")
            result["text_widget"].delete("1.0", tk.END)
            result["text_widget"].config(state="disabled")
            result["length"].config(text="Length: - bp")
            result["tm"].config(text="Tm: - degC")
        messagebox.showinfo("Cleared", "All fields have been cleared")

    def open_file(self):
        filepath = filedialog.askopenfilename(title="Open File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = f.read()
                self.ent_forward.delete(0, tk.END)
                self.ent_forward.insert(tk.END, data)
                messagebox.showinfo("Opened", f"File opened: {filepath}")
            except Exception as e:
                messagebox.showerror("Open File Error", str(e))

    def save_file(self):
        filepath = filedialog.asksaveasfilename(title="Save File As", defaultextension=".txt",
                                                  filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("Forward:\n" + self.txt_forward["text_widget"].get("1.0", tk.END).strip() + "\n")
                    f.write("Reverse:\n" + self.txt_reverse["text_widget"].get("1.0", tk.END).strip() + "\n")
                messagebox.showinfo("Saved", f"File saved: {filepath}")
            except Exception as e:
                messagebox.showerror("Save File Error", str(e))

    def show_about(self):
        messagebox.showinfo(
            "About PLAGENOR Cloning Primer Designer",
            "PLAGENOR Cloning Primer Designer v1.0\nDeveloped by Dr. Mohamed Merzoug\nPLAGENOR, ESSBO - Algeria\n\n"
            "This tool assists in designing cloning primers with basic properties such as Tm and length.\n"
            "© 2025 All rights reserved."
        )

if __name__ == "__main__":
    try:
        root = tk.Tk()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=PRIMARY_COLOR, font=FONT)
        style.configure("TButton", font=FONT, padding=6, background=ACCENT_COLOR, foreground="white")
        style.map("TButton",
                  background=[("active", ACCENT_COLOR)],
                  foreground=[("active", "white")])
        PrimerDesigner(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Critical Error", f"Application failed to start:\n{str(e)}")