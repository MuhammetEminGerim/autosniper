/**
 * AutoSniper Desktop App - Preload Script
 * Renderer process ile main process arasında güvenli köprü
 */

const { contextBridge, ipcRenderer } = require('electron');

// API'yi renderer process'e expose et
contextBridge.exposeInMainWorld('electronAPI', {
    // Lisans işlemleri
    saveLicenseKey: (licenseKey) => ipcRenderer.invoke('save-license-key', licenseKey),
    getLicenseKey: () => ipcRenderer.invoke('get-license-key'),
    deleteLicenseKey: () => ipcRenderer.invoke('delete-license-key'),

    // Backend URL
    getBackendURL: () => ipcRenderer.invoke('get-backend-url'),

    // Platform bilgisi
    platform: process.platform,

    // Versiyon bilgisi
    versions: {
        node: process.versions.node,
        chrome: process.versions.chrome,
        electron: process.versions.electron
    }
});

console.log('Preload script loaded');
