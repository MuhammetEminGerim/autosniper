import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import './Favorites.css'

interface PriceChange {
  original_price: number | null
  current_price: number
  difference: number
  percentage: number
  direction: 'up' | 'down' | 'same'
}

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
  price_change?: PriceChange | null
  price_history?: Array<{ price: number; date: string; old_price?: number }>
}

const Favorites = () => {
  const [favorites, setFavorites] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadFavorites()
  }, [])

  const loadFavorites = async () => {
    try {
      const response = await api.get('/api/favorites')
      setFavorites(response.data)
    } catch (error) {
      toast.error('Favoriler yüklenemedi')
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (listingId: number) => {
    try {
      await api.delete(`/api/favorites/${listingId}`)
      toast.success('Favorilerden çıkarıldı')
      setFavorites(favorites.filter(f => f.id !== listingId))
    } catch (error) {
      toast.error('İşlem başarısız')
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      maximumFractionDigits: 0,
    }).format(price)
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
    <div className="favorites-page">
      <div className="page-header">
        <div>
          <h1>❤️ Favorilerim</h1>
          <p>{favorites.length} ilan kayıtlı</p>
        </div>
      </div>

      {favorites.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💔</div>
          <h3>Favori ilanınız yok</h3>
          <p>Beğendiğiniz ilanları favorilere ekleyin</p>
          <Link to="/listings" className="btn btn-primary">
            İlanlara Git
          </Link>
        </div>
      ) : (
        <div className="favorites-grid">
          {favorites.map((listing, index) => (
            <div 
              key={listing.id} 
              className="favorite-card"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <button 
                className="remove-btn"
                onClick={() => handleRemove(listing.id)}
                title="Favorilerden Çıkar"
              >
                ✕
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
                      <p>Resim Yok</p>
                    </div>
                  )}
                </div>

                <div className="card-content">
                  <h3 className="card-title">{listing.title}</h3>
                  <div className="price-section">
                    <p className="card-price">{formatPrice(listing.price)}</p>
                    {listing.price_change && listing.price_change.direction !== 'same' && (
                      <div className={`price-change ${listing.price_change.direction}`}>
                        {listing.price_change.direction === 'down' ? (
                          <>
                            <span className="change-icon">📉</span>
                            <span className="change-text">
                              {formatPrice(Math.abs(listing.price_change.difference))} düştü
                            </span>
                            <span className="change-percent">
                              ({listing.price_change.percentage}%)
                            </span>
                          </>
                        ) : (
                          <>
                            <span className="change-icon">📈</span>
                            <span className="change-text">
                              {formatPrice(listing.price_change.difference)} arttı
                            </span>
                            <span className="change-percent">
                              (+{listing.price_change.percentage}%)
                            </span>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="card-details">
                    {listing.year && (
                      <span className="detail-tag">
                        📅 {listing.year}
                      </span>
                    )}
                    {listing.city && (
                      <span className="detail-tag">
                        📍 {listing.city}
                      </span>
                    )}
                    {listing.fuel_type && (
                      <span className="detail-tag">
                        ⛽ {listing.fuel_type}
                      </span>
                    )}
                    {listing.transmission && (
                      <span className="detail-tag">
                        ⚙️ {listing.transmission}
                      </span>
                    )}
                  </div>
                </div>
              </Link>

              <div className="card-actions">
                <a 
                  href={listing.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn btn-secondary btn-sm"
                >
                  🔗 Orijinal İlan
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Favorites

