# LISTADO DE ENTRADAS Y SALIDAS — TGBT SCMTA

> **Versión:** 1.0  
> **Fecha:** 2026-02-20  
> **Fuente:** TGBT_Config - listado de entradas y salidas.pdf (06_CONFIG), código SCL v3.0  
> **CPU:** S7-1215C DC/DC/Rly (14 DI / 10 DO / 2 AI integradas)

---

## 1. Resumen de I/O

| Tipo | Asignadas | Disponible CPU | Módulos Expansión |
|------|-----------|---------------|-------------------|
| **DI** | 16 confirmadas + 10 feeders pendientes | 14 integradas | Requiere expansión |
| **DO** | 16 ACB+sistema + 57 feeders pendientes | 10 integradas | Requiere expansión |
| **AI** | 0 (mediciones por Modbus) | 2 integradas | — |
| **Modbus RTU** | 22 dispositivos (3 ACB + 19 feeders) | — | Puerto RS-485 |

---

## 2. Entradas Digitales (DI) — Asignadas en OB1

### 2.1 Sistema y Selectores

| Dirección | Señal | Descripción | Tipo |
|-----------|-------|-------------|------|
| %I0.0 | DI_SYS_AUTO | Selector AUTO/MANUAL del sistema | Selector 2 pos |
| %I0.1 | DI_QT1_REMOTE_SEL | Selector LOCAL/REMOTO QT1 | Selector 2 pos |
| %I0.4 | DI_QG1_REMOTE_SEL | Selector LOCAL/REMOTO QG1 | Selector 2 pos |
| %I1.0 | DI_QG2_REMOTE_SEL | Selector LOCAL/REMOTO QG2 | Selector 2 pos |

### 2.2 Pulsadores Interruptores Fuente

| Dirección | Señal | Descripción | Tipo |
|-----------|-------|-------------|------|
| %I0.2 | DI_QT1_PB_OPEN | Pulsador ABRIR QT1 | NA, 24VDC |
| %I0.3 | DI_QT1_PB_CLOSE | Pulsador CERRAR QT1 | NA, 24VDC |
| %I0.5 | DI_QG1_PB_OPEN | Pulsador ABRIR QG1 | NA, 24VDC |
| %I0.6 | DI_QG1_PB_CLOSE | Pulsador CERRAR QG1 | NA, 24VDC |
| %I1.1 | DI_QG2_PB_OPEN | Pulsador ABRIR QG2 | NA, 24VDC |
| %I1.2 | DI_QG2_PB_CLOSE | Pulsador CERRAR QG2 | NA, 24VDC |

### 2.3 Grupo Electrógeno 1 (GD1)

| Dirección | Señal | Descripción | Tipo |
|-----------|-------|-------------|------|
| %I1.3 | DI_GD_READY | GD1 listo para transferir | Contacto aux |
| %I1.4 | DI_GD_RUNNING | GD1 en marcha | Contacto aux |
| %I1.5 | DI_GD_ALARM | GD1 en alarma/falla | Contacto aux |

### 2.4 Grupo Electrógeno 2 (GD2)

| Dirección | Señal | Descripción | Tipo |
|-----------|-------|-------------|------|
| %I1.6 | DI_GD2_READY | GD2 listo para transferir | Contacto aux |
| %I1.7 | DI_GD2_RUNNING | GD2 en marcha | Contacto aux |
| %I2.1 | DI_GD2_ALARM | GD2 en alarma/falla | Contacto aux |

### 2.5 Control

| Dirección | Señal | Descripción | Tipo |
|-----------|-------|-------------|------|
| %I2.0 | RESET_FAULT | Reset/Reconocimiento falla | Pulsador NA |
| %I2.1 | ACK_ALARM | Reconocimiento alarma | Pulsador NA |

### 2.6 Pulsadores Feeders (PENDIENTE — Solo tipo a)

Solo los 5 feeders tipo a tienen pulsadores físicos. Requieren módulo de expansión DI.

| Dirección | Señal | Feeder | Tipo |
|-----------|-------|--------|------|
| **TODO** | DI_FEEDER_PB_OPEN[1] | Q3.1 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_OPEN[2] | Q3.2 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_OPEN[3] | Q3.3 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_OPEN[12] | Q5.2 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_OPEN[18] | Q22 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_CLOSE[1] | Q3.1 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_CLOSE[2] | Q3.2 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_CLOSE[3] | Q3.3 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_CLOSE[12] | Q5.2 (tipo a) | NA, 24VDC |
| **TODO** | DI_FEEDER_PB_CLOSE[18] | Q22 (tipo a) | NA, 24VDC |

**Total DI feeders:** 10 (5 open + 5 close)

### 2.7 DI NO implementada

| Señal | Descripción | Motivo |
|-------|-------------|--------|
| DI_QT1_POWER_SEL | Selector potencia QT1 (0-1-2) | No se implementa en esta versión |

