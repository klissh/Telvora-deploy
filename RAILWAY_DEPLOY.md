# 🚀 Deploy Telvora ke Railway (All-in-One)

## Keuntungan Deploy di Railway Saja:
✅ **Satu platform** - Backend & Frontend dalam satu project
✅ **Mudah** - Hanya perlu setup satu kali
✅ **Gratis** - Free tier Railway cukup untuk project ini
✅ **Auto-deploy** - Push ke GitHub = auto update

---

## 📦 Langkah Deployment

### 1. Push Code ke GitHub

```powershell
git add .
git commit -m "Add Railway all-in-one deployment"
git push origin master
```

### 2. Setup Railway

#### 2.1 Buat Akun
1. Buka [railway.app](https://railway.app)
2. Click "Login" → Sign in dengan GitHub
3. Authorize Railway untuk akses repository

#### 2.2 Deploy Project
1. Click "New Project"
2. Pilih "Deploy from GitHub repo"
3. Cari dan pilih repository **Telmi**
4. Railway akan otomatis detect dan mulai deploy

#### 2.3 Set Environment Variables
1. Di Railway Dashboard, click project Anda
2. Click tab "Variables"
3. Tambahkan variabel berikut:

```bash
# Supabase (WAJIB)
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend URL (Set ke localhost karena backend & frontend sama-sama di Railway)
BACKEND_URL=http://localhost:8000

# Optional: AI Features (bisa dikosongkan)
GEMINI_API_KEY=your_gemini_api_key
OLLAMA_MODEL=
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=
```

**⚠️ PENTING:** 
- `BACKEND_URL` harus `http://localhost:8000` karena backend dan frontend berjalan di container yang sama
- Jangan lupa ganti Supabase credentials dengan milik Anda!

#### 2.4 Deploy Ulang (Jika Perlu)
Setelah set environment variables:
1. Click "Deployments" tab
2. Click tombol "Redeploy" atau tunggu auto-deploy dari GitHub

### 3. Akses Aplikasi

Railway akan memberikan URL publik (contoh: `https://telmi-production.up.railway.app`)

**Tunggu 3-5 menit** untuk deployment pertama kali.

---

## 🎯 Cara Kerja

Railway akan:
1. ✅ Install dependencies (`requirements.txt` backend + streamlit/plotly)
2. ✅ Load model artifacts dari `src/services/model/`
3. ✅ Start FastAPI backend di port 8000 (internal)
4. ✅ Start Streamlit frontend di port Railway (publik)
5. ✅ Streamlit connect ke FastAPI via localhost:8000

**Arsitektur:**
```
Railway Container
├── FastAPI Backend (port 8000 - internal)
└── Streamlit Frontend (port $PORT - publik)
    └── Calls → http://localhost:8000
```

---

## ✅ Checklist Deployment

### Sebelum Deploy:
- [ ] File model ada di `src/services/model/`
  - `model_dokter_rf.pkl`
  - `label_encoder.pkl`
  - `global_averages.pkl`
- [ ] Supabase sudah setup & ada data
- [ ] Code sudah di-push ke GitHub

### Saat Deploy Railway:
- [ ] Project Railway dibuat
- [ ] Repository Telmi terhubung
- [ ] Environment variables diset (Supabase, BACKEND_URL)
- [ ] Deployment berhasil (status hijau)

### Testing:
- [ ] Buka URL Railway
- [ ] Dashboard tampil
- [ ] Backend status "Connected" ✅
- [ ] Test Customer Analytics
- [ ] Test Product Simulation

---

## 🐛 Troubleshooting

### Build Failed
**Kemungkinan Penyebab:**
- Dependencies tidak lengkap
- Model files tidak ter-upload

**Solusi:**
1. Cek Railway logs (tab "Deployments" → Click deployment → "View Logs")
2. Pastikan semua file di `src/services/model/` ter-push ke GitHub:
   ```powershell
   git add src/services/model/*.pkl
   git commit -m "Add model files"
   git push
   ```

### Backend tidak tersedia
**Kemungkinan Penyebab:**
- Environment variables salah
- Backend belum ready saat Streamlit start

**Solusi:**
1. Cek `BACKEND_URL` = `http://localhost:8000`
2. Cek Supabase credentials sudah benar
3. Redeploy project

### "Database not configured"
**Penyebab:** Supabase credentials tidak diset

**Solusi:**
1. Tambahkan `VITE_SUPABASE_URL` dan `VITE_SUPABASE_ANON_KEY` di Variables
2. Redeploy

---

## 📊 Monitoring

### Cek Logs
1. Railway Dashboard → Project
2. Tab "Deployments"
3. Click deployment terbaru
4. Click "View Logs"

Anda akan lihat:
- ✅ Backend FastAPI starting...
- ✅ Streamlit starting...
- ✅ Model artifacts loaded
- ✅ Supabase connected

### Cek Resource Usage
Tab "Metrics" menampilkan:
- CPU usage
- Memory usage
- Network traffic

Railway free tier: $5 credit/bulan (cukup untuk project ini)

---

## 🎉 Selesai!

Aplikasi Anda sekarang online di **satu platform Railway**!

### Share dengan Dosen:

```
🌐 Aplikasi Telvora (Live Demo):
https://your-project.up.railway.app

📚 GitHub Repository:
https://github.com/Hazyrzq/Telmi

📖 Tech Stack:
- Frontend: Streamlit
- Backend: FastAPI + scikit-learn
- Database: Supabase
- Hosting: Railway
```

---

## 💡 Tips

1. **Auto-deploy:** Setiap push ke GitHub akan auto-deploy ke Railway
2. **Custom Domain:** Railway support custom domain (Settings → Domains)
3. **Logs:** Selalu cek logs jika ada error
4. **Free Tier:** Monitor usage di tab "Usage" (free: $5/month)

---

## 🔄 Update Aplikasi

Untuk update aplikasi:
```powershell
# Edit code
git add .
git commit -m "Update feature X"
git push origin master
```

Railway akan otomatis re-deploy! 🚀

---

**Good luck with your presentation! 🎓**
