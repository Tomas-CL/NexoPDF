import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import threading


class NexoPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexo PDF")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self.source_folder = tk.StringVar(value=os.path.expanduser("~"))
        self.destination_folder = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "PDFs"))

        self.create_widgets()
        self.ensure_destination_folder()

    def ensure_destination_folder(self):
        dest = self.destination_folder.get()
        if not os.path.exists(dest):
            os.makedirs(dest)

    def create_widgets(self):
        tk.Label(self.root, text="Nexo PDF", font=("Arial", 20, "bold")).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Carpeta origen:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frame, textvariable=self.source_folder, width=40).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Buscar", command=self.select_source).grid(row=0, column=2)

        tk.Label(frame, text="Carpeta destino:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frame, textvariable=self.destination_folder, width=40).grid(row=1, column=1, padx=5)
        tk.Button(frame, text="Buscar", command=self.select_destination).grid(row=1, column=2)

        self.start_button = tk.Button(self.root, text="Iniciar escaneo", font=("Arial", 12), command=self.start_scan)
        self.start_button.pack(pady=20)

        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=10)

    def select_source(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta origen")
        if folder:
            self.source_folder.set(folder)

    def select_destination(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta destino")
        if folder:
            self.destination_folder.set(folder)

    def scan_and_copy(self):
        source = self.source_folder.get()
        destination = self.destination_folder.get()

        if not source or not destination:
            self.root.after(0, lambda: messagebox.showerror("Error", "Seleccione ambas carpetas"))
            self.root.after(0, self.enable_button)
            return

        if not os.path.exists(destination):
            os.makedirs(destination)

        pdf_files = []
        for root_dir, dirs, files in os.walk(source):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append((os.path.join(root_dir, file), file))

        total = len(pdf_files)
        copied = 0
        duplicates = 0

        self.root.after(0, lambda: self.status_label.config(text=f"Escaneando... 0/{total}"))

        for i, (src_path, filename) in enumerate(pdf_files):
            dest_path = os.path.join(destination, filename)

            if os.path.exists(dest_path):
                duplicates += 1
            else:
                shutil.copy2(src_path, dest_path)
                copied += 1

            self.root.after(0, lambda i=i: self.status_label.config(text=f"Procesando... {i + 1}/{total}"))

        self.root.after(0, lambda: self.status_label.config(text=f"Completado: {copied} copiados, {duplicates} duplicados"))
        self.root.after(0, self.enable_button)
        self.root.after(0, lambda: messagebox.showinfo("Completado", f"Se copiaron {copied} archivos PDF.\n{duplicates} archivos duplicados fueron omitidos."))
        self.root.after(0, lambda: os.startfile(destination) if os.name == 'nt' else os.system(f'xdg-open "{destination}"'))

    def start_scan(self):
        self.start_button.config(state="disabled")
        thread = threading.Thread(target=self.scan_and_copy)
        thread.start()

    def enable_button(self):
        self.start_button.config(state="normal")


def main():
    root = tk.Tk()
    app = NexoPDFApp(root)
    root.mainloop()

main()
