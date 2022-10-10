import hashlib
from flask import Flask,render_template,request,jsonify, redirect, session
#Importa la libreria de SQLITE
import sqlite3
from werkzeug.utils import secure_filename
import os

app=Flask(__name__)
FOLDER_IMAGES = 'static/'
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#session(app)
#SESSION_TYPE = 'filesystem'
#app.config.from_object(__name__)
# session(app)
app.secret_key = os.urandom(24)

nombreUsuarioActivo = ""
correo = ""

# Endpoint para cargar formulario Usuarios
@app.route("/",methods=["get"])
def home():
    return render_template("login.html")

# Procesa los datos que vienen del formulario usuarios
# Acepta el método post para recepción de datos
@app.route("/usuarios/procesar", methods=["post"])
def procesar():
    if 'btnGuardar' in request.form:
        # Captura los datos del estudiante desde el formulario enviado por la vista
        
        nombre_cuenta = request.form["Nombre_usu"]
        clave_cuenta = request.form["Contraseña2"]
        perfil_cuenta = request.form["Correo"]
        #fecha_registro(no)
        nombre_usuario = request.form["Nombre"]
        apellido_usuario = request.form["Apellido"]
        fecha_nac_usuario = request.form["Fecha_de_nacimiento"]
        #foto_usuario = request.form[""]

    # Captura los datos del usuario
        user = request.form["Nombre_usu"]
        password = request.form["Contraseña"]
        confirm = request.form["Contraseña2"]
        #Validaciones
        if (password != confirm):
            return "Password no coincide"
        
        if not user:
            return "Debe digitar un username"

        if not password:
            return "Debe digitar un password"
        # Aplica la función hash (haslib) al password
        clave_cuenta = hashlib.sha256(password.encode())
        # Convierte el password a hexadecimal tipo string
        pwd = clave_cuenta.hexdigest()
        #cuenta = request.form["nombre"]
        #usuario = request.form["nombre_usuario"]
        #apellido = request.form["apellido_usuario"]

        # Se obtiene la imagen
        #foto = request.files["foto_usuario"]
        #Obtiene el nombre del archivo
        #nom_archivo = foto.filename
        # Crea la ruta
        ruta2 = FOLDER_IMAGES + "User_with_smile.svg"
        #Guarda el archivo en disco duro
        #foto.save(ruta)

        # Se conecta a la BD
        with sqlite3.connect("pogona.db") as con:
            # Crea un apuntador para manipular la BD
            cur = con.cursor()
            if siExiste(nombre_usuario,perfil_cuenta):
                return "YA existe el Usuario o el Correo!"
            # Ejecuta la sentencia SQL para guardar los datos
            cur.execute("INSERT INTO usuarios (nombre_cuenta,clave_cuenta,perfil_cuenta,nombre_usuario,apellido_usuario,fecha_nac_usuario,foto_usuario) VALUES (?,?,?,?,?,?,?)",[nombre_cuenta,pwd,perfil_cuenta,nombre_usuario,apellido_usuario,fecha_nac_usuario,ruta2])
            # Guardar en BD
            con.commit()
            directorio = "static\\" + perfil_cuenta
            os.mkdir(directorio)
        return "Guardado!! <a href='/'>Ir atrás </a>"
    elif 'btnConsultar' in request.form:
        id = request.form["txtId"]
        with sqlite3.connect("pogona.db") as con:
            # Crea un apuntador para manipular la BD
            cur = con.cursor()
            cur.execute("SELECT * FROM usuarios WHERE id = ?",[id])
            row = cur.fetchone()
            if row:
                return jsonify(row[1])
            else:
                return "Usuario no existe"
    elif 'btnListar' in request.form:
        with sqlite3.connect("pogona.db") as con:
            # Convierte el registro en un diccionario
            con.row_factory = sqlite3.Row
            # Crea un apuntador para manipular la BD
            cur = con.cursor()
            cur.execute("SELECT * FROM usuarios")
            row = cur.fetchall()
            return render_template("lista-usuarios.html", alumnos=row)

