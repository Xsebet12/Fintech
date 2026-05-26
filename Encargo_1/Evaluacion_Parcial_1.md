# Evaluación Parcial N°1 - ITY1101 Gestión de Datos para IA

**Caso de Estudio 1: Sistema de Auditoría para una Fintech**
* **Asignatura:** Gestión De Datos Para IA 002D
* **Profesor:** Hector Andres Morel Briones
* **Fecha:** 12 abr 2026
* **Integrantes:** Sebastian Cornejo, Jaime Alvarez y Lucas Fuentes

## 1. Selección y Justificación de la Arquitectura

### Introducción al caso y su problemática
En este proyecto abordamos el desafío de construir un sistema de auditoría para una Fintech, enfocado en procesar y almacenar transacciones de pago. Al ser un sector altamente regulado, el sistema debe garantizar que los registros jamás se alteren, operar con transacciones ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad) y permitir consultas del historial exacto en cualquier momento. Esto asegura la generación mensual de los reportes regulatorios sin margen de error.

### Arquitectura Seleccionada: Lakehouse
Se seleccionó la arquitectura Lakehouse porque satisface los requisitos críticos de inmutabilidad total de registros, cumplimiento de transacciones ACID y soporte para auditorías exactas de datos históricos.
* **Escalabilidad:** Separa el cómputo del almacenamiento, permitiendo escalar cada dimensión de forma independiente para absorber grandes volúmenes de transacciones. Almacena datos en formatos abiertos (Parquet).
* **Seguridad:** La implementación de Delta Lake garantiza transacciones ACID y el versionado asegura la inmutabilidad lógica de los registros.
* **Interoperabilidad:** Permite que herramientas SQL estándar accedan directamente a los metadatos y versiones históricas (time travel). Evita la complejidad de una arquitectura Lambda o Pipeline Híbrido.

## 2. Componentes Tecnológicos Clave

| Etapa | Tecnología | Justificación |
| :--- | :--- | :--- |
| Ingesta / Almacenamiento Crudo | Delta Lake | Capa open-source que añade transacciones ACID, control de versiones (time travel), rollback y soporte para Parquet/CSV/JSON. Garantiza la inmutabilidad exigida. |
| Procesamiento / Transformación | Capa Medallion (Bronze → Silver → Gold) | Organiza los datos en calidad: Bronze almacena crudos; Silver limpia; Gold entrega datos curados para reportería. |
| Servicio / Exposición de Datos | Dashboard con Endpoint SQL | Expone exclusivamente los datos validados de la Capa Gold mediante SQL, centralizando KPIs. |

## 3. Plan de Gestión y Seguimiento del Proyecto

### Metodología Seleccionada: Predictiva (Cascada)
Se seleccionó por tener requisitos definidos y estáticos sin necesidad de iterar sobre nuevas funcionalidades. Permite validar rigurosamente cada fase de seguridad e inmutabilidad antes de avanzar.

### Estructura de Desglose del Trabajo (WBS/EDT)

| Fase (id) | Elemento | Tipo | Fecha Inicio | Fecha Término | Nivel |
| :--- | :--- | :--- | :--- | :--- | :--- |
| | Sistema de Auditoria Fintech | WBS | 10/04/2026 | | 0 |
| 1 | Gestión del Proyecto | WBS | 10/04/2026 | 13/04/2026 | 1 |
| 1-1 | Informe de encargo (Evaluación Parcial 1) | Entregable | 10/04/2026 | 13/04/2026 | 2 |
| 1-1-1 | README.md inicial del repositorio | Entregable | 10/04/2026 | 12/04/2026 | 3 |
| 1-2 | Hito 1: Plan de Trabajo Aprobado | Hito | | | 2 |
| 2 | Diseño de Arquitectura Lakehouse | WBS | | | 1 |
| 2-1 | Diseño de Capa Bronze | Entregable | | | 2 |
| 2-2 | Diseño de Capa Silver | Entregable | | | 2 |
| 2-3 | Diseño de Capa Gold | Entregable | | | 2 |
| 2-4 | Documento de diseño técnico y Capas Medallion | Entregable | | | 2 |
| 2-5 | Hito 2: Arquitectura y Cumplimiento Aprobado | Hito | | | 2 |
| 3 | Ingeniería e Implementación de Datos | WBS | | | 1 |
| 3-1 | Configuración de entorno Delta Lake (ACID) | Entregable | | | 2 |
| 3-2 | Script de Ingesta y almacenamiento Bronze | Entregable | | | 2 |
| 3-3 | Script de transformación y validación Silver | Entregable | | | 2 |
| 3-4 | Carga de datos curados en Capa Gold para IA | Entregable | | | 2 |
| 3-5 | Hito 3: Capa Inmutable Operacional (Staging) | Hito | | | 2 |
| 4 | Servicio y Entrega de Reportes | WBS | | | 1 |
| 4-1 | README.md actualizado final | Entregable | | | 2 |
| 4-2 | Informe de Auditoria y Documento Consolidado | Entregable | | | 2 |
| 4-3 | Hito 4: Entrega final completa | Hito | | | 2 |

## 4. Diseño del Flujo de Datos y Estructuras

* **DFD Nivel 0 (Contexto):** Muestra las 4 entidades externas: Fuentes de Pago, Pasarela/API Externa, Área de Compliance y el Ente Regulador interactuando con el Sistema de Auditoría Fintech.
* **DFD Nivel 1 (Descomposición):** Expande el proceso en 6 subprocesos: Recepción y Validación, Ingesta Cruda, Limpieza, Transformación (Medallion: Bronze/Silver/Gold), Generación de Reportes y Exposición.
* **DFD Nivel 2 (Ingesta P2):** Descompone la ingesta mostrando validación, manejo de errores a una *Dead Letter Queue*, y registros en log de Delta.

### Diccionario de Datos Clave

| Entidad | Atributo | Tipo de Dato | Restricciones |
| :--- | :--- | :--- | :--- |
| **Transacción** | `transaction_id` | VARCHAR(36) | PK, NOT NULL, UNIQUE |
| | `amount` | DECIMAL(18,2) | NOT NULL, > 0 |
| | `timestamp_utc` | TIMESTAMP | NOT NULL, Inmutable |
| | `status` | ENUM | NOT NULL |
| **Cuenta** | `account_id` | VARCHAR(36) | PK, NOT NULL |
| | `account_type` | ENUM | NOT NULL |
| | `owner_name` | VARCHAR(120) | NOT NULL |
| **Reporte Regulatorio** | `report_id` | VARCHAR(36) | PK, NOT NULL |
| | `period_month` | DATE | NOT NULL |
| | `generated_at` | TIMESTAMP | NOT NULL |
| **Auditoría** | `audit_id` | VARCHAR(36) | PK, NOT NULL |
| | `event_type` | ENUM | NOT NULL |
| | `delta_version` | BIGINT | NOT NULL |

## 5. Conclusiones
Este proyecto establece una base sólida y transparente para la gestión de datos en la Fintech, priorizando la integridad y el cumplimiento normativo mediante una arquitectura Lakehouse. Al implementar un pipeline basado en la Capa Medallion y tecnología Delta Lake, se transforman datos crudos en reportes precisos, eliminando márgenes de error. La metodología predictiva asegura que cada fase de seguridad se valide rigurosamente, entregando una solución escalable.