import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'
import UsageStats from '../components/UsageStats'
import './Dashboard.css'

interface Stats {
  totalListings: number
  totalFilters: number
  totalFavorites: number
  newToday: number
}

interface RecentListing {
  id: number
  title: string
  price: number
  city: string | null
  images: string[] | null
}

interface SchedulerInfo {
  total_filters: number
  active_schedulers: number
  total_scans: number
  total_new_listings: number
  next_scan_at: string | null
}

const Dashboard = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [quickSearching, setQuickSearching] = useState(false)
  const [stats, setStats] = useState<Stats>({
    totalListings: 0,
    totalFilters: 0,
    totalFavorites: 0,
    newToday: 0
  })
  const [schedulerInfo, setSchedulerInfo] = useState<SchedulerInfo | null>(null)
  const [recentListings, setRecentListings] = useState<RecentListing[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [listingsRes, filtersRes, favoritesRes, schedulerRes] = await Promise.all([
        api.get('/api/listings?page=1&page_size=6'),
        api.get('/api/filters'),
        api.get('/api/favorites'),
        api.get('/api/filters/scheduler/all-status').catch(() => ({ data: null }))
      ])

      setStats({
        totalListings: listingsRes.data.total || listingsRes.data.items?.length || 0,
        totalFilters: filtersRes.data.length || 0,
        totalFavorites: favoritesRes.data.length || 0,
        newToday: listingsRes.data.items?.filter((l: any) => l.is_new)?.length || 0
      })

      if (schedulerRes.data) {
        setSchedulerInfo(schedulerRes.data)
      }

      setRecentListings(listingsRes.data.items?.slice(0, 6) || [])
    } catch (error) {
      console.error('Dashboard veri yüklenemedi:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatTimeRemaining = (nextScanAt: string | null): string => {
    if (!nextScanAt) return '-'
    const next = new Date(nextScanAt)
    const now = new Date()
    const diff = next.getTime() - now.getTime()

    if (diff <= 0) return 'Şimdi'

    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)

    if (hours > 0) {
      return `${hours}s ${minutes % 60}dk`
    }
    return `${minutes}dk`
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      maximumFractionDigits: 0,
    }).format(price)
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Günaydın'
    if (hour < 18) return 'İyi günler'
    return 'İyi akşamlar'
  }

  const handleQuickSearch = async () => {
    setQuickSearching(true)
    toast.loading('Son ilanlar taranıyor...', { id: 'quick-search' })

    try {
      const response = await api.post('/api/test/scrape', {})
      toast.dismiss('quick-search')
      toast.success(`✅ ${response.data.new_listings_added} yeni ilan eklendi!`, { duration: 5000 })
      navigate('/listings')
    } catch (error: any) {
      toast.dismiss('quick-search')
      toast.error(error.response?.data?.detail || 'Tarama başarısız')
    } finally {
      setQuickSearching(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Yükleniyor...</p>
      </div>
    )
  }

  return (
    <div className="dashboard-page">
      {/* Welcome Section */}
      <div className="welcome-section">
        <div className="welcome-content">
          <h1>{getGreeting()}, {user?.email?.split('@')[0]}! 👋</h1>
          <p>İkinci el araç fırsatlarını takip edin</p>
        </div>
        <div className="welcome-actions">
          <button
            onClick={handleQuickSearch}
            className="btn btn-quick"
            disabled={quickSearching}
          >
            {quickSearching ? '⏳ Taranıyor...' : '⚡ Hızlı Tarama'}
          </button>
          <Link to="/search" className="btn btn-white">
            🔍 Detaylı Arama
          </Link>
        </div>
      </div>

      {/* Usage Stats Widget */}
      <UsageStats />

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon blue">🚗</div>
          <div className="stat-content">
            <span className="stat-value">{stats.totalListings}</span>
            <span className="stat-label">Toplam İlan</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon purple">⚙️</div>
          <div className="stat-content">
            <span className="stat-value">{stats.totalFilters}</span>
            <span className="stat-label">Aktif Filtre</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon red">❤️</div>
          <div className="stat-content">
            <span className="stat-value">{stats.totalFavorites}</span>
            <span className="stat-label">Favori</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green">✨</div>
          <div className="stat-content">
            <span className="stat-value">{stats.newToday}</span>
            <span className="stat-label">Yeni İlan</span>
          </div>
        </div>
      </div>

      {/* Scheduler Status */}
      {schedulerInfo && schedulerInfo.active_schedulers > 0 && (
        <div className="scheduler-widget">
          <div className="scheduler-widget-header">
            <h2>⏰ Otomatik Tarama</h2>
            <Link to="/my-filters" className="manage-link">Yönet →</Link>
          </div>
          <div className="scheduler-stats">
            <div className="scheduler-stat-item">
              <span className="stat-icon-sm">🔄</span>
              <div className="stat-info">
                <span className="stat-num">{schedulerInfo.active_schedulers}</span>
                <span className="stat-text">Aktif Tarama</span>
              </div>
            </div>
            <div className="scheduler-stat-item">
              <span className="stat-icon-sm">📊</span>
              <div className="stat-info">
                <span className="stat-num">{schedulerInfo.total_scans}</span>
                <span className="stat-text">Toplam Tarama</span>
              </div>
            </div>
            <div className="scheduler-stat-item">
              <span className="stat-icon-sm">🆕</span>
              <div className="stat-info">
                <span className="stat-num">{schedulerInfo.total_new_listings}</span>
                <span className="stat-text">Bulunan İlan</span>
              </div>
            </div>
            <div className="scheduler-stat-item next-scan">
              <span className="stat-icon-sm">⏭️</span>
              <div className="stat-info">
                <span className="stat-num">{formatTimeRemaining(schedulerInfo.next_scan_at)}</span>
                <span className="stat-text">Sonraki Tarama</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Hızlı İşlemler</h2>
        <div className="actions-grid">
          <Link to="/search" className="action-card">
            <span className="action-icon">🔍</span>
            <span className="action-title">İlan Ara</span>
            <span className="action-desc">arabam.com'dan ilan tara</span>
          </Link>
          <Link to="/my-filters" className="action-card">
            <span className="action-icon">➕</span>
            <span className="action-title">Filtre Oluştur</span>
            <span className="action-desc">Arama kriterlerini kaydet</span>
          </Link>
          <Link to="/listings" className="action-card">
            <span className="action-icon">📋</span>
            <span className="action-title">Tüm İlanlar</span>
            <span className="action-desc">Kayıtlı ilanları görüntüle</span>
          </Link>
          <Link to="/favorites" className="action-card">
            <span className="action-icon">❤️</span>
            <span className="action-title">Favoriler</span>
            <span className="action-desc">Beğendiğin ilanları gör</span>
          </Link>
        </div>
      </div>

      {/* Recent Listings */}
      {recentListings.length > 0 && (
        <div className="recent-section">
          <div className="section-header">
            <h2>Son Eklenen İlanlar</h2>
            <Link to="/listings" className="view-all">
              Tümünü Gör →
            </Link>
          </div>
          <div className="recent-grid">
            {recentListings.map((listing, index) => (
              <Link
                key={listing.id}
                to={`/listings/${listing.id}`}
                className="recent-card"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="recent-image">
                  {listing.images && listing.images.length > 0 ? (
                    <img
                      src={listing.images[0]}
                      alt={listing.title}
                      loading="lazy"
                      decoding="async"
                    />
                  ) : (
                    <div className="no-image">📷</div>
                  )}
                </div>
                <div className="recent-content">
                  <h4>{listing.title}</h4>
                  <p className="recent-price">{formatPrice(listing.price)}</p>
                  {listing.city && <span className="recent-city">📍 {listing.city}</span>}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
