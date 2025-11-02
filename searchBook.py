import tkinter as tk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, db

# Firebase Initialization
cred = credentials.Certificate("firebase-key.json")  # Change to your JSON key path
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://perpustakaan-859b4-default-rtdb.asia-southeast1.firebasedatabase.app/"
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

def fetch_books(search_term):
    try:
        ref = db.reference('books')
        ref_peminjaman = db.reference('peminjaman')
        all_books = ref.get()
        all_peminjaman = ref_peminjaman.get() or {}
        matching_books = []

        if all_books:
            search_terms = search_term.lower().split()
            for key, book in all_books.items():
                # Mengambil nilai yang akan dicari
                book_title = book.get('judul', '').lower()
                book_author = book.get('penulis', '').lower()
                book_year = str(book.get('tahun_terbit', '')).lower()
                
                # Cek apakah kata pencarian cocok dengan salah satu kriteria
                matches = False
                for term in search_terms:
                    if (term in book_title or 
                        term in book_author or 
                        term in book_year):
                        matches = True
                        break
                
                if matches:
                    # Hitung jumlah buku yang sedang dipinjam
                    borrowed_count = 0
                    for peminjaman in all_peminjaman.values():
                        if (peminjaman.get('kode_buku') == book.get('kode_unik') and 
                            peminjaman.get('status') == "Dipinjam"):
                            borrowed_count += 1
                    
                    # Hitung stok tersedia
                    total_stock = book.get('jumlah_buku', 0)
                    available_stock = total_stock - borrowed_count
                    book['stok_tersedia'] = available_stock
                    book['total_stok'] = total_stock
                    matching_books.append(book)
        
        return matching_books
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return []

def search_books():
    search_term = entry_search.get()
    if search_term == "Masukkan judul/penulis/tahun terbit" or not search_term.strip():
        messagebox.showerror("Error", "Silakan masukkan kata kunci pencarian.")
        return
    
    books = fetch_books(search_term)
    
    if books:
        display_books(books)
    else:
        messagebox.showinfo("Info", "Buku tidak ditemukan.")

def display_books(books):
    text_result.configure(state='normal')
    text_result.delete(1.0, tk.END)
    
    result_text = "Buku yang ditemukan:\n\n"
    for i, book in enumerate(books, 1):
        result_text += f"""
{i}. Judul: {book.get('judul', 'N/A')}
   Penulis: {book.get('penulis', 'N/A')}
   Tahun Terbit: {book.get('tahun_terbit', 'N/A')}
   Genre: {book.get('genre', 'N/A')}
   Deskripsi: {book.get('deskripsi', 'N/A')}
   Kode Buku: {book.get('kode_unik', 'N/A')}
   Tersedia: {book.get('stok_tersedia', 0)} dari {book.get('total_stok', 0)} buku
   {'='*50}
"""
    
    text_result.insert(tk.END, result_text)
    text_result.configure(state='disabled')

# Creating GUI with Tkinter
root = tk.Tk()
root.title("Pencarian Buku")
root.geometry("400x600")  # Memperbesar ukuran window
root.configure(bg="#f0f0f0")

# Frame untuk pencarian
frame_search = tk.LabelFrame(root, text="Pencarian", padx=10, pady=10, bg="#ffffff")
frame_search.pack(padx=10, pady=10, fill="x")

# Search Entry dan Button dalam frame_search
tk.Label(frame_search, text='Kata Kunci Pencarian *', bg="#ffffff").pack(pady=5)
entry_search = tk.Entry(frame_search, width=30)
entry_search.pack(pady=5)
set_placeholder(entry_search, "Masukkan judul/penulis/tahun terbit")

# Tambahkan label informasi
info_label = tk.Label(
    frame_search, 
    text="*Dapat mencari berdasarkan judul, penulis, atau tahun terbit",
    bg="#ffffff",
    fg="#666666",
    font=("Arial", 8, "italic")
)
info_label.pack(pady=(0, 5))

search_button = tk.Button(
    frame_search, 
    text='Cari Buku', 
    command=search_books,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief=tk.RAISED,
    padx=20,
    pady=5
)
search_button.pack(pady=10)

# Frame untuk hasil pencarian
frame_result = tk.LabelFrame(root, text="Hasil Pencarian", padx=10, pady=10, bg="#ffffff")
frame_result.pack(padx=10, pady=5, fill="both", expand=True)

# Text widget dengan scrollbar untuk hasil
text_result = tk.Text(frame_result, wrap=tk.WORD, padx=10, pady=10, height=20)
scrollbar = tk.Scrollbar(frame_result, command=text_result.yview)
text_result.configure(yscrollcommand=scrollbar.set)

# Pack widgets hasil
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop() 