# API para loguear
@app.route("/login", methods=["post"])
def login():
    error = [""]
    # Captura los datos enviados
    username = request.form["Nombre_usu"]
    password = request.form["Contraseña"]
    global nombreUsuarioActivo
    nombreUsuarioActivo = username
    global correo
    global id_cuenta

    # Validaciones
    if not username or not password:
        error.append("Username/Password son requeridos")
    
    if len(username) > 50:
        error.append("Username excede longitud máxima")
    
    clave = hashlib.sha256(password.encode())
    pwd = clave.hexdigest()
    
    #Conexión a BD
    with sqlite3.connect("pogona.db") as con:
        # Convierte el registro en un diccionario
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # FORMA INCORRECTA DE REALIZAR UNA CONSULTA SQL (NO CONCATENAR)
        #cur.execute("SELECT 1 FROM usuario5784 WHERE username ='" + username + "' AND password ='" + password +"'")

        # Sentencias preparadas
        cur.execute("SELECT * FROM usuarios WHERE nombre_cuenta = ? AND clave_cuenta = ?",[username, pwd])
        row =cur.fetchone()
        if row:
            # session["usuario"] = row["username"]
            #session["perfil"] = row["username"]
            #nombreUsuarioActivo = username
            cur.execute("SELECT perfil_cuenta FROM usuarios WHERE nombre_cuenta = ? AND clave_cuenta = ?",[username, pwd])
            row = cur.fetchone
            correo = dict(result=[dict(r) for r in cur.fetchall()])
            correo = correo['result'][0]
            listOfKeys = correo.values()
            listOfKeys = list(listOfKeys)
            correo = "".join(listOfKeys)
            #print(listOfKeys)
            #print(listOfKeys[4:20])
            #correo = row. ['apellido_usuario']
            print(correo)
            cur.execute("SELECT id_cuenta FROM usuarios WHERE nombre_cuenta = ? AND clave_cuenta = ?",[username, pwd])
            row = cur.fetchone
            id_cuenta = dict(result=[dict(r) for r in cur.fetchall()])
            print(id_cuenta)
            id_cuenta = id_cuenta['result'][0]
            listOfKeys = id_cuenta.values()
            print(listOfKeys)
            listOfKeys = list(listOfKeys)
            print(listOfKeys)
            #id_cuenta=listOfKeys
            id_cuenta = "".join([str(_) for _ in listOfKeys])
            print(id_cuenta)
            session["user"] = "username"
            session["usuario"] = "username"
            return redirect("cuentaUsuario")
        else:
            error = "Usuario o password no existe"

    
    return render_template("login.html", error = error)


@app.route("/usuarios")
def usuario():
    # if session["perfil"] == "admin" or session["perfil"] == "super-admin":
    # if "usuario" in session:
    return render_template("usuarios.html")

    # return render_template("login.html",error= ["Usuario inválido!"])
"""
Endpoint para registra un usuario en la BD
Metodo : post
return : string
"""
@app.route("/usuario/crear",methods=["post"])
def usuario_crear():
    # Captura los datos del usuario
    user = request.form["nombre_cuenta"]
    password = request.form["clave_cuenta"]
    confirm = request.form["txtConfirmar"]
    #Validaciones
    if (password != confirm):
        return "Password no coincide"
    
    if not user:
        return "Debe digitar un username"

    if not password:
        return "Debe digitar un password"
    # Aplica la función hash (haslib) al password
    clave = hashlib.sha256(password.encode())
    # Convierte el password a hexadecimal tipo string
    pwd = clave.hexdigest()
    # Se conecta a la BD
    with sqlite3.connect("pogona.db") as con:
        cur = con.cursor()
        # Consultar si ya existe Usuario
        if siExiste(user):
            return "YA existe el Usuario!"
        #Crea el nuevo Usuario
        cur.execute("INSERT INTO usuarios (nombre_cuenta, clave_cuenta) VALUES (?,?);",[user, pwd])
        con.commit()
        return "Usuario Creado"    

@app.route("/registrar")
def registrar_usuario():
    return render_template("Registro.html")


def siExiste(user, correo):
     # Se conecta a la BD
    with sqlite3.connect("pogona.db") as con:
        cur = con.cursor()
        # Consultar si ya existe Usuario
        cur.execute("SELECT nombre_cuenta FROM usuarios WHERE nombre_cuenta=?",[user])
        if cur.fetchone():
            return True
        cur.execute("SELECT perfil_cuenta FROM usuarios WHERE perfil_cuenta=?",[correo])
        if cur.fetchone():
            return True
    
    return False

@app.route("/logout")
def logout():
    #if not 'usuario' in session

    session.pop("usuario", None)
    nombreUsuarioActivo = "" 
    id_cuenta = ""
    return redirect("/")

@app.before_request
def antes_de_cada_peticion():
    ruta = request.path
    # Si no ha iniciado sesión y no quiere ir a algo relacionado al login, lo redireccionamos al login
    if not 'usuario' in session and ruta != "/" and ruta != "/login" and ruta != "/registrar" and ruta != "/logout" and not ruta.startswith("/static"):
        print("Inicia sesión para continuar")
        return redirect("/")

#end point de jhony

# Endpoint para cargar formulario Estudiantes
@app.route("/cuentaUsuario",methods=["get"])
def cuentaUsuario():
    #if 'nombreUsuarioActivo' in session:
        #print("Eureka")
        #return redirect("/")
    #nombreUsuarioActivo = "Johny_Urbano"
    #id_cuenta = "1"
    
    with sqlite3.connect("pogona.db") as con:
        # Convierte el registro en un diccionario
        con.row_factory = sqlite3.Row
        # Crea un apuntador para manipular la BD
        cur = con.cursor()
        cur.execute("SELECT * FROM imagenes WHERE id_cuenta=?",[id_cuenta])
        row = cur.fetchall()
        alu=row
        cur.execute("SELECT * FROM usuarios WHERE nombre_cuenta=?",[nombreUsuarioActivo])
        row = cur.fetchall()
        usu=row
    return render_template("cuentaUsuario.html", alumnos=alu, usuario=usu)

