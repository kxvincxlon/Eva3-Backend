"""
Script para crear datos de ejemplo en el sistema de inventario
Ejecutar con: python manage.py shell < create_sample_data.py
"""

from inventario.models import Producto

# Crear productos de ejemplo
productos_ejemplo = [
    {
        'nombre': 'Laptop Dell Inspiron 15',
        'descripcion': 'Laptop con procesador Intel Core i5, 8GB RAM, 256GB SSD, pantalla de 15.6 pulgadas',
        'precio': 899.99,
        'stock': 15
    },
    {
        'nombre': 'Mouse Inalámbrico Logitech',
        'descripcion': 'Mouse inalámbrico con tecnología USB, ergonómico, batería de larga duración',
        'precio': 25.50,
        'stock': 50
    },
    {
        'nombre': 'Teclado Mecánico RGB',
        'descripcion': 'Teclado mecánico con switches azules, retroiluminación RGB personalizable',
        'precio': 120.00,
        'stock': 8
    },
    {
        'nombre': 'Monitor 24" Full HD',
        'descripcion': 'Monitor LED de 24 pulgadas, resolución 1920x1080, conectividad HDMI y VGA',
        'precio': 180.75,
        'stock': 12
    },
    {
        'nombre': 'Webcam HD',
        'descripcion': 'Cámara web con resolución 1080p, micrófono integrado, ideal para videollamadas',
        'precio': 45.99,
        'stock': 25
    },
    {
        'nombre': 'Disco Duro Externo 1TB',
        'descripcion': 'Disco duro portátil de 1TB, USB 3.0, compatible con Windows y Mac',
        'precio': 75.00,
        'stock': 3
    }
]

print("Creando productos de ejemplo...")

for producto_data in productos_ejemplo:
    producto, created = Producto.objects.get_or_create(
        nombre=producto_data['nombre'],
        defaults=producto_data
    )
    if created:
        print(f"✓ Producto creado: {producto.nombre}")
    else:
        print(f"- Producto ya existe: {producto.nombre}")

print(f"\nTotal de productos en la base de datos: {Producto.objects.count()}")
print("¡Datos de ejemplo creados exitosamente!")
