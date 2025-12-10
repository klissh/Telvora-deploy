# 🚀 Panduan Deployment Telvora ke Streamlit Cloud

Dokumen ini berisi panduan lengkap untuk hosting aplikasi Telvora (Frontend + Backend) ke Streamlit Cloud.

## 📋 Daftar Isi
1. [Persiapan](#persiapan)
2. [Deploy Backend (FastAPI)](#deploy-backend-fastapi)
3. [Deploy Frontend (Streamlit)](#deploy-frontend-streamlit)
4. [Testing & Troubleshooting](#testing--troubleshooting)

---

## Persiapan

### 1. File-file yang Sudah Disiapkan ✅

Berikut file-file yang sudah dibuat untuk deployment:

```
Telmi/
├── streamlit_app.py                    # Aplikasi Streamlit utama
├── requirements-streamlit.txt          # Dependencies untuk Streamlit
├── .streamlit/
│   ├── config.toml                     # Konfigurasi Streamlit
│   └── secrets.toml.example            # Template secrets
├── src/services/recsys_agentic/
│   ├── main.py                         # Backend FastAPI
│   └── requirements.txt                # Dependencies backend
└── DEPLOYMENT.md                       # Dokumentasi ini
```

### 2. Persiapan Akun

Anda memerlukan:
- ✅ Akun GitHub (untuk repository)
- ✅ Akun Streamlit Cloud (gratis, sign up dengan GitHub)
- ✅ Akun Railway/Render (untuk backend FastAPI - pilih salah satu)
- ✅ Akun Supabase (untuk database)

---

## Deploy Backend (FastAPI)

Backend harus di-deploy terpisah karena Streamlit Cloud tidak support menjalankan FastAPI server secara native.

### Opsi 1: Deploy ke Railway (Recommended) 🚂

Railway menyediakan free tier yang cocok untuk project ini.

#### Langkah-langkah:

1. **Buat akun Railway**
   - Kunjungi [railway.app](https://railway.app)
   - Sign up dengan GitHub

2. **Buat Project Baru**
   - Click "New Project"
   - Pilih "Deploy from GitHub repo"
   - Pilih repository Telmi Anda

3. **Konfigurasi Backend**
   
   Buat file `railway.json` di root project:
   ```json
   {
     "build": {
       "builder": "NIXPACKS",
       "buildCommand": "pip install -r src/services/recsys_agentic/requirements.txt"
     },
     "deploy": {
       "startCommand": "uvicorn src.services.recsys_agentic.main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

4. **Set Environment Variables di Railway**
   
   Tambahkan variabel berikut di Railway Dashboard → Settings → Variables:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   GEMINI_API_KEY=your_gemini_api_key (optional)
   OLLAMA_MODEL=your_ollama_model (optional, kosongkan jika tidak pakai)
   ```

5. **Deploy**
   - Railway akan otomatis build dan deploy
   - Catat URL backend Anda (misal: `https://your-app.railway.app`)

### Opsi 2: Deploy ke Render 🎨

1. **Buat akun Render**
   - Kunjungi [render.com](https://render.com)
   - Sign up dengan GitHub

2. **Buat Web Service Baru**
   - Click "New +" → "Web Service"
   - Connect repository GitHub Anda
   - Pilih branch `master` atau `main`

3. **Konfigurasi Service**
   ```
   Name: telvora-backend
   Environment: Python
   Build Command: pip install -r src/services/recsys_agentic/requirements.txt
   Start Command: uvicorn src.services.recsys_agentic.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Set Environment Variables**
   
   Tambahkan di Render Dashboard → Environment:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   GEMINI_API_KEY=your_gemini_api_key (optional)
   OLLAMA_MODEL=your_ollama_model (optional)
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Catat URL backend (misal: `https://telvora-backend.onrender.com`)

---

## Deploy Frontend (Streamlit)

### Langkah 1: Push Code ke GitHub

1. **Commit semua perubahan**
   ```powershell
   git add .
   git commit -m "Add Streamlit deployment files"
   git push origin master
   ```

2. **Pastikan file-file ini ada di repository:**
   - ✅ `streamlit_app.py`
   - ✅ `requirements-streamlit.txt`
   - ✅ `.streamlit/config.toml`

### Langkah 2: Deploy ke Streamlit Cloud

1. **Buka Streamlit Cloud**
   - Kunjungi [share.streamlit.io](https://share.streamlit.io)
   - Sign in dengan GitHub

2. **Create New App**
   - Click "New app"
   - Pilih repository: `Hazyrzq/Telmi`
   - Branch: `master`
   - Main file path: `streamlit_app.py`
   - Click "Advanced settings"

3. **Set Secrets (PENTING!)**
   
   Di Advanced settings → Secrets, tambahkan:
   ```toml
   # Backend URL (ganti dengan URL Railway/Render Anda)
   BACKEND_URL = "https://your-backend-url.railway.app"
   
   # Supabase
   VITE_SUPABASE_URL = "your_supabase_url"
   VITE_SUPABASE_ANON_KEY = "your_supabase_anon_key"
   
   # Optional: AI
   GEMINI_API_KEY = "your_gemini_api_key"
   OLLAMA_MODEL = ""
   ```
   
   **⚠️ PENTING:** Ganti `BACKEND_URL` dengan URL backend yang sudah Anda deploy di Railway/Render!

4. **Set Python Version (Optional)**
   
   Buat file `.streamlit/config.toml` dengan:
   ```toml
   [server]
   headless = true
   ```

5. **Deploy**
   - Click "Deploy!"
   - Tunggu proses build selesai (2-5 menit)
   - Aplikasi akan tersedia di: `https://your-app-name.streamlit.app`

---

## Testing & Troubleshooting

### Test Lokal Sebelum Deploy

1. **Jalankan Backend**
   ```powershell
   # Aktivasi virtual environment
   .\.venv310\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r src/services/recsys_agentic/requirements.txt
   
   # Jalankan backend
   uvicorn src.services.recsys_agentic.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Jalankan Streamlit (di terminal baru)**
   ```powershell
   # Install Streamlit
   pip install streamlit plotly requests
   
   # Set environment variable (optional untuk testing lokal)
   $env:BACKEND_URL = "http://localhost:8000"
   
   # Jalankan Streamlit
   streamlit run streamlit_app.py
   ```

3. **Buka Browser**
   - Streamlit: http://localhost:8501
   - Backend API Docs: http://localhost:8000/docs

### Troubleshooting Common Issues

#### ❌ Error: "Backend tidak tersedia"

**Penyebab:**
- Backend belum running
- URL backend salah
- CORS issue

**Solusi:**
1. Pastikan backend sudah deployed dan running
2. Cek URL backend di Streamlit secrets
3. Pastikan backend mengizinkan CORS (sudah dikonfigurasi di `main.py`)

#### ❌ Error: "Database not configured"

**Penyebab:**
- Supabase credentials tidak diset

**Solusi:**
1. Cek environment variables di backend (Railway/Render)
2. Pastikan `VITE_SUPABASE_URL` dan `VITE_SUPABASE_ANON_KEY` sudah benar

#### ❌ Error: "Model artifacts not found"

**Penyebab:**
- File model tidak ter-upload ke server

**Solusi:**
1. Pastikan folder `src/services/model/` ada dan berisi:
   - `model_dokter_rf.pkl`
   - `label_encoder.pkl`
   - `global_averages.pkl`
2. Push ke GitHub dan redeploy

#### ❌ Streamlit App Error saat Build

**Penyebab:**
- Dependencies tidak lengkap

**Solusi:**
1. Pastikan `requirements-streamlit.txt` sudah benar
2. Rename menjadi `requirements.txt` (Streamlit Cloud mencari file ini by default)
   ```powershell
   # Di local
   copy requirements-streamlit.txt requirements.txt
   git add requirements.txt
   git commit -m "Add requirements.txt for Streamlit"
   git push
   ```

### Monitoring & Logs

#### Railway Logs
- Dashboard → Service → Logs
- Monitor real-time logs backend

#### Render Logs
- Dashboard → Service → Logs tab

#### Streamlit Cloud Logs
- App dashboard → "Manage app" → "Logs"

---

## 📊 Checklist Deployment

### Pre-Deployment ✅
- [ ] File `streamlit_app.py` sudah dibuat
- [ ] File `requirements-streamlit.txt` sudah dibuat
- [ ] Folder `.streamlit/` dengan `config.toml` sudah ada
- [ ] Model files ada di `src/services/model/`
- [ ] Database Supabase sudah disetup
- [ ] Credentials Supabase sudah disiapkan

### Backend Deployment ✅
- [ ] Backend deployed ke Railway/Render
- [ ] Environment variables sudah diset
- [ ] Backend URL sudah dicatat
- [ ] Test endpoint `/health` berhasil

### Frontend Deployment ✅
- [ ] Code di-push ke GitHub
- [ ] Streamlit Cloud app sudah dibuat
- [ ] Secrets sudah diset dengan benar
- [ ] `BACKEND_URL` sudah diupdate
- [ ] Deploy berhasil

### Post-Deployment Testing ✅
- [ ] Dashboard bisa dibuka
- [ ] Backend status "Connected"
- [ ] Customer Analytics berfungsi
- [ ] Product Simulation berfungsi
- [ ] Charts dan visualisasi tampil

---

## 🎉 Selesai!

Aplikasi Telvora Anda sekarang sudah online!

**URL Aplikasi:**
- Frontend (Streamlit): `https://your-app.streamlit.app`
- Backend (API): `https://your-backend.railway.app`
- API Docs: `https://your-backend.railway.app/docs`

### Share dengan Dosen

Kirimkan link berikut:
```
Aplikasi Telvora (Streamlit):
https://your-app.streamlit.app

API Documentation (FastAPI):
https://your-backend.railway.app/docs

GitHub Repository:
https://github.com/Hazyrzq/Telmi
```

---

## 💡 Tips Production

1. **Monitoring**: Aktifkan monitoring di Railway/Render
2. **Backups**: Backup database Supabase secara berkala
3. **Rate Limiting**: Tambahkan rate limiting di backend untuk production
4. **Caching**: Gunakan Streamlit caching (`@st.cache_data`) untuk optimize performance
5. **Authentication**: Tambahkan auth jika diperlukan (Streamlit mendukung authentication)

---

## 📞 Support

Jika ada masalah:
1. Cek logs di Railway/Render (backend)
2. Cek logs di Streamlit Cloud (frontend)
3. Test endpoint backend langsung di `/docs`
4. Pastikan semua secrets sudah benar

**Dokumentasi Referensi:**
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Good luck! 🚀**
