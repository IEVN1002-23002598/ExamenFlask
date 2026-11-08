
from flask import Blueprint, jsonify
from database import mysql

ventas_bp = Blueprint(
    'ventas',
    __name__,
    url_prefix='/api/ventas'
)

dias = {
    'lunes': 2, 'martes': 3, 'miercoles': 4,
    'jueves': 5, 'viernes': 6, 'sabado': 7,
    'domingo': 1
}

meses = {
    'enero': 1, 'febrero': 2, 'marzo': 3,
    'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9,
    'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

def convertir_ventas(filas):
    return [
        {
            'idVenta': fila[0],
            'cliente': fila[1],
            'fecha': str(fila[2]),
            'total': float(fila[3])
        }
        for fila in filas
    ]

@ventas_bp.route('/dia/<dia>', methods=['GET'])
def ventas_por_dia(dia):
    numero = dias.get(dia.lower().replace('é', 'e').replace('á', 'a'))

    if numero is None:
        return jsonify({'mensaje': 'Día inválido', 'exito': False}), 400

    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id_pedido, nombre, fecha, total
            FROM pedidos
            WHERE DAYOFWEEK(fecha) = %s
            ORDER BY fecha DESC
        """, (numero,))

        ventas = convertir_ventas(cursor.fetchall())

        return jsonify({
            'ventas': ventas,
            'totalAcumulado': round(sum(v['total'] for v in ventas), 2),
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({'mensaje': str(ex), 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()

@ventas_bp.route('/mes/<mes>', methods=['GET'])
def ventas_por_mes(mes):
    numero = meses.get(mes.lower())

    if numero is None:
        return jsonify({'mensaje': 'Mes inválido', 'exito': False}), 400

    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id_pedido, nombre, fecha, total
            FROM pedidos
            WHERE MONTH(fecha) = %s
            ORDER BY fecha DESC
        """, (numero,))

        ventas = convertir_ventas(cursor.fetchall())

        return jsonify({
            'ventas': ventas,
            'totalAcumulado': round(sum(v['total'] for v in ventas), 2),
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({'mensaje': str(ex), 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()

@ventas_bp.route('/detalle/<int:idVenta>', methods=['GET'])
def detalle_venta(idVenta):
    cursor = None
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT id_pedido, nombre, direccion, telefono, fecha, total
            FROM pedidos WHERE id_pedido = %s
        """, (idVenta,))

        pedido = cursor.fetchone()

        if pedido is None:
            return jsonify({'mensaje': 'Venta no encontrada', 'exito': False}), 404

        cursor.execute("""
            SELECT tamano, ingredientes, cantidad, precio_unitario, subtotal
            FROM detalle_pedidos WHERE id_pedido = %s
        """, (idVenta,))

        pizzas = [
            {
                'tamano': fila[0],
                'ingredientes': fila[1].split(', ') if fila[1] else [],
                'numPizzas': fila[2],
                'precioUnitario': float(fila[3]),
                'subtotal': float(fila[4])
            }
            for fila in cursor.fetchall()
        ]

        return jsonify({
            'exito': True,
            'venta': {
                'idVenta': pedido[0],
                'cliente': pedido[1],
                'direccion': pedido[2],
                'telefono': pedido[3],
                'fecha': str(pedido[4]),
                'total': float(pedido[5])
            },
            'pizzas': pizzas
        }), 200

    except Exception as ex:
        return jsonify({'mensaje': str(ex), 'exito': False}), 500
    finally:
        if cursor is not None:
            cursor.close()
