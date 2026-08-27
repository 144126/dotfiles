// speak — reads pi's assistant replies out loud via local piper (~/.local/bin/say).
// Toggle with /speak. Skips code blocks and long text.

import { spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const SAY = "/home/ed/.local/bin/say";
// when set (remote machines), tts is synthesized+played on the laptop via bridge
const TTS_URL = process.env.PI_TTS_URL || "";
const BRIDGE_TOKEN = process.env.PI_BRIDGE_TOKEN || "";

function authHeaders(): Record<string, string> {
	return BRIDGE_TOKEN ? { "X-Bridge-Token": BRIDGE_TOKEN } : {};
}

let enabled = true;
let sayProc: ChildProcess | null = null;

function stopSpeaking() {
	if (TTS_URL) {
		fetch(`${TTS_URL}/say-stop`, { headers: authHeaders(), signal: AbortSignal.timeout(5000) }).catch(() => {});
		return;
	}
	if (sayProc) {
		sayProc.kill("SIGKILL");
		sayProc = null;
	}
	if (fs.existsSync(SAY)) {
		spawn(SAY, ["--stop"], { stdio: "ignore", detached: true }).unref();
	}
}

function ttsPart(text: string): string {
	const i = text.indexOf("|||");
	return i === -1 ? text : text.slice(0, i);
}

function clean(text: string): string {
	return text
		.replace(/```[\s\S]*?```/g, " ")
		.replace(/`[^`]*`/g, " ")
		.replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
		.replace(/[*_#>|]/g, "")
		.replace(/\r?\n+/g, " ")
		.replace(/\s+/g, " ")
		.replace(/\s*([,.!?;:])\s*/g, "$1 ")
		.replace(/\s{2,}/g, " ")
		.trim();
}

export default function speak(pi: ExtensionAPI) {
	pi.on("message_end", async (event) => {
		if (!enabled || event.message.role !== "assistant") return;
		const content = event.message.content;
		const text =
			typeof content === "string"
				? content
				: Array.isArray(content)
					? content
							.filter((b: any) => b.type === "text")
							.map((b: any) => b.text)
							.join(" ")
					: "";
		const spoken = clean(ttsPart(text));
		if (spoken.length < 2) return;
		stopSpeaking(); // one voice at a time
		if (TTS_URL) {
			// remote: laptop synthesizes and plays on its own speakers
			fetch(`${TTS_URL}/say`, {
				method: "POST",
				headers: authHeaders(),
				body: spoken,
				signal: AbortSignal.timeout(10000),
			}).catch(() => {});
			return;
		}
		if (!fs.existsSync(SAY)) return; // no tts available: stay silent, never crash
		sayProc = spawn(SAY, [spoken], {
			stdio: "ignore",
			detached: true,
		});
		sayProc.unref();
	});

	pi.registerShortcut("ctrl+s", {
		description: "Stop text-to-speech playback",
		handler: async (ctx) => {
			if (!sayProc && !TTS_URL) return;
			stopSpeaking();
			ctx.ui.notify("tts stopped", "info");
		},
	});

	pi.registerCommand("speak", {
		description: "Toggle speaking replies out loud",
		handler: async (args, ctx) => {
			enabled = args?.trim() ? args.trim() === "on" : !enabled;
			ctx.ui.notify(`speaking ${enabled ? "on" : "off"}`, "info");
		},
	});
}
