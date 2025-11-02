import tkinter as tk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, db
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from tkinter import ttk
import random
import string

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "Your URL"
    })

class LoginPage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login Perpustakaan UBSI")
        self.root.minsize(400, 600)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.configure(bg="#ffffff")
        
        self.main_container = tk.Frame(self.root, bg="#ffffff")
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Simpan referensi logo sebagai atribut class
        self.logo_photo = None
        self.setup_logo()

        self.login_frame = tk.Frame(self.main_container, bg="#ffffff")
        self.login_frame.grid(row=1, column=0, sticky="nsew")
        self.login_frame.grid_columnconfigure(0, weight=1)

        tk.Label(self.login_frame, text="ID Anggota:", bg="#ffffff", font=("Arial", 10)).pack(pady=(0,5))
        self.username_entry = tk.Entry(self.login_frame, width=30)
        self.username_entry.pack(ipady=8)

        tk.Label(self.login_frame, text="Password:", bg="#ffffff", font=("Arial", 10)).pack(pady=(15,5))
        self.password_entry = tk.Entry(self.login_frame, width=30, show="*")
        self.password_entry.pack(ipady=8)

        button_style = {
            "width": 25,
            "height": 2,
            "font": ("Arial", 10, "bold"),
            "borderwidth": 0,
            "cursor": "hand2"
        }

        login_button = tk.Button(
            self.login_frame,
            text="Login",
            command=self.login,
            bg="#9C5CCE",
            fg="white",
            **button_style
        )
        login_button.pack(pady=20)

        forgot_pass_button = tk.Button(
            self.login_frame,
            text="Lupa Password?",
            command=self.forgot_password,
            bg="#ffffff",
            fg="#9C5CCE",
            bd=0,
            font=("Arial", 9, "underline"),
            cursor="hand2"
        )
        forgot_pass_button.pack(pady=5)

        register_button = tk.Button(
            self.login_frame,
            text="Buat Akun Baru",
            command=self.show_register_page,
            bg="#4CAF50",
            fg="white",
            **button_style
        )
        register_button.pack(pady=15)

        self._bind_hover_effects(login_button, "#8445b5", "#9C5CCE")
        self._bind_hover_effects(register_button, "#3d8c40", "#4CAF50")

    def setup_logo(self):
        """Metode terpisah untuk setup logo"""
        self.logo_frame = tk.Frame(self.main_container, bg="#ffffff")
        self.logo_frame.grid(row=0, column=0, pady=20, sticky="ew")
        
        logo_path = os.path.join(os.path.dirname(__file__), "Image", "logo.jpg")
        try:
            # Buka dan resize gambar
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)
            
            # Simpan sebagai atribut class
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            # Buat label dan simpan referensi gambar
            logo_label = tk.Label(self.logo_frame, image=self.logo_photo, bg="#ffffff")
            logo_label.photo = self.logo_photo  # Simpan referensi di widget
            logo_label.pack()
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback text jika gambar gagal dimuat
            tk.Label(
                self.logo_frame, 
                text="PERPUSTAKAAN UBSI",
                font=("Arial", 16, "bold"),
                bg="#ffffff"
            ).pack(pady=20)

    def _bind_hover_effects(self, button, hover_color, normal_color):
        button.bind("<Enter>", lambda e: button.configure(bg=hover_color))
        button.bind("<Leave>", lambda e: button.configure(bg=normal_color))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Silakan lengkapi semua field")
            return

        try:
            ref = db.reference('anggota_perpus')
            users = ref.get()

            user_found = False
            for user in users.values():
                if user.get('id_anggota') == username and user.get('password') == password:
                    user_found = True
                    self.show_user_dashboard(user)
                    break

            if not user_found:
                messagebox.showerror("Error", "ID Anggota atau Password salah")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal login: {str(e)}")

    def forgot_password(self):
        username = self.username_entry.get()
        if not username:
            messagebox.showerror("Error", "Masukkan ID Anggota terlebih dahulu")
            return

        try:
            ref = db.reference('anggota_perpus')
            users = ref.get()

            user_found = False
            for user in users.values():
                if user.get('id_anggota') == username:
                    user_found = True
                    self.send_password_email(user.get('email'), user.get('password'), user.get('nama_lengkap'))
                    break

            if not user_found:
                messagebox.showerror("Error", "ID Anggota tidak ditemukan")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengirim password: {str(e)}")

    def send_password_email(self, email, password, name):
        sender_email = "aspiraass@gmail.com"
        app_password = "cybh reuw atfc mome"

        message = MIMEMultipart('related')
        message['Subject'] = "Password Recovery - Perpustakaan UBSI"
        message['From'] = sender_email
        message['To'] = email

        # HTML template
        html = f"""
        <div style="background-color: #ffffff; padding: 20px; font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
              
              <div style="text-align: center; margin-bottom: 20px;">
                  <img src="cid:logo" alt="Logo Perpustakaan UBSI" style="width: 100%; max-width: 150px; height: auto;" />
              </div>

              <div style="border-top: 2px solid #BA68C8; margin: 20px 0;"></div>

              <h2 style="text-align: center; color: #333; font-size: 24px;">Password Recovery</h2>
              
              <div style="text-align: left; margin: 20px 0;">
                  <p style="font-size: 16px; color: #333;">Halo {name},</p>
                  <p style="font-size: 16px; color: #333;">Berikut adalah password akun perpustakaan Anda:</p>
                  
                  <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                      <p style="margin: 5px 0;"><strong>Password:</strong> {password}</p>
                  </div>
                  
                  <p style="font-size: 16px; color: #333;">Silakan gunakan password ini untuk login ke akun Anda.</p>
              </div>

              <div style="text-align: center; margin-top: 30px;">
                  <a href="https://perpustakaan.ubsi.ac.id/" 
                     style="display: inline-flex; justify-content: center; align-items: center; background-color: #9C5CCE; color: #fff; padding: 10px 20px; font-size: 18px; font-weight: bold; text-decoration: none; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);">
                      Kunjungi Perpustakaan
                  </a>
              </div>

              <p style="text-align: center; color: #666; font-size: 15px; margin-top: 20px;">Terima kasih telah menggunakan layanan Perpustakaan UBSI!</p>
              <p style="text-align: center; color: #999; margin-top: 20px; font-size: 14px;">&copy; 2024 Perpustakaan UBSI. Seluruh hak cipta dilindungi.</p>
            </div>
        </div>
        """

        msg_alternative = MIMEMultipart('alternative')
        message.attach(msg_alternative)
        msg_html = MIMEText(html, 'html')
        msg_alternative.attach(msg_html)

        # Tambahkan logo
        try:
            with open('Image/logo.jpg', 'rb') as logo_file:
                msg_image = MIMEImage(logo_file.read())
                msg_image.add_header('Content-ID', '<logo>')
                message.attach(msg_image)
        except Exception as e:
            print(f"Error menambahkan logo: {e}")

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, app_password)
                server.send_message(message)
            messagebox.showinfo("Sukses", "Password telah dikirim ke email Anda")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengirim email: {str(e)}")

    def show_register_page(self):
        self.root.withdraw()  # Sembunyikan halaman login
        try:
            import subprocess
            process = subprocess.Popen(['python', 'registerUser.py'])
            
            # Tunggu sampai proses registerUser.py selesai
            process.wait()
            
            # Setelah register selesai, tampilkan kembali login
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka halaman registrasi: {str(e)}")
            self.root.deiconify()

    def on_register_close(self, register_window):
        register_window.root.destroy()
        self.root.deiconify()  # Tampilkan kembali halaman login

    def show_user_dashboard(self, user_data):
        self.root.withdraw()  # Sembunyikan halaman login
        UserDashboard(user_data)

    def run(self):
        self.root.mainloop()

