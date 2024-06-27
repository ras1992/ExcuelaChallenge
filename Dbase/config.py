# config.py

class Config:
    MONGO_URI = "mongodb+srv://excuela-challenge:trauOxbBroEhSUQE@cluster-excuela.fx7c6ld.mongodb.net/excuela?retryWrites=true&w=majority"
    JWT_SECRET_KEY = "test"  # Clave secreta para JWT
    JWT_TOKEN_LOCATION = ['headers', 'cookies'] # Ubicación del Token
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'