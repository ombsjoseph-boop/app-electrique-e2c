from flask import request, jsonify,session
from db import get_conn
from datetime import datetime


def register_routes(app):
    @app.route('/api/bills', methods=['GET'])
    def bills_list():
        
       # utilisateur connecté - session ou paramètre user_id; autoriser ?all=1 pour l'application desktop
        user_id = session.get('user_id') or request.args.get('user_id')
        allow_all = (request.args.get('all') == '1') or (request.args.get('admin') == '1')

        if not user_id and not allow_all:
            return jsonify({'error': 'unauthorized'}), 401

        conn = get_conn()
        c = conn.cursor()
        # Si on demande toutes les factures (desktop/admin), ne pas filtrer par user
        if allow_all:
            c.execute('''SELECT id, user_id, user_nom, reference, amount, due_date, status, created_at, paid_at,
                 subscription_fee, consumption_kwh, unit_price, consumption_cost, fourniture_cost, acheminement_cost,
                 tcfe_pct, tcfe_amount, cta_pct, cta_amount, tva_pct, tva_amount, total_amount
                 FROM bills
                 ORDER BY created_at DESC''')
        else:
            try:
                uid = int(user_id)
            except Exception:
                uid = user_id
            c.execute('''SELECT id, user_id, user_nom, reference, amount, due_date, status, created_at, paid_at,
                 subscription_fee, consumption_kwh, unit_price, consumption_cost, fourniture_cost, acheminement_cost,
                 tcfe_pct, tcfe_amount, cta_pct, cta_amount, tva_pct, tva_amount, total_amount
                 FROM bills
                 WHERE user_id = %s
                 ORDER BY created_at DESC''', (uid,))

        rows = c.fetchall()
        conn.close()
        def fmt(dt):
            try:
                return dt.isoformat()
            except Exception:
                return str(dt)

        return jsonify([{
            'id': r[0], 'user_id': r[1], 'user_nom': r[2], 'reference': r[3], 'amount': float(r[4] or 0),
            'due_date': fmt(r[5]), 'status': r[6], 'created_at': fmt(r[7]), 'paid_at': fmt(r[8]) if r[8] else None,
            'subscription_fee': float(r[9] or 0),'consumption_kwh': float(r[10] or 0),'unit_price': float(r[11] or 0),'consumption_cost': float(r[12] or 0),'fourniture_cost': float(r[13] or 0),'acheminement_cost': float(r[14] or 0),
            'tcfe_pct': float(r[15] or 0),'tcfe_amount': float(r[16] or 0),'cta_pct': float(r[17] or 0),'cta_amount': float(r[18] or 0),'tva_pct': float(r[19] or 0),'tva_amount': float(r[20] or 0),'total_amount': float(r[21] or 0)
        } for r in rows])

    @app.route('/api/bills/create', methods=['POST'])
    def create_bill():
        data = request.json or {}
        user_id = data.get('user_id')
        username = data.get('user')
        amount = data.get('amount')
        due_date = data.get('due_date')
        reference = data.get('reference') or f'BILL-{int(datetime.now().timestamp())}'

        conn = get_conn()
        c = conn.cursor()
        uid = None
        user_nom = data.get('user_nom')
        
        try:
            if username:
                c.execute('SELECT id FROM users WHERE username=%s', (username,))
                r = c.fetchone()
                if r:
                    uid = r[0]
                else:
                    try:
                        c.execute('INSERT INTO users (username, password, created_at) VALUES (%s,%s,%s)', (username, 'changeme', datetime.now().isoformat()))
                        conn.commit()
                        uid = c.lastrowid
                    except Exception:
                        try:
                            c.execute('INSERT INTO users (username, password) VALUES (%s,%s)', (username, 'changeme'))
                            conn.commit()
                            uid = c.lastrowid
                        except Exception:
                            uid = None
                if not user_nom:
                    user_nom = username
            elif user_id is not None:
                try:
                    uid_candidate = int(user_id)
                    c.execute('SELECT id FROM users WHERE id=%s', (uid_candidate,))
                    r = c.fetchone()
                    if r:
                        uid = r[0]
                    else:
                        uid = None
                except Exception:
                    uid = None

            subscription_fee = float(data.get('subscription_fee') or 0)
            consumption_kwh = float(data.get('consumption_kwh') or 0)
            unit_price = float(data.get('unit_price') or 0)
            consumption_cost = float(data.get('consumption_cost') or (consumption_kwh * unit_price))
            fourniture_cost = float(data.get('fourniture_cost') or 0)
            acheminement_cost = float(data.get('acheminement_cost') or 0)
            tcfe_pct = float(data.get('tcfe_pct') or 0)
            cta_pct = float(data.get('cta_pct') or 0)
            tva_pct = float(data.get('tva_pct') or 0)

            subtotal = subscription_fee + consumption_cost + fourniture_cost + acheminement_cost
            tcfe_amount = round(subtotal * (tcfe_pct / 100.0), 2)
            cta_amount = round(subtotal * (cta_pct / 100.0), 2)
            tva_amount = round(subtotal * (tva_pct / 100.0), 2)
            total_amount = round(subtotal + tcfe_amount + cta_amount + tva_amount, 2)

            amount_to_store = float(amount) if amount is not None else total_amount

            c.execute('''INSERT INTO bills (user_id, user_nom, reference, amount, due_date, status, created_at,
                subscription_fee, consumption_kwh, unit_price, consumption_cost, fourniture_cost, acheminement_cost,
                tcfe_pct, tcfe_amount, cta_pct, cta_amount, tva_pct, tva_amount, total_amount)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ''', (uid, user_nom, reference, amount_to_store, due_date, 'unpaid', datetime.now().isoformat(),
                  subscription_fee, consumption_kwh, unit_price, consumption_cost, fourniture_cost, acheminement_cost,
                  tcfe_pct, tcfe_amount, cta_pct, cta_amount, tva_pct, tva_amount, total_amount))
            conn.commit()
            bid = c.lastrowid
        finally:
            try:
                c.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

        from .helpers import notify_dashboard
        notify_dashboard()
        return jsonify({'id': bid, 'reference': reference}), 201

    @app.route('/api/bills/<int:bill_id>/pay', methods=['POST'])
    def pay_bill(bill_id):
        data = request.json or {}
        payer = data.get('payer')
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute('UPDATE bills SET status=%s, paid_at=%s WHERE id=%s', ('paid', datetime.now().isoformat(), bill_id))
            conn.commit()
            c.execute('SELECT id, status, paid_at FROM bills WHERE id=%s', (bill_id,))
            row = c.fetchone()
            conn.close()
            from .helpers import notify_dashboard
            notify_dashboard()
            return jsonify({'id': row[0], 'status': row[1], 'paid_at': row[2]}), 200
        except Exception:
            conn.close()
            return jsonify({'error': 'failed'}), 500

    @app.route('/api/bills/<int:bill_id>', methods=['GET'])
    def bill_detail(bill_id):
        user_id = session.get('user_id') or request.args.get('user_id')
        allow_all = (request.args.get('all') == '1') or (request.args.get('admin') == '1')

        if not user_id and not allow_all:
            return jsonify({'error': 'unauthorized'}), 401
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute('''SELECT id, user_id, user_nom, reference, amount, due_date, status, created_at, paid_at,
                         subscription_fee, consumption_kwh, unit_price, consumption_cost, fourniture_cost, acheminement_cost,
                         tcfe_pct, tcfe_amount, cta_pct, cta_amount, tva_pct, tva_amount, total_amount
                         FROM bills WHERE id=%s''', (bill_id,))
            r = c.fetchone()
            conn.close()
            if not r:
                return jsonify({'error': 'not_found'}), 404
            # Si l'appel n'est pas en mode 'all', vérifier que l'utilisateur demandé est propriétaire
            if not allow_all:
                try:
                    uid = int(user_id)
                except Exception:
                    uid = user_id
                if r[1] is not None and uid and int(r[1]) != int(uid):
                    return jsonify({'error': 'forbidden'}), 403
            def fmt(dt):
                try:
                    return dt.isoformat()
                except Exception:
                    return str(dt)
            return jsonify({
                'id': r[0], 'user_id': r[1], 'user_nom': r[2], 'reference': r[3], 'amount': float(r[4] or 0),
                'due_date': fmt(r[5]), 'status': r[6], 'created_at': fmt(r[7]), 'paid_at': fmt(r[8]) if r[8] else None,
                'subscription_fee': float(r[9] or 0),'consumption_kwh': float(r[10] or 0),'unit_price': float(r[11] or 0),'consumption_cost': float(r[12] or 0),'fourniture_cost': float(r[13] or 0),'acheminement_cost': float(r[14] or 0),
                'tcfe_pct': float(r[15] or 0),'tcfe_amount': float(r[16] or 0),'cta_pct': float(r[17] or 0),'cta_amount': float(r[18] or 0),'tva_pct': float(r[19] or 0),'tva_amount': float(r[20] or 0),'total_amount': float(r[21] or 0)
            }), 200
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/bills/<int:bill_id>/pdf', methods=['GET'])
    def bill_pdf(bill_id):
        """Exporte une facture en PDF"""
        user_id = session.get('user_id') or request.args.get('user_id')
        allow_all = (request.args.get('all') == '1') or (request.args.get('admin') == '1')

        if not user_id and not allow_all:
            return jsonify({'error': 'unauthorized'}), 401
        
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute('''SELECT id, user_id, user_nom, reference, amount, due_date, status, created_at, paid_at,
                         subscription_fee, consumption_kwh, unit_price, consumption_cost, fourniture_cost, acheminement_cost,
                         tcfe_pct, tcfe_amount, cta_pct, cta_amount, tva_pct, tva_amount, total_amount
                         FROM bills WHERE id=%s''', (bill_id,))
            r = c.fetchone()
            conn.close()
            
            if not r:
                return jsonify({'error': 'not_found'}), 404
            
            # Vérifier les droits
            if not allow_all:
                try:
                    uid = int(user_id)
                except Exception:
                    uid = user_id
                if r[1] is not None and uid and int(r[1]) != int(uid):
                    return jsonify({'error': 'forbidden'}), 403
            
            # Formatter les données
            bill = {
                'id': r[0],
                'user_id': r[1],
                'user_nom': r[2],
                'reference': r[3],
                'amount': float(r[4] or 0),
                'due_date': str(r[5]) if r[5] else None,
                'status': r[6],
                'created_at': str(r[7]) if r[7] else None,
                'paid_at': str(r[8]) if r[8] else None,
                'subscription_fee': float(r[9] or 0),
                'consumption_kwh': float(r[10] or 0),
                'unit_price': float(r[11] or 0),
                'consumption_cost': float(r[12] or 0),
                'fourniture_cost': float(r[13] or 0),
                'acheminement_cost': float(r[14] or 0),
                'tcfe_pct': float(r[15] or 0),
                'tcfe_amount': float(r[16] or 0),
                'cta_pct': float(r[17] or 0),
                'cta_amount': float(r[18] or 0),
                'tva_pct': float(r[19] or 0),
                'tva_amount': float(r[20] or 0),
                'total_amount': float(r[21] or 0),
            }
            
            # Générer le PDF
            try:
                from bill_pdf_generator import generate_bill_pdf
                pdf_data = generate_bill_pdf(bill)
                
                if pdf_data:
                    from flask import send_file
                    from io import BytesIO
                    return send_file(
                        BytesIO(pdf_data),
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f"{bill['reference']}.pdf"
                    )
                else:
                    return jsonify({'error': 'pdf_generation_failed'}), 500
            except ImportError:
                return jsonify({'error': 'pdf_generator_not_available'}), 501
        except Exception as e:
            try:
                conn.close()
            except:
                pass
            return jsonify({'error': str(e)}), 500
            return jsonify({'error': str(e)}), 500
