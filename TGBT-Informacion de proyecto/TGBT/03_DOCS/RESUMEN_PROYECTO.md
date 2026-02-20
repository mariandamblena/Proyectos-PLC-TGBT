# RESUMEN DEL PROYECTO — SCMTA TGBT

> **Versión:** 1.0  
> **Fecha:** 2026-02-20  
> **CPU:** Siemens S7-1215C DC/DC/Rly  
> **IDE:** TIA Portal V18  
> **Lenguaje:** SCL (Structured Control Language)

---

## 1. ¿Qué es el proyecto SCMTA?

**SCMTA** = Sistema de Conmutación y Monitoreo de Tablero de distribución principal de baja tensión (TGBT).

El PLC gestiona automáticamente la **transferencia de alimentación** entre la red eléctrica pública y dos grupos electrógenos (GD1 y GD2), además de controlar el **deslastre/reenganche** de cargas (feeders) y la **señalización** del tablero.

---

## 2. Qué hacía ANTES (V1.0 → V2.0)

La versión original del código tenía las siguientes características:

### Alcance V1.0/V2.0
- **18 feeders** (arrays `[1..18]`)
- Solo GD1 (sin redundancia GD2)
- Máquina de estados SCMTA con **15 estados**
- Sin soporte para feeders tipo a/b
- Señales ficticias que no existían en hardware:
  - `DO_PILOT_QT1_LOCAL`, `QG1_LOCAL`, `QG2_LOCAL` → no hay pilotos LOCAL físicos
  - `DO_PILOT_TRANSFER` → no hay LED de transferencia en tablero
  - `DO_ALARM_HORN` → no hay bocina ni sirena
  - `DI_FEEDER_REMOTE_SEL[1..18]` → no hay selectores Remoto/Local en feeders
- Variables innecesarias: `FEEDER_REMOTE_ALLOWED`, `FEEDER_LOCAL_MODE`, `HMI_FEEDER_LOCAL`, `ENABLE_HORN`
- La señalización de interruptores solo tenía: OPEN, CLOSED, LOCAL (3 pilotos)
- Sin indicación de falla (FAULT) ni carga de resorte (CHARGING) para QT1/QG1/QG2
- Sin pilotos físicos para feeders

### Problemas V1.0/V2.0
1. Cantidad de feeders errónea (18 vs 19 reales con Modbus)
2. Señales de hardware ficticias → error al compilar o DO sin efecto
3. Faltaban pilotos de FAULT y CHARGING para interruptores fuente
4. Faltaban los 57 pilotos DO de feeders (19 × 3)
5. Lógica de FEEDER_REMOTE_ALLOWED bloqueaba comandos innecesariamente

---

## 3. Qué hace AHORA (V3.0)

### 3.1 Máquina de Estados SCMTA — 21 estados

El corazón del sistema. Gestiona la transferencia automática entre fuentes:

| Rango | Grupo | Estados |
|-------|-------|---------|
| 0 | Inicio | INIT |
| 1-4 | RED | ON_GRID, GRID_FAIL_DETECT, GRID_FAIL_CONFIRMED, WAIT_GD_READY |
| 5-9 | Transferencia a GD | START_GD, GD_RUNNING_WAIT, OPEN_QT1, CLOSE_QG1, ON_GD |
| 10-14 | Retorno a RED | GRID_STABLE_DETECT, GRID_STABLE_CONFIRMED, OPEN_QG1, CLOSE_QT1, RETURN_TO_GRID |
| 15-20 | GD2 (failover) | GD1_FAIL_DETECT, OPEN_QG1_FOR_GD2, START_GD2, CLOSE_QG2, ON_GD2, GD2_RETURN |

### 3.2 Deslastre y Reenganche (FB_SHED V2.0)

Cuando opera en grupo electrógeno, si la carga supera umbrales configurables, el sistema desconecta feeders no esenciales automáticamente. Cuando la carga baja, los reconecta.

- **19 feeders** gestionados (`[1..19]`)
- Orden de deslastre y reenganche configurable por parámetros
- Clasificación esencial/no-esencial por feeder
- 6 modos de operación (Normal, SHED_STAGE_1..4, RECONNECT, FAULT)

### 3.3 Señalización (FB_OUTPUTS V3.0)

**Pilotos sistema (4 DO):**
| Piloto | Color | Señal |
|--------|-------|-------|
| EN RED | Verde | DO_PILOT_ON_GRID |
| EN GRUPO | Amarillo | DO_PILOT_ON_GD |
| FALLA | Rojo | DO_PILOT_FAULT |
| DESLASTRE | Amarillo | DO_PILOT_SHED |

