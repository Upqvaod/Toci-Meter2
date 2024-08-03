from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'tocimeter'
app.secret_key = 'mysecretkey'

mysql = MySQL(app)

@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    return render_template('login.html', usuarios=usuarios)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['txtUsuario']
        password = request.form['txtPass']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s', (usuario, password))
        account = cursor.fetchone()

        if account:
            return redirect(url_for('inicio'))
        else:
            flash('Usuario, contraseña o perfil incorrectos', 'danger')

    return render_template('login.html')

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM plantas WHERE nombre LIKE %s OR descripcion LIKE %s', ('%' + query + '%', '%' + query + '%'))
    resultados = cursor.fetchall()
    return render_template('Plantas.html', query=query, plantas=resultados)

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

@app.route('/Plantas')
def plantas():
    return render_template('Plantas.html')

@app.route('/Herramientas')
def herramientas():
    return render_template('Herramientas.html')

@app.route('/Foro', methods=['GET', 'POST'])
def foro():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        contenido = request.form['contenido']
        autor = "Anonimo"  # Reemplaza con el nombre del usuario logueado si tienes un sistema de autenticación
        cursor.execute('INSERT INTO publicaciones (contenido, autor) VALUES (%s, %s)', (contenido, autor))
        mysql.connection.commit()
        flash('Publicación exitosa', 'success')
        return redirect(url_for('foro'))

    cursor.execute('SELECT * FROM publicaciones ORDER BY fecha_publicacion DESC')
    publicaciones = cursor.fetchall()
    return render_template('foro.html', publicaciones=publicaciones)

@app.route('/Articulos')
def articulos():
    return render_template('Articulos.html')

@app.route('/Huertos')
def huertos():
    return render_template('Huertos.html')

@app.route('/crear_cita', methods=['POST'])     
def crear_cita():
    fecha_consulta = request.form['fecha_consulta']
    hora_consulta = request.form['hora_consulta']
    duracion = request.form['duracion']
    id_experto = request.form['id_experto']
    id_usuario = request.form['id_usuario']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        INSERT INTO Consulta (fecha_consulta, hora, duracion, id_experto, id_usuario)
        VALUES (%s, %s, %s, %s, %s)
    """, (fecha_consulta, hora_consulta, duracion, id_experto, id_usuario))
    mysql.connection.commit()
    cursor.close()
    
    flash('Cita generada exitosamente', 'success')
    return redirect(url_for('citas'))

@app.route('/Citas')
def citas():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Consulta')
    consultas = cursor.fetchall()
    return render_template('Citas.html', consultas=consultas)


@app.route('/logout')
def logout():
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['txtUsuario']
        nombre = request.form['txtNombre']
        email = request.form['txtEmail']
        telefono = request.form['txtTelefono']
        fecha_nacimiento = request.form['txtFechaNacimiento']
        direccion = request.form['txtDireccion']
        contraseña = request.form['txtPass']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO usuarios (usuario, nombre, email, telefono, fecha_nacimiento, direccion, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (usuario, nombre, email, telefono, fecha_nacimiento, direccion, contraseña))
        mysql.connection.commit()
        flash('Usuario registrado satisfactoriamente', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_user(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        usuario = request.form['txtUsuario']
        password = request.form['txtPass']

        cursor.execute('UPDATE usuarios SET usuario = %s, contraseña = %s WHERE id = %s',
                       (usuario, password, id))
        mysql.connection.commit()
        flash('Usuario actualizado satisfactoriamente')
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM usuarios WHERE id = %s', [id])
    usuario = cursor.fetchone()
    return render_template('edit.html', usuario=usuario)

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete_user(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM usuarios WHERE id = %s', [id])
    mysql.connection.commit()
    flash('Usuario eliminado satisfactoriamente')
    return redirect(url_for('index'))

@app.route('/get_publicaciones')
def get_publicaciones():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM publicaciones ORDER BY fecha_publicacion DESC')
    publicaciones = cursor.fetchall()
    return jsonify(publicaciones)

@app.route('/Huertos', methods=['GET', 'POST'])
def gestionar_huertos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        imagen = request.files['imagen']

        if imagen:
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"
        else:
            imagen_path = None

        cursor.execute('INSERT INTO huertas (nombre, descripcion, imagen_path) VALUES (%s, %s, %s)',
                       (nombre, descripcion, imagen_path))
        mysql.connection.commit()
        flash('Huerta añadida exitosamente', 'success')
        return redirect(url_for('gestionar_huertos'))

    cursor.execute('SELECT * FROM huertas')
    huertas = cursor.fetchall()
    return render_template('huertos.html', huertas=huertas)


@app.route('/huertos/delete/<int:id>', methods=['POST'])
def delete_huerto(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM huertas WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Huerta eliminada exitosamente', 'success')
    return redirect(url_for('gestionar_huertos'))

@app.route('/huertos/edit/<int:id>', methods=['POST'])
def edit_huerto(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    cursor.execute('UPDATE huertas SET nombre = %s, descripcion = %s WHERE id = %s', 
                   (nombre, descripcion, id))
    mysql.connection.commit()
    flash('Huerta actualizada exitosamente', 'success')
    return redirect(url_for('gestionar_huertos'))



@app.route('/inicio2')
def inicio2():
    return render_template('inicio2.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)
