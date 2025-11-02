Sistem Perpustakaan UBSI

Sistem manajemen perpustakaan berbasis Python dengan GUI Tkinter dan Firebase Realtime Database.

# Fitur Utama

## 1. Peminjaman Buku
- Verifikasi anggota perpustakaan
- Pengecekan status peminjaman (maksimal 3 buku)
- Pengecekan blacklist
- Notifikasi email otomatis
- Riwayat peminjaman

## 2. Pengembalian Buku
- Verifikasi kode buku
- Perhitungan keterlambatan
- Status pengembalian
- Update database otomatis

## 3. Pencarian Buku
- Pencarian berdasarkan judul
- Informasi ketersediaan buku
- Detail buku lengkap

## Persyaratan Sistem

## Dependencies
```bash
pip install -r requirements.txt
```

## Konfigurasi Firebase
1. Buat proyek di Firebase Console
2. Download firebase-key.json
3. Update DatabaseURL di kode

## Struktur Kode

### 1. borrowBook.py
```python
# Fitur utama:
- Peminjaman buku
- Validasi anggota
- Notifikasi email
- Riwayat peminjaman
```

### 2. returnBook.py
```python
# Fitur utama:
- Pengembalian buku
- Perhitungan keterlambatan
- Update status peminjaman
```

### 3. searchBook.py
```python
# Fitur utama:
- Pencarian buku
- Tampilan detail buku
- Status ketersediaan
```

## Struktur Database Firebase

### 1. Koleksi 'books'
```json
{
  "kode_unik": "string",
  "judul": "string",
  "penulis": "string",
  "tahun_terbit": "string",
  "genre": "string",
  "deskripsi": "string"
}
```

### 2. Koleksi 'anggota_perpus'
```json
{
  "id_anggota": "string",
  "nama_lengkap": "string",
  "email": "string",
  "jenis_anggota": "string"
}
```

### 3. Koleksi 'peminjaman'
```json
{
  "id_anggota": "string",
  "kode_buku": "string",
  "tanggal_pinjam": "date",
  "tanggal_kembali": "date",
  "status": "string",
  "tanggal_pengembalian": "date",
  "keterlambatan": "number"
}
```

## Aturan Bisnis

1. **Peminjaman**
   - Maksimal 3 buku per anggota
   - Durasi peminjaman 14 hari
   - Blacklist jika terlambat > 1 tahun

2. **Pengembalian**
   - Hitung keterlambatan otomatis
   - Update status buku
   - Catat tanggal pengembalian aktual

3. **Pencarian**
   - Pencarian case-insensitive
   - Tampilkan status ketersediaan
   - Filter berdasarkan judul

## Penggunaan

1. **Peminjaman Buku**
   ```bash
   python borrowBook.py
   ```
   - Masukkan ID Anggota
   - Pilih buku
   - Konfirmasi peminjaman

2. **Pengembalian Buku**
   ```bash
   python returnBook.py
   ```
   - Masukkan kode buku
   - Konfirmasi pengembalian

3. **Pencarian Buku**
   ```bash
   python searchBook.py
   ```
   - Masukkan judul buku
   - Lihat detail dan ketersediaan

## Keamanan

1. **Firebase**
   - Gunakan firebase-key.json
   - Jangan share kredensial

2. **Email**
   - Gunakan App Password Gmail
   - Enkripsi password

## Pengembangan Selanjutnya

1. Tambah fitur denda
2. Sistem reservasi buku
3. Laporan statistik
4. Dashboard admin
5. Manajemen kategori buku

## Kontribusi

Silakan berkontribusi dengan:
1. Fork repository
2. Buat branch fitur
3. Submit pull request

## Lisensi

MIT License - Bebas digunakan dan dimodifikasi

## Kontak

Email: [aspiraass@gmail.com](mailto:aspiraass@gmail.com)