// voice — pi speaks its replies as they stream (Paradee, ~/i/paradee/voice.py) and takes voice calls.
// ctrl+e: voice call; talk any time, talking over pi cuts it off. ctrl+r: dictate; press again to send.
// ctrl+s: stop pi talking; when quiet, read the part after ||| aloud; in a call, mute your mic.
// /speak on|off toggles speaking replies outside calls.

import { spawn } from "node:child_process";
import fs from "node:fs";
import net from "node:net";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

const DIR = "/home/ed/i/paradee";
const SOCK = "/tmp/paradee.sock";
const FLAG = "/home/ed/.pi/speak";
const CALL_PROMPT =
	"\n\nVOICE CALL: the user is talking to you and hears your reply as speech. Reply in short plain spoken English only. No markdown, tables, lists, code, headings, TLDR or ||| split. Two to five short sentences. Sound like you are talking, not writing.";
const BOUNDARY = /[.!?…](?=\s)|\n/g;

let api: ExtensionAPI;
let ui: ExtensionContext | null = null;
let tui = false;
let gen = 0;
let chain = Promise.resolve();
let starting: Promise<boolean> | null = null;
let spoken_to = 0;
let silenced = false;
let streaming = false;
let call: net.Socket | null = null;
let rec: net.Socket | null = null;
let muted = false;

function send(msg: string): Promise<string | null> {
	return new Promise((resolve) => {
		let out = "";
		const c = net.connect(SOCK, () => c.end(msg));
		c.setEncoding("utf8");
		c.on("data", (d) => (out += d));
		c.on("error", () => {});
		c.on("close", (failed) => resolve(failed ? null : out));
	});
}

function daemon(): Promise<boolean> {
	starting ??= (async () => {
		if ((await send("ping\n")) !== null) return true;
		spawn(`${DIR}/.venv/bin/python`, [`${DIR}/voice.py`, "--serve"], {
			stdio: "ignore",
			detached: true,
			env: { ...process.env, HF_HUB_OFFLINE: "1" },
		}).unref();
		for (let i = 0; i < 60; i++) {
			await new Promise((r) => setTimeout(r, 500));
			if ((await send("ping\n")) !== null) return true;
		}
		return false;
	})().finally(() => (starting = null));
	return starting;
}

function say(text: string) {
	const my = gen;
	chain = chain.then(async () => {
		if (my === gen && (await send(`q\n${text}`)) === null && (await daemon()) && my === gen) await send(`q\n${text}`);
	});
}

function hush() {
	gen++;
	void send("stop\n");
}

// scripted runs (pi -p, rpc) stay silent
function speaking(): boolean {
	if (call) return true;
	if (!tui) return false;
	try {
		return fs.readFileSync(FLAG, "utf8").trim() !== "off";
	} catch {
		return true;
	}
}

