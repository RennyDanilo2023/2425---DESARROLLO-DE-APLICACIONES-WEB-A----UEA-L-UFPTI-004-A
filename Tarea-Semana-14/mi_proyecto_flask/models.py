from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password_hash):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash
