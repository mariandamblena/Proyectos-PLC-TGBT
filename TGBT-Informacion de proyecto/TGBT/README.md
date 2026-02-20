# PROYECTO SCMTA — TGBT

> **Versión:** 3.0  
> **Fecha:** 2026-02-20  
> **CPU:** Siemens S7-1215C DC/DC/Rly  
> **IDE:** TIA Portal V18  
> **Lenguaje:** SCL (Structured Control Language)

---

## Descripción

**SCMTA** = Sistema de Conmutación y Monitoreo de Tablero General de Baja Tensión.

El PLC controla la **transferencia automática** entre red eléctrica (QT1) y dos grupos electrógenos (QG1/QG2), gestiona **deslastre/reenganche** de 19 feeders con Modbus, y maneja toda la **señalización** física (pilotos LED) y HMI del tablero.

---

## Estructura del Proyecto

```
TGBT/
├── 01_SCL/                          ← Código fuente SCL (10 archivos)
│   ├── 01_FB_IO_NORMALIZE.scl       → Normalización DI (selectores, pulsadores, GD)
│   ├── 02_FB_SCMTA.scl              → Máquina de estados transferencia (21 estados)
│   ├── 03_FB_SHED.scl               → Deslastre y reenganche (19 feeders, 6 modos)
│   ├── 04_FB_CMD_ARBITER.scl        → Arbitración comandos + enclavamiento
│   ├── 05_FB_OUTPUTS.scl            → Pilotos LED + alarmas + señales HMI
│   ├── 06_FB_MODBUS_MANAGER.scl     → Scheduler comunicación Modbus RTU
│   ├── 07_FB_MTZ_DRIVER.scl         → Driver Modbus MasterPact MTZ
│   ├── 08_DB_GLOBAL_STATUS.scl      → DATA_BUFF — DB global compartido
│   ├── 09_DB_PARAMS.scl             → Parámetros configurables (RETAIN)
│   └── 10_OB1_MAIN.scl              → OB1 Main — orquestador (7 networks)
│
├── 02_LADDER/                       ← Conversiones LADDER (referencia)
│
├── 03_DOCS/                         ← Documentación técnica
│   ├── RESUMEN_PROYECTO.md           → Resumen antes/ahora + qué se controla
│   ├── LISTADO_EQUIPOS.md            → 39 equipos (3 ACB + 36 feeders)
│   ├── LISTADO_IO.md                 → Mapeo completo DI/DO/Modbus/HMI
│   ├── INDEX.md                      → Índice maestro de archivos
│   ├── README_SCMTA.md               → Documentación técnica master (~30 pág)
│   ├── ARQUITECTURA_DESLASTRE_V2.md  → Diseño SHED V2.0 (6 modos)
│   ├── CAMBIOS_REQ_2_SEGUNDOS.md     → REQ Modbus 2s (requisito hardware)
│   ├── INSTRUCCIONES_CORRECCION_OB1.md → Renombrado DB → DATA_BUFF
│   ├── GUIA_COMPLETA_SCL_LADDER.md   → SCL vs LADDER + recomendaciones
│   ├── INTRODUCCION_TECNICA_INGENIERO.md → Guía onboarding ingeniero
│   └── VALIDACION_SCL_TIA_V18.md     → Validación compatibilidad TIA V18
│
├── 04_UML/                          ← Diagramas PlantUML (5 diagramas)
│   ├── 11_UML_SCMTA_StateMachine.puml
│   ├── 12_UML_MTZ_Driver_StateMachine.puml
│   ├── 13_UML_SHED_Activity.puml
│   ├── 14_UML_SCMTA_GD2_StateMachine.puml
│   ├── 15_UML_System_Architecture.puml
│   └── README_UML.md
│
├── 05_MANUALES/                     ← Manuales de referencia
│   ├── MTZ MANUAL.pdf                → Manual MasterPact MTZ Modbus
│   ├── Escritura_MTZ.pdf             → Procedimiento escritura MTZ
│   ├── NSX MANUAL.pdf                → Manual Compact NSX Modbus
│   ├── masterpact mtz1 y mtz2.pdf    → Catálogo MasterPact
│   ├── MTZ_MODBUS_CHARGING_REGISTERS.md → Extracto registros Modbus
│   ├── s71200_system_manual_en-US_en-US.pdf
│   ├── s7_1500_compare_table_en_mnemo.pdf
│   └── 81318674_Programming_guideline_DOC_v16_en.pdf
│
├── 06_CONFIG/                       ← Config y documentos de proyecto
│   ├── TGBT_Config - listado de equipos.pdf
│   ├── TGBT_Config - listado de entradas y salidas.pdf
│   ├── TGBT_Config - pm5330.pdf
│   └── ET MONTAJE-TGBT.pdf
│
└── 07_TEST/                         ← Tests automatizados SCL
    ├── TEST_FB_IO_NORMALIZE_SCMTA.scl
    ├── TEST_FB_FALLAS_SCMTA.scl
    ├── TEST_FB_SHED.scl
    ├── TEST_FB_GD2_FAILOVER.scl
    ├── README_TEST.md
    └── README_TEST_FALLAS.md
```