const blank = (m: string) => " ".repeat(m.length);
const mask_fences = (t: string) => t.replace(/```[\s\S]*?```/g, blank);
const mask = (t: string) => mask_fences(t).replace(/`[^`\n]*`/g, blank);

function clean(text: string): string {
	return text
		.replace(/```[\s\S]*?```/g, " ")
		.replace(/^\s*[-+]\s+/, "")
		.replace(/`([^`]*)`/g, (_, code: string) => (code.length <= 30 ? code : " "))
		.replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
		.replace(/https?:\/\/\S+/g, "link")
		.replace(/[*#>|]/g, "")
		.replace(/_/g, " ")
		.replace(/\(\s*\)|\[\s*\]/g, "")
		.replace(/\s+/g, " ")
		.replace(/\s+([,.!?;:])/g, "$1")
		.trim();
}

function sentences(raw: string): string[] {
	const out: string[] = [];
	let at = 0;
	for (const m of mask(raw).matchAll(BOUNDARY)) {
		out.push(raw.slice(at, m.index! + 1));
		at = m.index! + 1;
	}
	out.push(raw.slice(at));
	return out.map(clean).filter((s) => /[\p{L}\p{N}]/u.test(s));
}

// the spoken part is before |||; while pi is still writing, stop at code that is not closed yet
function speakable(full: string, done: boolean): string {
	let raw = full.split("|||")[0];
	const fence = mask_fences(raw).indexOf("```");
	if (fence !== -1) raw = raw.slice(0, fence);
	const tick = done ? -1 : mask(raw).indexOf("`");
	return tick === -1 ? raw : raw.slice(0, tick);
}

function speak_new(full: string, done: boolean) {
	const raw = speakable(full, done);
	let end = done ? raw.length : spoken_to;
	if (!done) for (const m of mask(raw).matchAll(BOUNDARY)) end = Math.max(end, m.index! + 1);
	if (end <= spoken_to) return;
	for (const s of sentences(raw.slice(spoken_to, end))) say(s);
	spoken_to = end;
}

function text_of(content: unknown): string {
	if (typeof content === "string") return content;
	if (!Array.isArray(content)) return "";
	return content
		.filter((b: any) => b.type === "text")
		.map((b: any) => b.text)
		.join("\n");
}

function last_reply(ctx: ExtensionContext): string {
	for (const e of ctx.sessionManager.getBranch().reverse() as any[]) {
		if (e.type === "message" && e.message?.role === "assistant" && text_of(e.message.content).trim()) return text_of(e.message.content);
	}
	return "";
}

function show(text?: string) {
	ui?.ui.setStatus("voice", text);
}

// while pi is busy, a plain send fails; steer queues it into the run
function deliver(text: string) {
	if (ui?.isIdle()) api.sendUserMessage(text);
	else api.sendUserMessage(text, { deliverAs: "steer" });
}

function on_event(line: string) {
	const i = line.indexOf(" ");
	const kind = i === -1 ? line : line.slice(0, i);
	const arg = i === -1 ? "" : line.slice(i + 1);
	if (kind === "speech") {
		silenced = true;
		hush();
		return show("voice: hearing you");
	}
	if (kind === "heard") return show("voice: transcribing");
	if (kind === "ready" && arg === "noaec") ui?.ui.notify("No echo cancelling: pi can't hear you while it talks. Headphones avoid this.", "warning");
	if (kind === "error") ui?.ui.notify(arg, "error");
	// noise, not words: let pi carry on talking
	if (kind === "drop") silenced = false;
	if (kind === "text") deliver(arg);
	show(muted ? "voice: muted" : "voice: listening");
}

async function toggle_call(ctx: ExtensionContext) {
	ui = ctx;
	if (call) return void call.end();
	if (rec) return ctx.ui.notify("Finish dictating first (ctrl+r)", "warning");
	show("voice: connecting");
	if (!(await daemon())) {
		show();
		return ctx.ui.notify("Voice daemon did not start", "error");
	}
	if (call) return;
	hush();
	silenced = true;
	muted = false;
	const c = net.connect(SOCK, () => c.write("listen\n"));
	call = c;
	let buf = "";
	c.setEncoding("utf8");
	c.on("data", (d) => {
		buf += d;
		for (let i = buf.indexOf("\n"); i !== -1; i = buf.indexOf("\n")) {
			on_event(buf.slice(0, i));
			buf = buf.slice(i + 1);
		}
	});
	c.on("error", () => {});
	c.on("close", () => {
		if (call !== c) return;
		call = null;
		show();
		ctx.ui.notify("Voice call ended", "info");
	});
}

async function dictate(ctx: ExtensionContext) {
	ui = ctx;
	if (call) return ctx.ui.notify("Dictation is off during a voice call", "warning");
	if (rec) {
		rec.write("stop\n");
		return show("voice: transcribing");
	}
	if (!(await daemon())) return ctx.ui.notify("Voice daemon did not start", "error");
	if (rec || call) return;
	silenced = true;
	hush();
	const c = net.connect(SOCK, () => c.write("rec\n"));
	rec = c;
	show("voice: recording, ctrl+r to send");
	let out = "";
	c.setEncoding("utf8");
	c.on("data", (d) => (out += d));
	c.on("error", () => {});
	c.on("close", () => {
		if (rec !== c) return;
		rec = null;
		show();
		if (out.startsWith("text ")) {
			deliver(`${ctx.ui.getEditorText().trim()} ${out.slice(5).trim()}`.trim());
			ctx.ui.setEditorText("");
		} else if (out.startsWith("error ")) ctx.ui.notify(out.slice(6).trim(), "error");
		else ctx.ui.notify("No speech heard", "warning");
	});
}

async function ctrl_s(ctx: ExtensionContext) {
	ui = ctx;
	if (call) {
		muted = !muted;
		call.write(muted ? "mute\n" : "unmute\n");
		return show(muted ? "voice: muted" : "voice: listening");
	}
	if ((streaming && speaking() && !silenced) || (await send("status\n")) === "1") {
		silenced = true;
		return hush();
	}
	const text = last_reply(ctx);
	for (const s of sentences(text.includes("|||") ? text.slice(text.indexOf("|||") + 3) : text)) say(s);
}

export default function voice(pi: ExtensionAPI) {
	api = pi;

	pi.on("session_start", async (_event, ctx) => {
		tui = ctx.mode === "tui";
		if (speaking()) void daemon();
	});

	pi.on("session_shutdown", async () => {
		const open = [call, rec];
		call = rec = null;
		for (const c of open) c?.destroy();
		show();
	});

	pi.on("before_agent_start", async (event) => {
		if (call) return { systemPrompt: event.systemPrompt + CALL_PROMPT };
	});

	pi.on("agent_start", async () => {
		hush();
		silenced = false;
	});

	pi.on("message_start", async (event) => {
		if (event.message.role === "user") silenced = false;
		if (event.message.role !== "assistant") return;
		spoken_to = 0;
		streaming = true;
	});

	pi.on("message_update", async (event) => {
		if (event.message.role !== "assistant" || event.assistantMessageEvent.type !== "text_delta") return;
		if (speaking() && !silenced) speak_new(text_of(event.message.content), false);
	});

	pi.on("message_end", async (event) => {
		if (event.message.role !== "assistant") return;
		streaming = false;
		if ((event.message as any).stopReason === "aborted") {
			silenced = true;
			return hush();
		}
		if (speaking() && !silenced) speak_new(text_of(event.message.content), true);
	});

	pi.registerShortcut("ctrl+e", {
		description: "Voice call: talk to pi hands-free; talk over it to cut it off",
		handler: async (ctx) => toggle_call(ctx),
	});

	pi.registerShortcut("ctrl+r", {
		description: "Dictate a message; press again to send it",
		handler: async (ctx) => dictate(ctx),
	});

	pi.registerShortcut("ctrl+s", {
		description: "Stop pi talking; when quiet, read the part after ||| aloud; in a call, mute your mic",
		handler: async (ctx) => ctrl_s(ctx),
	});

	pi.registerCommand("voice", {
		description: "Toggle a voice call (ctrl+e)",
		handler: async (_args, ctx) => toggle_call(ctx),
	});

	pi.registerCommand("voice-record", {
		description: "Dictate a message (ctrl+r)",
		handler: async (_args, ctx) => dictate(ctx),
	});

	pi.registerCommand("speak", {
		description: "Toggle speaking replies out loud",
		handler: async (args, ctx) => {
			const on = args?.trim() ? args.trim() === "on" : !speaking();
			fs.writeFileSync(FLAG, on ? "on\n" : "off\n");
			if (on) void daemon();
			else hush();
			ctx.ui.notify(`speaking ${on ? "on" : "off"}`, "info");
		},
	});
}
