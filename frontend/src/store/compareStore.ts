import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Listing {
  id: number
  title: string
  price: number
  year: number | null
  brand: string | null
  model: string | null
  city: string | null
  fuel_type: string | null
  transmission: string | null
  mileage: number | null
  images: string[] | null
  source_url: string
  damage_info?: any
}

interface CompareState {
  listings: Listing[]
  addToCompare: (listing: Listing) => boolean
  removeFromCompare: (listingId: number) => void
  clearCompare: () => void
  isInCompare: (listingId: number) => boolean
}

export const useCompareStore = create<CompareState>()(
  persist(
    (set, get) => ({
      listings: [],
      
      addToCompare: (listing: Listing) => {
        const current = get().listings
        if (current.length >= 3) {
          return false // Max 3 ilan
        }
        if (current.find(l => l.id === listing.id)) {
          return false // Zaten var
        }
        set({ listings: [...current, listing] })
        return true
      },
      
      removeFromCompare: (listingId: number) => {
        set({ listings: get().listings.filter(l => l.id !== listingId) })
      },
      
      clearCompare: () => {
        set({ listings: [] })
      },
      
      isInCompare: (listingId: number) => {
        return get().listings.some(l => l.id === listingId)
      }
    }),
    {
      name: 'compare-storage'
    }
  )
)

