from map_server import start_map_server, MAP_SERVER

# Démarrer le serveur si nécessaire
start_map_server()
app = MAP_SERVER
if app is None:
    print('MAP_SERVER is None')
else:
    print('Registered routes:')
    for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
        methods = ','.join(sorted([m for m in r.methods if m not in ('HEAD','OPTIONS')]))
        print(f"{r.rule} -> methods: {methods}")
