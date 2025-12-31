import { useState, useEffect } from 'react'
import api from '../services/api'
import './Statistics.css'

interface MarketStats {
  total_listings: number
  avg_price: number
  min_price: number
  max_price: number
  avg_mileage: number
  avg_year: number
  price_change_7d: number
  new_listings_24h: number
}

interface BrandStats {
  brand: string
  count: number
  avg_price: number
  percentage: number
}

interface CityStats {
  city: string
  count: number
  avg_price: number
  percentage: number
}

interface PriceRange {
  range: string
  count: number
  percentage: number
}

const Statistics = () => {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<MarketStats | null>(null)
  const [brandStats, setBrandStats] = useState<BrandStats[]>([])
  const [cityStats, setCityStats] = useState<CityStats[]>([])
  const [priceRanges, setPriceRanges] = useState<PriceRange[]>([])

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      const response = await api.get('/api/listings/statistics')
      const data = response.data
      
      setStats(data.market)
      setBrandStats(data.brands || [])
      setCityStats(data.cities || [])
      setPriceRanges(data.price_ranges || [])
    } catch (error) {
      console.error('İstatistikler yüklenemedi:', error)
      // Boş veri göster
      setStats({
        total_listings: 0,
        avg_price: 0,
        min_price: 0,
        max_price: 0,
        avg_mileage: 0,
        avg_year: 0,
        price_change_7d: 0,
        new_listings_24h: 0
      })
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price: number) => {
    return price.toLocaleString('tr-TR', { maximumFractionDigits: 0 }) + ' TL'
  }

  const formatNumber = (num: number) => {
    return num.toLocaleString('tr-TR', { maximumFractionDigits: 0 })
  }

  if (loading) {
    return (
      <div className="statistics-page">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>İstatistikler yükleniyor...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="statistics-page animate-fade-in">
      <header className="page-header">
        <div>
          <h1>📊 Piyasa İstatistikleri</h1>
          <p>İlan verilerinize dayalı piyasa analizi</p>
        </div>
      </header>

      {/* Overview Cards */}
      <div className="stats-overview">
        <div className="overview-card">
          <div className="overview-icon">🚗</div>
          <div className="overview-content">
            <span className="overview-value">{formatNumber(stats?.total_listings || 0)}</span>
            <span className="overview-label">Toplam İlan</span>
          </div>
        </div>

        <div className="overview-card">
          <div className="overview-icon">💰</div>
          <div className="overview-content">
            <span className="overview-value">{formatPrice(stats?.avg_price || 0)}</span>
            <span className="overview-label">Ortalama Fiyat</span>
          </div>
        </div>

        <div className="overview-card">
          <div className="overview-icon">📅</div>
          <div className="overview-content">
            <span className="overview-value">{Math.round(stats?.avg_year || 0)}</span>
            <span className="overview-label">Ortalama Yıl</span>
          </div>
        </div>

        <div className="overview-card">
          <div className="overview-icon">🛣️</div>
          <div className="overview-content">
            <span className="overview-value">{formatNumber(stats?.avg_mileage || 0)} km</span>
            <span className="overview-label">Ortalama KM</span>
          </div>
        </div>

        <div className="overview-card highlight">
          <div className="overview-icon">🆕</div>
          <div className="overview-content">
            <span className="overview-value">+{stats?.new_listings_24h || 0}</span>
            <span className="overview-label">Son 24 Saat</span>
          </div>
        </div>

        <div className="overview-card">
          <div className="overview-icon">{(stats?.price_change_7d || 0) >= 0 ? '📈' : '📉'}</div>
          <div className="overview-content">
            <span className={`overview-value ${(stats?.price_change_7d || 0) >= 0 ? 'up' : 'down'}`}>
              {(stats?.price_change_7d || 0) >= 0 ? '+' : ''}{(stats?.price_change_7d || 0).toFixed(1)}%
            </span>
            <span className="overview-label">7 Günlük Değişim</span>
          </div>
        </div>
      </div>

      {/* Price Range */}
      <div className="stats-section">
        <div className="section-header">
          <h2>💵 Fiyat Aralığı</h2>
        </div>
        <div className="price-range-card">
          <div className="price-range-item">
            <span className="range-label">En Düşük</span>
            <span className="range-value min">{formatPrice(stats?.min_price || 0)}</span>
          </div>
          <div className="price-range-bar">
            <div className="bar-track">
              <div className="bar-fill"></div>
            </div>
          </div>
          <div className="price-range-item">
            <span className="range-label">En Yüksek</span>
            <span className="range-value max">{formatPrice(stats?.max_price || 0)}</span>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        {/* Brand Distribution */}
        <div className="stats-section">
          <div className="section-header">
            <h2>🏷️ Marka Dağılımı</h2>
          </div>
          <div className="distribution-list">
            {brandStats.length > 0 ? (
              brandStats.slice(0, 10).map((brand, index) => (
                <div key={brand.brand} className="distribution-item">
                  <div className="item-rank">#{index + 1}</div>
                  <div className="item-info">
                    <span className="item-name">{brand.brand}</span>
                    <span className="item-meta">{brand.count} ilan • Ort. {formatPrice(brand.avg_price)}</span>
                  </div>
                  <div className="item-bar">
                    <div 
                      className="bar-fill" 
                      style={{ width: `${brand.percentage}%` }}
                    ></div>
                  </div>
                  <span className="item-percentage">{brand.percentage.toFixed(1)}%</span>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <span>📭</span>
                <p>Henüz veri yok</p>
              </div>
            )}
          </div>
        </div>

        {/* City Distribution */}
        <div className="stats-section">
          <div className="section-header">
            <h2>📍 Şehir Dağılımı</h2>
          </div>
          <div className="distribution-list">
            {cityStats.length > 0 ? (
              cityStats.slice(0, 10).map((city, index) => (
                <div key={city.city} className="distribution-item">
                  <div className="item-rank">#{index + 1}</div>
                  <div className="item-info">
                    <span className="item-name">{city.city}</span>
                    <span className="item-meta">{city.count} ilan • Ort. {formatPrice(city.avg_price)}</span>
                  </div>
                  <div className="item-bar">
                    <div 
                      className="bar-fill city" 
                      style={{ width: `${city.percentage}%` }}
                    ></div>
                  </div>
                  <span className="item-percentage">{city.percentage.toFixed(1)}%</span>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <span>📭</span>
                <p>Henüz veri yok</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Price Distribution */}
      <div className="stats-section full-width">
        <div className="section-header">
          <h2>📊 Fiyat Dağılımı</h2>
        </div>
        <div className="price-distribution">
          {priceRanges.length > 0 ? (
            priceRanges.map((range) => (
              <div key={range.range} className="price-bar-item">
                <div className="price-bar-container">
                  <div 
                    className="price-bar" 
                    style={{ height: `${Math.max(range.percentage * 2, 10)}%` }}
                  >
                    <span className="bar-count">{range.count}</span>
                  </div>
                </div>
                <span className="price-label">{range.range}</span>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <span>📭</span>
              <p>Henüz veri yok</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Statistics

