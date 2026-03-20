const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("nxlims", {
	app: "NxLIMS Desktop"
});
