import random
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageTk
import qrcode
import firebase_admin
from firebase_admin import credentials, db
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Firebase Initialization
cred = credentials.Certificate("firebase-key.json")  # Change to your JSON key path
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://perpustakaan-859b4-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# Global Variables
background_path = "Image/background.jpg"
foto_path = 'Image/profile.jpg'
msg = MIMEMultipart()

# Locations for dropdown locations
locations = {
    "Aceh": ["Banda Aceh", "Sabang", "Langsa", "Lhokseumawe", "Subulussalam"],
    "Sumatera Utara": ["Medan", "Binjai", "Tebing Tinggi", "Pematangsiantar", "Sibolga", "Tanjungbalai", "Padangsidimpuan", "Gunungsitoli"],
    "Sumatera Barat": ["Padang", "Bukittinggi", "Payakumbuh", "Solok", "Pariaman", "Padang Panjang", "Sawahlunto"],
    "Riau": ["Pekanbaru", "Dumai"],
    "Kepulauan Riau": ["Batam", "Tanjungpinang"],
    "Jambi": ["Jambi", "Sungai Penuh"],
    "Sumatera Selatan": ["Palembang", "Lubuklinggau", "Prabumulih", "Pagar Alam"],
    "Bengkulu": ["Bengkulu"],
    "Lampung": ["Bandar Lampung", "Metro"],
    "Bangka Belitung": ["Pangkalpinang"],
    "Banten": ["Serang", "Tangerang", "Tangerang Selatan", "Cilegon"],
    "Jawa Barat": ["Bandung", "Bekasi", "Bogor", "Cimahi", "Cirebon", "Depok", "Sukabumi", "Tasikmalaya", "Banjar"],
    "Jawa Tengah": ["Semarang", "Surakarta", "Magelang", "Pekalongan", "Salatiga", "Tegal"],
    "Daerah Istimewa Yogyakarta": ["Yogyakarta"],
    "Jawa Timur": ["Surabaya", "Malang", "Kediri", "Madiun", "Mojokerto", "Pasuruan", "Probolinggo", "Blitar", "Batu"],
    "DKI Jakarta": ["Jakarta Barat", "Jakarta Pusat", "Jakarta Selatan", "Jakarta Timur", "Jakarta Utara"],
    "Bali": ["Denpasar"],
    "Nusa Tenggara Barat": ["Mataram", "Bima"],
    "Nusa Tenggara Timur": ["Kupang"],
    "Kalimantan Barat": ["Pontianak", "Singkawang"],
    "Kalimantan Tengah": ["Palangka Raya"],
    "Kalimantan Selatan": ["Banjarmasin", "Banjarbaru"],
    "Kalimantan Timur": ["Samarinda", "Balikpapan", "Bontang"],
    "Kalimantan Utara": ["Tarakan"],
    "Sulawesi Utara": ["Manado", "Bitung", "Tomohon", "Kotamobagu"],
    "Sulawesi Tengah": ["Palu"],
    "Sulawesi Selatan": ["Makassar", "Parepare", "Palopo"],
    "Sulawesi Tenggara": ["Kendari", "Baubau"],
    "Gorontalo": ["Gorontalo"],
    "Maluku": ["Ambon", "Tual"],
    "Maluku Utara": ["Ternate", "Tidore Kepulauan"],
    "Papua": ["Jayapura"],
    "Papua Barat Daya": ["Sorong"],
    "Nusantara": ["Nusantara"]
}


entries = []
id_anggota = f"PU-{random.randint(10**8, 10**9 - 1)}"

# Helper Function to Create Library Card
def buat_kartu_perpus(nama_lengkap, jenis_anggota, foto_path, background_path, output_path):
    lebar_kartu, tinggi_kartu = 600, 1050
    background = Image.open(background_path).resize((lebar_kartu, tinggi_kartu))
    kartu = background.copy()
    draw = ImageDraw.Draw(kartu)

    try:
        font_nama = ImageFont.truetype("arial.ttf", 32)
        font_jenis_anggota = ImageFont.truetype("arialbd.ttf", 43)
        font_id_anggota = ImageFont.truetype("arialbd.ttf", 50)
    except IOError:
        font_nama = font_jenis_anggota = font_id_anggota = ImageFont.load_default()

    foto = Image.open(foto_path).resize((280, 280))
    mask = Image.new("L", foto.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, foto.width, foto.height), fill=255)

    kartu.paste(foto, (65, 80), mask)
    draw.text((60, 775), nama_lengkap.upper(), fill="black", font=font_nama)
    draw.text((60, 823), jenis_anggota.upper(), fill="black", font=font_jenis_anggota)
    draw.text((60, 953), id_anggota, fill="black", font=font_id_anggota)

    qr = qrcode.QRCode(box_size=20, border=1)
    qr.add_data(id_anggota)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((100, 100))

    kartu.paste(qr_img, (lebar_kartu - 170, tinggi_kartu - 120))
    kartu.save(output_path)

    return id_anggota

