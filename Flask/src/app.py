
from flask import Flask
from flask_cors import CORS
from config import config
from database import mysql
from blueprints import register_blueprint

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app, resources={
    r"/api/*": {"origins": "http://localhost:4200"}
})

mysql.init_app(app)
register_blueprint(app)

@app.route('/')
def inicio():
    return {'mensaje': 'API Pizzeria funcionando', 'exito': True}

if __name__ == '__main__':
    app.run(port=5000, debug=True)
