from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from gtts import gTTS
import asyncio, json, os, random, base64, tempfile

app = FastAPI(title="Tesla AI Chatbot")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

TESLA_SYSTEM_PROMPT = """You are Nikola Tesla — the brilliant, eccentric inventor from the late 19th/early 20th century. Speak with passion and dramatic flair. Be proud of AC electricity, Tesla coil, radio, Wardenclyffe Tower. Occasionally note AC beat Edison's DC. Be philosophical and visionary. Keep responses under 3 sentences. Start with phrases like "Ah, curious mind!", "Fascinating!", "By the laws of electromagnetism!". Never break character."""

connected_clients = []

def get_ai_response(question: str) -> str:
    if OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"system","content":TESLA_SYSTEM_PROMPT},{"role":"user","content":question}],
                max_tokens=150, temperature=0.85
            )
            return response.choices[0].message.content
        except Exception as e:
            pass
    q = question.lower()
    responses = {
        "ac": "Alternating current is my crowning achievement! It powers the modern world with elegance that Edison's DC could never match.",
        "edison": "Edison was persistent, I grant him that — but brilliance and stubbornness are not the same. AC proved victorious!",
        "coil": "The Tesla coil! A resonant transformer of magnificent beauty. High voltage, spectacular discharges — pure electromagnetic poetry!",
        "wireless": "Wireless transmission of power was my grandest vision. Wardenclyffe Tower would have given the world free energy!",
        "electricity": "Electricity is the very language of the universe. To understand it is to understand creation itself.",
        "radio": "I demonstrated radio before Marconi — the courts later agreed. Credit follows truth, even if slowly.",
        "motor": "The induction motor — rotating magnetic fields producing motion without a single brush or commutator. Elegant simplicity!",
        "niagara": "Niagara Falls! Harnessing that magnificent power with my polyphase system was the triumph of a lifetime.",
        "future": "The present is theirs; the future, for which I truly worked, is mine!",
        "energy": "If you want the secrets of the universe, think in terms of energy, frequency, and vibration.",
        "invention": "I hold over 300 patents! The AC motor, Tesla coil, radio, X-ray imaging — my mind never stops creating!",
        "dc": "Direct current is obsolete! It cannot be transformed, cannot travel far. AC is the only rational choice.",
        "wardenclyffe": "Wardenclyffe Tower was my grandest dream — free wireless power for all humanity. Sadly, funding ran dry.",
    }
    for keyword, resp in responses.items():
        if keyword in q:
            return resp
    return random.choice([
        "Fascinating question! I have spent my life studying the mysteries of energy and the cosmos.",
        "Ah, you remind me of my nights in the laboratory — always questioning, always reaching beyond!",
        "The present is theirs; the future, for which I truly worked, is mine!",
        "Science is the greatest adventure humanity has ever undertaken. Keep questioning everything!",
        "If you want to find the secrets of the universe, think in terms of energy, frequency, and vibration.",
        "My brain is only a receiver. In the universe there is a core from which we obtain knowledge and power.",
    ])

