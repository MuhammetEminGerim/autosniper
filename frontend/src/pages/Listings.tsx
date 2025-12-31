import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { useCompareStore } from '../store/compareStore'
import './Listings.css'

interface Listing {
  id: number
  title: string
  price: number
  year: number | null
  brand: string | null
  city: string | null
  fuel_type: string | null
  transmission: string | null
  images: string[] | null
  source_url: string
  is_new: boolean
}

type SourceTab = 'all' | 'quick' | 'filtered'

const Listings = () => {
  const navigate = useNavigate()
  const { listings: compareListings, addToCompare, removeFromCompare, isInCompare } = useCompareStore()
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)
  const [favorites, setFavorites] = useState<Set<number>>(new Set())
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [activeTab, setActiveTab] = useState<SourceTab>('all')
  const [tabCounts, setTabCounts] = useState({ all: 0, quick: 0, filtered: 0 })
  const [filters, setFilters] = useState({
    brand: '',
    city: '',
    minPrice: '',
    maxPrice: ''
  })

  useEffect(() => {
    loadListings()
    loadFavorites()
    loadTabCounts()
  }, [page, activeTab])

  const loadListings = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '20',
        source: activeTab
      })
      
      if (filters.brand) params.append('brand', filters.brand)
      if (filters.city) params.append('city', filters.city)
      if (filters.minPrice) params.append('min_price', filters.minPrice)
      if (filters.maxPrice) params.append('max_price', filters.maxPrice)

      const response = await api.get(`/api/listings?${params}`)
      setListings(response.data.items || [])
      setTotalPages(Math.ceil((response.data.total || 0) / 20) || 1)
    } catch (error) {
      toast.error('İlanlar yüklenemedi')
    } finally {
      setLoading(false)
    }
  }

  const loadTabCounts = async () => {
    try {
      const [allRes, quickRes, filteredRes] = await Promise.all([
        api.get('/api/listings?page=1&page_size=1&source=all'),
        api.get('/api/listings?page=1&page_size=1&source=quick'),
        api.get('/api/listings?page=1&page_size=1&source=filtered')
      ])
      setTabCounts({
        all: allRes.data.total || 0,
        quick: quickRes.data.total || 0,
        filtered: filteredRes.data.total || 0
      })
    } catch (error) {
      console.error('Tab counts yüklenemedi')
    }
  }

  const handleTabChange = (tab: SourceTab) => {
    setActiveTab(tab)
    setPage(1)
  }

  const loadFavorites = async () => {
    try {
      const response = await api.get('/api/favorites')
      const favIds = new Set<number>(response.data.map((f: any) => f.id))
      setFavorites(favIds)
    } catch (error) {
      console.error('Favoriler yüklenemedi')
    }
  }

  const toggleFavorite = async (listingId: number) => {
    try {
      if (favorites.has(listingId)) {
        await api.delete(`/api/favorites/${listingId}`)
        setFavorites(prev => {
          const newSet = new Set(prev)
          newSet.delete(listingId)
          return newSet
        })
        toast.success('Favorilerden çıkarıldı')
      } else {
        await api.post(`/api/favorites/${listingId}`)
        setFavorites(prev => new Set([...prev, listingId]))
        toast.success('Favorilere eklendi')
      }
    } catch (error) {
      toast.error('İşlem başarısız')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Bu ilanı silmek istediğinize emin misiniz?')) return
    try {
      await api.delete(`/api/listings/${id}`)
      toast.success('İlan silindi')
      loadListings()
    } catch (error) {
      toast.error('İlan silinemedi')
    }
  }

  const getTabLabel = () => {
    switch (activeTab) {
      case 'quick': return 'Hızlı Tarama'
      case 'filtered': return 'Filtrelerimden'
      default: return 'Tüm'
    }
  }

  const handleDeleteAll = async () => {
    const label = getTabLabel()
    const count = activeTab === 'all' ? tabCounts.all : activeTab === 'quick' ? tabCounts.quick : tabCounts.filtered
    
    if (!confirm(`${label} sekmesindeki ${count} ilanı silmek istediğinize emin misiniz? Bu işlem geri alınamaz!`)) return
    
    try {
      await api.delete(`/api/listings?source=${activeTab}`)
      toast.success(`${label} ilanları silindi`)
      loadListings()
      loadTabCounts()
    } catch (error) {
      toast.error('İlanlar silinemedi')
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      maximumFractionDigits: 0,
    }).format(price)
  }

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    loadListings()
  }

  if (loading && listings.length === 0) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Yükleniyor...</p>
      </div>
    )
  }

  return (
    <div className="listings-page">
      <div className="page-header">
        <div>
          <h1>🚗 İlanlar</h1>
          <p>Taranan tüm ilanlar</p>
        </div>
        <div className="header-actions">
          {compareListings.length > 0 && (
            <button 
              onClick={() => navigate('/compare')} 
              className="btn btn-compare"
            >
              ⚖️ Karşılaştır ({compareListings.length})
            </button>
          )}
          <Link to="/search" className="btn btn-primary">
            🔍 Yeni Arama
          </Link>
          {listings.length > 0 && (
            <button onClick={handleDeleteAll} className="btn btn-danger">
              🗑️ {activeTab === 'all' ? 'Tümünü' : getTabLabel() + ' İlanlarını'} Sil
            </button>
          )}
        </div>
      </div>

      {/* Sekmeler */}
      <div className="tabs-container">
        <button 
          className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => handleTabChange('all')}
        >
          📋 Tümü <span className="tab-count">{tabCounts.all}</span>
        </button>
        <button 
          className={`tab-btn ${activeTab === 'quick' ? 'active' : ''}`}
          onClick={() => handleTabChange('quick')}
        >
          ⚡ Hızlı Tarama <span className="tab-count">{tabCounts.quick}</span>
        </button>
        <button 
          className={`tab-btn ${activeTab === 'filtered' ? 'active' : ''}`}
          onClick={() => handleTabChange('filtered')}
        >
          ⚙️ Filtrelerimden <span className="tab-count">{tabCounts.filtered}</span>
        </button>
      </div>

      {/* Filters */}
      <form onSubmit={handleFilterSubmit} className="filter-bar">
        <input
          type="text"
          placeholder="Marka..."
          value={filters.brand}
          onChange={(e) => setFilters({...filters, brand: e.target.value})}
        />
        <input
          type="text"
          placeholder="Şehir..."
          value={filters.city}
          onChange={(e) => setFilters({...filters, city: e.target.value})}
        />
        <input
          type="number"
          placeholder="Min Fiyat"
          value={filters.minPrice}
          onChange={(e) => setFilters({...filters, minPrice: e.target.value})}
        />
        <input
          type="number"
          placeholder="Max Fiyat"
          value={filters.maxPrice}
          onChange={(e) => setFilters({...filters, maxPrice: e.target.value})}
        />
        <button type="submit" className="btn btn-secondary">
          Filtrele
        </button>
      </form>

      {listings.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>İlan bulunamadı</h3>
          <p>Henüz ilan taranmamış veya filtrelere uygun ilan yok</p>
          <Link to="/search" className="btn btn-primary">
            İlan Ara
          </Link>
        </div>
      ) : (
        <>
          <div className="listings-grid">
            {listings.map((listing, index) => (
              <div 
                key={listing.id} 
                className={`listing-card ${listing.is_new ? 'new' : ''}`}
                style={{ animationDelay: `${index * 0.03}s` }}
              >
                {listing.is_new && <span className="new-badge">YENİ</span>}
                
                <button 
                  className={`favorite-btn ${favorites.has(listing.id) ? 'active' : ''}`}
                  onClick={() => toggleFavorite(listing.id)}
                  title={favorites.has(listing.id) ? 'Favorilerden Çıkar' : 'Favorilere Ekle'}
                >
                  {favorites.has(listing.id) ? '❤️' : '🤍'}
                </button>

                <button 
                  className="delete-btn"
                  onClick={() => handleDelete(listing.id)}
                  title="Sil"
                >
                  ✕
                </button>

                <button 
                  className={`compare-btn ${isInCompare(listing.id) ? 'active' : ''}`}
                  onClick={() => {
                    if (isInCompare(listing.id)) {
                      removeFromCompare(listing.id)
                      toast.success('Karşılaştırmadan çıkarıldı')
                    } else {
                      const success = addToCompare(listing as any)
                      if (success) {
                        toast.success('Karşılaştırmaya eklendi')
                      } else {
                        toast.error('En fazla 3 ilan karşılaştırılabilir')
                      }
                    }
                  }}
                  title={isInCompare(listing.id) ? 'Karşılaştırmadan Çıkar' : 'Karşılaştır'}
                >
                  ⚖️
                </button>

                <Link to={`/listings/${listing.id}`} className="card-link">
                  <div className="card-image">
                    {listing.images && listing.images.length > 0 ? (
                      <img 
                        src={listing.images[0]} 
                        alt={listing.title}
                        loading="lazy"
                        decoding="async"
                        onError={(e) => {
                          e.currentTarget.src = 'https://via.placeholder.com/400x300?text=Resim+Yok'
                        }}
                      />
                    ) : (
                      <div className="no-image">
                        <span>📷</span>
                      </div>
                    )}
                  </div>

                  <div className="card-content">
                    <h3 className="card-title">{listing.title}</h3>
                    <p className="card-price">{formatPrice(listing.price)}</p>
                    
                    <div className="card-details">
                      {listing.year && <span>📅 {listing.year}</span>}
                      {listing.city && <span>📍 {listing.city}</span>}
                      {listing.fuel_type && <span>⛽ {listing.fuel_type}</span>}
                      {listing.transmission && <span>⚙️ {listing.transmission}</span>}
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn btn-secondary"
              >
                ← Önceki
              </button>
              <span className="page-info">
                Sayfa {page} / {totalPages}
              </span>
              <button 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn btn-secondary"
              >
                Sonraki →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Listings
