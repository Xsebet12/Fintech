# Data Quality

## Función
Esta carpeta agrupa las validaciones de calidad, consistencia y reglas de negocio del flujo fintech.

## Archivo principal
- `validacion.py`: evalúa montos, estados, saldos, mes de reporte, hashes y unicidad del identificador.

## Entradas
- `Fintech` transformado.
- Configuración opcional de tolerancias y reglas de validación.

## Salidas
- `Fintech Validos`
- `Fintech Invalidos`
- Columnas de control como `registro_valido` y `observaciones`

## Uso
Esta etapa separa los registros correctos de los que deben revisarse. Es la base para calcular KPIs y para la carga posterior a archivos o base de datos.