from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from biblioteca.models import Autor, Categoria, Ejemplar, Estudiante, Libro, Prestamo


class Command(BaseCommand):
    help = "Carga datos de prueba (5 libros, 3 autores, 8 copias, 4 estudiantes, 6 préstamos)."

    def handle(self, *args, **options):
        if Libro.objects.exists():
            self.stdout.write("Ya hay datos; no se carga nada.")
            return
        hoy = timezone.localdate()

        novela = Categoria.objects.create(nombre="Novela")
        ing = Categoria.objects.create(nombre="Ingeniería")
        hist = Categoria.objects.create(nombre="Historia")

        garcia = Autor.objects.create(nombre="Gabriel García Márquez")
        martin = Autor.objects.create(nombre="Robert C. Martin")
        sommer = Autor.objects.create(nombre="Ian Sommerville")

        cien = Libro.objects.create(titulo="Cien años de soledad", anio_publicacion=1967,
                                    isbn="978-0307474728", categoria=novela)
        cien.autores.add(garcia)
        amor = Libro.objects.create(titulo="El amor en los tiempos del cólera", anio_publicacion=1985,
                                    isbn="978-0307389732", categoria=novela)
        amor.autores.add(garcia)
        clean = Libro.objects.create(titulo="Clean Code", anio_publicacion=2008,
                                     isbn="978-0132350884", categoria=ing)
        clean.autores.add(martin)
        se = Libro.objects.create(titulo="Ingeniería de Software", anio_publicacion=2011,
                                  isbn="978-0137035151", categoria=ing)
        se.autores.add(sommer)
        # Libro con dos autores (para probar el many-to-many)
        arq = Libro.objects.create(titulo="Historia de la Ingeniería de Software", anio_publicacion=2015,
                                   isbn="978-1234567890", categoria=hist)
        arq.autores.add(martin, sommer)

        def copia(codigo, libro, cond="nuevo"):
            return Ejemplar.objects.create(codigo_inventario=codigo, libro=libro, condicion=cond)

        c1 = copia("INV-001", cien)
        c2 = copia("INV-002", cien, "usado")
        c3 = copia("INV-003", amor)
        c4 = copia("INV-004", clean)
        c5 = copia("INV-005", clean, "usado")
        c6 = copia("INV-006", se)
        c7 = copia("INV-007", se, "danado")
        c8 = copia("INV-008", arq)

        e1 = Estudiante.objects.create(codigo="1152001", nombre="Ana Pérez", correo="ana@ufps.edu.co")
        e2 = Estudiante.objects.create(codigo="1152002", nombre="Luis Gómez", correo="luis@ufps.edu.co")
        e3 = Estudiante.objects.create(codigo="1152003", nombre="María Rojas", correo="maria@ufps.edu.co")
        Estudiante.objects.create(codigo="1152004", nombre="Carlos Díaz", correo="carlos@ufps.edu.co")

        d = lambda n: hoy - timedelta(days=n)
        # Devueltos
        Prestamo.objects.create(ejemplar=c1, estudiante=e1, fecha_prestamo=d(30), fecha_limite=d(16), fecha_devolucion=d(20))
        Prestamo.objects.create(ejemplar=c4, estudiante=e1, fecha_prestamo=d(25), fecha_limite=d(11), fecha_devolucion=d(12))
        Prestamo.objects.create(ejemplar=c1, estudiante=e2, fecha_prestamo=d(15), fecha_limite=d(1), fecha_devolucion=d(2))
        # Activos (sin devolver)
        Prestamo.objects.create(ejemplar=c1, estudiante=e3, fecha_prestamo=d(5), fecha_limite=hoy + timedelta(days=9))
        Prestamo.objects.create(ejemplar=c4, estudiante=e2, fecha_prestamo=d(3), fecha_limite=hoy + timedelta(days=11))
        Prestamo.objects.create(ejemplar=c6, estudiante=e1, fecha_prestamo=d(2), fecha_limite=hoy + timedelta(days=12))

        self.stdout.write(self.style.SUCCESS("Datos de prueba cargados."))
