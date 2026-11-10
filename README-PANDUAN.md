# FadStore Admin Dashboard

Panel admin untuk mengelola katalog Free Fire, Mobile Legends, Roblox, stok, pengaturan toko, dan riwayat pesanan manual. Login menggunakan email + password melalui Supabase Auth.

## Penting: setup pertama kali

Website ini adalah frontend statis. Agar login dan penyimpanan data benar-benar bekerja, hubungkan ke project Supabase milik Anda. Saya tidak bisa membuat project atau akun Supabase atas nama Anda tanpa akses akun Anda.

### 1. Buat project Supabase
1. Buka https://supabase.com/ lalu login/daftar.
2. Buat project baru bernama `fadstore`.
3. Simpan database password di tempat aman (tidak perlu dikirim ke saya).
4. Setelah project siap, buka **Project Settings → API** (atau **Connect**) dan salin **Project URL** serta **publishable/anon key**.

### 2. Buat tabel database
1. Di Supabase, buka **SQL Editor → New query**.
2. Buka file `supabase-schema.sql` dari folder ini.
3. Salin seluruh isinya ke SQL Editor dan tekan **Run**.

### 3. Buat email admin
1. Buka **Authentication → Users → Add user**.
2. Masukkan email yang ingin dipakai untuk login dan buat password yang kuat.
3. Konfirmasi/create user sesuai opsi yang tampil.
4. Untuk keamanan, jangan aktifkan public sign-ups. Buat user admin sendiri dari dashboard Supabase.
5. Saat ini kebijakan database memberi akses kepada user yang sudah terautentikasi. Jangan bagikan kredensial admin kepada orang lain.

### 4. Hubungkan frontend
1. Buka file `config.js`.
2. Isi nilai berikut:
```js
window.FADSTORE_CONFIG = {
  SUPABASE_URL: "https://PROJECT-REF.supabase.co",
  SUPABASE_ANON_KEY: "PUBLISHABLE_OR_ANON_KEY"
};
```
3. Simpan file. Key yang dipakai di browser harus publishable/anon key, BUKAN `service_role` atau secret key.

### 5. Jalankan / deploy
- Tes lokal: jalankan server statis lokal (misalnya VS Code Live Server), atau buka `index.html` jika browser mengizinkan resource CDN.
- Deploy gratis: upload semua file ke GitHub repository, lalu aktifkan **Settings → Pages → Deploy from a branch → main → /(root)**.
- Dashboard login: buka URL website. Login memakai email/password yang dibuat di Supabase.

## Pengelolaan
- **Produk & Stok**: tambah, edit, hapus, ubah harga, foto, spesifikasi, dan status tersedia/terjual.
- **Riwayat Pesanan**: catat pesanan manual yang masuk melalui WhatsApp; ubah status Menunggu/Diproses/Selesai/Dibatalkan.
- **Pengaturan Toko**: ubah nama toko dan kontak.

## Batasan yang perlu diketahui
1. Riwayat pesanan **tidak otomatis ditarik dari WhatsApp**. Admin perlu mencatatnya sendiri di dashboard. Integrasi otomatis memerlukan WhatsApp Business Platform/API dan konfigurasi tambahan.
2. File ini adalah **dashboard admin**. Katalog publik pelanggan perlu dihubungkan ke tabel `products` agar perubahan admin langsung tampil di halaman toko publik. Keduanya bisa di-host di GitHub Pages yang sama, tetapi halaman publik dan dashboard perlu dibuat sebagai bagian frontend terpisah.
3. Foto produk pada versi ini menggunakan URL gambar langsung, bukan upload file ke storage. Upload foto langsung bisa ditambahkan dengan Supabase Storage.
4. Setup SQL saat ini memberi hak CRUD kepada seluruh user terautentikasi. Karena hanya admin yang boleh dibuat, nonaktifkan pendaftaran publik dan jangan membuat user lain. Untuk toko multi-admin, ganti kebijakan dengan pembatasan role/admin yang lebih ketat.
5. Jangan masukkan password akun game, OTP, email pemulihan, atau data rahasia ke catatan pesanan.
6. Pastikan penjualan/pengalihan akun sesuai aturan dari masing-masing game.

## Kontak awal
- WhatsApp admin: 085273114090 (format link internasional: 6285273114090)
- Telegram: @fadstore
