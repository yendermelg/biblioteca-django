BEGIN;
--
-- Create model Autor
--
CREATE TABLE "biblioteca_autor" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nombre" varchar(150) NOT NULL);
--
-- Create model Categoria
--
CREATE TABLE "biblioteca_categoria" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nombre" varchar(80) NOT NULL UNIQUE);
--
-- Create model Estudiante
--
CREATE TABLE "biblioteca_estudiante" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "codigo" varchar(20) NOT NULL UNIQUE, "nombre" varchar(150) NOT NULL, "correo" varchar(254) NOT NULL UNIQUE);
--
-- Create model Libro
--
CREATE TABLE "biblioteca_libro" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "titulo" varchar(200) NOT NULL, "anio_publicacion" integer NOT NULL, "isbn" varchar(17) NOT NULL UNIQUE, "categoria_id" bigint NOT NULL REFERENCES "biblioteca_categoria" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "biblioteca_libro_autores" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "libro_id" bigint NOT NULL REFERENCES "biblioteca_libro" ("id") DEFERRABLE INITIALLY DEFERRED, "autor_id" bigint NOT NULL REFERENCES "biblioteca_autor" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Ejemplar
--
CREATE TABLE "biblioteca_ejemplar" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "codigo_inventario" varchar(30) NOT NULL UNIQUE, "condicion" varchar(10) NOT NULL, "libro_id" bigint NOT NULL REFERENCES "biblioteca_libro" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Prestamo
--
CREATE TABLE "biblioteca_prestamo" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "fecha_prestamo" date NOT NULL, "fecha_limite" date NOT NULL, "fecha_devolucion" date NULL, "registrado_en" datetime NOT NULL, "ejemplar_id" bigint NOT NULL REFERENCES "biblioteca_ejemplar" ("id") DEFERRABLE INITIALLY DEFERRED, "estudiante_id" bigint NOT NULL REFERENCES "biblioteca_estudiante" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "fecha_limite_no_anterior_al_prestamo" CHECK ("fecha_limite" >= ("fecha_prestamo")));
CREATE INDEX "biblioteca_libro_categoria_id_a729cd97" ON "biblioteca_libro" ("categoria_id");
CREATE UNIQUE INDEX "biblioteca_libro_autores_libro_id_autor_id_d65051fa_uniq" ON "biblioteca_libro_autores" ("libro_id", "autor_id");
CREATE INDEX "biblioteca_libro_autores_libro_id_65e665c5" ON "biblioteca_libro_autores" ("libro_id");
CREATE INDEX "biblioteca_libro_autores_autor_id_784a4900" ON "biblioteca_libro_autores" ("autor_id");
CREATE INDEX "biblioteca_ejemplar_libro_id_be75ba6c" ON "biblioteca_ejemplar" ("libro_id");
CREATE UNIQUE INDEX "un_prestamo_activo_por_ejemplar" ON "biblioteca_prestamo" ("ejemplar_id") WHERE "fecha_devolucion" IS NULL;
CREATE INDEX "biblioteca_prestamo_ejemplar_id_bb55ff1d" ON "biblioteca_prestamo" ("ejemplar_id");
CREATE INDEX "biblioteca_prestamo_estudiante_id_f583385a" ON "biblioteca_prestamo" ("estudiante_id");
COMMIT;
