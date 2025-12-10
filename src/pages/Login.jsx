import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { isSupabaseConfigured, isValidUrl, isJwt, isWrongKeyPrefix } from '../lib/supabaseClient'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { User, Lock, AlertCircle, ArrowRight, Sparkles, Eye, EyeOff, Loader2 } from 'lucide-react'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/admin'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      await signIn(email, password)
      // Small delay for smooth transition
      setTimeout(() => {
        navigate(from, { replace: true })
      }, 500)
    } catch (err) {
      setLoading(false)
      const msg = err?.message || 'Gagal login'
      if (!isSupabaseConfigured) {
        if (isWrongKeyPrefix) {
          setError('Key bukan Supabase Anon. Jangan pakai sb_publishable/sb_secret; gunakan Anon public key (JWT mulai eyJ...).')
        } else if (!isValidUrl) {
          setError('VITE_SUPABASE_URL tidak valid. Gunakan https://<project-ref>.supabase.co.')
        } else if (!isJwt) {
          setError('VITE_SUPABASE_ANON_KEY harus JWT (mulai eyJ..., berisi titik).')
        } else {
          setError('Konfigurasi Supabase belum diatur dengan benar.')
        }
      } else if (msg === 'Failed to fetch') {
        const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:5174'
        setError(`Tidak bisa terhubung ke Supabase. Periksa URL/Key, koneksi internet, dan whitelist ${origin} di Auth settings.`)
      } else {
        setError(msg)
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white dark:bg-slate-950 p-4 relative overflow-hidden transition-colors">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 dark:bg-cyan-500/10 rounded-full blur-3xl animate-pulse-glow-soft"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 dark:bg-blue-500/10 rounded-full blur-3xl animate-pulse-glow-soft delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-emerald-500/5 dark:bg-emerald-500/5 rounded-full blur-3xl animate-pulse-glow-soft delay-2000"></div>
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:24px_24px]"></div>

      <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 lg:gap-12 items-center relative z-10">
        {/* Left Side - Branding */}
        <div className="hidden md:flex flex-col items-center justify-center text-center space-y-8 p-8 animate-fade-in-up">
          <div className="relative animate-float-soft">
            <div className="flex h-32 w-32 items-center justify-center rounded-2xl bg-white/5 border border-slate-200 dark:border-slate-800 shadow-lg shadow-black/10 animate-glow-soft overflow-hidden">
              <img
                src="/logo.png"
                alt="Telvora logo"
                className="h-20 w-20 object-contain"
                loading="lazy"
              />
            </div>
          </div>
          
          <div className="space-y-4 animate-fade-in-up delay-200">
            <h1 className="text-5xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              Telvora
            </h1>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800/70 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 text-sm font-medium animate-fade-in delay-300 animate-float-soft">
              <Sparkles className="w-4 h-4 text-cyan-500 dark:text-cyan-300" />
              <span>Analytics Portal</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 text-base leading-relaxed max-w-sm mx-auto animate-fade-in-up delay-400">
              Platform analitik berbasis Machine Learning untuk mengelola pelanggan dan memberikan rekomendasi produk yang tepat sasaran.
            </p>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full flex items-center justify-center animate-fade-in-up delay-300">
          <Card className="w-full max-w-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 backdrop-blur-sm shadow-xl hover:shadow-2xl transition-all duration-300">
            <CardHeader className="space-y-2 text-center animate-fade-in-up delay-400">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-500 mb-4 mx-auto animate-float-soft">
                <Lock className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                ADMIN LOGIN
              </CardTitle>
              <CardDescription className="text-slate-600 dark:text-slate-400 text-base">
                Akses Telvora Analytics Portal
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2 animate-fade-in-up delay-500">
                  <Label htmlFor="email" className="text-slate-900 dark:text-slate-300 text-sm font-medium">
                    Email Address
                  </Label>
                  <div className="relative group">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 dark:text-slate-500 group-focus-within:text-cyan-500 dark:group-focus-within:text-cyan-400 transition-colors duration-200" />
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      className="pl-10 bg-slate-100 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:border-cyan-500 focus:ring-cyan-500/20 transition-all duration-200"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2 animate-fade-in-up delay-600">
                  <Label htmlFor="password" className="text-slate-900 dark:text-slate-300 text-sm font-medium">
                    Password
                  </Label>
                  <div className="relative group">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 dark:text-slate-500 group-focus-within:text-cyan-500 dark:group-focus-within:text-cyan-400 transition-colors duration-200" />
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="pl-10 pr-10 bg-slate-100 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:border-cyan-500 focus:ring-cyan-500/20 transition-all duration-200"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-lg text-slate-400 dark:text-slate-500 hover:text-cyan-500 dark:hover:text-cyan-400 hover:bg-slate-200 dark:hover:bg-slate-700/50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="flex items-start gap-3 p-4 text-sm text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-800/50 rounded-lg animate-fade-in-up">
                    <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    <span className="leading-relaxed">{error}</span>
                  </div>
                )}

                <Button 
                  type="submit" 
                  disabled={loading}
                  className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-600/70 disabled:cursor-not-allowed text-white font-semibold text-base py-6 h-auto rounded-xl transition-all duration-300 ease-out hover:-translate-y-0.5 hover:shadow-lg hover:shadow-cyan-500/30 active:translate-y-0 animate-fade-in-up delay-700 relative overflow-hidden"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      <span>Signing In...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In</span>
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                  {loading && (
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer"></div>
                  )}
                </Button>

                <div className="text-center text-sm text-slate-500 dark:text-slate-400 pt-2 animate-fade-in-up delay-800">
                  <p className="leading-relaxed">
                    Gunakan akun admin atau pengguna untuk akses ke dashboard. 
                    <span className="block mt-1">Sesi dikelola oleh Supabase Auth.</span>
                  </p>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Login