---

## Hardware del Tablero

| Componente | Modelo | Cant. | Comunicación |
|------------|--------|-------|-------------|
| PLC | Siemens S7-1215C DC/DC/Rly | 1 | — |
| Interruptores fuente (ACB) | Schneider MasterPact MTZ | 3 | Modbus RTU |
| Feeders con Modbus | Schneider NSX Micrologic | 19 | Modbus RTU |
| Feeders sin Modbus | Schneider NSX | 17 | — |
| Medidor RED | Schneider PM5330/5350 | 1 | Modbus RTU |
| Módulo RS-485 | Siemens CM 1241 | 1 | Modbus Master |

**Total dispositivos Modbus:** 22 (3 ACB + 19 feeders) + PM5330

Ver detalle completo en [03_DOCS/LISTADO_EQUIPOS.md](03_DOCS/LISTADO_EQUIPOS.md)

---

## Funcionalidades

| Función | Estado | Descripción |
|---------|--------|-------------|
| Transferencia automática | ✅ | 21 estados, failover GD1↔GD2 |
| Deslastre de cargas | ✅ | 19 feeders, 6 modos, esencial/no-esencial |
| Señalización interruptores | ✅ | 4 pilotos × 3 ACB (Open, Closed, Fault, Charging) |
| Señalización feeders | ✅ | 3 pilotos × 19 feeders (Fault, Closed, Open) |
| Señalización sistema | ✅ | 4 pilotos (ON_GRID, ON_GD, FAULT, SHED) + baliza |
| Comandos interruptores | ✅ | Pulsadores + HMI, con enclavamiento |
| Comandos feeders | ✅ | Pulsadores tipo a + HMI, arbitración prioridades |
| Comunicación Modbus | ✅ | Scheduler + driver MTZ + protocolo Command Interface |
| Señales HMI | ✅ | Estados, alarmas, feeders vía DATA_BUFF |

---

## Importar a TIA Portal

```
1. Abrir TIA Portal V18
2. Crear proyecto → Agregar CPU S7-1215C DC/DC/Rly
3. Importar en este orden:
   a. 08_DB_GLOBAL_STATUS.scl  (renombrar bloque a "DATA_BUFF")
   b. 09_DB_PARAMS.scl         (renombrar bloque a "DB_PARAMS")
   c. 01 a 07_*.scl            (Function Blocks)
   d. 10_OB1_MAIN.scl          (copiar código a OB1 "Main")
4. Renombrar Instance DBs según INSTRUCCIONES_CORRECCION_OB1.md
5. Compilar → Verificar 0 errores
6. Mapear %I/%Q según 03_DOCS/LISTADO_IO.md
7. Configurar Modbus RTU (CM 1241 RS-485, 19200 baud)
```

---

## Documentación Principal

| Documento | Contenido |
|-----------|-----------|
| [RESUMEN_PROYECTO.md](03_DOCS/RESUMEN_PROYECTO.md) | Qué hacía antes vs. ahora, cambios V2→V3 |
| [LISTADO_EQUIPOS.md](03_DOCS/LISTADO_EQUIPOS.md) | 39 equipos, tipos a/b/c/d, mapeo índices |
| [LISTADO_IO.md](03_DOCS/LISTADO_IO.md) | Todas las DI/DO con %I/%Q, Modbus, HMI |
| [README_SCMTA.md](03_DOCS/README_SCMTA.md) | Documentación técnica completa (~30 pág) |
| [INSTRUCCIONES_CORRECCION_OB1.md](03_DOCS/INSTRUCCIONES_CORRECCION_OB1.md) | Cómo importar y renombrar DBs |

---

## Estado del Proyecto

| Etapa | Estado | Fecha |
|-------|--------|-------|
| Diseño y arquitectura | ✅ Completado | 04/02/2026 |
| Código SCL 10 bloques | ✅ Completado | 10/02/2026 |
| GD2 Failover (estados 15-20) | ✅ Completado | 10/02/2026 |
| SHED V2.0 (6 modos) | ✅ Completado | 10/02/2026 |
| Corrección OB1 + DATA_BUFF | ✅ Completado | 14/02/2026 |
| Validación I/O vs hardware real | ✅ Completado | 19/02/2026 |
| FB_OUTPUTS V3.0 (pilotos reales) | ✅ Completado | 19/02/2026 |
| Mapeo %Q feeders (57 DO) | ⏳ Pendiente | — |
| Mapeo %I feeders tipo a (10 DI) | ⏳ Pendiente | — |
| FB_MODBUS_MANAGER completo | ⏳ Pendiente | — |
| Testing en hardware | ⏳ Pendiente | — |
| Integración HMI | ⏳ Pendiente | — |
| Comisionamiento | ⏳ Pendiente | — |

---

**Versión:** 3.0 — Febrero 2026
