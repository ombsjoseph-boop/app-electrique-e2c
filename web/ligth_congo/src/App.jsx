import React, { useEffect, useState } from 'react';
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMapEvents
} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

/* =============== API =============== */
const API = {
  getMarkers: async () => (await axios.get('/api/markers')).data,
  addMarker: async (marker) => (await axios.post('/api/markers', marker)).data,
};

/* =============== MAP =============== */
function Markers({ markers }) {
  return markers.map((m) => (
    <CircleMarker
      key={m.id}
      center={[m.lat, m.lng]}
      radius={8}
      color={m.color || '#ef4444'}
      fillColor={m.color || '#ef4444'}
      fillOpacity={0.85}
    >
      <Popup>
        <div className="text-sm">
          <h4 className="font-bold text-base">{m.title}</h4>
          <p><b>État :</b> {m.status || 'Coupure signalée'}</p>
          <p><b>Cause :</b> {m.reason || 'Maintenance / Incident'}</p>
          <p><b>Retour :</b> {m.restore_time || 'À confirmer'}</p>
        </div>
      </Popup>
    </CircleMarker>
  ));
}

function AddMarkerOnClick({ onAdd }) {
  useMapEvents({
    click(e) {
      const title = prompt('Quartier / Zone concernée :');
      if (!title) return;
      onAdd({
        title,
        lat: e.latlng.lat,
        lng: e.latlng.lng,
        color: '#ef4444'
      });
    }
  });
  return null;
}

function MapPage({ markers, onAdd, interactive = true }) {
  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <h2 className="text-2xl font-bold mb-4">🗺️ Carte des coupures</h2>
      <div className="h-[65vh] rounded-xl overflow-hidden shadow border">
        <MapContainer
          center={[-2.5, 23.5]}
          zoom={5}
          className="h-full w-full"
          dragging={interactive}
          touchZoom={interactive}
          scrollWheelZoom={interactive}
          doubleClickZoom={interactive}
          boxZoom={interactive}
          keyboard={interactive}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Markers markers={markers} />
          {interactive && <AddMarkerOnClick onAdd={onAdd} />}
        </MapContainer>
      </div>
    </div>
  );
}

/* =============== CARROUSEL =============== */
function Carousel() {
  const images = [
    '/src/assets/ps.jpg',
    '/src/assets/ps1.jpg',
    '/src/assets/ps2.jpg'
  ];
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % images.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full h-64 md:h-80 mb-6 relative overflow-hidden rounded-xl shadow-lg">
      {images.map((src, i) => (
        <img
          key={i}
          src={src}
          alt={`Slide ${i + 1}`}
          className={`absolute top-0 left-0 w-full h-full object-cover transition-opacity duration-1000 ${i === index ? 'opacity-100' : 'opacity-0'}`}
        />
      ))}
    </div>
  );
}

