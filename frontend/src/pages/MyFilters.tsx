import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import './MyFilters.css'

interface Filter {
  id: number
  name: string
  criteria: Record<string, any>
  is_active: boolean
  created_at: string
  auto_scan_enabled: boolean
  scan_interval: number
  last_scan_at: string | null
  next_scan_at: string | null
  total_scans: number
  new_listings_found: number
}

const SCAN_INTERVALS = [
  { value: 15, label: '15 dakika' },
  { value: 30, label: '30 dakika' },
  { value: 60, label: '1 saat' },
  { value: 120, label: '2 saat' },
  { value: 360, label: '6 saat' },
  { value: 720, label: '12 saat' },
  { value: 1440, label: '24 saat' },
]

const MyFilters = () => {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<Filter[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingFilter, setEditingFilter] = useState<Filter | null>(null)
  const [searching, setSearching] = useState<number | null>(null)
  const [togglingScheduler, setTogglingScheduler] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    brand: '',
    model: '',
    minYear: '',
    maxYear: '',
    minPrice: '',
    maxPrice: '',
    minMileage: '',
    maxMileage: '',
    city: '',
    fuelType: '',
    transmission: '',
    is_active: true,
    auto_scan_enabled: false,
    scan_interval: 30,
  })

  const cities = [
    'Adana', 'Ankara', 'Antalya', 'Aydın', 'Balıkesir', 'Bolu', 'Bursa',
    'Denizli', 'Diyarbakır', 'Eskişehir', 'Gaziantep', 'Hatay', 'Istanbul',
    'İzmir', 'Kayseri', 'Kocaeli', 'Konya', 'Malatya', 'Manisa', 'Mersin',
    'Muğla', 'Sakarya', 'Samsun', 'Tekirdağ', 'Trabzon'
  ]

  const brands = [
    'Audi', 'BMW', 'Chevrolet', 'Citroen', 'Dacia', 'Fiat', 'Ford', 
    'Honda', 'Hyundai', 'Jeep', 'Kia', 'Mazda', 'Mercedes', 'Mitsubishi',
    'Nissan', 'Opel', 'Peugeot', 'Renault', 'Seat', 'Skoda', 'Suzuki',
    'Toyota', 'Volkswagen', 'Volvo'
  ]

  useEffect(() => {
    loadFilters()
  }, [])

  const loadFilters = async () => {
    try {
      const response = await api.get('/api/filters')
      setFilters(response.data)
    } catch (error) {
      toast.error('Filtreler yüklenemedi')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const criteria: Record<string, any> = {}
    if (formData.brand) criteria.brand = formData.brand
    if (formData.model) criteria.model = formData.model
    if (formData.minYear) criteria.min_year = parseInt(formData.minYear)
    if (formData.maxYear) criteria.max_year = parseInt(formData.maxYear)
    if (formData.minPrice) criteria.min_price = parseFloat(formData.minPrice)
    if (formData.maxPrice) criteria.max_price = parseFloat(formData.maxPrice)
    if (formData.minMileage) criteria.min_mileage = parseInt(formData.minMileage)
    if (formData.maxMileage) criteria.max_mileage = parseInt(formData.maxMileage)
    if (formData.city) criteria.city = formData.city
    if (formData.fuelType) criteria.fuel_type = formData.fuelType
    if (formData.transmission) criteria.transmission = formData.transmission

    try {
      if (editingFilter) {
        // Güncelleme
        await api.put(`/api/filters/${editingFilter.id}`, {
          name: formData.name,
          criteria,
          is_active: formData.is_active,
          auto_scan_enabled: formData.auto_scan_enabled,
          scan_interval: formData.scan_interval,
        })
        toast.success('Filtre güncellendi!')
      } else {
        // Yeni oluştur
        await api.post('/api/filters', {
          name: formData.name,
          criteria,
          is_active: formData.is_active,
          auto_scan_enabled: formData.auto_scan_enabled,
          scan_interval: formData.scan_interval,
        })
        toast.success('Filtre oluşturuldu!')
      }
      setShowForm(false)
      setEditingFilter(null)
      resetForm()
      loadFilters()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'İşlem başarısız')
    }
  }

  const handleEdit = (filter: Filter) => {
    setEditingFilter(filter)
    setFormData({
      name: filter.name,
      brand: filter.criteria.brand || '',
      model: filter.criteria.model || '',
      minYear: filter.criteria.min_year?.toString() || '',
      maxYear: filter.criteria.max_year?.toString() || '',
      minPrice: filter.criteria.min_price?.toString() || '',
      maxPrice: filter.criteria.max_price?.toString() || '',
      minMileage: filter.criteria.min_mileage?.toString() || '',
      maxMileage: filter.criteria.max_mileage?.toString() || '',
      city: filter.criteria.city || '',
      fuelType: filter.criteria.fuel_type || '',
      transmission: filter.criteria.transmission || '',
      is_active: filter.is_active,
      auto_scan_enabled: filter.auto_scan_enabled,
      scan_interval: filter.scan_interval,
    })
    setShowForm(true)
  }

  const handleCancelEdit = () => {
    setShowForm(false)
    setEditingFilter(null)
    resetForm()
  }

  const resetForm = () => {
    setFormData({
      name: '',
      brand: '',
      model: '',
      minYear: '',
      maxYear: '',
      minPrice: '',
      maxPrice: '',
      minMileage: '',
      maxMileage: '',
      city: '',
      fuelType: '',
      transmission: '',
      is_active: true,
      auto_scan_enabled: false,
      scan_interval: 30,
    })
  }

  const toggleScheduler = async (filter: Filter, enabled: boolean, interval?: number) => {
    setTogglingScheduler(filter.id)
    try {
      await api.post(`/api/filters/${filter.id}/scheduler`, {
        enabled,
        interval: interval || filter.scan_interval
      })
      toast.success(enabled ? '⏰ Otomatik tarama aktif!' : '⏹️ Otomatik tarama durduruldu')
      loadFilters()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Scheduler güncellenemedi')
    } finally {
      setTogglingScheduler(null)
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

  const formatLastScan = (lastScanAt: string | null): string => {
    if (!lastScanAt) return 'Henüz tarama yapılmadı'
    const date = new Date(lastScanAt)
    return date.toLocaleString('tr-TR')
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Bu filtreyi silmek istediğinize emin misiniz?')) return

    try {
      await api.delete(`/api/filters/${id}`)
      toast.success('Filtre silindi')
      loadFilters()
    } catch (error) {
      toast.error('Filtre silinemedi')
    }
  }

  const toggleActive = async (filter: Filter) => {
    try {
      await api.put(`/api/filters/${filter.id}`, {
        is_active: !filter.is_active,
      })
      toast.success(`Filtre ${!filter.is_active ? 'aktif' : 'pasif'} edildi`)
      loadFilters()
    } catch (error) {
      toast.error('Filtre güncellenemedi')
    }
  }

  const handleSearch = async (filter: Filter) => {
    setSearching(filter.id)
    toast.loading('İlanlar aranıyor...', { id: 'search' })
    
    try {
      const response = await api.post(`/api/filters/${filter.id}/search`)
      toast.success(
        `${response.data.total_found || 0} ilan bulundu, ${response.data.new_saved || 0} yeni kaydedildi!`,
        { id: 'search', duration: 5000 }
      )
      navigate('/listings')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Arama sırasında hata oluştu', { id: 'search' })
    } finally {
      setSearching(null)
    }
  }

  const formatCriteriaLabel = (key: string): string => {
    const labels: Record<string, string> = {
      brand: 'Marka',
      model: 'Model',
      min_year: 'Min Yıl',
      max_year: 'Max Yıl',
      min_price: 'Min Fiyat',
      max_price: 'Max Fiyat',
      min_mileage: 'Min KM',
      max_mileage: 'Max KM',
      city: 'Şehir',
      fuel_type: 'Yakıt',
      transmission: 'Vites'
    }
    return labels[key] || key
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
    <div className="my-filters-page">
      <div className="page-header">
        <div>
          <h1>⚙️ Filtrelerim</h1>
          <p>Kayıtlı arama filtrelerinizi yönetin</p>
        </div>
        <button 
          className={`btn ${showForm ? 'btn-secondary' : 'btn-primary'}`}
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? '✕ İptal' : '➕ Yeni Filtre'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="filter-form card animate-fade-in">
          <h2>{editingFilter ? '✏️ Filtreyi Düzenle' : '🆕 Yeni Filtre Oluştur'}</h2>
          
          <div className="form-section">
            <div className="form-group full-width">
              <label>Filtre Adı *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="Örn: Ankara BMW 3 Serisi"
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Araç Bilgileri</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Marka</label>
                <select
                  value={formData.brand}
                  onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                >
                  <option value="">Tümü</option>
                  {brands.map(brand => (
                    <option key={brand} value={brand}>{brand}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Model</label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  placeholder="Örn: 320i, Focus"
                />
              </div>
              <div className="form-group">
                <label>Min Yıl</label>
                <input
                  type="number"
                  value={formData.minYear}
                  onChange={(e) => setFormData({ ...formData, minYear: e.target.value })}
                  placeholder="2015"
                />
              </div>
              <div className="form-group">
                <label>Max Yıl</label>
                <input
                  type="number"
                  value={formData.maxYear}
                  onChange={(e) => setFormData({ ...formData, maxYear: e.target.value })}
                  placeholder="2024"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Fiyat & Konum</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Min Fiyat (TL)</label>
                <input
                  type="number"
                  value={formData.minPrice}
                  onChange={(e) => setFormData({ ...formData, minPrice: e.target.value })}
                  placeholder="100000"
                />
              </div>
              <div className="form-group">
                <label>Max Fiyat (TL)</label>
                <input
                  type="number"
                  value={formData.maxPrice}
                  onChange={(e) => setFormData({ ...formData, maxPrice: e.target.value })}
                  placeholder="500000"
                />
              </div>
              <div className="form-group">
                <label>Min Kilometre</label>
                <input
                  type="number"
                  value={formData.minMileage}
                  onChange={(e) => setFormData({ ...formData, minMileage: e.target.value })}
                  placeholder="0"
                />
              </div>
              <div className="form-group">
                <label>Max Kilometre</label>
                <input
                  type="number"
                  value={formData.maxMileage}
                  onChange={(e) => setFormData({ ...formData, maxMileage: e.target.value })}
                  placeholder="150000"
                />
              </div>
              <div className="form-group">
                <label>Şehir</label>
                <select
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                >
                  <option value="">Tümü</option>
                  {cities.map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Diğer Özellikler</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Yakıt Tipi</label>
                <select
                  value={formData.fuelType}
                  onChange={(e) => setFormData({ ...formData, fuelType: e.target.value })}
                >
                  <option value="">Tümü</option>
                  <option value="benzin">Benzin</option>
                  <option value="dizel">Dizel</option>
                  <option value="lpg">LPG</option>
                  <option value="elektrik">Elektrik</option>
                  <option value="hibrit">Hibrit</option>
                </select>
              </div>
              <div className="form-group">
                <label>Vites</label>
                <select
                  value={formData.transmission}
                  onChange={(e) => setFormData({ ...formData, transmission: e.target.value })}
                >
                  <option value="">Tümü</option>
                  <option value="otomatik">Otomatik</option>
                  <option value="manuel">Manuel</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section scheduler-section">
            <h3>⏰ Otomatik Tarama</h3>
            <div className="form-grid">
              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.auto_scan_enabled}
                    onChange={(e) => setFormData({ ...formData, auto_scan_enabled: e.target.checked })}
                  />
                  <span className="checkmark"></span>
                  Otomatik tarama aktif
                </label>
              </div>
              {formData.auto_scan_enabled && (
                <div className="form-group">
                  <label>Tarama Sıklığı</label>
                  <select
                    value={formData.scan_interval}
                    onChange={(e) => setFormData({ ...formData, scan_interval: parseInt(e.target.value) })}
                  >
                    {SCAN_INTERVALS.map(interval => (
                      <option key={interval.value} value={interval.value}>
                        {interval.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
            {formData.auto_scan_enabled && (
              <p className="scheduler-info">
                🤖 Bu filtre her {SCAN_INTERVALS.find(i => i.value === formData.scan_interval)?.label} otomatik olarak taranacak
              </p>
            )}
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={handleCancelEdit}>
              İptal
            </button>
            <button type="submit" className="btn btn-success">
              {editingFilter ? '✓ Güncelle' : '✓ Filtre Oluştur'}
            </button>
          </div>
        </form>
      )}

      <div className="filters-grid">
        {filters.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>Henüz filtre yok</h3>
            <p>Arama kriterlerinizi kaydedin ve tekrar kullanın</p>
            <button className="btn btn-primary" onClick={() => setShowForm(true)}>
              ➕ İlk Filtreyi Oluştur
            </button>
          </div>
        ) : (
          filters.map((filter, index) => (
            <div 
              key={filter.id} 
              className={`filter-card card ${filter.is_active ? 'active' : 'inactive'} ${filter.auto_scan_enabled ? 'scheduler-active' : ''}`}
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className="filter-header">
                <div className="filter-info">
                  <h3>{filter.name}</h3>
                  <div className="badges">
                    <span className={`status-badge ${filter.is_active ? 'badge-success' : 'badge-warning'}`}>
                      {filter.is_active ? '● Aktif' : '○ Pasif'}
                    </span>
                    {filter.auto_scan_enabled && (
                      <span className="status-badge badge-scheduler">
                        ⏰ Otomatik
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="filter-criteria">
                {Object.entries(filter.criteria).map(([key, value]) => (
                  <span key={key} className="criteria-tag">
                    <strong>{formatCriteriaLabel(key)}:</strong> {String(value)}
                  </span>
                ))}
              </div>

              {/* Scheduler Info */}
              {filter.auto_scan_enabled && (
                <div className="scheduler-status">
                  <div className="scheduler-stat">
                    <span className="stat-label">⏱️ Sıklık:</span>
                    <span className="stat-value">{SCAN_INTERVALS.find(i => i.value === filter.scan_interval)?.label || `${filter.scan_interval}dk`}</span>
                  </div>
                  <div className="scheduler-stat">
                    <span className="stat-label">⏭️ Sonraki:</span>
                    <span className="stat-value">{formatTimeRemaining(filter.next_scan_at)}</span>
                  </div>
                  <div className="scheduler-stat">
                    <span className="stat-label">📊 Toplam:</span>
                    <span className="stat-value">{filter.total_scans || 0} tarama</span>
                  </div>
                  <div className="scheduler-stat">
                    <span className="stat-label">🆕 Bulunan:</span>
                    <span className="stat-value">{filter.new_listings_found || 0} ilan</span>
                  </div>
                </div>
              )}

              {/* Scheduler Controls */}
              <div className="scheduler-controls">
                <label className="scheduler-toggle">
                  <input
                    type="checkbox"
                    checked={filter.auto_scan_enabled}
                    onChange={(e) => toggleScheduler(filter, e.target.checked)}
                    disabled={togglingScheduler === filter.id}
                  />
                  <span className="toggle-slider"></span>
                  <span className="toggle-label">
                    {filter.auto_scan_enabled ? '⏰ Otomatik Tarama Açık' : '⏹️ Otomatik Tarama Kapalı'}
                  </span>
                </label>
                {filter.auto_scan_enabled && (
                  <select
                    className="interval-select"
                    value={filter.scan_interval}
                    onChange={(e) => toggleScheduler(filter, true, parseInt(e.target.value))}
                    disabled={togglingScheduler === filter.id}
                  >
                    {SCAN_INTERVALS.map(interval => (
                      <option key={interval.value} value={interval.value}>
                        {interval.label}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div className="filter-actions">
                <button
                  onClick={() => handleSearch(filter)}
                  className="btn btn-primary btn-sm"
                  disabled={searching === filter.id}
                >
                  {searching === filter.id ? '⏳ Aranıyor...' : '🔍 Şimdi Ara'}
                </button>
                <button
                  onClick={() => handleEdit(filter)}
                  className="btn btn-secondary btn-sm"
                >
                  ✏️ Düzenle
                </button>
                <button
                  onClick={() => toggleActive(filter)}
                  className="btn btn-secondary btn-sm"
                >
                  {filter.is_active ? '⏸️ Durdur' : '▶️ Aktif Et'}
                </button>
                <button
                  onClick={() => handleDelete(filter.id)}
                  className="btn btn-danger btn-sm"
                >
                  🗑️
                </button>
              </div>

              {filter.last_scan_at && (
                <div className="last-scan-info">
                  📅 Son tarama: {formatLastScan(filter.last_scan_at)}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default MyFilters

