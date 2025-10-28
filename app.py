from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime
import re

# Hola Yo estoy aquí :
app = Flask(__name__)
app.secret_key = 'tu-clave-secreta-aqui'  # Cambia por una clave fija para desarrollo
app.config['DATABASE'] = 'database/app.db'

def get_db_connection():
    """Establece conexión con la base de datos"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos con tablas necesarias"""
    os.makedirs('database', exist_ok=True)
    conn = get_db_connection()
    
    # Tabla de usuarios
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de tareas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            status TEXT DEFAULT 'active',
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Insertar usuario demo si no existe
    try:
        password_hash = hashlib.sha256('demo123'.encode()).hexdigest()
        conn.execute(
            'INSERT OR IGNORE INTO users (username, email, password) VALUES (?, ?, ?)',
            ('demo', 'demo@example.com', password_hash)
        )
        
        # Insertar algunas tareas de demo
        conn.execute(
            'INSERT OR IGNORE INTO tasks (title, description, category, user_id) VALUES (?, ?, ?, ?)',
            ('Tarea de ejemplo', 'Esta es una tarea de demostración', 'trabajo', 1)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    
    conn.close()

def hash_password(password):
    """Hashea la contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def login_required(f):
    """Decorator para requerir autenticación"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de Autenticación
@app.route('/')
def index():
    """Página principal"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Manejo de login"""
    print(f"Método de request: {request.method}")  # Debug
    
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        print("Procesando POST request")  # Debug
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"Usuario: {username}, Password: {password}")  # Debug
        
        if not username or not password:
            flash('Por favor, completa todos los campos.', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            flash(f'¡Bienvenido, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    
    # GET request
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validaciones
        if not all([username, email, password, confirm_password]):
            flash('Por favor, completa todos los campos.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Por favor, ingresa un email válido.', 'error')
            return render_template('register.html')
        
        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hash_password(password))
            )
            conn.commit()
            conn.close()
            
            flash('¡Registro exitoso! Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
            flash('El usuario o email ya existen.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

# Rutas del CRUD de Tareas
@app.route('/dashboard')
@login_required
def dashboard():
    """Panel principal del usuario"""
    conn = get_db_connection()
    tasks = conn.execute(
        '''SELECT * FROM tasks 
           WHERE user_id = ? AND status = 'active' 
           ORDER BY created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('dashboard.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    """Agregar nueva tarea"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        
        if not title:
            flash('El título es obligatorio.', 'error')
            return render_template('add_item.html')
        
        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO tasks (title, description, category, user_id) VALUES (?, ?, ?, ?)',
                (title, description, category, session['user_id'])
            )
            conn.commit()
            conn.close()
            
            flash('¡Tarea agregada correctamente!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash('Error al agregar la tarea.', 'error')
    
    return render_template('add_item.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Editar tarea existente"""
    conn = get_db_connection()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, session['user_id'])
    ).fetchone()
    
    if not task:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        
        if not title:
            flash('El título es obligatorio.', 'error')
            return render_template('edit_item.html', task=task)
        
        try:
            conn.execute(
                '''UPDATE tasks SET title = ?, description = ?, category = ?, 
                   updated_at = CURRENT_TIMESTAMP WHERE id = ?''',
                (title, description, category, task_id)
            )
            conn.commit()
            conn.close()
            
            flash('¡Tarea actualizada correctamente!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash('Error al actualizar la tarea.', 'error')
    
    conn.close()
    return render_template('edit_item.html', task=task)

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    """Eliminar tarea (soft delete)"""
    conn = get_db_connection()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, session['user_id'])
    ).fetchone()
    
    if not task:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        conn.execute(
            'UPDATE tasks SET status = "deleted" WHERE id = ?',
            (task_id,)
        )
        conn.commit()
        conn.close()
        
        flash('¡Tarea eliminada correctamente!', 'success')
    except Exception as e:
        flash('Error al eliminar la tarea.', 'error')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    print("=== Iniciando aplicación Flask ===")
    print("URL: http://localhost:5000")
    print("Usuario demo: demo")
    print("Contraseña demo: demo123")
    app.run(host='0.0.0.0', port=5000, debug=True)
