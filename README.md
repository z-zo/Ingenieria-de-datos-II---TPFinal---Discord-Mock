# Discord Architecture Clone: Implementación de Persistencia Políglota

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![ScyllaDB](https://img.shields.io/badge/ScyllaDB-59B287?style=for-the-badge&logo=scylladb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Este proyecto es una Prueba de Concepto (PoC) diseñada para demostrar la aplicación práctica de la **Persistencia Políglota** en sistemas distribuidos. Simula la arquitectura subyacente de plataformas de mensajería masiva como Discord, resolviendo el problema de manejar dos cargas de trabajo (workloads) diametralmente opuestas a través de motores de bases de datos especializados.

## 🏗️ Arquitectura y Decisiones de Diseño

El sistema está dividido en dos grandes dominios, alineados con el Teorema CAP y los paradigmas ACID/BASE:

### 1. Control Plane (Motor Relacional - PostgreSQL)
Encargado de la **Seguridad, Control de Acceso y Gestión de Entidades**. 
* **Paradigma:** ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad).
* **Justificación:** Las relaciones entre Usuarios, Servidores, Canales y Roles requieren **Consistencia Fuerte**. Cuando un usuario intenta enviar un mensaje, la API realiza una validación síncrona (bloqueante) usando `psycopg2` para garantizar transaccionalmente que el usuario posee los permisos adecuados (`SEND_MESSAGES`).
* **Auto-Inicialización:** La base de datos nace poblada utilizando un script de inyección en el _entrypoint_ de Docker.

### 2. Data Plane (Motor NoSQL Wide-Column - ScyllaDB)
Encargado de la **Ingesta Masiva y Almacenamiento de Historial**.
* **Paradigma:** BASE (Basically Available, Soft state, Eventual consistency).
* **Justificación:** El historial de chat es inmutable, secuencial y requiere alta disponibilidad (AP en el Teorema CAP) con un Throughput masivo. 
* **Modelado Orientado a Consultas:** La tabla `messages` utiliza una Clave de Partición compuesta (`channel_id` + `bucket` temporal) para evitar el _Scatter-Gather_ en la red, y un `TIMEUUID` como Clave de Agrupamiento para garantizar el ordenamiento cronológico natural en disco.
* **Inyección Asincrónica:** Se utiliza el driver oficial de DataStax (`cassandra-driver`) con `execute_async()` (Fire-and-Forget) para delegar la carga de I/O a la red, evitando bloqueos en la capa del orquestador.

## 📂 Estructura del Proyecto

```text
/
├── docker-compose.yml       # Orquestación de infraestructura
├── estructura_relacional.sql   # DDL e inyección de datos semilla (PostgreSQL)
├── esquema_nosql.cql        # DDL orientado a consultas (ScyllaDB)
├── orquestador.py           # API Híbrida: Validación ACID -> Inyección BASE
├── inyeccion_asyncronica.py          # Script de estrés para inyección asincrónica masiva
├── .gitignore               # Exclusiones de Git
└── README.md                # Documentación técnica
