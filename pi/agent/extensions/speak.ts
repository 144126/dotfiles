// speak — reads pi's assistant replies out loud as they stream, via the warm paradee server.
// Toggle with /speak. Skips code blocks and anything after |||.

import { spawn } from "node:child_process";
import fs from "node:fs";
import net from "node:net";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const PARADEE = "/home/ed/i/paradee";
const SOCK = "/tmp/paradee.sock";
const FLAG = "/home/ed/.pi/speak";
const VOICE_FLAG = "/home/ed/.pi/voice-mode";
// when set (remote machines), tts is synthesized+played on the laptop via bridge
const TTS_URL = process.env.PI_TTS_URL || "";
const BRIDGE_TOKEN = process.env.PI_BRIDGE_TOKEN || "";

function authHeaders(): Record<string, string> {
	return BRIDGE_TOKEN ? { "X-Bridge-Token": BRIDGE_TOKEN } : {};
}

function speaking(): boolean {
	try {
		if (fs.readFileSync(VOICE_FLAG, "utf8").trim() === "on") return false;
	} catch {
		// voice mode off
	}
	try {
		return fs.readFileSync(FLAG, "utf8").trim() !== "off";
	} catch {
		return true;
	}
}

function setSpeaking(on: boolean) {
	fs.writeFileSync(FLAG, on ? "on\n" : "off\n");
}

function stopSpeaking() {
	if (TTS_URL) {
		fetch(`${TTS_URL}/say-stop`, { headers: authHeaders(), signal: AbortSignal.timeout(5000) }).catch(() => {});
		return;
	}
	queue = Promise.resolve();
	paradee("stop\n");
}

function paradee(msg: string): Promise<boolean> {
	return new Promise((resolve) => {
		const c = net.connect(SOCK, () => c.end(msg));
		c.on("close", () => resolve(true));
		c.on("error", () => resolve(false));
	});
}

let queue = Promise.resolve();

function enqueue(text: string) {
	queue = queue.then(async () => {
		if (await paradee(`q\n${text}`)) return;
		// server down: start it and wait for the model to load
		spawn(`${PARADEE}/.venv/bin/python`, [`${PARADEE}/say.py`, "--serve"], {
			stdio: "ignore",
			detached: true,
			env: { ...process.env, HF_HUB_OFFLINE: "1" },
		}).unref();
		for (let i = 0; i < 40; i++) {
			await new Promise((r) => setTimeout(r, 500));
			if (await paradee(`q\n${text}`)) return;
		}
	});
}

// blank out code so sentence ends inside it are ignored, keeping offsets
const blank = (m: string) => " ".repeat(m.length);
const maskFences = (text: string) => text.replace(/```[\s\S]*?```/g, blank);
const mask = (text: string) => maskFences(text).replace(/`[^`\n]*`/g, blank);

let spokenTo = 0;

function speakNew(full: string, done: boolean) {
	let raw = ttsPart(full);
	const open = maskFences(raw).indexOf("```");
	if (open !== -1) raw = raw.slice(0, open);
	let end = done ? raw.length : -1;
	if (!done) {
		const re = /[.!?:;](?=\s)|\n/g;
		re.lastIndex = spokenTo;
		const m = mask(raw);
		for (let x; (x = re.exec(m)); ) end = x.index + 1;
	}
	if (end <= spokenTo) return;
	const spoken = clean(raw.slice(spokenTo, end));
	spokenTo = end;
	if (spoken.length >= 2) enqueue(spoken);
}

function textOf(content: unknown): string {
	return typeof content === "string"
		? content
		: Array.isArray(content)
			? content
					.filter((b: any) => b.type === "text")
					.map((b: any) => b.text)
					.join("\n")
			: "";
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
	pi.on("agent_start", async () => {
		if (!TTS_URL) stopSpeaking(); // new prompt: drop the old reply
	});

	pi.on("message_start", async () => {
		spokenTo = 0;
	});

	pi.on("message_update", async (event) => {
		if (TTS_URL || !speaking() || event.message.role !== "assistant") return;
		if (event.assistantMessageEvent.type !== "text_delta") return;
		speakNew(textOf(event.message.content), false);
	});

	pi.on("message_end", async (event) => {
		if (!speaking() || event.message.role !== "assistant") return;
		const text = textOf(event.message.content);
		if (!TTS_URL) return speakNew(text, true);
		const spoken = clean(ttsPart(text));
		if (spoken.length < 2) return;
		stopSpeaking(); // one voice at a time
		// remote: laptop synthesizes and plays on its own speakers
		fetch(`${TTS_URL}/say`, {
			method: "POST",
			headers: authHeaders(),
			body: spoken,
			signal: AbortSignal.timeout(10000),
		}).catch(() => {});
	});

	pi.registerShortcut("ctrl+s", {
		description: "Stop text-to-speech playback",
		handler: async (ctx) => {
			stopSpeaking();
			ctx.ui.notify("tts stopped", "info");
		},
	});

	pi.registerCommand("speak", {
		description: "Toggle speaking replies out loud",
		handler: async (args, ctx) => {
			const on = args?.trim() ? args.trim() === "on" : !speaking();
			setSpeaking(on);
			if (!on) stopSpeaking();
			ctx.ui.notify(`speaking ${on ? "on" : "off"}`, "info");
		},
	});
}