/* =============== HOME PAGE =============== */
function HomePage({ markers }) {
  const status = { level: 'normal', text: 'Réseau normal' };
  const colors = { normal: 'bg-green-100 text-green-800', perturbé: 'bg-orange-100 text-orange-800', critique: 'bg-red-100 text-red-800' };

  const regionData = {
    labels: ['Kinshasa', 'Lubumbashi', 'Matadi', 'Goma', 'Kananga'],
    datasets: [{ label: 'Coupures signalées', data: [5, 2, 3, 4, 1], backgroundColor: 'rgba(239,68,68,0.7)' }],
  };

  const causeData = {
    labels: ['Maintenance', 'Panne ligne', 'Tempête', 'Autres'],
    datasets: [{ label: 'Causes', data: [8, 5, 3, 2], backgroundColor: ['rgba(34,197,94,0.7)', 'rgba(239,68,68,0.7)', 'rgba(251,191,36,0.7)', 'rgba(147,51,234,0.7)'] }],
  };

  const messages = [
    { title: 'Travaux programmés – Kinshasa', text: 'Maintenance prévue le 20 janvier de 08h à 16h.' },
    { title: 'Retour du courant – Lubumbashi', text: 'La panne générale a été réparée.' },
  ];

  const galleryImages = [
    '/src/assets/ps3.jpg', '/src/assets/ps3.jpg', '/src/assets/ps3.jpg',
    '/src/assets/ps3.jpg', '/src/assets/ps3.jpg', '/src/assets/ps3.jpg'
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <h2 className="text-3xl font-bold mb-6"> Accueil</h2>

      <Carousel />

      <div className='grid grid-cols-3 gap-4 mb-6 '>
        <button className='bg-blue-200 p-4 rounded-lg'>Voir</button>
        <button className='bg-blue-200 p-4 rounded-lg'>Note</button>
        <button className='bg-blue-200 p-4 rounded-lg'>Info</button>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className={`p-6 rounded-xl shadow ${colors[status.level] || colors.normal}`}>
          <h3 className="font-semibold text-lg mb-2">Statut du réseau</h3>
          <p className="text-xl font-bold">{status.text}</p>
        </div>
        <div className="p-6 rounded-xl shadow bg-blue-50">
          <h3 className="font-semibold text-lg mb-2">Points signalés</h3>
          <p className="text-xl font-bold">{markers.length}</p>
        </div>
        <div className="p-6 rounded-xl shadow bg-yellow-50">
          <h3 className="font-semibold text-lg mb-2">Actions rapides</h3>
          <ul className="list-disc pl-5 text-gray-700">
            <li>Voir la carte</li>
            <li>Consulter les infos</li>
            <li>Signaler un problème</li>
          </ul>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="p-4 rounded-xl shadow bg-white">
          <h3 className="font-semibold text-lg mb-3">Répartition par région</h3>
          <Bar data={regionData} options={{ responsive: true }} />
        </div>
        <div className="p-4 rounded-xl shadow bg-white">
          <h3 className="font-semibold text-lg mb-3">Types de pannes</h3>
          <Pie data={causeData} options={{ responsive: true }} />
        </div>
      </div>

      <div>
        <h3 className="text-xl font-bold mt-6 mb-3">Derniers messages officiels</h3>
        <div className="space-y-3">
          {messages.map((m, i) => (
            <div key={i} className="p-4 rounded-xl border-l-4 border-blue-500 bg-blue-50 shadow">
              <h4 className="font-semibold">{m.title}</h4>
              <p className="text-gray-700">{m.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-2xl font-bold mt-8 mb-4"> Galerie des installations</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
          {galleryImages.map((src, i) => (
            <div key={i} className="rounded-lg overflow-hidden shadow-lg hover:scale-105 transform transition duration-300">
              <img src={src} alt={`Galerie ${i + 1}`} className="w-full h-24 object-cover " />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* =============== INFO PAGE =============== */
function InfoPage() {
  const informations = [
    { title: 'Prévention des coupures', text: 'Planification et entretien régulier pour éviter les interruptions de courant.' },
    { title: 'Alertes météo', text: 'Des notifications sont envoyées en cas de tempêtes ou conditions climatiques affectant le réseau.' },
    { title: 'Conseils de sécurité', text: 'Ne touchez jamais les câbles tombés et signalez toute anomalie immédiatement.' },
    { title: 'Tarification & facturation', text: 'Consultez vos factures et les informations tarifaires sur notre portail citoyen.' },
    { title: 'Projets en cours', text: 'Suivez les projets d’extension du réseau dans votre région.' },
    { title: 'Service client', text: 'Contactez-nous pour toute assistance via téléphone, email ou formulaire en ligne.' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <h2 className="text-3xl font-bold mb-6"> Informations aux citoyens</h2>
      <div className="grid md:grid-cols-2 gap-6">
        {informations.map((info, i) => (
          <div key={i} className="p-6 rounded-xl shadow bg-white hover:shadow-lg transition">
            <h3 className="font-semibold text-lg mb-2">{info.title}</h3>
            <p className="text-gray-700">{info.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* =============== FORMULAIRE DE REPORT =============== */
function ReportPage() {
  const [form, setForm] = useState({ name: '', location: '', issue: '' });
  const submit = () => { alert('Merci ! Votre signalement a été envoyé.'); setForm({ name: '', location: '', issue: '' }); };
  return (
    <div className="max-w-4xl mx-auto px-2 py-6 space-y-4">
      <h2 className="text-2xl font-bold mb-4"> Signaler une coupure</h2>
        <form action="" method="post" className=' '>
      <input placeholder="Nom (facultatif)" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full p-2 rounded border" />
      <input placeholder="Quartier / Ville" value={form.location} onChange={e => setForm({ ...form, location: e.target.value })} className="w-full p-2 rounded border" />
      <textarea placeholder="Décrivez le problème..." value={form.issue} onChange={e => setForm({ ...form, issue: e.target.value })} className="w-full p-2 rounded border" />
      <button onClick={submit} className="px-4 py-2 bg-blue-700 text-white rounded hover:bg-blue-600">Envoyer</button>
      </form>
    </div>

  );
}

/* =============== APP =============== */
export default function App() {
  const [page, setPage] = useState('home');
  const [markers, setMarkers] = useState([]);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    API.getMarkers().then(setMarkers);
  }, []);

  const navItems = [
    ['home', ' Accueil'],
    ['map', ' Carte'],
    ['info', ' Infos'],
    ['report', ' Signaler']
  ];

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      {/* HEADER */}
      <header className="bg-blue-900 text-white px-6 py-5 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">⚡ Électricité Congo-Brazzaville</h1>
          <p className="text-sm opacity-90">Information • Coupures • Signalement citoyen</p>
        </div>
        {/* Hamburger */}
        <button
          className="md:hidden text-white text-3xl font-bold"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          ☰
        </button>

        {/* Desktop Nav */}
        <nav className="hidden md:flex gap-2">
          {navItems.map(([k, label]) => (
            <button key={k} onClick={() => setPage(k)} className={`px-4 py-2 rounded-xl text-sm font-medium ${page === k ? 'bg-white text-blue-900' : 'bg-blue-700 hover:bg-blue-600'}`}>
              {label}
            </button>
          ))}
        </nav>
      </header>

      {/* MOBILE SLIDE MENU */}
      <div className={`fixed top-0 right-0 h-full w-64 bg-blue-900 text-white shadow-lg transform transition-transform duration-300 z-50 ${menuOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <button className="absolute top-4 right-4 text-2xl" onClick={() => setMenuOpen(false)}>×</button>
        <div className="flex flex-col mt-20 gap-4 px-4">
          {navItems.map(([k, label]) => (
            <button key={k} onClick={() => { setPage(k); setMenuOpen(false) }} className={`px-4 py-2 rounded-xl text-left text-white hover:bg-blue-700 ${page === k ? 'bg-white text-blue-900' : ''}`}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* MAIN */}
      <main className="flex-1 relative">
        {/* Overlay pour bloquer clics carte quand menu ouvert */}
        {menuOpen && (
          <div
            className="fixed inset-0 bg-black/40 z-40"
            onClick={() => setMenuOpen(false)}
          />
        )}

        {page === 'home' && <HomePage markers={markers} />}
        {page === 'map' && <MapPage markers={markers} onAdd={() => { }} interactive={!menuOpen} />}
        {page === 'info' && <InfoPage />}
        {page === 'report' && <ReportPage />}
      </main>

      {/* FOOTER */}
      {/* FOOTER */}
      <footer className="bg-gray-900 text-gray-300 py-6 mt-6">
        <div className="max-w-7xl mx-auto px-4 grid md:grid-cols-3 gap-6 text-center md:text-left">

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-2">Contact</h4>
            <p> Urgence électricité : 177</p>
            <p> Email : support@electricite-CG.cg</p>
            <p> Siège : Brazzaville, Congo-Brazzaville</p>
          </div>

          {/* Liens utiles */}
          <div>
            <h4 className="text-white font-semibold mb-2">Liens utiles</h4>
            <ul className="space-y-1">
              <li><a href="#home" className="hover:text-white">Accueil</a></li>
              <li><a href="#map" className="hover:text-white">Carte des coupures</a></li>
              <li><a href="#info" className="hover:text-white">Infos & Conseils</a></li>
              <li><a href="#report" className="hover:text-white">Signaler un problème</a></li>
            </ul>
          </div>

          {/* Réseaux sociaux */}
          <div>
            <h4 className="text-white font-semibold mb-2">Réseaux sociaux</h4>
            <div className="flex justify-center md:justify-start gap-4 text-2xl">
              <a href="#" className="hover:text-white"></a>
              <a href="#" className="hover:text-white"></a>
              <a href="#" className="hover:text-white"></a>
              <a href="#" className="hover:text-white"></a>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          © 2025 Électricité Congo-Brazzaville. Tous droits réservés.
        </div>
      </footer>

    </div>
  );
}
