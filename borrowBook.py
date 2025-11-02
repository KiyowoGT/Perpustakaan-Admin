import tkinter as tk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Firebase Initialization
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "Your URL"
})

def set_placeholder(entry, placeholder):
    if isinstance(entry, tk.Entry):  
        entry.delete(0, tk.END)  
        entry.insert(0, placeholder)
        entry.config(fg='gray')
        
        def on_focus_in(event):
            if entry.get() == placeholder and entry.cget('fg') == 'gray':
                entry.delete(0, tk.END)
                entry.config(fg='black')
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg='gray')
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

def fetch_member_data(member_id):
    try:
        ref = db.reference('anggota_perpus')
        all_members = ref.get()

        if all_members:
            for key, value in all_members.items():
                if value.get('id_anggota') == member_id:
                    return value
        return None
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

def fetch_book_data(book_code):
    try:
        ref = db.reference('books')
        all_books = ref.get()

        if all_books:
            for key, value in all_books.items():
                if value.get('kode_unik') == book_code:
                    return value
        return None
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

def check_member_status(member_id):
    try:
        ref_peminjaman = db.reference('peminjaman')
        all_peminjaman = ref_peminjaman.get() or {}
        
        active_loans = []
        blacklisted = False
        
        for loan in all_peminjaman.values():
            if loan.get('id_anggota') == member_id:
                # Cek status peminjaman
                if loan.get('status') == "Dipinjam":
                    active_loans.append(loan)
                
                # Cek keterlambatan untuk blacklist
                if loan.get('status') == "Dikembalikan":
                    tanggal_kembali = datetime.strptime(loan.get('tanggal_kembali'), "%Y-%m-%d")
                    tanggal_pengembalian = datetime.strptime(loan.get('tanggal_pengembalian'), "%Y-%m-%d")
                    
                    # Hitung selisih hari
                    selisih = tanggal_pengembalian - tanggal_kembali
                    if selisih.days > 365:  # Jika telat lebih dari 1 tahun
                        blacklisted = True
                        break
        
        return {
            'active_loans': active_loans,
            'blacklisted': blacklisted,
            'can_borrow': len(active_loans) < 3 and not blacklisted
        }
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

