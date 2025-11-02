import tkinter as tk
from tkinter import messagebox, ttk
import firebase_admin
from firebase_admin import credentials, db
import random

# Firebase Initialization
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "Your URL"
})

class BookInputApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Form Input Buku")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Buat frame utama dengan padding dan margin
        self.main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Judul form
        self.title_label = tk.Label(
            self.main_frame,
            text="FORM INPUT BUKU",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        self.title_label.pack(pady=(0, 20))

        # Frame untuk form
        self.form_frame = tk.LabelFrame(
            self.main_frame,
            text="Data Buku",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=20,
            bg="white",
            relief=tk.GROOVE
        )
        self.form_frame.pack(fill=tk.BOTH, expand=True)

        # Style untuk entry fields
        self.style = ttk.Style()
        self.style.configure(
            "Custom.TEntry",
            padding=10,
            relief="flat",
            fieldbackground="#f8f9fa"
        )

        # Membuat dan menempatkan form fields
        self.entries = {}
        self.create_form_fields()

        # Tombol Submit
        self.submit_button = tk.Button(
            self.main_frame,
            text="Simpan Data Buku",
            command=self.submit_book,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.RAISED,
            padx=30,
            pady=15,
            cursor="hand2"
        )
        self.submit_button.pack(pady=20)

        # Bind hover effects
        self.submit_button.bind("<Enter>", self.on_enter)
        self.submit_button.bind("<Leave>", self.on_leave)

    def create_form_fields(self):
        fields = {
            "judul": "Judul Buku",
            "penulis": "Penulis",
            "tahun": "Tahun Terbit",
            "genre": "Genre",
            "deskripsi": "Deskripsi",
            "jumlah": "Jumlah Buku"
        }

        for i, (key, label) in enumerate(fields.items()):
            # Container frame untuk setiap field
            field_frame = tk.Frame(self.form_frame, bg="white")
            field_frame.pack(fill=tk.X, pady=10)

            # Label
            tk.Label(
                field_frame,
                text=f"{label} *",
                font=("Arial", 11),
                bg="white",
                width=15,
                anchor="w"
            ).pack(side=tk.LEFT)

            # Entry
            entry = ttk.Entry(
                field_frame,
                style="Custom.TEntry",
                width=40,
                font=("Arial", 11)
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
            
            self.entries[key] = entry
            self.set_placeholder(entry, f"Masukkan {label.lower()}")

    def set_placeholder(self, entry, placeholder):
        entry.insert(0, placeholder)
        entry.config(foreground='gray')
        
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground='black')
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground='gray')
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    def on_enter(self, e):
        self.submit_button.config(bg="#45a049")

    def on_leave(self, e):
        self.submit_button.config(bg="#4CAF50")

    def submit_book(self):
        # Validasi fields
        for key, entry in self.entries.items():
            value = entry.get()
            if value == "" or entry.cget('foreground') == 'gray':
                messagebox.showwarning(
                    "Input Error",
                    "Semua field harus diisi!",
                    parent=self.root
                )
                return

        # Validasi jumlah buku
        try:
            jumlah_buku = int(self.entries['jumlah'].get())
            if jumlah_buku <= 0:
                messagebox.showwarning(
                    "Input Error",
                    "Jumlah buku harus lebih dari 0!",
                    parent=self.root
                )
                return
        except ValueError:
            messagebox.showwarning(
                "Input Error",
                "Jumlah buku harus berupa angka!",
                parent=self.root
            )
            return

        # Generate kode unik
        unique_code = f"BOOK-{random.randint(10000, 99999)}"

        # Menyiapkan data
        book_data = {
            "judul": self.entries['judul'].get(),
            "penulis": self.entries['penulis'].get(),
            "tahun_terbit": self.entries['tahun'].get(),
            "genre": self.entries['genre'].get(),
            "deskripsi": self.entries['deskripsi'].get(),
            "jumlah_buku": jumlah_buku,
            "kode_unik": unique_code,
        }

        try:
            ref = db.reference('books')
            ref.push(book_data)
            messagebox.showinfo(
                "Sukses",
                f"Data buku berhasil disimpan!\nKode Unik: {unique_code}",
                parent=self.root
            )
            self.clear_fields()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Gagal menyimpan data buku: {str(e)}",
                parent=self.root
            )

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            if hasattr(entry, '_placeholder'):
                self.set_placeholder(entry, entry._placeholder)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookInputApp(root)
    root.mainloop()