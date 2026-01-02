import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LicenseExpired.css';

export default function LicenseExpired() {
    const navigate = useNavigate();

    useEffect(() => {
        // Lisans durumunu kontrol et
        checkLicenseStatus();
    }, []);

    const checkLicenseStatus = async () => {
        try {
            const backendURL = window.electronAPI
                ? await window.electronAPI.getBackendURL()
                : 'http://localhost:8000';

            const response = await fetch(`${backendURL}/api/license/status`);

            if (response.ok) {
                // Lisans geçerli, dashboard'a yönlendir
                navigate('/dashboard');
            }
        } catch (error) {
            // Lisans geçersiz, bu sayfada kal
        }
    };

    const handleRenew = () => {
        window.open('https://autosniper.com/pricing', '_blank');
    };

    const handleNewLicense = () => {
        navigate('/license-activation');
    };

    return (
        <div className="license-expired">
            <div className="expired-container">
                <div className="expired-icon">⏰</div>

                <h1>Lisans Süresi Doldu</h1>
                <p className="expired-message">
                    AutoSniper lisansınızın süresi dolmuş. Uygulamayı kullanmaya devam etmek için
                    lisansınızı yenileyin veya yeni bir lisans satın alın.
                </p>

                <div className="expired-actions">
                    <button onClick={handleRenew} className="renew-btn">
                        🔄 Lisansı Yenile
                    </button>
                    <button onClick={handleNewLicense} className="new-license-btn">
                        🔑 Yeni Lisans Gir
                    </button>
                </div>

                <div className="expired-footer">
                    <p>Sorularınız mı var?</p>
                    <a href="mailto:support@autosniper.com">
                        Destek ekibiyle iletişime geçin →
                    </a>
                </div>
            </div>
        </div>
    );
}
