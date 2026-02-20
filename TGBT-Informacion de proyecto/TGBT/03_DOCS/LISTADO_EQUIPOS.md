# LISTADO DE EQUIPOS — TGBT SCMTA

> **Versión:** 1.0  
> **Fecha:** 2026-02-20  
> **Fuente:** TGBT_Config - listado de equipos.pdf (06_CONFIG)

---

## 1. Resumen General

| Concepto | Cantidad |
|----------|----------|
| Interruptores Fuente (ACB) MasterPact MTZ | 3 |
| Feeders con Modbus | 19 |
| Feeders sin Modbus | 17 |
| **Total equipos tablero** | **39** |
| Dispositivos con comunicación Modbus | 22 (3 ACB + 19 feeders) |

---

## 2. Interruptores de Fuente (ACB — MasterPact MTZ)

| ID | Designación | Tipo | Comunicación | Función |
|----|-------------|------|-------------|---------|
| QT1 | Interruptor RED | MasterPact MTZ | Modbus RTU | Alimentación desde transformador (red pública) |
| QG1 | Interruptor GD01 | MasterPact MTZ | Modbus RTU | Alimentación desde Grupo Electrógeno 1 |
| QG2 | Interruptor GD02 | MasterPact MTZ | Modbus RTU | Alimentación desde Grupo Electrógeno 2 |

Señales disponibles por Modbus (Registro 32001):
- **Bit 0 (OF):** Open/Closed (estado interruptor)
- **Bit 1 (SD):** Tripped (disparado por falla)
- **Bit 3 (CH):** Spring charged (resorte cargado)
- **Bit 5 (PF):** Ready to close (preparado para cerrar)

---

## 3. Feeders con Modbus (19 unidades)

Estos feeders se comunican por Modbus RTU y son gestionados por el PLC para deslastre, monitoreo y señalización.

Se dividen en dos tipos según su hardware en puerta de tablero:

### Tipo A — Con pulsadores físicos (5 feeders)
Tienen botonera ABRIR/CERRAR en puerta del tablero.

| Índice | ID Tablero | Pulsadores | Observaciones |
|--------|-----------|------------|--------------|
| 1 | Q3.1 | SI | Modbus tipo a |
| 2 | Q3.2 | SI | Modbus tipo a |
| 3 | Q3.3 | SI | Modbus tipo a |
| 12 | Q5.2 | SI | Modbus tipo a |
| 18 | Q22 | SI | Modbus tipo a |

### Tipo B — Sin pulsadores físicos (14 feeders)
Solo monitoreo y comando remoto (PLC/HMI).

| Índice | ID Tablero | Pulsadores | Observaciones |
|--------|-----------|------------|--------------|
| 4 | Q3.4 | NO | Modbus tipo b |
| 5 | Q3.5 | NO | Modbus tipo b |
| 6 | Q3.6 | NO | Modbus tipo b |
| 7 | Q4.1 | NO | Modbus tipo b |
| 8 | Q4.2 | NO | Modbus tipo b |
| 9 | Q4.3 | NO | Modbus tipo b |
| 10 | Q4.4 | NO | Modbus tipo b |
| 11 | Q5.1 | NO | Modbus tipo b |
| 13 | Q5.3 | NO | Modbus tipo b |
| 14 | Q5.4 | NO | Modbus tipo b |
| 15 | Q5.5 | NO | Modbus tipo b |
| 16 | Q5.6 | NO | Modbus tipo b |
| 17 | Q21 | NO | Modbus tipo b |
| 19 | Q23 | NO | Modbus tipo b |

### Tabla completa ordenada por índice

