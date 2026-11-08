
from flask import Blueprint, jsonify, request
from database import mysql
from datetime import date

pedidos_bp = Blueprint(
    'pedidos',
    __name__,
    url_prefix='/api/pedidos'
)

@pedidos_bp.route('', methods=['POST'])
def registrar_pedido():
    cursor = None

    try:
        datos = request.get_json()
        if not isinstance(datos, dict):
            return jsonify({'mensaje': 'JSON inválido', 'exito': False}), 400

        cliente = datos.get('cliente', {})
        pizzas = datos.get('pizzas', [])

        if not isinstance(cliente, dict) or not isinstance(pizzas, list):
            return jsonify({'mensaje': 'Datos inválidos', 'exito': False}), 400

        if not all(cliente.get(campo) for campo in ['nombre', 'direccion', 'telefono']):
            return jsonify({'mensaje': 'Faltan datos del cliente', 'exito': False}), 400

        if not pizzas:
            return jsonify({'mensaje': 'Agrega al menos una pizza', 'exito': False}), 400

        precios = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
        ingredientes_validos = {'Jamón', 'Piña', 'Champiñones'}
        detalles = []
        total = 0

        for pizza in pizzas:
            tamano = pizza.get('tamano')
            ingredientes = pizza.get('ingredientes', [])
            cantidad = pizza.get('numPizzas')

            if tamano not in precios:
                return jsonify({'mensaje': 'Tamaño inválido', 'exito': False}), 400

            if not isinstance(ingredientes, list) or len(ingredientes) != len(set(ingredientes)) or any(i not in ingredientes_validos for i in ingredientes):
                return jsonify({'mensaje': 'Ingredientes inválidos', 'exito': False}), 400

            if type(cantidad) is not int or cantidad < 1:
                return jsonify({'mensaje': 'Cantidad inválida', 'exito': False}), 400

            precio_unitario = precios[tamano] + len(ingredientes) * 10
            subtotal = precio_unitario * cantidad
            total += subtotal

            detalles.append((tamano, ', '.join(ingredientes), cantidad, precio_unitario, subtotal))

        fecha = cliente.get('fecha') or date.today().isoformat()
        try:
            fecha = date.fromisoformat(fecha).isoformat()
        except (ValueError, TypeError):
            return jsonify({'mensaje': 'Fecha inválida', 'exito': False}), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO pedidos (nombre, direccion, telefono, fecha, total)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            cliente['nombre'],
            cliente['direccion'],
            cliente['telefono'],
            fecha,
            total
        ))

        id_pedido = cursor.lastrowid

        for tamano, ingredientes, cantidad, precio, subtotal in detalles:
            cursor.execute("""
                INSERT INTO detalle_pedidos
                (id_pedido, tamano, ingredientes, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                id_pedido, tamano, ingredientes,
                cantidad, precio, subtotal
            ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Pedido registrado correctamente',
            'exito': True,
            'idVenta': id_pedido,
            'total': total
        }), 201

    except Exception as ex:
        mysql.connection.rollback()
        return jsonify({
            'mensaje': 'Error al registrar pedido',
            'error': str(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
