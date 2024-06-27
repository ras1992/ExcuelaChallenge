# API de Usuarios con Flask y MongoDB

Esta es una API desarrollada en Flask para gestionar usuarios utilizando MongoDB como base de datos. Proporciona endpoints para registrar usuarios, autenticación mediante JWT, y operaciones CRUD básicas sobre usuarios.

## Configuración

1. **Instalación de Dependencias:**
   Asegúrate de tener Python y pip instalados. Luego, instala las dependencias necesarias:

   ```bash
   pip install Flask Flask-PyMongo Flask-JWT-Extended pymongo WTForms

2. **Configuración de MongoDB:**

Asegúrate de tener una instancia de MongoDB ejecutándose localmente o especifica la URI de conexión en config.py.
Configuración del Entorno:

Crea un archivo config.py con la configuración de tu aplicación. Un ejemplo básico:

3. **Configuración:**
   Asegúrate de tener la conexión a la base de datos correctamente configurada dentro del archivo config.py:

   ```bash
   class Config:
    MONGO_URI = "URL_ACCESO_MONGODB"
    JWT_SECRET_KEY = "test"  # Clave secreta para JWT
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'


4. **Ejecución:**
   Para ejecutar la aplicación:
   ```bash
   python app.py
   La API estará disponible en http://localhost:5000/.

5. **Utilizacón de rutas:**

Esta es una API desarrollada en Flask para gestionar usuarios utilizando MongoDB como base de datos. Proporciona endpoints para registrar usuarios, autenticación mediante JWT, y operaciones CRUD básicas sobre usuarios.

## Rutas

### GET /

- **Descripción:** Página de inicio de la API.
- **Respuesta:** "¡Bienvenido a la aplicación Flask con MongoDB!"

### POST /register

- **Descripción:** Registrar un nuevo usuario.
- **Parámetros:** JSON con `username`, `password`, y `email`.
- **Respuesta:** JSON con mensaje de éxito o error.

### POST /login

- **Descripción:** Autenticar usuario y generar token JWT.
- **Parámetros:** JSON con `username` y `password`.
- **Respuesta:** JSON con token JWT válido por 24 horas.

### GET /users

- **Descripción:** Obtener información del usuario autenticado.
- **Autenticación:** Requiere token JWT válido.
- **Respuesta:** JSON con información del usuario.

### PUT /user

- **Descripción:** Actualizar información del usuario autenticado.
- **Autenticación:** Requiere token JWT válido.
- **Parámetros:** JSON con `username` y/o `email` a actualizar.
- **Respuesta:** Mensaje de éxito o error.

### DELETE /user

- **Descripción:** Eliminar al usuario autenticado.
- **Autenticación:** Requiere token JWT válido.
- **Respuesta:** Mensaje de éxito o error.

## Consideraciones

- La aplicación está configurada para mostrar mensajes de depuración en la consola (`print`). Para entornos de producción, considera utilizar un sistema de registro más robusto.
- Asegúrate de proteger la clave secreta JWT (`JWT_SECRET_KEY`) y otros datos sensibles en entornos de producción.
- Esta api es solo en concepto para un challenge.