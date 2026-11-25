from django.contrib import admin, messages
from django.utils import timezone

from .models import Autor, Categoria, Ejemplar, Estudiante, Libro, Prestamo


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


class EjemplarInline(admin.TabularInline):
    model = Ejemplar
    extra = 1


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "anio_publicacion", "isbn", "categoria")
    search_fields = ("titulo", "isbn", "autores__nombre")
    list_filter = ("categoria", "anio_publicacion")
    filter_horizontal = ("autores",)
    inlines = [EjemplarInline]
    list_select_related = ("categoria",)


@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display = ("codigo_inventario", "libro", "condicion")
    search_fields = ("codigo_inventario", "libro__titulo")
    list_filter = ("condicion",)
    list_select_related = ("libro",)


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    # Mini reto: buscar un estudiante por código o por nombre
    list_display = ("codigo", "nombre", "correo")
    search_fields = ("codigo", "nombre")


class EstadoPrestamoFilter(admin.SimpleListFilter):
    title = "estado"
    parameter_name = "estado"

    def lookups(self, request, model_admin):
        return [("activo", "Sin devolver"), ("devuelto", "Devuelto")]

    def queryset(self, request, queryset):
        if self.value() == "activo":
            return queryset.filter(fecha_devolucion__isnull=True)
        if self.value() == "devuelto":
            return queryset.filter(fecha_devolucion__isnull=False)
        return queryset


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    # Mini reto: ver de un vistazo qué préstamos siguen sin devolverse
    list_display = (
        "ejemplar",
        "estudiante",
        "fecha_prestamo",
        "fecha_limite",
        "fecha_devolucion",
        "esta_devuelto",
    )
    list_filter = (EstadoPrestamoFilter, "fecha_prestamo")
    search_fields = (
        "estudiante__codigo",
        "estudiante__nombre",
        "ejemplar__codigo_inventario",
        "ejemplar__libro__titulo",
    )
    # Mini reto: elegir copias sin confundirse (se busca por código o título)
    autocomplete_fields = ("ejemplar", "estudiante")
    readonly_fields = ("registrado_en",)
    list_select_related = ("ejemplar__libro", "estudiante")
    actions = ["marcar_devueltos"]

    @admin.display(boolean=True, description="Devuelto")
    def esta_devuelto(self, obj):
        return obj.devuelto

    @admin.action(description="Marcar préstamos seleccionados como devueltos (hoy)")
    def marcar_devueltos(self, request, queryset):
        n = queryset.filter(fecha_devolucion__isnull=True).update(
            fecha_devolucion=timezone.localdate()
        )
        self.message_user(
            request, f"{n} préstamo(s) marcados como devueltos.", messages.SUCCESS
        )
