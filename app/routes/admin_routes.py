from flask import Blueprint, render_template, request, redirect, flash, session, jsonify, Response
import sqlite3, random
from app.utils.email_utils import send_email_otp

admin = Blueprint('admin', __name__)

YOUR_EMAIL = 'kingking250700@gmail.com'
OTP_STORE = {}

@admin.route('/login')
def login():
    return render_template('login.html', admin_email=YOUR_EMAIL)

@admin.route('/api/send-otp', methods=['POST'])
def api_send_otp():
    email = request.form.get('email', '').strip().lower()
    if email == YOUR_EMAIL:
        otp = str(random.randint(100000, 999999))
        OTP_STORE[email] = otp
        if send_email_otp(email, otp):
            return jsonify({'status': 'success', 'message': 'OTP sent to your email.'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send OTP.'}), 500
    return jsonify({'status': 'error', 'message': 'Unauthorized email.'}), 401

@admin.route('/api/verify-otp', methods=['POST'])
def api_verify_otp():
    email = request.form.get('email', '').strip().lower()
    otp_entered = request.form.get('otp', '')
    if OTP_STORE.get(email) == otp_entered:
        session['admin'] = True
        OTP_STORE.pop(email)
        return jsonify({'status': 'success', 'message': 'OTP verified!'})
    return jsonify({'status': 'error', 'message': 'Invalid OTP.'}), 400

@admin.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/login')
    with sqlite3.connect('portfolio.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM contacts ORDER BY id DESC")
        contacts = c.fetchall()
    return render_template('AdminDashboard..html', contacts=contacts, viewer_count=len(contacts), admin_email=YOUR_EMAIL)

@admin.route('/delete-contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    if not session.get('admin'):
        return redirect('/login')
    try:
        with sqlite3.connect('portfolio.db') as conn:
            conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            flash("\U0001f5d1\ufe0f Contact deleted successfully!", "success")
    except Exception as e:
        flash(f"\u274C Error deleting contact: {str(e)}", "error")
    return redirect('/admin')

@admin.route('/export-contacts')
def export_contacts():
    if not session.get('admin'):
        return redirect('/login')
    with sqlite3.connect('portfolio.db') as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, email, phone, company, message FROM contacts ORDER BY id DESC")
        contacts = c.fetchall()

    def generate():
        data = ['ID,Name,Email,Phone,Company,Message\n']
        for row in contacts:
            row = [str(item).replace('\n', ' ').replace('\r', '') for item in row]
            data.append(','.join('"%s"' % item.replace('"', '""') for item in row) + '\n')
        return data

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=contacts.csv"})
