GOOGLE_MAP_HTML = '''
<!doctype html>
<html>
    <head>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
        <meta charset="utf-8" />
        <title>Carte interactive</title>
        <style>#map{height:90vh;width:100%;}</style>
        <script src="https://maps.googleapis.com/maps/api/js?key={{ api_key }}"></script>
    </head>
    <body>
        <div id="map"></div>
        <script>
            const userId = '{{ user_id }}';
            const map = new google.maps.Map(document.getElementById('map'), {center:{lat:-2.5,lng:23.5},zoom:5});
            fetch(`/api/markers?user_id=${userId}`)
                .then(r=>r.json()).then(data=>{data.forEach(m=>{addMarkerToMap(m)});});
            function addMarkerToMap(m){
                    const marker = new google.maps.Marker({position:{lat:parseFloat(m.lat),lng:parseFloat(m.lng)},map:map,title:m.title});
                    marker.addListener('rightclick',()=>{
                        const choice = prompt('Entrez "#rrggbb" pour changer la couleur, ou "s" pour supprimer:');
                        if(!choice) return;
                        if(choice.toLowerCase() === 's'){
                            if(confirm('Supprimer ?')){
                                fetch(`/api/markers/${m.id}`,{method:'DELETE'}).then(()=>location.reload())
                            }
                            return;
                        }
                        if(/^#([0-9a-fA-F]{6})$/.test(choice)){
                            fetch(`/api/markers/${m.id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:m.title,lat:m.lat,lng:m.lng,color:choice})}).then(()=>location.reload());
                        }else{
                            alert('Code couleur invalide. Format attendu : #rrggbb');
                        }
                    });
            }
            map.addListener('click', function(e){
                const title = prompt('Titre du point:');
                if(!title) return;
                const color = '#ff0000';
                const lat = e.latLng.lat(); const lng = e.latLng.lng();
                fetch('/api/markers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:userId,title:title,lat:lat,lng:lng,color:color})}).then(()=>location.reload());
            });
        </script>
    </body>
</html>
'''

LEAFLET_MAP_HTML = '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
        <style>#map{height:90vh;width:100%;}</style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            const userId='{{ user_id }}';
            const map = L.map('map').setView([-2.5, 23.5], 5);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
            fetch(`/api/markers?user_id=${userId}`).then(r=>r.json()).then(data=>{data.forEach(m=>{
                const mk = L.circleMarker([m.lat,m.lng],{radius:6,color:m.color||'#f00'}).addTo(map).bindPopup(m.title);
                mk.on('contextmenu', function(e){
                    const choice = prompt('Entrez "#rrggbb" pour changer la couleur, ou "s" pour supprimer:');
                    if(!choice) return;
                    if(choice.toLowerCase() === 's'){
                        if(confirm('Supprimer ?')){ fetch(`/api/markers/${m.id}`,{method:'DELETE'}).then(()=>location.reload()); }
                        return;
                    }
                    if(/^#([0-9a-fA-F]{6})$/.test(choice)){
                        fetch(`/api/markers/${m.id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:m.title,lat:m.lat,lng:m.lng,color:choice})}).then(()=>location.reload());
                    } else { alert('Code couleur invalide. Format attendu : #rrggbb'); }
                });
            });});
            map.on('click', function(e){
                const title = prompt('Titre du point:'); if(!title) return;
                const color = '#ff0000';
                const lat = e.latlng.lat; const lng = e.latlng.lng;
                fetch('/api/markers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:userId,title:title,lat:lat,lng:lng,color:color})}).then(()=>location.reload());
            });
        </script>
    </body>
</html>
'''
