# Sistema de Auditoría — Fintech Lakehouse

> Pipeline de datos para procesamiento, almacenamiento y auditoría histórica exacta de transacciones de pago, cumpliendo con los requisitos regulatorios de una empresa Fintech.

---

## Descripción del Proyecto

Este proyecto implementa un pipeline de datos completo sobre una arquitectura **Lakehouse** para una empresa de tecnología financiera (Fintech) que requiere:

- Inmutabilidad total de los registros de transacciones de pago
- Cumplimiento de transacciones ACID en cada operación de escritura
- Auditorías exactas de datos históricos mediante *time travel*
- Generación de reportes regulatorios fijos con periodicidad mensual

El sistema está diseñado bajo una metodología **Predictiva (Cascada)**, dado que los requisitos son fijos y no evolucionan durante el ciclo de vida del proyecto.

---

## Arquitectura Seleccionada

**Tipo:** Lakehouse (Delta Lake + Capa Medallion)

| Etapa | Tecnología | Rol |
|-------|-----------|-----|
| Ingesta / Almacenamiento Crudo | Delta Lake | Escritura inmutable, ACID, versionado, rollback |
| Procesamiento / Transformación | Capa Medallion (Bronze → Silver → Gold) | Limpieza, validación y curación de datos |
| Servicio / Exposición | Dashboard + Endpoint SQL | Reportería regulatoria desde Capa Gold |

**Flujo de datos:**

```
Fuentes Externas
  └─► [P1] Ingesta y Almacenamiento Crudo
        └─► [D1] Delta Lake — Bronze
              └─► [P2] Validación y Limpieza
                    └─► [D2] Delta Lake — Silver
                          └─► [P3] Transformación y Curación
                                └─► [D3] Delta Lake — Gold
                                      └─► [P4] Exposición y Generación de Reportes
                                            └─► Área de Compliance (Reporte Mensual)
```

---

## Requisitos y Configuración del Entorno Técnico

| Herramienta | Versión mínima | Propósito |
|-------------|---------------|-----------|
| Git | 2.40+ | Control de versiones del proyecto |
| Docker | 24.0+ | Contenerización del entorno de ejecución |
| Python | 3.11+ | Scripts ETL y transformación de datos |
| Apache Spark | 3.5+ | Motor de procesamiento distribuido |
| Delta Lake | 3.0+ | Capa de almacenamiento ACID sobre Parquet |
| PostgreSQL | 15+ | Metastore y control de catálogo de datos |
| Grafana / Metabase | Latest | Dashboard y visualización de reportes regulatorios |

**Variables de entorno requeridas** (crear un archivo `.env` en la raíz):

```env
SPARK_MASTER=local[*]
DELTA_LOG_PATH=/data/delta/_delta_log
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fintech_metastore
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_password
REPORT_OUTPUT_PATH=/data/gold/reports/
```

---

## Instrucciones de Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/org/fintech-lakehouse.git
cd fintech-lakehouse
```

### 2. Levantar el entorno con Docker

```bash
docker-compose up -d
```

> Esto levanta los contenedores de Spark, PostgreSQL y el servicio de Dashboard.

### 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con las credenciales del entorno
```

### 5. Ejecutar pipeline completo (Bronze → Silver → Gold)

```bash
python src/pipeline/run_full_pipeline.py
```

### 6. Generar reporte regulatorio del mes actual

```bash
python src/reporting/generate_monthly_report.py --period 2025-04
```

---

## Estructura del Repositorio

```
fintech-lakehouse/
│
├── src/
│   ├── ingestion/          # Scripts de ingesta hacia Delta Lake (Capa Bronze)
│   │   ├── api_ingestor.py
│   │   └── batch_loader.py
│   ├── pipeline/           # Orquestación Bronze → Silver → Gold
│   │   ├── bronze_to_silver.py
│   │   ├── silver_to_gold.py
│   │   └── run_full_pipeline.py
│   └── reporting/          # Generación de reportes regulatorios mensuales
│       └── generate_monthly_report.py
│
├── data/
│   ├── bronze/             # Datos crudos inmutables (Delta Lake, Parquet)
│   ├── silver/             # Datos validados y estandarizados
│   └── gold/               # Datos curados listos para reportería
│       └── reports/        # Reportes mensuales generados
│
├── docs/
│   ├── arquitectura.md     # Documentación técnica de la arquitectura
│   ├── dfd.png             # Diagrama de Flujo de Datos (DFD)
│   └── diccionario_datos.md
│
├── tests/
│   ├── test_acid.py        # Validación de transacciones ACID
│   └── test_immutability.py
│
├── .env.example            # Plantilla de variables de entorno
├── docker-compose.yml      # Configuración de contenedores
├── requirements.txt        # Dependencias Python
└── README.md               # Este archivo
```

---

## Notas de Auditoría y Cumplimiento

- Todos los datos en la Capa Bronze son **inmutables**. No se realizan operaciones `DELETE` ni `UPDATE` directos; los cambios se registran como nuevas versiones via Delta Lake.
- El acceso a datos históricos se realiza mediante **time travel**: `SELECT * FROM delta.bronze WHERE version = N`.
- Los reportes generados se almacenan en `/data/gold/reports/` con hash SHA-256 para verificar integridad.
- El sistema cumple con los principios ACID: Atomicidad, Consistencia, Aislamiento y Durabilidad en cada transacción.
