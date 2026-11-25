from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .models import Autor, Categoria, Ejemplar, Estudiante, Libro, Prestamo


class ReglaCopiaPrestadaTests(TestCase):
    def setUp(self):
        cat = Categoria.objects.create(nombre="Novela")
        libro = Libro.objects.create(titulo="X", anio_publicacion=2000, isbn="1", categoria=cat)
        self.copia = Ejemplar.objects.create(libro=libro, codigo_inventario="INV-1")
        self.e1 = Estudiante.objects.create(codigo="1", nombre="A", correo="a@x.co")
        self.e2 = Estudiante.objects.create(codigo="2", nombre="B", correo="b@x.co")
        self.hoy = timezone.localdate()
        self.limite = self.hoy + timedelta(days=14)

    def test_no_se_puede_prestar_dos_veces_la_misma_copia(self):
        Prestamo.objects.create(ejemplar=self.copia, estudiante=self.e1, fecha_limite=self.limite)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Prestamo.objects.create(ejemplar=self.copia, estudiante=self.e2, fecha_limite=self.limite)

    def test_se_puede_volver_a_prestar_despues_de_devolver(self):
        p = Prestamo.objects.create(ejemplar=self.copia, estudiante=self.e1, fecha_limite=self.limite)
        p.fecha_devolucion = self.hoy
        p.save()
        Prestamo.objects.create(ejemplar=self.copia, estudiante=self.e2, fecha_limite=self.limite)
        self.assertEqual(Prestamo.objects.filter(ejemplar=self.copia).count(), 2)

    def test_fecha_limite_no_puede_ser_anterior(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Prestamo.objects.create(ejemplar=self.copia, estudiante=self.e1,
                                    fecha_limite=self.hoy - timedelta(days=1))
