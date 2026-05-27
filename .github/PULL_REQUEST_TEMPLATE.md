<!-- Plantilla de Pull Request: use para describir cambios y advertir sobre stubs de prueba -->
# Título
Breve resumen de los cambios (máx. 72 caracteres)

# Descripción
Describe claramente qué cambia y por qué.

# Cambios realizados
- Archivo(s) modificados: lista corta
- Resumen funcional de los cambios

# Checklist
- [ ] Pruebas unitarias locales pasan
- [ ] Linter / formateador aplicado
- [ ] Documentación actualizada si aplica

# Advertencia importante sobre stubs de prueba
Este PR incluye stubs de prueba local ubicados en `archivos_test/` (por ejemplo `leer_batch.py`, `fuente_realtime.py`).

- Estos stubs solo deben mantenerse en ramas de pruebas y NUNCA fusionarse a `main` sin revisión explícita.
- Antes de fusionar a `main`, reemplaza o elimina los stubs y asegúrate de que las implementaciones reales de `ingestion/*` existan y pasen las pruebas de integración.

Si este PR es sólo para compartir ayuda local o demostraciones, marca claramente el PR como `WIP` o incluye `test` en el título.

# Cómo probar (local)
```bash
git checkout -b feat/mi-rama
git add .
git commit -m "Describe cambios"
python3 -m pip install -r requirements.txt
python3 pipeline.py --sources csv,batch,realtime
```
