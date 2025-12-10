import React, { useState, useEffect } from 'react'
import { Link, useLocation, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Menu, X, ChevronDown, LogOut, Home, Users, Package, BarChart3, User } from 'lucide-react'

const AdminLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    // Set initial state based on screen size
    if (typeof window !== 'undefined') {
      return window.innerWidth >= 768
    }
    return true
  })
  const [productDropdownOpen, setProductDropdownOpen] = useState(false)
  const { user, signOut } = useAuth()
  const location = useLocation()

  // Handle sidebar state on resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setSidebarOpen(true)
      } else {
        setSidebarOpen(false)
      }
    }
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Close sidebar on mobile when clicking a link
  const handleLinkClick = () => {
    if (window.innerWidth < 768) {
      setSidebarOpen(false)
    }
  }

  const menuItems = [
    { path: '/admin', icon: Home, label: 'Dashboard', exact: true },
    { path: '/admin/customers', icon: Users, label: 'Pelanggan' },
    {
      type: 'dropdown',
      icon: Package,
      label: 'Produk',
      submenu: [
        { path: '/admin/packages', label: 'Manajemen Produk' },
        { path: '/admin/product-lab', label: 'Product Lab' }
      ]
    },
    { path: '/admin/recommendations', icon: BarChart3, label: 'Analitik' }
  ]

  const isActive = (path, exact = false) => {
    if (exact) return location.pathname === path
    return location.pathname.startsWith(path)
  }

  const isDropdownActive = (submenu) => submenu.some(item => location.pathname.startsWith(item.path))

  const handleLogout = async () => {
    await signOut()
  }

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      {/* Sidebar */}
      <aside className={
        `fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 border-r border-slate-800 shadow-xl transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] md:static md:translate-x-0 ` +
        (sidebarOpen ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0 md:translate-x-0 md:opacity-100')
      }>
        <div className="flex h-full flex-col">
          {/* Logo/Brand */}
          <div className="flex items-center gap-3 border-b border-slate-800 p-4 h-16 flex-shrink-0">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-white/5 border border-slate-800 text-white shadow-lg shadow-black/10 overflow-hidden">
              <img src="/logo.png" alt="Telvora logo" className="h-8 w-8 object-contain" loading="lazy" />
            </div>
            <div className="flex flex-col">
              <div className="text-sm font-bold text-white leading-tight">Telvora</div>
              <div className="text-xs text-slate-400 leading-tight">Admin Panel</div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex flex-1 flex-col p-4 space-y-1.5 overflow-y-auto overflow-x-hidden">
            {menuItems.map((item, idx) => {
              if (item.type === 'dropdown') {
                const active = isDropdownActive(item.submenu)
                return (
                  <div key={idx}>
                    <button
                      onClick={() => setProductDropdownOpen(!productDropdownOpen)}
                      className={`w-full flex items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] ${active ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}>
                      <div className="flex items-center gap-3 min-w-0">
                        <item.icon size={18} className="flex-shrink-0" />
                        <span className="truncate">{item.label}</span>
                      </div>
                      <ChevronDown size={16} className={`flex-shrink-0 transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${productDropdownOpen ? 'rotate-180' : 'rotate-0'}`} />
                    </button>

                    <div className={`mt-1.5 ml-9 flex flex-col gap-1 overflow-hidden transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${productDropdownOpen ? 'max-h-40 opacity-100' : 'max-h-0 opacity-0'}`}>
                      {item.submenu.map((sub, sidx) => (
                        <Link
                          key={sidx}
                          to={sub.path}
                          onClick={handleLinkClick}
                          className={`rounded-lg px-3 py-2 text-sm transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${isActive(sub.path) ? 'bg-cyan-500/20 text-cyan-400 font-semibold border border-cyan-500/30' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}>
                          {sub.label}
                        </Link>
                      ))}
                    </div>
                  </div>
                )
              }

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={handleLinkClick}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] ${isActive(item.path, item.exact) ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}>
                  <item.icon size={18} className="flex-shrink-0" />
                  <span className="truncate">{item.label}</span>
                </Link>
              )
            })}
          </nav>

          {/* Footer Actions */}
          <div className="border-t border-slate-800 p-3 flex flex-col gap-1.5 flex-shrink-0">
            <button 
              onClick={() => {
                handleLogout()
                handleLinkClick()
              }} 
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-300 hover:bg-red-500/20 hover:text-red-400 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
            >
              <LogOut size={18} className="flex-shrink-0" />
              <span className="truncate">Logout</span>
            </button>

            <Link 
              to="/" 
              onClick={handleLinkClick}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
            >
              <ChevronDown size={18} className="rotate-90 flex-shrink-0" />
              <span className="truncate">Ke Situs</span>
            </Link>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      <div 
        className={`fixed inset-0 bg-black/50 z-30 md:hidden transition-opacity duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${sidebarOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Main content area */}
      <div className="flex flex-1 flex-col min-w-0 md:ml-0">
        {/* Header */}
        <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-slate-800 bg-slate-900/95 backdrop-blur-sm px-4 md:px-6 h-16 flex-shrink-0 shadow-lg">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <button 
              onClick={() => setSidebarOpen(!sidebarOpen)} 
              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] flex-shrink-0 md:hidden active:scale-95"
            >
              {sidebarOpen ? <X size={18} className="transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]" /> : <Menu size={18} className="transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]" />}
            </button>
            <div className="min-w-0">
              <h1 className="text-base md:text-lg font-bold text-white tracking-tight">Panel Admin Telvora</h1>
              <p className="text-xs text-slate-400 hidden sm:block">Kelola produk, pelanggan, dan analitik Anda</p>
            </div>
          </div>

          <div className="flex items-center flex-shrink-0">
            <div className="flex items-center gap-3 pl-4 border-l border-slate-700/50">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 text-white shadow-md shadow-cyan-500/20 flex-shrink-0">
                <User size={18} />
              </div>
              <div className="hidden sm:block min-w-0 pr-2">
                <div className="text-sm font-semibold text-white leading-none mb-0.5 truncate max-w-[150px]">{user?.email?.split('@')[0] || 'Admin'}</div>
                <div className="text-xs text-slate-400 leading-none truncate">Administrator</div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto bg-slate-950">
          <div className="w-full h-full px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 max-w-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default AdminLayout