@app.route("/imagenes",methods=["get"])
def imagenes():
    nombreUsuario = "Johny"
    #id_cuenta = 1
    with sqlite3.connect("pogona.db") as con:
        # Convierte el registro en un diccionario
        con.row_factory = sqlite3.Row
        # Crea un apuntador para manipular la BD
        cur = con.cursor()
        cur.execute("SELECT * FROM imagenes WHERE id_cuenta=?",[id_cuenta])
        row = cur.fetchall()
        alu=row
        cur.execute("SELECT * FROM usuarios WHERE nombre_cuenta=? and id_cuenta=?",[nombreUsuarioActivo, id_cuenta])
        row = cur.fetchall()
        usu=row
    return render_template("imagenes.html", alumnos=alu, usuario=usu)

@app.route("/cargarimagenes",methods=["get"])
def cargarimagenes():
    return render_template("CargarImagen.html")

@app.route("/cargarimagenes2",methods=["post"])
def cargarimagenes2():
    if 'btnGuardar' in request.form:
        nombreUsuario = "Johny"
        #id_cuenta = 1
        descripcion = request.form["txtDescripcion"]
        comentario = request.form["txtComentario"]
        # Captura los datos del estudiante desde el formulario enviado por la vista
        #nombre = request.form["txtNombre"]
        #direccion = request.form["txtDireccion"]
        #telefono = request.form["txtTelefono"]

        # Se obtiene la imagen
        foto = request.files["txtImagen"]
        #Obtiene el nombre del archivo
        nom_archivo = foto.filename
        # Crea la ruta
        #ruta = FOLDER_IMAGES + secure_filename(nom_archivo)
        ruta2 = FOLDER_IMAGES + correo + "/" + secure_filename(nom_archivo)
        #Guarda el archivo en disco duro
        foto.save(ruta2)
        #ruta = "../" + FOLDER_IMAGES + secure_filename(nom_archivo)
        ruta = "../" + FOLDER_IMAGES + correo + "/" + secure_filename(nom_archivo)

        # Se conecta a la BD
        with sqlite3.connect("pogona.db") as con:
            # Crea un apuntador para manipular la BD
            cur = con.cursor()
            # Ejecuta la sentencia SQL para guardar los datos
            cur.execute("INSERT INTO imagenes (nombre_imagen, url_imagen, id_cuenta, descripcion, comentario) VALUES (?,?,?,?,?)",[nom_archivo, ruta, id_cuenta, descripcion, comentario])
            # Guardar en BD
            con.commit()
        return "Guardado!! <a href='/cargarimagenes'>Ir atrás </a>"
    return render_template("CargarImagen2.html")

@app.route("/eliminarimagenes",methods=["get"])
def eliminarimagenes():
    #return render_template("EliminarImagen.html")
    nombreUsuario = "Johny"
    #id_cuenta = 1
    with sqlite3.connect("pogona.db") as con:
        # Convierte el registro en un diccionario
        con.row_factory = sqlite3.Row
        # Crea un apuntador para manipular la BD
        cur = con.cursor()
        cur.execute("SELECT * FROM imagenes WHERE id_cuenta=?",[id_cuenta])
        row = cur.fetchall()
        alu=row
        cur.execute("SELECT * FROM usuarios WHERE nombre_cuenta=?",[nombreUsuarioActivo])
        row = cur.fetchall()
        usu=row
    return render_template("EliminarImagen.html", alumnos=alu, usuario=usu)

@app.route("/eliminarimagenes2",methods=["post"])
def eliminarimagenes2():
    if 'btnGuardar' in request.form:
        #nombreUsuario = "Johny"
        #id_cuenta = 1
        # Captura los datos del estudiante desde el formulario enviado por la vista
        #nombre = request.form["txtNombre"]
        #direccion = request.form["txtDireccion"]
        #telefono = request.form["txtTelefono"]

        # Se obtiene la imagen
        #foto = request.files["txtImagen"]
        #Obtiene el nombre del archivo
        id_archivo = request.form["txtIdImagen"]
        # Crea la ruta
        #ruta = FOLDER_IMAGES + secure_filename(nom_archivo)
        #Guarda el archivo en disco duro
        #foto.save(ruta)
        #ruta = "../" + FOLDER_IMAGES + secure_filename(nom_archivo)

        # Se conecta a la BD
        with sqlite3.connect("pogona.db") as con:
            # Crea un apuntador para manipular la BD
            cur = con.cursor()
            # Ejecuta la sentencia SQL para guardar los datos
            cur.execute("DELETE FROM imagenes WHERE id_imagen = ?",[id_archivo])
            # Guardar en BD
            con.commit()
        return "Imagen borrada!! <a href='/eliminarimagenes'>Ir atrás </a>"
    
    return render_template("EliminarImagen2.html")
# Fin end point jhony
app.run(debug=True)