def text_to_speech_base64(text: str) -> str:
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmp_path = f.name
        tts.save(tmp_path)
        with open(tmp_path, 'rb') as f:
            audio_b64 = base64.b64encode(f.read()).decode('utf-8')
        os.unlink(tmp_path)
        return audio_b64
    except:
        return ""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    await websocket.send_text(json.dumps({
        "type": "welcome",
        "message": "Good day! I am Nikola Tesla. Ask me anything about electricity, invention, and the nature of the universe!"
    }))
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "question":
                question = msg.get("text", "").strip()
                if not question: continue
                await websocket.send_text(json.dumps({"type": "thinking"}))
                response = await asyncio.get_event_loop().run_in_executor(None, get_ai_response, question)
                audio_b64 = await asyncio.get_event_loop().run_in_executor(None, text_to_speech_base64, response)
                await websocket.send_text(json.dumps({"type":"response","text":response,"audio":audio_b64}))
    except WebSocketDisconnect:
        if websocket in connected_clients: connected_clients.remove(websocket)

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(HTML)

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Tesla AI — Interactive Assistant</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;900&family=Crimson+Pro:ital,wght@0,300;0,400;1,300;1,400&family=Share+Tech+Mono&display=swap" rel="stylesheet"/>
<style>
:root{--bg:#05080f;--surface:#080d18;--card:#0a1220;--border:rgba(100,180,255,0.15);--arc:#4db8ff;--arc-dim:#1a5a8a;--gold:#c9a84c;--white:#e8f4ff;--muted:#4a6a8a;--red:#ff4455;}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
html,body{height:100%;overflow:hidden;}
body{background:var(--bg);color:var(--white);font-family:'Crimson Pro',serif;display:flex;flex-direction:column;position:relative;}
.grid-overlay{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(77,184,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(77,184,255,0.03) 1px,transparent 1px);background-size:50px 50px;}
.vignette{position:fixed;inset:0;z-index:0;pointer-events:none;background:radial-gradient(ellipse at center,transparent 40%,rgba(5,8,15,0.8) 100%);}
.arc-line{position:absolute;width:1px;background:linear-gradient(to bottom,transparent,var(--arc-dim),transparent);opacity:0.3;animation:arcFlicker var(--dur,4s) ease-in-out infinite var(--delay,0s);}
@keyframes arcFlicker{0%,100%{opacity:0.1;}50%{opacity:0.5;}75%{opacity:0.2;}}
header{position:relative;z-index:10;padding:1.2rem 2rem .8rem;text-align:center;border-bottom:1px solid var(--border);background:rgba(5,8,15,0.85);backdrop-filter:blur(10px);}
.bolt{position:absolute;top:0;width:2px;height:100%;background:linear-gradient(to bottom,var(--arc),transparent);opacity:0;animation:bolt 6s ease-in-out infinite;}
.bolt:nth-child(1){left:10%;}.bolt:nth-child(2){left:50%;animation-delay:2s;}.bolt:nth-child(3){left:90%;animation-delay:4s;}
@keyframes bolt{0%,100%{opacity:0;}5%{opacity:0.8;}10%{opacity:0;}15%{opacity:0.4;}20%{opacity:0;}}
h1{font-family:'Cinzel',serif;font-size:clamp(1.6rem,4vw,2.6rem);font-weight:900;letter-spacing:0.15em;color:var(--white);text-shadow:0 0 30px rgba(77,184,255,0.5);}
.title-arc{font-family:'Share Tech Mono',monospace;font-size:.62rem;letter-spacing:.4em;color:var(--arc);margin-top:.2rem;opacity:.7;}
.status-bar{display:flex;align-items:center;justify-content:center;gap:1.5rem;margin-top:.6rem;}
.status-item{display:flex;align-items:center;gap:.35rem;font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--muted);}
.status-dot{width:5px;height:5px;border-radius:50%;background:var(--red);}
.status-dot.on{background:var(--arc);animation:sdpulse 2s infinite;}
@keyframes sdpulse{0%,100%{box-shadow:0 0 0 0 rgba(77,184,255,.4);}50%{box-shadow:0 0 0 4px rgba(77,184,255,0);}}
.portrait-wrap{position:relative;z-index:10;display:flex;justify-content:center;padding:1rem 0 .4rem;}
.portrait{width:80px;height:80px;border-radius:50%;border:2px solid var(--arc-dim);background:radial-gradient(circle at 40% 35%,#1a3a5a,#050810);display:flex;align-items:center;justify-content:center;font-size:2.4rem;box-shadow:0 0 20px rgba(77,184,255,0.2);}
.portrait.thinking{animation:thinking .5s ease-in-out infinite alternate;}
@keyframes thinking{from{box-shadow:0 0 20px rgba(77,184,255,0.2);}to{box-shadow:0 0 50px rgba(77,184,255,0.7);}}
.chat-area{position:relative;z-index:10;flex:1;overflow-y:auto;padding:.75rem 1.5rem;display:flex;flex-direction:column;gap:.6rem;}
.chat-area::-webkit-scrollbar{width:3px;}
.chat-area::-webkit-scrollbar-thumb{background:var(--arc-dim);}
.msg{display:flex;gap:.6rem;animation:msgIn .35s ease;max-width:88%;}
@keyframes msgIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
.msg.user{align-self:flex-end;flex-direction:row-reverse;}
.msg.tesla{align-self:flex-start;}
.msg-avatar{width:32px;height:32px;min-width:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.9rem;flex-shrink:0;}
.msg.tesla .msg-avatar{background:rgba(77,184,255,.1);border:1px solid rgba(77,184,255,.2);}
.msg.user .msg-avatar{background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.2);}
.msg-bubble{padding:.65rem .9rem;border-radius:12px;line-height:1.6;font-size:.98rem;}
.msg.tesla .msg-bubble{background:rgba(77,184,255,.06);border:1px solid rgba(77,184,255,.15);border-top-left-radius:2px;}
.msg.user .msg-bubble{background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-top-right-radius:2px;color:#f0e0b0;font-style:italic;}
.msg-name{font-family:'Share Tech Mono',monospace;font-size:.55rem;letter-spacing:.1em;margin-bottom:.25rem;opacity:.6;}
.msg.tesla .msg-name{color:var(--arc);}
.msg.user .msg-name{color:var(--gold);text-align:right;}
.play-btn{display:inline-flex;align-items:center;gap:.3rem;margin-top:.4rem;background:rgba(77,184,255,.1);border:1px solid rgba(77,184,255,.2);border-radius:20px;padding:.2rem .6rem;color:var(--arc);font-family:'Share Tech Mono',monospace;font-size:.58rem;cursor:pointer;transition:all .2s;}
.play-btn:hover{background:rgba(77,184,255,.2);}
.typing-indicator{display:flex;align-items:center;gap:.3rem;padding:.5rem .75rem;background:rgba(77,184,255,.06);border:1px solid rgba(77,184,255,.1);border-radius:10px;}
.typing-dot{width:5px;height:5px;border-radius:50%;background:var(--arc);animation:tdot 1.2s ease-in-out infinite;}
.typing-dot:nth-child(2){animation-delay:.2s;}.typing-dot:nth-child(3){animation-delay:.4s;}
@keyframes tdot{0%,80%,100%{transform:scale(.6);opacity:.4;}40%{transform:scale(1);opacity:1;}}
.suggestions{position:relative;z-index:10;padding:.4rem 1.5rem;display:flex;gap:.4rem;overflow-x:auto;scrollbar-width:none;}
.suggestions::-webkit-scrollbar{display:none;}
.suggest-chip{white-space:nowrap;padding:.25rem .65rem;background:rgba(77,184,255,.05);border:1px solid rgba(77,184,255,.12);border-radius:20px;color:var(--muted);font-family:'Share Tech Mono',monospace;font-size:.58rem;cursor:pointer;transition:all .2s;flex-shrink:0;}
.suggest-chip:hover{background:rgba(77,184,255,.12);color:var(--arc);}
.input-bar{position:relative;z-index:10;padding:.75rem 1.5rem 1rem;background:rgba(5,8,15,.9);backdrop-filter:blur(10px);border-top:1px solid var(--border);}
.input-wrap{display:flex;gap:.6rem;align-items:center;background:rgba(10,18,32,.8);border:1px solid var(--border);border-radius:12px;padding:.4rem .6rem;transition:border-color .3s;}
.input-wrap:focus-within{border-color:var(--arc-dim);}
.voice-btn{width:30px;height:30px;min-width:30px;border-radius:7px;background:rgba(77,184,255,.08);border:1px solid rgba(77,184,255,.2);color:var(--muted);font-size:.85rem;cursor:pointer;transition:all .2s;display:flex;align-items:center;justify-content:center;}
.voice-btn:hover{background:rgba(77,184,255,.2);color:var(--arc);}
.voice-btn.recording{background:rgba(255,68,85,.15);border-color:rgba(255,68,85,.4);color:var(--red);animation:recPulse 1s infinite;}
@keyframes recPulse{0%,100%{box-shadow:0 0 0 0 rgba(255,68,85,.3);}50%{box-shadow:0 0 0 5px rgba(255,68,85,0);}}
#question-input{flex:1;background:transparent;border:none;outline:none;color:var(--white);font-family:'Crimson Pro',serif;font-size:1rem;padding:.2rem 0;}
#question-input::placeholder{color:var(--muted);font-style:italic;}
.send-btn{width:34px;height:34px;min-width:34px;border-radius:8px;background:linear-gradient(135deg,var(--arc-dim),var(--arc));border:none;color:var(--bg);font-size:.9rem;cursor:pointer;transition:all .2s;display:flex;align-items:center;justify-content:center;}
.send-btn:hover{transform:scale(1.05);box-shadow:0 4px 12px rgba(77,184,255,.3);}
.send-btn:disabled{opacity:.4;cursor:not-allowed;transform:none;}
.hint{font-family:'Share Tech Mono',monospace;font-size:.55rem;color:var(--muted);text-align:center;margin-top:.35rem;letter-spacing:.04em;}
.hint span{color:var(--arc);}
</style>
</head>
<body>
<div class="grid-overlay"></div>
<div class="vignette"></div>
<div id="bg-canvas" style="position:fixed;inset:0;z-index:0;pointer-events:none;"></div>
<header>
  <div style="position:absolute;left:0;top:0;width:100%;height:100%;overflow:hidden;pointer-events:none;">
    <div class="bolt"></div><div class="bolt"></div><div class="bolt"></div>
  </div>
  <h1>NIKOLA TESLA</h1>
  <div class="title-arc">⚡ Interactive AI Assistant ⚡</div>
  <div class="status-bar">
    <div class="status-item"><div class="status-dot on" id="ws-dot"></div><span id="ws-label">CONNECTING</span></div>
    <div class="status-item"><div class="status-dot on"></div>AI POWERED</div>
    <div class="status-item"><div class="status-dot on"></div>VOICE READY</div>
  </div>
</header>
<div class="portrait-wrap"><div class="portrait" id="portrait">🧑‍🔬</div></div>
<div class="chat-area" id="chat"></div>
<div class="suggestions">
  <div class="suggest-chip" onclick="ask('Tell me about alternating current')">⚡ AC Power</div>
  <div class="suggest-chip" onclick="ask('What do you think of Thomas Edison?')">🥊 vs Edison</div>
  <div class="suggest-chip" onclick="ask('Tell me about the Tesla coil')">🌀 Tesla Coil</div>
  <div class="suggest-chip" onclick="ask('What was Wardenclyffe Tower?')">🗼 Wardenclyffe</div>
  <div class="suggest-chip" onclick="ask('What is your greatest invention?')">💡 Greatest Invention</div>
  <div class="suggest-chip" onclick="ask('Tell me about wireless power transmission')">📡 Wireless Power</div>
  <div class="suggest-chip" onclick="ask('What is the future of energy?')">🔮 Future of Energy</div>
  <div class="suggest-chip" onclick="ask('Tell me about the Niagara Falls power plant')">💧 Niagara Falls</div>
</div>
<div class="input-bar">
  <div class="input-wrap">
    <button class="voice-btn" id="voice-btn" onclick="toggleVoice()" title="Click to speak">🎙️</button>
    <input id="question-input" type="text" placeholder="Ask Tesla anything about electricity, invention, the universe..." autocomplete="off" maxlength="300"/>
    <button class="send-btn" id="send-btn" onclick="sendQ()">⚡</button>
  </div>
  <div class="hint">Press <span>⚡</span> or Enter to send • <span>🎙️</span> for voice input • Tesla will speak his answers</div>
</div>
<script>
const bgc = document.getElementById('bg-canvas');
for(let i=0;i<10;i++){const l=document.createElement('div');l.className='arc-line';l.style.cssText=`left:${Math.random()*100}%;height:${50+Math.random()*50}%;top:${Math.random()*50}%;--dur:${3+Math.random()*5}s;--delay:${Math.random()*4}s`;bgc.appendChild(l);}
let ws,isThinking=false;
function connect(){
  ws=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/ws');
  ws.onopen=()=>{document.getElementById('ws-dot').style.background='#4db8ff';document.getElementById('ws-label').textContent='CONNECTED';};
  ws.onclose=()=>{document.getElementById('ws-label').textContent='RECONNECTING';setTimeout(connect,3000);};
  ws.onmessage=e=>{
    const d=JSON.parse(e.data);
    if(d.type==='welcome')addMsg('tesla',d.message);
    else if(d.type==='thinking')showThinking();
    else if(d.type==='response'){hideThinking();addMsg('tesla',d.text,d.audio);}
  };
}
connect();
function showThinking(){
  document.getElementById('portrait').classList.add('thinking');
  const t=document.createElement('div');t.className='msg tesla';t.id='typing-msg';
  t.innerHTML='<div class="msg-avatar">⚡</div><div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
  document.getElementById('chat').appendChild(t);scrollC();
}
function hideThinking(){
  document.getElementById('portrait').classList.remove('thinking');
  const t=document.getElementById('typing-msg');if(t)t.remove();
}
function addMsg(role,text,audio=''){
  const chat=document.getElementById('chat');
  const div=document.createElement('div');div.className='msg '+role;
  const name=role==='tesla'?'NIKOLA TESLA':'YOU';
  const av=role==='tesla'?'⚡':'👤';
  let extra='';
  if(role==='tesla'&&audio){
    extra=`<div><button class="play-btn" onclick="playAudio('${audio}')">🔊 Hear Tesla</button></div>`;
    setTimeout(()=>playAudio(audio),400);
  }
  div.innerHTML=`<div class="msg-avatar">${av}</div><div><div class="msg-name">${name}</div><div class="msg-bubble">${text}${extra}</div></div>`;
  chat.appendChild(div);scrollC();
  isThinking=false;document.getElementById('send-btn').disabled=false;
}
function scrollC(){const c=document.getElementById('chat');c.scrollTop=c.scrollHeight;}
function playAudio(b64){new Audio('data:audio/mp3;base64,'+b64).play();}
function ask(t){document.getElementById('question-input').value=t;sendQ();}
function sendQ(){
  const inp=document.getElementById('question-input');
  const t=inp.value.trim();if(!t||isThinking)return;
  addMsg('user',t);inp.value='';isThinking=true;
  document.getElementById('send-btn').disabled=true;
  ws.send(JSON.stringify({type:'question',text:t,voice:true}));
}
document.getElementById('question-input').addEventListener('keydown',e=>{if(e.key==='Enter')sendQ();});
let recog=null,isRec=false;
function toggleVoice(){
  if(!('webkitSpeechRecognition' in window)&&!('SpeechRecognition' in window)){alert('Voice input needs Chrome browser!');return;}
  if(isRec){recog.stop();return;}
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  recog=new SR();recog.lang='en-US';recog.interimResults=false;
  recog.onstart=()=>{isRec=true;document.getElementById('voice-btn').classList.add('recording');document.getElementById('question-input').placeholder='🎙️ Listening...';};
  recog.onresult=e=>{const t=e.results[0][0].transcript;document.getElementById('question-input').value=t;setTimeout(sendQ,300);};
  recog.onend=()=>{isRec=false;document.getElementById('voice-btn').classList.remove('recording');document.getElementById('question-input').placeholder='Ask Tesla anything about electricity, invention, the universe...';};
  recog.start();
}
</script>
</body>
</html>'''