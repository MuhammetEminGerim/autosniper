import React from 'react';
import './CarDamageDiagram.css';

interface DamageInfo {
  original?: string[];
  local_painted?: string[];
  painted?: string[];
  changed?: string[];
  unknown?: string[];
  tramer_amount?: string;
}

interface CarDamageDiagramProps {
  damageInfo: DamageInfo;
}

// Parça isimlerini SVG ID'lerine eşle
const partNameToId: Record<string, string> = {
  // Ön
  'Ön Tampon': 'front-bumper',
  'Motor Kaputu': 'hood',
  // Sol taraf
  'Sol Ön Çamurluk': 'left-front-fender',
  'Sol Ön Kapı': 'left-front-door',
  'Sol Arka Kapı': 'left-rear-door',
  'Sol Arka Çamurluk': 'left-rear-fender',
  // Sağ taraf
  'Sağ Ön Çamurluk': 'right-front-fender',
  'Sağ Ön Kapı': 'right-front-door',
  'Sağ Arka Kapı': 'right-rear-door',
  'Sağ Arka Çamurluk': 'right-rear-fender',
  // Arka
  'Arka Kaput': 'trunk',
  'Bagaj Kapağı': 'trunk',
  'Arka Tampon': 'rear-bumper',
  // Üst
  'Tavan': 'roof',
};

const CarDamageDiagram: React.FC<CarDamageDiagramProps> = ({ damageInfo }) => {
  // Her parça için renk belirle
  const getPartColor = (partId: string): string => {
    // Parça adını bul
    const partName = Object.keys(partNameToId).find(name => partNameToId[name] === partId);
    if (!partName) return '#E5E7EB'; // Varsayılan gri

    // Kategoriye göre renk
    if (damageInfo.original?.includes(partName)) return '#22C55E'; // Yeşil - Orijinal
    if (damageInfo.local_painted?.includes(partName)) return 'url(#stripe-pattern)'; // Çizgili - Lokal Boyalı
    if (damageInfo.painted?.includes(partName)) return '#F59E0B'; // Sarı/Turuncu - Boyalı
    if (damageInfo.changed?.includes(partName)) return '#EF4444'; // Kırmızı - Değişmiş
    if (damageInfo.unknown?.includes(partName)) return '#9CA3AF'; // Gri - Belirtilmemiş
    
    return '#E5E7EB'; // Varsayılan
  };

  return (
    <div className="car-damage-diagram">
      <svg viewBox="0 0 200 400" className="car-svg">
        <defs>
          {/* Lokal boyalı için çizgili desen */}
          <pattern id="stripe-pattern" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)">
            <rect width="4" height="8" fill="#F59E0B" />
            <rect x="4" width="4" height="8" fill="#FEF3C7" />
          </pattern>
        </defs>

        {/* Araç gövdesi - Üstten görünüm */}
        <g className="car-body">
          {/* Ön Tampon */}
          <path
            id="front-bumper"
            d="M 50 20 Q 100 5 150 20 L 150 40 L 50 40 Z"
            fill={getPartColor('front-bumper')}
            stroke="#374151"
            strokeWidth="1.5"
          />
          
          {/* Motor Kaputu */}
          <path
            id="hood"
            d="M 50 40 L 150 40 L 155 100 L 45 100 Z"
            fill={getPartColor('hood')}
            stroke="#374151"
            strokeWidth="1.5"
          />
          
          {/* Tavan */}
          <rect
            id="roof"
            x="55"
            y="150"
            width="90"
            height="100"
            rx="10"
            fill={getPartColor('roof')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Sol Ön Çamurluk */}
          <path
            id="left-front-fender"
            d="M 30 50 L 50 40 L 45 100 L 45 120 L 30 120 Q 20 85 30 50"
            fill={getPartColor('left-front-fender')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Sol Ön Kapı */}
          <rect
            id="left-front-door"
            x="30"
            y="120"
            width="25"
            height="75"
            rx="3"
            fill={getPartColor('left-front-door')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Sol Arka Kapı */}
          <rect
            id="left-rear-door"
            x="30"
            y="195"
            width="25"
            height="75"
            rx="3"
            fill={getPartColor('left-rear-door')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Sol Arka Çamurluk */}
          <path
            id="left-rear-fender"
            d="M 30 270 L 55 270 L 45 320 L 45 340 L 30 340 Q 20 305 30 270"
            fill={getPartColor('left-rear-fender')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Sağ Ön Çamurluk */}
          <path
            id="right-front-fender"
            d="M 170 50 L 150 40 L 155 100 L 155 120 L 170 120 Q 180 85 170 50"
            fill={getPartColor('right-front-fender')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Sağ Ön Kapı */}
          <rect
            id="right-front-door"
            x="145"
            y="120"
            width="25"
            height="75"
            rx="3"
            fill={getPartColor('right-front-door')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Sağ Arka Kapı */}
          <rect
            id="right-rear-door"
            x="145"
            y="195"
            width="25"
            height="75"
            rx="3"
            fill={getPartColor('right-rear-door')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Sağ Arka Çamurluk */}
          <path
            id="right-rear-fender"
            d="M 170 270 L 145 270 L 155 320 L 155 340 L 170 340 Q 180 305 170 270"
            fill={getPartColor('right-rear-fender')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Bagaj Kapağı / Arka Kaput */}
          <path
            id="trunk"
            d="M 45 300 L 155 300 L 150 350 L 50 350 Z"
            fill={getPartColor('trunk')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Arka Tampon */}
          <path
            id="rear-bumper"
            d="M 50 350 L 150 350 Q 100 380 50 350"
            fill={getPartColor('rear-bumper')}
            stroke="#374151"
            strokeWidth="1.5"
          />

          {/* Camlar (dekoratif) */}
          <rect x="60" y="105" width="80" height="40" rx="5" fill="#1F2937" opacity="0.3" />
          <rect x="60" y="255" width="80" height="40" rx="5" fill="#1F2937" opacity="0.3" />
        </g>
      </svg>

      {/* Legend */}
      <div className="damage-legend">
        <div className="legend-item">
          <span className="legend-dot original"></span>
          <span>Orijinal</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot painted"></span>
          <span>Boyalı</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot local-painted"></span>
          <span>Lokal Boyalı</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot changed"></span>
          <span>Değişmiş</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot unknown"></span>
          <span>Belirtilmemiş</span>
        </div>
      </div>
    </div>
  );
};

export default CarDamageDiagram;

