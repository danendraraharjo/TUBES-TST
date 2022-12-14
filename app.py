from flask import Flask, jsonify, request
from database import db
from flask_mail import Mail, Message
import pyotp
import hashlib
import jwt
from datetime import datetime, timedelta
from functools import wraps

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
            cur = db.cursor()
            cur.execute(
                f'''SELECT * FROM user WHERE id = {data['user_id']};  ''')
            columns = cur.description
            data = cur.fetchall()
            user = None
            for value in data:
                tmp = {}
                for (index, column) in enumerate(value):
                    tmp[columns[index][0]] = column
                user = tmp
                break
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
    cur = db.cursor()
    cur.execute("SELECT * FROM penduduk_2017")
    data = cur.fetchall()
    columns = cur.description
    result = []
    for value in data:
        tmp = {}
        for (index, column) in enumerate(value):
            tmp[columns[index][0]] = column
        result.append(tmp)
    return jsonify(result)


@ app.route("/get-kecamatan", methods=["GET"])
def get_kecamatan():
    cur = db.cursor()
    kecamatan = request.args.get("nama_kecamatan")
    cur.execute(f'''
    SELECT * FROM penduduk_2017 WHERE nama_kecamatan = '{kecamatan}';
    ''')
    columns = cur.description
    data = cur.fetchall()
    result = []
    for value in data:
        tmp = {}
        for (index, column) in enumerate(value):
            tmp[columns[index][0]] = column
        result.append(tmp)
    return jsonify(result)


@ app.route("/get-kelurahan", methods=["GET"])
def get_kelurahan():
    cur = db.cursor()
    kelurahan = request.args.get("nama_kelurahan")
    cur.execute(f'''
    SELECT * FROM penduduk_2017 WHERE nama_kelurahan = '{kelurahan}';
    ''')
    columns = cur.description
    data = cur.fetchall()
    result = []
    for value in data:
        tmp = {}
        for (index, column) in enumerate(value):
            tmp[columns[index][0]] = column
        result.append(tmp)
    return jsonify(result)


@app.route("/add-penduduk", methods=["POST"])
def addDataPenduduk():
    try:
        cur = db.cursor()
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
        cur.execute(f'''
        SELECT * FROM penduduk_2017 WHERE id = {id};  
        ''')
        check_data = cur.fetchall()
        if len(check_data) == 0:
            cur.execute(f'''
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
        cur = db.cursor()
        id = request.args.get("id")
        cur.execute(f'''
        SELECT * FROM penduduk_2017 WHERE id = '{id}';  
        ''')
        check_data = cur.fetchall()
        if len(check_data) == 1:
            cur.execute(f'''
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
        cur = db.cursor()
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
        cur.execute(f'''
        SELECT * FROM penduduk_2017 WHERE id = {req_id};  
        ''')
        check_data = cur.fetchall()
        if len(check_data) == 1:
            cur.execute(f'''
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
        cur = db.cursor()
        data = request.json
        email = data["email"]
        username = data["username"]
        password = data["password"]
        cur.execute(f'''
        SELECT * FROM user WHERE username = '{username}' or email = '{email}';  
        ''')
        check_data = cur.fetchall()
        if len(check_data) == 0:
            cur.execute(f'''
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
        cur = db.cursor()
        data = request.json
        username = data["username"]
        password = data["password"]
        cur.execute(f'''
        SELECT * FROM user WHERE username = '{username}';  
        ''')
        columns = cur.description
        data = cur.fetchall()
        user = None
        for value in data:
            tmp = {}
            for (index, column) in enumerate(value):
                tmp[columns[index][0]] = column
            user = tmp
            break
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
        print(e)
        return ({"message": str(e)})


@app.route("/verify-otp", methods=['GET'])
def verify_otp():
    cur = db.cursor()
    data = request.json
    username = data["username"]
    otp = data["otp"]
    cur.execute(f'''SELECT * FROM user WHERE username = '{username}';  ''')
    columns = cur.description
    data = cur.fetchall()
    user = None
    for value in data:
        tmp = {}
        for (index, column) in enumerate(value):
            tmp[columns[index][0]] = column
        user = tmp
        break
    if not user:
        return (jsonify({'error': 'Akun tidak ada.'}), 401)
    if totp.verify(otp):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.utcnow() + timedelta(minutes=60)
        }, app.config['SECRET_KEY'])
        return jsonify({'access_token': token})
    return (jsonify({'error': 'OTP Salah.'}), 401)
