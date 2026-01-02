/**
 * AutoSniper Desktop App - Main Process
 * Electron ana süreç - window yönetimi, backend başlatma, lisans kontrolü
 */

const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Simple config storage (JSON file instead of electron-store)
const configPath = path.join(app.getPath('userData'), 'config.json');

function getConfig() {
    try {
        if (fs.existsSync(configPath)) {
            return JSON.parse(fs.readFileSync(configPath, 'utf8'));
        }
    } catch (e) {
        console.error('Config read error:', e);
    }
    return {};
}

function setConfig(key, value) {
    const config = getConfig();
    config[key] = value;
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}

let mainWindow = null;
let backendProcess = null;
let tray = null;

// Backend port
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

/**
 * Backend subprocess başlat
 */
function startBackend() {
    console.log('Starting backend...');

    // Development modda Python çalıştır
    if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
        const backendPath = path.join(__dirname, '..', 'backend');
        console.log('Backend path:', backendPath);

        backendProcess = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--reload', '--port', String(BACKEND_PORT)], {
            cwd: backendPath,
            shell: true,
            stdio: 'inherit'
        });
    } else {
        // Production modda packaged backend .exe çalıştır
        const backendExe = path.join(process.resourcesPath, 'backend', 'autosniper-backend.exe');
        console.log('Backend exe:', backendExe);

        backendProcess = spawn(backendExe, [], {
            shell: true,
            stdio: 'inherit'
        });
    }

    if (backendProcess) {
        backendProcess.on('error', (err) => {
            console.error('Backend start error:', err);
        });

        backendProcess.on('close', (code) => {
            console.log(`Backend exited with code ${code}`);
        });
    }
}

/**
 * Backend'i durdur
 */
function stopBackend() {
    if (backendProcess) {
        console.log('Stopping backend...');
        backendProcess.kill();
        backendProcess = null;
    }
}

/**
 * Ana pencereyi oluştur
 */
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        },
        icon: path.join(__dirname, '..', 'build', 'icon.png'),
        title: 'AutoSniper',
        show: false // Hazır olunca göster
    });

    // Development modda localhost:3000, production'da dist klasörü
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'));
    }

    // Hazır olunca göster
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Kapatıldığında
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

/**
 * System tray oluştur
 */
function createTray() {
    const iconPath = path.join(__dirname, '..', 'build', 'icon.png');
    tray = new Tray(iconPath);

    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'AutoSniper Aç',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                } else {
                    createWindow();
                }
            }
        },
        {
            label: 'Lisans Bilgisi',
            click: () => {
                const licenseKey = store.get('licenseKey');
                if (licenseKey) {
                    // TODO: Lisans bilgisini göster
                    console.log('License:', licenseKey);
                } else {
                    console.log('No license found');
                }
            }
        },
        { type: 'separator' },
        {
            label: 'Çıkış',
            click: () => {
                app.quit();
            }
        }
    ]);

    tray.setToolTip('AutoSniper');
    tray.setContextMenu(contextMenu);

    // Tray'e tıklandığında pencereyi göster
    tray.on('click', () => {
        if (mainWindow) {
            mainWindow.show();
        } else {
            createWindow();
        }
    });
}

/**
 * IPC Handlers
 */

// Lisans key kaydet
ipcMain.handle('save-license-key', async (event, licenseKey) => {
    setConfig('licenseKey', licenseKey);
    return { success: true };
});

// Lisans key oku
ipcMain.handle('get-license-key', async () => {
    const config = getConfig();
    return config.licenseKey || null;
});

// Lisans key sil
ipcMain.handle('delete-license-key', async () => {
    const config = getConfig();
    delete config.licenseKey;
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    return { success: true };
});

// Backend URL al
ipcMain.handle('get-backend-url', async () => {
    return BACKEND_URL;
});

/**
 * App lifecycle
 */

app.whenReady().then(() => {
    // Backend başlat
    startBackend();

    // Backend'in hazır olmasını bekle (3 saniye)
    setTimeout(() => {
        createWindow();
        createTray();
    }, 3000);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    // macOS'ta app menüde kalır
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    stopBackend();
});

app.on('will-quit', () => {
    stopBackend();
});
