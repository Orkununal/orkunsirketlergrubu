// Wix ziyaretçi sayfası kodu. API_BASE değerini canlı backend adresinizle değiştirin.
import { fetch } from 'wix-fetch';
const API_BASE = 'https://RENDER-SERVIS-ADINIZ.onrender.com';
let history = [];
let chatting = false;
let saving = false;

async function postJSON(path, body) {
  const response = await fetch(API_BASE + path, {
    method: 'post', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok || !data.basari) throw new Error(data.hata || 'İşlem tamamlanamadı.');
  return data;
}

$w.onReady(() => {
  $w('#sorButton').onClick(async () => {
    const message = $w('#mesajInput').value.trim();
    if (!message || chatting) return;
    chatting = true;
    $w('#sorButton').disable();
    $w('#cevapText').text = 'Yanıt hazırlanıyor…';
    try {
      const data = await postJSON('/api/sohbet', {mesaj: message, gecmis: history.slice(-12)});
      $w('#cevapText').text = data.cevap;
      history.push({role: 'user', content: message}, {role: 'assistant', content: data.cevap.slice(0, 2000)});
      history = history.slice(-12);
      $w('#mesajInput').value = '';
    } catch (error) {
      $w('#cevapText').text = error.message || 'Bağlantı kurulamadı.';
    } finally {
      chatting = false;
      $w('#sorButton').enable();
    }
  });

  $w('#kaydetButton').onClick(async () => {
    if (saving) return;
    const isim = $w('#isimInput').value.trim();
    const telefon = $w('#telefonInput').value.trim();
    if (!isim || !telefon) {
      $w('#durumText').text = 'Adınızı ve telefon numaranızı girin.';
      return;
    }
    saving = true;
    $w('#kaydetButton').disable();
    $w('#durumText').text = 'Talebiniz kaydediliyor…';
    try {
      const service = $w('#hizmetDropdown').value;
      const message = $w('#talepInput').value.trim();
      const data = await postJSON('/api/leads', {isim, telefon,
        mesaj: [service ? 'Hizmet: ' + service : '', message].filter(Boolean).join('\n')});
      $w('#durumText').text = data.mesaj + ' Talep numarası: #' + data.id;
      $w('#isimInput').value = '';
      $w('#telefonInput').value = '';
      $w('#talepInput').value = '';
      $w('#hizmetDropdown').value = '';
    } catch (error) {
      $w('#durumText').text = error.message || 'Bağlantı kurulamadı.';
    } finally {
      saving = false;
      $w('#kaydetButton').enable();
    }
  });
});
