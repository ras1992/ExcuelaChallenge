# app.py

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from Dbase.config import Config
from wtforms import Form, StringField, PasswordField, validators
from werkzeug.datastructures import MultiDict
import hashlib
from datetime import datetime, timedelta, timezone
from bson import ObjectId
import logging
import jwt

from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config.from_object(Config)

# Intentar conectar a MongoDB y manejar cualquier excepción que ocurra
try:
    mongo = PyMongo(app)
    jwt2= JWTManager(app)
    mongo.cx.server_info()  # Intenta obtener información del servidor para comprobar la conexión
    print("Conexión a MongoDB establecida correctamente.")
except Exception as e:
    logging.error(f"Error al conectar a MongoDB: {e}")
    print("Error al conectar a MongoDB.")
    mongo = None

@app.route('/')
def index():
    return "¡Bienvenido a la aplicación Flask con MongoDB!"

# Función para hashear la contraseña
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class UserForm(Form):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired(), validators.Length(min=6)])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])


# Ruta para añadir un usuario
@app.route('/register', methods=['POST'])
def add_user():
    if mongo.db is None:
        return jsonify({"error": "Conexión a MongoDB no establecida"}), 500
    
    # Obtener los datos JSON de la solicitud
    json_data = request.get_json()
    
    # Crear un MultiDict a partir de los datos JSON
    form_data = MultiDict(json_data)
    
    # Validar el formulario con los datos convertidos
    form = UserForm(form_data)
    
    # Validar el formulario
    if not form.validate():
        errors = form.errors
        return jsonify({"error": errors}), 400
    
    try:
        # Extraer datos del usuario validados por wtforms
        username = form.username.data
        password = form.password.data
        email = form.email.data
        
        # Hashear la contraseña
        hashed_password = hash_password(password)
        
        # Crear un objeto de usuario con datos adicionales
        user = {
            'username': username,
            'password': hashed_password,
            'email': email,
            'created_at': datetime.utcnow()
        }
        
        # Añadir mensajes de depuración para entender mejor el problema
        print("Intentando añadir usuario:", user)
        
        # Insertar el usuario en la colección 'users'
        result = mongo.db.users.insert_one(user)
        print("Usuario añadido con ID:", result.inserted_id)
        
        return jsonify({"msg": "Usuario añadido con éxito"}), 201
    
    except Exception as e:
        logging.error(f"Error al añadir usuario: {e}")
        return jsonify({"error": f"Error al añadir usuario: {e}"}), 500

# Ruta para loguear
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({"error": "Falta nombre de usuario o contraseña"}), 400

    user = mongo.db.users.find_one({'username': auth['username']})

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Hashear la contraseña proporcionada y compararla con la almacenada
    hashed_password = hash_password(auth['password'])

    if hashed_password == user['password']:
        # Generar token JWT válido por 24 horas
        expiration = datetime.now(timezone.utc) + timedelta(hours=24)
        token = jwt.encode({
            'sub': str(user['_id']),  # Aquí usamos 'sub' en lugar de 'sup'
            'username': user['username'],
            'exp': expiration
        }, app.config['JWT_SECRET_KEY'])

        print(f"Usuario {user['username']} logueado correctamente.")
        
        # Retornar el token como JSON
        return jsonify({'token': token}), 200
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401


# Ruta para obtener todos los usuarios
@app.route('/users', methods=['GET'])
@jwt_required()  # Requiere autenticación JWT
def get_user_info():
    current_user_id = get_jwt_identity()  # Obtiene la identidad del usuario desde el token JWT (como string)
    if not current_user_id:
        return jsonify({"error": "Usuario no encontrado en el token JWT"}), 400
    
    try:
        # Convertir current_user_id a ObjectId
        user_id = ObjectId(current_user_id)
        
        # Buscar al usuario en la base de datos por su _id (ObjectId)
        user_data = mongo.db.users.find_one({'_id': user_id})
        
        if not user_data:
            return jsonify({"error": "Usuario no encontrado en la base de datos"}), 404
        
        # Aquí puedes ajustar los campos que deseas devolver del usuario
        # Por ejemplo, excluyendo el campo '_id' de MongoDB si lo prefieres
        user_data['_id'] = str(user_data['_id'])  # Convertir ObjectId a string
        
        return jsonify(user_data), 200
    except Exception as e:
        app.logger.error(f"Error al obtener información del usuario: {e}")
        return jsonify({"error": "Error al obtener información del usuario"}), 500

# Ruta para editar un usuario
@app.route('/user', methods=['PUT'])
@jwt_required()  # Requiere autenticación JWT
def update_user():
    current_user_id = get_jwt_identity()  # Obtiene la identidad del usuario desde el token JWT (como string)
    if not current_user_id:
        return jsonify({"error": "Usuario no encontrado en el token JWT"}), 400
    
    try:
        # Convertir current_user_id a ObjectId
        user_id = ObjectId(current_user_id)
        
        # Obtener los datos del usuario a actualizar del cuerpo de la solicitud
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({"error": "Datos de actualización no proporcionados"}), 400
        
        # Validar y obtener los campos a actualizar (username y/o email)
        username = update_data.get('username')
        email = update_data.get('email')
        
        # Validar que al menos uno de los campos esté presente para actualizar
        if not (username or email):
            return jsonify({"error": "Se requiere al menos 'username' o 'email' para actualizar"}), 400
        
        
        # Actualizar los campos en la base de datos MongoDB
        update_query = {}
        if username:
            update_query['username'] = username
        if email:
            update_query['email'] = email
        
        # Añadir la fecha de actualización utilizando datetime.now(timezone.utc)
        update_query['updated_at'] = datetime.now(timezone.utc)
        
        # Realizar la actualización en la base de datos
        result = mongo.db.users.update_one(
            {'_id': user_id},
            {'$set': update_query}
        )
        
        if result.modified_count == 1:
            return jsonify({"message": "Usuario actualizado correctamente"}), 200
        else:
            return jsonify({"error": "No se pudo actualizar el usuario"}), 500
    
    except Exception as e:
        app.logger.error(f"Error al actualizar información del usuario: {e}")
        return jsonify({"error": "Error al actualizar información del usuario"}), 500
    
# Ruta para eliminar un usuario
@app.route('/user', methods=['DELETE'])
@jwt_required()  # Requiere autenticación JWT
def delete_user():
    current_user_id = get_jwt_identity()  # Obtiene la identidad del usuario desde el token JWT (como string)
    if not current_user_id:
        return jsonify({"error": "Usuario no encontrado en el token JWT"}), 400
    
    try:
        # Convertir current_user_id a ObjectId
        user_id = ObjectId(current_user_id)
        
        # Eliminar al usuario de la base de datos MongoDB
        result = mongo.db.users.delete_one({'_id': user_id})
        
        if result.deleted_count == 1:
            return jsonify({"message": "Usuario eliminado correctamente"}), 200
        else:
            return jsonify({"error": "No se pudo eliminar el usuario"}), 500
    
    except Exception as e:
        app.logger.error(f"Error al eliminar usuario: {e}")
        return jsonify({"error": "Error al eliminar usuario"}), 500

if __name__ == '__main__':
    app.run(debug=True)