| Índice | ID Tablero | Tipo | Columna tablero |
|--------|-----------|------|-----------------|
| 1 | Q3.1 | a | Columna 3 |
| 2 | Q3.2 | a | Columna 3 |
| 3 | Q3.3 | a | Columna 3 |
| 4 | Q3.4 | b | Columna 3 |
| 5 | Q3.5 | b | Columna 3 |
| 6 | Q3.6 | b | Columna 3 |
| 7 | Q4.1 | b | Columna 4 |
| 8 | Q4.2 | b | Columna 4 |
| 9 | Q4.3 | b | Columna 4 |
| 10 | Q4.4 | b | Columna 4 |
| 11 | Q5.1 | b | Columna 5 |
| 12 | Q5.2 | a | Columna 5 |
| 13 | Q5.3 | b | Columna 5 |
| 14 | Q5.4 | b | Columna 5 |
| 15 | Q5.5 | b | Columna 5 |
| 16 | Q5.6 | b | Columna 5 |
| 17 | Q21 | b | — |
| 18 | Q22 | a | — |
| 19 | Q23 | b | — |

---

## 4. Feeders SIN Modbus (17 unidades)

Estos feeders **no tienen comunicación** con el PLC. No participan en deslastre ni monitoreo.

### Tipo C — Sin Modbus, con pulsadores

| ID Tablero | Pulsadores | Observaciones |
|-----------|------------|--------------|
| Q1.1 | SI | Sin Modbus tipo c |
| Q1.2 | SI | Sin Modbus tipo c |
| Q1.3 | SI | Sin Modbus tipo c |
| Q1.4 | SI | Sin Modbus tipo c |
| Q2.1 | SI | Sin Modbus tipo c |
| Q2.2 | SI | Sin Modbus tipo c |
| Q2.3 | SI | Sin Modbus tipo c |
| Q2.4 | SI | Sin Modbus tipo c |
| Q2.5 | SI | Sin Modbus tipo c |
| Q2.6 | SI | Sin Modbus tipo c |

### Tipo D — Sin Modbus, sin pulsadores

| ID Tablero | Pulsadores | Observaciones |
|-----------|------------|--------------|
| Q1.5 | NO | Sin Modbus tipo d |
| Q1.6 | NO | Sin Modbus tipo d |
| Q1.7 | NO | Sin Modbus tipo d |
| Q2.7 | NO | Sin Modbus tipo d |
| Q5.7 | NO | Sin Modbus tipo d |
| Q5.8 | NO | Sin Modbus tipo d |
| Q5.9 | NO | Sin Modbus tipo d |

---

## 5. Relación Tipo ↔ Hardware

| Tipo | Modbus | Pulsadores | Pilotos DO | Cantidad |
|------|--------|-----------|-----------|----------|
| **ACB** | SI | — | 4 (Open, Closed, Fault, Charging) | 3 |
| **a** | SI | SI (ABRIR/CERRAR) | 3 (Fault, Closed, Open) | 5 |
| **b** | SI | NO | 3 (Fault, Closed, Open) | 14 |
| **c** | NO | SI | — | 10 |
| **d** | NO | NO | — | 7 |

---

## 6. Distribución por Columna de Tablero

| Columna | Feeders | Observaciones |
|---------|---------|--------------|
| 1 | Q1.1–Q1.7 | Sin Modbus (4 tipo c, 3 tipo d) |
| 2 | Q2.1–Q2.7 | Sin Modbus (6 tipo c, 1 tipo d) |
| 3 | Q3.1–Q3.6 | Todos con Modbus (3 tipo a, 3 tipo b) |
| 4 | Q4.1–Q4.4 | Todos con Modbus tipo b |
| 5 | Q5.1–Q5.9 | Mixto: 6 con Modbus (1a, 5b) + 3 sin Modbus (tipo d) |
| — | Q21, Q22, Q23 | Con Modbus (Q22 tipo a, resto tipo b) |

---

## 7. Observaciones

1. **QT1 (Power Selector 0-1-2):** Existe físicamente pero **NO se implementa** en esta versión del programa.
2. **Los 19 feeders Modbus** son los únicos que participan en deslastre (FB_SHED) y comando (FB_CMD_ARBITER).
3. **Los 17 feeders sin Modbus** funcionan de forma autónoma — el PLC no los controla ni monitorea.
4. **Arrays en el programa** usan índice `[1..19]` correspondiendo a la tabla de la Sección 3.
5. **SLAVE_ID_FEEDER[1..19]** en DB_PARAMS mapea cada índice a su dirección Modbus real.