---

## 3. Salidas Digitales (DO) — Asignadas en OB1

### 3.1 Pilotos Sistema (4 DO)

| Dirección | Señal | Descripción | Color LED |
|-----------|-------|-------------|-----------|
| %Q1.0 | DO_PILOT_ON_GRID | Piloto "EN RED" | Verde |
| %Q1.1 | DO_PILOT_ON_GD | Piloto "EN GRUPO" | Amarillo |
| %Q1.2 | DO_PILOT_FAULT | Piloto "FALLA" | Rojo |
| %Q1.3 | DO_PILOT_SHED | Piloto "DESLASTRE ACTIVO" | Amarillo |

### 3.2 Pilotos Interruptor QT1 (4 DO)

| Dirección | Señal | Descripción | Color LED | Fuente |
|-----------|-------|-------------|-----------|--------|
| %Q1.4 | DO_PILOT_QT1_OPEN | QT1 abierto | Verde | QT1_STATE = 0 |
| %Q1.5 | DO_PILOT_QT1_CLOSED | QT1 cerrado | Rojo | QT1_STATE = 1 |
| %Q1.6 | DO_PILOT_QT1_FAULT | QT1 falla/disparado | Ámbar | QT1_TRIPPED (Modbus SD) |
| %Q1.7 | DO_PILOT_QT1_CHARGING | QT1 listo (resorte cargado) | Blanco | QT1_READY (Modbus PF) |

### 3.3 Pilotos Interruptor QG1 (4 DO)

| Dirección | Señal | Descripción | Color LED | Fuente |
|-----------|-------|-------------|-----------|--------|
| %Q2.0 | DO_PILOT_QG1_OPEN | QG1 abierto | Verde | QG1_STATE = 0 |
| %Q2.1 | DO_PILOT_QG1_CLOSED | QG1 cerrado | Rojo | QG1_STATE = 1 |
| %Q2.2 | DO_PILOT_QG1_FAULT | QG1 falla/disparado | Ámbar | QG1_TRIPPED (Modbus SD) |
| %Q2.3 | DO_PILOT_QG1_CHARGING | QG1 listo (resorte cargado) | Blanco | QG1_READY (Modbus PF) |

### 3.4 Pilotos Interruptor QG2 (4 DO)

| Dirección | Señal | Descripción | Color LED | Fuente |
|-----------|-------|-------------|-----------|--------|
| %Q2.4 | DO_PILOT_QG2_OPEN | QG2 abierto | Verde | QG2_STATE = 0 |
| %Q2.5 | DO_PILOT_QG2_CLOSED | QG2 cerrado | Rojo | QG2_STATE = 1 |
| %Q2.6 | DO_PILOT_QG2_FAULT | QG2 falla/disparado | Ámbar | QG2_TRIPPED (Modbus SD) |
| %Q2.7 | DO_PILOT_QG2_CHARGING | QG2 listo (resorte cargado) | Blanco | QG2_READY (Modbus PF) |

### 3.5 Alarmas (1 DO)

| Dirección | Señal | Descripción | Tipo |
|-----------|-------|-------------|------|
| %Q3.0 | DO_ALARM_BEACON | Baliza alarma | Relé/Piloto rojo |

### 3.6 Pilotos Feeders (PENDIENTE — 57 DO)

Cada uno de los 19 feeders con Modbus tiene 3 pilotos:

| Señal | Descripción | Color LED | Fuente |
|-------|-------------|-----------|--------|
| DO_PILOT_FEEDER_FAULT[i] | Feeder en falla | Ámbar | FEEDER_TRIPPED OR FEEDER_ALARM |
| DO_PILOT_FEEDER_CLOSED[i] | Feeder cerrado | Rojo | FEEDER_STATE = 1 |
| DO_PILOT_FEEDER_OPEN[i] | Feeder abierto | Verde | FEEDER_STATE = 0 |

**Total DO feeders:** 57 (19 × 3)

> **NOTA:** Las direcciones %Q de los 57 pilotos de feeders están pendientes de asignar.  
> Se requieren módulos de expansión DO adicionales (ej: SM 1222 de 8 DO relé).  
> Mínimo 8 módulos de 8 DO = 64 DO → cubren los 57 pilotos de feeders.

### 3.7 Señales ELIMINADAS v3.0

| Señal eliminada | Motivo |
|----------------|--------|
| DO_PILOT_QT1_LOCAL | No existe piloto LOCAL físico |
| DO_PILOT_QG1_LOCAL | No existe piloto LOCAL físico |
| DO_PILOT_QG2_LOCAL | No existe piloto LOCAL físico |
| DO_PILOT_TRANSFER | No fue solicitado — no hay LED transferencia |
| DO_ALARM_HORN | No existe bocina/sirena en tablero |

