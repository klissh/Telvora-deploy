# 🚀 Deploy Telvora ke Streamlit Community Cloud (100% GRATIS!)

## ✨ Keuntungan Streamlit Community Cloud:
✅ **100% Gratis** - Selamanya, tanpa kartu kredit!
✅ **Tanpa Backend Terpisah** - Semua logic dalam satu app
✅ **Super Mudah** - Deploy dalam 3 langkah!
✅ **Auto-Deploy** - Push GitHub = auto update

---

## 📦 Langkah Deployment (3 Menit!)

### Step 1: Commit & Push ke GitHub

```powershell
cd "D:\documents\Kuliah\Tugas Bootcamp\Asah Led by Dicoding\telvora\Telmi"
git checkout deploy
git add streamlit_app.py requirements.txt packages.txt
git commit -m "Refactor: Streamlit standalone version (no backend needed)"
git push origin deploy
```

### Step 2: Buka Streamlit Community Cloud

1. **Buka**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in dengan GitHub**
3. **Click "New app"**

### Step 3: Configure & Deploy

**Repository:**
```
klissh/Telvora-deploy
```

**Branch:**
```
deploy
```

**Main file path:**
```
streamlit_app.py
```

**Click "Advanced settings..."**

### Step 4: Set Secrets (PENTING!)

Di bagian "Secrets", paste ini (ganti dengan credentials Anda):

```toml
# Supabase Configuration (WAJIB!)
VITE_SUPABASE_URL = "your_supabase_project_url_here"
VITE_SUPABASE_ANON_KEY = "your_supabase_anon_key_here"

# Optional: AI Features (bisa dikosongkan)
GEMINI_API_KEY = ""
OLLAMA_MODEL = ""
```

**⚠️ PENTING:** Ganti dengan Supabase credentials Anda yang sebenarnya!

### Step 5: Deploy!

- **Click "Deploy!"**
- **Tunggu 2-3 menit**
- **Aplikasi online!** 🎉

---

## ✅ Checklist Deployment

**Pre-Deployment:**
- [ ] File `streamlit_app.py` (standalone version) sudah ada
- [ ] File `requirements.txt` sudah update
- [ ] File `packages.txt` sudah ada
- [ ] Model files di `src/services/model/` sudah ter-push
- [ ] Supabase credentials siap

**Saat Deploy:**
- [ ] Streamlit Cloud account dibuat (sign in dengan GitHub)
- [ ] Repository: `klissh/Telvora-deploy`
- [ ] Branch: `deploy`
- [ ] Secrets diset (Supabase URL & Key)
- [ ] Deploy button clicked

**Testing:**
- [ ] URL Streamlit bisa dibuka
- [ ] Dashboard tampil data
- [ ] Customer Analytics works
- [ ] Product Simulation works
- [ ] No error di logs

---

## 🎯 Cara Mendapatkan Supabase Credentials

1. **Login ke Supabase**: [supabase.com](https://supabase.com)
2. **Pilih Project Anda**
3. **Click Settings (gear icon) → API**
4. **Copy:**
   - Project URL → `VITE_SUPABASE_URL`
   - `anon` `public` key → `VITE_SUPABASE_ANON_KEY`

---

## 🐛 Troubleshooting

### Error: "Supabase credentials not found"
**Solusi:**
1. Pastikan secrets sudah diset di Streamlit Cloud
2. Format secrets harus TOML (key = "value")
3. Redeploy app (click "Reboot app")

### Error: "Model files not found"
**Solusi:**
1. Pastikan folder `src/services/model/` ter-push ke GitHub
2. Cek apakah file `.gitignore` tidak exclude `*.pkl`
3. Push ulang:
   ```powershell
   git add src/services/model/*.pkl --force
   git commit -m "Add model files"
   git push origin deploy
   ```

### App Stuck / Slow Loading
**Penyebab:** Model ML butuh waktu load (pertama kali)

**Solusi:**
- Tunggu 1-2 menit
- Refresh page
- Check logs di Streamlit Cloud dashboard

### Database Connection Error
**Solusi:**
1. Cek Supabase URL & key sudah benar
2. Pastikan Supabase project masih aktif
3. Test credentials manual di Supabase dashboard

---

## 📊 Monitoring & Logs

### Cek Logs
1. **Streamlit Cloud Dashboard**
2. **Click aplikasi Anda**
3. **Click hamburger menu (☰)**
4. **Pilih "Manage app" → "Logs"**

Anda akan lihat:
```
✅ Loading ML models...
✅ Initializing Supabase...
✅ App ready!
```

### Reboot App
Jika ada error atau update:
1. Dashboard → Manage app
2. Click "Reboot app"
3. Tunggu 1-2 menit

---

## 🔄 Update Aplikasi

Setiap push ke GitHub akan auto-update:

```powershell
# Edit code lokal
# ...

# Commit & push
git add .
git commit -m "Update: Fix feature X"
git push origin deploy

# Streamlit akan auto-deploy dalam 1-2 menit 🚀
```

---

## 💡 Pro Tips

1. **Always Check Logs** - Jika ada error, logs adalah teman terbaik
2. **Use st.cache** - App sudah optimize dengan caching
3. **Free Tier Limits** - Streamlit free tier OK untuk project ini
4. **Custom URL** - Bisa request custom subdomain di settings
5. **Share Link** - Link publik bisa langsung dibagikan ke dosen

---

## 🎉 Selesai!

Aplikasi Telvora Anda sekarang **online dan gratis selamanya!**

### Share dengan Dosen:

```
🌐 Live Demo (Streamlit):
https://your-app-name.streamlit.app

📚 GitHub Repository:
https://github.com/klissh/Telvora-deploy/tree/deploy

📖 Tech Stack:
- Frontend & Backend: Streamlit (Python)
- ML Model: scikit-learn (Random Forest)
- Database: Supabase (PostgreSQL)
- Hosting: Streamlit Community Cloud (Free Forever!)
```

---

## 🆚 Perbandingan dengan Versi Sebelumnya

| Feature | Versi Lama (FastAPI + Streamlit) | Versi Baru (Streamlit Only) |
|---------|-----------------------------------|------------------------------|
| Deployment | 2 platform (Railway + Streamlit) | 1 platform (Streamlit) |
| Kartu Kredit | Diperlukan (Render/Railway) | **TIDAK diperlukan** ✅ |
| Gratis | Limited (credit habis) | **Selamanya** ✅ |
| Setup | Complex (2 services) | **Super simple** ✅ |
| API Endpoint | Ya (FastAPI) | Tidak (tapi tidak perlu) |
| Performance | Sama | Sama ✅ |
| Fitur | Lengkap | **Lengkap** ✅ |

---

## 📞 Support

Jika ada masalah:
1. **Check logs** di Streamlit Cloud dashboard
2. **Verify secrets** (Supabase credentials)
3. **Check GitHub** - pastikan semua files ter-push
4. **Reboot app** jika perlu

**Dokumentasi Streamlit:**
- [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

**Siap deploy? Good luck! 🚀**
