from flask import Flask, render_template_string, jsonify
import requests, random, time, threading

app = Flask(__name__)

BASE_URL = "https://m.shein.com/ph/ark/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

running = False
checked = set()
working = []
status = {
    "running": False,
    "checked": 0,
    "last": ""
}

MIN_ARK = 1000
MAX_ARK = 20000

def random_digits():
    return str(random.randint(MIN_ARK, MAX_ARK))

def scanner():
    global running
    while running:
        code = random_digits()
        if code in checked:
            continue

        checked.add(code)
        status["checked"] += 1

        url = BASE_URL.format(code)
        status["last"] = url

        try:
            r = requests.get(url, headers=HEADERS, timeout=8)

            # VERY LOOSE RULE:
            if r.status_code == 200:
                working.append(url)

        except:
            pass

        time.sleep(1)

@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SHEIN Scanner</title>
<style>
body { font-family: Arial; background:#0f172a; color:#e5e7eb; padding:20px; }
button { padding:12px; width:100%; border:none; border-radius:8px; font-weight:bold; margin-bottom:10px; }
.start { background:#22c55e; }
.stop { background:#ef4444; }
.box { background:#020617; padding:12px; border-radius:10px; margin-bottom:12px; }
ul { padding-left:20px; max-height:300px; overflow:auto; }
li { font-size:14px; margin-bottom:6px; }
</style>
</head>
<body>

<h2>🔎 SHEIN Link Checker (Real-Time)</h2>
<p>Base: https://m.shein.com/ph/ark/0000</p>

<button class="start" onclick="fetch('/start')">▶ Start</button>
<button class="stop" onclick="fetch('/stop')">⏹ Stop</button>

<div class="box">
  <div><b>Status:</b> <span id="run">Stopped</span></div>
  <div><b>Checked:</b> <span id="count">0</span></div>
  <div style="font-size:12px;"><b>Last checked:</b><br><span id="last">—</span></div>
</div>

<h3>✅ Links That Loaded</h3>
<ul id="results"></ul>

<script>
function update(){
  fetch('/status').then(r=>r.json()).then(s=>{
    document.getElementById('run').innerText = s.running ? 'Running' : 'Stopped';
    document.getElementById('count').innerText = s.checked;
    document.getElementById('last').innerText = s.last || '—';
  });

  fetch('/results').then(r=>r.json()).then(list=>{
    const ul = document.getElementById('results');
    ul.innerHTML = '';
    list.slice().reverse().forEach(l=>{
      const li = document.createElement('li');
      li.innerHTML = `<a href="${l}" target="_blank">${l}</a>`;
      ul.appendChild(li);
    });
  });
}
setInterval(update, 1500);
</script>

</body>
</html>
""")

@app.route("/start")
def start():
    global running
    running = True
    status["running"] = True
    threading.Thread(target=scanner, daemon=True).start()
    return "started"

@app.route("/stop")
def stop():
    global running
    running = False
    status["running"] = False
    return "stopped"

@app.route("/results")
def results():
    return jsonify(working)

@app.route("/status")
def stat():
    return jsonify(status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

