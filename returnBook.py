import tkinter as tk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os

# Firebase Initialization
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://perpustakaan-859b4-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

def set_placeholder(entry, placeholder):
    if isinstance(entry, tk.Entry):
        # Simpan placeholder dan status sebagai atribut entry
        entry._placeholder = placeholder
        entry._is_placeholder_visible = True  # Ganti nama atribut
        
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        entry.config(fg='gray')
        
        def on_focus_in(event):
            if entry._is_placeholder_visible:  # Gunakan atribut baru
                entry.delete(0, tk.END)
                entry.config(fg='black')
                entry._is_placeholder_visible = False
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, entry._placeholder)
                entry.config(fg='gray')
                entry._is_placeholder_visible = True
        
        def on_change(*args):
            if entry._is_placeholder_visible:  # Gunakan atribut baru
                entry.delete(0, tk.END)
                entry.config(fg='black')
                entry._is_placeholder_visible = False
        
        # Bind events
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        entry.bind('<Key>', on_change)

def check_book():
    book_code = entry_book_code.get()
    # Cek apakah input adalah placeholder atau kosong
    if (hasattr(entry_book_code, '_is_placeholder_visible') and 
        entry_book_code._is_placeholder_visible) or not book_code.strip():
        messagebox.showerror("Error", "Silakan masukkan Kode Buku")
        return

    try:
        ref_peminjaman = db.reference('peminjaman')
        ref_books = db.reference('books')
        
        # Ambil data buku
        books = ref_books.get()
        book_data = None
        for book in books.values():
            if book.get('kode_unik') == book_code:
                book_data = book
                break
        
        if not book_data:
            messagebox.showerror("Error", "Buku tidak ditemukan")
            clear_fields()
            return

        # Cari peminjaman aktif
        peminjaman = ref_peminjaman.get()
        active_loan = None
        loan_key = None
        
        for key, loan in peminjaman.items():
            if (loan.get('kode_buku') == book_code and 
                loan.get('status') == "Dipinjam"):
                active_loan = loan
                loan_key = key
                break
        
        if active_loan:
            # Update labels dengan informasi peminjaman
            label_book_title_value.config(text=book_data.get('judul', 'N/A'))
            label_borrower_value.config(text=active_loan.get('nama_peminjam', 'N/A'))
            label_borrow_date_value.config(text=active_loan.get('tanggal_pinjam', 'N/A'))
            label_return_date_value.config(text=active_loan.get('tanggal_kembali', 'N/A'))
            
            # Tambahkan tanggal pengembalian aktual (hari ini)
            label_actual_return_value.config(text=datetime.now().strftime("%Y-%m-%d"))
            
            # Hitung keterlambatan
            tanggal_kembali = datetime.strptime(active_loan.get('tanggal_kembali'), "%Y-%m-%d")
            tanggal_aktual = datetime.now()
            selisih = tanggal_aktual - tanggal_kembali
            
            if selisih.days > 0:
                label_late_value.config(text=f"Terlambat {selisih.days} hari", fg="red")
            else:
                label_late_value.config(text="Tepat waktu", fg="green")
            
            # Simpan loan_key sebagai atribut root window
            root.current_loan_key = loan_key
        else:
            messagebox.showinfo("Info", "Tidak ada peminjaman aktif untuk buku ini")
            clear_fields()
            
    except Exception as e:
        messagebox.showerror("Error", str(e))
        clear_fields()

def send_return_notification(peminjam_email, notification_html):
    try:
        if not peminjam_email:
            raise ValueError("Email peminjam tidak tersedia")
            
        sender_email = "aspiraass@gmail.com"
        app_password = "cybh reuw atfc mome"

        # Setup email
        message = MIMEMultipart('related')
        message['Subject'] = "Notifikasi Pengembalian Buku - Perpustakaan UBSI"
        message['From'] = sender_email
        message['To'] = peminjam_email

        # Buat bagian HTML
        msg_alternative = MIMEMultipart('alternative')
        message.attach(msg_alternative)

        # Lampirkan HTML
        msg_html = MIMEText(notification_html, 'html')
        msg_alternative.attach(msg_html)

        # Tambahkan logo
        try:
            with open('Image/logo.jpg', 'rb') as logo_file:
                msg_image = MIMEImage(logo_file.read())
                msg_image.add_header('Content-ID', '<logo>')
                message.attach(msg_image)
        except Exception as e:
            print(f"Error menambahkan logo: {e}")

        # Kirim email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(message)
            
        return True, "Email berhasil dikirim"
        
    except ValueError as e:
        return False, str(e)
    except smtplib.SMTPAuthenticationError:
        return False, "Gagal autentikasi email pengirim"
    except Exception as e:
        return False, f"Gagal mengirim email: {str(e)}"

