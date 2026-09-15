
      async function loadNews(){
        try{
          const res = await fetch('/api/news');
          const data = await res.json();
          const container = document.getElementById('news');
          if(!data || data.length===0){ container.innerHTML = '<p>Aucune actualité pour le moment.</p>'; return; }
          container.innerHTML = data.map(n=>`<article class="p-4 bg-white rounded shadow mb-3"><h4 class="font-semibold">${n.title}</h4><div class="text-sm text-gray-700 mt-2">${n.body}</div><div class="text-xs text-gray-500 mt-2">Publié: ${n.created_at}</div></article>`).join('');
        }catch(e){ document.getElementById('news').innerText = 'Erreur: '+e }
      }
      loadNews();

      // No client-side publish controls: news are published from the desktop/backend services.
    