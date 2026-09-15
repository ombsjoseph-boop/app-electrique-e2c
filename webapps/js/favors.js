
      async function load(){
        try{
          const res = await fetch('/api/markers');
          const data = await res.json();
          // sort by likes desc
          data.sort((a,b)=> (b.likes||0) - (a.likes||0));
          const top = data.slice(0,20);
          const container = document.getElementById('favorites');
          if(!top || top.length===0){ container.innerHTML = '<p>Aucun favori.</p>'; return; }
          container.innerHTML = '<ul class="space-y-3">' + top.map(m => `<li class="p-3 bg-white rounded shadow"><strong>${m.title}</strong> — ❤ ${m.likes||0} <div class="text-sm text-gray-600">${m.lat}, ${m.lng}</div></li>`).join('') + '</ul>'
        }catch(e){ document.getElementById('favorites').innerText = 'Erreur: '+e }
      }
      load();
   