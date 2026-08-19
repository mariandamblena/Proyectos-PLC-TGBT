# SISTEMA SCMTA - DOCUMENTACIÓN TÉCNICA COMPLETA
**Sistema de Control y Monitoreo de Transferencia Automática para TGBT**

**Versión:** 3.0  
**Fecha:** 10 de febrero de 2026  
**Plataforma:** Siemens TIA Portal V18 (S7-1200/1500) - SCL  
**Autor:** Ingeniero Senior Automatización Industrial

---

## 📋 ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Function Blocks Implementados](#function-blocks-implementados)
4. [Data Blocks](#data-blocks)
5. [Máquina de Estados SCMTA](#máquina-de-estados-scmta)
6. [Protocolo Modbus RTU](#protocolo-modbus-rtu)
7. [Deslastre y Reenganche](#deslastre-y-reenganche)
8. [Enclavamiento de Seguridad](#enclavamiento-de-seguridad)
9. [Configuración y Parámetros](#configuración-y-parámetros)
10. [Testing y Comisionamiento](#testing-y-comisionamiento)
11. [Troubleshooting](#troubleshooting)
12. [Mantenimiento](#mantenimiento)

---

## 1. RESUMEN EJECUTIVO

### Objetivo del Sistema
El sistema SCMTA gestiona la **transferencia automática entre Red Externa y Grupo Diésel (GD01/GD02)** en un Tablero General de Baja Tensión (TGBT) real, con control de deslastre de cargas (en modos RED y GD), failover bidireccional GD1↔GD2 y enclavamiento absoluto de fuentes.

### Características Principales
- ✅ **Transferencia automática Red→GD1** con secuencia temporizada y segura
- ✅ **Failover GD1→GD2** cuando GD1 falla (alarma/no arranca)
- ✅ **Failover bidireccional GD1↔GD2** con conmutación automática
- ✅ **Retorno automático GD→Red** con estabilidad de 120s
- ✅ **Deslastre V2** con 6 modos (GRID_SHED, GD_INITIAL_SHED, GD_REACTIVE_SHED, etc.)
- ✅ **Clasificación FEEDER_ESSENTIAL** (esenciales protegidos del deslastre)
- ✅ **Enclavamiento fuente única** fail-safe (QT1/QG1/QG2)
- ✅ **Control Modbus RTU** de interruptores MTZ/NSX con Micrologic
- ✅ **Monitoreo eléctrico** con medidores PM5350
- ✅ **Modo AUTO/MANUAL** + selectores **LOCAL/REMOTO**
- ✅ **Fault lockout** con reset manual
- ✅ **HMI-ready** (señales consolidadas en DB_GLOBAL_STATUS)

### Prioridad Operativa
**RED > GRUPO DIÉSEL**  
El sistema siempre prioriza la red externa sobre el grupo diésel. El retorno a red es automático sin requerir confirmación del operador.

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Topología Eléctrica

```
┌──────────────┐
│  RED EXTERNA │ (380V 3Ph 50Hz)
└──────┬───────┘
       │
    ┌──▼──┐
    │ QT1 │ ◄── Masterpact MTZ1 (Modbus RTU)
    └──┬──┘
       │
       │           ┌──────────────┐
       │           │   GD01       │ 1000 kVA
       │           │ (Grupo       │
       │           │  Diésel)     │
       │           └──────┬───────┘
       │                  │
       │               ┌──▼──┐
       │               │ QG1 │ ◄── Masterpact MTZ2 (Modbus RTU)
       │               └──┬──┘
       │                  │
       │           ┌──────┴───────┐
       │           │   GD02       │ (Futuro)
       │           │ (Expansión)  │
       │           └──────┬───────┘
       │                  │
       │               ┌──▼──┐
       │               │ QG2 │ ◄── Masterpact MTZ (futuro)
       │               └──┬──┘
       └──────────────────┘
                 │
         ┌───────▼───────┐
         │  BARRA COMÚN  │
         └───────┬───────┘
                 │
    ┌────────────┴────────────┐
    │   SALIDAS (18 feeders)  │
    │   NSX con Micrologic    │
    │   (Modbus RTU)          │
    └─────────────────────────┘
```

**REGLA ABSOLUTA:** Solo un interruptor de fuente (QT1/QG1/QG2) puede estar cerrado simultáneamente.

### 2.2 Arquitectura Software (OB1)

```
OB1 - MAIN CYCLIC EXECUTION (100-200ms)
│
├─ Network 1: FB_IO_NORMALIZE (DB_IO)
│   └─ Input: DI físicas (selectores, pulsadores, GD)
│   └─ Output: Señales lógicas normalizadas
│
├─ Network 2: FB_SCMTA (DB_SCMTA)
│   └─ Input: Modo, estados, mediciones
│   └─ Output: Requests SCMTA, DO_GD_START/STOP, flags estado
│
├─ Network 3: FB_SHED (DB_SHED)
│   └─ Input: IS_ON_GD, carga GD/TR, arrays config
│   └─ Output: Requests SHED (abrir/cerrar feeders)
│
├─ Network 4: FB_CMD_ARBITER (DB_ARBITER)
│   └─ Input: Requests SCMTA/SHED/MANUAL, permisos LOCAL/REMOTO
│   └─ Output: Comandos finales CMD_* (con enclavamiento)
│
├─ Network 5: FB_OUTPUTS (DB_OUTPUTS)
│   └─ Input: Estados, alarmas
│   └─ Output: DO pilotos, bocina, baliza, HMI
│
├─ Network 6: Drivers MTZ (DB_QT1_DRV, DB_QG1_DRV, DB_QG2_DRV)
│   └─ Input: CMD_OPEN/CLOSE
│   └─ Output: CB_STATE, CB_TRIPPED, CB_READY
│
└─ Network 7: Cálculos auxiliares
    └─ GD_LoadPct, TR_LoadPct, Uptime
```

### 2.3 Flujo de Datos

```
DI físicas
    ↓
FB_IO_NORMALIZE → Señales lógicas → DB_GLOBAL_STATUS
    ↓
FB_SCMTA (máquina estados) → Requests SCMTA
    ↓                              ↓
FB_SHED (deslastre)    →    Requests SHED
    ↓                              ↓
         FB_CMD_ARBITER (priorización + enclavamiento)
                   ↓
            Comandos CMD_*
                   ↓
         Drivers MTZ/NSX (Modbus RTU)
                   ↓
         Interruptores físicos
                   ↓
         Feedback estado → DB_GLOBAL_STATUS
```

---

## 3. FUNCTION BLOCKS IMPLEMENTADOS

### 3.1 FB_IO_NORMALIZE (Normalización E/S)

**Archivo:** `01_FB_IO_NORMALIZE.scl`

**Responsabilidades:**
1. Conversión selector AUTO/MANUAL → `MODE_AUTO` / `MODE_MANUAL`
2. Interpretación selectores LOCAL/REMOTO → `*_REMOTE_ALLOWED`
3. Debounce 50ms en pulsadores Open/Close
4. Detección flancos → `REQ_MAN_*` (pulsos 1 scan)
5. Passthrough señales GD (READY, RUNNING, ALARM)

**Entradas:**
- `DI_SYS_AUTO`: Selector Auto/Manual (TRUE=Auto)
- `DI_QT1_REMOTE_SEL`: Selector Local/Remoto QT1
- `DI_QT1_PB_OPEN/CLOSE`: Pulsadores QT1
- (Idem QG1, QG2)
- `DI_GD_READY/RUNNING/ALARM`: Señales GD

**Salidas:**
- `MODE_AUTO` / `MODE_MANUAL`
- `QT1_REMOTE_ALLOWED` / `QG1_REMOTE_ALLOWED` / `QG2_REMOTE_ALLOWED`
- `REQ_MAN_QT1_OPEN/CLOSE` (pulsos)
- `GD_READY` / `GD_RUNNING` / `GD_ALARM`

**Lógica Fail-Safe:**
- Si selector AUTO indefinido → DEFAULT a MANUAL

---

### 3.2 FB_SCMTA (Máquina de Estados Transferencia)

**Archivo:** `02_FB_SCMTA.scl`

**Responsabilidades:**
1. Detección falta de red (tensión + falta de fase + frecuencia)
2. Secuencia automática Red→GD con tiempos de seguridad
3. Retorno automático GD→Red con estabilidad 120s
4. Generación requests abstractos (`REQ_SCMTA_OPEN_QT1`, etc.)
5. Control marcha/parada GD (`DO_GD_START`/`DO_GD_STOP`)
6. Gestión fallas y lockout

**Estados (0-20):**
| Estado | Nombre | Descripción |
|--------|--------|-------------|
| 0 | INIT | Inicialización sistema |
| 1 | NORMAL_ON_GRID | Operación normal con RED (QT1 cerrado) |
| 2 | GRID_FAIL_DETECTED | Falla de red detectada (filtrada 2s) |
| 3 | OPEN_QT1 | Abriendo QT1 (timeout 2s) |
| 4 | START_GD_DELAY | Delay 3s antes de arrancar GD1 |
| 5 | START_GD | Dando orden marcha GD1 (`DO_GD_START=1`) |
| 6 | WAIT_GD_READY | Esperando GD1_READY + estabilización 5s (timeout 30s) |
| 7 | CLOSE_QG1 | Cerrando QG1 con enclavamiento (timeout 2s) |
| 8 | ON_GD | Operación normal con GD1 (QG1 cerrado) |
| 9 | GRID_RETURN_DETECTED | Retorno de red detectado |
| 10 | WAIT_GRID_STABLE | Esperando estabilidad red 120s (si rebota vuelve a ON_GD) |
| 11 | OPEN_QG1 | Abriendo QG1 para retorno (timeout 2s) |
| 12 | CLOSE_QT1 | Cerrando QT1 con enclavamiento (timeout 2s) |
| 13 | GD_COOLDOWN | Cooldown 60s y parada GD (`DO_GD_STOP=1`) |
| 14 | FAULT_LOCKOUT | Falla - requiere `RESET_FAULT` manual |
| 15 | START_GD2_DELAY | Delay antes de arrancar GD2 (failover desde GD1) |
| 16 | START_GD2 | Dando orden marcha GD2 (`DO_GD2_START=1`) |
| 17 | WAIT_GD2_READY | Esperando GD2_READY + estabilización (timeout 30s) |
| 18 | CLOSE_QG2 | Cerrando QG2 con enclavamiento (timeout 2s) |
| 19 | ON_GD2 | Operación normal con GD2 (QG2 cerrado) |
| 20 | OPEN_GD_FOR_SWITCH | Abriendo GD actual para conmutar a otro GD |

**Condiciones de Falta de Red:**
```
GRID_FAIL = TRUE si:
  - V_L1L2 < V_MIN (85% de 380V = 323V) OR > V_MAX (110% = 418V)
  - V_L2L3 < V_MIN OR > V_MAX
  - V_L3L1 < V_MIN OR > V_MAX
  - FREQ < FREQ_MIN (49 Hz) OR > FREQ_MAX (51 Hz)
  - GRID_MEASUREMENT_OK = FALSE
  
  Filtro: 2s sostenido para confirmar falla (evitar transitorios)
```

**Códigos de Falla:**
| Código | Descripción |
|--------|-------------|
| 101 | Timeout Open QT1 (>2s) |
| 102 | GD no alcanzó READY (>30s) |
| 103 | Timeout Close QG1 (>2s) |
| 104 | Timeout Open QG1 (>2s) |
| 105 | Timeout Close QT1 (>2s) |
| 106 | Alarma GD (falla grupo diésel) |
| 107 | Violación enclavamiento fuente única |
| 108 | Estado máquina desconocido |
| 202 | Timeout Open QG1 en failover GD1→GD2 |
| 203 | GD2 no alcanzó READY (timeout) |
| 204 | Timeout Close QG2 |
| 205 | Alarma GD2 |
| 206 | Timeout Open QG2 en failover GD2→GD1 |
| 207 | GD1 no alcanzó READY en failover (timeout) |
| 208 | Timeout Close QG1 en failover GD2→GD1 |
| 209 | Timeout Open GD para conmutación |
| 210 | Failover GD1↔GD2 fallido (ambos GD no disponibles) |

**Transiciones GD2 (Failover):**
- Estado 8 (ON_GD1) → Si GD1_ALARM o GD1 falla → Estado 15 (START_GD2_DELAY)
- Estado 19 (ON_GD2) → Si GD2_ALARM o GD2 falla → Estado 20 (OPEN_GD_FOR_SWITCH) → GD1
- Estado 19 (ON_GD2) → Si GRID_OK retorna → misma secuencia retorno (estados 9-13)

---

### 3.3 FB_SHED (Deslastre y Reenganche V2.0)

**Archivo:** `03_FB_SHED.scl`

**Responsabilidades:**
1. Deslastre escalonado en modo GD (sobrecarga GD) **y** en modo RED (sobrecarga trafo)
2. Reenganche escalonado al reducir carga o retornar a red
3. Clasificación **FEEDER_ESSENTIAL** (feeders esenciales protegidos del deslastre)
4. Gestión prioridades mediante arrays `SHED_ORDER[1..18]` y `RECONNECT_ORDER[1..18]`
5. Enable/disable por feeder mediante `SHED_ENABLE[1..18]`
6. Máquina de 6 modos de operación (SHED_MODE)

**Modos de Operación (SHED_MODE):**
| Modo | Nombre | Descripción |
|------|--------|-------------|
| 0 | IDLE | Sin deslastre activo |
| 1 | GRID_SHED | Deslastre por sobrecarga de trafo en RED (TR_LoadPct > TR_SHED_ON) |
| 2 | GD_INITIAL_SHED | Deslastre inicial al entrar a GD (cortar no-esenciales) |
| 3 | GD_RECONNECT | Reenganche parcial en GD (reconectar si carga permite) |
| 4 | GD_REACTIVE_SHED | Deslastre reactivo en GD (GD_LoadPct > SHED_ON) |
| 5 | GRID_RECONNECT | Reenganche al retornar a RED (reconectar todos) |

**Clasificación FEEDER_ESSENTIAL:**
```
FEEDER_ESSENTIAL[1..18] : ARRAY OF BOOL
  - TRUE = Feeder esencial (NO se deslasta en GD_INITIAL_SHED)
  - FALSE = Feeder no-esencial (se deslasta al entrar a GD)
```

**Lógica Deslastre GD (reactivo):**
```
IF (GD_LoadPct > SHED_ON_PCT) AND IS_ON_GD AND MODE_AUTO THEN
    SHED_MODE := 4  // GD_REACTIVE_SHED
    Filtrar 2s (evitar bouncing)
    
    FOR SHED_STEP = 1 TO 18 DO
        feederID = SHED_ORDER[SHED_STEP]
        
        IF SHED_ENABLE[feederID] AND NOT FEEDER_ESSENTIAL[feederID]
           AND FEEDER_STATE[feederID] = CERRADO THEN
            REQ_SHED_OPEN[feederID] = TRUE
            Esperar T_SHED_STEP (3-5s)
        END_IF
        
        IF GD_LoadPct < SHED_OFF (70%) THEN
            CANCELAR deslastre (histéresis)
            EXIT
        END_IF
    END_FOR
END_IF
```

**Lógica Deslastre RED (trafo):**
```
IF (TR_LoadPct > TR_SHED_ON_PCT) AND IS_ON_GRID AND MODE_AUTO THEN
    SHED_MODE := 1  // GRID_SHED
    Misma lógica escalonada pero con umbrales de trafo
END_IF
```

**Lógica Reenganche:**
```
IF IS_ON_GRID AND FEEDERS_SHED > 0 AND MODE_AUTO THEN
    SHED_MODE := 5  // GRID_RECONNECT
    FOR RECONNECT_STEP = 1 TO 18 DO
        feederID = RECONNECT_ORDER[RECONNECT_STEP]
        
        IF SHED_ENABLE[feederID] AND FEEDER_STATE[feederID] = ABIERTO THEN
            REQ_SHED_CLOSE[feederID] = TRUE
            Esperar T_RECONNECT_STEP (3-5s)
        END_IF
    END_FOR
END_IF
```

**Configuración Prioridades:**
El array `SHED_ORDER` define el orden de corte de feeders. Ejemplo:
```
SHED_ORDER = [5, 12, 3, 8, 15, 1, 9, ...]
  → Paso 1: cortar feeder 5 (ej. 400A)
  → Paso 2: cortar feeder 12 (ej. 320A)
  → Paso 3: cortar feeder 3 (ej. 250A)
  → etc.
```

Típicamente se deslastran primero los feeders de **mayor amperaje** (400A → 320A → 250A) para tener mayor impacto en la reducción de carga.

---

### 3.4 FB_CMD_ARBITER (Árbitro de Comandos)

**Archivo:** `04_FB_CMD_ARBITER.scl`

**Responsabilidades:**
1. Priorizar requests: **SCMTA > SHED > MANUAL**
2. Verificar enclavamiento fuente única (QT1/QG1/QG2)
3. Bloquear comandos si interruptor en LOCAL
4. Evitar comandos simultáneos Open+Close
5. Generar comandos finales `CMD_*` para drivers Modbus

**Lógica de Priorización:**
```
IF MODE_AUTO = TRUE THEN
    // Prioridad 1: SCMTA (transferencia automática)
    CMD_OPEN_QT1 = REQ_SCMTA_OPEN_QT1
    CMD_CLOSE_QG1 = REQ_SCMTA_CLOSE_QG1
    etc.
    
    // Prioridad 2: SHED (si no hay request SCMTA activo)
    FOR i = 1 TO 18 DO
        IF REQ_SHED_OPEN[i] = TRUE THEN
            CMD_OPEN_FEEDER[i] = REQ_SHED_OPEN[i]
        END_IF
    END_FOR

ELSIF MODE_MANUAL = TRUE THEN
    // Prioridad 3: MANUAL (solo si modo manual)
    CMD_OPEN_QT1 = REQ_MAN_QT1_OPEN
    CMD_CLOSE_QT1 = REQ_MAN_QT1_CLOSE
    etc.
END_IF
```

**Enclavamiento Fuente Única:**
```
// Antes de cerrar QT1, verificar que QG1 y QG2 estén ABIERTOS
IF REQ_*_CLOSE_QT1 = TRUE THEN
    IF (QG1_STATE = 0) AND (QG2_STATE = 0) THEN
        CMD_CLOSE_QT1 = TRUE  // OK, enclavamiento verificado
    ELSE
        BLOCK_INTERLOCK = TRUE  // BLOQUEAR comando
    END_IF
END_IF

// Idem para QG1 y QG2
```

**Bloqueo por LOCAL:**
```
// Si interruptor está en LOCAL, PLC no debe comandar
IF REQ_*_OPEN_QT1 = TRUE AND QT1_REMOTE_ALLOWED = FALSE THEN
    BLOCK_LOCAL = TRUE  // BLOQUEAR comando
    CMD_OPEN_QT1 = FALSE
END_IF
```

---

### 3.5 FB_OUTPUTS (Pilotos y Alarmas)

**Archivo:** `05_FB_OUTPUTS.scl`

**Responsabilidades:**
1. Activar pilotos LED de estado (ON_GRID, ON_GD, TRANSFER, FAULT, SHED)
2. Gestionar bocina y baliza de alarma
3. Consolidar señales para HMI

**Salidas Físicas (DO):**
| Señal | Estado | Descripción |
|-------|--------|-------------|
| `DO_PILOT_ON_GRID` | Verde fijo | Operando con red (QT1 cerrado) |
| `DO_PILOT_ON_GD` | Amarillo fijo | Operando con GD (QG1 cerrado) |
| `DO_PILOT_TRANSFER` | Amarillo parpadeante 500ms | En proceso transferencia |
| `DO_PILOT_FAULT` | Rojo fijo | Falla - lockout activo |
| `DO_PILOT_SHED` | Amarillo fijo | Deslastre activo |
| `DO_ALARM_HORN` | ON/OFF | Bocina (silencia con ACK) |
| `DO_ALARM_BEACON` | Rojo parpadeante | Baliza (no silencia con ACK) |

**Gestión Alarmas:**
```
IF IS_FAULT = TRUE OR ALM_INTERLOCK_VIOLATION = TRUE THEN
    HMI_ALARM_ACTIVE = TRUE
    HMI_ALARM_TEXT = "Descripción falla según FAULT_CODE"
    
    DO_ALARM_HORN = TRUE  // Hasta que operador presione ACK_ALARM
    DO_ALARM_BEACON = TRUE  // Mientras alarma activa
END_IF
```

---

### 3.6 FB_MTZ_DRIVER (Driver Modbus MTZ/NSX)

**Archivo:** `07_FB_MTZ_DRIVER.scl`

**Responsabilidades:**
1. Lectura estado: registros 32000 (calidad) y 32001 (OF/SD/PF)
2. Escritura comandos: buffer 8000-8019 + polling 8020-8021
3. Máquina de estados: IDLE → BUILD → WRITE → POLL → CONFIRM → DONE/ERROR
4. Gestión password nivel 3 (típicamente "3333")

**Protocolo Command Interface (Schneider):**

**Paso 1: Preparar buffer 8000-8019**
| Registro | Valor | Descripción |
|----------|-------|-------------|
| 8000 | 904 / 905 / 906 | Código comando (Open/Close/Reset) |
| 8001 | 10 | Constante protocolo |
| 8002 | 5377 (0x1501) | Constante protocolo |
| 8003 | 1 | Requiere password (1=YES) |
| 8004 | 0x3333 | Password ASCII "33" |
| 8005 | 0x3333 | Password ASCII "33" |
| 8006-8016 | 0 | Reservados |
| 8017 | 8019 | Constante |
| 8018 | 8020 | Constante |
| 8019 | 8021 | Constante |

**Paso 2: Escribir 20 registros (FC16 Write Multiple Registers)**
```
MB_CLIENT.WRITE_MULTIPLE_REGISTERS(
    SlaveID := SLAVE_ID,
    StartAddress := 8000,
    Count := 20,
    Data := cmdBuffer[0..19]
)
```

**Paso 3: Polling respuesta (leer 8020-8021)**
```
WHILE TRUE DO
    MB_CLIENT.READ_HOLDING_REGISTERS(
        SlaveID := SLAVE_ID,
        StartAddress := 8020,
        Count := 2,
        Data := responseBuffer[0..1]
    )
    
    IF responseBuffer[1] = 0x0003 THEN
        // Busy, continuar polling
        WAIT
    ELSIF responseBuffer[1].LSB = 0x0000 THEN
        // OK, comando aceptado
        EXIT
    ELSIF responseBuffer[1].LSB = 0x0001 THEN
        // Already in requested state (código benigno)
        EXIT
    ELSE
        // Error
        ERROR_CODE = responseBuffer[1]
        EXIT ERROR
    END_IF
    
    IF Timeout > 5s THEN
        ERROR_CODE = 201  // Timeout poll
        EXIT ERROR
    END_IF
END_WHILE
```

**Paso 4: Confirmar estado físico (leer 32000-32001)**
```
MB_CLIENT.READ_HOLDING_REGISTERS(
    SlaveID := SLAVE_ID,
    StartAddress := 32000,
    Count := 2,
    Data := [statusReg32000, statusReg32001]
)

// Decodificar bits registro 32001
OF = statusReg32001.Bit0  // Open Feedback (1=abierto, 0=cerrado)
SD = statusReg32001.Bit1  // Shunt trip (1=disparado)
PF = statusReg32001.Bit2  // Pre-fault / Ready to close

IF OF = 1 THEN
    CB_STATE = 0  // Abierto
ELSE
    CB_STATE = 1  // Cerrado
END_IF
```

---

## 4. DATA BLOCKS

### 4.1 DB_GLOBAL_STATUS (Estados Consolidados)

**Archivo:** `08_DB_GLOBAL_STATUS.scl`

Contiene todos los estados y señales consolidados del sistema, accesibles por todos los FBs y el HMI.

**Secciones:**
1. **Modo operativo:** `MODE_AUTO`, `MODE_MANUAL`, `DIAG_MODE_VALID`
2. **Permisos LOCAL/REMOTO:** `QT1_REMOTE_ALLOWED`, `QG1_REMOTE_ALLOWED`, etc.
3. **Requests manuales:** `REQ_MAN_QT1_OPEN`, `REQ_MAN_QT1_CLOSE`, etc.
4. **Señales GD:** `GD_READY`, `GD_RUNNING`, `GD_ALARM`
5. **Estados interruptores:** `QT1_STATE`, `QG1_STATE`, `QG2_STATE`, `FEEDER_STATE[1..18]`
6. **Mediciones eléctricas:** `GRID_V_L1L2`, `GRID_FREQ`, `GD_LoadPct`, `TR_LoadPct`, etc.
7. **Estado SCMTA:** `SCMTA_STATE`, `IS_ON_GRID`, `IS_ON_GD`, `IS_FAULT`, `FAULT_CODE`
8. **Estado deslastre:** `SHED_ACTIVE`, `SHED_STEP`, `FEEDERS_SHED`
9. **Alarmas:** `ALM_INTERLOCK_VIOLATION`, `HMI_ALARM_ACTIVE`, `HMI_ALARM_TEXT`
10. **Comunicaciones:** `COMM_OK`, `COMM_ERRORS`, `ACTIVE_DEVICE`
11. **Timestamps:** `SYSTEM_UPTIME`, `TRANSFER_COUNT`, `LAST_FAULT_TIMESTAMP`

**Tipo:** NON_RETAIN (se pierde al apagar PLC, se reinicializa en OB100 startup si necesario)

---

### 4.2 DB_PARAMS (Parámetros Configurables)

**Archivo:** `09_DB_PARAMS.scl`

Contiene todos los parámetros configurables del sistema, modificables desde HMI con nivel ADMIN.

**Secciones:**
1. **Parámetros tensión/frecuencia red:**
   - `V_NOM = 380.0` [V]
   - `V_MIN_PCT = 85.0` [%]
   - `V_MAX_PCT = 110.0` [%]
   - `FREQ_MIN = 49.0` [Hz]
   - `FREQ_MAX = 51.0` [Hz]

2. **Tiempos transferencia Red→GD:**
   - `T_OPEN_QT1 = T#2s`
   - `T_START_GD_DELAY = T#3s`
   - `T_GD_READY_TIMEOUT = T#30s`
   - `MAX_GD_START_RETRIES = 2` (reintentos adicionales antes de lockout)
   - `T_GD_STABILIZATION = T#5s`
   - `T_CLOSE_QG1 = T#2s`
   - `T_GRID_FAIL_FILTER = T#2s`

3. **Tiempos retorno GD→Red:**
   - `T_GRID_STABLE = T#120s`
   - `T_OPEN_QG1 = T#2s`
   - `T_CLOSE_QT1 = T#2s`
   - `T_GD_COOLDOWN = T#60s`

4. **Parámetros deslastre:**
   - `SHED_ON = 90.0` [%] (umbral deslastre GD)
   - `TR_SHED_ON = 95.0` [%] (umbral deslastre trafo)
   - `SHED_OFF = 70.0` [%] (histéresis)
   - `T_SHED_STEP = T#5s`
   - `T_RECONNECT_STEP = T#5s`

5. **Arrays deslastre:**
   - `SHED_ORDER[1..18]`: orden de corte
   - `RECONNECT_ORDER[1..18]`: orden de reenganche
   - `SHED_ENABLE[1..18]`: habilitar/deshabilitar por feeder

6. **Configuración Modbus:**
   - `SLAVE_ID_QT1 = 1`
   - `SLAVE_ID_QG1 = 2`
   - `SLAVE_ID_QG2 = 3`
   - `SLAVE_ID_FEEDER[1..18]` (direcciones NSX)
   - `PASSWORD_MTZ_QT1 = "3333"`
   - `T_MODBUS_POLL_TIMEOUT = T#5s`

7. **Calibración GD/TR:**
   - `GD_POWER_NOMINAL = 1000.0` [kW]
   - `TR_POWER_NOMINAL = 1000.0` [kVA]

8. **Flags sistema:**
   - `ENABLE_SCMTA = TRUE`
   - `ENABLE_SHED = TRUE`
   - `ENABLE_AUTO_RETURN = TRUE`

**Tipo:** RETAIN (valores se mantienen después de apagar PLC)

---

## 5. MÁQUINA DE ESTADOS SCMTA

### 5.1 Diagrama de Estados

Ver archivo `11_UML_SCMTA_StateMachine.puml` para diagrama PlantUML completo.

### 5.2 Secuencia Transferencia Red→GD

```
1. NORMAL_ON_GRID (QT1 cerrado)
    ↓ GRID_FAIL detectado (2s filtro)
    
2. GRID_FAIL_DETECTED
    ↓
    
3. OPEN_QT1 (REQ_SCMTA_OPEN_QT1 = TRUE)
    ↓ QT1 abierto confirmado (o timeout 2s → FAULT)
    
4. START_GD_DELAY (esperar 3s seguridad)
    ↓
    
5. START_GD (DO_GD_START = TRUE)
    ↓ GD_RUNNING = TRUE (o GD_ALARM → FAULT)
    
6. WAIT_GD_READY
    ↓ GD_READY = TRUE y estable 5s (o timeout 30s → FAULT)
    
7. CLOSE_QG1 (REQ_SCMTA_CLOSE_QG1 = TRUE + enclavamiento)
    ↓ QG1 cerrado confirmado (o timeout 2s → FAULT)
    
8. ON_GD (QG1 cerrado, operación con GD)
```

**Tiempo total típico Red→GD:** ~15-20 segundos (sin retardos por fallas)

### 5.3 Secuencia Retorno GD→Red

```
8. ON_GD
    ↓ GRID_OK detectado (2s filtro)
    
9. GRID_RETURN_DETECTED
    ↓
    
10. WAIT_GRID_STABLE (esperar 120s confirmación)
    ↓ Si GRID_FAIL durante espera → volver a ON_GD
    ↓ Si 120s OK
    
11. OPEN_QG1 (REQ_SCMTA_OPEN_QG1 = TRUE)
    ↓ QG1 abierto confirmado (o timeout 2s → FAULT)
    
12. CLOSE_QT1 (REQ_SCMTA_CLOSE_QT1 = TRUE + enclavamiento)
    ↓ QT1 cerrado confirmado (o timeout 2s → FAULT)
    
13. GD_COOLDOWN (esperar 60s y DO_GD_STOP = TRUE)
    ↓
    
1. NORMAL_ON_GRID (retorno completo)
```

**Tiempo total retorno GD→Red:** ~124 segundos (mayoritariamente espera estabilidad)

---

## 6. PROTOCOLO MODBUS RTU

### 6.1 Configuración Bus

- **Protocolo:** Modbus RTU
- **Baudrate:** 9600 / 19200 bps (según configuración equipos)
- **Paridad:** Even / None
- **Stop bits:** 1
- **Timeout:** 1000 ms
- **Máximo reintentos:** 3

### 6.2 Equipos en Bus

| Equipo | Slave ID | Descripción |
|--------|----------|-------------|
| QT1 | 1 | Masterpact MTZ1 (Interruptor RED) |
| QG1 | 2 | Masterpact MTZ2 (Interruptor GD01) |
| QG2 | 3 | Masterpact MTZ (Interruptor GD02 futuro) |
| PM5350 Grid | 10 | Medidor entrada RED |
| PM5350 GD | 11 | Medidor salida GD |
| PM5350 TR | 12 | Medidor salida transformador |
| NSX Feeder 1-18 | 20-37 | Compact NSX con Micrologic (salidas) |

### 6.3 Registros MTZ/NSX (Micrologic)

#### Lectura Estado
| Registro | Tipo | Descripción |
|----------|------|-------------|
| 32000 | Holding | Calidad medición (bit 0: 1=OK) |
| 32001 | Holding | Estado interruptor (OF/SD/PF) |

**Decodificación 32001:**
- Bit 0 (OF): Open Feedback (1=abierto, 0=cerrado)
- Bit 1 (SD): Shunt trip (1=disparado)
- Bit 2 (PF): Pre-fault / Ready to close (1=listo)

#### Escritura Comandos (Command Interface)
| Registro | Función | Descripción |
|----------|---------|-------------|
| 8000-8019 | FC16 Write Multiple | Buffer comando (ver sección 3.6) |
| 8020-8021 | FC3 Read Holding | Respuesta comando |

### 6.4 Registros PM5350 (Medidor PowerLogic)

Ver archivo `TGBT_Config - pm5330.pdf` para mapeo completo.

**Registros principales:**
| Registro | Tipo | Unidad | Descripción |
|----------|------|--------|-------------|
| 3000 | Float | V | Tensión L1-L2 |
| 3002 | Float | V | Tensión L2-L3 |
| 3004 | Float | V | Tensión L3-L1 |
| 3020 | Float | A | Corriente L1 |
| 3022 | Float | A | Corriente L2 |
| 3024 | Float | A | Corriente L3 |
| 3050 | Float | Hz | Frecuencia |
| 3060 | Float | kW | Potencia activa total |
| 3070 | Float | kVAr | Potencia reactiva total |
| 3080 | Float | kVA | Potencia aparente total |
| 3090 | Float | - | Factor de potencia |
| 3200 | Float | kWh | Energía activa acumulada |

**Nota:** Registros Float son de 32 bits (2 registros Modbus consecutivos, formato IEEE754).

---

## 7. DESLASTRE Y REENGANCHE

### 7.1 Criterios de Deslastre

El deslastre opera en **6 modos** según la situación:

| Modo | Condición de Activación |
|------|------------------------|
| IDLE (0) | Sin condición de deslastre |
| GRID_SHED (1) | `IS_ON_GRID` AND `TR_LoadPct > TR_SHED_ON` (sobrecarga trafo) |
| GD_INITIAL_SHED (2) | Al entrar a GD, cortar feeders no-esenciales (`FEEDER_ESSENTIAL = FALSE`) |
| GD_RECONNECT (3) | En GD, carga permite reconectar feeders (`GD_LoadPct < RECONNECT_PCT`) |
| GD_REACTIVE_SHED (4) | En GD, `GD_LoadPct > SHED_ON_PCT` (sobrecarga reactiva) |
| GRID_RECONNECT (5) | Al retornar a RED, reconectar todos los feeders deslastrados |

**Requisitos comunes:**
1. Modo automático (`MODE_AUTO = TRUE`)
2. Condición sostenida por 2 segundos (filtro anti-bouncing)
3. Feeders esenciales (`FEEDER_ESSENTIAL = TRUE`) protegidos en modos iniciales

### 7.2 Configuración Prioridades

**Ejemplo configuración típica:**
```scl
// DB_PARAMS.SHED_ORDER (orden de corte)
SHED_ORDER[1] := 5;   // Feeder 5: Climatización (400A)
SHED_ORDER[2] := 12;  // Feeder 12: Bombas secundarias (320A)
SHED_ORDER[3] := 3;   // Feeder 3: Iluminación no esencial (250A)
SHED_ORDER[4] := 8;   // Feeder 8: Enchufes oficinas (160A)
// ... continuar según relevamiento

// DB_PARAMS.SHED_ENABLE (habilitar deslastre por feeder)
SHED_ENABLE[1] := FALSE;  // Feeder 1: Esencial (UPS, servidores)
SHED_ENABLE[2] := FALSE;  // Feeder 2: Esencial (iluminación emergencia)
SHED_ENABLE[3] := TRUE;   // Feeder 3: No esencial (deslastre permitido)
SHED_ENABLE[5] := TRUE;   // Feeder 5: No esencial (climatización)
// ... etc.
```

### 7.3 Procedimiento Modificación Prioridades (HMI)

1. Ingresar al HMI con **usuario ADMIN** (nivel 10)
2. Navegar a **Configuración → Deslastre → Prioridades**
3. Modificar array `SHED_ORDER`:
   - Posición 1 = feeder con mayor prioridad de corte (típicamente mayor amperaje)
   - Posición 18 = feeder con menor prioridad
4. Modificar array `SHED_ENABLE`:
   - TRUE = permite deslastre
   - FALSE = excluir (carga esencial, nunca cortar)
5. Guardar cambios (escritura a DB_PARAMS RETAIN)
6. **Probar secuencia** en modo manual antes de habilitar AUTO

---

## 8. ENCLAVAMIENTO DE SEGURIDAD

### 8.1 Regla Absoluta

**NUNCA puede haber más de un interruptor de fuente cerrado simultáneamente:**
- QT1 (RED)
- QG1 (GD01)
- QG2 (GD02)

### 8.2 Implementación Fail-Safe

**Antes de cerrar cualquier interruptor de fuente:**
```ladder
IF REQ_CLOSE_QT1 = TRUE THEN
    // Verificar que QG1 y QG2 estén ABIERTOS (estado 0)
    IF (QG1_STATE = 0) AND (QG2_STATE = 0) THEN
        CMD_CLOSE_QT1 := TRUE  // OK, enclavamiento verificado
    ELSE
        BLOCK_INTERLOCK := TRUE  // BLOQUEAR comando
        ALM_INTERLOCK_VIOLATION := TRUE  // ALARMA
    END_IF
END_IF
```

**Detección violación (múltiples fuentes cerradas):**
```ladder
IF (QT1_STATE = 1) AND (QG1_STATE = 1) THEN
    ALM_INTERLOCK_VIOLATION := TRUE  // ALARMA CRÍTICA
    SCMTA_STATE := FAULT_LOCKOUT
    FAULT_CODE := 107
END_IF
```

### 8.3 Acciones ante Violación

1. **Alarma sonora y visual** (bocina + baliza roja)
2. **Lockout inmediato** (estado FAULT_LOCKOUT)
3. **Bloqueo de comandos** (ARBITER no permite nuevos comandos)
4. **Registro evento** en HMI con timestamp
5. **Requiere intervención operador:**
   - Verificar estado físico de interruptores
   - Identificar causa (falla comunicación, falla mecánica, etc.)
   - Corregir estado manualmente (selectores LOCAL)
   - Presionar RESET_FAULT en HMI

---

## 9. CONFIGURACIÓN Y PARÁMETROS

### 9.1 Parámetros Críticos (No Modificar Sin Autorización)

| Parámetro | Valor Default | Justificación |
|-----------|---------------|---------------|
| `T_START_GD_DELAY` | 3s | Tiempo seguridad apertura QT1 antes arranque GD |
| `T_GRID_STABLE` | 120s | Estabilidad red antes retorno (norma IEEE 1547) |
| `T_GD_COOLDOWN` | 60s | Cooldown motor GD antes parada |
| `V_MIN_PCT` | 85% | Umbral subtensión según norma |
| `V_MAX_PCT` | 110% | Umbral sobretensión según norma |

### 9.2 Parámetros Ajustables en Campo

| Parámetro | Rango | Recomendación |
|-----------|-------|---------------|
| `SHED_ON` | 80-95% | Típicamente 90% carga GD |
| `TR_SHED_ON` | 90-100% | Típicamente 95% carga trafo (contingencia) |
| `T_SHED_STEP` | 3-10s | 3-5s recomendado (escalonado suave) |
| `T_RECONNECT_STEP` | 3-10s | 3-5s recomendado (evitar inrush simultáneo) |

### 9.3 Calibración Carga GD/Transformador

Para cálculo correcto de `GD_LoadPct` y `TR_LoadPct`, verificar:
```scl
// DB_PARAMS
GD_POWER_NOMINAL := 1000.0;  // [kW] (1000 kVA @ PF=1)
GD_CURRENT_NOMINAL := 1520.0;  // [A] calculado: 1000 kVA / (√3 * 0.38 kV)

TR_POWER_NOMINAL := 1000.0;  // [kVA]
TR_CURRENT_NOMINAL := 1520.0;  // [A]
```

Luego en OB1:
```scl
GD_LoadPct := (GD_P_TOTAL / GD_POWER_NOMINAL) * 100.0;
TR_LoadPct := (TR_P_TOTAL / TR_POWER_NOMINAL) * 100.0;
```

---

## 10. TESTING Y COMISIONAMIENTO

### 10.1 Checklist Pre-Comisionamiento

**Hardware:**
- [ ] Verificar cableado PLC (entradas DI, salidas DO, comunicación Modbus)
- [ ] Verificar alimentación 24VDC (fuente redundante recomendada)
- [ ] Verificar terminación bus Modbus RTU (resistencias 120Ω en extremos)
- [ ] Verificar direcciones Modbus de todos los equipos (sin duplicados)
- [ ] Verificar selectores Local/Remoto en posición REMOTO (para test)
- [ ] Verificar contactos auxiliares GD (READY, RUNNING, ALARM)

**Software:**
- [ ] Cargar programa completo en PLC (todos los FBs + DBs + OB1)
- [ ] Verificar direcciones físicas E/S (mapeo %I, %Q según hardware real)
- [ ] Configurar parámetros DB_PARAMS según instalación
- [ ] Configurar arrays SHED_ORDER/ENABLE según relevamiento de cargas
- [ ] Cargar configuración Modbus (baudrate, paridad, timeouts)

### 10.2 Secuencia de Tests

**Test 1: Entradas/Salidas Físicas**
1. Verificar lectura selector AUTO/MANUAL (DI_SYS_AUTO)
2. Verificar lectura selectores LOCAL/REMOTO (todos los interruptores)
3. Presionar pulsadores Open/Close y verificar `REQ_MAN_*` en HMI
4. Verificar activación pilotos LED (forzar estados en HMI modo test)

**Test 2: Comunicación Modbus**
1. En modo MANUAL, verificar lectura estados QT1/QG1/QG2 (32001)
2. Verificar lectura mediciones PM5350 (tensiones, corrientes, potencia)
3. Verificar calidad comunicación (COMM_OK = TRUE, COMM_ERRORS = 0)

**Test 3: Comandos Modbus (LOCAL)**
1. Poner QT1 en LOCAL, intentar comando desde HMI → debe bloquearse (BLOCK_LOCAL = TRUE)
2. Poner QT1 en REMOTO, enviar comando Open → verificar ejecución OK

**Test 4: Enclavamiento**
1. Con QT1 cerrado, intentar cerrar QG1 desde HMI manual
   - **Resultado esperado:** BLOCK_INTERLOCK = TRUE, comando rechazado
2. Abrir QT1, luego cerrar QG1 → debe permitir
3. Forzar (en test) QT1=cerrado Y QG1=cerrado simultáneamente
   - **Resultado esperado:** ALM_INTERLOCK_VIOLATION = TRUE, FAULT_LOCKOUT

**Test 5: Transferencia Red→GD (Simulada)**
1. Poner sistema en AUTO con QT1 cerrado (NORMAL_ON_GRID)
2. Simular falta de red (forzar GRID_FAIL = TRUE en test, o desconectar medidor PM5350)
3. Verificar secuencia completa:
   - Estado 2: GRID_FAIL_DETECTED
   - Estado 3: OPEN_QT1 (verificar comando enviado)
   - Estado 4: START_GD_DELAY (3s)
   - Estado 5: START_GD (verificar DO_GD_START = TRUE)
   - Estado 6: WAIT_GD_READY (simular GD_READY = TRUE después de 10s)
   - Estado 7: CLOSE_QG1 (verificar enclavamiento OK)
   - Estado 8: ON_GD
4. Verificar tiempo total transferencia (~15-20s)

**Test 6: Retorno GD→Red (Simulado)**
1. Desde estado ON_GD, simular retorno red (GRID_OK = TRUE)
2. Verificar estado 10: WAIT_GRID_STABLE (debe esperar 120s)
3. Durante espera, simular rebote red (GRID_FAIL = TRUE momentáneo)
   - **Resultado esperado:** volver a ON_GD, reiniciar timer 120s
4. Con red estable 120s, verificar secuencia:
   - Estado 11: OPEN_QG1
   - Estado 12: CLOSE_QT1 (verificar enclavamiento)
   - Estado 13: GD_COOLDOWN (60s, luego DO_GD_STOP = TRUE)
   - Estado 1: NORMAL_ON_GRID

**Test 7: Deslastre (Simulado)**
1. Sistema en ON_GD, forzar GD_LoadPct = 95%
2. Verificar activación deslastre después de filtro 2s (SHED_MODE = 4 GD_REACTIVE_SHED)
3. Verificar corte escalonado según SHED_ORDER (5s entre pasos)
4. Verificar solo se cortan feeders con SHED_ENABLE = TRUE y FEEDER_ESSENTIAL = FALSE
5. Reducir carga a 65%, verificar cancelación deslastre (histéresis)

**Test 7b: Deslastre RED (Simulado)**
1. Sistema en NORMAL_ON_GRID, forzar TR_LoadPct = 96%
2. Verificar SHED_MODE = 1 (GRID_SHED)
3. Verificar corte escalonado de feeders no-esenciales

**Test 7c: Failover GD1→GD2 (Simulado)**
1. Sistema en ON_GD (estado 8), forzar GD1_ALARM = TRUE
2. Verificar secuencia: 8→15→16→17→18→19 (START_GD2_DELAY→ON_GD2)
3. Verificar QG1 abre, QG2 cierra (enclavamiento)
4. Verificar GD2 arranca correctamente

**Test 7d: Failover GD2→GD1 (Simulado)**
1. Sistema en ON_GD2 (estado 19), forzar GD2_ALARM = TRUE
2. Verificar secuencia: 19→20→4→5→6→7→8 (vuelve a GD1)
3. Verificar QG2 abre, QG1 cierra

**Test 8: Reenganche**
1. Con feeders deslastrados (abiertos), retornar a red
2. Verificar reenganche escalonado según RECONNECT_ORDER (5s entre pasos)
3. Verificar todos los feeders vuelven a estado cerrado

**Test 9: Fault Lockout**
1. Simular timeout (ej. QT1 no responde a comando Open en 2s)
   - **Resultado esperado:** FAULT_CODE = 101, estado FAULT_LOCKOUT
2. Verificar alarma sonora/visual activa
3. Presionar RESET_FAULT en HMI
   - **Resultado esperado:** volver a estado seguro (NORMAL_ON_GRID o ON_GD según GRID_OK)

**Test 10: Modo MANUAL**
1. Poner selector en MANUAL
2. Verificar SCMTA no ejecuta secuencias automáticas
3. Presionar pulsador PB_OPEN QT1 → verificar comando enviado
4. Verificar deslastre deshabilitado en modo MANUAL

### 10.3 Criterios de Aceptación

- [ ] Todas las entradas DI leen correctamente (debounce 50ms OK)
- [ ] Todas las salidas DO actúan correctamente (pilotos, bocina, marcha GD)
- [ ] Comunicación Modbus estable (tasa error <1%, sin timeouts)
- [ ] Enclavamiento fuente única verificado (imposible cerrar 2 fuentes)
- [ ] Transferencia Red→GD completa en <25s (sin alarmas GD)
- [ ] Retorno GD→Red completa en ~124s (con espera estabilidad)
- [ ] Deslastre reduce carga GD según secuencia configurada
- [ ] Reenganche restaura todos los feeders habilitados
- [ ] Modo MANUAL inhibe secuencias automáticas
- [ ] Selectores LOCAL bloquean comandos PLC
- [ ] Fault lockout funciona correctamente (requiere reset manual)
- [ ] HMI muestra estados, alarmas y parámetros correctamente

---

## 11. TROUBLESHOOTING

### 11.1 Problemas Comunes

**Problema: Sistema no arranca GD (stuck en estado 5 START_GD)**
- **Causa:** GD no arranca físicamente, o señal GD_RUNNING no llega al PLC
- **Verificar:**
  1. Salida DO_GD_START activa físicamente (medir continuidad relé)
  2. Contacto NA en bornera GD cerrado
  3. Entrada DI_GD_RUNNING cableada correctamente
  4. GD en modo AUTO (selector local del GD)
- **Solución:** Corregir cableado o modo GD. Si GD no arranca, verificar alarma GD física.

**Problema: Timeout CLOSE_QG1 (FAULT_CODE = 103)**
- **Causa:** QG1 no cierra, o feedback Modbus no llega
- **Verificar:**
  1. Comunicación Modbus con QG1 (leer 32001, verificar respuesta)
  2. Comando Modbus enviado correctamente (8000-8019)
  3. Respuesta 8021 = 0x0000 (OK) o código error
  4. Estado físico QG1 (¿bobina de cierre activada?)
- **Solución:**
  - Si error Modbus: verificar cableado bus, dirección slave, password
  - Si QG1 físicamente no cierra: verificar alimentación bobina, bloqueo mecánico

**Problema: Enclavamiento bloquea comandos (BLOCK_INTERLOCK = TRUE)**
- **Causa:** Estado de otro interruptor no es ABIERTO (0)
- **Verificar:**
  1. Leer estados QT1/QG1/QG2 en HMI (¿alguno en estado 2=Desconocido?)
  2. Si estado desconocido: problema comunicación Modbus con ese interruptor
  3. Verificar registro 32000 (calidad medición)
- **Solución:**
  - Poner interruptor en LOCAL y abrir manualmente
  - Verificar comunicación Modbus
  - Una vez abierto, volver a REMOTO

**Problema: Deslastre no actúa (carga GD > 90%, SHED_ACTIVE = FALSE)**
- **Causa:** Condición no cumplida o filtro no transcurrido
- **Verificar:**
  1. ¿IS_ON_GD = TRUE? (debe estar operando con GD)
  2. ¿MODE_AUTO = TRUE? (debe estar en automático)
  3. ¿GD_LoadPct > SHED_ON? (verificar cálculo LoadPct)
  4. ¿Filtro 2s transcurrido? (ver DIAG_LOAD_OVER_LIMIT)
  5. ¿Algún feeder con SHED_ENABLE = TRUE y FEEDER_ESSENTIAL = FALSE?
  6. ¿SHED_MODE correcto? (verificar valor actual 0-5)
- **Solución:**
  - Verificar medición GD_P_TOTAL (Modbus PM5350 GD)
  - Verificar GD_POWER_NOMINAL correcto en DB_PARAMS
  - Habilitar al menos un feeder en SHED_ENABLE con FEEDER_ESSENTIAL = FALSE

**Problema: Red no retorna después de 120s (stuck en WAIT_GRID_STABLE)**
- **Causa:** Red rebota durante ventana de 120s
- **Verificar:**
  1. Tensiones/frecuencia red estables (ver medidor PM5350)
  2. ¿GRID_FAIL = FALSE sostenido? (si rebota, timer reinicia)
  3. Calidad medición PM5350 (GRID_MEASUREMENT_OK = TRUE)
- **Solución:**
  - Esperar estabilidad real de red (puede tomar >120s si hay problemas)
  - Si red inestable permanentemente: reducir T_GRID_STABLE (no recomendado)

**Problema: Comunicación Modbus inestable (COMM_ERRORS incrementa)**
- **Causa:** Interferencia, baudrate incorrecto, cableado defectuoso
- **Verificar:**
  1. Cableado bus Modbus (par trenzado apantallado, máx 1000m)
  2. Terminación 120Ω en extremos del bus (solo extremos, no en equipos intermedios)
  3. Baudrate igual en todos los equipos (típicamente 9600 o 19200)
  4. Paridad configurada igual (Even/None)
  5. Direcciones Modbus sin duplicados
  6. Longitud cable <1000m, derivaciones cortas (<20m)
- **Solución:**
  - Revisar cableado físico
  - Reducir baudrate si interferencia (9600 más robusto que 19200)
  - Agregar ferrites en cable si EMI alto

---

## 12. MANTENIMIENTO

### 12.1 Mantenimiento Preventivo (Trimestral)

**PLC:**
- [ ] Verificar indicadores LED PLC (RUN, ERROR, COMM)
- [ ] Limpiar ventilación PLC (aire comprimido sin contacto)
- [ ] Verificar torque bornes E/S (apretar si necesario)
- [ ] Backup programa PLC y parámetros DB_PARAMS

**Comunicaciones:**
- [ ] Verificar COMM_ERRORS en HMI (debe ser 0 o <10/día)
- [ ] Verificar conectores bus Modbus (corrosión, apriete)
- [ ] Medir resistencia terminación (debe ser ~60Ω extremo-extremo)

**Interruptores (MTZ/NSX):**
- [ ] Verificar comunicación Modbus con cada interruptor (leer 32000-32001)
- [ ] Verificar passwords (no cambiar sin autorización)
- [ ] Test manual Open/Close (modo LOCAL) de cada interruptor
- [ ] Verificar contactos auxiliares (OF, SD, PF) con multímetro

**Grupo Diésel:**
- [ ] Test marcha GD manual (modo LOCAL del GD)
- [ ] Verificar señales GD_READY, GD_RUNNING, GD_ALARM al PLC
- [ ] Verificar salida DO_GD_START actúa correctamente
- [ ] Test transferencia completa Red→GD→Red en horario programado

**Medidores PM5350:**
- [ ] Verificar lecturas medidores (comparar con instrumentos portátiles)
- [ ] Verificar cálculo LoadPct (vs. amperímetro pinza)
- [ ] Limpiar pantalla medidor
- [ ] Verificar parámetros configuración (CT ratio, PT ratio)

### 12.2 Mantenimiento Correctivo

**Ante falla PLC:**
1. Verificar alimentación 24VDC (medir tensión bornes)
2. Verificar LED ERROR encendido → consultar buffer diagnóstico (SFC51)
3. Reemplazar PLC (usar backup programa)
4. Recargar programa y parámetros RETAIN desde backup

**Ante falla comunicación Modbus:**
1. Aislar equipo problemático (desconectar del bus)
2. Verificar comunicación resto de equipos
3. Reemplazar equipo o revisar configuración Modbus interna

**Ante falla interruptor (no responde a comandos):**
1. Poner en LOCAL y operar manualmente (verificar funcionamiento mecánico)
2. Verificar alimentación auxiliar interruptor (24VDC o 220VAC según modelo)
3. Verificar comunicación Modbus (leer 32000-32001)
4. Si persiste: llamar servicio técnico Schneider

### 12.3 Actualizaciones Software

**Procedimiento actualización programa PLC:**
1. Realizar backup completo (programa + DB_PARAMS RETAIN)
2. Planificar ventana de mantenimiento (parada programada)
3. Poner sistema en MANUAL
4. Cargar nueva versión programa
5. Verificar DB_PARAMS se mantienen (RETAIN)
6. Ejecutar tests de comisionamiento (sección 10.2)
7. Documentar cambios en log de revisiones

**Control de versiones:**
- Mantener registro de versiones en archivo `VERSION_HISTORY.md`
- Formato: `vX.Y.Z (YYYY-MM-DD): Descripción cambios`
- Ejemplo:
  ```
  v1.0.0 (2026-02-04): Versión inicial completa
  v1.0.1 (2026-03-15): Fix timeout GD_READY (30s → 45s)
  v1.1.0 (2026-04-20): Agregar soporte QG2 (expansión GD02)
  ```

---

## 13. ARCHIVOS DEL PROYECTO

### 13.1 Código Fuente PLC

| Archivo | Descripción |
|---------|-------------|
| `01_FB_IO_NORMALIZE.scl` | Function Block normalización E/S |
| `01_FB_IO_NORMALIZE_LADDER.md` | Documentación Ladder FB_IO_NORMALIZE |
| `02_FB_SCMTA.scl` | Function Block máquina estados transferencia |
| `03_FB_SHED.scl` | Function Block deslastre y reenganche |
| `04_FB_CMD_ARBITER.scl` | Function Block árbitro comandos + enclavamiento |
| `05_FB_OUTPUTS.scl` | Function Block pilotos y alarmas |
| `06_FB_MODBUS_MANAGER.scl` | Function Block scheduler Modbus |
| `07_FB_MTZ_DRIVER.scl` | Function Block driver MTZ/NSX |
| `08_DB_GLOBAL_STATUS.scl` | Data Block estados consolidados |
| `09_DB_PARAMS.scl` | Data Block parámetros configurables (RETAIN) |
| `10_OB1_MAIN.scl` | Organization Block principal (Main) |

### 13.2 Diagramas UML (PlantUML)

| Archivo | Descripción |
|---------|-------------|
| `11_UML_SCMTA_StateMachine.puml` | Diagrama estados SCMTA (0-14 GD1) |
| `12_UML_MTZ_Driver_StateMachine.puml` | Diagrama estados driver MTZ |
| `13_UML_SHED_Activity.puml` | Diagrama actividad deslastre |
| `14_UML_SCMTA_GD2_StateMachine.puml` | Diagrama estados SCMTA con GD2/failover (15-20) |
| `15_UML_System_Architecture.puml` | Arquitectura completa del sistema |

### 13.3 Documentación Base (Fuentes Proyecto)

| Archivo | Descripción |
|---------|-------------|
| `TGBT_Config - listado de entradas y salidas.pdf` | Señales DI/DO, selectores, pulsadores |
| `TGBT_Config - listado de equipos.pdf` | Equipos con Modbus RTU |
| `TGBT_Config - pm5330.pdf` | Medición eléctrica PM5350 |
| `Escritura_MTZ.pdf` | Protocolo escritura Command Interface MTZ |
| `MTZ MANUAL.pdf` | Manual Masterpact MTZ1/MTZ2 |
| `NSX MANUAL.pdf` | Manual Compact NSX Micrologic |

### 13.4 Documentación Técnica

| Archivo | Descripción |
|---------|-------------|
| `README_SCMTA.md` | Este documento (documentación completa V3.0) |

---

## 14. CONTACTOS Y SOPORTE

### 14.1 Equipo Técnico

**Ingeniero de Automatización:**
- Responsable: (Completar con datos reales)
- Email: (Completar)
- Teléfono: (Completar)

**Electricista Senior:**
- Responsable: (Completar)
- Email: (Completar)
- Teléfono: (Completar)

### 14.2 Proveedores

**Schneider Electric (Interruptores MTZ/NSX):**
- Soporte técnico: www.schneider-electric.com/support
- Teléfono: (Consultar distribuidor local)

**Siemens (PLC TIA Portal):**
- Soporte técnico: www.siemens.com/automation/support
- Teléfono: (Consultar distribuidor local)

---

## 15. NOTAS FINALES

### 15.1 Decisiones de Diseño Clave

1. **Prioridad RED > GD:** Sistema siempre intenta retornar a red automáticamente (sin confirmación operador)
2. **Failover GD1↔GD2:** Si GD1 falla durante operación, conmutación automática a GD2 (y viceversa)
3. **Enclavamiento absoluto:** Implementado en FB_CMD_ARBITER (verificación antes de cada cierre)
4. **Fail-safe por defecto:** Si hay duda (estado desconocido, timeout), sistema va a FAULT_LOCKOUT
5. **Modbus sin redundancia:** Por ahora no hay watchdog complejo; a futuro agregar diagnóstico avanzado
6. **Arrays configurables:** SHED_ORDER/ENABLE/ESSENTIAL permiten ajustar prioridades desde HMI sin reprogramar PLC
7. **SHED V2.0 en RED y GD:** Deslastre opera tanto en sobrecarga de trafo (RED) como sobrecarga GD
8. **Tiempos conservadores:** T_GRID_STABLE=120s (puede parecer largo, pero evita rebotes y es norma IEEE 1547)

### 15.2 Trabajo Futuro (TODO)

- [ ] Implementar FB_MODBUS_MANAGER completo (cola de operaciones, time-slicing)
- [ ] Agregar drivers NSX individuales (1-18) con polling cíclico
- [ ] Implementar watchdog comunicación Modbus (timeout sin respuesta → COMM_ERROR)
- [ ] Agregar lectura medidor PM5350 completa (registros 3000-3200)
- [ ] Implementar log de eventos con timestamp (DB circular, 1000 eventos)
- [ ] Implementar pantalla HMI completa (Siemens WinCC o similar)
- [ ] Agregar trending histórico (carga GD, tensiones, transferencias)
- [ ] Implementar envío alarmas por email/SMS (vía gateway)
- [ ] Agregar soporte Modbus TCP (para SCADA remoto)

### 15.3 Revisiones Documento

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2026-02-04 | Sistema SCMTA | Versión inicial completa |

---

## 📄 FIN DE DOCUMENTACIÓN

**Total páginas:** ~30  
**Total archivos código:** 10 FBs + 2 DBs + 1 OB1 = **13 archivos SCL**  
**Total diagramas:** 5 PlantUML  
**Total estados SCMTA:** 21 (0-20)  
**Total modos SHED:** 6  
**Estado:** ✅ **PROYECTO V3.0 - GD2 FAILOVER Y SHED V2 IMPLEMENTADOS**

Para soporte técnico o consultas, consultar sección 14 (Contactos y Soporte).

---

**Nota:** Este documento y código fuente son propiedad del proyecto TGBT SCMTA. Distribución restringida a personal autorizado.
