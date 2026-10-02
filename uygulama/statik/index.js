import { apiJSON, status } from "./api.js";
const byId = id => document.getElementById(id);
const history = [];
const chatForm = byId("chatForm");
const chatInput = byId("mesajInput");
const sendButton = byId("sorButton");
const quickButtons = [...document.querySelectorAll("[data-question]")];
let chatting = false;
function bubble(text, kind) {
  const item = document.createElement("div");
  item.className = "bubble " + kind;
  item.textContent = text; // Kullanıcı/AI metni HTML olarak çalıştırılmaz.
  byId("chatMessages").append(item);
  item.scrollIntoView({block: "nearest", behavior: "smooth"});
}
chatForm.addEventListener("submit", async event => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message || chatting) return;
  chatting = true;
  sendButton.disabled = true;
  quickButtons.forEach(button => button.disabled = true);
  bubble(message, "user");
  chatInput.value = "";
  byId("chatStatus").textContent = "Yanıt hazırlanıyor…";
  try {
    const data = await apiJSON("/api/sohbet", {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({mesaj: message, gecmis: history.slice(-12)})});
    history.push({role: "user", content: message}, {role: "assistant", content: data.cevap.slice(0, 2000)});
    if (history.length > 12) history.splice(0, history.length - 12);
    bubble(data.cevap, "assistant");
    byId("chatStatus").textContent = data.demo ? "Demo modu · Bu yanıt yapay zekâ tarafından üretilmedi." : "Yanıt hazır. Kesin teklif için görüşme talebi bırakabilirsiniz.";
  } catch (error) {
    bubble(error.message, "error");
    chatInput.value = message;
    byId("chatStatus").textContent = "Mesaj gönderilemedi. Yeniden deneyebilirsiniz.";
  } finally {
    chatting = false; sendButton.disabled = false;
    quickButtons.forEach(button => button.disabled = false);
  }
});
quickButtons.forEach(button => button.addEventListener("click", () => {
  chatInput.value = button.dataset.question;
  chatForm.requestSubmit();
}));
document.querySelectorAll("[data-service]").forEach(link => link.addEventListener("click", () => {
  byId("hizmetInput").value = link.dataset.service;
}));
byId("leadForm").addEventListener("submit", async event => {
  event.preventDefault();
  const button = byId("kaydetButton");
  if (button.disabled) return;
  button.disabled = true;
  status(byId("leadStatus"), "Talebiniz kaydediliyor…");
  const service = byId("hizmetInput").value;
  const detail = byId("talepInput").value.trim();
  try {
    const data = await apiJSON("/api/leads", {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({isim: byId("isimInput").value.trim(), telefon: byId("telefonInput").value.trim(),
        mesaj: [service ? "Hizmet: " + service : "", detail].filter(Boolean).join("\n")})});
    status(byId("leadStatus"), data.mesaj + " Talep numaranız: #" + data.id);
    event.target.reset();
  } catch (error) { status(byId("leadStatus"), error.message, true); }
  finally { button.disabled = false; }
});
