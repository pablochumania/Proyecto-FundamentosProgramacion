from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Usado para mensajes flash

# Funciones de la base de datos
def crear_tablas():
    try:
        conn = sqlite3.connect('gestion_tareas.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS listas_tareas (
                            id INTEGER PRIMARY KEY,
                            nombre TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tareas (
                            id INTEGER PRIMARY KEY,
                            nombre_lista TEXT NOT NULL,
                            nombre_tarea TEXT NOT NULL,
                            descripcion TEXT,
                            fecha_creacion TEXT DEFAULT CURRENT_DATE,
                            fecha_vencimiento TEXT,
                            estado TEXT)''')
        conn.commit()
        print("Tablas creadas exitosamente")
    except sqlite3.Error as e:
        print(f"Error al crear tablas: {e}")
    finally:
        conn.close()

def obtener_listas_tareas():
    conn = sqlite3.connect('gestion_tareas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listas_tareas ORDER BY id DESC")
    listas_tareas = cursor.fetchall()
    conn.close()
    return listas_tareas

def obtener_tareas(lista_id):
    conn = sqlite3.connect('gestion_tareas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tareas WHERE nombre_lista=? ORDER BY id DESC", (lista_id,))
    tareas = cursor.fetchall()
    conn.close()
    return tareas

def crear_nueva_lista(nombre_lista):
    conn = sqlite3.connect('gestion_tareas.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO listas_tareas (nombre) VALUES (?)", (nombre_lista,))
    conn.commit()
    conn.close()

def crear_nueva_tarea(nombre_lista, nombre_tarea, descripcion, fecha_vencimiento, estado):
    estado = bool(int(estado))  # Convertir el estado a un booleano
    conn = sqlite3.connect('gestion_tareas.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tareas (nombre_lista, nombre_tarea, descripcion, fecha_vencimiento, estado) VALUES (?, ?, ?, ?, ?)",
                   (nombre_lista, nombre_tarea, descripcion, fecha_vencimiento, estado))
    conn.commit()
    conn.close()

# Rutas
@app.route('/')
def index():
    listas_tareas = obtener_listas_tareas()
    if not listas_tareas:
        flash('Aún no existe ninguna lista', 'info')
    return render_template('index.html', listas_tareas=listas_tareas)

@app.route('/lista/<int:lista_id>')
def mostrar_tareas(lista_id):
    conn = sqlite3.connect('gestion_tareas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM listas_tareas WHERE id=?", (lista_id,))
    nombre_lista = cursor.fetchone()[0]
    tareas = obtener_tareas(nombre_lista)
    if not tareas:
        flash('No existen tareas para esta lista', 'info')
    return render_template('tareas.html', lista_id=lista_id, nombre_lista=nombre_lista, tareas=tareas)

@app.route('/nueva_lista', methods=['POST'])
def nueva_lista():
    nombre_lista = request.form['nombre_lista']
    crear_nueva_lista(nombre_lista)
    flash('Nueva lista de tareas creada', 'success')
    return redirect(url_for('index'))

@app.route('/nueva_tarea/<int:lista_id>', methods=['POST'])
def nueva_tarea(lista_id):
    nombre_lista = request.form['nombre_lista']
    nombre_tarea = request.form['nombre_tarea']
    descripcion = request.form['descripcion']
    fecha_vencimiento = request.form['fecha_vencimiento']
    estado = request.form['estado']

    crear_nueva_tarea(nombre_lista, nombre_tarea, descripcion, fecha_vencimiento, estado)
    flash('Nueva tarea creada', 'success')
    return redirect(url_for('mostrar_tareas', lista_id=lista_id))

@app.route('/eliminar_tarea/<int:tarea_id>/<int:lista_id>', methods=['POST'])
def eliminar_tarea(tarea_id, lista_id):
    conn = sqlite3.connect('gestion_tareas.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id=?", (tarea_id,))
    conn.commit()
    conn.close()
    flash('Tarea eliminada con éxito', 'success')
    return redirect(url_for('mostrar_tareas', lista_id=lista_id))  # o redirige a la página que prefieras

@app.route('/cambiar_estado/<int:tarea_id>/<int:lista_id>', methods=['POST'])
def cambiar_estado(tarea_id, lista_id):
    conn = sqlite3.connect('gestion_tareas.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tareas SET estado = 1 - estado WHERE id=?", (tarea_id,))
    conn.commit()
    conn.close()
    flash('Estado de la tarea actualizado con éxito', 'success')
    return redirect(url_for('mostrar_tareas', lista_id=lista_id))

if __name__ == "__main__":
    crear_tablas()  # Crear las tablas de la base de datos al iniciar la aplicación
    app.run(debug=True)
