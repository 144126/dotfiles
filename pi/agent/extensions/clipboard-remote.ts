// clipboard-remote — Ctrl+V on a remote machine (no local clipboard) fetches the
// user's clipboard image/text from the laptop via the recorder-daemon bridge.
// Only activates inside ssh sessions; on the local machine pi's built-in paste wins.

import fs from "node:fs";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

const BRIDGE = process.env.PI_CLIPBOARD_URL || "http://127.0.0.1:18083";
const BRIDGE_TOKEN = process.env.PI_BRIDGE_TOKEN || "";

function authHeaders(): Record<string, string> {
	return BRIDGE_TOKEN ? { "X-Bridge-Token": BRIDGE_TOKEN } : {};
}

export default function clipboardRemote(pi: ExtensionAPI) {
	if (!process.env.SSH_CONNECTION) return; // local: don't hijack Ctrl+V, let pi's built-in wl-paste handler win
	pi.registerShortcut("ctrl+v", {
		description: "Paste image/text from the local (laptop) clipboard over ssh",
		handler: async (ctx) => {
			const c = ctx as ExtensionContext;
			try {
				const img = await fetch(`${BRIDGE}/clipboard/image`, { headers: authHeaders(), signal: AbortSignal.timeout(8000) });
				if (img.ok) {
					const mime = img.headers.get("content-type") || "image/png";
					const ext = mime.includes("jpeg") ? "jpg" : mime.includes("webp") ? "webp" : mime.includes("gif") ? "gif" : "png";
					const file = `/tmp/pi-clipboard-${crypto.randomUUID()}.${ext}`;
					fs.writeFileSync(file, Buffer.from(await img.arrayBuffer()));
					append(c, file);
					c.ui.notify("image pasted from laptop clipboard", "info");
					return;
				}
				const txt = await fetch(`${BRIDGE}/clipboard/text`, { headers: authHeaders(), signal: AbortSignal.timeout(8000) });
				if (txt.ok) {
					const text = (await txt.text()).trim();
					if (text) {
						append(c, text);
						return;
					}
				}
			} catch {
				// bridge down (no ssh session / no VPN): fall through quietly
			}
		},
	});
}

function append(ctx: ExtensionContext, text: string) {
	const existing = (ctx.ui.getEditorText?.() ?? "").trim();
	ctx.ui.setEditorText(existing ? `${existing} ${text}` : text);
}