class RegisterPage:
    def __init__(self, login_page):
        self.login_page = login_page
        self.root = tk.Toplevel()
        self.root.title("Registrasi Anggota Perpustakaan UBSI")
        self.root.geometry("500x800")
        self.root.configure(bg="#ffffff")
        
        # Main container
        main_container = tk.Frame(self.root, bg="#ffffff")
        main_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Simpan referensi logo sebagai atribut class
        self.logo_photo = None
        self.setup_logo(main_container)

        # Judul
        tk.Label(
            main_container,
            text="REGISTRASI ANGGOTA PERPUSTAKAAN",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#9C5CCE"
        ).pack(pady=(0, 20))

        # Form fields dalam scrollable frame
        canvas = tk.Canvas(main_container, bg="#ffffff")
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.form_frame = tk.Frame(canvas, bg="#ffffff")

        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar dan canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw", width=canvas.winfo_reqwidth())

        # Form fields
        fields = [
            ("Nama Lengkap*", "nama_lengkap"),
            ("Jenis Kelamin*", "jenis_kelamin", ["Laki-laki", "Perempuan"]),
            ("Tempat Lahir*", "tempat_lahir"),
            ("Tanggal Lahir*", "tanggal_lahir"),
            ("Jenis Identitas*", "jenis_identitas", ["KTP", "SIM", "Kartu Pelajar"]),
            ("Nomor Identitas*", "nomor_identitas"),
            ("Email*", "email"),
            ("Password*", "password"),
            ("Jenis Anggota*", "jenis_anggota", ["Mahasiswa", "Dosen", "Umum"]),
            ("Program Studi*", "program_studi"),
            ("Alamat*", "alamat"),
            ("Kota*", "kota"),
            ("No. Telepon*", "telepon")
        ]

        self.entries = {}
        for i, field_data in enumerate(fields):
            frame = tk.Frame(self.form_frame, bg="#ffffff")
            frame.pack(fill="x", pady=5)

            if len(field_data) == 3:  # Combobox
                label_text, field_name, options = field_data
                tk.Label(
                    frame,
                    text=label_text,
                    bg="#ffffff",
                    font=("Arial", 10)
                ).pack(anchor="w")
                
                combo = ttk.Combobox(frame, values=options, state="readonly", width=27)
                combo.pack(anchor="w")
                self.entries[field_name] = combo
            else:  # Normal Entry
                label_text, field_name = field_data
                tk.Label(
                    frame,
                    text=label_text,
                    bg="#ffffff",
                    font=("Arial", 10)
                ).pack(anchor="w")
                
                entry = tk.Entry(frame, width=30)
                if field_name == "password":
                    entry.config(show="*")
                entry.pack(anchor="w")
                self.entries[field_name] = entry

        # Buttons frame
        button_frame = tk.Frame(main_container, bg="#ffffff")
        button_frame.pack(fill="x", pady=20)

        # Register button
        register_button = tk.Button(
            button_frame,
            text="Daftar",
            command=self.register,
            bg="#9C5CCE",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2
        )
        register_button.pack(pady=(0, 10))

        # Back button
        back_button = tk.Button(
            button_frame,
            text="Kembali ke Login",
            command=self.back_to_login,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11),
            width=20,
            height=2
        )
        back_button.pack()

        # Configure canvas scrolling
        self.form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def setup_logo(self, container):
        """Metode terpisah untuk setup logo"""
        logo_path = os.path.join(os.path.dirname(__file__), "Image", "logo.jpg")
        try:
            # Buka dan resize gambar
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)
            
            # Simpan sebagai atribut class
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            # Buat label dan simpan referensi gambar
            logo_label = tk.Label(container, image=self.logo_photo, bg="#ffffff")
            logo_label.photo = self.logo_photo  # Simpan referensi di widget
            logo_label.pack(pady=(0, 20))
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback text jika gambar gagal dimuat
            tk.Label(
                container,
                text="PERPUSTAKAAN UBSI",
                font=("Arial", 16, "bold"),
                bg="#ffffff"
            ).pack(pady=(0, 20))

    def generate_member_id(self):
        # Generate random ID: MBR-XXXX (X = random alphanumeric)
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choice(chars) for _ in range(4))
        return f"MBR-{random_part}"

    def register(self):
        # Validasi semua field required
        for field_name, entry in self.entries.items():
            if isinstance(entry, ttk.Combobox):
                if not entry.get():
                    messagebox.showerror("Error", f"Silakan pilih {field_name.replace('_', ' ').title()}")
                    return
            elif not entry.get().strip():
                messagebox.showerror("Error", f"Silakan lengkapi {field_name.replace('_', ' ').title()}")
                return

        # Validasi format email
        email = self.entries['email'].get()
        if '@' not in email or '.' not in email:
            messagebox.showerror("Error", "Format email tidak valid")
            return

        try:
            ref = db.reference('anggota_perpus')
            
            # Generate ID Anggota unik
            while True:
                member_id = self.generate_member_id()
                # Cek apakah ID sudah ada
                users = ref.get() or {}
                if not any(user.get('id_anggota') == member_id for user in users.values()):
                    break

            # Siapkan data user
            user_data = {
                'id_anggota': member_id,
                'nama_lengkap': self.entries['nama_lengkap'].get(),
                'jenis_kelamin': self.entries['jenis_kelamin'].get(),
                'tempat_lahir': self.entries['tempat_lahir'].get(),
                'tanggal_lahir': self.entries['tanggal_lahir'].get(),
                'jenis_identitas': self.entries['jenis_identitas'].get(),
                'nomor_identitas': self.entries['nomor_identitas'].get(),
                'email': self.entries['email'].get(),
                'password': self.entries['password'].get(),
                'jenis_anggota': self.entries['jenis_anggota'].get(),
                'program_studi': self.entries['program_studi'].get(),
                'alamat': self.entries['alamat'].get(),
                'kota': self.entries['kota'].get(),
                'telepon': self.entries['telepon'].get()
            }
            
            # Simpan ke Firebase
            ref.push(user_data)
            
            # Tampilkan ID Anggota
            messagebox.showinfo(
                "Registrasi Berhasil", 
                f"Registrasi berhasil!\nID Anggota Anda: {member_id}\n\nSilakan login menggunakan ID Anggota ini."
            )
            self.back_to_login()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mendaftar: {str(e)}")

    def back_to_login(self):
        self.root.destroy()
        self.login_page.root.deiconify()

