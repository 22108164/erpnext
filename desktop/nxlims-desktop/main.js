const { app, BrowserWindow, Menu, ipcMain, nativeImage } = require("electron");
const path = require("node:path");
const Store = require("electron-store");
const { v4: uuidv4 } = require("uuid");

const store = new Store({
	defaults: {
		baseUrl: "http://127.0.0.1:8000",
		offlineMode: false,
		reloadIntervalMs: 20000,
		deviceId: uuidv4()
	}
});

let mainWindow;

function createWindow() {
	const icon = nativeImage.createFromPath(path.join(__dirname, "assets", "icon.ico"));
	mainWindow = new BrowserWindow({
		width: 1400,
		height: 920,
		minWidth: 1024,
		minHeight: 720,
		icon,
		backgroundColor: "#f2f7fa",
		webPreferences: {
			preload: path.join(__dirname, "preload.js"),
			contextIsolation: true,
			nodeIntegration: false,
			sandbox: true
		}
	});

	// Create application menu
	createMenu();

	loadTarget();

	mainWindow.webContents.on("crashed", () => {
		mainWindow.destroy();
		createWindow();
	});
}

function createMenu() {
	const template = [
		{
			label: "NxLIMS",
			submenu: [
				{
					label: "About NxLIMS",
					accelerator: "CmdOrCtrl+I",
					click: () => {
						mainWindow.webContents.send("open-about");
					}
				},
				{
					label: "Settings",
					accelerator: "CmdOrCtrl+,",
					click: () => {
						mainWindow.webContents.send("open-settings");
					}
				},
				{ type: "separator" },
				{ label: "Exit", accelerator: "CmdOrCtrl+Q", click: () => app.quit() }
			]
		},
		{
			label: "Edit",
			submenu: [
				{ role: "undo" },
				{ role: "redo" },
				{ type: "separator" },
				{ role: "cut" },
				{ role: "copy" },
				{ role: "paste" }
			]
		},
		{
			label: "View",
			submenu: [
				{
					label: "Reload",
					accelerator: "CmdOrCtrl+R",
					click: () => mainWindow.webContents.reload()
				},
				{
					label: "Force Reload",
					accelerator: "CmdOrCtrl+Shift+R",
					click: () => mainWindow.webContents.reloadIgnoringCache()
				},
				{
					label: "Toggle Developer Tools",
					accelerator: process.platform === "darwin" ? "Alt+Cmd+I" : "Ctrl+Shift+I",
					click: () => mainWindow.webContents.toggleDevTools()
				}
			]
		},
		{
			label: "Help",
			submenu: [
				{
					label: "Documentation",
					click: () => {
						mainWindow.webContents.send("open-documentation");
					}
				}
			]
		}
	];

	Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

function loadTarget() {
	const baseUrl = store.get("baseUrl");
	const offlineMode = store.get("offlineMode");

	mainWindow
		.loadURL(baseUrl)
		.then(() => {
			mainWindow.webContents.send("connection-status", { online: true });
		})
		.catch(() => {
			if (!offlineMode) {
				mainWindow.loadFile(path.join(__dirname, "offline.html"));
				mainWindow.webContents.send("connection-status", { online: false });
				setTimeout(loadTarget, store.get("reloadIntervalMs"));
			}
		});
}

// IPC Handlers
ipcMain.handle("get-device-id", () => store.get("deviceId"));

ipcMain.handle("get-base-url", () => store.get("baseUrl"));

ipcMain.handle("set-base-url", (event, url) => {
	store.set("baseUrl", url);
	setTimeout(() => loadTarget(), 1000);
	return { success: true };
});

ipcMain.handle("get-offline-mode", () => store.get("offlineMode"));

ipcMain.handle("set-offline-mode", (event, enabled) => {
	store.set("offlineMode", enabled);
	return { success: true };
});

ipcMain.handle("get-sync-interval", () => store.get("reloadIntervalMs"));

ipcMain.handle("set-sync-interval", (event, interval) => {
	store.set("reloadIntervalMs", Math.max(5000, interval));
	return { success: true };
});

app.whenReady().then(() => {
	createWindow();

	app.on("activate", () => {
		if (BrowserWindow.getAllWindows().length === 0) {
			createWindow();
		}
	});
});

app.on("window-all-closed", () => {
	if (process.platform !== "darwin") {
		app.quit();
	}
});

