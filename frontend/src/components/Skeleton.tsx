import React from 'react';
import './Skeleton.css';

interface SkeletonProps {
  type: 'card' | 'stat' | 'text' | 'image' | 'avatar';
  count?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({ type, count = 1 }) => {
  const items = Array.from({ length: count }, (_, i) => i);

  if (type === 'card') {
    return (
      <>
        {items.map((i) => (
          <div key={i} className="skeleton-card" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className="skeleton-card-image skeleton"></div>
            <div className="skeleton-card-content">
              <div className="skeleton skeleton-title"></div>
              <div className="skeleton skeleton-price"></div>
              <div className="skeleton-tags">
                <div className="skeleton skeleton-tag"></div>
                <div className="skeleton skeleton-tag"></div>
                <div className="skeleton skeleton-tag"></div>
              </div>
            </div>
          </div>
        ))}
      </>
    );
  }

  if (type === 'stat') {
    return (
      <>
        {items.map((i) => (
          <div key={i} className="skeleton-stat" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className="skeleton skeleton-stat-icon"></div>
            <div className="skeleton-stat-content">
              <div className="skeleton skeleton-stat-value"></div>
              <div className="skeleton skeleton-stat-label"></div>
            </div>
          </div>
        ))}
      </>
    );
  }

  if (type === 'text') {
    return (
      <>
        {items.map((i) => (
          <div 
            key={i} 
            className="skeleton skeleton-text" 
            style={{ 
              animationDelay: `${i * 0.05}s`,
              width: i === items.length - 1 ? '60%' : '100%'
            }}
          ></div>
        ))}
      </>
    );
  }

  if (type === 'image') {
    return <div className="skeleton skeleton-image"></div>;
  }

  if (type === 'avatar') {
    return <div className="skeleton skeleton-avatar"></div>;
  }

  return null;
};

export const CardSkeletonGrid: React.FC<{ count?: number }> = ({ count = 6 }) => {
  return (
    <div className="skeleton-grid">
      <Skeleton type="card" count={count} />
    </div>
  );
};

export const StatSkeletonGrid: React.FC<{ count?: number }> = ({ count = 4 }) => {
  return (
    <div className="skeleton-stats-grid">
      <Skeleton type="stat" count={count} />
    </div>
  );
};

