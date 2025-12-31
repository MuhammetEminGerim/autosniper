import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import api from '../services/api'
import './Search.css'

const Search = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
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
    transmission: ''
  })

  const brands = [
    'Audi', 'BMW', 'Chevrolet', 'Citroen', 'Dacia', 'Fiat', 'Ford', 
    'Honda', 'Hyundai', 'Jeep', 'Kia', 'Mazda', 'Mercedes', 'Mitsubishi',
    'Nissan', 'Opel', 'Peugeot', 'Renault', 'Seat', 'Skoda', 'Suzuki',
    'Toyota', 'Volkswagen', 'Volvo'
  ]

  const cities = [
    'Adana', 'Ankara', 'Antalya', 'Aydın', 'Balıkesir', 'Bolu', 'Bursa',
    'Denizli', 'Diyarbakır', 'Eskişehir', 'Gaziantep', 'Hatay', 'Istanbul',
    'İzmir', 'Kayseri', 'Kocaeli', 'Konya', 'Malatya', 'Manisa', 'Mersin',
    'Muğla', 'Sakarya', 'Samsun', 'Tekirdağ', 'Trabzon'
  ]

  const handleSearch = async () => {
    setLoading(true)
    try {
      // Filtre kriterlerini oluştur
      const criteria: Record<string, any> = {}
      if (filters.brand) criteria.brand = filters.brand
      if (filters.model) criteria.model = filters.model
      if (filters.minYear) criteria.min_year = parseInt(filters.minYear)
      if (filters.maxYear) criteria.max_year = parseInt(filters.maxYear)
      if (filters.minPrice) criteria.min_price = parseFloat(filters.minPrice)
      if (filters.maxPrice) criteria.max_price = parseFloat(filters.maxPrice)
      if (filters.minMileage) criteria.min_mileage = parseInt(filters.minMileage)
      if (filters.maxMileage) criteria.max_mileage = parseInt(filters.maxMileage)
      if (filters.city) criteria.city = filters.city
      if (filters.fuelType) criteria.fuel_type = filters.fuelType
      if (filters.transmission) criteria.transmission = filters.transmission

      toast.loading('İlanlar taranıyor...', { id: 'search' })
      
      const response = await api.post('/api/test/scrape', { criteria })
      
      toast.dismiss('search')
      toast.success(`✅ ${response.data.new_listings_added} yeni ilan bulundu!`, { duration: 5000 })
      
      // İlanlar sayfasına yönlendir
      navigate('/listings')
    } catch (error: any) {
      toast.dismiss('search')
      toast.error(error.response?.data?.detail || 'Arama başarısız')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setFilters({
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
      transmission: ''
    })
  }

  return (
    <div className="search-page">
      <div className="page-header">
        <div>
          <h1>🔍 İlan Ara</h1>
          <p>arabam.com üzerinden ilan tarayın</p>
        </div>
      </div>

      <div className="search-container">
        <div className="search-card">
          <h2>Arama Kriterleri</h2>
          
          <div className="filter-grid">
            <div className="filter-group">
              <label>Marka</label>
              <select 
                value={filters.brand} 
                onChange={(e) => setFilters({...filters, brand: e.target.value})}
              >
                <option value="">Tümü</option>
                {brands.map(brand => (
                  <option key={brand} value={brand}>{brand}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Model</label>
              <input 
                type="text" 
                placeholder="Örn: Focus, Corolla"
                value={filters.model}
                onChange={(e) => setFilters({...filters, model: e.target.value})}
              />
            </div>

            <div className="filter-group">
              <label>Min Yıl</label>
              <input 
                type="number" 
                placeholder="2015"
                value={filters.minYear}
                onChange={(e) => setFilters({...filters, minYear: e.target.value})}
              />
            </div>

            <div className="filter-group">
              <label>Max Yıl</label>
              <input 
                type="number" 
                placeholder="2024"
                value={filters.maxYear}
                onChange={(e) => setFilters({...filters, maxYear: e.target.value})}
              />
            </div>

            <div className="filter-group">
              <label>Min Fiyat (TL)</label>
              <input 
                type="number" 
                placeholder="100000"
                value={filters.minPrice}
                onChange={(e) => setFilters({...filters, minPrice: e.target.value})}
              />
            </div>

            <div className="filter-group">
              <label>Max Fiyat (TL)</label>
              <input 
                type="number" 
                placeholder="500000"
                value={filters.maxPrice}
                onChange={(e) => setFilters({...filters, maxPrice: e.target.value})}
              />
            </div>

            <div className="filter-group">
              <label>Min Kilometre</label>
              <input 
                type="number" 
                placeholder="0"
                value={filters.minMileage}
                onChange={(e) => setFilters({...filters, minMileage: e.target.value})}
              />
            </div>

            <div className="filter-group">
              <label>Max Kilometre</label>
              <input 
                type="number" 
                placeholder="150000"
                value={filters.maxMileage}
                onChange={(e) => setFilters({...filters, maxMileage: e.target.value})}
              />
            </div>

            <div className="filter-group">
              <label>Şehir</label>
              <select 
                value={filters.city} 
                onChange={(e) => setFilters({...filters, city: e.target.value})}
              >
                <option value="">Tümü</option>
                {cities.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Yakıt Tipi</label>
              <select 
                value={filters.fuelType} 
                onChange={(e) => setFilters({...filters, fuelType: e.target.value})}
              >
                <option value="">Tümü</option>
                <option value="benzin">Benzin</option>
                <option value="dizel">Dizel</option>
                <option value="lpg">LPG</option>
                <option value="elektrik">Elektrik</option>
                <option value="hibrit">Hibrit</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Vites</label>
              <select 
                value={filters.transmission} 
                onChange={(e) => setFilters({...filters, transmission: e.target.value})}
              >
                <option value="">Tümü</option>
                <option value="otomatik">Otomatik</option>
                <option value="manuel">Manuel</option>
                <option value="yarı otomatik">Yarı Otomatik</option>
              </select>
            </div>
          </div>

          <div className="search-actions">
            <button className="btn btn-secondary" onClick={handleClear}>
              Temizle
            </button>
            <button 
              className="btn btn-primary" 
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? '⏳ Taranıyor...' : '🔍 Ara'}
            </button>
          </div>
        </div>

        <div className="search-tips">
          <h3>💡 İpuçları</h3>
          <ul>
            <li>Daha spesifik kriterler daha hızlı sonuç verir</li>
            <li>Şehir seçimi zorunlu değil ama önerilir</li>
            <li>Bulunan ilanlar "İlanlar" sayfasına kaydedilir</li>
            <li>Sık kullandığınız kriterleri "Filtrelerim"e kaydedin</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Search

