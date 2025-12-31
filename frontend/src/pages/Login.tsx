import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import toast from 'react-hot-toast'
import './Auth.css'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/api/auth/login', {
        email,
        password
      })

      // Token'ı set et
      const token = response.data.access_token

      // Token ile kullanıcı bilgilerini al
      const userResponse = await api.get('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      console.log('User data from /me:', userResponse.data)

      setAuth(
        userResponse.data,
        token
      )

      toast.success('Giriş başarılı!')
      navigate('/')
    } catch (err: any) {
      console.error('Login error:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'Giriş başarısız'
      setError(typeof errorMessage === 'string' ? errorMessage : 'Giriş başarısız')
      toast.error(typeof errorMessage === 'string' ? errorMessage : 'Giriş başarısız')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <div className="auth-logo">🎯</div>
          <h1>AutoSniper</h1>
          <p>Hesabınıza giriş yapın</p>
        </div>

        <div className="auth-card">
          <form onSubmit={handleSubmit} className="auth-form">
            {error && <div className="error-message">{error}</div>}

            <div className="form-group">
              <label>E-posta</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ornek@email.com"
                required
              />
            </div>

            <div className="form-group">
              <label>Şifre</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '⏳ Giriş yapılıyor...' : '🚀 Giriş Yap'}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              <Link to="/forgot-password">Şifremi Unuttum</Link>
            </p>
            <p>
              Hesabınız yok mu?{' '}
              <Link to="/register">Kayıt Ol</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