**Pilotos interruptores fuente (4 DO × 3 = 12 DO):**
| Piloto | Color | Fuente Modbus |
|--------|-------|---------------|
| OPEN (abierto) | Verde | Registro 32001 Bit 0 (OF) |
| CLOSED (cerrado) | Rojo | Registro 32001 Bit 0 (OF) |
| FAULT (falla) | Ámbar | Registro 32001 Bit 1 (SD) = TRIPPED |
| CHARGING (resorte) | Blanco | Registro 32001 Bit 5 (PF) = READY |

**Pilotos feeders (3 DO × 19 = 57 DO):**
| Piloto | Color | Condición |
|--------|-------|-----------|
| FAULT | Ámbar | TRIPPED OR ALARM |
| CLOSED | Rojo | STATE = 1 |
| OPEN | Verde | STATE = 0 |

**Alarma (1 DO):**
- Baliza roja parpadeante

### 3.4 Arbitración de Comandos (FB_CMD_ARBITER)

Prioriza y valida todos los comandos de apertura/cierre:
1. **Prioridad 0:** Protección por enclavamiento (bloquea maniobras peligrosas)
2. **Prioridad 1:** Deslastre automático (FB_SHED)
3. **Prioridad 2:** SCMTA automático (transferencia)
4. **Prioridad 3:** Comandos manuales (pulsadores y HMI)

### 3.5 Comunicación Modbus RTU

- 22 dispositivos en bus RS-485
- 3 MasterPact MTZ (QT1, QG1, QG2) — lectura estado + comandos
- 19 feeders NSX — lectura estado + comandos
- Time-slicing: 1 dispositivo por ciclo de polling
- Prioridad: escrituras (comandos) > lecturas (estado)

### 3.6 Normalización I/O (FB_IO_NORMALIZE)

- Convertir señales físicas DI (selectores, pulsadores, contactos GD) a señales lógicas
- Debounce 50ms en pulsadores
- Detección de flancos → pulsos de 1 scan para comandos manuales
- Fail-safe: si selector AUTO indefinido → modo MANUAL

---

## 4. Arquitectura de Bloques

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   OB1_MAIN   │────▶│  DATA_BUFF   │◀───▶│   DB_PARAMS  │
│ (orquestador)│     │  (DB global) │     │  (config)    │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ├── Network 1: FB_IO_NORMALIZE    (DI → señales lógicas)
       ├── Network 2: FB_SCMTA           (máquina de estados 21 estados)
       ├── Network 3: FB_SHED            (deslastre/reenganche)
       ├── Network 4: FB_CMD_ARBITER     (priorización comandos)
       ├── Network 5: FB_OUTPUTS         (DO pilotos + HMI)
       ├── Network 6: FB_MTZ_DRIVER ×3   (Modbus QT1/QG1/QG2)
       └── Network 7: Cálculos aux       (LoadPct, Uptime)
