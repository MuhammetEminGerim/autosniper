import { Link } from 'react-router-dom'
import { useCompareStore } from '../store/compareStore'
import './Compare.css'

const Compare = () => {
  const { listings, removeFromCompare, clearCompare } = useCompareStore()

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      maximumFractionDigits: 0,
    }).format(price)
  }

  const formatMileage = (mileage: number | null) => {
    if (!mileage) return '-'
    return `${mileage.toLocaleString('tr-TR')} km`
  }

  // En düşük fiyatı bul
  const lowestPrice = Math.min(...listings.map(l => l.price))

  // Karşılaştırma satırları
  const comparisonRows = [
    { label: 'Fiyat', key: 'price', format: formatPrice, highlight: 'lowest' },
    { label: 'Yıl', key: 'year', format: (v: any) => v || '-' },
    { label: 'Marka', key: 'brand', format: (v: any) => v || '-' },
    { label: 'Model', key: 'model', format: (v: any) => v || '-' },
    { label: 'Kilometre', key: 'mileage', format: formatMileage, highlight: 'lowest' },
    { label: 'Yakıt', key: 'fuel_type', format: (v: any) => v || '-' },
    { label: 'Vites', key: 'transmission', format: (v: any) => v || '-' },
    { label: 'Şehir', key: 'city', format: (v: any) => v || '-' },
  ]

  if (listings.length === 0) {
    return (
      <div className="compare-page">
        <div className="page-header">
          <h1>⚖️ İlan Karşılaştırma</h1>
          <p>Karşılaştırmak için ilan seçin</p>
        </div>

        <div className="empty-state">
          <div className="empty-icon">⚖️</div>
          <h3>Karşılaştırılacak ilan yok</h3>
          <p>İlanlar sayfasından karşılaştırmak istediğiniz ilanları seçin</p>
          <Link to="/listings" className="btn btn-primary">
            İlanlara Git
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="compare-page">
      <div className="page-header">
        <div>
          <h1>⚖️ İlan Karşılaştırma</h1>
          <p>{listings.length} ilan karşılaştırılıyor</p>
        </div>
        <div className="header-actions">
          <Link to="/listings" className="btn btn-secondary">
            + İlan Ekle
          </Link>
          <button onClick={clearCompare} className="btn btn-danger">
            🗑️ Temizle
          </button>
        </div>
      </div>

      <div className="compare-container">
        {/* Header Row - Images */}
        <div className="compare-header">
          <div className="compare-label-cell"></div>
          {listings.map((listing) => (
            <div key={listing.id} className="compare-header-cell">
              <button 
                className="remove-btn"
                onClick={() => removeFromCompare(listing.id)}
                title="Karşılaştırmadan Çıkar"
              >
                ✕
              </button>
              <div className="compare-image">
                {listing.images && listing.images.length > 0 ? (
                  <img src={listing.images[0]} alt={listing.title} />
                ) : (
                  <div className="no-image">📷</div>
                )}
              </div>
              <h3 className="compare-title">{listing.title}</h3>
              <a 
                href={listing.source_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="view-link"
              >
                İlanı Gör ↗
              </a>
            </div>
          ))}
        </div>

        {/* Comparison Rows */}
        <div className="compare-body">
          {comparisonRows.map((row) => (
            <div key={row.key} className="compare-row">
              <div className="compare-label-cell">{row.label}</div>
              {listings.map((listing) => {
                const value = (listing as any)[row.key]
                const formattedValue = row.format(value)
                
                // Highlight logic
                let cellClass = 'compare-value-cell'
                if (row.highlight === 'lowest' && row.key === 'price') {
                  if (listing.price === lowestPrice) {
                    cellClass += ' highlight-best'
                  }
                }
                if (row.highlight === 'lowest' && row.key === 'mileage') {
                  const mileages = listings.map(l => l.mileage).filter(m => m !== null) as number[]
                  if (mileages.length > 0 && listing.mileage === Math.min(...mileages)) {
                    cellClass += ' highlight-best'
                  }
                }

                return (
                  <div key={listing.id} className={cellClass}>
                    {formattedValue}
                  </div>
                )
              })}
            </div>
          ))}

          {/* Damage Info Row */}
          <div className="compare-row">
            <div className="compare-label-cell">Ekspertiz</div>
            {listings.map((listing) => (
              <div key={listing.id} className="compare-value-cell">
                {listing.damage_info ? (
                  <div className="damage-summary">
                    {listing.damage_info.original?.length > 0 && (
                      <span className="damage-tag original">
                        🟢 {listing.damage_info.original.length} Orijinal
                      </span>
                    )}
                    {listing.damage_info.painted?.length > 0 && (
                      <span className="damage-tag painted">
                        🟡 {listing.damage_info.painted.length} Boyalı
                      </span>
                    )}
                    {listing.damage_info.changed?.length > 0 && (
                      <span className="damage-tag changed">
                        🔴 {listing.damage_info.changed.length} Değişen
                      </span>
                    )}
                    {listing.damage_info.tramer_amount && (
                      <span className="damage-tag tramer">
                        💰 {listing.damage_info.tramer_amount}
                      </span>
                    )}
                  </div>
                ) : (
                  <span className="no-data">Bilgi yok</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Compare

