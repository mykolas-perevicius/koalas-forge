const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        icon: path.join(__dirname, 'icon.png'),
        title: 'Koala\'s Forge Dashboard'
    });

    // Load the dashboard from local server
    mainWindow.loadURL('http://localhost:8080');

    // Create application menu
    const template = [
        {
            label: 'Koala\'s Forge',
            submenu: [
                {
                    label: 'About',
                    click: () => {
                        const aboutWindow = new BrowserWindow({
                            width: 400,
                            height: 300,
                            parent: mainWindow,
                            modal: true,
                            webPreferences: {
                                nodeIntegration: true
                            }
                        });
                        aboutWindow.loadURL(`data:text/html,
                            <html>
                                <body style="font-family: -apple-system, sans-serif; padding: 20px;">
                                    <h2>🐨 Koala's Forge</h2>
                                    <p>Version 1.9.0</p>
                                    <p>Intelligent Package Management System</p>
                                    <p>© 2025 Koala's Forge</p>
                                </body>
                            </html>
                        `);
                    }
                },
                { type: 'separator' },
                { role: 'quit' }
            ]
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' }
            ]
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'forceReload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        {
            label: 'Tools',
            submenu: [
                {
                    label: 'Run Self-Test',
                    click: () => {
                        mainWindow.webContents.executeJavaScript(`runCommand('self-test')`);
                    }
                },
                {
                    label: 'Check Dependencies',
                    click: () => {
                        mainWindow.webContents.executeJavaScript(`checkDependencies()`);
                    }
                },
                {
                    label: 'Create Snapshot',
                    click: () => {
                        mainWindow.webContents.executeJavaScript(`createSnapshot()`);
                    }
                },
                { type: 'separator' },
                {
                    label: 'Export Setup',
                    click: () => {
                        mainWindow.webContents.executeJavaScript(`exportPackages()`);
                    }
                }
            ]
        },
        {
            label: 'Window',
            submenu: [
                { role: 'minimize' },
                { role: 'close' }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);

    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// App ready
app.whenReady().then(createWindow);

// Quit when all windows are closed
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Create window if activated and none exists
app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});