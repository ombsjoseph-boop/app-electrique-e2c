   // Professional invoice display with detailed breakdown
async function loadBills() {
  try {
    // Récupérer d'abord les informations de session
    const sessionRes = await fetch("/api/session", {
      method: "GET",
      credentials: "include"
    });
    
    const sessionData = await sessionRes.json();
    console.log('Session data:', sessionData);
    
    if (!sessionData.authenticated || !sessionData.user_id) {
      document.getElementById('bills-list').innerHTML = '<div class="bg-blue-50 border border-blue-200 rounded p-4 text-blue-800"><i class="fas fa-lock mr-2"></i>Connectez-vous pour voir vos factures</div>';
      // Afficher un message dans la section principale
      const mainContainer = document.querySelector('main');
      if (mainContainer) {
        mainContainer.innerHTML = `
          <div class="max-w-6xl mx-auto p-6">
            <h1 class="text-3xl font-bold text-gray-900 mb-4">Vos Factures</h1>
            <p class="text-gray-600 mb-6">Consultez et gérez vos factures électriques en ligne</p>
            <div class="bg-blue-50 border-2 border-blue-200 rounded-lg p-8 text-center">
              <i class="fas fa-lock text-4xl text-blue-600 mb-4"></i>
              <h2 class="text-2xl font-semibold text-gray-800 mb-2">Accès Réservé</h2>
              <p class="text-gray-600 mb-6">Veuillez vous connecter pour consulter vos factures.</p>
              <button class="px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700" onclick="document.getElementById('auth-modal').classList.remove('hidden')">
                <i class="fas fa-sign-in-alt mr-2"></i>Se Connecter
              </button>
            </div>
          </div>
        `;
      }
      return;
    }
    
    // Récupérer les factures de l'utilisateur connecté
    const res = await fetch(`/api/bills?user_id=${sessionData.user_id}`, {
      method: "GET",
      credentials: "include",
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!res.ok) {
      console.error('Erreur API:', res.status);
      document.getElementById('bills-list').innerHTML = '<div class="bg-red-50 border border-red-200 rounded p-4 text-red-800"><i class="fas fa-exclamation-triangle mr-2"></i>Erreur lors du chargement des factures</div>';
      return;
    }
    
    const data = await res.json();
    console.log('Bills data:', data);
    
    const container = document.getElementById('bills-list');
    if (!data || data.length === 0) {
      // Afficher les infos utilisateur d'abord
      displayUserInfo(sessionData);
      
      container.innerHTML = '<div class="bg-gray-50 border border-gray-200 rounded p-6 text-center text-gray-600"><i class="fas fa-file-invoice mr-2"></i>Aucune facture disponible</div>';
      return;
    }

    // Afficher les informations de l'utilisateur
    displayUserInfo(sessionData);

    // Display bills as professional invoice cards
    container.innerHTML = data.map(bill => createBillCard(bill)).join('');
    
    // Attach event listeners
    document.querySelectorAll('.view-bill-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const billId = e.target.getAttribute('data-id');
        const bill = data.find(b => b.id == billId);
        if (bill) showBillDetail(bill);
      });
    });

    document.querySelectorAll('.pay-bill-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const billId = e.target.getAttribute('data-id');
        const confirmPay = confirm('Êtes-vous sûr de vouloir payer cette facture ?');
        if (!confirmPay) return;
        
        try {
          const res = await fetch(`/api/bills/${billId}/pay`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payer: 'web' })
          });
          
          if (res.ok) {
            alert('Paiement effectué avec succès');
            loadBills();
          } else {
            const j = await res.json();
            alert('Erreur: ' + (j.error || res.status));
          }
        } catch (e) {
          alert('Erreur lors du paiement: ' + e);
        }
      });
    });

  } catch (e) {
    console.error('Error loading bills:', e);
    document.getElementById('bills-list').innerHTML = '<div class="bg-red-50 border border-red-200 rounded p-4 text-red-800"><i class="fas fa-exclamation-circle mr-2"></i>Erreur lors du chargement des factures: ' + e.message + '</div>';
  }
}

