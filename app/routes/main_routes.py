from flask import Blueprint, render_template, request, redirect, flash, session
import sqlite3

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/contact', methods=['POST'])
def contact():
    form = request.form
    try:
        with sqlite3.connect('portfolio.db') as conn:
            c = conn.cursor()
            sql = "INSERT INTO contacts (name, email, phone, company, message) VALUES (?, ?, ?, ?, ?)"
            data = (form['name'], form['email'], form['phone'], form['company'], form['message'])
            c.execute(sql, data)
            conn.commit()
            flash("\u2705 Contact form submitted successfully!", "success")
    except Exception as e:
        flash(f"\u274C Error: {str(e)}", "error")
    return redirect('/')

@main.route('/logout')
def logout():
    session.pop('admin', None)
    flash("\u2705 Logged out successfully.", "success")
    return redirect('/')