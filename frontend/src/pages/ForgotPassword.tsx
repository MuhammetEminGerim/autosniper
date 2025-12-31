import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import './Auth.css'

const ForgotPassword = () => {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [resetToken, setResetToken] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await api.post('/api/auth/forgot-password', { email })
      
      if (response.data.success) {
        setSent(true)
        // Development: Token'ı göster
        if (response.data.reset_token) {
          setResetToken(response.data.reset_token)
        }
        toast.success('Şifre sıfırlama bağlantısı gönderildi!')
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Bir hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-header">
            <div className="auth-logo">📧</div>
            <h1>Email Gönderildi</h1>
            <p>Şifre sıfırlama bağlantısı email adresinize gönderildi</p>
          </div>

          <div className="auth-card">
            <div className="success-message">
              <p>
                <strong>{email}</strong> adresine şifre sıfırlama bağlantısı gönderdik.
                Lütfen gelen kutunuzu kontrol edin.
              </p>
            </div>

            {/* Development: Token göster */}
            {resetToken && (
              <div className="dev-token-box">
                <p className="dev-label">🔧 Development Token:</p>
                <Link 
                  to={`/reset-password?token=${resetToken}`}
                  className="btn btn-primary"
                >
                  Şifreyi Sıfırla
                </Link>
              </div>
            )}

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
          <div className="auth-logo">🔑</div>
          <h1>Şifremi Unuttum</h1>
          <p>Email adresinizi girin, size sıfırlama bağlantısı gönderelim</p>
        </div>

        <div className="auth-card">
          <form onSubmit={handleSubmit} className="auth-form">
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

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '⏳ Gönderiliyor...' : '📧 Sıfırlama Bağlantısı Gönder'}
            </button>
          </form>

          <div className="auth-footer">
            <p>
              Şifrenizi hatırladınız mı?{' '}
              <Link to="/login">Giriş Yap</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ForgotPassword

