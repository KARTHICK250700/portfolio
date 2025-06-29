from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
import sqlite3, random, smtplib, ssl
from email.mime.text import MIMEText
from flask_cors import CORS
import csv
from flask import Response


app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'  # Change this to a secure random string

# Email config
YOUR_EMAIL = 'kingking250700@gmail.com'
EMAIL_PASSWORD = 'kdvp hgcs ukis pqzw'  # Gmail App password
OTP_STORE = {}

# Initialize DB
def init_db():
    with sqlite3.connect('portfolio.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT, company TEXT, message TEXT)''')
        conn.commit()

init_db()

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Contact Form POST handler
@app.route('/contact', methods=['POST'])
def contact():
    form = request.form
    try:
        with sqlite3.connect('portfolio.db') as conn:
            c = conn.cursor()
            sql = "INSERT INTO contacts (name, email, phone, company, message) VALUES (?, ?, ?, ?, ?)"
            data = (form['name'], form['email'], form['phone'], form['company'], form['message'])
            c.execute(sql, data)
            conn.commit()
            flash("✅ Contact form submitted successfully!", "success")
    except Exception as e:
        flash(f"❌ Error: {str(e)}", "error")
    return redirect('/')

# Admin Login + OTP (single page)
@app.route('/login')
def login():
    return render_template('login.html', admin_email=YOUR_EMAIL)

# AJAX: Send OTP
@app.route('/api/send-otp', methods=['POST'])
def api_send_otp():
    email = request.form.get('email', '').strip().lower()
    if email == YOUR_EMAIL:
        otp = str(random.randint(100000, 999999))
        OTP_STORE[email] = otp
        if send_email_otp(email, otp):
            return jsonify({'status': 'success', 'message': 'OTP sent to your email.'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send OTP. Check email config.'}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Unauthorized email address.'}), 401

# AJAX: Verify OTP
@app.route('/api/verify-otp', methods=['POST'])
def api_verify_otp():
    email = request.form.get('email', '').strip().lower()
    otp_entered = request.form.get('otp', '')
    if OTP_STORE.get(email) == otp_entered:
        session['admin'] = True
        OTP_STORE.pop(email)
        return jsonify({'status': 'success', 'message': 'OTP verified!'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid OTP.'}), 400

# Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/login')
    with sqlite3.connect('portfolio.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM contacts ORDER BY id DESC")
        contacts = c.fetchall()
    return render_template('AdminDashboard..html',
                           contacts=contacts,
                           viewer_count=len(contacts),
                           admin_email=YOUR_EMAIL)

# Delete a Contact
@app.route('/delete-contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    if not session.get('admin'):
        return redirect('/login')
    try:
        with sqlite3.connect('portfolio.db') as conn:
            conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            flash("🗑️ Contact deleted successfully!", "success")
    except Exception as e:
        flash(f"❌ Error deleting contact: {str(e)}", "error")
    return redirect('/admin')

@app.route('/export-contacts')
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

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=contacts.csv"})


# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("✅ Logged out successfully.", "success")
    return redirect('/')

# Send OTP Email
def send_email_otp(to_email, otp):
    try:
        msg = MIMEText(f"Your OTP is: {otp}")
        msg['Subject'] = "Your Login OTP"
        msg['From'] = YOUR_EMAIL
        msg['To'] = to_email

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(YOUR_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email sending failed:", e)
        return False

if __name__ == '__main__':
    app.run(debug=True)
