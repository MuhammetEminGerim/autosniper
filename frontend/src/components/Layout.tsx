import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './Layout.css'

interface LayoutProps {
  children: React.ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const isActive = (path: string) => location.pathname === path

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/search', label: 'Arama', icon: '🔍' },
    { path: '/my-filters', label: 'Filtrelerim', icon: '🎯' },
    { path: '/listings', label: 'İlanlar', icon: '🚗' },
    { path: '/favorites', label: 'Favoriler', icon: '❤️' },
    { path: '/compare', label: 'Karşılaştır', icon: '⚖️' },
    { path: '/statistics', label: 'İstatistikler', icon: '📊' },
    { path: '/settings', label: 'Ayarlar', icon: '⚙️' },
  ]

  // Admin kullanıcılar için admin paneli ekle
  if (user?.is_admin) {
    navItems.push({ path: '/admin', label: 'Admin Panel', icon: '🛡️' })
  }

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <Link to="/" className="logo">
            <span className="logo-icon">🎯</span>
            <span className="logo-text">AutoSniper</span>
          </Link>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">
              {user?.email?.charAt(0).toUpperCase()}
            </div>
            <div className="user-details">
              <span className="user-email">{user?.email}</span>
              <span className="user-role">
                {user?.is_admin ? '🛡️ Admin' : 'Üye'}
              </span>
            </div>
          </div>
          <button onClick={logout} className="logout-btn" title="Çıkış Yap">
            🚪
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <div className="content-wrapper">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
