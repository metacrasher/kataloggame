import logging, os, re, uuid
from io import BytesIO
from decimal import Decimal, InvalidOperation
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("fadstore-bot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_TELEGRAM_ID"])
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "product-images")
API = f"{SUPABASE_URL}/rest/v1"
HEADERS = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "application/json"}
GAMES = ["Free Fire", "Mobile Legends", "Roblox"]
STATES = {}

def is_admin(update):
    u = update.effective_user
    return bool(u and u.id == ADMIN_ID)

def db_get(table, params=None):
    r = requests.get(f"{API}/{table}", headers=HEADERS, params=params or {}, timeout=25)
    r.raise_for_status()
    return r.json()

def db_write(table, method, payload=None, params=None):
    h = dict(HEADERS); h["Prefer"] = "return=representation"
    r = requests.request(method, f"{API}/{table}", headers=h, params=params or {}, json=payload, timeout=25)
    r.raise_for_status()
    return r.json() if r.content else []

def money(n):
    return "Rp" + f"{int(n):,}".replace(",", ".")

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Tambah stok", callback_data="add"), InlineKeyboardButton("📦 Daftar stok", callback_data="list")],
        [InlineKeyboardButton("✏️ Edit stok", callback_data="editpick"), InlineKeyboardButton("🗑 Hapus stok", callback_data="delpick")],
        [InlineKeyboardButton("🔄 Status READY/SOLD", callback_data="statuspick"), InlineKeyboardButton("📊 Ringkasan", callback_data="stats")],
        [InlineKeyboardButton("🧾 Pesanan", callback_data="orders"), InlineKeyboardButton("⚙️ Pengaturan toko", callback_data="settings")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Akses ditolak. Bot ini khusus admin toko.")
        return
    await update.message.reply_text("🎮 *FadStore Admin Bot*\nPilih fitur pengelolaan toko:", parse_mode="Markdown", reply_markup=menu())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    STATES.pop(update.effective_user.id, None)
    await update.message.reply_text("Proses dibatalkan.", reply_markup=menu())

async def show_products(chat, mode="list"):
    rows = db_get("products", {"select":"id,game,name,price,stock,rank,level,image", "order":"created_at.desc", "limit":"30"})
    if not rows:
        await chat.reply_text("Belum ada stok.")
        return
    for p in rows:
        status = "🟢 READY" if p.get("stock") else "🔴 SOLD"
        caption = f"#{p['id']} · {p['game']}\n*{p['name']}*\nHarga: {money(p['price'])}\nStatus: {status}\nRank: {p.get('rank') or '-'} · Level: {p.get('level') or '-'}"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Pilih", callback_data=f"{mode}:{p['id']}")]]) if mode != "list" else None
        if p.get("image"):
            await chat.reply_photo(p["image"], caption=caption, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await chat.reply_text(caption, parse_mode="Markdown", reply_markup=keyboard)

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not is_admin(update):
        await q.edit_message_text("⛔ Akses ditolak.")
        return
    data = q.data
    if data == "home":
        await q.message.reply_text("Menu admin:", reply_markup=menu()); return
    if data == "list":
        await show_products(q.message); return
    if data == "add":
        STATES[ADMIN_ID] = {"action":"add","step":"game"}
        await q.message.reply_text("Pilih game:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(g, callback_data=f"game:{i}") for i,g in enumerate(GAMES)]] + [[InlineKeyboardButton("Batal", callback_data="cancel")]])); return
    if data.startswith("game:"):
        s = STATES.get(ADMIN_ID)
        if not s or s.get("action") != "add": return
        s["game"] = GAMES[int(data.split(":")[1])]
        s["step"] = "name"
        await q.message.reply_text("Kirim *nama akun*:", parse_mode="Markdown"); return
    if data in ("editpick","delpick","statuspick"):
        await show_products(q.message, {"editpick":"edit","delpick":"delete","statuspick":"status"}[data]); return
    if data.startswith(("delete:","status:","edit:")):
        action, pid = data.split(":")
        p = db_get("products", {"id":f"eq.{pid}","select":"*"})
        if not p: await q.message.reply_text("Produk tidak ditemukan."); return
        p = p[0]
        if action == "delete":
            db_write("products","DELETE",params={"id":f"eq.{pid}"})
            await q.message.reply_text(f"✅ Stok #{pid} berhasil dihapus."); return
        if action == "status":
            db_write("products","PATCH",{"stock":not bool(p["stock"])}, {"id":f"eq.{pid}"})
            await q.message.reply_text(f"✅ Status *{p['name']}* sekarang {'READY' if not p['stock'] else 'SOLD'}.",parse_mode="Markdown"); return
        STATES[ADMIN_ID] = {"action":"edit","step":"name","id":pid,"product":p}
        await q.message.reply_text(f"Edit *{p['name']}*. Kirim nama baru, atau kirim - untuk mempertahankan nilai:",parse_mode="Markdown"); return
    if data == "stats":
        rows=db_get("products",{"select":"stock"})
        total=len(rows); ready=sum(1 for x in rows if x["stock"])
        orders=db_get("orders",{"select":"id"})
        await q.message.reply_text(f"📊 *Ringkasan FadStore*\nTotal stok: {total}\n🟢 READY: {ready}\n🔴 SOLD: {total-ready}\nPesanan tercatat: {len(orders)}",parse_mode="Markdown"); return
    if data == "orders":
        rows=db_get("orders",{"select":"id,customer_name,product_name,amount,status,created_at","order":"created_at.desc","limit":"15"})
        if not rows: await q.message.reply_text("Belum ada pesanan."); return
        for o in rows:
            await q.message.reply_text(f"Pesanan #{o['id']}\n{o['customer_name']} — {o['product_name']}\n{money(o['amount'])}\nStatus: {o['status']}")
        return
    if data == "settings":
        rows=db_get("store_settings",{"select":"key,value"})
        txt="⚙️ *Pengaturan toko*\n"+"\n".join(f"{x['key']}: {x['value']}" for x in rows)
        await q.message.reply_text(txt+"\n\nGunakan /setnama, /setwa, atau /settelegram di chat.",parse_mode="Markdown"); return
    if data == "cancel":
        STATES.pop(ADMIN_ID,None); await q.message.reply_text("Dibatalkan.",reply_markup=menu()); return

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    s=STATES.get(ADMIN_ID)
    if not s:
        await update.message.reply_text("Pilih menu dengan /start.")
        return
    value=update.message.text.strip()
    if s["action"]=="add":
        step=s["step"]
        if step=="name":
            s["name"]=value; s["step"]="price"; await update.message.reply_text("Masukkan harga angka saja, contoh 350000:"); return
        if step=="price":
            try: s["price"]=int(value); assert s["price"]>=0
            except: await update.message.reply_text("Harga harus angka 0 atau lebih. Coba lagi."); return
            s["step"]="rank"; await update.message.reply_text("Rank/kategori akun (kirim - jika kosong):"); return
        if step=="rank":
            s["rank"]="" if value=="-" else value; s["step"]="level"; await update.message.reply_text("Level akun (kirim - jika kosong):"); return
        if step=="level":
            s["level"]="" if value=="-" else value; s["step"]="items"; await update.message.reply_text("Item/keterangan singkat (kirim - jika kosong):"); return
        if step=="items":
            s["items"]="" if value=="-" else value; s["step"]="photo"
            await update.message.reply_text("Kirim foto akun sekarang, atau ketik *lewati* jika tanpa foto.",parse_mode="Markdown"); return
        if step=="photo":
            if value.lower()!="lewati":
                await update.message.reply_text("Kirim foto sebagai gambar Telegram, atau ketik lewati."); return
            save_product(s,None,update); return
    if s["action"]=="edit":
        p=s["product"]; field=s["step"]
        if field=="name":
            if value!="-": p["name"]=value
            s["step"]="price"; await update.message.reply_text(f"Harga sekarang {p['price']}. Kirim harga baru atau -:"); return
        if field=="price":
            if value!="-":
                try: p["price"]=int(value); assert p["price"]>=0
                except: await update.message.reply_text("Harga harus angka 0 atau lebih, atau -."); return
            s["step"]="rank"; await update.message.reply_text(f"Rank sekarang {p.get('rank') or '-'}. Kirim nilai baru atau -:"); return
        if field=="rank":
            if value!="-": p["rank"]=value
            s["step"]="level"; await update.message.reply_text(f"Level sekarang {p.get('level') or '-'}. Kirim nilai baru atau -:"); return
        if field=="level":
            if value!="-": p["level"]=value
            s["step"]="items"; await update.message.reply_text(f"Keterangan sekarang {p.get('items') or '-'}. Kirim nilai baru atau -:"); return
        if field=="items":
            if value!="-": p["items"]=value
            s["step"]="photo"; await update.message.reply_text("Kirim foto baru, ketik *hapus* untuk mengosongkan foto, atau - untuk mempertahankan foto.",parse_mode="Markdown"); return
        if field=="photo":
            if value=="-": p.pop("_keep_image",None)
            elif value.lower()=="hapus": p["image"]=None
            else: await update.message.reply_text("Kirim foto, hapus, atau -."); return
            payload={k:p.get(k) for k in ["name","price","rank","level","items","image"]}
            db_write("products","PATCH",payload,{"id":f"eq.{s['id']}"})
            STATES.pop(ADMIN_ID,None); await update.message.reply_text("✅ Produk berhasil diperbarui.",reply_markup=menu()); return

async def save_product(s, image_url, update):
    row={"game":s["game"],"name":s["name"],"price":s["price"],"stock":True,"rank":s.get("rank",""),"level":s.get("level",""),"items":s.get("items",""),"image":image_url}
    db_write("products","POST",row)
    STATES.pop(ADMIN_ID,None)
    await update.message.reply_text("✅ Stok berhasil ditambahkan ke website!",reply_markup=menu())

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    s=STATES.get(ADMIN_ID)
    if not s or s.get("step")!="photo": return
    photo=update.message.photo[-1]
    tg_file=await context.bot.get_file(photo.file_id)
    raw=BytesIO(); await tg_file.download_to_memory(out=raw)
    raw.seek(0)
    path=f"{uuid.uuid4().hex}.jpg"
    headers={"apikey":SERVICE_KEY,"Authorization":f"Bearer {SERVICE_KEY}","Content-Type":"image/jpeg","x-upsert":"true"}
    r=requests.post(f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}",headers=headers,data=raw.getvalue(),timeout=60)
    if r.status_code not in (200,201):
        log.error("Storage upload failed: %s",r.text)
        await update.message.reply_text("Upload foto gagal. Pastikan bucket Storage sudah dibuat. Coba lagi atau ketik lewati."); return
    url=f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{path}"
    if s["action"]=="add":
        await save_product(s,url,update)
    else:
        p=s["product"]; p["image"]=url
        db_write("products","PATCH",{"image":url},{"id":f"eq.{s['id']}"})
        STATES.pop(ADMIN_ID,None); await update.message.reply_text("✅ Foto dan data produk berhasil diperbarui.",reply_markup=menu())

async def set_setting(update, context, key):
    if not is_admin(update): return
    value=" ".join(context.args).strip()
    if not value: await update.message.reply_text("Format: /"+update.message.text.split()[0][1:]+" nilai_baru"); return
    db_write("store_settings","PATCH",{"value":value},{"key":f"eq.{key}"})
    await update.message.reply_text("✅ Pengaturan diperbarui.")

async def setnama(u,c): await set_setting(u,c,"store_name")
async def setwa(u,c): await set_setting(u,c,"whatsapp")
async def settg(u,c): await set_setting(u,c,"telegram")

async def error_handler(update, context):
    log.exception("Bot error", exc_info=context.error)
    if update and update.effective_message and is_admin(update):
        await update.effective_message.reply_text("Terjadi kesalahan. Periksa log hosting atau coba lagi.")

def main():
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("cancel",cancel))
    app.add_handler(CommandHandler("setnama",setnama))
    app.add_handler(CommandHandler("setwa",setwa))
    app.add_handler(CommandHandler("settelegram",settg))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.PHOTO,photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler))
    app.add_error_handler(error_handler)
    log.info("FadStore Telegram admin bot starting")
    app.run_polling(drop_pending_updates=True)

if __name__=="__main__": main()