def display_loan_history(member_id):
    history_window = tk.Toplevel(root)
    history_window.title("Riwayat Peminjaman")
    history_window.geometry("600x400")
    
    # Create Text widget with scrollbar
    text_widget = tk.Text(history_window, wrap=tk.WORD, padx=10, pady=10)
    scrollbar = tk.Scrollbar(history_window, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    try:
        ref_peminjaman = db.reference('peminjaman')
        all_peminjaman = ref_peminjaman.get() or {}
        
        history_text = "Riwayat Peminjaman:\n\n"
        for loan in all_peminjaman.values():
            if loan.get('id_anggota') == member_id:
                status = loan.get('status', 'N/A')
                keterlambatan = ""
                tanggal_pengembalian_info = ""
                
                if status == "Dikembalikan":
                    tanggal_kembali = datetime.strptime(loan.get('tanggal_kembali'), "%Y-%m-%d")
                    tanggal_pengembalian = datetime.strptime(loan.get('tanggal_pengembalian'), "%Y-%m-%d")
                    selisih = tanggal_pengembalian - tanggal_kembali
                    
                    tanggal_pengembalian_info = f"\nTanggal Pengembalian Aktual: {loan.get('tanggal_pengembalian')}"
                    
                    if selisih.days > 0:
                        keterlambatan = f"\nKeterlambatan: {selisih.days} hari"
                        status_keterlambatan = "Terlambat"
                    else:
                        status_keterlambatan = "Tepat Waktu"
                
                history_text += f"""
Judul: {loan.get('judul_buku', 'N/A')}
Tanggal Pinjam: {loan.get('tanggal_pinjam', 'N/A')}
Tanggal Kembali Seharusnya: {loan.get('tanggal_kembali', 'N/A')}{tanggal_pengembalian_info}
Status: {status}
{f'Status Keterlambatan: {status_keterlambatan}' if status == 'Dikembalikan' else ''}{keterlambatan}
{'='*50}
"""
        
        text_widget.insert(tk.END, history_text)
        text_widget.configure(state='disabled')
    except Exception as e:
        messagebox.showerror("Error", str(e))

def check_member():
    member_id = entry_member_id.get()
    if member_id == "Masukkan ID Anggota" or not member_id.strip():
        messagebox.showerror("Error", "Silakan masukkan ID Anggota")
        return
    
    member_data = fetch_member_data(member_id)
    if member_data:
        # Cek status peminjaman
        status = check_member_status(member_id)
        if status:
            if status['blacklisted']:
                messagebox.showerror("Error", "Anggota masuk daftar hitam karena keterlambatan lebih dari 1 tahun")
                return
            
            if not status['can_borrow']:
                messagebox.showerror("Error", "Anggota sudah meminjam 3 buku")
                display_loan_history(member_id)
                return
            
            # Update labels
            label_member_name_value.config(text=member_data.get('nama_lengkap', 'N/A'))
            label_member_type_value.config(text=member_data.get('jenis_anggota', 'N/A'))
            label_member_email_value.config(text=member_data.get('email', 'N/A'))
            
            # Tampilkan riwayat peminjaman
            display_loan_history(member_id)
    else:
        messagebox.showinfo("Info", "Data anggota tidak ditemukan")
        label_member_name_value.config(text="-")
        label_member_type_value.config(text="-")
        label_member_email_value.config(text="-")

def check_book():
    book_code = entry_book_code.get()
    if book_code == "Masukkan Kode Buku" or not book_code.strip():
        messagebox.showerror("Error", "Silakan masukkan Kode Buku")
        return
    
    book_data = fetch_book_data(book_code)
    if book_data:
        label_book_title_value.config(text=book_data.get('judul', 'N/A'))
        label_book_author_value.config(text=book_data.get('penulis', 'N/A'))
        label_book_year_value.config(text=book_data.get('tahun_terbit', 'N/A'))
    else:
        messagebox.showinfo("Info", "Data buku tidak ditemukan")
        label_book_title_value.config(text="-")
        label_book_author_value.config(text="-")
        label_book_year_value.config(text="-")

# Fungsi untuk mengirim email notifikasi
def send_email_notification(member_email, member_name, book_title, borrow_date, return_date):
    sender_email = 'aspiraass@gmail.com'
    app_password = 'cybh reuw atfc mome'
    receiver_email = member_email

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Notifikasi Peminjaman Buku - Perpustakaan UBSI'

    # Body HTML dengan format yang sama seperti registrasi
    body_html = f"""
    <div style="background-color: #ffffff; padding: 20px; font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
          
          <div style="text-align: center; margin-bottom: 20px;">
              <img src="cid:logo" alt="Logo Perpustakaan UBSI" style="width: 100%; max-width: 150px; height: auto;" />
          </div>

          <div style="border-top: 2px solid #BA68C8; margin: 20px 0;"></div>

          <h2 style="text-align: center; color: #333; font-size: 24px;">Notifikasi Peminjaman Buku</h2>
          
          <div style="text-align: left; margin: 20px 0;">
              <p style="font-size: 16px; color: #333;">Halo {member_name},</p>
              <p style="font-size: 16px; color: #333;">Anda telah berhasil meminjam buku dari Perpustakaan UBSI.</p>
              
              <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                  <h3 style="color: #BA68C8; margin-bottom: 10px;">Detail Peminjaman:</h3>
                  <p style="margin: 5px 0;"><strong>Judul Buku:</strong> {book_title}</p>
                  <p style="margin: 5px 0;"><strong>Tanggal Peminjaman:</strong> {borrow_date.strftime('%Y-%m-%d')}</p>
                  <p style="margin: 5px 0;"><strong>Tanggal Pengembalian:</strong> {return_date.strftime('%Y-%m-%d')}</p>
              </div>
              
              <p style="font-size: 16px; color: #333;">Harap mengembalikan buku tepat waktu sesuai dengan tanggal yang telah ditentukan.</p>
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
    
    msg.attach(MIMEText(body_html, 'html'))

    # Tambahkan logo
    with open('Image/logo.jpg', 'rb') as logo:
        logo_part = MIMEBase('application', 'octet-stream')
        logo_part.set_payload(logo.read())
        encoders.encode_base64(logo_part)
        logo_part.add_header('Content-Disposition', 'inline', filename='logo.jpg')
        logo_part.add_header('Content-ID', '<logo>')
        msg.attach(logo_part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        print("Email notifikasi berhasil dikirim.")
    except Exception as e:
        print(f"Gagal mengirim email: {str(e)}")

def submit_borrow():
    member_id = entry_member_id.get()
    book_code = entry_book_code.get()
    
    if (member_id == "Masukkan ID Anggota" or not member_id.strip() or
        book_code == "Masukkan Kode Buku" or not book_code.strip()):
        messagebox.showerror("Error", "Silakan lengkapi data peminjaman")
        return
    
    member_data = fetch_member_data(member_id)
    book_data = fetch_book_data(book_code)
    
    if not member_data or not book_data:
        messagebox.showerror("Error", "Data anggota atau buku tidak valid")
        return
    
    # Set tanggal peminjaman dan pengembalian
    borrow_date = datetime.now()
    return_date = borrow_date + timedelta(days=14)
    
    # Tambahkan email peminjam ke data peminjaman
    borrow_data = {
        "id_anggota": member_id,
        "nama_peminjam": member_data.get('nama_lengkap'),
        "email_peminjam": member_data.get('email'),  # Tambahkan email peminjam
        "kode_buku": book_code,
        "judul_buku": book_data.get('judul'),
        "tanggal_pinjam": borrow_date.strftime("%Y-%m-%d"),
        "tanggal_kembali": return_date.strftime("%Y-%m-%d"),
        "status": "Dipinjam"
    }
    
    try:
        ref = db.reference('peminjaman')
        ref.push(borrow_data)
        messagebox.showinfo("Sukses", 
            f"Peminjaman berhasil!\n\n"
            f"Tanggal Pinjam: {borrow_date.strftime('%Y-%m-%d')}\n"
            f"Tanggal Kembali: {return_date.strftime('%Y-%m-%d')}")
        
        # Kirim email notifikasi
        send_email_notification(
            member_email=member_data.get('email'),
            member_name=member_data.get('nama_lengkap'),
            book_title=book_data.get('judul'),
            borrow_date=borrow_date,
            return_date=return_date
        )
        
        clear_fields()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan data peminjaman: {str(e)}")

def clear_fields():
    # Reset entry fields
    set_placeholder(entry_member_id, "Masukkan ID Anggota")
    set_placeholder(entry_book_code, "Masukkan Kode Buku")
    
    # Reset labels
    label_member_name_value.config(text="-")
    label_member_type_value.config(text="-")
    label_member_email_value.config(text="-")
    label_book_title_value.config(text="-")
    label_book_author_value.config(text="-")
    label_book_year_value.config(text="-")

# Creating GUI with Tkinter
root = tk.Tk()
root.title("Peminjaman Buku")
root.geometry("400x600")
root.configure(bg="#f0f0f0")

# Member Frame
frame_member = tk.LabelFrame(root, text="Data Anggota", padx=10, pady=10, bg="#ffffff")
frame_member.pack(padx=10, pady=10, fill="both")

# Member ID input
tk.Label(frame_member, text='ID Anggota *', bg="#ffffff").pack(pady=5)
entry_member_id = tk.Entry(frame_member, width=30)
entry_member_id.pack(pady=5)
set_placeholder(entry_member_id, "Masukkan ID Anggota")

# Check Member Button
check_member_button = tk.Button(
    frame_member,
    text='Cek Anggota',
    command=check_member,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 9),
    relief=tk.RAISED,
    padx=10,
    pady=5
)
check_member_button.pack(pady=5)

# Member Details
tk.Label(frame_member, text='Nama:', bg="#ffffff").pack()
label_member_name_value = tk.Label(frame_member, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_member_name_value.pack()

tk.Label(frame_member, text='Jenis Anggota:', bg="#ffffff").pack()
label_member_type_value = tk.Label(frame_member, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_member_type_value.pack()

tk.Label(frame_member, text='Email:', bg="#ffffff").pack()
label_member_email_value = tk.Label(frame_member, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_member_email_value.pack()

# Book Frame
frame_book = tk.LabelFrame(root, text="Data Buku", padx=10, pady=10, bg="#ffffff")
frame_book.pack(padx=10, pady=10, fill="both")

# Book Code input
tk.Label(frame_book, text='Kode Buku *', bg="#ffffff").pack(pady=5)
entry_book_code = tk.Entry(frame_book, width=30)
entry_book_code.pack(pady=5)
set_placeholder(entry_book_code, "Masukkan Kode Buku")

# Check Book Button
check_book_button = tk.Button(
    frame_book,
    text='Cek Buku',
    command=check_book,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 9),
    relief=tk.RAISED,
    padx=10,
    pady=5
)
check_book_button.pack(pady=5)

# Book Details
tk.Label(frame_book, text='Judul:', bg="#ffffff").pack()
label_book_title_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_book_title_value.pack()

tk.Label(frame_book, text='Penulis:', bg="#ffffff").pack()
label_book_author_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_book_author_value.pack()

tk.Label(frame_book, text='Tahun Terbit:', bg="#ffffff").pack()
label_book_year_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_book_year_value.pack()

# Submit Button
submit_button = tk.Button(
    root, 
    text='Proses Peminjaman', 
    command=submit_borrow,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief=tk.RAISED,
    padx=20,
    pady=10
)
submit_button.pack(pady=20)

root.mainloop() 