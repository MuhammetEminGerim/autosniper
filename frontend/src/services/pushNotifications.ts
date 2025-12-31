/**
 * Browser Push Notifications Service
 * Tarayıcı bildirimleri için servis
 */

class PushNotificationService {
  private permission: NotificationPermission = 'default'

  constructor() {
    if ('Notification' in window) {
      this.permission = Notification.permission
    }
  }

  /**
   * Bildirim izni durumunu kontrol et
   */
  get isSupported(): boolean {
    return 'Notification' in window
  }

  get isEnabled(): boolean {
    return this.permission === 'granted'
  }

  get isDenied(): boolean {
    return this.permission === 'denied'
  }

  /**
   * Bildirim izni iste
   */
  async requestPermission(): Promise<boolean> {
    if (!this.isSupported) {
      console.warn('Push notifications not supported')
      return false
    }

    try {
      const permission = await Notification.requestPermission()
      this.permission = permission
      return permission === 'granted'
    } catch (error) {
      console.error('Error requesting notification permission:', error)
      return false
    }
  }

  /**
   * Bildirim gönder
   */
  async notify(title: string, options?: NotificationOptions): Promise<void> {
    if (!this.isEnabled) {
      console.warn('Notifications not enabled')
      return
    }

    try {
      const notification = new Notification(title, {
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        ...options
      })

      // Tıklanınca odaklan
      notification.onclick = () => {
        window.focus()
        notification.close()
      }

      // 5 saniye sonra otomatik kapat
      setTimeout(() => notification.close(), 5000)
    } catch (error) {
      console.error('Error showing notification:', error)
    }
  }

  /**
   * Yeni ilan bildirimi
   */
  async notifyNewListings(filterName: string, count: number): Promise<void> {
    await this.notify(`🚗 ${count} Yeni İlan!`, {
      body: `"${filterName}" filtrenizde ${count} yeni ilan bulundu.`,
      tag: 'new-listings'
    })
  }

  /**
   * Fiyat düşüşü bildirimi
   */
  async notifyPriceDrop(
    listingTitle: string,
    oldPrice: number,
    newPrice: number
  ): Promise<void> {
    const change = oldPrice - newPrice
    const changeStr = change.toLocaleString('tr-TR')
    
    await this.notify('📉 Fiyat Düştü!', {
      body: `${listingTitle}\n${changeStr} TL indirim!`,
      tag: 'price-drop'
    })
  }
}

export const pushNotifications = new PushNotificationService()
export default pushNotifications

