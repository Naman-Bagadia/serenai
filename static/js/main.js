
const startBtn = document.getElementById("startVoice");
const faceImg = document.getElementById("face");
const conversation = document.getElementById("conversationArea");

let ws = new WebSocket(`ws://${window.location.host}/ws`);
let isListening = false;

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "user") {
    appendMsg("🧑‍💬 " + data.message);
  } else if (data.type === "ai") {
    appendMsg("🤖 " + data.message);
    faceImg.src = "/static/gifs/talking.gif";
    setTimeout(() => {
      faceImg.src = "/static/gifs/idle.gif";
    }, 2000);
  }
};

function appendMsg(text) {
  const div = document.createElement("div");
  div.textContent = text;
  conversation.appendChild(div);
  conversation.scrollTop = conversation.scrollHeight;
}

startBtn.onclick = async () => {
  isListening = !isListening;
  if (isListening) {
    startBtn.textContent = "Stop Voice";
    faceImg.src = "/static/gifs/talking.gif";
    ws.send(JSON.stringify({ type: "start_voice" }));
    await fetch("/start-voice");
  } else {
    startBtn.textContent = "Start Voice";
    faceImg.src = "/static/gifs/idle.gif";
    ws.send(JSON.stringify({ type: "stop_voice" }));
  }
};