# Firebase Save Function
def simpan_ke_firebase(data):
    try:
        ref = db.reference("anggota_perpus")
        ref.push(data)
        print("Data berhasil disimpan ke Firebase.")
    except Exception as e:
        print(f"Error saat menyimpan data ke Firebase: {e}")

# Function to Update City Dropdown based on selected province
def update_kota(event):
    selected_province_identitas = combo_provinsi_identitas.get()
    combo_kota_identitas['values'] = locations.get(selected_province_identitas, [])
    
    selected_province_saat_ini = combo_provinsi_saat_ini.get()
    combo_kota_saat_ini['values'] = locations.get(selected_province_saat_ini, [])

# Function to Capture Photo
def capture_photo():
    global foto_path
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Error", "Tidak dapat mengakses kamera.")
        return

    def take_picture():
        nonlocal cap
        ret, frame = cap.read()
        if ret:
            if not os.path.exists('Image'):
                os.makedirs('Image')
            cv2.imwrite(foto_path, frame)
            cv2.imshow("Captured Photo", frame)
        else:
            messagebox.showerror("Error", "Gagal mengambil foto.")

    def close_camera():
        cap.release()
        cv2.destroyAllWindows()
        camera_window.destroy()
        finish_capture()  # Call finish_capture after closing camera

    camera_window = tk.Toplevel(root)
    camera_window.title("Ambil Foto")
    
    tk.Button(camera_window, text="Ambil Foto", command=take_picture).pack(pady=10)
    tk.Button(camera_window, text="Selesai", command=close_camera).pack(pady=10)

# Function to Send Email with Attachment