class UserDashboard:
    def __init__(self, user_data):
        self.root = tk.Tk()
        self.root.title("Dashboard Perpustakaan UBSI")
        self.root.geometry("800x600")
        self.root.configure(bg="#ffffff")
        self.user_data = user_data

        # Create main container
        self.main_container = tk.Frame(self.root, bg="#ffffff")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header with user info
        self.create_header()

        # Create tabs
        self.create_tabs()

    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg="#ffffff")
        header_frame.pack(fill="x", pady=(0, 20))

        # User info
        user_info = f"Selamat datang, {self.user_data.get('nama_lengkap', 'User')}!"
        tk.Label(
            header_frame, 
            text=user_info,
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        ).pack(side="left")

        # Logout button
        tk.Button(
            header_frame,
            text="Logout",
            command=self.logout,
            bg="#dc3545",
            fg="white",
            font=("Arial", 10)
        ).pack(side="right")

    def create_tabs(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True)

        # Profile tab
        self.profile_tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.profile_tab, text="Profile")
        self.create_profile_tab()

        # Search books tab
        self.search_tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.search_tab, text="Cari Buku")
        self.create_search_tab()

        # Loan history tab
        self.history_tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.history_tab, text="Riwayat Peminjaman")
        self.create_history_tab()

    def create_profile_tab(self):
        # Display user information
        fields = [
            ("Nama Lengkap:", "nama_lengkap"),
            ("ID Anggota:", "id_anggota"),
            ("Email:", "email"),
            ("No. Telepon:", "telepon"),
            ("Alamat:", "alamat")
        ]

        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(
                self.profile_tab,
                text=label_text,
                bg="#ffffff",
                font=("Arial", 10, "bold")
            ).pack(pady=(10, 0))
            
            tk.Label(
                self.profile_tab,
                text=self.user_data.get(field_name, "N/A"),
                bg="#ffffff"
            ).pack()

    def create_search_tab(self):
        # Search frame
        search_frame = tk.Frame(self.search_tab, bg="#ffffff")
        search_frame.pack(fill="x", pady=10)

        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="Cari",
            command=self.search_books,
            bg="#9C5CCE",
            fg="white"
        ).pack(side="left")

        # Results
        self.results_frame = tk.Frame(self.search_tab, bg="#ffffff")
        self.results_frame.pack(fill="both", expand=True)

    def create_history_tab(self):
        # Create treeview for loan history
        columns = ("Judul Buku", "Tanggal Pinjam", "Tanggal Kembali", "Status")
        self.history_tree = ttk.Treeview(self.history_tab, columns=columns, show="headings")

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)

        self.history_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_loan_history()

    def search_books(self):
        search_term = self.search_entry.get().lower()
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        try:
            ref = db.reference('books')
            books = ref.get() or {}

            found = False
            for book in books.values():
                if (search_term in book.get('judul', '').lower() or 
                    search_term in book.get('penulis', '').lower()):
                    found = True
                    self.create_book_card(book)

            if not found:
                tk.Label(
                    self.results_frame,
                    text="Tidak ada buku yang ditemukan",
                    bg="#ffffff"
                ).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mencari buku: {str(e)}")

    def create_book_card(self, book):
        card = tk.Frame(
            self.results_frame,
            bg="#f8f9fa",
            relief="solid",
            borderwidth=1
        )
        card.pack(fill="x", padx=10, pady=5)

        tk.Label(
            card,
            text=book.get('judul', 'N/A'),
            font=("Arial", 12, "bold"),
            bg="#f8f9fa"
        ).pack(anchor="w", padx=10, pady=5)

        tk.Label(
            card,
            text=f"Penulis: {book.get('penulis', 'N/A')}",
            bg="#f8f9fa"
        ).pack(anchor="w", padx=10)

        tk.Label(
            card,
            text=f"Tahun Terbit: {book.get('tahun_terbit', 'N/A')}",
            bg="#f8f9fa"
        ).pack(anchor="w", padx=10, pady=5)

    def load_loan_history(self):
        try:
            ref = db.reference('peminjaman')
            loans = ref.get() or {}

            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            for loan in loans.values():
                if loan.get('id_anggota') == self.user_data.get('id_anggota'):
                    self.history_tree.insert('', 'end', values=(
                        loan.get('judul_buku', 'N/A'),
                        loan.get('tanggal_pinjam', 'N/A'),
                        loan.get('tanggal_kembali', 'N/A'),
                        loan.get('status', 'N/A')
                    ))

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat riwayat: {str(e)}")

    def logout(self):
        self.root.destroy()
        self.login_page.root.deiconify()

if __name__ == "__main__":
    login_page = LoginPage()
    login_page.run()