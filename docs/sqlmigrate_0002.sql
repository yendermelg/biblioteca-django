BEGIN;
--
-- Add field idioma to libro
--
CREATE TABLE "new__biblioteca_libro" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "idioma" varchar(30) NOT NULL, "titulo" varchar(200) NOT NULL, "anio_publicacion" integer NOT NULL, "isbn" varchar(17) NOT NULL UNIQUE, "categoria_id" bigint NOT NULL REFERENCES "biblioteca_categoria" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__biblioteca_libro" ("id", "titulo", "anio_publicacion", "isbn", "categoria_id", "idioma") SELECT "id", "titulo", "anio_publicacion", "isbn", "categoria_id", 'Español' FROM "biblioteca_libro";
DROP TABLE "biblioteca_libro";
ALTER TABLE "new__biblioteca_libro" RENAME TO "biblioteca_libro";
CREATE INDEX "biblioteca_libro_categoria_id_a729cd97" ON "biblioteca_libro" ("categoria_id");
COMMIT;
