# ÍNDICE MAESTRO DE ARCHIVOS — SCMTA TGBT

> **Actualizado:** 2026-02-21 | **Versión proyecto:** 3.1

---

## 01_SCL/ — Código Fuente

| Archivo | Bloque | Versión | Descripción |
|---------|--------|---------|-------------|
| 01_FB_IO_NORMALIZE.scl | FB | 2.0 | Normalización DI → señales lógicas (selectores, pulsadores, GD) |
| 02_FB_SCMTA.scl | FB | 3.0 | Máquina de estados transferencia automática (21 estados, GD2 failover) |
| 03_FB_SHED.scl | FB | 2.0 | Deslastre y reenganche de cargas (19 feeders, 6 modos) |
| 04_FB_CMD_ARBITER.scl | FB | 2.0 | Arbitración comandos (SCMTA > SHED > MANUAL) + enclavamiento |
| 05_FB_OUTPUTS.scl | FB | 3.0 | Pilotos LED (sistema + ACB + feeders) + alarmas + HMI |
| 06_FB_MODBUS_MANAGER.scl | FB | 0.1 | Scheduler Modbus RTU (time-slicing 22 dispositivos) |
| 07_FB_MTZ_DRIVER.scl | FB | 1.1 | Driver Modbus Schneider Command Interface (MasterPact MTZ) |
| 08_DB_GLOBAL_STATUS.scl | DB | 3.0 | DATA_BUFF — DB global compartido (blackboard) |
| 09_DB_PARAMS.scl | DB | 3.0 | Parámetros configurables (RETAIN) |
| 10_OB1_MAIN.scl | OB | 3.0 | Programa principal cíclico (7 networks) |
| 11_INSTANCE_DBS.scl | DB | 0.1 | Instance DBs para FB 03-07 (6 instancias) |

---

## 02_LADDER/ — Conversiones LADDER (referencia)

| Archivo | Descripción |
|---------|-------------|
| 01_FB_IO_NORMALIZE_LADDER.md | FB_IO_NORMALIZE en LADDER |
| LADDER_01_FB_IO_NORMALIZE.md | Conversión completa con rungs |
| LADDER_05_FB_OUTPUTS.md | FB_OUTPUTS en LADDER (versión previa) |
| LADDER_10_OB1_MAIN.md | OB1 en LADDER (visual) |

> **Nota:** Los archivos LADDER corresponden a versiones anteriores del código (pre V3.0). Usar como referencia visual únicamente.

---

## 03_DOCS/ — Documentación Técnica

### Documentos Principales (leer primero)

| Archivo | Contenido | Audiencia |
|---------|-----------|-----------|
| **RESUMEN_PROYECTO.md** | Qué hacía antes vs. ahora, cambios V2→V3, todo lo que controla | Todos |
| **LISTADO_EQUIPOS.md** | 39 equipos del tablero, tipos a/b/c/d, mapeo índices [1..19] | Todos |
| **LISTADO_IO.md** | Mapeo completo DI/DO/%I/%Q, Modbus, HMI, módulos expansión | Programador |
| **README_SCMTA.md** | Documentación técnica master (~30 páginas, 15 secciones) | Programador |

### Documentos de Referencia

| Archivo | Contenido | Audiencia |
|---------|-----------|-----------|
| ARQUITECTURA_DESLASTRE_V2.md | Diseño detallado SHED V2.0 (6 modos, temporal) | Programador |
| CAMBIOS_REQ_2_SEGUNDOS.md | REQ Modbus activo 2s (requisito hardware RS-485) | Programador |
| INSTRUCCIONES_CORRECCION_OB1.md | Renombrado DB_GLOBAL_STATUS → DATA_BUFF + instancias | Programador |
| GUIA_COMPLETA_SCL_LADDER.md | Comparación SCL vs LADDER, recomendaciones | Decisión |
| INTRODUCCION_TECNICA_INGENIERO.md | Guía onboarding ingeniero nuevo (plan 20 días) | Nuevo miembro |
| VALIDACION_SCL_TIA_V18.md | Validación compatibilidad código SCL con TIA V18 | QA |
| INDEX.md | **Este archivo** | Todos |

---

## 04_UML/ — Diagramas PlantUML

