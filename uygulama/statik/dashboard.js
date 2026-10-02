import { apiJSON, status } from "./api.js";
const byId = id => document.getElementById(id);
let token = ""; // Yalnızca bellek: localStorage, URL veya kalıcı çereze yazılmaz.
let leads = [];
let generation = 0;
function render() {
  const term = byId("searchInput").value.toLocaleLowerCase("tr-TR").trim();
  const visible = leads.filter(lead => [lead.isim, lead.telefon, lead.mesaj].join(" ").toLocaleLowerCase("tr-TR").includes(term));
  byId("leadRows").replaceChildren();
  visible.forEach(lead => {
    const row = document.createElement("tr");
    [lead.isim, lead.telefon, lead.mesaj || "Belirtilmedi", new Date(lead.tarih).toLocaleString("tr-TR")].forEach(value => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    byId("leadRows").append(row);
  });
  byId("emptyState").hidden = visible.length > 0;
  byId("emptyState").textContent = leads.length ? "Aramanızla eşleşen kayıt bulunamadı." : "Henüz görüşme talebi yok. İlk kayıt, teklif formu gönderildiğinde burada görünecek.";
  byId("visibleCount").textContent = visible.length + " / " + leads.length + " talep gösteriliyor · En yeni önce";
}
function logout() {
  generation++;
  token = ""; leads = [];
  byId("tokenInput").value = "";
  byId("searchInput").value = "";
  byId("dashboardContent").hidden = true;
  byId("authForm").hidden = false;
  byId("leadRows").replaceChildren();
  status(byId("dashboardStatus"), "");
}
async function load() {
  const current = generation;
  byId("loginButton").disabled = true;
  byId("refreshButton").disabled = true;
  status(byId("dashboardStatus"), "Talepler yükleniyor…");
  try {
    const data = await apiJSON("/api/leads", {headers: {Authorization: "Bearer " + token}});
    if (current !== generation) return;
    leads = data.leadler;
    byId("authForm").hidden = true;
    byId("dashboardContent").hidden = false;
    byId("tokenInput").value = "";
    byId("totalCount").textContent = leads.length;
    byId("todayCount").textContent = leads.filter(lead => new Date(lead.tarih).toDateString() === new Date().toDateString()).length;
    byId("lastUpdate").textContent = new Date().toLocaleTimeString("tr-TR", {hour: "2-digit", minute: "2-digit"});
    status(byId("dashboardStatus"), "");
    render();
  } catch (error) {
    if (current !== generation) return;
    if (error.status === 401) logout();
    status(byId("dashboardStatus"), error.message, true);
  } finally { byId("loginButton").disabled = false; byId("refreshButton").disabled = false; }
}
byId("authForm").addEventListener("submit", event => {
  event.preventDefault();
  if (byId("loginButton").disabled) return;
  token = byId("tokenInput").value.trim();
  generation++;
  load();
});
byId("refreshButton").addEventListener("click", load);
byId("logoutButton").addEventListener("click", logout);
byId("searchInput").addEventListener("input", render);
