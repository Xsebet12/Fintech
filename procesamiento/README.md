# Procesamiento

## Función
Esta carpeta contiene la capa de limpieza, normalización y derivación de campos del proyecto fintech.

## Archivo principal
- `transformacion.py`: convierte tipos, estandariza columnas, calcula `amount_signed`, rellena saldos faltantes y genera resúmenes agregados.

## Entradas
- `DataFrame` de la etapa de ingesta.
- Estructura mínima de columnas de transacciones.

## Salidas
- `Fintech` transformado.
- `Resumen_Mensual` con agregados por mes y tipo de transacción.
- `Resumen_Cuentas` con agregados por cuenta.

## Uso
Se ejecuta desde `pipeline.py` antes de la validación. No debería contener lógica de carga ni de persistencia.