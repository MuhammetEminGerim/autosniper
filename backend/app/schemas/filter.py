from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class FilterCreate(BaseModel):
    name: str
    criteria: Dict[str, Any]  # JSON kriterler
    is_active: bool = True
    auto_scan_enabled: bool = False
    scan_interval: int = 30  # Dakika

class FilterUpdate(BaseModel):
    name: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    auto_scan_enabled: Optional[bool] = None
    scan_interval: Optional[int] = None

class FilterResponse(BaseModel):
    id: int
    user_id: int
    name: str
    criteria: Dict[str, Any]
    is_active: bool
    created_at: datetime
    auto_scan_enabled: bool = False
    scan_interval: int = 30
    last_scan_at: Optional[datetime] = None
    next_scan_at: Optional[datetime] = None
    total_scans: int = 0
    new_listings_found: int = 0

    class Config:
        from_attributes = True

class SchedulerToggle(BaseModel):
    enabled: bool
    interval: int = 30  # 15, 30, 60, 120, 360, 720, 1440

class SchedulerStatus(BaseModel):
    filter_id: int
    filter_name: str
    auto_scan_enabled: bool
    scan_interval: int
    last_scan_at: Optional[datetime] = None
    next_scan_at: Optional[datetime] = None
    total_scans: int = 0
    new_listings_found: int = 0

