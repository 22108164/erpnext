const { app, BrowserWindow, nativeImage } = require("electron");
const path = require("node:path");
const Store = require("electron-store");

const store = new Store({
	defaults: {
		baseUrl: "http://127.0.0.1:8000",
		offlineMode: false,
		reloadIntervalMs: 20000
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

	loadTarget();
}

function loadTarget() {
	const baseUrl = store.get("baseUrl");
	const offlineMode = store.get("offlineMode");
	mainWindow
		.loadURL(baseUrl)
		.catch(() => {
			if (!offlineMode) {
				mainWindow.loadFile(path.join(__dirname, "offline.html"));
				setTimeout(loadTarget, store.get("reloadIntervalMs"));
			}
		});
}

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
