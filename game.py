"""Math game for kids: find all integer pairs that sum to a target.

Run with: python3 game.py
Then open http://localhost:8000 in your browser.
"""

import errno
import http.server
import json
import os
import random
import signal
import socketserver
import subprocess
import threading
import time
import webbrowser

PORT = 8000
LOTTIE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lottie")


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>
<title>Sum Hunter</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: linear-gradient(135deg, #ffd86b 0%, #ff7a91 100%);
    min-height: 100vh;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 24px;
    color: #2b2b3d;
  }
  .card {
    background: #fff;
    border-radius: 24px;
    padding: 28px 32px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.18);
    width: 100%;
    max-width: 520px;
  }
  h1 { margin: 0 0 4px; font-size: 28px; }
  .subtitle { margin: 0 0 20px; color: #666; font-size: 15px; }
  .target-box {
    text-align: center;
    background: #f4f0ff;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 18px;
  }
  .target-label { font-size: 14px; color: #6a5acd; letter-spacing: 1px; }
  .target-number { font-size: 64px; font-weight: 800; color: #5b3fce; line-height: 1; }
  .progress { font-size: 14px; color: #666; margin-top: 4px; }
  .input-row {
    display: flex;
    gap: 10px;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;
  }
  input[type=number] {
    width: 90px;
    font-size: 28px;
    padding: 8px 10px;
    text-align: center;
    border: 2px solid #d8d0f5;
    border-radius: 12px;
    outline: none;
    -moz-appearance: textfield;
    appearance: textfield;
  }
  input[type=number]::-webkit-inner-spin-button,
  input[type=number]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  input[type=number]:focus { border-color: #5b3fce; }
  .plus { font-size: 28px; font-weight: 700; color: #5b3fce; }
  button {
    font-size: 16px;
    font-weight: 600;
    padding: 10px 18px;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    transition: transform .05s ease, background .15s ease;
  }
  button:active { transform: scale(0.97); }
  .btn-primary { background: #5b3fce; color: #fff; }
  .btn-primary:hover { background: #4a32ad; }
  .btn-ghost { background: #f0eaff; color: #5b3fce; }
  .btn-ghost:hover { background: #e3d9ff; }
  .feedback {
    min-height: 44px;
    margin: 8px 0 16px;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 15px;
    text-align: center;
  }
  .feedback.correct { background: #e3fbe1; color: #1f7a2e; }
  .feedback.wrong { background: #ffe1e6; color: #b3203a; }
  .feedback.duplicate { background: #fff4d6; color: #8a5a00; }
  .feedback.invalid { background: #fff4d6; color: #8a5a00; }
  .feedback.win { background: #f0eaff; color: #5b3fce; font-weight: 700; font-size: 18px; }
  .found-title { font-size: 14px; color: #888; margin-bottom: 6px; }
  .found-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    min-height: 36px;
  }
  .pair-chip {
    background: #e3fbe1;
    color: #1f7a2e;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 15px;
  }
  .top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .confetti-canvas {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 9999;
  }
  .win-overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 6vh;
    pointer-events: none;
    z-index: 10000;
    transition: opacity .8s ease, transform .8s ease;
  }
  .win-overlay.fade-out { opacity: 0; transform: scale(1.15); }
  .win-text {
    font-size: 52px;
    font-weight: 900;
    color: #fff;
    text-align: center;
    padding: 12px 26px;
    border-radius: 18px;
    background: linear-gradient(135deg, #ff7a91, #ffd86b 50%, #5b3fce);
    box-shadow: 0 18px 50px rgba(91, 63, 206, 0.4);
    text-shadow: 0 3px 0 rgba(0,0,0,0.18);
    animation: pop 0.9s cubic-bezier(.34, 1.56, .64, 1), wiggle 1.2s ease-in-out 0.9s infinite;
  }
  @keyframes pop {
    0% { transform: scale(0) rotate(-20deg); }
    60% { transform: scale(1.2) rotate(6deg); }
    100% { transform: scale(1) rotate(0); }
  }
  @keyframes wiggle {
    0%, 100% { transform: rotate(-2deg) scale(1); }
    50% { transform: rotate(2deg) scale(1.04); }
  }
  .target-number.celebrate {
    animation: target-pulse 0.6s ease infinite alternate;
  }
  @keyframes target-pulse {
    from { transform: scale(1); color: #5b3fce; }
    to { transform: scale(1.15); color: #ff7a91; }
  }

  /* Dance scene */
  .animal-stage {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9998;
    overflow: hidden;
  }
  .dance-floor {
    position: absolute;
    left: 0; right: 0;
    bottom: 0;
    height: 240px;
    background: linear-gradient(180deg, transparent 0%, rgba(255,122,145,0.25) 40%, rgba(91,63,206,0.45) 100%);
    animation: floor-flash 0.5s ease infinite alternate;
  }
  @keyframes floor-flash {
    from { filter: hue-rotate(0deg) brightness(1); }
    to   { filter: hue-rotate(80deg) brightness(1.3); }
  }
  .lottie-dancer {
    position: absolute;
    left: 50%;
    bottom: 60px;
    width: min(70vmin, 560px);
    height: min(70vmin, 560px);
    animation: dancer-entry 0.7s ease-out both;
  }
  @keyframes dancer-entry {
    from { opacity: 0; transform: translate(-50%, 80px) scale(0.6); }
    to   { opacity: 1; transform: translate(-50%, 0) scale(1); }
  }
  .music-note {
    position: absolute;
    font-size: 32px;
    opacity: 0;
    animation: note-rise 3s linear forwards;
  }
  @keyframes note-rise {
    0%   { opacity: 0; transform: translateY(0) rotate(0); }
    15%  { opacity: 1; }
    100% { opacity: 0; transform: translateY(-300px) rotate(20deg); }
  }
</style>
</head>
<body>
  <div class="card">
    <div class="top-row">
      <div>
        <h1>Sum Hunter</h1>
        <p class="subtitle">Find every pair of different numbers that adds up to the target.</p>
      </div>
      <button id="new-game" class="btn-ghost">New game</button>
    </div>

    <div class="target-box">
      <div class="target-label">TARGET</div>
      <div id="target" class="target-number">--</div>
      <div id="progress" class="progress">Loading...</div>
    </div>

    <form id="guess-form">
      <div class="input-row">
        <input id="a" type="number" inputmode="numeric" required autocomplete="off" />
        <span class="plus">+</span>
        <input id="b" type="number" inputmode="numeric" required autocomplete="off" />
        <button type="submit" class="btn-primary">Check</button>
      </div>
    </form>

    <div id="feedback" class="feedback"></div>

    <div class="found-title">Pairs you found</div>
    <div id="found" class="found-list"></div>
  </div>

<script>
  const targetEl = document.getElementById('target');
  const progressEl = document.getElementById('progress');
  const feedbackEl = document.getElementById('feedback');
  const foundEl = document.getElementById('found');
  const aInput = document.getElementById('a');
  const bInput = document.getElementById('b');
  const form = document.getElementById('guess-form');
  const newGameBtn = document.getElementById('new-game');

  let totalPairs = 0;
  let won = false;
  let audioCtx = null;

  function getAudio() {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return null;
    if (!audioCtx) audioCtx = new Ctx();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    return audioCtx;
  }

  function playCorrectSound() {
    const ctx = getAudio();
    if (!ctx) return;
    const now = ctx.currentTime;
    const notes = [
      { f: 659.25, t: 0.00, d: 0.12 },  // E5
      { f: 987.77, t: 0.07, d: 0.20 },  // B5
    ];
    for (const n of notes) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(n.f, now + n.t);
      gain.gain.setValueAtTime(0, now + n.t);
      gain.gain.linearRampToValueAtTime(0.20, now + n.t + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.001, now + n.t + n.d);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now + n.t);
      osc.stop(now + n.t + n.d + 0.05);
    }
  }

  function playWrongSound() {
    const ctx = getAudio();
    if (!ctx) return;
    const now = ctx.currentTime;
    const notes = [
      { f: 329.63, t: 0.00, d: 0.13 },  // E4
      { f: 246.94, t: 0.10, d: 0.22 },  // B3 (descending fourth)
    ];
    for (const n of notes) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(n.f, now + n.t);
      gain.gain.setValueAtTime(0, now + n.t);
      gain.gain.linearRampToValueAtTime(0.16, now + n.t + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, now + n.t + n.d);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now + n.t);
      osc.stop(now + n.t + n.d + 0.05);
    }
  }

  function playWinSound() {
    const ctx = getAudio();
    if (!ctx) return;
    const now = ctx.currentTime;

    // Ascending fanfare: C5 - E5 - G5 - C6 (sustained)
    const notes = [
      { f: 523.25, t: 0.00, d: 0.20 },
      { f: 659.25, t: 0.12, d: 0.20 },
      { f: 783.99, t: 0.24, d: 0.24 },
      { f: 1046.50, t: 0.40, d: 0.85 },
    ];
    for (const n of notes) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(n.f, now + n.t);
      gain.gain.setValueAtTime(0, now + n.t);
      gain.gain.linearRampToValueAtTime(0.25, now + n.t + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, now + n.t + n.d);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now + n.t);
      osc.stop(now + n.t + n.d + 0.05);
    }

    // Sparkle layer: random high blips
    for (let i = 0; i < 8; i++) {
      const t = 0.45 + Math.random() * 0.9;
      const f = 1600 + Math.random() * 1800;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(f, now + t);
      gain.gain.setValueAtTime(0, now + t);
      gain.gain.linearRampToValueAtTime(0.08, now + t + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, now + t + 0.18);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now + t);
      osc.stop(now + t + 0.22);
    }
  }

  const LOTTIE_FILES = [
    'cats_dance.json',
    'cat_playing.json',
    'cat_box.json',
    'shiba_happy.json',
    'shiba_relax.json',
    'dog.json',
  ];
  const NOTES = ['🎵', '🎶', '🎼', '✨', '⭐'];

  function runAnimalAnimation() {
    const stage = document.createElement('div');
    stage.className = 'animal-stage';
    document.body.appendChild(stage);

    const floor = document.createElement('div');
    floor.className = 'dance-floor';
    stage.appendChild(floor);

    const picked = LOTTIE_FILES[Math.floor(Math.random() * LOTTIE_FILES.length)];
    const slot = document.createElement('div');
    slot.className = 'lottie-dancer';
    stage.appendChild(slot);

    if (window.lottie) {
      try {
        lottie.loadAnimation({
          container: slot,
          renderer: 'svg',
          loop: true,
          autoplay: true,
          path: '/lottie/' + picked,
        });
      } catch (e) {
        console.warn('lottie load failed for', picked, e);
      }
    }

    const noteInterval = setInterval(() => {
      const n = document.createElement('div');
      n.className = 'music-note';
      n.textContent = NOTES[Math.floor(Math.random() * NOTES.length)];
      n.style.left = (Math.random() * 90 + 5) + 'vw';
      n.style.bottom = (10 + Math.random() * 28) + '%';
      stage.appendChild(n);
      setTimeout(() => n.remove(), 3500);
    }, 220);

    setTimeout(() => clearInterval(noteInterval), 5000);
    setTimeout(() => stage.remove(), 6500);
  }

  function clearCelebration() {
    document.querySelectorAll('.confetti-canvas, .win-overlay, .animal-stage').forEach(el => el.remove());
    targetEl.classList.remove('celebrate');
  }

  function celebrate() {
    clearCelebration();
    playWinSound();
    runAnimalAnimation();
    targetEl.classList.add('celebrate');

    const overlay = document.createElement('div');
    overlay.className = 'win-overlay';
    overlay.innerHTML = '<div class="win-text">YOU WIN!</div>';
    document.body.appendChild(overlay);

    const canvas = document.createElement('canvas');
    canvas.className = 'confetti-canvas';
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    const colors = ['#ff7a91', '#ffd86b', '#5b3fce', '#1f7a2e', '#3fa9ff', '#ff5acd', '#fff'];
    const particles = [];

    function spawn(x, y, vx, vy) {
      particles.push({
        x, y, vx, vy,
        size: 7 + Math.random() * 9,
        color: colors[Math.floor(Math.random() * colors.length)],
        rot: Math.random() * Math.PI * 2,
        vrot: (Math.random() - 0.5) * 0.35,
        shape: Math.random() < 0.4 ? 'circle' : 'rect',
      });
    }

    // Two cannons firing inward from bottom corners
    for (let i = 0; i < 90; i++) {
      const angle = (Math.PI / 4) + Math.random() * (Math.PI / 4);
      const speed = 9 + Math.random() * 9;
      spawn(0, canvas.height, Math.cos(angle) * speed, -Math.sin(angle) * speed);
      spawn(canvas.width, canvas.height, -Math.cos(angle) * speed, -Math.sin(angle) * speed);
    }

    // Continuous shower from the top
    const shower = setInterval(() => {
      for (let i = 0; i < 5; i++) {
        spawn(Math.random() * canvas.width, -10, (Math.random() - 0.5) * 4, 2 + Math.random() * 3);
      }
    }, 60);

    const start = performance.now();
    function frame(now) {
      const elapsed = now - start;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const p of particles) {
        p.vy += 0.22;
        p.vx *= 0.995;
        p.x += p.vx;
        p.y += p.vy;
        p.rot += p.vrot;
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.fillStyle = p.color;
        if (p.shape === 'circle') {
          ctx.beginPath();
          ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
          ctx.fill();
        } else {
          ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
        }
        ctx.restore();
      }
      for (let i = particles.length - 1; i >= 0; i--) {
        if (particles[i].y > canvas.height + 30) particles.splice(i, 1);
      }
      if (elapsed > 4500) clearInterval(shower);
      if (elapsed < 6500 || particles.length > 0) {
        requestAnimationFrame(frame);
      } else {
        canvas.remove();
      }
    }
    requestAnimationFrame(frame);

    setTimeout(() => overlay.classList.add('fade-out'), 2800);
    setTimeout(() => overlay.remove(), 3700);
  }

  function setFeedback(message, kind) {
    feedbackEl.textContent = message || '';
    feedbackEl.className = 'feedback' + (kind ? ' ' + kind : '');
  }

  function renderFound(pairs) {
    foundEl.innerHTML = '';
    for (const [a, b] of pairs) {
      const chip = document.createElement('span');
      chip.className = 'pair-chip';
      chip.textContent = a + ' + ' + b;
      foundEl.appendChild(chip);
    }
  }

  function setProgress(foundCount) {
    progressEl.textContent = foundCount + ' of ' + totalPairs + ' pairs found';
  }

  async function newGame() {
    const r = await fetch('/api/new', { method: 'POST' });
    const data = await r.json();
    clearCelebration();
    targetEl.textContent = data.target;
    totalPairs = data.totalPairs;
    won = false;
    setProgress(0);
    setFeedback('', '');
    renderFound([]);
    aInput.disabled = false;
    bInput.disabled = false;
    aInput.value = '';
    bInput.value = '';
    aInput.focus();
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (won) return;
    const a = aInput.value;
    const b = bInput.value;
    if (a === '' || b === '') return;
    getAudio();  // prime the audio context inside the user gesture
    const r = await fetch('/api/guess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ a: Number(a), b: Number(b) }),
    });
    const data = await r.json();
    setFeedback(data.message, data.status);
    if (data.found) {
      renderFound(data.found);
      setProgress(data.found.length);
    }
    if (data.status === 'correct' && !data.won) {
      playCorrectSound();
    } else if (data.status === 'wrong') {
      playWrongSound();
    }
    if (data.won) {
      won = true;
      setFeedback('You found them all! Press "New game" to play again.', 'win');
      aInput.disabled = true;
      bInput.disabled = true;
      celebrate();
    } else {
      aInput.value = '';
      bInput.value = '';
      aInput.focus();
    }
  });

  newGameBtn.addEventListener('click', newGame);
  newGame();
</script>
</body>
</html>
"""


class GameState:
    def __init__(self):
        self.target = None
        self.required = set()
        self.found = set()
        self.lock = threading.Lock()

    def new_game(self):
        with self.lock:
            self.target = random.randint(10, 30)
            self.required = set()
            for a in range(1, self.target):
                b = self.target - a
                if b >= a:
                    self.required.add((a, b))
            self.found = set()
            return self.target, len(self.required)

    def guess(self, a, b):
        with self.lock:
            if self.target is None:
                return {"status": "invalid", "message": "Start a new game first."}

            if a + b != self.target:
                return {
                    "status": "wrong",
                    "message": f"{a} + {b} = {a + b}, not {self.target}. Try again!",
                }

            pair = (min(a, b), max(a, b))

            if pair[0] < 1 or pair[1] > self.target - 1:
                return {
                    "status": "invalid",
                    "message": f"Use whole numbers between 1 and {self.target - 1}.",
                }

            if pair in self.found:
                return {
                    "status": "duplicate",
                    "message": f"You already found {pair[0]} + {pair[1]}. Try a different pair.",
                }

            self.found.add(pair)
            won = len(self.found) == len(self.required)
            return {
                "status": "correct",
                "message": f"Nice! {pair[0]} + {pair[1]} = {self.target}.",
                "found": sorted([list(p) for p in self.found]),
                "remaining": len(self.required) - len(self.found),
                "won": won,
            }


state = GameState()


class Handler(http.server.BaseHTTPRequestHandler):
    def _respond(self, code, data, content_type="application/json"):
        if content_type == "application/json":
            payload = json.dumps(data).encode("utf-8")
        else:
            payload = data if isinstance(data, bytes) else data.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self._respond(200, INDEX_HTML, "text/html")
        elif self.path.startswith("/lottie/"):
            name = os.path.basename(self.path[len("/lottie/"):].split("?", 1)[0])
            if not name.endswith(".json") or name.startswith("."):
                self._respond(404, {"error": "Not found"})
                return
            full = os.path.join(LOTTIE_DIR, name)
            try:
                with open(full, "rb") as f:
                    data = f.read()
            except FileNotFoundError:
                self._respond(404, {"error": "Not found"})
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(data)
        else:
            self._respond(404, {"error": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        if self.path == "/api/new":
            target, total = state.new_game()
            self._respond(200, {"target": target, "totalPairs": total})
        elif self.path == "/api/guess":
            try:
                a = int(body["a"])
                b = int(body["b"])
            except (KeyError, TypeError, ValueError):
                self._respond(400, {"error": "Provide integer values for a and b."})
                return
            self._respond(200, state.guess(a, b))
        else:
            self._respond(404, {"error": "Not found"})

    def log_message(self, fmt, *args):
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def kill_listeners_on(port):
    """Find any process listening on `port` and terminate it. macOS/Linux only."""
    try:
        out = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}", "-sTCP:LISTEN"],
            capture_output=True, text=True, timeout=3,
        ).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    pids = [int(p) for p in out.split() if p.strip().isdigit() and int(p) != os.getpid()]
    if not pids:
        return False
    for pid in pids:
        print(f"Port {port} is busy (PID {pid}). Stopping the old instance.")
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue
    # Give them a moment, then escalate if still alive.
    deadline = time.time() + 2.0
    while time.time() < deadline:
        alive = []
        for pid in pids:
            try:
                os.kill(pid, 0)
                alive.append(pid)
            except ProcessLookupError:
                pass
        if not alive:
            return True
        time.sleep(0.1)
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    time.sleep(0.2)
    return True


def bind_server():
    try:
        return ReusableTCPServer(("", PORT), Handler)
    except OSError as e:
        if e.errno != errno.EADDRINUSE:
            raise
        if not kill_listeners_on(PORT):
            raise
        return ReusableTCPServer(("", PORT), Handler)


def main():
    url = f"http://localhost:{PORT}"
    with bind_server() as httpd:
        print(f"Sum Hunter running at {url}")
        print("Press Ctrl+C to stop.")
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    main()
