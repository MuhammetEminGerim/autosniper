from typing import Dict, Any, List
from app.models.listing import Listing
from app.models.filter import Filter

class FilterMatcher:
    """Filtre kriterlerine göre ilanları eşleştir"""
    
    @staticmethod
    def matches(listing: Listing, filter_obj: Filter) -> bool:
        """
        İlanın filtre kriterlerine uyup uymadığını kontrol et
        
        Args:
            listing: Kontrol edilecek ilan
            filter_obj: Filtre objesi
        
        Returns:
            True eğer ilan filtreye uyuyorsa
        """
        criteria = filter_obj.criteria
        
        # Marka kontrolü
        if criteria.get("brand") and listing.brand:
            if criteria["brand"].lower() not in listing.brand.lower():
                return False
        
        # Model kontrolü
        if criteria.get("model") and listing.model:
            if criteria["model"].lower() not in listing.model.lower():
                return False
        
        # Yıl kontrolü
        if listing.year:
            if criteria.get("min_year") and listing.year < criteria["min_year"]:
                return False
            if criteria.get("max_year") and listing.year > criteria["max_year"]:
                return False
        
        # Fiyat kontrolü
        if listing.price:
            if criteria.get("min_price") and listing.price < criteria["min_price"]:
                return False
            if criteria.get("max_price") and listing.price > criteria["max_price"]:
                return False
        
        # Şehir kontrolü
        if criteria.get("city") and listing.city:
            if criteria["city"].lower() not in listing.city.lower():
                return False
        
        # Yakıt tipi kontrolü
        if criteria.get("fuel_type") and listing.fuel_type:
            if criteria["fuel_type"].lower() != listing.fuel_type.lower():
                return False
        
        # Şanzıman kontrolü
        if criteria.get("transmission") and listing.transmission:
            if criteria["transmission"].lower() != listing.transmission.lower():
                return False
        
        return True
    
    @staticmethod
    def find_matching_filters(listing: Listing, filters: List[Filter]) -> List[Filter]:
        """
        Bir ilana uyan tüm filtreleri bul
        
        Args:
            listing: İlan
            filters: Kontrol edilecek filtreler
        
        Returns:
            Uyan filtrelerin listesi
        """
        matching = []
        for filter_obj in filters:
            if filter_obj.is_active and FilterMatcher.matches(listing, filter_obj):
                matching.append(filter_obj)
        return matching

