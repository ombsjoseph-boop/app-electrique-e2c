// Simple map frontend that talks to the local map server API.
(function(){
  const API_BASE = (location && location.origin && location.origin.startsWith('http')) ? location.origin : 'http://127.0.0.1:5001';

  const map = L.map('map').setView([0, 0], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);

  let markersGroup = L.layerGroup().addTo(map);
  let pointsGroup = L.layerGroup().addTo(map);
  let zonesGroup = L.layerGroup().addTo(map);

  function zoneColor(status){
    if(!status) return '#888';
    status = status.toLowerCase();
    if(status.includes('fonction')) return '#10b981'; // green
    if(status.includes('maintenance')) return '#f59e0b'; // orange
    if(status.includes('hors')) return '#ef4444'; // red
    return '#6b7280';
  }

  async function loadMarkers(){
    try{
      const res = await fetch(`${API_BASE}/api/markers`);
      if(!res.ok) throw new Error('Erreur API');
      const data = await res.json();
      markersGroup.clearLayers();
      if(data.length){
        data.forEach(m => {
          const lat = parseFloat(m.lat), lng = parseFloat(m.lng);
          if(Number.isFinite(lat) && Number.isFinite(lng)){
            const circle = L.circleMarker([lat, lng], { radius:6, color: m.color || '#ff0000' }).addTo(markersGroup);
            const likes = m.likes || 0;
            const popupHtml = `<div style="min-width:140px;"><strong>${(m.title||'Point')}</strong><div class="mt-1"><small>id: ${m.id}</small></div><div class="mt-2"><button id="like-${m.id}" style="padding:6px 8px;border-radius:6px;background:#ef4444;color:#fff;border:none;cursor:pointer;">❤ J'aime (${likes})</button></div></div>`;
            circle.bindPopup(popupHtml);
            // Prevent editing from web UI — provide only like action
            circle.on('popupopen', () => {
              const btn = document.getElementById(`like-${m.id}`);
              if(btn){
                btn.addEventListener('click', async function(){
                  try{
                    btn.disabled = true;
                    const res = await fetch(`${API_BASE}/api/markers/${m.id}/like`, { method: 'POST' });
                    if(res.ok){
                      const data = await res.json();
                      // Refresh markers to reflect new likes
                      await loadMarkers();
                    } else {
                      console.warn('Like failed', res.status);
                      btn.disabled = false;
                    }
                  } catch(e){ console.warn('Like error', e); btn.disabled = false; }
                });
              }
            });
          }
        });
      }
    } catch(e){ console.warn('loadMarkers error', e); }
  }

  async function loadMapPoints(){
    try{
      const res = await fetch(`${API_BASE}/api/map_points`);
      if(!res.ok) throw new Error('Erreur API points');
      const data = await res.json();
      pointsGroup.clearLayers();
      if(data.length){
        data.forEach(p => {
          const lat = parseFloat(p.lat), lng = parseFloat(p.lng);
          if(Number.isFinite(lat) && Number.isFinite(lng)){
            const mark = L.marker([lat, lng], { title: `Point #${p.id}` }).addTo(pointsGroup);
            mark.bindPopup(`<strong>Point</strong><div class="mt-1"><small>id: ${p.id}</small></div><div class="mt-1">Créé: ${p.created_at}</div>`);
          }
        });
      }
    } catch(e){ console.warn('loadMapPoints error', e); }
  }

  async function loadZones(){
    try{
      const res = await fetch(`${API_BASE}/api/electric_zones`);
      if(!res.ok) throw new Error('Erreur API zones');
      const data = await res.json();
      zonesGroup.clearLayers();
      if(data.length){
        data.forEach(z => {
          const lat = parseFloat(z.lat), lng = parseFloat(z.lng);
          if(Number.isFinite(lat) && Number.isFinite(lng)){
            const color = zoneColor(z.status);
            // Use a smaller radius (meters) for better display; scale further if needed
            const circle = L.circle([lat, lng], { radius: 800, color: color, fillColor: color, fillOpacity: 0.25 }).addTo(zonesGroup);
            const popup = `<strong>${z.name}</strong><div class="mt-1"><small>${z.type} — ${z.city || ''}</small></div><div class="mt-1">Tension: ${z.voltage || 'N/A'}</div><div class="mt-1">État: ${z.status || ''}</div>`;
            circle.bindPopup(popup);
          }
        });
      }
    } catch(e){ console.warn('loadZones error', e); }
  }

  // Non-admin clients cannot change markers; admin actions must be done from the desktop app with the admin secret.
  async function handleMarkerContext(m){
    alert("Action réservée aux administrateurs. Pour ajouter/modifier/supprimer des marqueurs, utilisez l'application desktop (compte admin).");
  }

  // Disable adding markers from the web UI: only admins can add via the desktop app.
  // map.on('click', ...) intentionally removed.

  // Poll for updates every 5s
  loadMarkers();
  loadMapPoints();
  loadZones();
  setInterval(() => { loadMarkers(); loadMapPoints(); loadZones(); }, 5000);

})();