def return_book():
    if not hasattr(root, 'current_loan_key'):
        messagebox.showerror("Error", "Silakan cek buku terlebih dahulu")
        return
        
    try:
        ref_peminjaman = db.reference(f'peminjaman/{root.current_loan_key}')
        tanggal_pengembalian = datetime.now().strftime("%Y-%m-%d")
        
        # Ambil data peminjaman
        peminjaman_data = ref_peminjaman.get()
        peminjam_email = peminjaman_data.get('email_peminjam')
        
        # Update status peminjaman
        ref_peminjaman.update({
            'status': 'Dikembalikan',
            'tanggal_pengembalian': tanggal_pengembalian
        })
        
        # Hitung keterlambatan
        tanggal_kembali = datetime.strptime(peminjaman_data.get('tanggal_kembali'), "%Y-%m-%d")
        tanggal_aktual = datetime.now()
        selisih = tanggal_aktual - tanggal_kembali
        
        status_text = f"Terlambat {selisih.days} hari" if selisih.days > 0 else "Tepat Waktu"
        status_color = "#dc3545" if selisih.days > 0 else "#28a745"
        
        # Template email yang disesuaikan
        notification_html = f"""
        <div style="background-color: #ffffff; padding: 20px; font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
              
              <div style="text-align: center; margin-bottom: 20px;">
                  <img src="cid:logo" alt="Logo Perpustakaan UBSI" style="width: 100%; max-width: 150px; height: auto;" />
              </div>

              <div style="border-top: 2px solid #BA68C8; margin: 20px 0;"></div>

              <h2 style="text-align: center; color: #333; font-size: 24px;">Notifikasi Pengembalian Buku</h2>
              
              <div style="text-align: left; margin: 20px 0;">
                  <p style="font-size: 16px; color: #333;">Halo {peminjaman_data.get('nama_peminjam')},</p>
                  <p style="font-size: 16px; color: #333;">Berikut adalah detail pengembalian buku Anda:</p>
                  
                  <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                      <h3 style="color: #BA68C8; margin-bottom: 10px;">Detail Pengembalian:</h3>
                      <p style="margin: 5px 0;"><strong>Judul Buku:</strong> {label_book_title_value.cget('text')}</p>
                      <p style="margin: 5px 0;"><strong>Tanggal Peminjaman:</strong> {peminjaman_data.get('tanggal_pinjam')}</p>
                      <p style="margin: 5px 0;"><strong>Tanggal Kembali Seharusnya:</strong> {peminjaman_data.get('tanggal_kembali')}</p>
                      <p style="margin: 5px 0;"><strong>Tanggal Pengembalian Aktual:</strong> {tanggal_pengembalian}</p>
                      <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: {status_color};">{status_text}</span></p>
                  </div>
                  
                  <p style="font-size: 16px; color: #333;">{
                    'Mohon untuk lebih tepat waktu dalam pengembalian buku selanjutnya.' 
                    if selisih.days > 0 
                    else 'Terima kasih telah mengembalikan buku tepat waktu!'
                  }</p>
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
        
        # Kirim email notifikasi
        success, message = send_return_notification(peminjam_email, notification_html)
        
        if success:
            messagebox.showinfo(
                "Sukses", 
                "Buku berhasil dikembalikan dan notifikasi telah dikirim ke email peminjam!"
            )
        else:
            messagebox.showwarning(
                "Peringatan", 
                f"Buku berhasil dikembalikan tetapi gagal mengirim notifikasi email.\nDetail: {message}"
            )
        
        clear_fields()
        
    except Exception as e:
        messagebox.showerror("Error", f"Gagal mengembalikan buku: {str(e)}")

def clear_fields():
    # Reset entry field
    entry_book_code.delete(0, tk.END)
    entry_book_code.insert(0, entry_book_code._placeholder)
    entry_book_code.config(fg='gray')
    entry_book_code._is_placeholder_visible = True  # Gunakan atribut baru
    
    # Reset labels
    label_book_title_value.config(text="-")
    label_borrower_value.config(text="-")
    label_borrow_date_value.config(text="-")
    label_return_date_value.config(text="-")
    label_actual_return_value.config(text="-")
    label_late_value.config(text="-", fg="black")
    
    if hasattr(root, 'current_loan_key'):
        del root.current_loan_key

# Creating GUI with Tkinter
root = tk.Tk()
root.title("Pengembalian Buku")
root.geometry("400x500")
root.configure(bg="#f0f0f0")

# Book Frame
frame_book = tk.LabelFrame(root, text="Data Pengembalian", padx=10, pady=10, bg="#ffffff")
frame_book.pack(padx=10, pady=10, fill="both")

# Book Code input
tk.Label(frame_book, text='Kode Buku *', bg="#ffffff").pack(pady=5)
entry_book_code = tk.Entry(frame_book, width=30)
entry_book_code.pack(pady=5)
set_placeholder(entry_book_code, "Masukkan Kode Buku")

# Check Book Button
check_button = tk.Button(
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
check_button.pack(pady=10)

# Book Details
tk.Label(frame_book, text='Judul Buku:', bg="#ffffff").pack()
label_book_title_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_book_title_value.pack()

tk.Label(frame_book, text='Nama Peminjam:', bg="#ffffff").pack()
label_borrower_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_borrower_value.pack()

tk.Label(frame_book, text='Tanggal Pinjam:', bg="#ffffff").pack()
label_borrow_date_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_borrow_date_value.pack()

tk.Label(frame_book, text='Tanggal Kembali:', bg="#ffffff").pack()
label_return_date_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_return_date_value.pack()

tk.Label(frame_book, text='Tanggal Pengembalian Aktual:', bg="#ffffff").pack()
label_actual_return_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_actual_return_value.pack()

tk.Label(frame_book, text='Status Keterlambatan:', bg="#ffffff").pack()
label_late_value = tk.Label(frame_book, text="-", bg="#ffffff", font=("Arial", 10, "bold"))
label_late_value.pack()

# Return Button
return_button = tk.Button(
    root, 
    text='Proses Pengembalian', 
    command=return_book,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief=tk.RAISED,
    padx=20,
    pady=10
)
return_button.pack(pady=20)

root.mainloop() 