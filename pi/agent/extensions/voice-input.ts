// voice-input — Ctrl+E records, second press posts the wav to local Phonon-2.

import fs from "node:fs";
import { spawn, type ChildProcess } from "node:child_process";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

// ---- Configuration ----

const WAV_FILE = "/tmp/pi-voice.wav";
const LOG_FILE = "/tmp/pi-voice-plugin.log";
const LOCAL_URL = process.env.PI_VOICE_URL || "http://127.0.0.1:8081/";
const STT_TOKEN =
	process.env.PHONON_TOKEN ||
	process.env.PI_BRIDGE_TOKEN ||
	(() => {
		try {
			return fs.readFileSync("/home/ed/.config/jot-stt.token", "utf8").trim();
		} catch {
			return "";
		}
	})();

// ctrl+e starts recording; second press sends. rename session stays on
// ctrl+alt+r in ~/.pi/agent/keybindings.json.
const SHORTCUT = "ctrl+e";

// Keep sox alive after stop so PulseAudio/BlueZ flushes the last words.
const STOP_GRACE_MS = Number(process.env.PI_VOICE_STOP_GRACE_MS) || 1500;

// ---- State ----

let soxProc: ChildProcess | null = null;
let recording = false;
let processing = false;
let piRef: ExtensionAPI | null = null;

function log(line: string) {
	try {
		fs.appendFileSync(LOG_FILE, `[${new Date().toISOString()}] ${line}\n`);
	} catch {
		// logging must never break voice input
	}
}
log("voice-input loaded " + LOCAL_URL);

// Recording: local sox by default. If PI_VOICE_REC_CMD is set, run that instead.
// If PI_VOICE_REC_URL is set (remote machine with no mic), start/stop an HTTP
// recorder that streams the mic from the machine that has it.
const REC_CMD = process.env.PI_VOICE_REC_CMD || "";
const REC_URL = process.env.PI_VOICE_REC_URL || "";
const BRIDGE_TOKEN = process.env.PI_BRIDGE_TOKEN || "";

function authHeaders(): Record<string, string> {
	const h: Record<string, string> = {};
	if (BRIDGE_TOKEN) h["X-Bridge-Token"] = BRIDGE_TOKEN;
	if (STT_TOKEN) h.Authorization = "Bearer " + STT_TOKEN;
	return h;
}

function startRecording(
	notify: (message: string, variant: "info" | "warning" | "error") => void,
) {
	if (soxProc || recording) return;
	try {
		fs.unlinkSync(WAV_FILE);
	} catch {
		// file may not exist yet
	}
	if (REC_URL) {
		recording = true;
		log("recording started via " + REC_URL);
		fetch(REC_URL + "/start", { headers: authHeaders(), signal: AbortSignal.timeout(8000) }).catch((err) => {
			recording = false;
			notify(`Recording failed: ${err.message}`, "error");
		});
		notify("Recording started — press Ctrl+E again to stop & send", "info");
		return;
	}
	let outFd: number | null = null;
	if (REC_CMD) {
		outFd = fs.openSync(WAV_FILE, "w");
		soxProc = spawn("bash", ["-c", REC_CMD], { stdio: ["ignore", outFd, "ignore"] });
	} else {
		soxProc = spawn(
			"sox",
			["-d", "-r", "16000", "-c", "1", "-b", "16", WAV_FILE, "silence", "1", "0.1", "1%"],
			{ stdio: ["ignore", "ignore", "ignore"] },
		);
	}
	soxProc.on("error", (err) => {
		if (outFd !== null) fs.closeSync(outFd);
		soxProc = null;
		recording = false;
		notify(`Recording failed: ${err.message}`, "error");
	});
	soxProc.on("exit", () => {
		if (outFd !== null) fs.closeSync(outFd);
		soxProc = null;
	});
	soxProc.on("exit", () => {
		soxProc = null;
	});
	recording = true;
	log("recording started");
	notify("Recording started — press Ctrl+E again to stop & send", "info");
}

async function stopRecording() {
	if (REC_URL) {
		const resp = await fetch(REC_URL + "/stop", { headers: authHeaders(), signal: AbortSignal.timeout(15000) });
		const buf = await resp.arrayBuffer();
		if (buf.byteLength > 44) fs.writeFileSync(WAV_FILE, Buffer.from(buf));
		return;
	}
	if (soxProc) soxProc.kill("SIGINT");
}

