# 🚀 Deploy Telvora ke Render (Gratis Selamanya!)

**Render** adalah alternatif gratis dari Railway dengan unlimited free tier!

## ✨ Keuntungan Render:
✅ **100% Gratis** - Selamanya (tidak ada credit yang habis)
✅ **Satu Platform** - Backend & Frontend dalam satu service
✅ **Auto-Deploy** - Push GitHub = auto deploy
✅ **Easy Setup** - Seperti Railway tapi lebih simple

---

## 📦 Langkah Deployment ke Render

### 1. Persiapan (Di Local)

Pastikan Anda sudah di branch `deploy`:
```powershell
git branch
# Output: * deploy
```

Jika belum, switch ke branch deploy:
```powershell
git checkout deploy
```

### 2. Setup Render Account

1. **Buka [render.com](https://render.com)**
2. **Click "Sign up"**
3. **Choose: "Sign up with GitHub"**
4. **Authorize Render untuk akses repository**

### 3. Deploy Service

#### Option A: Deploy via Dashboard (Recommended)

1. **Klik "New +"** di dashboard
2. **Pilih "Web Service"**
3. **Connect Repository:**
   - Cari repository: `Telmi`
   - Click "Connect"

4. **Configure Service:**
   ```
   Name: telvora
   Environment: Python
   Build Command: 
     pip install --upgrade pip &&
     pip install -r src/services/recsys_agentic/requirements.txt &&
     pip install streamlit plotly requests
   
   Start Command:
     streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
   
   Plan: Free
   ```

5. **Branch:** `deploy` (dari dropdown)

6. **Scroll ke bawah → Environment Variables**
   
   Tambahkan variabel berikut:
   ```
   VITE_SUPABASE_URL          your_supabase_url
   VITE_SUPABASE_ANON_KEY     your_supabase_anon_key
   GEMINI_API_KEY             your_gemini_api_key (optional)
   BACKEND_URL                http://localhost:8000
   OLLAMA_MODEL               (kosongkan)
   OLLAMA_BASE_URL            http://localhost:11434
   ```

7. **Click "Create Web Service"**
8. **Tunggu 3-5 menit** untuk build & deploy pertama kali

#### Option B: Deploy via render.yaml (Lebih Cepat)

File `render.yaml` sudah saya siapkan di repository. Render akan otomatis detect file ini saat deploy.

Jika ingin trigger deploy otomatis:
1. Push ke GitHub:
   ```powershell
   git add render.yaml
   git commit -m "Add render.yaml configuration"
   git push origin deploy
   ```

2. Buka [render.com](https://render.com) → Create Service → Langsung pilih repository, render.yaml akan ter-load otomatis

### 4. Set Environment Variables (Penting!)

Setelah service dibuat:

1. **Click service "telvora"**
2. **Tab "Settings"**
3. **Environment → "Add Environment Variable"**

Tambahkan:
```
VITE_SUPABASE_URL = your_supabase_url
VITE_SUPABASE_ANON_KEY = your_supabase_anon_key
GEMINI_API_KEY = your_gemini_api_key (optional)
BACKEND_URL = http://localhost:8000
```

**⚠️ PENTING:**
- Jangan lupa ganti dengan **Supabase credentials Anda**!
- `BACKEND_URL` harus `http://localhost:8000` (backend & frontend sama container)

### 5. Deploy!

Render akan otomatis mulai build & deploy. Anda bisa lihat di **Deployments** tab.

Status akan berubah:
- 🟡 **Building** (3-5 menit)
- 🟢 **Live** (berhasil!)

---

## 🎯 Akses Aplikasi

Setelah deployment selesai, Render akan kasih URL:
```
https://telvora.onrender.com
```

(Nama service Anda akan berbeda, check di dashboard)

---

## ✅ Checklist Deployment

### Pre-Deployment:
- [ ] Local branch: `deploy` (aktif)
- [ ] File `render.yaml` sudah ada
- [ ] Model files di `src/services/model/` sudah ada
- [ ] Supabase credentials siap

### Saat Deploy:
- [ ] GitHub account terhubung ke Render
- [ ] Repository Telmi ter-connect
- [ ] Branch `deploy` dipilih
- [ ] Environment variables diset (Supabase + BACKEND_URL)
- [ ] Plan: **Free** (bukan paid!)

### Testing:
- [ ] URL Render bisa dibuka
- [ ] Dashboard tampil
- [ ] Backend status "Connected" ✅
- [ ] Test Customer Analytics
- [ ] Test Product Simulation

---

## 🐛 Troubleshooting

### Build Gagal
**Penyebab:** Missing dependencies atau model files

**Solusi:**
1. Cek logs di Render (Deployments tab → click deployment → Logs)
2. Pastikan model files ter-push:
   ```powershell
   git add src/services/model/*.pkl
   git commit -m "Add model files"
   git push origin deploy
   ```

### Backend Tidak Tersedia
**Penyebab:** Environment variables belum diset

**Solusi:**
1. Pastikan `BACKEND_URL = http://localhost:8000`
2. Pastikan Supabase URL & key sudah benar
3. Redeploy service (Settings → Redeploy)

### "Database not configured"
**Penyebab:** Supabase credentials salah atau tidak lengkap

**Solusi:**
1. Cek environment variables di Render Settings
2. Pastikan `VITE_SUPABASE_URL` dan `VITE_SUPABASE_ANON_KEY` sudah benar
3. Redeploy

### App Stuck / Timeout
**Penyebab:** Streamlit butuh waktu load model

**Solusi:**
- Tunggu lebih lama (model ML butuh waktu load)
- Check logs untuk error detail

---

## 📊 Monitoring

### Cek Logs
- Service dashboard → **Logs** tab
- Real-time logs saat startup

Anda akan lihat:
```
Installing dependencies...
✓ Model artifacts loaded
✓ Supabase connected
✓ Streamlit server started
```

### Cek Status
- Service dashboard → Status indicator (🟢 = online)
- Metrics tab → CPU/Memory usage

### Redeploy
Jika ada error:
1. Fix code lokal
2. Push ke GitHub
3. Render auto-redeploy
   
Atau manual redeploy:
- Settings → Manual Deploy → "Deploy latest commit"

---

## 🔄 Update Aplikasi

Setiap push ke GitHub akan auto-deploy:

```powershell
# Edit code lokal
# Test dengan baik

# Commit & push
git add .
git commit -m "Fix: Update feature X"
git push origin deploy

# Render akan otomatis deploy 🚀
```

---

## 💾 Backup & Restore

### Backup Database
Pastikan backup Supabase regularly:
1. [Supabase Dashboard](https://supabase.com) → Project
2. Settings → Backups
3. Enable automatic backups

### Restore
Jika ada masalah:
1. Restore dari Supabase backup
2. Redeploy di Render (Settings → Manual Deploy)

---

## 🎉 Selesai!

Aplikasi Telvora Anda sekarang **online dan gratis selamanya!**

### Share dengan Dosen:

```
🌐 Live Demo (Render):
https://telvora.onrender.com

📚 GitHub Repository (Branch Deploy):
https://github.com/Hazyrzq/Telmi/tree/deploy

📖 Tech Stack:
- Frontend: Streamlit (Python)
- Backend: FastAPI (Python)
- ML Model: scikit-learn (Random Forest)
- Database: Supabase (PostgreSQL)
- Hosting: Render (Free)
```

---

## 💡 Pro Tips

1. **Always Push to `deploy` branch** - Jangan ke `master`
2. **Monitor Logs** - Cek logs saat ada error
3. **Free Tier Limits** - Render free tier OK untuk project ini
4. **Custom Domain** - Bisa upgrade later untuk custom domain
5. **Auto-Redeploy** - Matikan jika ingin kontrol penuh (Settings)

---

## 🚀 Deploy Sekarang!

Siap? Buka [render.com](https://render.com) dan mulai deployment!

Jika ada pertanyaan atau error, cek logs di Render dashboard.

**Good luck! 🎓**