```

**Patrón:** Arquitectura Blackboard — todos los FBs leen/escriben en DATA_BUFF (DB23).

---

## 5. Archivos del Proyecto

### 5.1 Código SCL (01_SCL/)

| Archivo | Bloque | Versión | Función |
|---------|--------|---------|---------|
| 01_FB_IO_NORMALIZE.scl | FB | 2.0 | Normalización DI → señales lógicas |
| 02_FB_SCMTA.scl | FB | 3.0 | Máquina de estados transferencia (21 estados) |
| 03_FB_SHED.scl | FB | 2.0 | Deslastre y reenganche de cargas |
| 04_FB_CMD_ARBITER.scl | FB | 2.0 | Arbitración y priorización de comandos |
| 05_FB_OUTPUTS.scl | FB | 3.0 | Salidas físicas (pilotos, alarmas) + HMI |
| 06_FB_MODBUS_MANAGER.scl | FB | 0.1 | Scheduler comunicación Modbus RTU |
| 07_FB_MTZ_DRIVER.scl | FB | 1.1 | Driver Modbus para MasterPact MTZ |
| 08_DB_GLOBAL_STATUS.scl | DB | 3.0 | DATA_BUFF — DB global compartido |
| 09_DB_PARAMS.scl | DB | 3.0 | Parámetros configurables (RETAIN) |
| 10_OB1_MAIN.scl | OB | 3.0 | Programa principal — orquestador |

### 5.2 Documentación (03_DOCS/)

| Archivo | Contenido |
|---------|-----------|
| RESUMEN_PROYECTO.md | **Este archivo** — resumen antes/ahora |
| LISTADO_EQUIPOS.md | 39 equipos del tablero (3 ACB + 36 feeders) |
| LISTADO_IO.md | Mapeo completo DI/DO/Modbus/HMI |
| README_SCMTA.md | Documentación técnica master (~30 páginas) |
| ARQUITECTURA_DESLASTRE_V2.md | Diseño detallado SHED V2.0 |
| CAMBIOS_REQ_2_SEGUNDOS.md | REQ Modbus activo 2s (requisito hardware) |
| INSTRUCCIONES_CORRECCION_OB1.md | Renombrado DB → DATA_BUFF + instancias |
| GUIA_COMPLETA_SCL_LADDER.md | Comparativa SCL vs LADDER |
| INTRODUCCION_TECNICA_INGENIERO.md | Guía onboarding para ingeniero nuevo |
| VALIDACION_SCL_TIA_V18.md | Validación compatibilidad TIA V18 |
| INDEX.md | Índice maestro de todos los archivos |

### 5.3 Diagramas UML (04_UML/)

| Archivo | Contenido |
|---------|-----------|
| 11_UML_SCMTA_StateMachine.puml | Máquina estados SCMTA |
| 12_UML_MTZ_Driver_StateMachine.puml | Máquina estados driver MTZ |
| 13_UML_SHED_Activity.puml | Diagrama actividad deslastre |
| 14_UML_SCMTA_GD2_StateMachine.puml | Estados failover GD2 |
| 15_UML_System_Architecture.puml | Arquitectura general sistema |

### 5.4 Manuales Referencia (05_MANUALES/)

| Archivo | Contenido |
|---------|-----------|
| MTZ MANUAL.pdf | Manual MasterPact MTZ — Modbus |
| Escritura_MTZ.pdf | Procedimiento escritura/comando MTZ |
| masterpact mtz1 y mtz2.pdf | Catálogo MasterPact |
| NSX MANUAL.pdf | Manual NSX (feeders) — Modbus |
| s71200_system_manual_en-US_en-US.pdf | Manual CPU S7-1200 |
| MTZ_MODBUS_CHARGING_REGISTERS.md | Extracto registros Modbus MTZ |

### 5.5 Configuración (06_CONFIG/)

| Archivo | Contenido |
|---------|-----------|
| TGBT_Config - listado de equipos.pdf | Listado equipos original del proyecto |
| TGBT_Config - listado de entradas y salidas.pdf | Listado I/O original |
| TGBT_Config - pm5330.pdf | Config medidor PM5330 |
| ET MONTAJE-TGBT.pdf | Esquema montaje eléctrico |

---

## 6. Cambios V2.0 → V3.0 (resumen)

| Aspecto | V2.0 | V3.0 |
|---------|------|------|
| Feeders Modbus | 18 | **19** |
| Estados SCMTA | 15 | **21** (+ GD2 failover) |
| Pilotos QT1/QG1/QG2 | 3 (Open, Closed, Local) | **4** (Open, Closed, Fault, Charging) |
| Pilotos feeders | 0 (solo HMI) | **57** (19 × 3 DO físicas) |
| Pilotos sistema | 5 (incl. Transfer, Horn) | **4** (ON_GRID, ON_GD, FAULT, SHED) |
| DI_FEEDER_REMOTE_SEL | Existía (ficticia) | **Eliminada** |
| FEEDER_LOCAL_MODE | Existía | **Eliminada** |
| ENABLE_HORN | Existía | **Eliminada** |
| Feeders tipo a vs b | Sin distinción | **Diferenciados** (5 tipo a con pulsadores) |
| Indicación FAULT | No existía | **Implementada** (Modbus Bit 1 SD) |
| Indicación CHARGING | No existía | **Implementada** (Modbus Bit 5 PF) |

---

## 7. Pendientes (TODO)

| # | Tarea | Prioridad | Descripción |
|---|-------|-----------|-------------|
| 1 | Mapeo %Q feeders | Alta | Asignar 57 DO a módulos de expansión reales |
| 2 | Mapeo %I feeders | Alta | Asignar 10 DI pulsadores tipo a |
| 3 | FB_MODBUS_MANAGER | Media | Completar scheduler con drivers NSX |
| 4 | Power Selector QT1 | Baja | DI 3 posiciones (0-1-2) — pospuesto |
| 5 | FB_MTZ_DRIVER para NSX | Media | Adaptar driver MTZ o crear driver NSX |
| 6 | Pruebas integración | Alta | Ejecutar tests en hardware real |
| 7 | Configuración HMI | Media | Pantallas, tags, alarmas |
| 8 | Actualizar tests | Baja | TEST_FB_SHED y otros usan [1..18] |