async function waitForSoxExit(timeoutMs = 2000) {
	const start = Date.now();
	while (soxProc && Date.now() - start < timeoutMs) {
		await new Promise((r) => setTimeout(r, 100));
	}
	if (soxProc) {
		try {
			soxProc.kill("SIGKILL");
		} catch {
			// ignore
		}
		soxProc = null;
	}
}

async function transcribe(): Promise<{ text?: string; error?: string }> {
	if (!fs.existsSync(WAV_FILE) || fs.statSync(WAV_FILE).size <= 44) return { error: "No speech detected" };
	try {
		const resp = await fetch(LOCAL_URL, {
			method: "POST",
			headers: authHeaders(),
			body: fs.readFileSync(WAV_FILE),
			signal: AbortSignal.timeout(1_620_000),
		});
		const text = (await resp.text()).trim();
		if (!resp.ok) return { error: text || `STT ${resp.status}` };
		if (!text) return { error: "No speech detected" };
		return { text };
	} catch (err) {
		const m = err instanceof Error ? err.message : String(err);
		log(`transcribe error: ${m}`);
		return { error: m };
	}
}

async function run(ctx: ExtensionContext, autoSend = false) {
	const notify = (message: string, variant: "info" | "warning" | "error") => {
		log(`notify: variant=${variant} msg=${message}`);
		try {
			ctx.ui.notify(message, variant);
		} catch (e) {
			log(`notify FAILED: ${e instanceof Error ? e.message : String(e)}`);
		}
	};

	if (ctx.mode !== "tui") {
		notify("Voice input only works in the interactive TUI", "warning");
		return;
	}
	if (processing) {
		log("run: busy, ignoring");
		notify("Voice is busy, please wait…", "warning");
		return;
	}

	log("run fired; recording=" + recording);
	if (recording) {
		processing = true;
		try {
			notify("Stopping — capturing trailing audio…", "info");
			await new Promise((r) => setTimeout(r, STOP_GRACE_MS));
			await stopRecording();
			await waitForSoxExit();
			log("sox stopped, starting transcription");
			notify("Transcribing your voice…", "info");
			const result = await transcribe();
			log(
				"transcribe result: " +
					(result.error ? "ERROR " + result.error : "OK len=" + (result.text || "").length + " text=" + JSON.stringify((result.text || "").slice(0, 80))),
			);
			if (result.error) {
				notify(result.error, "error");
			} else if (!result.text) {
				notify("No speech detected", "warning");
			} else {
				const existing = (ctx.ui.getEditorText?.() ?? "").trim();
				const merged = existing ? existing + " " + result.text : result.text;
				if (autoSend) {
					ctx.ui.setEditorText("");
					// steer = immediate, followUp = wait until turn ends. Ctrl+E should steer so agent sees it right away
					try {
						if (ctx.isIdle()) piRef?.sendUserMessage(merged);
						else piRef?.sendUserMessage(merged, { deliverAs: "steer" } as any);
					} catch (e: any) {
						const msg = e?.message || String(e);
						if (msg.includes("streamingBehavior") || msg.includes("deliverAs")) {
							piRef?.sendUserMessage(merged, { deliverAs: "steer" } as any);
						} else throw e;
					}
					notify("Sent: " + result.text.slice(0, 60), "info");
				} else {
					ctx.ui.setEditorText(merged);
					notify("Transcription added to input", "info");
				}
			}
		} catch (err) {
			const detail = err instanceof Error ? err.message : String(err);
			log(`pipeline error: ${detail}`);
			notify(`Voice error: ${detail}`, "error");
		} finally {
			processing = false;
			recording = false;
		}
	} else {
		startRecording(notify);
	}
}

export default function (pi: ExtensionAPI) {
	piRef = pi;
	pi.registerShortcut(SHORTCUT, {
		description: "Voice: start recording (Ctrl+E again = transcribe and send)",
		handler: async (ctx) => {
			await run(ctx as ExtensionContext, true);
		},
	});
	pi.registerShortcut("ctrl+r", {
		description: "Voice: stop recording, transcribe without send",
		handler: async (ctx) => {
			if (!recording) {
				return;
			}
			await run(ctx as ExtensionContext, false);
		},
	});

	pi.registerCommand("voice-record", {
		description: "Toggle voice recording; press again to transcribe and add to prompt",
		handler: async (_args, ctx) => {
			await run(ctx as ExtensionContext);
		},
	});

	pi.on("session_shutdown", () => {
		if (soxProc) {
			try {
				soxProc.kill("SIGKILL");
			} catch {
				// ignore
			}
			soxProc = null;
		}
		recording = false;
		processing = false;
	});

	log("voice-input command + shortcut registered (local)");
}