def send_email(receiver_email, subject, body_html, attachment_path, logo_path):
    sender_email = 'aspiraass@gmail.com'
    app_password = 'cybh reuw atfc mome' 

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body_html, 'html'))

    with open(attachment_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        msg.attach(part)

    with open(logo_path, 'rb') as logo:
        logo_part = MIMEBase('application', 'octet-stream')
        logo_part.set_payload(logo.read())
        encoders.encode_base64(logo_part)
        logo_part.add_header('Content-Disposition', 'inline', filename='logo.jpg')
        logo_part.add_header('Content-ID', '<logo>')
        msg.attach(logo_part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)

# Function to Finish Capture and Create Card
def finish_capture():
    nama = entry_nama.get()
    jenis_anggota = combo_jenis_anggota.get() 

    if not foto_path:
        messagebox.showerror("Error", "Harap ambil foto terlebih dahulu.")
        return

    output_path = "./output/kartu_anggota.png"
    
    try:
        # Membuat kartu anggota
        id_anggota_created = buat_kartu_perpus(nama, jenis_anggota, foto_path, background_path, output_path)

        messagebox.showinfo("Sukses", f"Kartu anggota berhasil dibuat dengan ID {id_anggota_created}. Buka email Anda, untuk mendownload kartu.")
        
        # Kirim kartu melalui email setelah pembuatan.
        receiver_email = entry_email.get()
        subject = 'Library Card'
        
        # Body HTML dengan format responsif
        body_html = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* Reset CSS */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                /* Container utama */
                .container {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                }}
                
                /* Header dengan logo */
                .header {{
                    text-align: center;
                    padding: 20px 0;
                }}
                
                .header img {{
                    width: 150px;
                    height: auto;
                    max-width: 100%;
                }}
                
                /* Divider */
                .divider {{
                    border-top: 2px solid #BA68C8;
                    margin: 20px 0;
                }}
                
                /* Konten */
                .content {{
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                
                /* Heading */
                h2 {{
                    color: #333;
                    font-size: 24px;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                
                /* Info ID dan Password */
                .info-box {{
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                    text-align: center;
                }}
                
                .info-label {{
                    font-size: 16px;
                    color: #333;
                    margin-bottom: 5px;
                }}
                
                .info-value {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #BA68C8;
                }}
                
                /* Tombol */
                .button {{
                    display: inline-block;
                    background-color: #9C5CCE;
                    color: #ffffff;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                
                /* Footer */
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                
                /* Media Queries */
                @media only screen and (max-width: 480px) {{
                    .container {{
                        padding: 10px;
                    }}
                    
                    .content {{
                        padding: 15px;
                    }}
                    
                    h2 {{
                        font-size: 20px;
                    }}
                    
                    .info-value {{
                        font-size: 18px;
                    }}
                    
                    .button {{
                        display: block;
                        text-align: center;
                        margin: 20px auto;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <div class="header">
                        <img src="cid:logo" alt="Logo Perpustakaan UBSI">
                    </div>
                    
                    <div class="divider"></div>
                    
                    <h2>Kartu Anggota Perpustakaan UBSI</h2>
                    <p style="text-align: center; font-size: 18px;">Selamat! Kartu anggota Anda telah berhasil dibuat.</p>
                    
                    <div class="info-box">
                        <p class="info-label">ID Anggota Anda:</p>
                        <p class="info-value">{id_anggota_created}</p>
                        
                        <p class="info-label" style="margin-top: 15px;">Password Anda:</p>
                        <p class="info-value">{entry_password.get()}</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://perpustakaan.ubsi.ac.id/" class="button">
                            Kunjungi Perpustakaan
                        </a>
                    </div>
                    
                    <div class="footer">
                        <p>Terima kasih telah bergabung dengan kami!</p>
                        <p style="margin-top: 10px;">&copy; 2024 Perpustakaan UBSI. Seluruh hak cipta dilindungi.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        logo_path = 'Image/logo.jpg'
        send_email(receiver_email, subject, body_html, output_path, logo_path)
        
        # Menampilkan kartu yang telah dibuat
        tampilkan_kartu(output_path)

    except Exception as e:
        messagebox.showerror("Error", f"Gagal membuat kartu anggota: {str(e)}")

# Function to Display Card
def tampilkan_kartu(image_path):
    frame_kartu = tk.Toplevel(root)
    frame_kartu.title("Kartu Anggota")
    
    img = Image.open(image_path).resize((300, 500))
    
    img_tk = ImageTk.PhotoImage(img)
    
    label = tk.Label(frame_kartu, image=img_tk)
    
    label.image = img_tk 
    label.pack()
    
    tk.Button(frame_kartu, text="Tutup", command=frame_kartu.destroy).pack(pady=10)

# Function to copy address if checkbox is checked
def copy_address_if_same():
    if same_address_var.get():  # Check if the checkbox is checked
        # Copy values from identity fields to current address fields
        entry_alamat_saat_ini.delete(0, tk.END)
        entry_alamat_saat_ini.insert(0, entry_alamat_identitas.get())
        entry_alamat_saat_ini.config(fg='black')  # Set warna teks menjadi hitam
        
        combo_provinsi_saat_ini.set(combo_provinsi_identitas.get())
        combo_kota_saat_ini.set(combo_kota_identitas.get())
    else:
        # Reset fields when unchecked
        entry_alamat_saat_ini.delete(0, tk.END)
        entry_alamat_saat_ini.insert(0, "Masukkan alamat saat ini")
        entry_alamat_saat_ini.config(fg='gray')
        
        combo_provinsi_saat_ini.set("Pilih Provinsi")
        combo_kota_saat_ini.set("Pilih Kota/Kabupaten")

def set_placeholder(entry, placeholder):
    if isinstance(entry, tk.Entry):  # Pastikan hanya Entry widget yang mendapat placeholder
        entry.delete(0, tk.END)  # Hapus teks yang ada
        entry.insert(0, placeholder)
        entry.config(fg='gray')
        
        def on_focus_in(event):
            if entry.get() == placeholder and entry.cget('fg') == 'gray':
                entry.delete(0, tk.END)
                entry.config(fg='black')
                if entry == entry_password:  # Khusus untuk field password
                    entry.config(show='*')
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg='gray')
                if entry == entry_password:  # Khusus untuk field password
                    entry.config(show='')  # Hilangkan karakter tersembunyi untuk menampilkan placeholder
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

def submit_data():
    # Validasi combobox
    if (combo_provinsi_identitas.get() == "Pilih Provinsi" or
        combo_kota_identitas.get() == "Pilih Kota/Kabupaten" or
        combo_provinsi_saat_ini.get() == "Pilih Provinsi" or
        combo_kota_saat_ini.get() == "Pilih Kota/Kabupaten" or
        combo_jenis_anggota.get() == "Pilih Jenis Anggota" or
        combo_pendidikan.get() == "Pilih Pendidikan" or
        combo_jenis_kelamin.get() == "Pilih Jenis Kelamin" or
        combo_pekerjaan.get() == "Pilih Pekerjaan"):
        messagebox.showwarning("Input Error", "Mohon pilih semua opsi pada dropdown!")
        return

    # Validasi entry fields
    for entry in [entry_nama, entry_nomor_identitas, entry_tempat_lahir, 
                 entry_alamat_identitas, entry_alamat_saat_ini, entry_password,
                 entry_nomor_hp, entry_email, entry_nama_institut, entry_alamat_institut]:
        value = entry.get()
        if value == "" or (entry.cget('fg') == 'gray'):
            messagebox.showwarning("Input Error", "Semua field harus diisi!")
            return
    
    # Validasi format email
    email = entry_email.get()
    if not email.endswith("@gmail.com"):
        messagebox.showwarning("Input Error", "Email harus menggunakan domain @gmail.com!")
        return
            
    if not check_var.get():
        messagebox.showwarning("Input Error", "Anda harus setuju untuk menaati peraturan!")
        return
    
    # Jika semua validasi berhasil, lanjutkan dengan menyimpan data
    data = {
        "nama_lengkap": entry_nama.get(),
        "nomor_identitas": entry_nomor_identitas.get(),
        "tempat_lahir": entry_tempat_lahir.get(),
        "tanggal_lahir": entry_tanggal_lahir.get(),
        "alamat_identitas": entry_alamat_identitas.get(),
        "provinsi_identitas": combo_provinsi_identitas.get(),
        "kota_identitas": combo_kota_identitas.get(),
        "alamat_saat_ini": entry_alamat_saat_ini.get(),
        "provinsi_saat_ini": combo_provinsi_saat_ini.get(),
        "kota_saat_ini": combo_kota_saat_ini.get(),
        "jenis_anggota": combo_jenis_anggota.get(),
        "pendidikan": combo_pendidikan.get(),
        "jenis_kelamin": combo_jenis_kelamin.get(),
        "pekerjaan": combo_pekerjaan.get(),
        "password": entry_password.get(),
        "nomor_hp": entry_nomor_hp.get(),
        "email": entry_email.get(),
        "nama_institut": entry_nama_institut.get(),
        "alamat_institut": entry_alamat_institut.get(),
        "id_anggota": id_anggota,
    }
     
    simpan_ke_firebase(data)
    capture_photo()

# Creating GUI with Tkinter
root = tk.Tk()
root.title("Form Pendaftaran Anggota Perpustakaan")

frame_pribadi = tk.LabelFrame(root, text="Data Pribadi", padx=5, pady=5)
frame_pribadi.pack(padx=5, pady=5)

entry_width = 25

tk.Label(frame_pribadi, text='1. Nama Lengkap *').grid(row=0, column=0, sticky='w', padx=3, pady=2)
entry_nama = tk.Entry(frame_pribadi, width=entry_width)
entry_nama.grid(row=0, column=1, padx=3, pady=2)
set_placeholder(entry_nama, "Masukkan nama lengkap")

tk.Label(frame_pribadi, text='2. No Identitas *').grid(row=1, column=0, sticky='w', padx=3, pady=2)
entry_nomor_identitas = tk.Entry(frame_pribadi, width=entry_width)
entry_nomor_identitas.grid(row=1, column=1, padx=3, pady=2)
set_placeholder(entry_nomor_identitas, "Masukkan nomor identitas")

tk.Label(frame_pribadi, text='3. Tempat Lahir *').grid(row=2, column=0, sticky='w', padx=3, pady=2)
entry_tempat_lahir = tk.Entry(frame_pribadi, width=entry_width)
entry_tempat_lahir.grid(row=2, column=1, padx=3, pady=2)
set_placeholder(entry_tempat_lahir, "Masukkan tempat lahir")

tk.Label(frame_pribadi, text='Tanggal Lahir *').grid(row=3, column=0, sticky='w', padx=3, pady=2)
entry_tanggal_lahir = DateEntry(
    frame_pribadi,
    width=entry_width-2,
    date_pattern='dd/mm/yyyy',
    year=2024,
    locale='id_ID'
)
entry_tanggal_lahir.grid(row=3, column=1, padx=3, pady=2)

tk.Label(frame_pribadi, text='4. Alamat Sesuai Identitas *').grid(row=4, column=0, sticky='w', padx=3, pady=2)
entry_alamat_identitas = tk.Entry(frame_pribadi, width=entry_width)
entry_alamat_identitas.grid(row=4, column=1, padx=3, pady=2)
set_placeholder(entry_alamat_identitas, "Masukkan alamat sesuai identitas")

tk.Label(frame_pribadi, text='Provinsi Identitas*').grid(row=5, column=0, sticky='w', padx=3, pady=2)
combo_provinsi_identitas = tk.ttk.Combobox(frame_pribadi, width=entry_width-2)
combo_provinsi_identitas['values'] = list(locations.keys())
combo_provinsi_identitas.grid(row=5, column=1, padx=3, pady=2)
combo_provinsi_identitas.bind("<<ComboboxSelected>>", update_kota)

tk.Label(frame_pribadi, text='Kota/Kabupaten Identitas*').grid(row=6, column=0, sticky='w', padx=3, pady=2)
combo_kota_identitas = tk.ttk.Combobox(frame_pribadi, width=entry_width-2)
combo_kota_identitas.grid(row=6, column=1, padx=3, pady=2)

tk.Label(frame_pribadi, text='5. Alamat Saat Ini *').grid(row=7, column=0, sticky='w', padx=3, pady=2)
entry_alamat_saat_ini = tk.Entry(frame_pribadi, width=entry_width)
entry_alamat_saat_ini.grid(row=7, column=1, padx=3, pady=2)
set_placeholder(entry_alamat_saat_ini, "Masukkan alamat saat ini")

tk.Label(frame_pribadi, text='Provinsi Saat Ini*').grid(row=8, column=0, sticky='w', padx=3, pady=2)
combo_provinsi_saat_ini = tk.ttk.Combobox(frame_pribadi, width=entry_width-2)
combo_provinsi_saat_ini['values'] = list(locations.keys())
combo_provinsi_saat_ini.grid(row=8, column=1, padx=3, pady=2)
combo_provinsi_saat_ini.bind("<<ComboboxSelected>>", update_kota)

tk.Label(frame_pribadi, text='Kota/Kabupaten Saat Ini*').grid(row=9, column=0, sticky='w', padx=3, pady=2)
combo_kota_saat_ini = tk.ttk.Combobox(frame_pribadi, width=entry_width-2)
combo_kota_saat_ini.grid(row=9, column=1, padx=3, pady=2)

# Checkbox for same address option
same_address_var = tk.BooleanVar()
same_address_checkbox = tk.Checkbutton(
    frame_pribadi,
    text="Cekbox jika alamat saat ini sama dengan alamat sesuai identitas",
    variable=same_address_var,
    command=lambda: copy_address_if_same()  # Call the function without parameters
)
same_address_checkbox.grid(row=10, columnspan=2, padx=3, pady=2)

tk.Label(frame_pribadi, text='6. Jenis Anggota *').grid(row=11, column=0, sticky='w', padx=3, pady=2)
combo_jenis_anggota = tk.ttk.Combobox(frame_pribadi, width=entry_width-2)
combo_jenis_anggota['values'] = ["Pelajar", "Mahasiswa", "Umum", "Karyawan"]
combo_jenis_anggota.grid(row=11, column=1, padx=3, pady=2)

tk.Label(frame_pribadi, text='7. Pendidikan Terakhir *').grid(row=12, column=0, sticky='w', padx=3, pady=2)
combo_pendidikan = tk.ttk.Combobox(frame_pribadi, width=entry_width-2)
combo_pendidikan['values'] = ["SD", "SMP", "SMA", "Diploma", "Sarjana"]
combo_pendidikan.grid(row=12, column=1, padx=3, pady=2)

tk.Label(frame_pribadi, text='8. Jenis Kelamin *').grid(row=13, column=0, sticky='w', padx=3, pady=2)
combo_jenis_kelamin = tk.ttk.Combobox(frame_pribadi, width=entry_width-2)
combo_jenis_kelamin['values'] = ["Laki-Laki", "Perempuan"]
combo_jenis_kelamin.grid(row=13, column=1, padx=3, pady=2)

tk.Label(frame_pribadi, text='9. Pekerjaan *').grid(row=14, column=0, sticky='w', padx=3, pady=2)
combo_pekerjaan = tk.ttk.Combobox(frame_pribadi, width=entry_width-2)
combo_pekerjaan['values'] = ["Guru", "TNI", "Karyawan", "Wirasuasta", "Pelajar"]
combo_pekerjaan.grid(row=14, column=1, padx=3, pady=2)

tk.Label(frame_pribadi, text='Password *').grid(row=15, column=0, sticky='w', padx=3, pady=2)
entry_password = tk.Entry(frame_pribadi, width=entry_width)
entry_password.grid(row=15, column=1, padx=3, pady=2)
set_placeholder(entry_password, "Masukkan password")

tk.Label(frame_pribadi, text='Nomor HP *').grid(row=16, column=0, sticky='w', padx=3, pady=2)
entry_nomor_hp = tk.Entry(frame_pribadi, width=entry_width)
entry_nomor_hp.grid(row=16, column=1, padx=3, pady=2)
set_placeholder(entry_nomor_hp, "Masukkan nomor HP")

tk.Label(frame_pribadi, text='Alamat Email *').grid(row=17, column=0, sticky='w', padx=3, pady=2)
entry_email = tk.Entry(frame_pribadi, width=entry_width)
entry_email.grid(row=17, column=1, padx=3, pady=2)
set_placeholder(entry_email, "Masukkan alamat email")

tk.Label(frame_pribadi, text='Nama Institut *').grid(row=18, column=0, sticky='w', padx=3, pady=2)
entry_nama_institut = tk.Entry(frame_pribadi, width=entry_width)
entry_nama_institut.grid(row=18, column=1, padx=3, pady=2)
set_placeholder(entry_nama_institut, "Masukkan nama institut")

tk.Label(frame_pribadi, text='Alamat Institut *').grid(row=19, column=0, sticky='w', padx=3, pady=2)
entry_alamat_institut = tk.Entry(frame_pribadi, width=entry_width)
entry_alamat_institut.grid(row=19, column=1, padx=3, pady=2)
set_placeholder(entry_alamat_institut, "Masukkan alamat institut")

entries.extend([
    entry_nama,
    entry_nomor_identitas,
    entry_tempat_lahir,
    entry_tanggal_lahir,
    entry_alamat_identitas,
    combo_provinsi_identitas,
    combo_kota_identitas,
    entry_alamat_saat_ini,
    combo_provinsi_saat_ini,
    combo_kota_saat_ini,
    combo_jenis_anggota,
    combo_pendidikan,
    combo_jenis_kelamin,
    combo_pekerjaan,
    entry_password,
    entry_nomor_hp,
    entry_email,
    entry_nama_institut,
    entry_alamat_institut,
])

check_var = tk.BooleanVar()
check_box = tk.Checkbutton(root, text='Saya setuju untuk menaati peraturan.', variable=check_var)
check_box.pack()

submit_button = tk.Button(
    root, 
    text='Simpan Data', 
    command=submit_data,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief=tk.RAISED,
    padx=20,
    pady=10
)
submit_button.pack(pady=(10))

# Tambahkan placeholder text untuk combobox
combo_provinsi_identitas.set("Pilih Provinsi")
combo_kota_identitas.set("Pilih Kota/Kabupaten")
combo_provinsi_saat_ini.set("Pilih Provinsi")
combo_kota_saat_ini.set("Pilih Kota/Kabupaten")
combo_jenis_anggota.set("Pilih Jenis Anggota")
combo_pendidikan.set("Pilih Pendidikan")
combo_jenis_kelamin.set("Pilih Jenis Kelamin")
combo_pekerjaan.set("Pilih Pekerjaan")

root.mainloop()