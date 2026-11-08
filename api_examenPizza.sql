
CREATE DATABASE IF NOT EXISTS pizzeria;
USE pizzeria;

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS detalle_pedidos (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    tamano VARCHAR(20) NOT NULL,
    ingredientes VARCHAR(200),
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
);
SHOW TABLES;
SELECT * FROM pedidos;
SELECT * FROM detalle_pedidos;