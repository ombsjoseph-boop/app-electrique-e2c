
document.addEventListener('DOMContentLoaded', () => {


    
    const form = document.getElementById('contact-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // 🔥 bloque le GET

        var payload = {
            nom: document.getElementById('contact_nom').value.trim(),
            email: document.getElementById('contact_email').value.trim(),
            num_tel: document.getElementById('contact_tel').value.trim(),
            message: document.getElementById('contact_message').value.trim()
        };
        
        fetch('http://127.0.0.1:5001/api/contact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nom: payload.nom,
                email: payload.email,
                num_tel: payload.num_tel,
                message: payload.message
            })
        })
        .then(() => {
            document.getElementById('contact-success').innerText = 'Message envoyé avec succès ✅';
            document.getElementById('contact-success').classList.remove('hidden');
            document.getElementById('contact-error').classList.add('hidden');
            form.reset();
        })
        .catch(err => {
            document.getElementById('contact-error').innerText =
                err.error || 'Method Not Allowed / Erreur serveur';
            document.getElementById('contact-error').classList.remove('hidden');
        });
    });

});

