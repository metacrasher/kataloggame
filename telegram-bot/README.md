# FadStore Telegram Admin Bot

Bot ini mengelola tabel Supabase yang sama dengan dashboard FadStore: `products`, `orders`, dan `store_settings`.

## Deploy sebagai worker
1. Buat bot melalui Telegram `@BotFather` dengan perintah `/newbot`; simpan token secara rahasia.
2. Ambil Telegram numeric user ID dari `@userinfobot`.
3. Di Railway buat **New Project → Deploy from GitHub Repo** dan pilih `metacrasher/kataloggame`.
4. Atur **Root Directory** menjadi `/telegram-bot`. Build/install menggunakan `pip install -r requirements.txt`; Start Command: `python main.py`.
5. Tambahkan Variables berikut pada service:
   - `BOT_TOKEN` = token dari BotFather
   - `ADMIN_TELEGRAM_ID` = numeric Telegram user ID milik admin
   - `SUPABASE_URL` = Project URL Supabase
   - `SUPABASE_SERVICE_ROLE_KEY` = secret/service_role key Supabase (JANGAN pernah taruh di GitHub atau kirim ke chat)
   - `SUPABASE_STORAGE_BUCKET` = `product-images`
6. Jalankan SQL dari `supabase-storage-setup.sql` pada Supabase SQL Editor.
7. Pastikan hanya satu instance bot yang berjalan untuk token tersebut. Tes dengan membuka bot dan mengirim `/start`.

## Menu
- Tambah stok dengan foto, harga, game, rank, level, dan keterangan.
- Lihat 30 stok terbaru.
- Edit nama, harga, rank, level, keterangan, dan foto.
- Hapus stok.
- Ubah status READY/SOLD.
- Lihat ringkasan, pesanan, dan pengaturan toko.

Bot menggunakan service role hanya pada server worker, bukan browser. Jangan pernah memasukkan key tersebut ke `config.js`, HTML, atau JavaScript frontend.