// Afficher les informations de l'utilisateur connecté
function displayUserInfo(userInfo) {
  const mainContainer = document.querySelector('main');
  if (!mainContainer || document.getElementById('user-info-banner')) {
    return; // Banneau déjà affiché ou conteneur non trouvé
  }
  
  const banner = document.createElement('div');
  banner.id = 'user-info-banner';
  banner.className = 'mb-6 p-4 bg-gradient-to-r from-blue-100 to-blue-50 border border-blue-300 rounded-lg';
  banner.innerHTML = `
    <div class="flex justify-between items-center">
      <div>
        <p class="text-sm text-gray-600">Utilisateur connecté</p>
        <p class="text-lg font-semibold text-gray-900">${userInfo.username || 'Utilisateur'}</p>
        <p class="text-sm text-blue-600"><i class="fas fa-envelope mr-1"></i>'N/A'</p>
      </div>
      <div class="text-right">
        <p class="text-xs text-gray-500"></p>
        <button onclick="logoutUser()" class="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700">
          <i class="fas fa-sign-out-alt mr-1"></i>Déconnexion
        </button>
      </div>
    </div>
  `;
  
  // Insérer le banneau au début du conteneur main
  mainContainer.insertAdjacentElement('afterbegin', banner);
}

// Déconnexion de l'utilisateur
async function logoutUser() {
  try {
    await fetch('/api/logout', {
      method: 'POST',
      credentials: 'include'
    });
    window.location.reload();
  } catch (e) {
    console.error('Erreur lors de la déconnexion:', e);
  }
}

