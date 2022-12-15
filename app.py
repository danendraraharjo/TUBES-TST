from flask import Flask, jsonify, request
from database import db
from flask_mail import Mail, Message
import pyotp
import hashlib
import jwt
from datetime import datetime, timedelta
from functools import wraps
import requests
from fractions import Fraction

app = Flask(__name__)
app.config['SECRET_KEY'] = '3LiJVokKUuqYc1XVapGUPAaA22KiLSNp'
# MAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'dgilangraharjo@gmail.com'
app.config['MAIL_PASSWORD'] = 'diuraybiklidoutd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
totp = pyotp.TOTP('MEVKEPQSFBWVKE5IFXLMFN6OBUCJAJAV', interval=600)


PARTNER_API = 'http://127.0.0.1:8080'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({'error': 'Memerlukan akses token.'}), 401

        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            q = db.execute(
                f'''SELECT * FROM user WHERE id = {data['user_id']};  ''')
            data = q.mappings()
            # print(data)
            user = None
            for value in data:
                user = value
        except:
            return jsonify({'error': 'Token invalid!'}), 401
        return f(user, *args, **kwargs)
    return decorated


def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    hashed_password = sha256.hexdigest()
    return hashed_password


@app.route("/get-all-penduduk", methods=["GET"])
@token_required
def get_all_penduduk(user):
    if not user:
        return jsonify({"message": "Silahkan login terlebih dahulu"}), 401
    
    data = db.execute("SELECT * FROM penduduk_2017")
    data = data.mappings()
    result = []
    for value in data:
        result.append(dict(value))
    return jsonify(result)


@ app.route("/get-kecamatan", methods=["GET"])
def get_kecamatan():
    
    kecamatan = request.args.get("nama_kecamatan")
    data = db.execute(f'''
    SELECT * FROM penduduk_2017 WHERE nama_kecamatan = '{kecamatan}';
    ''')
    data = data.mappings()
    result = []
    for value in data:
        result.append(dict(value))
    return jsonify(result)


@ app.route("/get-kelurahan", methods=["GET"])
def get_kelurahan():
    
    kelurahan = request.args.get("nama_kelurahan")
    data = db.execute(f'''
    SELECT * FROM penduduk_2017 WHERE nama_kelurahan = '{kelurahan}';
    ''')
    data = data.mappings()
    result = []
    for value in data:
        result.append(dict(value))
    return jsonify(result)


@app.route("/add-penduduk", methods=["POST"])
def addDataPenduduk():
    try:
        
        data = request.json
        id = data["id"]
        jenis_kelamin = data["jenis_kelamin"]
        jumlah_penduduk = data["jumlah_penduduk"]
        nama_kabupaten_kota = data["nama_kabupaten_kota"]
        nama_kecamatan = data["nama_kecamatan"]
        nama_kelurahan = data["nama_kelurahan"]
        nama_provinsi = data["nama_provinsi"]
        tahun = data["tahun"]
        usia = data["usia"]
        q = db.execute(f'''
        SELECT * FROM penduduk_2017 WHERE id = {id};  
        ''')
        check_data = q.all()
        if len(check_data) == 0:
            db.execute(f'''
        INSERT INTO penduduk_2017 
        (id, jenis_kelamin, jumlah_penduduk, nama_kabupaten_kota, nama_kecamatan, nama_kelurahan, nama_provinsi, tahun, usia)
        VALUES ({id},'{jenis_kelamin}', {jumlah_penduduk}, '{nama_kabupaten_kota}', '{nama_kecamatan}', '{nama_kelurahan}', '{nama_provinsi}', {tahun}, '{usia}');  
        ''')
            db.commit()
        else:
            raise Exception(
                f'Data penduduk dengan id: {id} sudah terdaftar.')
    except Exception as e:
        print(e)
        return ({"message": str(e)})
    return jsonify({"message": f"Berhasil menambahkan data penduduk dengan id: {id}"})


@app.route("/delete-penduduk", methods=["DELETE"])
def deleteDataPenduduk():
    try:
        
        id = request.args.get("id")
        q = db.execute(f'''
        SELECT * FROM penduduk_2017 WHERE id = '{id}';  
        ''')
        check_data = q.all()
        if len(check_data) == 1:
            db.execute(f'''
            DELETE FROM penduduk_2017 
            WHERE id = '{id}';  
            ''')
            db.commit()
        else:
            raise Exception(
                f'Data penduduk dengan id: {id} tidak tersedia.')
    except Exception as e:
        return ({"message": str(e)})
    return jsonify({"message": f"Berhasil menghapus data penduduk dengan id: {id}"})


