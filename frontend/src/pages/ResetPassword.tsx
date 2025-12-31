import { useState, useEffect } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import './Auth.css'

const ResetPassword = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [validating, setValidating] = useState(true)
  const [tokenValid, setTokenValid] = useState(false)
  const [userEmail, setUserEmail] = useState('')

  useEffect(() => {
    if (token) {
      validateToken()
    } else {
      setValidating(false)
    }
  }, [token])

  const validateToken = async () => {
    try {
      const response = await api.get(`/api/auth/verify-reset-token/${token}`)
      if (response.data.valid) {
        setTokenValid(true)
        setUserEmail(response.data.email)
      }
    } catch (err) {
      setTokenValid(false)
    } finally {
      setValidating(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      toast.error('Şifreler eşleşmiyor')
      return
    }

    if (password.length < 6) {
      toast.error('Şifre en az 6 karakter olmalı')
      return
    }

    setLoading(true)

    try {
      const response = await api.post('/api/auth/reset-password', {
        token,
        new_password: password
      })

      if (response.data.success) {
        toast.success('Şifreniz başarıyla güncellendi!')
        navigate('/login')
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Şifre sıfırlama başarısız')
    } finally {
      setLoading(false)
    }
  }

  if (validating) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-header">
            <div className="auth-logo">⏳</div>
            <h1>Doğrulanıyor...</h1>
          </div>
        </div>
      </div>
    )
  }

  if (!token || !tokenValid) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-header">
            <div className="auth-logo">❌</div>
            <h1>Geçersiz Bağlantı</h1>
            <p>Bu şifre sıfırlama bağlantısı geçersiz veya süresi dolmuş</p>
          </div>

          <div className="auth-card">
            <div className="error-box">
              <p>Lütfen yeni bir şifre sıfırlama isteği gönderin.</p>
            </div>

            <Link to="/forgot-password" className="btn btn-primary">
              Yeni İstek Gönder
            </Link>

            <div className="auth-footer">
              <p>
                <Link to="/login">← Giriş sayfasına dön</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <div className="auth-logo">🔐</div>
          <h1>Yeni Şifre Belirle</h1>
          <p>{userEmail} için yeni şifre oluşturun</p>
        </div>

        <div className="auth-card">
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>Yeni Şifre</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
              />
            </div>

            <div className="form-group">
              <label>Şifre Tekrar</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '⏳ Güncelleniyor...' : '🔐 Şifreyi Güncelle'}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              <Link to="/login">← Giriş sayfasına dön</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResetPassword

