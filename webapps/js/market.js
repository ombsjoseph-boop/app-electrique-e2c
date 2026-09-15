
      async function load(){
        try{
          const res = await fetch('/api/markers');
          const data = await res.json();
          const container = document.getElementById('items');
          if(!data || data.length===0){ container.innerHTML = '<p>Aucun marqueur.</p>'; return; }
          container.innerHTML = '<ul class="space-y-3">' + data.map(m => `<li class="p-3 bg-white rounded shadow"><strong>${m.title}</strong> — ${m.lat}, ${m.lng} <div class="text-sm text-gray-600">❤ ${m.likes||0}</div></li>`).join('') + '</ul>'
        }catch(e){ document.getElementById('items').innerText = 'Erreur: '+e }
      }
      load();
   