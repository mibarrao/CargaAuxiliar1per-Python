# 📊 ETL Ingesta y Consolidación de Presupuesto / Budget Ingestion & Consolidation ETL

🇪🇸 **[ESPAÑOL]**

Este proyecto es un pipeline **ETL (Extracción, Transformación y Carga)** híbrido diseñado para centralizar presupuestos financieros, métricas operacionales y rendiciones contables distribuidas en múltiples archivos independientes de Excel. El sistema normaliza estructuras heterogéneas localmente mediante Python y, tras una ingesta automatizada y segura en SQL Server, orquesta la consolidación de la información en una matriz relacional para análisis avanzado.

### 🚀 Arquitectura y Flujo de Datos
1. **Extracción (Python/Pandas):** - Lectura dinámica de múltiples archivos de Excel independientes.
   - Conectividad nativa a rutas de red compartidas (**Rutas UNC**) abstrayéndose de restricciones de mapeo de discos (`Z:`, `X:`, etc.) y resolviendo dinámicamente codificaciones de caracteres latinos especiales mediante bytes binarios (`chr(193)`).
   - Identificación y extracción automatizada de pestañas específicas (ej. patrones como `4161200010 I UTILIDAD`).
2. **Transformación:** Mapeo seguro de columnas por posición (`.iloc`) para evitar errores de índices, limpieza profunda de filas de totales o encabezados internos, y normalización estandarizada de tipos de datos numéricos (mitigación de strings, celdas vacías o guiones contables `"-"` convirtiéndolos a ceros numéricos enteros reales).
3. **Carga (SQL Server):** Ingesta masiva, directa y atómica (`with engine.begin()`) hacia tablas intermedias con llaves primarias autoincrementales (`ID IDENTITY`). Incorpora optimizaciones de memoria de red mediante `fast_executemany=True` y segmentación por bloques (`chunksize=30000`) para mitigar por completo excepciones de concurrencia o bloqueo de recursos (*Deadlocks*).
4. **Consolidación (T-SQL):** Orquestación y ejecución automatizada de procedimientos almacenados y unpivots desde el script de Python para la actualización de estructuras transitorias y consolidación de matrices finales, auditando de manera síncrona cada hito en la tabla centralizada `dbo.Log_IDG`.

### 🛠️ Tecnologías Utilizadas

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQL Server](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-D71F1F?style=for-the-badge&logo=sqlalchemy&logoColor=white)

* **Lenguaje:** Python 3.12
* **Librerías:** `pandas`, `sqlalchemy (v2.0+)`, `pyodbc`
* **Base de Datos:** SQL Server (On-premise / `LH-GESTIONDOS2`)
* **Conceptos:** Conectividad UNC, Transacciones Atómicas, Mitigación de Deadlocks, Inserción por Bloques (Chunksize), SQL Dinámico.

---

🇬🇧 **[ENGLISH]**

This project is a hybrid **ETL (Extract, Transform, Load)** pipeline designed to centralize financial budgets, operational metrics, and accounting settlements distributed across multiple independent Excel files. The system normalizes heterogeneous data structures locally using Python and, following an automated and secure ingestion into SQL Server, orchestrates data consolidation into a relational matrix for advanced analysis.

### 🚀 Architecture & Data Flow
1. **Extraction (Python/Pandas):** - Dynamic reading of multiple independent Excel files.
   - Native connectivity to shared network paths (**UNC Paths**), bypassing local drive mapping constraints (`Z:`, `X:`, etc.) and dynamically resolving special Latin character encodings using binary bytes (`chr(193)`).
   - Automated identification and extraction of specific target sheets (e.g., patterns like `4161200010 I UTILIDAD`).
2. **Transformation:** Secure column mapping by position (`.iloc`) to prevent index errors, deep cleaning of internal header/total rows, and standardized normalization of numeric data types (handling strings, blanks, or accounting hyphens `"-"` by converting them into true real integers).
3. **Loading (SQL Server):** Massive, direct, and atomic ingestion (`with engine.begin()`) into intermediate staging tables with auto-incremental primary keys (`ID IDENTITY`). Includes network memory optimizations via `fast_executemany=True` and block segmentation (`chunksize=30000`) to completely mitigate concurrency exceptions or resource locking (*Deadlocks*).
4. **Consolidation (T-SQL):** Orchestration and automated execution of stored procedures and unpivots directly from the Python script to update transient structures and consolidate final matrices, synchronously auditing each milestone in the centralized log table `dbo.Log_IDG`.

### 🛠️ Tech Stack & Tools

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQL Server](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-D71F1F?style=for-the-badge&logo=sqlalchemy&logoColor=white)

* **Language:** Python 3.12
* **Libraries:** `pandas`, `sqlalchemy (v2.0+)`, `pyodbc`
* **Database:** SQL Server (On-premise / `LH-GESTIONDOS2`)
* **Concepts:** UNC Connectivity, Atomic Transactions, Deadlock Mitigation, Chunksize Bulk Ingestion, Dynamic SQL.

---

### 📂 Archivos del Proyecto / Project Files

* `BaseIndustrias_CantidadAfiliados.py`, `BaseIndustrias_MontosCreditosConsumo.py`, `BaseIndustrias_tasas.py`, `BaseIndustrias_TotalCreditosConsumo.py`: Script de Python para la lectura iterativa de archivos, limpieza posicional y consolidación local / *Python script for iterative file reading, positional cleansing, and local consolidation*.
* `CargaAporteUnoPython.py`: Script modular para la ingesta y sanitización automática de rendiciones contables, conectividad UNC nativa por bloques y orquestación síncrona de SPs / *Modular script for automated accounting settlement ingestion, native UNC chunked connectivity, and synchronous SP orchestration*.
* `Etl_BaseIndustria_CantidadAfiliado.sql`, `Etl_BaseIndustria_MontosCreditoConsumo`, `Etl_BaseIndustria_TasaCredito.sql`, `Etl_BaseIndustria_TotalCreditoConsumo`: Procedimiento almacenado de consolidación y unpivot ejecutado tras la ingesta manual / *Consolidation and unpivot stored procedure executed after manual ingestion*.
* `Etl_Actualiza_1por_tem.sql`, `Etl_Actualiza_1por.sql`: Procedimientos almacenados para la actualización transitoria y consolidación definitiva del aporte del 1% de pensionados / *Stored procedures for transient updates and definitive consolidation of the 1% pensioner contribution*.
