# Fstore Game Marketplace

Starter website jual beli akun game dengan tampilan Dark Gaming Merah dan integrasi awal Midtrans Snap.

## Menjalankan di Windows
1. Instal Node.js LTS (disarankan Node.js 22 LTS).
2. Ekstrak ZIP ini.
3. Buka folder `fstore-game-marketplace`.
4. Klik alamat folder di File Explorer, ketik `cmd`, tekan Enter.
5. Jalankan `npm install`.
6. Salin `.env.example` menjadi `.env`.
7. Jalankan `npm run dev`.
8. Buka http://localhost:3000.

## Pengaturan Midtrans
Daftar dan selesaikan verifikasi merchant. Masukkan Server Key dan Client Key Sandbox ke `.env`; jangan bagikan Server Key. Gunakan `MIDTRANS_IS_PRODUCTION=false` untuk Sandbox. Atur Payment Notification URL menjadi `https://DOMAIN/api/midtrans/notification` setelah website memiliki domain HTTPS. Checkout sengaja nonaktif: jangan ubah `ENABLE_CHECKOUT=true` sebelum kredensial dan pengujian Sandbox benar-benar selesai.

## Katalog
Produk contoh ada di `data/products.json`. Ganti dengan data akun yang benar-benar dimiliki/diizinkan untuk dijual.

## Catatan keamanan
Ini starter pengembangan, belum siap produksi. Penyimpanan JSON hanya untuk uji lokal. Sebelum menerima pembayaran sungguhan, tambahkan database produksi, login admin aman, proteksi brute-force/CSRF, audit log, backup, pemantauan, dan alur penyerahan akun setelah pembayaran terverifikasi. Jangan simpan password akun game atau email pemulihan di katalog. Periksa juga aturan game terkait jual beli akun.
