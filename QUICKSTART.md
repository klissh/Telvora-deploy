# 🚀 Quick Start - Hosting Telvora ke Streamlit Cloud

## Ringkasan Singkat

Ini adalah panduan cepat untuk hosting aplikasi Telvora. File-file deployment sudah disiapkan, Anda tinggal ikuti langkah berikut:

---

## 📦 Langkah 1: Deploy Backend (FastAPI) ke Railway

### 1.1 Setup Railway
1. Buka [railway.app](https://railway.app)
2. Sign up dengan GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Pilih repository **Telmi**

### 1.2 Set Environment Variables
Di Railway Dashboard → Variables, tambahkan:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
OLLAMA_MODEL=
```

### 1.3 Deploy
- Railway akan auto-deploy
- **Catat URL backend Anda** (contoh: `https://telmi-production.up.railway.app`)

---

## 🎨 Langkah 2: Deploy Frontend (Streamlit) ke Streamlit Cloud

### 2.1 Push ke GitHub
```powershell
git add .
git commit -m "Add Streamlit deployment"
git push origin master
```

### 2.2 Setup Streamlit Cloud
1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Sign in dengan GitHub
3. Click "New app"
   - Repository: `Hazyrzq/Telmi`
   - Branch: `master`
   - Main file: `streamlit_app.py`

### 2.3 Set Secrets
Di Advanced settings → Secrets, paste ini (ganti dengan nilai Anda):
```toml
BACKEND_URL = "https://your-backend-url.railway.app"
VITE_SUPABASE_URL = "your_supabase_url"
VITE_SUPABASE_ANON_KEY = "your_supabase_anon_key"
GEMINI_API_KEY = "your_gemini_api_key"
OLLAMA_MODEL = ""
```

**⚠️ PENTING:** Ganti `BACKEND_URL` dengan URL Railway Anda!

### 2.4 Deploy
- Click "Deploy!"
- Tunggu 2-5 menit
- Aplikasi Anda online! 🎉

---

## ✅ Testing

Buka aplikasi Streamlit Anda:
- URL: `https://your-app.streamlit.app`
- Cek "Backend Status" harus hijau ✅
- Test fitur Customer Analytics dan Product Simulation

---

## 🐛 Troubleshooting

### Error: Backend tidak tersedia
- Pastikan Railway backend sudah running
- Cek URL backend di Streamlit secrets sudah benar
- Test manual: buka `https://your-backend.railway.app/health`

### Error: Model artifacts not found
- Pastikan folder `src/services/model/` ter-push ke GitHub
- Berisi: `model_dokter_rf.pkl`, `label_encoder.pkl`, `global_averages.pkl`

### Streamlit gagal build
- Rename `requirements-streamlit.txt` → `requirements.txt`
  ```powershell
  copy requirements-streamlit.txt requirements.txt
  git add requirements.txt
  git commit -m "Add requirements"
  git push
  ```

---

## 📋 Checklist Cepat

**Backend (Railway):**
- [ ] Project Railway dibuat
- [ ] Environment variables diset
- [ ] Backend deployed & running
- [ ] URL backend dicatat

**Frontend (Streamlit):**
- [ ] Code di-push ke GitHub
- [ ] Streamlit app dibuat
- [ ] Secrets diset dengan BACKEND_URL yang benar
- [ ] App deployed & running

**Testing:**
- [ ] Backend status Connected ✅
- [ ] Dashboard tampil data
- [ ] Customer Analytics works
- [ ] Product Simulation works

---

## 🎯 Untuk Presentasi ke Dosen

Share 3 link ini:

1. **Aplikasi (Streamlit):**
   ```
   https://your-app.streamlit.app
   ```

2. **API Documentation (FastAPI):**
   ```
   https://your-backend.railway.app/docs
   ```

3. **GitHub Repository:**
   ```
   https://github.com/Hazyrzq/Telmi
   ```

---

## 📚 Dokumentasi Lengkap

Lihat **DEPLOYMENT.md** untuk panduan detail lengkap.

---

**Selamat! Aplikasi Anda sudah online! 🚀**