| Archivo | Contenido |
|---------|-----------|
| 11_UML_SCMTA_StateMachine.puml | Máquina estados SCMTA estados 0-14 (GD1) |
| 12_UML_MTZ_Driver_StateMachine.puml | Estados driver Modbus MTZ |
| 13_UML_SHED_Activity.puml | Diagrama actividad deslastre/reenganche |
| 14_UML_SCMTA_GD2_StateMachine.puml | Estados SCMTA GD2 failover (15-20) |
| 15_UML_System_Architecture.puml | Arquitectura completa del sistema |
| README_UML.md | Catálogo y documentación diagramas |

Visualizar con: [plantuml.com](https://www.plantuml.com/plantuml/uml/) o extensión VS Code PlantUML.

---

## 05_MANUALES/ — Manuales de Referencia

| Archivo | Contenido |
|---------|-----------|
| MTZ MANUAL.pdf | Manual MasterPact MTZ — protocolo Modbus, registros |
| Escritura_MTZ.pdf | Procedimiento escritura/comando MTZ vía Modbus |
| masterpact mtz1 y mtz2.pdf | Catálogo MasterPact MTZ1/MTZ2 |
| NSX MANUAL.pdf | Manual Compact NSX — Modbus feeders |
| MTZ_MODBUS_CHARGING_REGISTERS.md | Extracto registros clave: 32001 (estado), 8000 (cmd) |
| s71200_system_manual_en-US_en-US.pdf | Manual CPU S7-1200 |
| s7_1500_compare_table_en_mnemo.pdf | Tabla comparación S7-1500 (referencia) |
| 81318674_Programming_guideline_DOC_v16_en.pdf | Guía programación Siemens |

---

## 06_CONFIG/ — Configuración del Proyecto

| Archivo | Contenido |
|---------|-----------|
| TGBT_Config - listado de equipos.pdf | Listado original equipos del tablero |
| TGBT_Config - listado de entradas y salidas.pdf | Listado original I/O del proyecto |
| TGBT_Config - pm5330.pdf | Configuración medidor PM5330 |
| ET MONTAJE-TGBT.pdf | Esquema de montaje eléctrico |

---

## 07_TEST/ — Tests Automatizados

| Archivo | Contenido | Estado |
|---------|-----------|--------|
| TEST_FB_IO_NORMALIZE_SCMTA.scl | Test happy path (15 pasos) | ✅ Listo para TIA import |
| TEST_FB_FALLAS_SCMTA.scl | Test fallas (37 pasos) | ✅ Listo para TIA import |
| TEST_FB_SHED.scl | Test deslastre V2.0 (20 pasos, [1..19]) | ✅ Listo para TIA import |
| TEST_FB_GD2_FAILOVER.scl | Test failover GD1↔GD2 (25 pasos) | ✅ Listo para TIA import |
| TEST_FB_SYSTEM_VALIDATION.scl | Test integración completa (50 pasos) | ✅ Listo para TIA import |
| 12_TEST_INSTANCE_DBS.scl | Instance DBs para 5 test FBs | ✅ Listo para TIA import |
| README_TEST.md | Documentación test happy path | ✅ |
| README_TEST_FALLAS.md | Documentación test fallas | ✅ |

---

## Archivos Eliminados (histórico)

Los siguientes archivos fueron eliminados el 2026-02-20 por ser artefactos de análisis o documentos de reunión que ya no aplican:

| Archivo | Motivo eliminación |
|---------|-------------------|
| 03_DOCS/INDICE_REUNION.md | Preparación reunión 10/02 — ya pasó |
| 03_DOCS/PRESENTACION_REUNION_2026-02-10.md | Snapshot reunión 10/02 — métricas obsoletas |
| 03_DOCS/RESUMEN_EJECUTIVO_REUNION.md | Handout reunión 10/02 — redundante |
| 05_MANUALES/Escritura_MTZ_FULL_TEXT.txt | Extracción texto PDF — artefacto análisis |
| 05_MANUALES/Escritura_MTZ_RELEVANT.txt | Extracción texto PDF — artefacto análisis |
| 05_MANUALES/MTZ MANUAL_FULL_TEXT.txt | Extracción texto PDF — artefacto análisis |
| 05_MANUALES/MTZ MANUAL_RELEVANT.txt | Extracción texto PDF — artefacto análisis |
| 05_MANUALES/MTZ_MANUAL_STATUS_REGISTERS.txt | Extracción texto PDF — reemplazado por .md |
