// Mobile menu toggle
      document.addEventListener('DOMContentLoaded', function () {
        var btn = document.getElementById('mobile-menu-btn');
        var menu = document.getElementById('mobile-menu');
        if (btn && menu) {
          btn.addEventListener('click', function () {
            var expanded = btn.getAttribute('aria-expanded') === 'true';
            btn.setAttribute('aria-expanded', String(!expanded));
            menu.classList.toggle('hidden');
          });
        }

        // Init carousel
        (function(){
          var carousel = document.getElementById('home-carousel');
          if(!carousel) return;
          var slides = Array.from(carousel.querySelectorAll('.carousel-slide'));
          var indicators = Array.from(document.querySelectorAll('.carousel-indicator'));
          var prevBtn = document.getElementById('carousel-prev');
          var nextBtn = document.getElementById('carousel-next');
          var current = 0; var timer = null;
          function show(i){
            slides.forEach(function(s,idx){ s.classList.toggle('hidden', idx !== i); });
            indicators.forEach(function(b,idx){ b.classList.toggle('bg-white', idx === i); b.classList.toggle('bg-white/40', idx !== i); });
            current = i;
          }
          function next(){ show((current + 1) % slides.length); }
          function prev(){ show((current - 1 + slides.length) % slides.length); }
          function start(){ timer = setInterval(next, 5000); }
          function stop(){ if(timer){ clearInterval(timer); timer = null; } }

          indicators.forEach(function(b,idx){ b.addEventListener('click', function(){ stop(); show(idx); start(); }); });
          if(prevBtn) prevBtn.addEventListener('click', function(){ stop(); prev(); start(); });
          if(nextBtn) nextBtn.addEventListener('click', function(){ stop(); next(); start(); });
          carousel.addEventListener('mouseenter', stop);
          carousel.addEventListener('mouseleave', start);
          show(0); start();
        })();

        // Auth modal init (amélioré : animation, focus trap, validation)
        (function(){
          var modal = document.getElementById('auth-modal');
          var dialog = document.getElementById('auth-dialog');
          var backdrop = document.getElementById('auth-backdrop');
          var lastActive = null;

          function setMode(mode){
            var loginFields = document.getElementById('auth-login-fields'), regFields = document.getElementById('auth-register-fields');
            var tabs = Array.from(document.querySelectorAll('.auth-tab'));
            tabs.forEach(function(t){
              var is = t.getAttribute('data-mode')===mode;
              t.setAttribute('aria-selected', String(is));
              t.classList.toggle('font-semibold', is);
              t.classList.toggle('text-gray-600', !is);
            });
            if(mode==='register'){
              loginFields.classList.add('hidden'); regFields.classList.remove('hidden'); document.getElementById('auth-title').innerText='Créer un compte';
            } else {
              loginFields.classList.remove('hidden'); regFields.classList.add('hidden'); document.getElementById('auth-title').innerText='Se connecter';
            }
            // focus first input
            setTimeout(function(){ var f = dialog.querySelector('input:not([type=hidden])'); if(f) f.focus(); },50);
          }

          function openAuth(mode){
            if(!modal || !dialog) return;
            lastActive = document.activeElement;
            modal.classList.remove('hidden'); modal.removeAttribute('aria-hidden');
            // show with animation
            dialog.classList.remove('opacity-0','scale-95'); dialog.classList.add('opacity-100','scale-100');
            document.body.style.overflow='hidden';
            setMode(mode||'login');
            trapFocus();
          }

          function closeAuth(){
            if(!modal || !dialog) return;
            // start hide animation
            dialog.classList.remove('opacity-100','scale-100'); dialog.classList.add('opacity-0','scale-95');
            setTimeout(function(){ modal.classList.add('hidden'); modal.setAttribute('aria-hidden','true'); document.body.style.overflow=''; releaseFocusTrap(); if(lastActive) lastActive.focus(); },220);
          }

          // Focus trap
          var focusable = 'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])';
          var firstFocusable = null, lastFocusable = null, focTrapHandler = null;
          function trapFocus(){
            var nodes = Array.from(dialog.querySelectorAll(focusable)).filter(function(n){ return n.offsetParent !== null; });
            firstFocusable = nodes[0]; lastFocusable = nodes[nodes.length-1];
            focTrapHandler = function(e){
              if(e.key==='Tab'){
                if(e.shiftKey && document.activeElement===firstFocusable){ e.preventDefault(); lastFocusable.focus(); }
                else if(!e.shiftKey && document.activeElement===lastFocusable){ e.preventDefault(); firstFocusable.focus(); }
              }
            };
            document.addEventListener('keydown', focTrapHandler);
          }
          function releaseFocusTrap(){ document.removeEventListener('keydown', focTrapHandler); focTrapHandler=null; }

          // Simple validation helpers
          function showFieldError(el, msg){ var id = el.id ? 'err-'+el.id : null; if(!id) return; var err = document.getElementById(id); if(err){ err.innerText = msg; err.classList.remove('hidden'); el.setAttribute('aria-invalid','true'); } }
          function clearFieldError(el){ var id = el.id ? 'err-'+el.id : null; if(!id) return; var err = document.getElementById(id); if(err){ err.innerText = ''; err.classList.add('hidden'); el.removeAttribute('aria-invalid'); } }
          function validateForm(){
            var mode = document.getElementById('auth-register-fields').classList.contains('hidden') ? 'login' : 'register';
            var ok = true; var firstInvalid = null; document.getElementById('auth-error').classList.add('hidden');
            if(mode==='login'){
              var email = document.getElementById('login-email'); var pass = document.getElementById('login-password');
              clearFieldError(email); clearFieldError(pass);
              if(!email.checkValidity()){ showFieldError(email,'Veuillez saisir un email valide.'); ok=false; firstInvalid = firstInvalid || email; }
              if(!pass.checkValidity()){ showFieldError(pass,'Le mot de passe doit contenir au moins 6 caractères.'); ok=false; firstInvalid = firstInvalid || pass; }
            } else {
              var name = document.getElementById('reg-name'); var emailR = document.getElementById('reg-email'); var passR = document.getElementById('reg-password');
              clearFieldError(name); clearFieldError(emailR); clearFieldError(passR);
              if(!name.checkValidity()){ showFieldError(name,'Veuillez indiquer votre nom complet.'); ok=false; firstInvalid = firstInvalid || name; }
              if(!emailR.checkValidity()){ showFieldError(emailR,'Veuillez saisir un email valide.'); ok=false; firstInvalid = firstInvalid || emailR; }
              if(!passR.checkValidity()){ showFieldError(passR,'Le mot de passe doit contenir au moins 6 caractères.'); ok=false; firstInvalid = firstInvalid || passR; }
            }
            if(!ok){ if(firstInvalid) firstInvalid.focus(); document.getElementById('auth-error').classList.remove('hidden'); document.getElementById('auth-error').innerText='Veuillez corriger les erreurs ci-dessus.'; }
            return ok;
          }

          // Hook buttons
          var openBtns = ['open-login','open-register','open-login-mobile','open-register-mobile','open-login-footer','open-register-footer'].map(function(id){ return document.getElementById(id); }).filter(Boolean);
          openBtns.forEach(function(b){ b.addEventListener('click', function(e){ e.preventDefault(); openAuth(b.id.indexOf('register')>-1 ? 'register' : 'login'); }); });

          document.querySelectorAll('.auth-tab').forEach(function(t){ t.addEventListener('click', function(){ setMode(t.getAttribute('data-mode')); }); });
          document.getElementById('switch-to-register')?.addEventListener('click', function(e){ e.preventDefault(); setMode('register'); });
          document.getElementById('switch-to-login')?.addEventListener('click', function(e){ e.preventDefault(); setMode('login'); });

          document.getElementById('close-auth')?.addEventListener('click', function(){ closeAuth(); });
          backdrop?.addEventListener('click', function(){ closeAuth(); });
          document.addEventListener('keydown', function(e){ if(e.key==='Escape'){ closeAuth(); } });

          document.getElementById('auth-form')?.addEventListener('submit', function(e){ e.preventDefault(); if(!validateForm()) return; var mode = document.getElementById('auth-register-fields').classList.contains('hidden') ? 'login' : 'register';
            // Call server endpoints
            var payload = {};
            var url = mode==='login' ? '/api/login' : '/api/register';
            if(mode==='login'){
              payload = { email: document.getElementById('login-email').value, password: document.getElementById('login-password').value };
            } else {
              payload = { username: document.getElementById('reg-name').value, email: document.getElementById('reg-email').value, password: document.getElementById('reg-password').value };
            }
            fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, credentials:'same-origin', body:JSON.stringify(payload)})
              .then(function(r){
                if(r.ok) return r.json();
                return r.json().then(function(err){ throw err; });
              })
              .then(function(data){
                // On success, update UI to show username
                setAuthenticatedUser(data.username || data.email);
                closeAuth();
                // Recharger les factures si on est sur la page bills
                if(typeof window.loadBills === 'function'){
                  setTimeout(function(){ window.loadBills(); }, 300);
                }
              }).catch(function(err){
                var msg = err && err.error ? err.error : 'Erreur réseau';
                document.getElementById('auth-error').classList.remove('hidden');
                document.getElementById('auth-error').innerText = (msg==='user_exists' ? 'Cet utilisateur existe déjà.' : (msg==='invalid_credentials' ? 'Identifiants invalides.' : 'Erreur : '+msg));
              });
          });

          // Auth UI helpers: set/clear user display and check session
          function setAuthenticatedUser(username){
            // Desktop nav
            var loginBtn = document.getElementById('open-login');
            var regBtn = document.getElementById('open-register');
            if(loginBtn) loginBtn.style.display = 'none';
            if(regBtn) regBtn.style.display = 'none';
            var existing = document.getElementById('user-display');
            if(!existing){
              var span = document.createElement('div');
              span.id = 'user-display';
              span.className = 'flex items-center gap-3';
              span.innerHTML = '<div id="user-avatar" class="h-8 w-8 rounded-full bg-white flex items-center justify-center text-red-600 font-semibold">'+(username && username[0] ? username[0].toUpperCase() : 'U')+'</div><div class="hidden sm:block text-sm text-white"><strong id="user-name">'+username+'</strong></div><button id="logout-btn" class="ml-2 px-3 py-1 bg-white text-red-600 rounded text-sm">Se déconnecter</button>';
              var nav = document.querySelector('nav[aria-label="Navigation principale"]');
              if(nav) nav.appendChild(span);
              document.getElementById('logout-btn')?.addEventListener('click', logout);
            } else {
              document.getElementById('user-name').innerText = username;
              var avatar = document.getElementById('user-avatar'); if(avatar) avatar.innerText = (username && username[0] ? username[0].toUpperCase() : 'U');
            }

            // Mobile menu
            var loginMobile = document.getElementById('open-login-mobile');
            var regMobile = document.getElementById('open-register-mobile');
            if(loginMobile) loginMobile.style.display='none';
            if(regMobile) regMobile.style.display='none';
            if(!document.getElementById('user-mobile')){
              var link = document.createElement('a');
              link.href='#';
              link.id='user-mobile';
              link.className='block px-3 py-2 text-white rounded';
              link.innerText = 'Bonjour, '+username + ' — Se déconnecter';
              link.addEventListener('click', function(e){ e.preventDefault(); logout(); });
              var mobileNav = document.querySelector('#mobile-menu nav');
              if(mobileNav) mobileNav.appendChild(link);
            } else { document.getElementById('user-mobile').innerText = 'Bonjour, '+username + ' — Se déconnecter'; }

            // Footer
            var loginFooter = document.getElementById('open-login-footer');
            var regFooter = document.getElementById('open-register-footer');
            if(loginFooter) loginFooter.style.display='none';
            if(regFooter) regFooter.style.display='none';
            if(!document.getElementById('user-footer')){
              var div = document.createElement('div');
              div.id='user-footer';
              div.className='mt-2';
              div.innerHTML = '<div>Connecté : <strong>'+username+'</strong></div><div class="mt-2"><button id="logout-footer" class="px-3 py-2 bg-white text-red-600 rounded">Se déconnecter</button></div>';
              loginFooter?.parentNode?.appendChild(div);
              document.getElementById('logout-footer')?.addEventListener('click', logout);
            }
          }

            // Si une fonction loadBills existe (page bills), l'appeler pour rafraîchir l'affichage
            try{
              if(typeof window.loadBills === 'function'){
                window.loadBills();
              } else {
                // Sinon, si un conteneur #bills est présent, charger les factures et afficher un rendu simple
                var billsContainer = document.getElementById('bills');
                if(billsContainer){
                  fetch('/api/bills',{credentials:'same-origin'}).then(function(r){ if(!r.ok) throw r; return r.json(); }).then(function(data){
                    if(!data || data.length===0){ billsContainer.innerHTML = '<p>Aucune facture.</p>'; return; }
                    billsContainer.innerHTML = data.map(function(b){ var userLabel = b.user_nom || b.user_id; return '<div class="p-3 bg-white rounded shadow mb-3">' +
                      '<div><strong>Ref: '+(b.reference||'-')+'</strong> — Utilisateur: '+userLabel+'</div>' +
                      '<div>Montant: '+(Number(b.amount||0).toFixed(2))+' — Statut: '+(b.status||'')+'</div>' +
                      '</div>'; }).join('');
                  }).catch(function(){ billsContainer.innerText = 'Votre facture sera affichée lors de votre connexion.'; });
                }
              }
            }catch(e){ /* ignore */ }

          function clearAuthenticatedUser(){
            var loginBtn = document.getElementById('open-login');
            var regBtn = document.getElementById('open-register');
            if(loginBtn) loginBtn.style.display = '';
            if(regBtn) regBtn.style.display = '';
            var ud = document.getElementById('user-display'); if(ud) ud.remove();
            var um = document.getElementById('user-mobile'); if(um) um.remove();
            var uf = document.getElementById('user-footer'); if(uf) uf.remove();
            var loginMobile = document.getElementById('open-login-mobile'); if(loginMobile) loginMobile.style.display='';
            var regMobile = document.getElementById('open-register-mobile'); if(regMobile) regMobile.style.display='';
            var loginFooter = document.getElementById('open-login-footer'); if(loginFooter) loginFooter.style.display='';
            var regFooter = document.getElementById('open-register-footer'); if(regFooter) regFooter.style.display='';
          }

          function logout(){ fetch('/api/logout',{method:'POST',credentials:'same-origin'}).then(function(){ clearAuthenticatedUser(); }); }

          function checkSessionOnLoad(){ 
            fetch('/api/session',{credentials:'same-origin'}).then(function(r){
              return r.json();
            }).then(function(data){ 
              if(data && data.authenticated && data.username){ 
                setAuthenticatedUser(data.username);
                // Recharger les factures si on est sur la page bills
                if(typeof window.loadBills === 'function'){
                  setTimeout(function(){ window.loadBills(); }, 100);
                }
              } 
            }).catch(function(){}); 
          }

          checkSessionOnLoad();
        })();
      });

      // Load latest news for the home page
      fetch('/api/news').then(r=>r.json()).then(data=>{
        const el = document.getElementById('home-news');
        if(!data || data.length===0){ el.innerText = 'Aucune actualité pour le moment.'; return; }
        el.innerHTML = data.slice(0,3).map(n=>`<div class="mb-2"><strong>${n.title}</strong><div class="text-xs text-gray-500">${n.created_at}</div></div>`).join('');
      }).catch(()=>{document.getElementById('home-news').innerText='Impossible de charger.'});
   
      
    // Masquer le loader une fois la page chargée
    window.addEventListener('load', function() {
      const loader = document.getElementById('loader');
      setTimeout(function() {
        loader.classList.add('loader-hidden');
      }, 500);
    });

     // Sélection du type de paiement
    function selectPaymentMethod(method) {
      const mtnSection = document.getElementById('mtnSection');
      const bankSection = document.getElementById('bankSection');
      
      if (method === 'mtn') {
        mtnSection.classList.remove('hidden');
        bankSection.classList.add('hidden');
        // Réinitialiser les champs bancaires
        document.getElementById('bankName').value = '';
        document.getElementById('bankName_select').value = '';
        document.getElementById('bankAccount').value = '';
        document.getElementById('bankSwift').value = '';
        document.getElementById('bankAmount').value = '';
        document.getElementById('bankIban').value = '';
        document.getElementById('bankReference').value = '';
      } else if (method === 'bank') {
        bankSection.classList.remove('hidden');
        mtnSection.classList.add('hidden');
        // Réinitialiser les champs MTN
        document.getElementById('mtnName').value = '';
        document.getElementById('mtnNumber').value = '';
        document.getElementById('mtnAmount').value = '';
        document.getElementById('mtnPin').value = '';
        document.getElementById('mtnReference').value = '';
      }
    }

    // Formatage du numéro MTN
    document.getElementById('mtnNumber').addEventListener('input', function(e) {
      let value = e.target.value.replace(/\D/g, '');
      if (value.length > 0) {
        if (value.startsWith('243')) {
          value = '+' + value;
        } else if (value.startsWith('0')) {
          // Accepté tel quel
        } else if (value.length > 0) {
          // Préfixer avec 243
          value = '243' + value;
        }
      }
      e.target.value = value;
    });

    // Gestion de la soumission du formulaire
    async function handleTransaction(event) {
      event.preventDefault();

      const errorDiv = document.getElementById('errorMessage');
      const successDiv = document.getElementById('successMessage');
      const errorText = document.getElementById('errorText');

      // Masquer les messages
      errorDiv.classList.add('hidden');
      successDiv.classList.add('hidden');

      try {
        // Récupérer les données communes
        const invoiceNumber = document.getElementById('invoiceNumber').value;
        const userId = document.getElementById('userId').value;
        const paymentDate = document.getElementById('paymentDate').value;
        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
        const description = document.getElementById('description').value;

        // Valider les données communes
        if (!invoiceNumber || !userId || !paymentDate) {
          throw new Error('Veuillez remplir tous les champs obligatoires');
        }

        let payload = {
          invoice_number: invoiceNumber,
          user_id: parseInt(userId),
          payment_date: paymentDate,
          payment_method: paymentMethod,
          description: description,
          timestamp: new Date().toISOString()
        };

        // Ajouter les données spécifiques au méthode de paiement
        if (paymentMethod === 'mtn') {
          const mtnNumber = document.getElementById('mtnNumber').value;
          const mtnAmount = document.getElementById('mtnAmount').value;
          const mtnPin = document.getElementById('mtnPin').value;
          const mtnName = document.getElementById('mtnName').value;
          const mtnReference = document.getElementById('mtnReference').value;

          if (!mtnNumber || !mtnAmount || !mtnPin) {
            throw new Error('Veuillez remplir tous les champs MTN obligatoires');
          }

          payload.mtn = {
            number: mtnNumber,
            amount: parseFloat(mtnAmount),
            pin: mtnPin,
            name: mtnName,
            reference: mtnReference
          };
        } else if (paymentMethod === 'bank') {
          const bankName = document.getElementById('bankName').value;
          const bankNameSelect = document.getElementById('bankName_select').value;
          const bankAccount = document.getElementById('bankAccount').value;
          const bankAmount = document.getElementById('bankAmount').value;
          const bankSwift = document.getElementById('bankSwift').value;
          const bankIban = document.getElementById('bankIban').value;
          const bankReference = document.getElementById('bankReference').value;

          if (!bankName || !bankNameSelect || !bankAccount || !bankAmount) {
            throw new Error('Veuillez remplir tous les champs bancaires obligatoires');
          }

          payload.bank = {
            account_holder: bankName,
            bank_name: bankNameSelect,
            account_number: bankAccount,
            amount: parseFloat(bankAmount),
            swift_code: bankSwift || null,
            iban: bankIban || null,
            reference: bankReference
          };
        }

        // Envoyer la transaction au serveur
        console.log('Envoi de la transaction:', payload);
        
        const response = await fetch('/api/transactions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || 'Erreur lors du traitement de la transaction');
        }

        // Afficher le message de succès
        successDiv.classList.remove('hidden');
        document.getElementById('transactionForm').reset();
        
        // Rediriger après 2 secondes
        setTimeout(() => {
          window.location.href = '/bills';
        }, 2000);

      } catch (error) {
        console.error('Erreur:', error);
        errorText.textContent = error.message;
        errorDiv.classList.remove('hidden');
      }
    }

    // Initialiser la date d'aujourd'hui
    document.addEventListener('DOMContentLoaded', function() {
      const today = new Date().toISOString().split('T')[0];
      document.getElementById('paymentDate').value = today;
      document.getElementById('paymentDate').min = today;
    });
 
    // Gestion de la soumission du formulaire
    async function handleTransactions(event) {
      event.preventDefault();

      const errorDiv = document.getElementById('errorMessage');
      const successDiv = document.getElementById('successMessage');
      const errorText = document.getElementById('errorText');

      // Masquer les messages
      errorDiv.classList.add('hidden');
      successDiv.classList.add('hidden');

      try {
        // Récupérer les données communes
        const invoiceNumber = document.getElementById('invoiceNumber').value;
        const userId = document.getElementById('userId').value;
        const paymentDate = document.getElementById('paymentDate').value;
        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
        const description = document.getElementById('description').value;

        // Valider les données communes
        if (!invoiceNumber || !userId || !paymentDate) {
          throw new Error('Veuillez remplir tous les champs obligatoires');
        }

        let payload = {
          invoice_number: invoiceNumber,
          user_id: parseInt(userId),
          payment_date: paymentDate,
          payment_method: paymentMethod,
          description: description,
          timestamp: new Date().toISOString()
        };

        // Ajouter les données spécifiques au méthode de paiement
        if (paymentMethod === 'airtel') {
          const mtnNumber = document.getElementById('airtelNumber').value;
          const mtnAmount = document.getElementById('airtelAmount').value;
          const mtnPin = document.getElementById('airtelPin').value;
          const mtnName = document.getElementById('airtelName').value;
          const mtnReference = document.getElementById('airtelReference').value;
          if (!mtnNumber || !mtnAmount || !mtnPin) {
            throw new Error('Veuillez remplir tous les champs Airtel obligatoires');
          }

          payload.mtn = {
            number: mtnNumber,
            amount: parseFloat(mtnAmount),
            pin: mtnPin,
            name: mtnName,
            reference: mtnReference
          };
        } else if (paymentMethod === 'bank') {
          const bankName = document.getElementById('bankName').value;
          const bankNameSelect = document.getElementById('bankName_select').value;
          const bankAccount = document.getElementById('bankAccount').value;
          const bankAmount = document.getElementById('bankAmount').value;
          const bankSwift = document.getElementById('bankSwift').value;
          const bankIban = document.getElementById('bankIban').value;
          const bankReference = document.getElementById('bankReference').value;

          if (!bankName || !bankNameSelect || !bankAccount || !bankAmount) {
            throw new Error('Veuillez remplir tous les champs bancaires obligatoires');
          }

          payload.bank = {
            account_holder: bankName,
            bank_name: bankNameSelect,
            account_number: bankAccount,
            amount: parseFloat(bankAmount),
            swift_code: bankSwift || null,
            iban: bankIban || null,
            reference: bankReference
          };
        }

        // Envoyer la transaction au serveur
        console.log('Envoi de la transaction:', payload);
        
        const response = await fetch('/api/transactions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || 'Erreur lors du traitement de la transaction');
        }

        // Afficher le message de succès
        successDiv.classList.remove('hidden');
        document.getElementById('transactionForm').reset();
        
        // Rediriger après 2 secondes
        setTimeout(() => {
          window.location.href = '/bills';
        }, 2000);

      } catch (error) {
        console.error('Erreur:', error);
        errorText.textContent = error.message;
        errorDiv.classList.remove('hidden');
      }
    }

    // Initialiser la date d'aujourd'hui
    document.addEventListener('DOMContentLoaded', function() {
      const today = new Date().toISOString().split('T')[0];
      document.getElementById('paymentDate').value = today;
      document.getElementById('paymentDate').min = today;
    });

    // Mise à jour indicators barres + numéro slide
function updateHeroUI(idx) {
  document.querySelectorAll('[data-indicator]').forEach((btn, i) => {
    btn.className = i === idx
      ? 'h-1 rounded-full bg-yellow-400 transition-all duration-500 w-8'
      : 'h-1 rounded-full bg-white/40 hover:bg-white/70 transition-all duration-500 w-4';
  });
  const num = document.getElementById('hero-slide-num');
  if (num) num.textContent = String(idx + 1).padStart(2, '0');

  // Relance l'animation cascade au changement de slide
  const contenu = document.getElementById('contenu');
  if (contenu) {
    contenu.querySelectorAll('[style*="cascadeIn"]').forEach(el => {
      el.style.animation = 'none';
      el.offsetHeight; // reflow
      el.style.animation = '';
    });
  }
}
 
    