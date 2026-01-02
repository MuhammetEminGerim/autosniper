"""
License Database Model
Stores activated license information
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class License(Base):
    """License model for storing activated licenses"""
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # License key
    license_key = Column(String, unique=True, index=True, nullable=False)
    
    # Hardware info
    hardware_id = Column(String, nullable=False)
    
    # Package info
    package_type = Column(String, nullable=False)  # monthly, yearly, lifetime
    
    # Dates
    issued_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    activated_at = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # User relationship (optional - eğer user sistemi varsa)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="license")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<License {self.package_type} - Expires: {self.expires_at}>"
    
    @property
    def is_expired(self) -> bool:
        """Check if license is expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def days_remaining(self) -> int:
        """Get days remaining until expiry"""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return delta.days