---

## 4. Comunicación Modbus RTU

### 4.1 Interruptores Fuente (MasterPact MTZ)

| Slave ID | Equipo | Registro Lectura | Registro Escritura |
|----------|--------|------------------|--------------------|
| DB_PARAMS.SLAVE_ID_QT1 | QT1 (RED) | 32001 (estado) | 8000-8021 (comandos) |
| DB_PARAMS.SLAVE_ID_QG1 | QG1 (GD01) | 32001 (estado) | 8000-8021 (comandos) |
| DB_PARAMS.SLAVE_ID_QG2 | QG2 (GD02) | 32001 (estado) | 8000-8021 (comandos) |

Registro 32001 — Mapa de bits:
| Bit | Nombre | Descripción |
|-----|--------|-------------|
| 0 | OF | Open/Closed flag |
| 1 | SD | Tripped |
| 3 | CH | Spring charged |
| 5 | PF | Ready to close |

Códigos de comando:
| Código | Acción |
|--------|--------|
| 904 | Open (abrir) |
| 905 | Close (cerrar) |
| 906 | Reset (rearmar disparo) |

### 4.2 Feeders (NSX con Modbus)

| Slave ID | Equipo | Índice en arrays |
|----------|--------|-----------------|
| DB_PARAMS.SLAVE_ID_FEEDER[1] | Q3.1 | 1 |
| DB_PARAMS.SLAVE_ID_FEEDER[2] | Q3.2 | 2 |
| DB_PARAMS.SLAVE_ID_FEEDER[3] | Q3.3 | 3 |
| ... | ... | ... |
| DB_PARAMS.SLAVE_ID_FEEDER[19] | Q23 | 19 |

Ver tabla completa de mapeo índice ↔ feeder en [LISTADO_EQUIPOS.md](LISTADO_EQUIPOS.md).

---

## 5. Señales HMI (vía DATA_BUFF)

Estas señales no usan I/O física. Se transfieren por comunicación HMI↔PLC.

### 5.1 Estado General

| Variable DATA_BUFF | Tipo | Descripción |
|--------------------|------|-------------|
| SCMTA_STATE | Int | Estado actual máquina SCMTA (0-20) |
| SCMTA_STATE_NAME | String[30] | Nombre estado en texto |
| IS_ON_GRID | Bool | Alimentado por red pública |
| IS_ON_GD | Bool | Alimentado por grupo electrógeno |
| IS_IN_TRANSFER | Bool | En proceso de transferencia |
| IS_FAULT | Bool | En estado de falla |
| FAULT_CODE | Int | Código de falla activa |

### 5.2 HMI Feeders

| Variable DATA_BUFF | Tipo | Descripción |
|--------------------|------|-------------|
| HMI_FEEDER_OPEN[1..19] | Array of Bool | Feeders abiertos |
| HMI_FEEDER_CLOSED[1..19] | Array of Bool | Feeders cerrados |
| HMI_FEEDER_TRIPPED[1..19] | Array of Bool | Feeders disparados |
| HMI_FEEDER_ALARM[1..19] | Array of Bool | Feeders en alarma |
| HMI_ALARM_ACTIVE | Bool | Hay alarma activa |
| HMI_ALARM_TEXT | String[80] | Texto alarma para HMI |

### 5.3 Comandos HMI → PLC

| Variable DATA_BUFF | Tipo | Descripción |
|--------------------|------|-------------|
| HMI_CMD_OPEN_QT1 | Bool | Comando HMI abrir QT1 |
| HMI_CMD_CLOSE_QT1 | Bool | Comando HMI cerrar QT1 |
| HMI_CMD_OPEN_QG1 | Bool | Comando HMI abrir QG1 |
| HMI_CMD_CLOSE_QG1 | Bool | Comando HMI cerrar QG1 |
| HMI_CMD_OPEN_QG2 | Bool | Comando HMI abrir QG2 |
| HMI_CMD_CLOSE_QG2 | Bool | Comando HMI cerrar QG2 |
| HMI_CMD_FEEDER_OPEN[1..19] | Array of Bool | Comando HMI abrir feeder |
| HMI_CMD_FEEDER_CLOSE[1..19] | Array of Bool | Comando HMI cerrar feeder |

---

## 6. Resumen de Módulos de Expansión Necesarios

| Módulo | Cantidad | Señales | Uso |
|--------|----------|---------|-----|
| SM 1221 DI 8×24VDC | 2 | 16 DI | Pulsadores feeders (10 DI) + reserva |
| SM 1222 DO 8×Relé | 8 | 64 DO | Pilotos feeders (57 DO) + reserva |
| CM 1241 RS-485 | 1 | — | Modbus RTU Master |

> **NOTA:** Cantidades aproximadas. Confirmar con hardware real disponible.
