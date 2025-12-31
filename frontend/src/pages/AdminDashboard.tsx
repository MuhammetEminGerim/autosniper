import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';
import './Admin.css';

interface UserStats {
    id: number;
    email: string;
    subscription_tier: string;
    is_active: boolean;
    is_admin: boolean;
    created_at: string;
    last_login: string | null;
    filter_count: number;
    daily_search_count: number;
    daily_search_limit: number;
    max_filters: number;
}

interface SystemStats {
    total_users: number;
    active_users: number;
    total_filters: number;
    total_listings: number;
    new_users_today: number;
    new_users_this_week: number;
    searches_today: number;
    free_users: number;
    basic_users: number;
    pro_users: number;
}

const AdminDashboard: React.FC = () => {
    const navigate = useNavigate();
    const [users, setUsers] = useState<UserStats[]>([]);
    const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedUser, setSelectedUser] = useState<UserStats | null>(null);
    const [showEditModal, setShowEditModal] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [usersRes, statsRes] = await Promise.all([
                api.get('/api/admin/users'),
                api.get('/api/admin/stats')
            ]);
            setUsers(usersRes.data);
            setSystemStats(statsRes.data);
        } catch (error: any) {
            if (error.response?.status === 403) {
                toast.error('Admin yetkisi gerekli');
                navigate('/dashboard');
            } else {
                toast.error('Veriler yüklenirken hata oluştu');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateUser = async (userId: number, data: any) => {
        try {
            await api.put(`/api/admin/users/${userId}`, data);
            toast.success('Kullanıcı güncellendi');
            fetchData();
            setShowEditModal(false);
        } catch (error) {
            toast.error('Güncelleme başarısız');
        }
    };

    const handleDeleteUser = async (userId: number) => {
        if (!confirm('Bu kullanıcıyı silmek istediğinizden emin misiniz?')) return;

        try {
            await api.delete(`/api/admin/users/${userId}`);
            toast.success('Kullanıcı silindi');
            fetchData();
        } catch (error) {
            toast.error('Silme başarısız');
        }
    };

    const getTierBadge = (tier: string) => {
        const badges: any = {
            free: { label: 'FREE', color: '#6c757d' },
            basic: { label: 'BASIC', color: '#0d6efd' },
            pro: { label: 'PRO', color: '#ffc107' }
        };
        const badge = badges[tier] || badges.free;
        return (
            <span className="tier-badge" style={{ backgroundColor: badge.color }}>
                {badge.label}
            </span>
        );
    };

    if (loading) {
        return <div className="admin-loading">Yükleniyor...</div>;
    }

    return (
        <div className="admin-dashboard">
            <div className="admin-header">
                <h1>🛡️ Admin Panel</h1>
                <button onClick={() => navigate('/dashboard')} className="btn-back">
                    ← Ana Sayfa
                </button>
            </div>

            {/* System Stats */}
            {systemStats && (
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon">👥</div>
                        <div className="stat-content">
                            <div className="stat-value">{systemStats.total_users}</div>
                            <div className="stat-label">Toplam Kullanıcı</div>
                            <div className="stat-sub">Aktif: {systemStats.active_users}</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">🔍</div>
                        <div className="stat-content">
                            <div className="stat-value">{systemStats.total_filters}</div>
                            <div className="stat-label">Toplam Filtre</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">📋</div>
                        <div className="stat-content">
                            <div className="stat-value">{systemStats.total_listings}</div>
                            <div className="stat-label">Toplam İlan</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">🔥</div>
                        <div className="stat-content">
                            <div className="stat-value">{systemStats.searches_today}</div>
                            <div className="stat-label">Bugünkü Aramalar</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">🆓</div>
                        <div className="stat-content">
                            <div className="stat-value">{systemStats.free_users}</div>
                            <div className="stat-label">Free Kullanıcı</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">⭐</div>
                        <div className="stat-content">
                            <div className="stat-value">{systemStats.basic_users}</div>
                            <div className="stat-label">Basic Kullanıcı</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">💎</div>
                        <div className="stat-content">
                            <div className="stat-value">{systemStats.pro_users}</div>
                            <div className="stat-label">Pro Kullanıcı</div>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">📈</div>
                        <div className="stat-content">
                            <div className="stat-value">{systemStats.new_users_this_week}</div>
                            <div className="stat-label">Bu Hafta Yeni</div>
                            <div className="stat-sub">Bugün: {systemStats.new_users_today}</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Users Table */}
            <div className="users-section">
                <h2>Kullanıcılar ({users.length})</h2>
                <div className="table-container">
                    <table className="users-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Email</th>
                                <th>Paket</th>
                                <th>Filtre</th>
                                <th>Arama</th>
                                <th>Kayıt Tarihi</th>
                                <th>Son Giriş</th>
                                <th>Durum</th>
                                <th>İşlemler</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td>{user.id}</td>
                                    <td>
                                        {user.email}
                                        {user.is_admin && <span className="admin-badge">ADMIN</span>}
                                    </td>
                                    <td>{getTierBadge(user.subscription_tier)}</td>
                                    <td>{user.filter_count} / {user.max_filters}</td>
                                    <td>{user.daily_search_count} / {user.daily_search_limit}</td>
                                    <td>{new Date(user.created_at).toLocaleDateString('tr-TR')}</td>
                                    <td>
                                        {user.last_login
                                            ? new Date(user.last_login).toLocaleDateString('tr-TR')
                                            : '-'
                                        }
                                    </td>
                                    <td>
                                        <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                                            {user.is_active ? 'Aktif' : 'Pasif'}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="action-buttons">
                                            <button
                                                onClick={() => {
                                                    setSelectedUser(user);
                                                    setShowEditModal(true);
                                                }}
                                                className="btn-edit"
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                onClick={() => handleDeleteUser(user.id)}
                                                className="btn-delete"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Edit Modal */}
            {showEditModal && selectedUser && (
                <EditUserModal
                    user={selectedUser}
                    onClose={() => setShowEditModal(false)}
                    onSave={handleUpdateUser}
                />
            )}
        </div>
    );
};

// Edit User Modal Component
const EditUserModal: React.FC<{
    user: UserStats;
    onClose: () => void;
    onSave: (userId: number, data: any) => void;
}> = ({ user, onClose, onSave }) => {
    const [tier, setTier] = useState(user.subscription_tier);
    const [isActive, setIsActive] = useState(user.is_active);
    const [isAdmin, setIsAdmin] = useState(user.is_admin);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave(user.id, {
            subscription_tier: tier,
            is_active: isActive,
            is_admin: isAdmin
        });
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Kullanıcı Düzenle</h3>
                    <button onClick={onClose} className="modal-close">×</button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Email</label>
                        <input type="text" value={user.email} disabled />
                    </div>

                    <div className="form-group">
                        <label>Paket</label>
                        <select value={tier} onChange={(e) => setTier(e.target.value)}>
                            <option value="free">Free (50 arama/gün, 5 filtre)</option>
                            <option value="basic">Basic (500 arama/gün, 20 filtre)</option>
                            <option value="pro">Pro (2000 arama/gün, sınırsız filtre)</option>
                        </select>
                    </div>

                    <div className="form-group checkbox-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={isActive}
                                onChange={(e) => setIsActive(e.target.checked)}
                            />
                            Aktif
                        </label>
                    </div>

                    <div className="form-group checkbox-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={isAdmin}
                                onChange={(e) => setIsAdmin(e.target.checked)}
                            />
                            Admin Yetkisi
                        </label>
                    </div>

                    <div className="modal-actions">
                        <button type="button" onClick={onClose} className="btn-cancel">
                            İptal
                        </button>
                        <button type="submit" className="btn-save">
                            Kaydet
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AdminDashboard;
