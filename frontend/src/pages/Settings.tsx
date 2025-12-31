import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import api from '../services/api'
import pushNotifications from '../services/pushNotifications'
import './Settings.css'

interface TelegramSettings {
  telegram_chat_id: string | null
  telegram_enabled: boolean
  bot_configured: boolean
  bot_username: string | null
}

const Settings = () => {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [settings, setSettings] = useState<TelegramSettings>({
    telegram_chat_id: '',
    telegram_enabled: false,
    bot_configured: false,
    bot_username: null
  })
  
  // Push notification state
  const [pushSupported] = useState(pushNotifications.isSupported)
  const [pushEnabled, setPushEnabled] = useState(pushNotifications.isEnabled)
  const [pushDenied, setPushDenied] = useState(pushNotifications.isDenied)

  useEffect(() => {
    loadSettings()
    // Push notification durumunu güncelle
    setPushEnabled(pushNotifications.isEnabled)
    setPushDenied(pushNotifications.isDenied)
  }, [])

  const loadSettings = async () => {
    try {
      const response = await api.get('/api/settings/telegram')
      setSettings(response.data)
    } catch (error) {
      console.error('Ayarlar yüklenemedi:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const response = await api.put('/api/settings/telegram', {
        telegram_chat_id: settings.telegram_chat_id || null,
        telegram_enabled: settings.telegram_enabled
      })
      setSettings(response.data)
      toast.success('Ayarlar kaydedildi!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ayarlar kaydedilemedi')
    } finally {
      setSaving(false)
    }
  }

  const handleTest = async () => {
    if (!settings.telegram_chat_id) {
      toast.error('Lütfen önce Chat ID girin')
      return
    }

    setTesting(true)
    try {
      await api.post('/api/settings/telegram/test', {
        chat_id: settings.telegram_chat_id
      })
      toast.success('Test mesajı gönderildi! Telegram\'ı kontrol edin.')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Test mesajı gönderilemedi')
    } finally {
      setTesting(false)
    }
  }

  const handleEnablePush = async () => {
    const granted = await pushNotifications.requestPermission()
    setPushEnabled(granted)
    setPushDenied(!granted && pushNotifications.isDenied)
    
    if (granted) {
      toast.success('Tarayıcı bildirimleri etkinleştirildi!')
      // Test bildirimi gönder
      await pushNotifications.notify('🎉 Bildirimler Aktif!', {
        body: 'Artık yeni ilanlar ve fiyat değişiklikleri için bildirim alacaksınız.'
      })
    } else {
      toast.error('Bildirim izni reddedildi')
    }
  }

  const handleTestPush = async () => {
    await pushNotifications.notifyNewListings('Test Filtre', 3)
  }

  if (loading) {
    return (
      <div className="settings-page">
        <div className="loading">Yükleniyor...</div>
      </div>
    )
  }

  return (
    <div className="settings-page animate-fade-in">
      <header className="page-header">
        <h1>⚙️ Ayarlar</h1>
        <p>Bildirim ve uygulama ayarlarınızı yönetin</p>
      </header>

      <div className="settings-grid">
        {/* Telegram Bildirimleri */}
        <div className="settings-card card">
          <div className="card-header">
            <h2>🤖 Telegram Bildirimleri</h2>
            <span className={`status-badge ${settings.bot_configured ? 'active' : 'inactive'}`}>
              {settings.bot_configured ? '✅ Bot Aktif' : '⚠️ Bot Yapılandırılmamış'}
            </span>
          </div>

          <div className="card-content">
            {settings.bot_configured && settings.bot_username && (
              <div className="info-box success">
                <span className="icon">🤖</span>
                <div>
                  <strong>Bot: @{settings.bot_username}</strong>
                  <p>
                    Bildirimleri almak için{' '}
                    <a href={`https://t.me/${settings.bot_username}`} target="_blank" rel="noopener noreferrer">
                      @{settings.bot_username}
                    </a>
                    {' '}botuna /start yazın.
                  </p>
                </div>
              </div>
            )}

            {!settings.bot_configured && (
              <div className="info-box warning">
                <span className="icon">ℹ️</span>
                <div>
                  <strong>Telegram Bot Yapılandırması Gerekli</strong>
                  <p>
                    Sunucu tarafında TELEGRAM_BOT_TOKEN ayarlanmalı.
                    Aşağıdaki kurulum rehberini takip edin.
                  </p>
                </div>
              </div>
            )}

            <div className="form-group">
              <label>Chat ID</label>
              <input
                type="text"
                placeholder="123456789"
                value={settings.telegram_chat_id || ''}
                onChange={(e) => setSettings({ ...settings, telegram_chat_id: e.target.value })}
              />
              <span className="form-help">
                Chat ID'nizi öğrenmek için{' '}
                <a href="https://t.me/userinfobot" target="_blank" rel="noopener noreferrer">
                  @userinfobot
                </a>
                {' '}botuna /start yazın.
              </span>
            </div>

            <div className="form-group toggle-group">
              <label>
                <span>Bildirimleri Etkinleştir</span>
                <input
                  type="checkbox"
                  checked={settings.telegram_enabled}
                  onChange={(e) => setSettings({ ...settings, telegram_enabled: e.target.checked })}
                  disabled={!settings.bot_configured}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div className="card-actions">
            <button 
              className="btn btn-secondary"
              onClick={handleTest}
              disabled={testing || !settings.telegram_chat_id || !settings.bot_configured}
            >
              {testing ? '⏳ Gönderiliyor...' : '📤 Test Mesajı Gönder'}
            </button>
            <button 
              className="btn btn-primary"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? '⏳ Kaydediliyor...' : '💾 Kaydet'}
            </button>
          </div>
        </div>

        {/* Tarayıcı Bildirimleri */}
        <div className="settings-card card">
          <div className="card-header">
            <h2>🔔 Tarayıcı Bildirimleri</h2>
            <span className={`status-badge ${pushEnabled ? 'active' : pushDenied ? 'denied' : 'inactive'}`}>
              {pushEnabled ? '✅ Aktif' : pushDenied ? '❌ Reddedildi' : '⚠️ İzin Gerekli'}
            </span>
          </div>

          <div className="card-content">
            {!pushSupported ? (
              <div className="info-box warning">
                <span className="icon">⚠️</span>
                <div>
                  <strong>Desteklenmiyor</strong>
                  <p>Tarayıcınız push bildirimlerini desteklemiyor.</p>
                </div>
              </div>
            ) : pushEnabled ? (
              <div className="info-box success">
                <span className="icon">✅</span>
                <div>
                  <strong>Bildirimler Aktif</strong>
                  <p>Yeni ilanlar ve fiyat değişiklikleri için tarayıcı bildirimi alacaksınız.</p>
                </div>
              </div>
            ) : pushDenied ? (
              <div className="info-box warning">
                <span className="icon">❌</span>
                <div>
                  <strong>İzin Reddedildi</strong>
                  <p>Bildirimleri etkinleştirmek için tarayıcı ayarlarından izin verin.</p>
                </div>
              </div>
            ) : (
              <div className="info-box">
                <span className="icon">🔔</span>
                <div>
                  <strong>Bildirimleri Etkinleştir</strong>
                  <p>Yeni ilanlar ve fiyat düşüşleri için anlık bildirim alın.</p>
                </div>
              </div>
            )}
          </div>

          <div className="card-actions">
            {pushEnabled ? (
              <button className="btn btn-secondary" onClick={handleTestPush}>
                📤 Test Bildirimi
              </button>
            ) : !pushDenied && pushSupported ? (
              <button className="btn btn-primary" onClick={handleEnablePush}>
                🔔 Bildirimleri Etkinleştir
              </button>
            ) : null}
          </div>
        </div>

        {/* Bildirim Türleri */}
        <div className="settings-card card">
          <div className="card-header">
            <h2>📋 Bildirim Türleri</h2>
          </div>

          <div className="card-content">
            <div className="notification-types">
              <div className="notification-type">
                <div className="type-icon">🆕</div>
                <div className="type-info">
                  <h3>Yeni İlan Bildirimi</h3>
                  <p>Filtrelerinize uygun yeni ilan bulunduğunda bildirim alın</p>
                </div>
                <span className="type-status active">Otomatik</span>
              </div>

              <div className="notification-type">
                <div className="type-icon">📉</div>
                <div className="type-info">
                  <h3>Fiyat Düşüşü Bildirimi</h3>
                  <p>Favorilerdeki ilanların fiyatı düştüğünde bildirim alın</p>
                </div>
                <span className="type-status active">Otomatik</span>
              </div>
            </div>
          </div>
        </div>

        {/* Kurulum Rehberi */}
        <div className="settings-card card full-width">
          <div className="card-header">
            <h2>📖 Telegram Bot Kurulum Rehberi</h2>
            <span className="badge free">%100 ÜCRETSİZ</span>
          </div>

          <div className="card-content">
            <div className="setup-steps">
              <div className="step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h3>Bot Oluştur</h3>
                  <p>
                    Telegram'da{' '}
                    <a href="https://t.me/BotFather" target="_blank" rel="noopener noreferrer">
                      @BotFather
                    </a>
                    {' '}botuna gidin ve <code>/newbot</code> yazın. Bot adı ve username belirleyin.
                  </p>
                </div>
              </div>

              <div className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h3>Token'ı Al</h3>
                  <p>
                    BotFather size bir token verecek. Bu token'ı kopyalayın:
                  </p>
                  <code className="example-token">
                    1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
                  </code>
                </div>
              </div>

              <div className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Sunucuya Ekle</h3>
                  <p>
                    Token'ı sunucuda environment variable olarak ayarlayın:
                  </p>
                  <code className="env-vars">
                    TELEGRAM_BOT_TOKEN=your_bot_token_here
                  </code>
                </div>
              </div>

              <div className="step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h3>Chat ID'ni Öğren</h3>
                  <p>
                    <a href="https://t.me/userinfobot" target="_blank" rel="noopener noreferrer">
                      @userinfobot
                    </a>
                    {' '}botuna <code>/start</code> yazın. Size Chat ID'nizi verecek.
                  </p>
                </div>
              </div>

              <div className="step">
                <div className="step-number">5</div>
                <div className="step-content">
                  <h3>Botu Başlat</h3>
                  <p>
                    Kendi botunuza gidin ve <code>/start</code> yazın.
                    Bu adım olmadan bot size mesaj gönderemez!
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