@app.route("/edit-penduduk", methods=["PUT"])
def editDataPenduduk():
    try:
        data = request.json
        req_id = data["id"]
        jenis_kelamin = data["jenis_kelamin"]
        jumlah_penduduk = data["jumlah_penduduk"]
        nama_kabupaten_kota = data["nama_kabupaten_kota"]
        nama_kecamatan = data["nama_kecamatan"]
        nama_kelurahan = data["nama_kelurahan"]
        nama_provinsi = data["nama_provinsi"]
        tahun = data["tahun"]
        usia = data["usia"]
        q = db.execute(f'''
        SELECT * FROM penduduk_2017 WHERE id = {req_id};  
        ''')
        check_data = q.all()
        if len(check_data) == 1:
            q = db.execute(f'''
        UPDATE penduduk_2017
        SET jenis_kelamin = '{jenis_kelamin}', jumlah_penduduk = {jumlah_penduduk}, nama_kabupaten_kota = '{nama_kabupaten_kota}', nama_kecamatan = '{nama_kecamatan}', 
        nama_kelurahan = '{nama_kelurahan}', nama_provinsi = '{nama_provinsi}', tahun = {tahun}, usia = '{usia}'
        WHERE id = {req_id};
        ''')
            db.commit()
        else:
            raise Exception(
                f'Data penduduk dengan id: {req_id} tidak tersedia.')
    except Exception as e:
        print(e)
        return ({"message": str(e)})
    return jsonify({"message": f"Berhasil mengubah data penduduk dengan id: {req_id}"})


@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        email = data["email"]
        username = data["username"]
        password = data["password"]
        q = db.execute(f'''
        SELECT * FROM user WHERE username = '{username}' or email = '{email}';  
        ''')
        check_data = q.all()
        if len(check_data) == 0:
            db.execute(f'''
        INSERT INTO user
        (email, username, password)
        VALUES ('{email}', '{username}', '{hash_password(password)}');  
        ''')
            db.commit()
        else:
            raise Exception(
                f'User sudah terdaftar, silahkan login')
    except Exception as e:
        print(e)
        return ({"message": str(e)})
    return jsonify({"message": f"Berhasil signup"})


@app.route("/signin", methods=["POST"])
def signin():
    try:
        data = request.json
        username = data["username"]
        password = data["password"]
        q = db.execute(f'''
        SELECT * FROM user WHERE username = '{username}';  
        ''')
        data = q.mappings()
        # print(data)
        user = None
        for value in data:
            user = value
        if user:
            if user['password'] == hash_password(password):
                msg = Message(
                    'Smart Education - Highschool Recommendation',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[user['email']]
                )
                user_otp = totp.now()
                msg.body = f'Kode OTP Anda adalah: {user_otp}. Mohon untuk tidak berikan Kode OTP Anda ke siapapun! Kode ini akan berlaku selama 10 menit.'
                mail.send(msg)
                return jsonify({"message": "Silahkan memasukkan OTP yang telah dikirim"})
            else:
                raise Exception(
                    f'Username atau password salah')
        else:
            raise Exception(
                f'Username atau password salah')
    except Exception as e:
        return ({"message": str(e)})


@app.route("/verify-otp", methods=['GET'])
def verify_otp():
    
    data = request.json
    username = data["username"]
    otp = data["otp"]
    q = db.execute(f'''SELECT * FROM user WHERE username = '{username}';  ''') 
    data = q.mappings()
    # print(data)
    user = None
    for value in data:
        user = value
    if not user:
        return (jsonify({'error': 'Akun tidak ada.'}), 401)
    if totp.verify(otp):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.utcnow() + timedelta(minutes=60)
        }, app.config['SECRET_KEY'])
        return jsonify({'access_token': token})
    return (jsonify({'error': 'OTP Salah.'}), 401)

@app.route("/get-zonasi", methods=["GET"])
def get_zonasi():
    kelurahan1 = request.args.get("kelurahan1")
    kelurahan2 = request.args.get("kelurahan2")
    kelurahan = [kelurahan1,kelurahan2]
    res = []
    try:
        for k in kelurahan:
            q = db.execute(f'''SELECT * FROM penduduk_2017 WHERE nama_kelurahan = '{k}' ''')
            total_penduduk = 0
            data_kel = q.mappings()
            for _ in data_kel:
                if _['usia'] == '15-19':
                    total_penduduk += _['jumlah_penduduk']
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '
            }
            params = '/get-sma?kel=' + k
            response =  requests.get(PARTNER_API+params, headers=headers)
            total_siswa = 0
            for _ in response.json():
                total_siswa += _['jumlah_siswa']
            res.append({
                'kelurahan': k,
                'keketatan': str(Fraction(total_siswa, total_penduduk))
            })
    except:
        return (jsonify({'error': 'Kesalahan server'}), 500)
    return jsonify({'data': res, 'analisis': 'Ezzz deckk'})