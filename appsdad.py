from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

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
    cursor.execute('SELECT * FROM Usuarios')
    usuarios = cursor.fetchall()
    return render_template('inicio.html', usuarios=usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['txtUsuarios']
        password = request.form['txtPass']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s',
                       (usuario, password))
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

@app.route('/Foro')
def foro():
    return render_template('Foro.html')

@app.route('/Articulos')
def articulos():
    return render_template('Articulos.html')

@app.route('/Huertos')
def huertos():
    return render_template('Huertos.html')

@app.route('/Citas')
def citas():
    return render_template('Citas.html')

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

        cursor.execute('UPDATE usuarios SET usuario = %s, contraseña = %s, WHERE id = %s',
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


if __name__ == '__main__':
    app.run(port=3000, debug=True)

