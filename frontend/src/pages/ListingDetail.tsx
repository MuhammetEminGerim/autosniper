import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import CarDamageDiagram from '../components/CarDamageDiagram'
import './ListingDetail.css'

interface DamageInfo {
  original?: string[]
  local_painted?: string[]
  painted?: string[]
  changed?: string[]
  unknown?: string[]
  tramer_amount?: string
}

interface Listing {
  id: number
  source_url: string
  title: string
  price: number
  year?: number
  brand?: string
  model?: string
  fuel_type?: string
  transmission?: string
  mileage?: number
  city?: string
  description?: string
  images?: string[]
  damage_info?: DamageInfo
  is_new: boolean
  scraped_at: string
}

const ListingDetail = () => {
  const { id } = useParams<{ id: string }>()
  const [listing, setListing] = useState<Listing | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeImageIndex, setActiveImageIndex] = useState(0)

  useEffect(() => {
    if (id) {
      loadListing()
    }
  }, [id])

  const loadListing = async () => {
    try {
      const response = await api.get(`/api/listings/${id}`)
      setListing(response.data)
    } catch (error) {
      toast.error('İlan yüklenemedi')
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      maximumFractionDigits: 0,
    }).format(price)
  }

  // Hasar özeti hesapla
  const getDamageSummary = (info: DamageInfo) => {
    const total = (info.original?.length || 0) + 
                  (info.local_painted?.length || 0) + 
                  (info.painted?.length || 0) + 
                  (info.changed?.length || 0) + 
                  (info.unknown?.length || 0)
    const originalCount = info.original?.length || 0
    const problematicCount = (info.painted?.length || 0) + (info.changed?.length || 0)
    
    if (problematicCount === 0 && originalCount === total) return { text: 'Tamamen Orijinal', type: 'excellent' }
    if (problematicCount <= 2) return { text: 'İyi Durumda', type: 'good' }
    if (problematicCount <= 5) return { text: 'Orta Durumda', type: 'medium' }
    return { text: 'Dikkat Edilmeli', type: 'warning' }
  }

  if (loading) {
    return (
      <div className="detail-loading">
        <div className="loading-spinner"></div>
        <span>İlan yükleniyor...</span>
      </div>
    )
  }

  if (!listing) {
    return (
      <div className="error-state">
        <div className="error-icon">🚫</div>
        <h2>İlan Bulunamadı</h2>
        <p>Aradığınız ilan mevcut değil veya kaldırılmış olabilir.</p>
        <Link to="/listings" className="btn-back">
          ← İlanlara Dön
        </Link>
      </div>
    )
  }

  const damageSummary = listing.damage_info ? getDamageSummary(listing.damage_info) : null

  return (
    <div className="listing-detail-page">
      {/* Üst Bar */}
      <div className="detail-topbar">
        <Link to="/listings" className="back-link">
          <span className="back-icon">←</span>
          <span>İlanlara Dön</span>
        </Link>
        <span className="listing-id">İlan #{listing.id}</span>
      </div>

      {/* Ana İçerik - Kompakt */}
      <div className="detail-compact">
        {/* Üst Kısım: Fotoğraf + Bilgiler yan yana */}
        <div className="compact-top">
          {/* Sol: Küçük Fotoğraf */}
          <div className="compact-image">
            {listing.is_new && <span className="new-badge">YENİ</span>}
            {listing.images && listing.images.length > 0 ? (
              <img
                src={listing.images[activeImageIndex]}
                alt={listing.title}
                className="main-image"
                onError={(e) => {
                  e.currentTarget.src = 'https://via.placeholder.com/300x200?text=Araç'
                }}
              />
            ) : (
              <div className="image-placeholder">
                <span>🚗</span>
              </div>
            )}
            {listing.images && listing.images.length > 1 && (
              <div className="mini-thumbnails">
                {listing.images.slice(0, 4).map((img, idx) => (
                  <button
                    key={idx}
                    className={`mini-thumb ${idx === activeImageIndex ? 'active' : ''}`}
                    onClick={() => setActiveImageIndex(idx)}
                  >
                    <img src={img} alt="" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Orta: Başlık + Özellikler */}
          <div className="compact-info">
            <h1 className="listing-title">{listing.title}</h1>
            <div className="price-tag">{formatPrice(listing.price)}</div>
            
            <div className="specs-inline">
              {listing.year && <span className="spec-pill">📅 {listing.year}</span>}
              {listing.mileage && <span className="spec-pill">🛣️ {listing.mileage.toLocaleString('tr-TR')} km</span>}
              {listing.fuel_type && <span className="spec-pill">⛽ {listing.fuel_type}</span>}
              {listing.transmission && <span className="spec-pill">⚙️ {listing.transmission}</span>}
              {listing.city && <span className="spec-pill">📍 {listing.city}</span>}
            </div>

            {/* Açıklama - Kısa */}
            {listing.description && (
              <p className="compact-description">{listing.description.slice(0, 150)}{listing.description.length > 150 ? '...' : ''}</p>
            )}

            <a
              href={listing.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-goto"
            >
              İlana Git ↗
            </a>
          </div>

          {/* Sağ: Tramer Özeti */}
          <div className="compact-tramer">
            <div className="tramer-box">
              <div className="tramer-header">🔍 Ekspertiz</div>
              {listing.damage_info ? (
                <>
                  {damageSummary && (
                    <div className={`tramer-status ${damageSummary.type}`}>{damageSummary.text}</div>
                  )}
                  {listing.damage_info.tramer_amount && (
                    <div className="tramer-amount">
                      <span className="label">Tramer:</span>
                      <span className="value">{listing.damage_info.tramer_amount}</span>
                    </div>
                  )}
                  <div className="tramer-counts">
                    {listing.damage_info.original && listing.damage_info.original.length > 0 && (
                      <span className="count-item original">🟢 {listing.damage_info.original.length} Orijinal</span>
                    )}
                    {listing.damage_info.painted && listing.damage_info.painted.length > 0 && (
                      <span className="count-item painted">🟡 {listing.damage_info.painted.length} Boyalı</span>
                    )}
                    {listing.damage_info.changed && listing.damage_info.changed.length > 0 && (
                      <span className="count-item changed">🔴 {listing.damage_info.changed.length} Değişen</span>
                    )}
                  </div>
                </>
              ) : (
                <div className="no-damage-compact">
                  <span>🚛 Hasar bilgisi yok</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Boya-Değişen Detay Bölümü */}
      {listing.damage_info ? (
        <div className="damage-detail-section">
          <h2 className="section-title">
            <span className="title-icon">🔍</span>
            Boya-Değişen ve Tramer Raporu
          </h2>
          
          <div className="damage-layout">
            {/* Araç Şeması */}
            <div className="diagram-card">
              <CarDamageDiagram damageInfo={listing.damage_info} />
            </div>

            {/* Parça Listesi */}
            <div className="parts-card">
              <div className="parts-grid">
                {listing.damage_info.original && listing.damage_info.original.length > 0 && (
                  <div className="parts-category">
                    <div className="category-header original">
                      <span className="category-dot"></span>
                      <span className="category-name">Orijinal</span>
                      <span className="category-count">{listing.damage_info.original.length}</span>
                    </div>
                    <div className="parts-list">
                      {listing.damage_info.original.map((part, i) => (
                        <span key={i} className="part-tag original">{part}</span>
                      ))}
                    </div>
                  </div>
                )}

                {listing.damage_info.local_painted && listing.damage_info.local_painted.length > 0 && (
                  <div className="parts-category">
                    <div className="category-header local-painted">
                      <span className="category-dot"></span>
                      <span className="category-name">Lokal Boyalı</span>
                      <span className="category-count">{listing.damage_info.local_painted.length}</span>
                    </div>
                    <div className="parts-list">
                      {listing.damage_info.local_painted.map((part, i) => (
                        <span key={i} className="part-tag local-painted">{part}</span>
                      ))}
                    </div>
                  </div>
                )}

                {listing.damage_info.painted && listing.damage_info.painted.length > 0 && (
                  <div className="parts-category">
                    <div className="category-header painted">
                      <span className="category-dot"></span>
                      <span className="category-name">Boyalı</span>
                      <span className="category-count">{listing.damage_info.painted.length}</span>
                    </div>
                    <div className="parts-list">
                      {listing.damage_info.painted.map((part, i) => (
                        <span key={i} className="part-tag painted">{part}</span>
                      ))}
                    </div>
                  </div>
                )}

                {listing.damage_info.changed && listing.damage_info.changed.length > 0 && (
                  <div className="parts-category">
                    <div className="category-header changed">
                      <span className="category-dot"></span>
                      <span className="category-name">Değişmiş</span>
                      <span className="category-count">{listing.damage_info.changed.length}</span>
                    </div>
                    <div className="parts-list">
                      {listing.damage_info.changed.map((part, i) => (
                        <span key={i} className="part-tag changed">{part}</span>
                      ))}
                    </div>
                  </div>
                )}

                {listing.damage_info.unknown && listing.damage_info.unknown.length > 0 && (
                  <div className="parts-category">
                    <div className="category-header unknown">
                      <span className="category-dot"></span>
                      <span className="category-name">Belirtilmemiş</span>
                      <span className="category-count">{listing.damage_info.unknown.length}</span>
                    </div>
                    <div className="parts-list">
                      {listing.damage_info.unknown.map((part, i) => (
                        <span key={i} className="part-tag unknown">{part}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Tramer Bilgisi */}
              {listing.damage_info.tramer_amount && (
                <div className="tramer-card">
                  <span className="tramer-icon">💰</span>
                  <div className="tramer-content">
                    <span className="tramer-label">Tramer Tutarı</span>
                    <span className="tramer-value">{listing.damage_info.tramer_amount}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="damage-detail-section no-damage">
          <h2 className="section-title">
            <span className="title-icon">🔍</span>
            Boya-Değişen ve Tramer Raporu
          </h2>
          <div className="no-damage-message">
            <span className="no-damage-icon">🚛</span>
            <p>Bu araç için hasar bilgisi bulunmuyor.</p>
            <span className="no-damage-hint">Ticari araçlarda (kamyon, minibüs vb.) hasar diyagramı genellikle sunulmaz.</span>
          </div>
        </div>
      )}

      {/* Açıklama */}
      {listing.description && (
        <div className="description-section">
          <h2 className="section-title">
            <span className="title-icon">📝</span>
            Açıklama
          </h2>
          <p className="description-text">{listing.description}</p>
        </div>
      )}
    </div>
  )
}

export default ListingDetail
