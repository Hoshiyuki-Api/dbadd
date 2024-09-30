from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')  # Fallback ke SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model Pengguna
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    expired_date = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Buat tabel jika belum ada
def create_tables():
    with app.app_context():  # Memasukkan ke dalam konteks aplikasi
        db.create_all()

# Route untuk halaman utama
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# Route untuk mendapatkan data pengguna dalam format JSON
@app.route('/users/get/id', methods=['GET'])
def get_user():
    users = User.query.all()
    user_list = [
        {
            str(user.id): user.user_id,
            "name": user.name,
            "phone": user.phone,
            "expired_date": user.expired_date
        }
        for user in users
    ]
    return jsonify({"id": user_list})  # Format respons sesuai permintaan

# Tangani pengiriman form untuk menambah pengguna
@app.route('/adduser', methods=['POST'])
def handle_add_user():
    user_id = request.form['user_id']
    
    # Cek apakah user_id sudah ada
    existing_user = User.query.filter_by(user_id=user_id).first()
    if existing_user:
        return "User ID already exists", 400
    
    user = User(
        user_id=user_id,
        name=request.form['name'],
        phone=request.form.get('phone', ''),
        expired_date=request.form['expired_date']
    )
    db.session.add(user)
    db.session.commit()
    
    return redirect(url_for('index'))

# Tangani pengiriman form untuk mengedit pengguna
@app.route('/edituser', methods=['POST'])
def handle_edit_user():
    user_id = request.form['user_id']
    user = User.query.filter_by(user_id=user_id).first()
    
    if user:
        user.name = request.form.get('name', user.name)
        user.phone = request.form.get('phone', user.phone)
        user.expired_date = request.form.get('expired_date', user.expired_date)
        db.session.commit()
    
    return redirect(url_for('index'))

# Tangani pengiriman form untuk menghapus pengguna
@app.route('/deleteuser', methods=['POST'])
def handle_delete_user():
    user_id = request.form['user_id']
    user = User.query.filter_by(user_id=user_id).first()
    
    if user:
        db.session.delete(user)
        db.session.commit()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_tables()  # Memanggil fungsi untuk membuat tabel
    app.run(debug=True)
