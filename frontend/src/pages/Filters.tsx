import { useEffect, useState } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'
import './Filters.css'

interface Filter {
  id: number
  name: string
  criteria: Record<string, any>
  is_active: boolean
  created_at: string
}

const Filters = () => {
  const [filters, setFilters] = useState<Filter[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    brand: '',
    model: '',
    minYear: '',
    maxYear: '',
    minPrice: '',
    maxPrice: '',
    city: '',
    fuelType: '',
    transmission: '',
    is_active: true,
  })

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
    if (formData.city) criteria.city = formData.city
    if (formData.fuelType) criteria.fuel_type = formData.fuelType
    if (formData.transmission) criteria.transmission = formData.transmission

    try {
      await api.post('/api/filters', {
        name: formData.name,
        criteria,
        is_active: formData.is_active,
      })
      toast.success('Filtre oluşturuldu')
      setShowForm(false)
      setFormData({
        name: '',
        brand: '',
        model: '',
        minYear: '',
        maxYear: '',
        minPrice: '',
        maxPrice: '',
        city: '',
        fuelType: '',
        transmission: '',
        is_active: true,
      })
      loadFilters()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Filtre oluşturulamadı')
    }
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

  const [searching, setSearching] = useState<number | null>(null)

  const handleSearch = async (filter: Filter) => {
    setSearching(filter.id)
    toast.loading('İlanlar aranıyor...', { id: 'search' })
    
    try {
      const response = await api.post(`/api/filters/${filter.id}/search`)
      toast.success(
        `${response.data.total_found} ilan bulundu, ${response.data.new_saved} yeni ilan kaydedildi!`,
        { id: 'search' }
      )
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Arama sırasında hata oluştu', { id: 'search' })
    } finally {
      setSearching(null)
    }
  }

  if (loading) {
    return <div className="loading">Yükleniyor...</div>
  }

  return (
    <div className="filters-page">
      <div className="page-header">
        <h1>Filtreler</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? '❌ İptal' : '➕ Yeni Filtre'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="filter-form">
          <h2>Yeni Filtre Oluştur</h2>
          <div className="form-row">
            <div className="form-group">
              <label>Filtre Adı *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="Örn: Ankara Audi A3"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Marka</label>
              <input
                type="text"
                value={formData.brand}
                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                placeholder="Örn: Audi"
              />
            </div>
            <div className="form-group">
              <label>Model</label>
              <input
                type="text"
                value={formData.model}
                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                placeholder="Örn: A3"
              />
            </div>
          </div>

          <div className="form-row">
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

          <div className="form-row">
            <div className="form-group">
              <label>Min Fiyat (TL)</label>
              <input
                type="number"
                value={formData.minPrice}
                onChange={(e) => setFormData({ ...formData, minPrice: e.target.value })}
                placeholder="500000"
              />
            </div>
            <div className="form-group">
              <label>Max Fiyat (TL)</label>
              <input
                type="number"
                value={formData.maxPrice}
                onChange={(e) => setFormData({ ...formData, maxPrice: e.target.value })}
                placeholder="1000000"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Şehir</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                placeholder="Ankara"
              />
            </div>
            <div className="form-group">
              <label>Yakıt Tipi</label>
              <select
                value={formData.fuelType}
                onChange={(e) => setFormData({ ...formData, fuelType: e.target.value })}
              >
                <option value="">Seçiniz</option>
                <option value="dizel">Dizel</option>
                <option value="benzin">Benzin</option>
                <option value="elektrik">Elektrik</option>
                <option value="hibrit">Hibrit</option>
              </select>
            </div>
            <div className="form-group">
              <label>Şanzıman</label>
              <select
                value={formData.transmission}
                onChange={(e) => setFormData({ ...formData, transmission: e.target.value })}
              >
                <option value="">Seçiniz</option>
                <option value="otomatik">Otomatik</option>
                <option value="manuel">Manuel</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
              Aktif
            </label>
          </div>

          <button type="submit" className="btn-primary">
            Filtre Oluştur
          </button>
        </form>
      )}

      <div className="filters-list">
        {filters.length === 0 ? (
          <div className="empty-state">
            <p>Henüz filtre oluşturmadınız.</p>
            <button onClick={() => setShowForm(true)} className="btn-primary">
              İlk Filtrenizi Oluşturun
            </button>
          </div>
        ) : (
          filters.map((filter) => (
            <div key={filter.id} className="filter-card">
              <div className="filter-header">
                <h3>{filter.name}</h3>
                <div className="filter-actions">
                  <button
                    onClick={() => handleSearch(filter)}
                    className="search-btn"
                    disabled={searching === filter.id}
                  >
                    {searching === filter.id ? '🔄 Aranıyor...' : '🔍 Ara'}
                  </button>
                  <button
                    onClick={() => toggleActive(filter)}
                    className={`toggle-btn ${filter.is_active ? 'active' : 'inactive'}`}
                  >
                    {filter.is_active ? '✅ Aktif' : '⏸️ Pasif'}
                  </button>
                  <button
                    onClick={() => handleDelete(filter.id)}
                    className="delete-btn"
                  >
                    🗑️ Sil
                  </button>
                </div>
              </div>
              <div className="filter-criteria">
                {Object.entries(filter.criteria).map(([key, value]) => (
                  <span key={key} className="criteria-tag">
                    {key}: {String(value)}
                  </span>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Filters

