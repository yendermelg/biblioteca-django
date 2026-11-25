# Ejecutar con:  python manage.py shell -c "exec(open('docs/optimizacion_n_mas_1.py', encoding='utf-8').read())"
from django.db import connection
from django.test.utils import CaptureQueriesContext

from biblioteca.models import Libro, Prestamo

print("Préstamos en la BD:", Prestamo.objects.count(), "| Libros:", Libro.objects.count())

# --- Caso 1: préstamo -> estudiante, ejemplar -> libro
# Predicción antes: 1 (lista) + 6 (estudiante) + 6 (ejemplar) + 6 (libro) = 19
with CaptureQueriesContext(connection) as ctx:
    for p in Prestamo.objects.all():
        p.estudiante.nombre, p.ejemplar.libro.titulo
print("Caso 1 ANTES  :", len(ctx), "consultas")

# Predicción después: 1 consulta (JOIN de las 4 tablas)
with CaptureQueriesContext(connection) as ctx:
    for p in Prestamo.objects.select_related("estudiante", "ejemplar__libro"):
        p.estudiante.nombre, p.ejemplar.libro.titulo
print("Caso 1 DESPUÉS:", len(ctx), "consultas")

# --- Caso 2: libro -> lista de autores (ManyToMany)
# Predicción antes: 1 (libros) + 5 (autores de cada libro) = 6
with CaptureQueriesContext(connection) as ctx:
    for l in Libro.objects.all():
        [a.nombre for a in l.autores.all()]
print("Caso 2 ANTES  :", len(ctx), "consultas")

# Predicción después: 2 (una para libros, otra para todos los autores)
with CaptureQueriesContext(connection) as ctx:
    for l in Libro.objects.prefetch_related("autores"):
        [a.nombre for a in l.autores.all()]
print("Caso 2 DESPUÉS:", len(ctx), "consultas")
