// Wix yönetim sayfası kodu. Yönetici anahtarı kaynak koda yazılmaz.
import { fetch } from 'wix-fetch';
const API_BASE = 'https://RENDER-SERVIS-ADINIZ.onrender.com';
let token = '';
let busy = false;
let generation = 0;

$w.onReady(() => {
  // Önce olay bağlanır, ardından veri atanır.
  $w('#leadsRepeater').onItemReady(($item, itemData) => {
    $item('#isimText').text = itemData.isim;
    $item('#telefonText').text = itemData.telefon;
    $item('#mesajText').text = itemData.mesaj || 'Belirtilmedi';
    $item('#tarihText').text = new Date(itemData.tarih).toLocaleString('tr-TR');
  });
  $w('#leadsRepeater').data = [];

  $w('#yukleButton').onClick(async () => {
    if (busy) return;
    token = $w('#adminTokenInput').value.trim();
    if (!token) {
      $w('#durumText').text = 'Yönetici erişim anahtarınızı girin.';
      return;
    }
    busy = true;
    const current = ++generation;
    $w('#yukleButton').disable();
    $w('#durumText').text = 'Talepler yükleniyor…';
    try {
      const response = await fetch(API_BASE + '/api/leads', {
        method: 'get', headers: {Authorization: 'Bearer ' + token}
      });
      const data = await response.json();
      if (current !== generation) return;
      if (!response.ok || !data.basari) throw new Error(data.hata || 'Kayıtlar alınamadı.');
      // Sayısal id -> metin _id. Repeater içindeki öğelere $item ile erişilir.
      $w('#leadsRepeater').data = [];
      $w('#leadsRepeater').data = data.leadler.map(lead => ({...lead, _id: String(lead.id)}));
      $w('#durumText').text = data.leadler.length + ' görüşme talebi.';
      $w('#adminTokenInput').value = '';
      token = '';
    } catch (error) {
      if (current !== generation) return;
      $w('#leadsRepeater').data = [];
      $w('#durumText').text = error.message || 'Bağlantı kurulamadı.';
    } finally {
      busy = false;
      $w('#yukleButton').enable();
    }
  });

  $w('#cikisButton').onClick(() => {
    generation++;
    token = '';
    $w('#adminTokenInput').value = '';
    $w('#leadsRepeater').data = [];
    $w('#durumText').text = 'Çıkış yapıldı.';
  });
});
