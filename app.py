# app.py
import os
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from factory import ItemFactory
from strategies import EstrategiaPorTempo
from database import db

app = Flask(__name__)
app.secret_key = 'chave_secreta_projeto_estudos'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    data = db.buscar_um(
        "SELECT id, username FROM usuarios WHERE id = ?",
        (user_id,)
    )
    if data: return User(id=data[0], username=data[1])
    return None

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, meta_minutos INTEGER DEFAULT 0, total_segundos INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS jardim (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_planta TEXT, usuario_id INTEGER, posicao INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS repositorio (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, titulo TEXT, conteudo TEXT, resposta TEXT, usuario_id INTEGER)')
    conn.commit()
    conn.close()

init_db()


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        user, pwd = request.form.get('username'), request.form.get('password')
        try:
            db.executar(
                "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                (user, pwd)
            )
            flash('Conta criada! Faça login.')
            return redirect(url_for('login'))
        except: flash('Usuário já existe.')
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user, pwd = request.form.get('username'), request.form.get('password')
        data = db.buscar_um(
            "SELECT id, username, password FROM usuarios WHERE username = ?",
            (user,)
        )
        if data and data[2] == pwd:
            login_user(User(data[0], data[1]))
            return redirect(url_for('index'))
        flash('Usuário ou senha incorretos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index(): return render_template('index.html')
@app.route('/timer', methods=['GET', 'POST'])
@login_required
def timer():
    if request.method == 'POST':
        duracao = int(request.form.get('duracao', 0))
        estrategia = EstrategiaPorTempo()
        planta = estrategia.escolher(duracao)

        max_pos = db.buscar_um(
            "SELECT MAX(posicao) FROM jardim WHERE usuario_id = ?",
            (current_user.id,)
        )[0]
        nova_posicao = (max_pos or 0) + 1

        db.executar(
            "INSERT INTO jardim (tipo_planta, usuario_id, posicao) VALUES (?, ?, ?)",
            (planta, current_user.id, nova_posicao)
        )
        db.executar(
            "UPDATE usuarios SET total_segundos = total_segundos + ? WHERE id = ?",
            (duracao, current_user.id)
        )
        flash(f"Sessão finalizada! {duracao // 60} minutos contabilizados.")
        return redirect(url_for('jardim'))
    return render_template('timer.html')

@app.route('/metas', methods=['GET', 'POST'])
@login_required
def metas():
    if request.method == 'POST':
        nova_meta = request.form.get('nova_meta')
        if nova_meta:
            db.executar(
                "UPDATE usuarios SET meta_minutos = ? WHERE id = ?",
                (nova_meta, current_user.id)
            )
            flash(f"Meta de {nova_meta} minutos definida!")
        if 'resgatar' in request.form:
            plantas = ["Carvalho", "Cerejeira", "Cacto"]
            max_pos = db.buscar_um(
                "SELECT MAX(posicao) FROM jardim WHERE usuario_id = ?",
                (current_user.id,)
            )[0]
            nova_posicao = (max_pos or 0) + 1
            for i in range(5):
                db.executar(
                    "INSERT INTO jardim (tipo_planta, usuario_id, posicao) VALUES (?, ?, ?)",
                    (random.choice(plantas), current_user.id, nova_posicao + i)
                )
            db.executar(
                "UPDATE usuarios SET meta_minutos = 0 WHERE id = ?",
                (current_user.id,)
            )
            flash("Parabéns! 5 árvores bônus foram adicionadas ao seu jardim!")
            return redirect(url_for('jardim'))

    user_data = db.buscar_um(
        "SELECT meta_minutos, total_segundos FROM usuarios WHERE id = ?",
        (current_user.id,)
    )
    meta, total_minutos = user_data[0], user_data[1] // 60
    pode_resgatar = meta > 0 and total_minutos >= meta
    return render_template('metas.html', meta=meta, total_minutos=total_minutos, pode_resgatar=pode_resgatar)
@app.route('/jardim')
@login_required
def jardim():
    plantas = db.buscar(
        "SELECT id, tipo_planta FROM jardim WHERE usuario_id = ? ORDER BY posicao ASC",
        (current_user.id,)
    )
    return render_template('jardim.html', plantas=plantas)

@app.route('/reordenar', methods=['POST'])
@login_required
def reordenar():
    ordem_ids = request.get_json()
    for index, planta_id in enumerate(ordem_ids):
        db.executar(
            "UPDATE jardim SET posicao = ? WHERE id = ? AND usuario_id = ?",
            (index, planta_id, current_user.id)
        )
    return jsonify({"status": "sucesso"})
@app.route('/repositorio/<tipo>')
@login_required
def ver_repositorio(tipo):
    itens = db.buscar(
        "SELECT id, titulo, conteudo, resposta FROM repositorio WHERE tipo=? AND usuario_id=?",
        (tipo, current_user.id)
    )
    return render_template('repositorio.html', tipo=tipo, itens=itens)

@app.route('/adicionar/<tipo>', methods=['POST'])
@login_required
def adicionar(tipo):
    try:
        novo_item = ItemFactory.criar(tipo, request.form, current_user.id, request.files)
        novo_item.salvar()
    except ValueError as e:
        flash(str(e))
    return redirect(url_for('ver_repositorio', tipo=tipo))

if __name__ == '__main__':
    app.run(debug=True)