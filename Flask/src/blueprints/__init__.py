
from blueprints.pedidos.routes import pedidos_bp
from blueprints.ventas.routes import ventas_bp

def register_blueprint(app):
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(ventas_bp)
