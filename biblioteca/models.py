from django.db import models
from django.db.models import Q
from django.utils import timezone


class Autor(models.Model):
    nombre = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = "autores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    anio_publicacion = models.IntegerField("año de publicación")
    isbn = models.CharField("ISBN", max_length=17, unique=True)
    idioma = models.CharField(max_length=30, default="Español")
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="libros"
    )
    autores = models.ManyToManyField(Autor, related_name="libros")

    class Meta:
        ordering = ["titulo"]

    def __str__(self):
        return f"{self.titulo} ({self.anio_publicacion})"


class Ejemplar(models.Model):
    class Condicion(models.TextChoices):
        NUEVO = "nuevo", "Nuevo"
        USADO = "usado", "Usado"
        DANADO = "danado", "Dañado"

    libro = models.ForeignKey(
        Libro, on_delete=models.PROTECT, related_name="ejemplares"
    )
    codigo_inventario = models.CharField(max_length=30, unique=True)
    condicion = models.CharField(
        "condición", max_length=10, choices=Condicion.choices, default=Condicion.NUEVO
    )

    class Meta:
        verbose_name_plural = "ejemplares"
        ordering = ["codigo_inventario"]

    def __str__(self):
        return f"{self.codigo_inventario} · {self.libro.titulo}"


class Estudiante(models.Model):
    codigo = models.CharField("código estudiantil", max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} · {self.nombre}"


class Prestamo(models.Model):
    ejemplar = models.ForeignKey(
        Ejemplar, on_delete=models.PROTECT, related_name="prestamos"
    )
    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.PROTECT, related_name="prestamos"
    )
    fecha_prestamo = models.DateField("fecha de préstamo", default=timezone.localdate)
    fecha_limite = models.DateField("fecha límite de devolución")
    fecha_devolucion = models.DateField(
        "fecha real de devolución", null=True, blank=True
    )
    registrado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "préstamo"
        ordering = ["-fecha_prestamo", "-id"]
        constraints = [
            # Regla de negocio: una copia no puede tener dos préstamos activos
            # (activo = sin fecha de devolución). La base de datos lo hace cumplir.
            models.UniqueConstraint(
                fields=["ejemplar"],
                condition=Q(fecha_devolucion__isnull=True),
                name="un_prestamo_activo_por_ejemplar",
            ),
            models.CheckConstraint(
                condition=Q(fecha_limite__gte=models.F("fecha_prestamo")),
                name="fecha_limite_no_anterior_al_prestamo",
            ),
        ]

    @property
    def devuelto(self):
        return self.fecha_devolucion is not None

    def __str__(self):
        estado = "devuelto" if self.devuelto else "activo"
        return f"{self.ejemplar.codigo_inventario} → {self.estudiante.nombre} ({estado})"