function createBillCard(bill) {
  const formattedDate = new Date(bill.created_at).toLocaleDateString('fr-FR');
  const dueDate = bill.due_date ? new Date(bill.due_date).toLocaleDateString('fr-FR') : 'N/A';
  const statusColor = bill.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  const statusLabel = bill.status === 'paid' ? 'Payée' : 'À payer';
  
  return `
    <div class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
      <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold">${bill.reference || 'FACTURE-' + bill.id}</h3>
            <p class="text-blue-100 text-sm">Facture #${bill.id}</p>
          </div>
          <span class="px-3 py-1 rounded-full text-xs font-semibold ${statusColor}">
            ${statusLabel}
          </span>
        </div>
      </div>
      
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <!-- Client info -->
          <div>
            <p class="text-xs text-gray-500 uppercase font-semibold">Client</p>
            <p class="text-lg font-semibold text-gray-900">${bill.user_nom || 'Utilisateur ' + bill.user_id}</p>
          </div>
          
          <!-- Date info -->
          <div>
            <p class="text-xs text-gray-500 uppercase font-semibold">Date d'émission</p>
            <p class="text-lg font-semibold text-gray-900">${formattedDate}</p>
          </div>
          
          <!-- Amount info -->
          <div class="text-right">
            <p class="text-xs text-gray-500 uppercase font-semibold">Montant total</p>
            <p class="text-2xl font-bold text-blue-600">${(bill.total_amount || bill.amount || 0).toFixed(2)} FC</p>
          </div>
        </div>
        
        <!-- Bill summary -->
        <div class="bg-gray-50 rounded p-4 mb-4">
          <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
            <div>
              <span class="text-gray-600">Abonnement</span>
              <p class="font-semibold text-gray-900">${(bill.subscription_fee || 0).toFixed(2)} FC</p>
            </div>
            <div>
              <span class="text-gray-600">Consommation</span>
              <p class="font-semibold text-gray-900">${(bill.consumption_kwh || 0).toFixed(2)} kWh</p>
            </div>
            <div>
              <span class="text-gray-600">Acheminement</span>
              <p class="font-semibold text-gray-900">${(bill.acheminement_cost || 0).toFixed(2)} FC</p>
            </div>
          </div>
        </div>
        
        <!-- Due date and actions -->
        <div class="flex justify-between items-center pt-4 border-t border-gray-200">
          <div>
            <p class="text-sm text-gray-500">À payer avant le</p>
            <p class="font-semibold text-gray-900">${dueDate}</p>
          </div>
          <div class="flex gap-2">
            <button data-id="${bill.id}" class="view-bill-btn px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition text-sm font-medium">
              Voir détails
            </button>
            ${bill.status === 'unpaid' ? `
              <button data-id="${bill.id}" class="pay-bill-btn px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition text-sm font-medium">
                Payer
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    </div>
  `;
}

function showBillDetail(bill) {
  const modal = document.getElementById('bill-detail-modal');
  const content = document.getElementById('bill-detail-content');
  
  const formattedDate = new Date(bill.created_at).toLocaleDateString('fr-FR');
  const dueDate = bill.due_date ? new Date(bill.due_date).toLocaleDateString('fr-FR') : 'N/A';
  const branchementNo = bill.branchement_no || `BR-${String(bill.user_id).padStart(5, '0')}-${String(bill.id).padStart(4, '0')}`;
  
  // Calculate subtotal
  const subtotal = (bill.subscription_fee || 0) + (bill.consumption_cost || 0) + (bill.fourniture_cost || 0) + (bill.acheminement_cost || 0);
  
  // Redevances audiovisuelles (typically 2% of subtotal)
  const redevanceAV = subtotal * 0.02;
  
  content.innerHTML = `
    <!-- Professional Invoice Template -->
    <div class="bg-white">
      <!-- Header with Logo and Company Info -->
      <div class="border-b-4 border-blue-600 pb-6 mb-6">
        <div class="grid grid-cols-3 gap-4 items-start mb-6">
          <!-- Logo and Company Left -->
          <div class="col-span-1">
            <img src="https://e2c.cg/wp-content/uploads/2025/03/Logo-E2C-SAU_-2.png" alt="E²C Congo" class="h-16 mb-2" />
            <div>
              <p class="font-bold text-xl text-blue-600">E²C CONGO</p>
              <p class="text-xs text-gray-600">Société Énergie Électrique</p>
            </div>
          </div>
          
          <!-- Invoice Title Center -->
          <div class="col-span-1 text-center">
            <h1 class="text-4xl font-bold text-gray-900">FACTURE</h1>
            <p class="text-gray-600 text-sm mt-1">${bill.reference || 'FACTURE-' + bill.id}</p>
          </div>
          
          <!-- Total Amount Right -->
          <div class="col-span-1 text-right">
            <p class="text-3xl font-bold text-blue-600">${(bill.total_amount || bill.amount || 0).toFixed(2)} FC</p>
            <p class="text-sm text-gray-600 font-semibold">Montant total TTC</p>
          </div>
        </div>
      </div>

      <!-- Entreprise et Client Information Table -->
      <table class="w-full mb-8 border-collapse border border-gray-300">
        <thead>
          <tr class="bg-blue-100">
            <th class="text-left p-3 border border-gray-300 font-bold text-blue-900">ENTREPRISE E²C CONGO</th>
            <th class="text-left p-3 border border-gray-300 font-bold text-blue-900">CLIENT / ABONNÉ</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="p-3 border border-gray-300 align-top">
              <p class="text-sm"><strong>Dénomination:</strong> E²C CONGO S.A.</p>
              <p class="text-sm"><strong>Adresse:</strong> Avenue Denis Sassou Nguesso</p>
              <p class="text-sm"><strong>Ville:</strong> Brazzaville</p>
              <p class="text-sm"><strong>Tél:</strong> +242 200 000 000</p>
              <p class="text-sm"><strong>Email:</strong> contact@e2c.cg</p>
            </td>
            <td class="p-3 border border-gray-300 align-top">
              <p class="text-sm"><strong>Nom:</strong> ${bill.user_nom || 'Utilisateur ' + bill.user_id}</p>
              <p class="text-sm"><strong>Numéro de Branchement:</strong> <span class="font-bold text-blue-600">${branchementNo}</span></p>
              <p class="text-sm"><strong>Client ID:</strong> ${bill.user_id}</p>
              <p class="text-sm"><strong>Date d'émission:</strong> ${formattedDate}</p>
              <p class="text-sm"><strong>Date d'échéance:</strong> <span class="font-bold text-red-600">${dueDate}</span></p>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Payment Deadline Notice -->
      <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-8">
        <p class="text-sm font-bold text-yellow-800 mb-2">⚠️ IMPORTANT - DÉLAI DE PAIEMENT</p>
        <p class="text-sm text-yellow-900">
          Cette facture doit être payée avant le <strong>${dueDate}</strong>. 
          Tout retard de paiement pourra entraîner la suspension du service. 
          Veuillez effectuer votre paiement par virement bancaire, mobile money, 
          ou à nos guichets E²C CONGO.
        </p>
      </div>

      <!-- Detailed breakdown table -->
      <table class="w-full mb-8 border-collapse">
        <thead class="bg-blue-600 text-white">
          <tr>
            <th class="text-left p-3">Description</th>
            <th class="text-right p-3">Quantité</th>
            <th class="text-right p-3">Prix Unitaire</th>
            <th class="text-right p-3">Montant</th>
          </tr>
        </thead>
        <tbody>
          <tr class="border-b border-gray-200">
            <td class="p-3">Abonnement</td>
            <td class="text-right p-3">1</td>
            <td class="text-right p-3">${(bill.subscription_fee || 0).toFixed(2)} FC</td>
            <td class="text-right p-3 font-semibold">${(bill.subscription_fee || 0).toFixed(2)} FC</td>
          </tr>
          <tr class="border-b border-gray-200">
            <td class="p-3">Consommation d'énergie</td>
            <td class="text-right p-3">${(bill.consumption_kwh || 0).toFixed(3)}</td>
            <td class="text-right p-3">${(bill.unit_price || 0).toFixed(4)} FC/kWh</td>
            <td class="text-right p-3 font-semibold">${(bill.consumption_cost || 0).toFixed(2)} FC</td>
          </tr>
          <tr class="border-b border-gray-200">
            <td class="p-3">Fourniture d'électricité</td>
            <td class="text-right p-3">—</td>
            <td class="text-right p-3">—</td>
            <td class="text-right p-3 font-semibold">${(bill.fourniture_cost || 0).toFixed(2)} FC</td>
          </tr>
          <tr class="border-b border-gray-200">
            <td class="p-3">Acheminement</td>
            <td class="text-right p-3">—</td>
            <td class="text-right p-3">—</td>
            <td class="text-right p-3 font-semibold">${(bill.acheminement_cost || 0).toFixed(2)} FC</td>
          </tr>
        </tbody>
      </table>

      <!-- Redevances Audiovisuelles Section -->
      <table class="w-full mb-8 border-collapse border border-gray-300">
        <thead>
          <tr class="bg-purple-100">
            <th class="text-left p-3 border border-gray-300 font-bold text-purple-900">REDEVANCES AUDIOVISUELLES</th>
            <th class="text-right p-3 border border-gray-300 font-bold text-purple-900">Montant</th>
          </tr>
        </thead>
        <tbody>
          <tr class="border-b border-gray-300">
            <td class="p-3 border border-gray-300 text-sm">Redevance Audiovisuelle (2%)</td>
            <td class="p-3 border border-gray-300 text-right font-semibold">${redevanceAV.toFixed(2)} FC</td>
          </tr>
        </tbody>
      </table>

      <!-- Totals section -->
      <div class="grid grid-cols-2 gap-8 mb-8">
        <div></div>
        <div>
          <div class="bg-gray-50 rounded p-4 space-y-3">
            <div class="flex justify-between text-gray-700">
              <span>Sous-total</span>
              <span class="font-semibold">${subtotal.toFixed(2)} FC</span>
            </div>
            <div class="flex justify-between text-gray-700">
              <span>Redevance Audiovisuelle (2%)</span>
              <span class="font-semibold">${redevanceAV.toFixed(2)} FC</span>
            </div>
            ${bill.tcfe_amount ? `
              <div class="flex justify-between text-gray-700">
                <span>TCFE (${(bill.tcfe_pct || 0).toFixed(2)}%)</span>
                <span class="font-semibold">${(bill.tcfe_amount || 0).toFixed(2)} FC</span>
              </div>
            ` : ''}
            ${bill.cta_amount ? `
              <div class="flex justify-between text-gray-700">
                <span>CTA (${(bill.cta_pct || 0).toFixed(2)}%)</span>
                <span class="font-semibold">${(bill.cta_amount || 0).toFixed(2)} FC</span>
              </div>
            ` : ''}
            ${bill.tva_amount ? `
              <div class="flex justify-between text-gray-700">
                <span>TVA (${(bill.tva_pct || 0).toFixed(2)}%)</span>
                <span class="font-semibold">${(bill.tva_amount || 0).toFixed(2)} FC</span>
              </div>
            ` : ''}
            <div class="border-t border-gray-200 pt-3 flex justify-between text-lg font-bold text-blue-600">
              <span>TOTAL TTC</span>
              <span>${(bill.total_amount || bill.amount || 0).toFixed(2)} FC</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Status -->
      <div class="bg-blue-50 border border-blue-200 rounded p-4 mb-8">
        <p class="text-sm text-gray-600">
          <strong>Statut:</strong> 
          <span class="font-semibold ${bill.status === 'paid' ? 'text-green-700' : 'text-red-700'}">
            ${bill.status === 'paid' ? 'Payée ✓' : 'À payer ⚠️'}
          </span>
        </p>
        ${bill.paid_at ? `
          <p class="text-sm text-gray-600 mt-1">
            <strong>Payée le:</strong> ${new Date(bill.paid_at).toLocaleDateString('fr-FR')}
          </p>
        ` : ''}
      </div>

      <!-- Coupon Détachable Section -->
      <div class="border-2 border-dashed border-gray-400 p-6 mb-8 bg-gray-50">
        <p class="text-center font-bold text-gray-700 mb-4 pb-4 border-b-2 border-dashed border-gray-400">
          ✂️ COUPON À DÉTACHER - À CONSERVER OU À JOINDRE AU PAIEMENT ✂️
        </p>
        
        <div class="grid grid-cols-3 gap-4 text-sm">
          <div class="bg-white p-3 rounded border border-gray-300">
            <p class="font-bold text-gray-700">Numéro de Branchement</p>
            <p class="text-lg font-bold text-blue-600">${branchementNo}</p>
          </div>
          
          <div class="bg-white p-3 rounded border border-gray-300">
            <p class="font-bold text-gray-700">Montant à Payer</p>
            <p class="text-lg font-bold text-red-600">${(bill.total_amount || bill.amount || 0).toFixed(2)} FC</p>
          </div>
          
          <div class="bg-white p-3 rounded border border-gray-300">
            <p class="font-bold text-gray-700">Avant le</p>
            <p class="text-lg font-bold text-orange-600">${dueDate}</p>
          </div>
        </div>

        <div class="mt-4 bg-white p-3 rounded border border-gray-300">
          <p class="text-xs font-semibold text-gray-600 mb-2">MODES DE PAIEMENT:</p>
          <div class="grid grid-cols-3 gap-3 text-xs">
            <div>
              <p class="font-bold">📱 Mobile Money</p>
              <p>MTN: *156#</p>
              <p>Airtel: *143#</p>
            </div>
            <div>
              <p class="font-bold">🏦 Virement Bancaire</p>
              <p>BICEC: 1234567890</p>
              <p>ECOBANK: 0987654321</p>
            </div>
            <div>
              <p class="font-bold">🏢 Guichets E²C</p>
              <p>Lun-Ven: 8h-16h</p>
              <p>Siège: Brazzaville</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Information -->
      <div class="bg-gray-100 p-4 rounded mb-6 text-xs text-gray-700">
        <p class="font-semibold mb-2">📋 CONDITIONS IMPORTANTES:</p>
        <ul class="list-disc list-inside space-y-1">
          <li>Le paiement après date d'échéance peut entraîner une pénalité de 5% du montant</li>
          <li>Tout impayé plus de 30 jours entraînera la suspension du service</li>
          <li>Veuillez joindre ce coupon ou mentionner votre numéro de branchement lors du paiement</li>
          <li>Conservez votre reçu de paiement pour justification</li>
        </ul>
      </div>

      <!-- Footer -->
      <div class="border-t border-gray-200 pt-6 text-center text-xs text-gray-600">
        <p>Merci pour votre confiance. Pour toute question, contactez-nous à support@electrocg.com</p>
        <p class="mt-2">Facture générée le ${new Date().toLocaleDateString('fr-FR')}</p>
        
        <!-- Download PDF button -->
        <div class="mt-6 flex gap-4 justify-center">
          <button onclick="downloadBillPDF(${bill.id})" class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition font-medium">
            Télécharger en PDF
          </button>
          <button onclick="document.getElementById('bill-detail-modal').classList.add('hidden')" class="px-6 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition font-medium">
            Fermer
          </button>
        </div>
      </div>
    </div>
  `;
  
  modal.classList.remove('hidden');
}

function downloadBillPDF(billId) {
  const url = `/api/bills/${billId}/pdf`;
  const link = document.createElement('a');
  link.href = url;
  link.download = `facture-${billId}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Load bills on page load
loadBills();

// No client-side creation controls: bills are created from the desktop application.
   