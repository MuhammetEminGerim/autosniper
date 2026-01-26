import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import './LicenseActivation.css';

interface ElectronAPI {
    saveLicenseKey: (key: string) => Promise<{ success: boolean }>;
    getLicenseKey: () => Promise<string | null>;
    getBackendURL: () => Promise<string>;
}

declare global {
    interface Window {
        electronAPI?: ElectronAPI;
    }
}

export default function LicenseActivation() {
    const [licenseKey, setLicenseKey] = useState('');
    const [hardwareId, setHardwareId] = useState('');
    const [loading, setLoading] = useState(false);
    const [isElectron, setIsElectron] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Electron'da mı kontrol et
        setIsElectron(!!window.electronAPI);

        // Hardware ID al
        fetchHardwareId();

        // Mevcut lisans var mı kontrol et
        checkExistingLicense();
    }, []);

    const fetchHardwareId = async () => {
        try {
            const backendURL = window.electronAPI
                ? await window.electronAPI.getBackendURL()
                : 'http://localhost:8000';

            const response = await fetch(`${backendURL}/api/license/hardware-id`);
            const data = await response.json();
            setHardwareId(data.hardware_id);
        } catch (error) {
            console.error('Hardware ID alınamadı:', error);
        }
    };

    const checkExistingLicense = async () => {
        try {
            if (window.electronAPI) {
                const existingKey = await window.electronAPI.getLicenseKey();
                if (existingKey) {
                    // Mevcut lisansı doğrula
                    await validateLicense(existingKey);
                }
            }
        } catch (error) {
            console.error('Lisans kontrolü hatası:', error);
        }
    };

    const validateLicense = async (key: string) => {
        try {
            const backendURL = window.electronAPI
                ? await window.electronAPI.getBackendURL()
                : 'http://localhost:8000';

            const response = await fetch(`${backendURL}/api/license/activate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ license_key: key })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Lisans geçerli, kaydet ve yönlendir
                if (window.electronAPI) {
                    await window.electronAPI.saveLicenseKey(key);
                }
                toast.success(data.message);
                navigate('/dashboard');
            } else {
                toast.error(data.detail || data.message || 'Lisans geçersiz');
            }
        } catch (error: any) {
            toast.error('Lisans doğrulama hatası');
        }
    };

    const handleActivate = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!licenseKey.trim()) {
            toast.error('Lütfen lisans key\'inizi girin');
            return;
        }

        if (!licenseKey.startsWith('AUTOSNIPER-')) {
            toast.error('Geçersiz lisans formatı');
            return;
        }

        setLoading(true);
        await validateLicense(licenseKey);
        setLoading(false);
    };

    const copyHardwareId = () => {
        navigator.clipboard.writeText(hardwareId);
        toast.success('Hardware ID kopyalandı!');
    };

    return (
        <div className="license-activation">
            <div className="license-container">
                <div className="license-header">
                    <h1>🔐 AutoSniper Aktivasyonu</h1>
                    <p>Lisans key'inizi girerek uygulamayı aktif edin</p>
                </div>

                <form onSubmit={handleActivate} className="license-form">
                    <div className="form-group">
                        <label>Lisans Key</label>
                        <input
                            type="text"
                            value={licenseKey}
                            onChange={(e) => setLicenseKey(e.target.value)}
                            placeholder="AUTOSNIPER-XXXX-XXXX-XXXX-XXXX"
                            className="license-input"
                            disabled={loading}
                        />
                        <small>Satın aldığınız lisans key'ini buraya yapıştırın</small>
                    </div>

                    <div className="form-group">
                        <label>Hardware ID</label>
                        <div className="hardware-id-box">
                            <code>{hardwareId || 'Yükleniyor...'}</code>
                            {hardwareId && (
                                <button
                                    type="button"
                                    onClick={copyHardwareId}
                                    className="copy-btn"
                                    title="Kopyala"
                                >
                                    📋
                                </button>
                            )}
                        </div>
                        <small>Bu ID'yi lisans satın alırken kullanın</small>
                    </div>

                    <button
                        type="submit"
                        className="activate-btn"
                        disabled={loading}
                    >
                        {loading ? 'Doğrulanıyor...' : 'Aktif Et'}
                    </button>
                </form>

                <div className="license-footer">
                    <p>Henüz lisansınız yok mu?</p>
                    <div className="contact-info">
                        <p>📞 <strong>WhatsApp/Telefon:</strong> [Telefon Numaranız]</p>
                        <p>💳 <strong>IBAN:</strong> [IBAN Numaranız]</p>
                        <p>📦 <strong>Paketler:</strong></p>
                        <ul>
                            <li>Aylık: ₺299</li>
                            <li>Yıllık: ₺1.999</li>
                            <li>Lifetime: ₺4.999</li>
                        </ul>
                        <p><em>Hardware ID'nizi yukarıdaki kopyala butonu ile kopyalayıp bize gönderin</em></p>
                    </div>
                </div>

                {!isElectron && (
                    <div className="electron-warning">
                        ⚠️ Desktop uygulamasında değilsiniz. Lisans sistemi sadece desktop app'te çalışır.
                    </div>
                )}
            </div>
        </div>
    );
}
