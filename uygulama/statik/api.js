export async function apiJSON(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);
  try {
    const response = await fetch(path, {...options, signal: controller.signal});
    let data;
    try { data = await response.json(); }
    catch { throw new Error("Sunucudan geçerli yanıt alınamadı."); }
    if (!response.ok || !data.basari) {
      const error = new Error(data.hata || "İşlem tamamlanamadı.");
      error.status = response.status;
      throw error;
    }
    return data;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("İşlem zaman aşımına uğradı. Kaydın durumunu kontrol ederek tekrar deneyin.");
    if (error instanceof TypeError) throw new Error("Sunucuya ulaşılamıyor. Bağlantınızı kontrol edin.");
    throw error;
  } finally { clearTimeout(timer); }
}
export function status(element, message, isError = false) {
  element.textContent = message;
  element.className = "form-status " + (isError ? "error" : "success");
}
