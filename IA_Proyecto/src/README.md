# src

## Función
Esta carpeta contiene utilidades internas compartidas por distintas etapas del proyecto.

## Archivo principal
- `audit_utils.py`: funciones para crear directorios, generar hashes, guardar versiones y manejar metadatos.

## Uso
Estas utilidades son consumidas por la ingesta, la persistencia y cualquier otra parte del proyecto que necesite trazabilidad o versionado.

## Regla de diseño
La lógica de negocio no debe vivir aquí. Esta carpeta debe permanecer como soporte técnico reutilizable.