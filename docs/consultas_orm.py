# Ejecutar con:  python manage.py shell -c "exec(open('docs/consultas_orm.py', encoding='utf-8').read())"
# Todo corre dentro de una transacción que se revierte al final (no altera tus datos).
from django.db import connection, transaction
from django.db.models import Count, Q
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from biblioteca.models import Autor, Categoria, Ejemplar, Estudiante, Libro, Prestamo

hoy = timezone.localdate()
transaction.set_autocommit(False)
try:
    print("== RETO 1: crear autor, libro y dos copias")
    # Predicción: crea 1 autor, 1 libro, 2 copias; el libro queda con 1 autor.
    autor = Autor.objects.create(nombre="Autor de Prueba")
    cat = Categoria.objects.get(nombre="Novela")
    libro = Libro.objects.create(titulo="Libro de Prueba", anio_publicacion=2024, isbn="978-0000000001", categoria=cat)
    libro.autores.add(autor)
    Ejemplar.objects.create(libro=libro, codigo_inventario="INV-900")
    Ejemplar.objects.create(libro=libro, codigo_inventario="INV-901", condicion="usado")
    print(libro, "| autores:", list(libro.autores.all()), "| copias:", list(libro.ejemplares.values_list("codigo_inventario", flat=True)))

    print("== RETO 2: libros de un autor buscándolo por nombre")
    # Predicción: 2 libros (Cien años de soledad y El amor en los tiempos del cólera).
    print(list(Libro.objects.filter(autores__nombre="Gabriel García Márquez")))

    print("== RETO 3: títulos que contienen una palabra (sin importar mayúsculas)")
    # Predicción: 'SOFTWARE' aparece en 2 títulos (Ingeniería de Software e Historia de la Ingeniería de Software).
    # Nota: en SQLite icontains solo ignora mayúsculas en letras ASCII; con tildes ("INGENIERÍA") no encuentra nada.
    print(list(Libro.objects.filter(titulo__icontains="SOFTWARE")))

    print("== RETO 4: copias disponibles (sin préstamo activo)")
    # Predicción: 8 copias originales - 3 con préstamo activo (INV-001, 004, 006) = 5; más las 2 nuevas del reto 1 = 7.
    activos = Prestamo.objects.filter(fecha_devolucion__isnull=True)
    disp = Ejemplar.objects.exclude(pk__in=activos.values("ejemplar"))
    print(disp.count(), list(disp.values_list("codigo_inventario", flat=True)))

    print("== RETO 5: estudiantes con al menos un préstamo activo, sin repetir")
    # Predicción: Ana, Luis y María (3). Ana tiene 3 préstamos pero solo 1 activo.
    # Las dos condiciones van en el MISMO filter() para que apliquen a la misma fila del JOIN.
    print(list(Estudiante.objects.filter(prestamos__isnull=False, prestamos__fecha_devolucion__isnull=True).distinct()))

    print("== RETO 6: cuántos préstamos ha hecho cada estudiante (incluye devueltos)")
    # Predicción: Ana 3, Luis 2, María 1, Carlos 0.
    for e in Estudiante.objects.annotate(total=Count("prestamos")).order_by("-total"):
        print(e.nombre, e.total)

    print("== RETO 7: libro más prestado")
    # Predicción: 'Cien años de soledad' con 3 préstamos (todos sobre INV-001).
    top = Libro.objects.annotate(total=Count("ejemplares__prestamos")).order_by("-total").first()
    print(top.titulo, top.total)

    print("== RETO 8: estudiantes que nunca han pedido un préstamo")
    # Predicción: solo Carlos Díaz.
    print(list(Estudiante.objects.filter(prestamos__isnull=True)))

    print("== RETO 9: marcar un préstamo como devuelto con la fecha de hoy")
    # Predicción: el préstamo activo de INV-001 (María) queda con fecha_devolucion = hoy.
    p = Prestamo.objects.get(ejemplar__codigo_inventario="INV-001", fecha_devolucion__isnull=True)
    print("antes:", p.fecha_devolucion)
    p.fecha_devolucion = hoy
    p.save()
    p.refresh_from_db()
    print("después (releído de la BD):", p.fecha_devolucion, "| coincide con hoy:", p.fecha_devolucion == hoy)

    print("== RETO 10: borrar un autor y ver qué pasa con sus libros")
    # Predicción: el autor se borra, los libros siguen existiendo (sin ese autor): la relación es
    # ManyToMany, solo se borran las filas de la tabla intermedia, no los libros.
    g = Autor.objects.get(nombre="Gabriel García Márquez")
    antes = Libro.objects.count()
    print("libros antes:", antes, "| libros de García Márquez:", g.libros.count())
    g.delete()
    print("libros después:", Libro.objects.count())
    print("autores de 'Cien años de soledad':", list(Libro.objects.get(titulo="Cien años de soledad").autores.all()))
finally:
    transaction.rollback()
    transaction.set_autocommit(True)
