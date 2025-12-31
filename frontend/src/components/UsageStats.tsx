import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import './UsageStats.css'

interface UsageData {
    daily_search_count: number
    daily_search_limit: number
    subscription_tier: string
    max_filters: number
    current_filters: number
}

const UsageStats = () => {
    const navigate = useNavigate()
    const [usage, setUsage] = useState<UsageData | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchUsage()
    }, [])

    const fetchUsage = async () => {
        try {
            const response = await api.get('/api/auth/me')
            setUsage({
                daily_search_count: response.data.daily_search_count,
                daily_search_limit: response.data.daily_search_limit,
                subscription_tier: response.data.subscription_tier,
                max_filters: response.data.max_filters,
                current_filters: 0 // Bu filters endpoint'inden alınacak
            })
        } catch (error) {
            console.error('Kullanım bilgisi alınamadı:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading || !usage) {
        return <div className="usage-stats loading">Yükleniyor...</div>
    }

    const searchPercentage = (usage.daily_search_count / usage.daily_search_limit) * 100
    const remaining = usage.daily_search_limit - usage.daily_search_count

    const getTierColor = (tier: string) => {
        switch (tier) {
            case 'pro': return '#FFD700'
            case 'basic': return '#4A90E2'
            default: return '#95A5A6'
        }
    }

    const getTierLabel = (tier: string) => {
        switch (tier) {
            case 'pro': return '💎 Pro'
            case 'basic': return '⭐ Basic'
            default: return '🆓 Free'
        }
    }

    return (
        <div className="usage-stats">
            <div className="usage-header">
                <h3>Kullanım Durumu</h3>
                <span
                    className="tier-badge"
                    style={{ backgroundColor: getTierColor(usage.subscription_tier) }}
                >
                    {getTierLabel(usage.subscription_tier)}
                </span>
            </div>

            <div className="usage-item">
                <div className="usage-label">
                    <span>Günlük Arama</span>
                    <span className="usage-count">
                        {usage.daily_search_count} / {usage.daily_search_limit}
                    </span>
                </div>
                <div className="usage-bar">
                    <div
                        className={`usage-fill ${searchPercentage > 80 ? 'warning' : ''}`}
                        style={{ width: `${Math.min(searchPercentage, 100)}%` }}
                    />
                </div>
                <div className="usage-remaining">
                    {remaining > 0 ? (
                        <span className="remaining-text">
                            {remaining} arama hakkı kaldı
                        </span>
                    ) : (
                        <span className="limit-reached">
                            ⚠️ Günlük limit doldu
                        </span>
                    )}
                </div>
            </div>

            {searchPercentage > 80 && usage.subscription_tier === 'free' && (
                <button
                    className="upgrade-btn"
                    onClick={() => navigate('/pricing')}
                >
                    🚀 Upgrade Yap
                </button>
            )}

            {remaining === 0 && (
                <div className="limit-info">
                    <p>Limit gece 00:00'da sıfırlanacak</p>
                    <button
                        className="upgrade-btn-alt"
                        onClick={() => navigate('/pricing')}
                    >
                        Daha Fazla Arama İçin Upgrade
                    </button>
                </div>
            )}
        </div>
    )
}

export default UsageStats
