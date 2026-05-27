# Reporting

## Función
Esta carpeta genera indicadores de monitoreo del flujo fintech.

## Archivo principal
- `kpi.py`: calcula métricas globales sobre el total de registros, válidos, inválidos, montos, saldos y cuentas.

## Entradas
- Diccionario `almacen_datos` con `Fintech`, `Fintech Validos` y `Fintech Invalidos`.

## Salidas
- `DataFrame` con KPIs listos para guardar en CSV o cargar en base de datos.

## Uso
Se ejecuta después de la validación. Sus resultados alimentan tanto la demo como la carga final.