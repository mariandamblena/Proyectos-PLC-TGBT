# Introducción Técnica para Nuevo Ingeniero – Proyecto TGBT / SCMTA (PLC + HMI)

**Proyecto**: Sistema de Control y Monitoreo de Transferencia Automática (SCMTA)  
**Fecha**: 10 de febrero de 2026  
**Versión**: 3.0  
**TIA Portal**: V18  
**PLC**: Siemens S7-1200  
**Lenguaje principal**: SCL (Structured Control Language)

---

## 1) Objetivo del Sistema

El PLC debe controlar y monitorear un **Tablero General de Baja Tensión (TGBT)** con transferencia automática de fuentes y gestión de cargas (deslastre), garantizando siempre el **enclavamiento de fuente única**. 

El sistema permite:
- ✅ Operación automática (secuencias SCMTA)
- ✅ Operación manual (local y remota)
- ✅ Supervisión y parametrización desde HMI
- ✅ Comunicación Modbus RTU con interruptores inteligentes

---

## 2) Fuentes, Interruptores y Regla de Seguridad Principal

### **2.1 Fuentes Disponibles**

1. **Red eléctrica externa** (prioritaria)
2. **Grupo diésel de emergencia GD01** – 1000 kVA
3. **Grupo diésel GD02** – Implementado en V3.0 con failover bidireccional GD1↔GD2

### **2.2 Interruptores Principales (Nomenclatura)**

| Código | Descripción | Equipo |
|--------|-------------|---------|
| **QT1** | Interruptor de Red | Schneider Masterpact MTZ1 |
| **QG1** | Interruptor de GD01 | Schneider Compact NSX Micrologic |
| **QG2** | Interruptor de GD02 (implementado V3.0) | Schneider Compact NSX Micrologic |

### **2.3 Regla Absoluta – Enclavamiento Fuente Única**

⚠️ **CRÍTICO**: Bajo toda circunstancia (AUTO/MANUAL/REMOTO), **nunca pueden estar cerrados simultáneamente más de uno entre**:

```
QT1, QG1, QG2
```

**Operación normal "ON GRID"**:
- QT1 = **CERRADO** ✅
- QG1 = **ABIERTO** ⛔
- QG2 = **ABIERTO** ⛔

**Implementación en código**: Ver `01_SCL/04_FB_CMD_ARBITER.scl`
- Verificación interlock antes de cada comando
- Alarma `ALARM_INTERLOCK_VIOLATION` si se viola

### **Dónde está la info**:

📄 **Contexto funcional**: [`03_DOCS/README_SCMTA.md`](README_SCMTA.md) - Sección "Reglas de Seguridad"  
📄 **Señales eléctricas**: [`06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf`](../06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf)  
📄 **Listado equipos**: [`06_CONFIG/TGBT_Config - listado de equipos.pdf`](../06_CONFIG/TGBT_Config - listado de equipos.pdf)

---

## 3) Modos de Operación y Relación con Hardware (DI/DO/HMI)

### **3.1 Modo del Sistema: Automático vs Manual**

| Modo | Comportamiento |
|------|----------------|
| **Automático** | PLC ejecuta secuencia completa de transferencia Red↔GD y deslastre automático |
| **Manual** | PLC NO ejecuta secuencias automáticas. Permite maniobras remotas controladas (si REMOTO habilitado). Siempre monitorea y visualiza |

**Fuente de verdad**: Selector físico `DI_SYS_AUTO` (entrada digital)

**Implementación**:
- Entrada: `%I0.0` (ejemplo - verificar con listado I/O)
- Normalización: `01_SCL/01_FB_IO_NORMALIZE.scl` → `MODE_AUTO` / `MODE_MANUAL`
- Uso: `01_SCL/02_FB_SCMTA.scl` - Input `MODE_AUTO`

```scl
// En FB_IO_NORMALIZE
MODE_AUTO := DI_SYS_AUTO;
MODE_MANUAL := NOT DI_SYS_AUTO;
```

**HMI puede**:
- ✅ Mostrar el modo actual
- ✅ Solicitar cambio (informativo)
- ❌ **NO** debe sobrepasar al selector físico (seguridad)

---

### **3.2 Autoridad de Mando: Local vs Remoto (por Tablero/Equipo)**

Existen **selectores LOCAL/REMOTO** por cada interruptor principal (QT1, QG1, QG2).

**Regla**:
- **Si está en LOCAL**: PLC NO debe mandar comandos de apertura/cierre por Modbus (solo monitoreo)
- **Si está en REMOTO**: PLC/HMI pueden mandar comandos (según permisos y enclavamientos)

**Implementación**:

| Señal | Entrada Física | Significado |
|-------|----------------|-------------|
| `DI_QT1_REMOTE_SEL` | `%I0.1` | TRUE = Remoto (PLC control), FALSE = Local |
| `DI_QG1_REMOTE_SEL` | `%I0.4` | TRUE = Remoto, FALSE = Local |
| `DI_QG2_REMOTE_SEL` | `%I1.0` | TRUE = Remoto, FALSE = Local |

Normalización en `01_SCL/01_FB_IO_NORMALIZE.scl`:

```scl
QT1_REMOTE_ALLOWED := DI_QT1_REMOTE_SEL;
QG1_REMOTE_ALLOWED := DI_QG1_REMOTE_SEL;
QG2_REMOTE_ALLOWED := DI_QG2_REMOTE_SEL;
```

Árbitro en `01_SCL/04_FB_CMD_ARBITER.scl`:

```scl
// Bloqueo si está en LOCAL
IF NOT QT1_REMOTE_ALLOWED THEN
    CMD_OPEN_QT1 := FALSE;
    CMD_CLOSE_QT1 := FALSE;
END_IF;
```

---

### **3.3 Pulsadores del Frente**

Los pulsadores **OPEN/CLOSE** del frente del tablero entran al PLC como entradas digitales (DI).

**En modo MANUAL + REMOTO**:
- El flanco del pulsador genera una **request (pulso 1 scan)**
- El PLC ejecuta la maniobra por Modbus

**Implementación**:

Pulsadores físicos → Debounce (50ms) → R_TRIG → Request pulso

```scl
// En FB_IO_NORMALIZE
// Debounce 50ms
tonDebounce_QT1_Open(IN := DI_QT1_PB_OPEN, PT := T#50ms);
QT1_PB_Open_DB := tonDebounce_QT1_Open.Q;

// R_TRIG manual (flanco 0→1)
rtQT1_Open := QT1_PB_Open_DB AND NOT memQT1_PB_Open;
REQ_MAN_QT1_OPEN := rtQT1_Open;
memQT1_PB_Open := QT1_PB_Open_DB;
```

**Resultado**: `REQ_MAN_QT1_OPEN` es un pulso de 1 scan que va a `FB_CMD_ARBITER`

---

### **3.4 Salidas Digitales (DO)**

⚠️ **IMPORTANTE**: 
- ❌ **NO se usan DO** para accionar bobinas de cierre/apertura de interruptores de potencia
- ✅ La maniobra de QT1/QG1/QG2 es **por Modbus RTU** (protocolo Schneider Command Interface)
- ✅ Los DO se usan para:
  - Pilotos LED del tablero
  - Bocina de alarma
  - Baliza parpadeante
  - Marcha/Parada Grupo Diésel (`DO_GD_START`, `DO_GD_STOP`)

**Implementación**: `01_SCL/05_FB_OUTPUTS.scl`

```scl
DO_PILOT_ON_GRID := IS_ON_GRID AND NOT IS_FAULT;    // LED verde
DO_PILOT_ON_GD := IS_ON_GD AND NOT IS_FAULT;        // LED amarillo
DO_ALARM_HORN := alarmActive AND NOT alarmAcknowledged;
```

**Mapeo físico**: Ver `01_SCL/10_OB1_MAIN.scl` (ejemplo):

```scl
DO_GD_START => %Q0.0,           // Orden marcha GD
DO_GD_STOP => %Q0.1,            // Orden parada GD
DO_PILOT_ON_GRID => %Q1.0,      // LED verde "EN RED"
DO_ALARM_HORN => %Q1.5,         // Bocina alarma
```

### **Dónde está la info**:

📄 **Señales y selectores**: [`06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf`](../06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf)  
📄 **Equipos con comunicación**: [`06_CONFIG/TGBT_Config - listado de equipos.pdf`](../06_CONFIG/TGBT_Config - listado de equipos.pdf)  
📄 **Código FB_IO_NORMALIZE**: [`01_SCL/01_FB_IO_NORMALIZE.scl`](../01_SCL/01_FB_IO_NORMALIZE.scl)

---

## 4) Transferencia Automática (SCMTA): Secuencias y Tiempos Confirmados

### **4.1 Condición de "Falta de Red"**

Se considera **falta de red** por:

1. ✅ **Pérdida total de tensión** (V < V_MIN)
2. ✅ **Falta de fase** (alguna tensión L-L fuera de rango)
3. ✅ **Frecuencia fuera de rango** (opcional, parametrizable)

**Implementación en** `01_SCL/02_FB_SCMTA.scl`:

```scl
// Cálculo GRID_OK
vMin := V_NOM * (V_MIN_PCT / 100.0);
vMax := V_NOM * (V_MAX_PCT / 100.0);

phaseOk := (GRID_V_L1L2 >= vMin) AND (GRID_V_L1L2 <= vMax) AND
           (GRID_V_L2L3 >= vMin) AND (GRID_V_L2L3 <= vMax) AND
           (GRID_V_L3L1 >= vMin) AND (GRID_V_L3L1 <= vMax);

freqOk := (GRID_FREQ >= FREQ_MIN) AND (GRID_FREQ <= FREQ_MAX);

gridOkRaw := phaseOk AND freqOk AND GRID_MEASUREMENT_OK;

// Filtro anti-rebote 2s
tonGridFailFilter(IN := NOT gridOkRaw, PT := T_GRID_FAIL_FILTER);
GRID_FAIL := tonGridFailFilter.Q;
GRID_OK := NOT GRID_FAIL;
```

**Parámetros configurables** (en `01_SCL/09_DB_PARAMS.scl`):

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `V_NOM` | 380V | Tensión nominal línea-línea |
| `V_MIN_PCT` | 85% | Umbral subtensión (323V) |
| `V_MAX_PCT` | 110% | Umbral sobretensión (418V) |
| `FREQ_NOM` | 50Hz | Frecuencia nominal |
| `FREQ_MIN` | 49Hz | Frecuencia mínima |
| `FREQ_MAX` | 51Hz | Frecuencia máxima |
| `T_GRID_FAIL_FILTER` | 2s | Filtro anti-rebote falla red |

---

### **4.2 Secuencia Red → GD (Automática)**

**Máquina de estados** implementada en `01_SCL/02_FB_SCMTA.scl`:

```
┌──────────────────────────────────────────────────────────┐
│  ESTADO 1: NORMAL_ON_GRID                                │
│  (QT1 cerrado, alimentando con red)                      │
└───────────────┬──────────────────────────────────────────┘
                │ Detectar GRID_FAIL (filtrado 2s)
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 2: GRID_FAIL_DETECTED                            │
│  Timeout: T_OPEN_QT1 (2s)                                │
└───────────────┬──────────────────────────────────────────┘
                │ REQ_SCMTA_OPEN_QT1 → CMD_ARBITER
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 3: OPEN_QT1                                      │
│  Esperar confirmación QT1_STATE = 0 (abierto)            │
│  Timeout: T_OPEN_QT1 (2s)                                │
└───────────────┬──────────────────────────────────────────┘
                │ QT1 confirmado abierto
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 4: START_GD_DELAY                                │
│  Espera de seguridad: T_START_GD_DELAY (3s)              │
└───────────────┬──────────────────────────────────────────┘
                │ Timeout cumplido
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 5: START_GD                                      │
│  DO_GD_START := TRUE (orden marcha generador)            │
└───────────────┬──────────────────────────────────────────┘
                │ Inmediato
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 6: WAIT_GD_READY                                 │
│  Esperar GD_READY = TRUE                                 │
│  Timeout: T_GD_READY_TIMEOUT (30s)                       │
└───────────────┬──────────────────────────────────────────┘
                │ GD_READY detectado
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 6b: Estabilización GD                            │
│  Timer: T_GD_STABILIZATION (5s)                          │
│  (Esperar que tensión/frecuencia GD se estabilice)       │
└───────────────┬──────────────────────────────────────────┘
                │ Timeout cumplido
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 7: CLOSE_QG1                                     │
│  REQ_SCMTA_CLOSE_QG1 → CMD_ARBITER                       │
│  Esperar confirmación QG1_STATE = 1 (cerrado)            │
│  Timeout: T_CLOSE_QG1 (2s)                               │
└───────────────┬──────────────────────────────────────────┘
                │ QG1 confirmado cerrado
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 8: ON_GD                                         │
│  Sistema operando con Grupo Diésel                       │
│  Monitoreo continuo carga GD (para deslastre)            │
└──────────────────────────────────────────────────────────┘
```

**Timeouts configurables** (en `01_SCL/09_DB_PARAMS.scl`):

| Parámetro | Default | Uso |
|-----------|---------|-----|
| `T_OPEN_QT1` | 2s | Timeout comando abrir QT1 |
| `T_START_GD_DELAY` | 3s | Espera antes marcha GD |
| `T_GD_READY_TIMEOUT` | 30s | Timeout espera GD_READY |
| `T_GD_STABILIZATION` | 5s | Estabilización GD antes cerrar QG1 |
| `T_CLOSE_QG1` | 2s | Timeout comando cerrar QG1 |

**Códigos de falla** (si timeout):

| Código | Descripción |
|--------|-------------|
| 101 | TIMEOUT: No se pudo abrir QT1 |
| 102 | TIMEOUT: GD no alcanzó estado READY |
| 103 | TIMEOUT: No se pudo cerrar QG1 |
| 106 | ALARMA: Falla en Grupo Diésel |

---

### **4.3 Secuencia GD → Red (Automática)**

**Retorno a red** cuando red se restablece:

```
┌──────────────────────────────────────────────────────────┐
│  ESTADO 8: ON_GD                                         │
│  (QG1 cerrado, alimentando con generador)                │
└───────────────┬──────────────────────────────────────────┘
                │ Detectar GRID_OK = TRUE (red vuelve)
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 9: GRID_RETURN_DETECTED                          │
│  Inicio filtro estabilidad red                           │
└───────────────┬──────────────────────────────────────────┘
                │ Inmediato
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 10: WAIT_GRID_STABLE                             │
│  Verificar GRID_OK sostenido durante 120s                │
│  Timer: T_GRID_STABLE (120s)                             │
│  Si pierde red → volver a ON_GD                          │
└───────────────┬──────────────────────────────────────────┘
                │ Red estable 120s confirmados
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 11: OPEN_QG1                                     │
│  REQ_SCMTA_OPEN_QG1 → CMD_ARBITER                        │
│  Esperar QG1_STATE = 0 (abierto)                         │
│  Timeout: T_OPEN_QG1 (2s)                                │
└───────────────┬──────────────────────────────────────────┘
                │ QG1 confirmado abierto
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 12: CLOSE_QT1                                    │
│  REQ_SCMTA_CLOSE_QT1 → CMD_ARBITER                       │
│  Esperar QT1_STATE = 1 (cerrado)                         │
│  Timeout: T_CLOSE_QT1 (2s)                               │
└───────────────┬──────────────────────────────────────────┘
                │ QT1 confirmado cerrado
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 13: GD_COOLDOWN                                  │
│  Mantener generador marchando sin carga                  │
│  Timer: T_GD_COOLDOWN (60s)                              │
└───────────────┬──────────────────────────────────────────┘
                │ Cooldown completo
                │ DO_GD_STOP := TRUE (parada generador)
                ▼
┌──────────────────────────────────────────────────────────┐
│  ESTADO 1: NORMAL_ON_GRID                                │
│  Retorno a operación normal con red                      │
└──────────────────────────────────────────────────────────┘
```

**Timeouts configurables**:

| Parámetro | Default | Uso |
|-----------|---------|-----|
| `T_GRID_STABLE` | 120s | Estabilidad red antes retorno |
| `T_OPEN_QG1` | 2s | Timeout abrir QG1 |
| `T_CLOSE_QT1` | 2s | Timeout cerrar QT1 |
| `T_GD_COOLDOWN` | 60s | Cooldown GD antes parar |

**Códigos de falla**:

| Código | Descripción |
|--------|-------------|
| 104 | TIMEOUT: No se pudo abrir QG1 |
| 105 | TIMEOUT: No se pudo cerrar QT1 |

---

### **Dónde está la info**:

📄 **Código máquina estados**: [`01_SCL/02_FB_SCMTA.scl`](../01_SCL/02_FB_SCMTA.scl)  
📄 **Parámetros**: [`01_SCL/09_DB_PARAMS.scl`](../01_SCL/09_DB_PARAMS.scl)  
📄 **Diagrama estados UML**: [`04_UML/11_UML_SCMTA_StateMachine.puml`](../04_UML/11_UML_SCMTA_StateMachine.puml)  
📄 **Documentación detallada**: [`03_DOCS/README_SCMTA.md`](README_SCMTA.md) - Sección "FB_SCMTA"  
📄 **Señales GD_START/GD_READY**: [`06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf`](../06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf)  
📄 **Medición PM5350**: [`06_CONFIG/TGBT_Config - pm5330.pdf`](../06_CONFIG/TGBT_Config - pm5330.pdf)

---

## 5) Gestión de Cargas: Deslastre y Reenganche

### **5.1 Alcance**

- **18 interruptores de salida** (feeders) equipados con **Micrologic** para monitoreo/control vía Modbus
- No todos son "no esenciales" por defecto
- El conjunto se gestiona mediante **prioridad configurable**

### **5.2 Criterio de Deslastre**

**Activación del deslastre solo cuando**:

```scl
SHED_ENABLE := (STATE == ST_ON_GD) AND MODE_AUTO;
```

Es decir:
- ✅ Sistema operando con Grupo Diésel (`STATE = 8`)
- ✅ Modo automático (`MODE_AUTO = TRUE`)

**Disparo basado en**:

1. **% Carga del GD** (principal) - `GD_LoadPct`
2. **% Carga del Transformador** (contingencia) - `TR_LoadPct`

**Implementación en** `01_SCL/03_FB_SHED.scl`:

```scl
// Condición para iniciar deslastre
shedTrigger := (GD_LoadPct >= SHED_ON_PCT) OR (TR_LoadPct >= SHED_ON_PCT);

IF SHED_ENABLE AND shedTrigger AND NOT shedActive THEN
    shedActive := TRUE;
    shedIndex := 1;  // Comenzar por primer feeder en SHED_ORDER
END_IF;
```

**Parámetros** (en `01_SCL/09_DB_PARAMS.scl`):

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `SHED_ON_PCT` | 90% | Umbral activación deslastre |
| `SHED_OFF_PCT` | 80% | Umbral desactivación (histéresis) |
| `RECONNECT_PCT` | 70% | Umbral reenganche |

---

### **5.3 Forma de Deslastre**

✅ **Escalonado**, no todo de golpe  
✅ **Retardo entre pasos**: `T_SHED_STEP` (3-5s configurables)  
✅ **Prioridad**: Según array `SHED_ORDER[1..18]`

**Algoritmo** (en `01_SCL/03_FB_SHED.scl`):

```scl
// Deslastre escalonado
IF shedActive THEN
    tonShedStep(IN := TRUE, PT := T_SHED_STEP);
    
    IF tonShedStep.Q AND (shedIndex <= 18) THEN
        feederIdx := SHED_ORDER[shedIndex];
        
        IF SHED_ENABLE[feederIdx] THEN
            REQ_SHED_OPEN[feederIdx] := TRUE;  // Generar request abrir
            shedIndex := shedIndex + 1;
        END_IF;
        
        tonShedStep(IN := FALSE);  // Reset timer para próximo paso
    END_IF;
END_IF;
```

**Prioridad típica** (parametrizable desde HMI):

Escalonar primero feeders de **mayor amperaje**:
- Feeders 400A (primeros en deslastrar)
- Feeders 320A
- Feeders 250A
- Resto según configuración

**Ejemplo `SHED_ORDER` por defecto**:

```scl
SHED_ORDER : Array[1..18] of Int := [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18];
```

Ajustar desde HMI para priorizar feeders específicos.

---

### **5.4 Reenganche al Volver la Red**

✅ **Escalonado**, con misma lógica (o parametrizable)  
✅ **Arranca cuando**: Sistema vuelve a `NORMAL_ON_GRID` (estado 1)  
✅ **Retardo**: `T_RECONNECT_STEP` (3-5s)

**Algoritmo** (en `01_SCL/03_FB_SHED.scl`):

```scl
// Reenganche escalonado
IF reconnectActive THEN
    tonReconnectStep(IN := TRUE, PT := T_RECONNECT_STEP);
    
    IF tonReconnectStep.Q AND (reconnectIndex <= 18) THEN
        feederIdx := SHED_ORDER[18 - reconnectIndex + 1];  // Orden inverso
        
        IF SHED_ENABLE[feederIdx] THEN
            REQ_SHED_CLOSE[feederIdx] := TRUE;  // Generar request cerrar
            reconnectIndex := reconnectIndex + 1;
        END_IF;
        
        tonReconnectStep(IN := FALSE);
    END_IF;
END_IF;
```

**Condición inicio reenganche**:

```scl
IF IS_ON_GRID AND feedersOpenCount > 0 AND (TR_LoadPct < RECONNECT_PCT) THEN
    reconnectActive := TRUE;
    reconnectIndex := 1;
END_IF;
```

---

### **5.5 Prioridades Configurables (Decisión de Diseño Clave)**

Para evitar "ordenamiento" complejo en PLC:

✅ Se usa un **array parametrizable** desde HMI: `SHED_ORDER[1..N]`

```
SHED_ORDER[1] = ID del primer feeder a abrir (mayor prioridad deslastre)
SHED_ORDER[2] = segundo
...
SHED_ORDER[18] = último
```

✅ Array habilitación por feeder: `SHED_ENABLE[1..18]`

```scl
SHED_ENABLE : Array[1..18] of Bool := [
    TRUE,   // Feeder 1 participa deslastre
    TRUE,   // Feeder 2 participa
    FALSE,  // Feeder 3 NO participa (carga esencial)
    TRUE,   // Feeder 4 participa
    // ... resto
];
```

**Ventajas**:
- ✅ Configuración desde HMI sin recompilar PLC
- ✅ Lógica PLC independiente de prioridades específicas
- ✅ Fácil ajuste en campo según necesidades operativas

### **Dónde está la info**:

📄 **Código deslastre**: [`01_SCL/03_FB_SHED.scl`](../01_SCL/03_FB_SHED.scl)  
📄 **Parámetros**: [`01_SCL/09_DB_PARAMS.scl`](../01_SCL/09_DB_PARAMS.scl)  
📄 **Diagrama actividad UML**: [`04_UML/13_UML_SHED_Activity.puml`](../04_UML/13_UML_SHED_Activity.puml)  
📄 **Documentación detallada**: [`03_DOCS/README_SCMTA.md`](README_SCMTA.md) - Sección "FB_SHED"  
📄 **Dispositivos Micrologic**: [`06_CONFIG/TGBT_Config - listado de equipos.pdf`](../06_CONFIG/TGBT_Config - listado de equipos.pdf)  
📄 **Medición carga**: [`06_CONFIG/TGBT_Config - pm5330.pdf`](../06_CONFIG/TGBT_Config - pm5330.pdf)

---

## 6) Arquitectura de Software PLC (TIA Portal V18) Desarrollada

### **6.1 Decisión de Lenguaje**

✅ **SCL (Structured Control Language)** como lenguaje principal

**Razones**:
- Máquinas de estados complejas (21 estados SCMTA con failover GD1↔GD2)
- Arrays dinámicos (`SHED_ORDER[1..18]`)
- Loops (`FOR i := 1 TO 18`)
- Protocolos complejos (Modbus Command Interface)
- Cálculos matemáticos (tensión, frecuencia, porcentajes)
- Más compacto y mantenible que LADDER puro

**Nota**: Se proporcionan conversiones LADDER de referencia en carpeta `02_LADDER/` para bloques simples (IO_NORMALIZE, OUTPUTS, OB1).

---

### **6.2 Estructura Modular (Bloques Desarrollados)**

El proyecto está organizado en **7 Function Blocks + 2 Data Blocks + 1 OB1**:

```
📦 Arquitectura PLC (carpeta 01_SCL/)
│
├── 🔧 FUNCTION BLOCKS (FB)
│   │
│   ├── 01_FB_IO_NORMALIZE.scl
│   │   └─ Normalización entradas físicas
│   │      • Selector Auto/Manual → MODE_AUTO/MODE_MANUAL
│   │      • Selectores Local/Remoto → *_REMOTE_ALLOWED
│   │      • Pulsadores → Requests manuales (R_TRIG pulso 1 scan)
│   │      • Señales GD → GD_READY/RUNNING/ALARM
│   │      • Debounce 50ms en pulsadores
│   │
│   ├── 02_FB_SCMTA.scl
│   │   └─ Máquina estados transferencia automática
│   │      • 21 estados (0-20) con failover GD1↔GD2
│   │      • Secuencia Red→GD1 (con timeouts y confirmaciones)
│   │      • Secuencia GD→Red (con estabilidad 120s)
│   │      • Failover GD1→GD2 (estados 15-20)
│   │      • Failover GD2→GD1 (conmutación automática)
│   │      • Detección falla red (tensión + frecuencia + fase)
│   │      • Control marcha/parada GD1 y GD2
│   │      • Gestión fallas y lockout
│   │
│   ├── 03_FB_SHED.scl
│   │   └─ Deslastre y reenganche cargas V2.0
│   │      • 6 modos: IDLE, GRID_SHED, GD_INITIAL_SHED, GD_RECONNECT, GD_REACTIVE_SHED, GRID_RECONNECT
│   │      • FEEDER_ESSENTIAL[1..18] (esenciales protegidos)
│   │      • Deslastre en RED (sobrecarga trafo) y GD (sobrecarga GD)
│   │      • Arrays configurables SHED_ORDER[1..18], SHED_ENABLE[1..18]
│   │      • Reenganche escalonado automático
│   │      • Timeouts parametrizables (T_SHED_STEP, T_RECONNECT_STEP)
│   │
│   ├── 04_FB_CMD_ARBITER.scl
│   │   └─ Árbitro comandos con prioridades
│   │      • Prioridad: SCMTA > SHED > MANUAL
│   │      • Enclavamiento fuente única (QT1/QG1/QG2)
│   │      • Bloqueo por LOCAL/REMOTO
│   │      • Antidoble comando (no OPEN y CLOSE simultáneos)
│   │      • Alarmas violación interlock
│   │
│   ├── 05_FB_OUTPUTS.scl
│   │   └─ Gestión salidas físicas y HMI
│   │      • Pilotos LED (ON_GRID, ON_GD, TRANSFER, FAULT, SHED)
│   │      • Bocina alarma con ACK
│   │      • Baliza parpadeante
│   │      • Textos alarma (CASE statement)
│   │      • Señales consolidadas para HMI
│   │
│   ├── 06_FB_MODBUS_MANAGER.scl
│   │   └─ Scheduler comunicaciones Modbus RTU
│   │      • Gestión cola operaciones (lecturas + escrituras)
│   │      • Priorización comandos críticos
│   │      • Distribución tiempo entre equipos
│   │      • REQ activo 2 segundos (compatibilidad hardware)
│   │      • Coordinación drivers MTZ/NSX
│   │
│   └── 07_FB_MTZ_DRIVER.scl
│       └─ Driver protocolo Schneider Command Interface
│          • Máquina estados 5 estados (IDLE, BUILD_BUFFER, WRITE_CMD, POLL_RESPONSE, CONFIRM)
│          • Preparación buffer comandos (8000-8019)
│          • Escritura FC16 (Write Multiple Registers)
│          • Polling respuesta (8020-8021)
│          • Confirmación estado (32000-32001)
│          • REQ activo 2s durante escritura
│
├── 📊 DATA BLOCKS (DB)
│   │
│   ├── 08_DB_GLOBAL_STATUS.scl
│   │   └─ Estados sistema (NON_RETAIN)
│   │      • Modos operación (MODE_AUTO, MODE_MANUAL)
│   │      • Estados interruptores (QT1_STATE, QG1_STATE, QG2_STATE)
│   │      • Mediciones red (GRID_V_L1L2, GRID_FREQ, etc.)
│   │      • Flags sistema (IS_ON_GRID, IS_ON_GD, IS_IN_TRANSFER, IS_FAULT)
│   │      • Estados feeders
│   │      • Alarmas activas
│   │
│   └── 09_DB_PARAMS.scl
│       └─ Parámetros configurables (RETAIN)
│          • Umbrales tensión/frecuencia (V_NOM, V_MIN_PCT, FREQ_MIN)
│          • Timeouts secuencias (T_OPEN_QT1, T_GRID_STABLE, etc.)
│          • Umbrales deslastre (SHED_ON_PCT, RECONNECT_PCT)
│          • Arrays prioridad (SHED_ORDER[1..18], SHED_ENABLE[1..18])
│          • Configuración Modbus (SLAVE_ADDR, baudrate, etc.)
│
└── 🔄 ORGANIZATION BLOCK (OB)
    │
    └── 10_OB1_MAIN.scl
        └─ Main cíclico (orquestación)
           • Network 1: Llamada FB_IO_NORMALIZE
           • Network 2: Llamada FB_SCMTA
           • Network 3: Llamada FB_SHED
           • Network 4: Llamada FB_CMD_ARBITER
           • Network 5: Llamada FB_OUTPUTS
           • Network 6: Llamadas Drivers Modbus (QT1, QG1, QG2, Feeders)
           • Tiempo ciclo recomendado: 100-200 ms
```

---

### **6.3 Flujo de Ejecución (OB1)**

```
┌─────────────────────────────────────────────────────┐
│  OB1 - Main Cyclic Execution                        │
│  ┌───────────────────────────────────────────────┐  │
│  │ ① FB_IO_NORMALIZE                            │  │
│  │   DI físicas → Señales normalizadas           │  │
│  └────────────────┬──────────────────────────────┘  │
│                   ↓                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │ ② FB_SCMTA                                   │  │
│  │   Máquina estados Red↔GD                      │  │
│  │   Genera: REQ_SCMTA_OPEN/CLOSE_*              │  │
│  └────────────────┬──────────────────────────────┘  │
│                   ↓                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │ ③ FB_SHED                                    │  │
│  │   Deslastre/Reenganche                        │  │
│  │   Genera: REQ_SHED_OPEN/CLOSE[1..18]          │  │
│  └────────────────┬──────────────────────────────┘  │
│                   ↓                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │ ④ FB_CMD_ARBITER                             │  │
│  │   Prioriza: SCMTA > SHED > MANUAL             │  │
│  │   Aplica: Interlock + Local/Remoto            │  │
│  │   Genera: CMD_OPEN/CLOSE_* (arbitrados)       │  │
│  └────────────────┬──────────────────────────────┘  │
│                   ↓                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │ ⑤ FB_OUTPUTS                                 │  │
│  │   Pilotos, alarmas, HMI                       │  │
│  │   Salidas: DO físicas + señales HMI           │  │
│  └────────────────┬──────────────────────────────┘  │
│                   ↓                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │ ⑥ Drivers Modbus                             │  │
│  │   • FB_MTZ_DRIVER (QT1, QG1, QG2)             │  │
│  │   • FB_MODBUS_MANAGER (Scheduler)             │  │
│  │   Ejecuta: CMD_* → Modbus RTU                 │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Código completo**: [`01_SCL/10_OB1_MAIN.scl`](../01_SCL/10_OB1_MAIN.scl)

---

### **6.4 Conversiones LADDER (Referencia)**

Para ingenieros que prefieren LADDER, se proporcionan conversiones documentadas:

📄 [`02_LADDER/LADDER_01_FB_IO_NORMALIZE.md`](../02_LADDER/LADDER_01_FB_IO_NORMALIZE.md)
- 12 Networks, 33 Rungs
- Debounce + R_TRIG visual

📄 [`02_LADDER/LADDER_05_FB_OUTPUTS.md`](../02_LADDER/LADDER_05_FB_OUTPUTS.md)
- 12 Networks, 29 Rungs
- Recomendación: FB Mixto LADDER+SCL

📄 [`02_LADDER/LADDER_10_OB1_MAIN.md`](../02_LADDER/LADDER_10_OB1_MAIN.md)
- 6 Networks (CALL bloques)
- Visual y simple

**Guía completa**: [`03_DOCS/GUIA_COMPLETA_SCL_LADDER.md`](GUIA_COMPLETA_SCL_LADDER.md)
- Comparación técnica SCL vs LADDER
- Decisión por bloque
- Tabla comparativa

---

## 7) Modbus RTU: Lectura de Estado y Escritura de Comandos (MTZ/NSX Micrologic)

### **7.1 Lectura de Estado**

**Protocolo**: Modbus RTU, FC3 (Read Holding Registers)

**Registros de estado** (implementado en `01_SCL/07_FB_MTZ_DRIVER.scl`):

| Registro | Descripción | Uso |
|----------|-------------|-----|
| **32000** | Calidad de bits del 32001 | Validación (bit0=1 → OF válido) |
| **32001** | Estado del interruptor (bits) | Lectura estado |

**Bits del registro 32001**:

| Bit | Nombre | Descripción |
|-----|--------|-------------|
| bit 0 | **OF** (Open/Close) | 1 = Cerrado, 0 = Abierto |
| bit 1 | **SD** (Tripped) | 1 = Disparado/Falla, 0 = Normal |
| bit 5 | **PF** (Ready to Close) | 1 = Listo para cerrar (Masterpact) |

**Interpretación en código**:

```scl
// Lectura estado (en FB_MTZ_DRIVER)
CB_STATE := 2;  // Desconocido por defecto

IF statusQuality.bit0 THEN  // Validar calidad OF
    IF statusReg.bit0 THEN
        CB_STATE := 1;  // Cerrado
    ELSE
        CB_STATE := 0;  // Abierto
    END_IF;
END_IF;

IF statusReg.bit1 THEN
    CB_STATE := 2;  // Trip/Falla
END_IF;
```

---

### **7.2 Comandos de Apertura/Cierre (Command Interface Schneider)**

**Protocolo**: Modbus RTU, FC16 (Write Multiple Registers)

**Secuencia completa** (implementado en `01_SCL/07_FB_MTZ_DRIVER.scl`):

#### **Paso 1: Preparación Buffer (8000-8019)**

```scl
// Estado BUILD_BUFFER
cmdBuffer[0]  := 904;   // Código comando: 904=OPEN, 905=CLOSE, 906=RESET
cmdBuffer[1]  := 10;    // Longitud datos
cmdBuffer[2]  := 5377;  // Valor fijo protocolo
cmdBuffer[3]  := 1;     // Modo intrusivo con password
cmdBuffer[4]  := 13107; // Password ASCII byte 1-2 (ej: "3333" → 0x3333)
cmdBuffer[5]  := 13107; // Password ASCII byte 3-4
cmdBuffer[6]  := 0;     // Reservado
cmdBuffer[7]  := 0;
cmdBuffer[8]  := 0;
cmdBuffer[9]  := 0;
cmdBuffer[10] := 0;
cmdBuffer[11] := 0;
cmdBuffer[12] := 0;
cmdBuffer[13] := 0;
cmdBuffer[14] := 0;
cmdBuffer[15] := 0;
cmdBuffer[16] := 0;     // 8016
cmdBuffer[17] := 0;     // 8017 reservado
cmdBuffer[18] := 0;     // 8018 reservado
cmdBuffer[19] := 0;     // 8019 reservado
```

**Códigos de comando**:

| Código | Comando |
|--------|---------|
| 904 | OPEN (Abrir) |
| 905 | CLOSE (Cerrar) |
| 906 | RESET (Reset trip) |

**Passwords típicos** (nivel 3):

| ASCII | Hex | Decimal |
|-------|-----|---------|
| "3333" | 0x33333333 | 13107, 13107 |
| "4444" | 0x44444444 | 17476, 17476 |

#### **Paso 2: Escritura Buffer (FC16)**

```scl
// Estado WRITE_CMD
// Escribir registros 8000-8019 (20 registros)
MB_CLIENT(
    REQ := reqWriteActive,  // REQ activo 2 segundos
    MB_MODE := 1,           // FC16 Write Multiple Registers
    ADDR := 8000,
    LEN := 20,
    DATA := cmdBuffer
);

// Mantener REQ activo 2s
tonReqWrite(IN := reqWriteActive, PT := T#2s);
IF tonReqWrite.Q THEN
    reqWriteActive := FALSE;
    STATE := 3;  // POLL_RESPONSE
END_IF;
```

#### **Paso 3: Polling Respuesta (8020-8021)**

```scl
// Estado POLL_RESPONSE
// Leer registros 8020-8021
MB_CLIENT(
    REQ := reqPoll,
    MB_MODE := 0,   // FC3 Read Holding Registers
    ADDR := 8020,
    LEN := 2,
    DATA := responseBuffer
);

// responseBuffer[1] = 8021 (estado ocupado)
// Valor 0x0003 = ocupado, esperar
// Valor distinto = completado
```

#### **Paso 4: Validación Resultado (8021)**

```scl
// Verificar LSB del registro 8021
IF (responseBuffer[1] AND 16#0001) = 0 THEN
    // LSB=0 → Comando OK
    STATE := 4;  // CONFIRM
ELSE
    // LSB=1 → Error
    STATE := 5;  // ERROR
    ERROR_CODE := 201;  // Error ejecución comando
END_IF;
```

#### **Paso 5: Confirmación Estado (32000-32001)**

```scl
// Estado CONFIRM
// Volver a leer 32001 para confirmar cambio estado físico
MB_CLIENT(
    REQ := reqConfirm,
    MB_MODE := 0,
    ADDR := 32000,
    LEN := 2,
    DATA := statusBuffer
);

// Verificar que OF cambió según comando enviado
IF (CMD_OPEN AND statusBuffer[1].bit0 = 0) OR 
   (CMD_CLOSE AND statusBuffer[1].bit0 = 1) THEN
    // Estado confirmado OK
    STATE := 0;  // IDLE
ELSE
    // Estado no cambió → Error
    ERROR_CODE := 202;  // Timeout confirmación
    STATE := 5;  // ERROR
END_IF;
```

---

### **7.3 Driver por Equipo (Decisión de Diseño)**

**Implementación**: Un driver **parametrizable** por tipo de equipo

**Instancias del driver**:

```scl
// En OB1_MAIN.scl
"DB_QT1_DRV"(
    ENABLE := TRUE,
    SLAVE_ADDR := 1,        // Dirección Modbus MTZ1
    CMD_OPEN := "DB_ARBITER".CMD_OPEN_QT1,
    CMD_CLOSE := "DB_ARBITER".CMD_CLOSE_QT1,
    CB_STATE => "DB_GLOBAL_STATUS".QT1_STATE,
    COMM_OK => "DB_GLOBAL_STATUS".QT1_COMM_OK
);

"DB_QG1_DRV"(
    ENABLE := TRUE,
    SLAVE_ADDR := 2,        // Dirección Modbus NSX1
    CMD_OPEN := "DB_ARBITER".CMD_OPEN_QG1,
    CMD_CLOSE := "DB_ARBITER".CMD_CLOSE_QG1,
    CB_STATE => "DB_GLOBAL_STATUS".QG1_STATE
);

"DB_QG2_DRV"(
    ENABLE := TRUE,         // Implementado V3.0
    SLAVE_ADDR := 3,
    CMD_OPEN := "DB_ARBITER".CMD_OPEN_QG2,
    CMD_CLOSE := "DB_ARBITER".CMD_CLOSE_QG2,
    CB_STATE => "DB_GLOBAL_STATUS".QG2_STATE
);
```

**Scheduler global**: `01_SCL/06_FB_MODBUS_MANAGER.scl`
- Coordina tiempo entre múltiples drivers
- Evita colisiones en bus RTU
- Prioriza comandos críticos sobre lecturas

---

### **7.4 Modificación REQ 2 Segundos**

⚠️ **IMPORTANTE**: El hardware Modbus Master requiere que **REQ se mantenga activo por 2 segundos** (no pulso 1 scan).

**Implementación**:

```scl
// En FB_MODBUS_MANAGER
IF tonPollCycle.Q THEN
    reqModbusActive := TRUE;
    tonReqActive(IN := FALSE);  // Reset timer
END_IF;

// Mantener REQ por 2s
tonReqActive(IN := reqModbusActive, PT := T#2s);
IF tonReqActive.Q THEN
    reqModbusActive := FALSE;
END_IF;

// Conectar reqModbusActive a MB_MASTER.REQ
```

**Documentación detallada**: [`03_DOCS/CAMBIOS_REQ_2_SEGUNDOS.md`](CAMBIOS_REQ_2_SEGUNDOS.md)

---

### **Dónde está la info**:

📄 **Código driver**: [`01_SCL/07_FB_MTZ_DRIVER.scl`](../01_SCL/07_FB_MTZ_DRIVER.scl)  
📄 **Código scheduler**: [`01_SCL/06_FB_MODBUS_MANAGER.scl`](../01_SCL/06_FB_MODBUS_MANAGER.scl)  
📄 **Diagrama estados UML**: [`04_UML/12_UML_MTZ_Driver_StateMachine.puml`](../04_UML/12_UML_MTZ_Driver_StateMachine.puml)  
📄 **Modificación REQ 2s**: [`03_DOCS/CAMBIOS_REQ_2_SEGUNDOS.md`](CAMBIOS_REQ_2_SEGUNDOS.md)  
📄 **Manual MTZ**: [`05_MANUALES/MTZ MANUAL.pdf`](../05_MANUALES/MTZ MANUAL.pdf)  
📄 **Manual NSX**: [`05_MANUALES/NSX MANUAL.pdf`](../05_MANUALES/NSX MANUAL.pdf)  
📄 **Escritura MTZ**: [`05_MANUALES/Escritura_MTZ.pdf`](../05_MANUALES/Escritura_MTZ.pdf)  
📄 **Listado equipos Modbus**: [`06_CONFIG/TGBT_Config - listado de equipos.pdf`](../06_CONFIG/TGBT_Config - listado de equipos.pdf)

---

## 8) Qué Hacer Como Nuevo Ingeniero (Lista de Trabajo)

### **8.1 Familiarización con el Proyecto (Día 1-2)**

✅ **Leer documentación principal**:

1. [`README.md`](../README.md) - Vista general del proyecto
2. [`03_DOCS/README_SCMTA.md`](README_SCMTA.md) - Documentación técnica completa (~30 páginas, V3.0)
3. [`03_DOCS/VALIDACION_SCL_TIA_V18.md`](VALIDACION_SCL_TIA_V18.md) - Validación código (100% compatible)
4. Este documento - Introducción técnica

✅ **Revisar diagramas**:

1. [`04_UML/11_UML_SCMTA_StateMachine.puml`](../04_UML/11_UML_SCMTA_StateMachine.puml) - Estados SCMTA (GD1, 0-14)
2. [`04_UML/14_UML_SCMTA_GD2_StateMachine.puml`](../04_UML/14_UML_SCMTA_GD2_StateMachine.puml) - Estados SCMTA GD2 failover (15-20)
3. [`04_UML/12_UML_MTZ_Driver_StateMachine.puml`](../04_UML/12_UML_MTZ_Driver_StateMachine.puml) - Estados Driver
4. [`04_UML/13_UML_SHED_Activity.puml`](../04_UML/13_UML_SHED_Activity.puml) - Actividad deslastre
5. [`04_UML/15_UML_System_Architecture.puml`](../04_UML/15_UML_System_Architecture.puml) - Arquitectura sistema

✅ **Revisar configuración hardware**:

1. [`06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf`](../06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf)
2. [`06_CONFIG/TGBT_Config - listado de equipos.pdf`](../06_CONFIG/TGBT_Config - listado de equipos.pdf)
3. [`06_CONFIG/ET MONTAJE-TGBT.pdf`](../06_CONFIG/ET MONTAJE-TGBT.pdf)

---

### **8.2 Configuración Entorno TIA Portal (Día 2-3)**

✅ **Instalar software**:
- TIA Portal V18 (verificar licencia)
- S7-1200 support package

✅ **Crear proyecto**:

```
1. Abrir TIA Portal V18
2. "Create new project" → Nombre: "TGBT_SCMTA"
3. Add new device → SIMATIC S7-1200
4. Seleccionar CPU: 1214C DC/DC/DC o superior
   (Verificar modelo exacto según hardware)
```

✅ **Importar código fuente**:

**Orden de importación** (carpeta `01_SCL/`):

```
1. 08_DB_GLOBAL_STATUS.scl  ← Data Blocks primero
2. 09_DB_PARAMS.scl
3. 01_FB_IO_NORMALIZE.scl   ← Function Blocks
4. 02_FB_SCMTA.scl
5. 03_FB_SHED.scl
6. 04_FB_CMD_ARBITER.scl
7. 05_FB_OUTPUTS.scl
8. 06_FB_MODBUS_MANAGER.scl
9. 07_FB_MTZ_DRIVER.scl
10. 10_OB1_MAIN.scl         ← Organization Block al final
```

**Procedimiento importación**:
```
Proyecto → External source files → Add new external file
→ Seleccionar archivo .scl → Generate blocks from source
```

✅ **Compilar proyecto**:

```
Build → Compile all blocks
Verificar: 0 errors, 0 warnings
```

---

### **8.3 Mapeo Direcciones Físicas (Día 3-4)**

⚠️ **CRÍTICO**: Las direcciones físicas `%I` / `%Q` en `10_OB1_MAIN.scl` son **ejemplos**.

**Debes mapear según**:
[`06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf`](../06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf)

**Ejemplo ajuste en `10_OB1_MAIN.scl`**:

```scl
// Network 1: FB_IO_NORMALIZE
"DB_IO"(
    // ANTES (ejemplo):
    DI_SYS_AUTO := %I0.0,
    
    // DESPUÉS (según listado real):
    DI_SYS_AUTO := %I2.3,  // ← Ajustar según PDF
    
    // Repetir para todas las entradas/salidas
    // ...
);
```

**Crear tabla de mapeo** (Excel recomendado):

| Señal | Dirección TIA | Módulo Físico | Terminal | Comentario |
|-------|---------------|---------------|----------|------------|
| DI_SYS_AUTO | %I2.3 | DI16x24VDC | 3 | Selector Auto/Manual |
| DO_GD_START | %Q1.0 | DO16x24VDC | 0 | Marcha GD |
| ... | ... | ... | ... | ... |

---

### **8.4 Configuración Modbus RTU (Día 4-5)**

✅ **Agregar módulo comunicación**:

```
1. Device view → PLC → Hardware catalog
2. Agregar: CM 1241 RS485 (o equivalente según hardware)
3. Configurar puerto:
   - Protocol: Freeport (Modbus RTU)
   - Baud rate: 19200
   - Parity: Even (2)
   - Stop bits: 1
```

✅ **Configurar MB_MASTER / MB_CLIENT**:

```
1. Instructions → Communication → Modbus RTU → MB_CLIENT
2. Arrastrar a FB_MTZ_DRIVER donde dice "// TODO: MB_CLIENT"
3. Conectar parámetros:
   REQ := reqWriteActive
   MB_MODE := 1  (FC16 Write)
   ADDR := 8000
   LEN := 20
   MB_ADDR := SLAVE_ADDR
```

✅ **Configurar direcciones Modbus** (en `09_DB_PARAMS.scl`):

| Equipo | Parámetro | Valor | Verificar en |
|--------|-----------|-------|--------------|
| QT1 (MTZ1) | SLAVE_ADDR_QT1 | 1 | Listado equipos PDF |
| QG1 (NSX1) | SLAVE_ADDR_QG1 | 2 | Listado equipos PDF |
| QG2 (NSX2) | SLAVE_ADDR_QG2 | 3 | Listado equipos PDF |
| PM5350 (Medidor) | SLAVE_ADDR_PM5350 | 10 | TGBT_Config - pm5330.pdf |

---

### **8.5 Parametrización Inicial (Día 5)**

✅ **Ajustar parámetros en** `09_DB_PARAMS.scl`:

**Umbrales red**:
```scl
V_NOM := 380.0;         // [V] Verificar tensión nominal instalación
V_MIN_PCT := 85.0;      // [%] Ajustar según requerimiento
FREQ_NOM := 50.0;       // [Hz] 50Hz Argentina / 60Hz otros
```

**Timeouts transferencia**:
```scl
T_GRID_STABLE := T#120s;    // Confirmar con operación
T_GD_COOLDOWN := T#60s;     // Ajustar según fabricante GD
```

**Deslastre**:
```scl
SHED_ON_PCT := 90.0;        // [%] Umbral sobrecarga GD
SHED_ORDER := [1,2,3,...];  // Ajustar según prioridades operativas
```

✅ **Crear tabla parámetros** para HMI futuro

---

### **8.6 Testing en Simulación (Día 6-8)**

✅ **Usar PLCSIM** (TIA Portal Simulation):

```
1. Project → Download to device → PLCSIM
2. Start simulation
3. Online & diagnostics → Watch tables
```

✅ **Crear Watch Tables** para:

**Tabla 1: Estados sistema**
```
DB_GLOBAL_STATUS.MODE_AUTO
DB_GLOBAL_STATUS.SCMTA_STATE
DB_GLOBAL_STATUS.QT1_STATE
DB_GLOBAL_STATUS.QG1_STATE
DB_GLOBAL_STATUS.IS_ON_GRID
DB_GLOBAL_STATUS.IS_ON_GD
```

**Tabla 2: Mediciones**
```
DB_GLOBAL_STATUS.GRID_V_L1L2
DB_GLOBAL_STATUS.GRID_FREQ
DB_GLOBAL_STATUS.GD_LoadPct
```

**Tabla 3: Comandos**
```
DB_ARBITER.CMD_OPEN_QT1
DB_ARBITER.CMD_CLOSE_QT1
DB_ARBITER.CMD_OPEN_QG1
DB_ARBITER.CMD_CLOSE_QG1
```

✅ **Scenarios de prueba**:

**Test 1: Transferencia Red→GD (falla red)**
```
1. Forzar GRID_V_L1L2 = 0V (simular falla red)
2. Verificar secuencia estados SCMTA: 1→2→3→4→5→6→7→8
3. Verificar timeouts respetados
4. Verificar QT1 abre, QG1 cierra (en simulación forzar confirmaciones)
```

**Test 2: Retorno GD→Red**
```
1. Desde estado ON_GD (8)
2. Forzar GRID_V_L1L2 = 380V (simular retorno red)
3. Verificar espera 120s (T_GRID_STABLE)
4. Verificar secuencia: 8→9→10→11→12→13→1
```

**Test 3: Deslastre automático**
```
1. Forzar estado ON_GD (8)
2. Forzar GD_LoadPct = 95% (> SHED_ON_PCT)
3. Verificar SHED_MODE = 4 (GD_REACTIVE_SHED)
4. Verificar deslastre escalonado según SHED_ORDER
5. Verificar T_SHED_STEP (3-5s) entre pasos
6. Verificar FEEDER_ESSENTIAL protegidos
```

**Test 3b: Failover GD1→GD2**
```
1. Desde estado ON_GD (8), forzar GD1_ALARM = TRUE
2. Verificar secuencia: 8→15→16→17→18→19 (ON_GD2)
3. Verificar QG1 abre, QG2 cierra
4. Verificar GD2 arranca correctamente
```

**Test 4: Enclavamiento fuente única**
```
1. Forzar CMD_CLOSE_QT1 + CMD_CLOSE_QG1 simultáneos
2. Verificar: FB_CMD_ARBITER bloquea uno
3. Verificar: ALARM_INTERLOCK_VIOLATION = TRUE
```

**Test 5: Bloqueo LOCAL**
```
1. Forzar QT1_REMOTE_ALLOWED = FALSE (selector en LOCAL)
2. Intentar CMD_CLOSE_QT1
3. Verificar: Comando bloqueado por ARBITER
```

---

### **8.7 Documentar Resultados Testing (Día 8-9)**

✅ **Crear Excel "Test Report"**:

| Test ID | Descripción | Resultado | Observaciones | Estado |
|---------|-------------|-----------|---------------|--------|
| T001 | Transferencia Red→GD | PASS | Timeouts OK | ✅ |
| T002 | Retorno GD→Red | PASS | 120s confirmado | ✅ |
| T003 | Deslastre automático | PENDING | Ajustar SHED_ORDER | ⏳ |
| ... | ... | ... | ... | ... |

✅ **Documentar ajustes necesarios**:
- Parámetros a modificar
- Bugs encontrados (si alguno)
- Mejoras sugeridas

---

### **8.8 Integración Modbus Real (Día 10-15)**

⚠️ **REQUIERE HARDWARE**: PLC + módulo CM1241 RS485 + equipos Modbus

✅ **Conectar físicamente**:

```
1. CM1241 RS485 → Terminal A, B, GND
2. Verificar resistencia terminación (120Ω en extremos)
3. Conectar equipos en cadena (daisy chain)
4. Verificar polaridad A/B correcta
```

✅ **Testing Modbus por equipo**:

**Test QT1 (MTZ1)**:
```
1. Conectar solo QT1 (dirección 1)
2. Leer 32000-32001 (estado)
3. Verificar COMM_OK = TRUE
4. Enviar comando OPEN (904)
5. Verificar ejecución y confirmación
```

**Repetir para QG1, QG2, PM5350**

✅ **Debugging Modbus**:

- Usar Online & Diagnostics → MB_CLIENT status
- Verificar ERROR_ID:
  - 0 = OK
  - 80A1 = Timeout comunicación
  - 80C4 = Exception Modbus (verificar dirección/registro)

---

### **8.9 Comisionamiento en Campo (Día 16-20)**

⚠️ **REQUIERE COORDINACIÓN** con instalador eléctrico y operación

✅ **Pre-comisionamiento**:

```
1. Verificar instalación eléctrica completa
2. Verificar cableado señales (según listado I/O)
3. Verificar configuración equipos Modbus
4. Backup proyecto TIA Portal
```

✅ **Comisionamiento por etapas**:

**Etapa 1: Monitoreo sin control**
```
1. Descargar programa PLC
2. Modo MANUAL + LOCAL (PLC solo monitorea)
3. Verificar lectura estados correcta
4. Verificar mediciones red/GD
5. Realizar maniobras manualmente, verificar feedback PLC
```

**Etapa 2: Control manual remoto**
```
1. Modo MANUAL + REMOTO
2. Probar comandos individuales desde HMI/Watch Table
3. Verificar enclavamientos
4. Probar con QT1, QG1 sin carga
```

**Etapa 3: Transferencia automática sin carga**
```
1. Modo AUTOMÁTICO
2. Simular falla red (abrir interruptor aguas arriba)
3. Verificar secuencia Red→GD completa
4. Verificar retorno GD→Red
5. Ajustar timeouts si necesario
```

**Etapa 4: Transferencia automática con carga**
```
1. Conectar cargas progresivamente
2. Repetir pruebas transferencia
3. Probar deslastre (forzar sobrecarga si posible)
4. Ajustar SHED_ORDER según necesidades operativas
```

✅ **Documentar puesta en marcha**:
- Parámetros finales ajustados
- Tiempos reales medidos
- Incidencias y soluciones
- Protocolo de entrega

---

### **8.10 Desarrollo HMI (Paralelo o Posterior)**

⚠️ **No cubierto en este proyecto** (solo PLC)

**Recomendaciones para HMI**:

✅ **Pantalla principal**:
- Unifilar TGBT con estados QT1/QG1/QG2
- Indicación fuente activa (RED / GD)
- Estado SCMTA (texto + color)
- Mediciones principales (V, I, P, f)

✅ **Pantalla alarmas**:
- Lista alarmas activas
- Histórico alarmas
- Botón ACK

✅ **Pantalla parámetros**:
- Editable: timeouts, umbrales, SHED_ORDER
- Con contraseña nivel supervisor

✅ **Pantalla deslastre**:
- Estados 18 feeders
- Prioridad (SHED_ORDER)
- Habilitación (SHED_ENABLE)
- Botón reset deslastre

✅ **Tags HMI → PLC**:

Leer de `DB_GLOBAL_STATUS`:
```
MODE_AUTO, SCMTA_STATE, STATE_NAME,
QT1_STATE, QG1_STATE, QG2_STATE,
GRID_V_L1L2, GRID_FREQ, GD_LoadPct,
IS_ON_GRID, IS_ON_GD, IS_FAULT,
HMI_ALARM_ACTIVE, HMI_ALARM_TEXT
```

Escribir a `DB_PARAMS`:
```
V_MIN_PCT, SHED_ON_PCT, T_GRID_STABLE,
SHED_ORDER[1..18], SHED_ENABLE[1..18]
```

---

## 9) Dónde Encontrar Cada Información (Guía Rápida de Referencias)

### **📁 Código Fuente PLC**

| Qué necesitas | Archivo | Ubicación |
|---------------|---------|-----------|
| **Normalización entradas** | 01_FB_IO_NORMALIZE.scl | [`01_SCL/`](../01_SCL/) |
| **Máquina estados SCMTA** | 02_FB_SCMTA.scl | [`01_SCL/`](../01_SCL/) |
| **Deslastre cargas** | 03_FB_SHED.scl | [`01_SCL/`](../01_SCL/) |
| **Árbitro comandos** | 04_FB_CMD_ARBITER.scl | [`01_SCL/`](../01_SCL/) |
| **Pilotos y alarmas** | 05_FB_OUTPUTS.scl | [`01_SCL/`](../01_SCL/) |
| **Scheduler Modbus** | 06_FB_MODBUS_MANAGER.scl | [`01_SCL/`](../01_SCL/) |
| **Driver MTZ/NSX** | 07_FB_MTZ_DRIVER.scl | [`01_SCL/`](../01_SCL/) |
| **Estados sistema** | 08_DB_GLOBAL_STATUS.scl | [`01_SCL/`](../01_SCL/) |
| **Parámetros** | 09_DB_PARAMS.scl | [`01_SCL/`](../01_SCL/) |
| **Main cíclico** | 10_OB1_MAIN.scl | [`01_SCL/`](../01_SCL/) |

---

### **📄 Documentación Técnica**

| Qué necesitas | Archivo | Ubicación |
|---------------|---------|-----------|
| **Vista general proyecto** | README.md | Raíz [`/`](../) |
| **Documentación completa** (25 págs) | README_SCMTA.md | [`03_DOCS/`](../03_DOCS/) |
| **Validación código SCL** | VALIDACION_SCL_TIA_V18.md | [`03_DOCS/`](../03_DOCS/) |
| **Guía SCL vs LADDER** | GUIA_COMPLETA_SCL_LADDER.md | [`03_DOCS/`](../03_DOCS/) |
| **Modificación REQ 2s** | CAMBIOS_REQ_2_SEGUNDOS.md | [`03_DOCS/`](../03_DOCS/) |
| **Índice archivos** | INDEX.md | [`03_DOCS/`](../03_DOCS/) |
| **Esta introducción** | INTRODUCCION_TECNICA_INGENIERO.md | [`03_DOCS/`](../03_DOCS/) |

---

### **🎨 Diagramas UML**

| Qué necesitas | Archivo | Ubicación |
|---------------|---------|-----------|
| **Estados SCMTA GD1** (estados 0-14) | 11_UML_SCMTA_StateMachine.puml | [`04_UML/`](../04_UML/) |
| **Estados SCMTA GD2 Failover** (estados 15-20) | 14_UML_SCMTA_GD2_StateMachine.puml | [`04_UML/`](../04_UML/) |
| **Arquitectura Sistema** | 15_UML_System_Architecture.puml | [`04_UML/`](../04_UML/) |
| **Estados Driver MTZ** | 12_UML_MTZ_Driver_StateMachine.puml | [`04_UML/`](../04_UML/) |
| **Actividad deslastre** | 13_UML_SHED_Activity.puml | [`04_UML/`](../04_UML/) |

**Visualizar PlantUML**:
- Online: [plantuml.com/es/](http://www.plantuml.com/plantuml)
- VS Code: Extensión "PlantUML"

---

### **📚 Manuales Equipos**

| Qué necesitas | Archivo | Ubicación |
|---------------|---------|-----------|
| **Manual S7-1200** | s71200_system_manual_en-US_en-US.pdf | [`05_MANUALES/`](../05_MANUALES/) |
| **Guía programación TIA** | 81318674_Programming_guideline_DOC_v16_en.pdf | [`05_MANUALES/`](../05_MANUALES/) |
| **Manual Masterpact MTZ** | MTZ MANUAL.pdf | [`05_MANUALES/`](../05_MANUALES/) |
| **Manual Compact NSX** | NSX MANUAL.pdf | [`05_MANUALES/`](../05_MANUALES/) |
| **Especificaciones MTZ1/MTZ2** | masterpact mtz1 y mtz2.pdf | [`05_MANUALES/`](../05_MANUALES/) |
| **Procedimiento escritura MTZ** | Escritura_MTZ.pdf | [`05_MANUALES/`](../05_MANUALES/) |
| **Comparación S7-1500** | s7_1500_compare_table_en_mnemo.pdf | [`05_MANUALES/`](../05_MANUALES/) |

---

### **⚙️ Configuración TGBT**

| Qué necesitas | Archivo | Ubicación |
|---------------|---------|-----------|
| **Listado I/O (DI/DO)** | TGBT_Config - listado de entradas y salidas.pdf | [`06_CONFIG/`](../06_CONFIG/) |
| **Listado equipos Modbus** | TGBT_Config - listado de equipos.pdf | [`06_CONFIG/`](../06_CONFIG/) |
| **Configuración PM5350** | TGBT_Config - pm5330.pdf | [`06_CONFIG/`](../06_CONFIG/) |
| **Esquema montaje tablero** | ET MONTAJE-TGBT.pdf | [`06_CONFIG/`](../06_CONFIG/) |

---

### **🔄 Conversiones LADDER (Referencia)**

| Qué necesitas | Archivo | Ubicación |
|---------------|---------|-----------|
| **FB_IO_NORMALIZE en LADDER** | LADDER_01_FB_IO_NORMALIZE.md | [`02_LADDER/`](../02_LADDER/) |
| **FB_OUTPUTS en LADDER** | LADDER_05_FB_OUTPUTS.md | [`02_LADDER/`](../02_LADDER/) |
| **OB1_MAIN en LADDER** | LADDER_10_OB1_MAIN.md | [`02_LADDER/`](../02_LADDER/) |

---

## 10) Entregables Esperados del Software PLC

### **10.1 Código PLC (TIA Portal V18)**

✅ **Archivo proyecto**: `TGBT_SCMTA.zap18` (archivo comprimido TIA Portal)

✅ **Contenido**:
- 7 Function Blocks (FB_IO_NORMALIZE, FB_SCMTA, FB_SHED, etc.)
- 2 Data Blocks (DB_GLOBAL_STATUS, DB_PARAMS)
- 1 Organization Block (OB1_MAIN)
- Configuración hardware (CPU S7-1200 + CM1241 RS485)
- Tablas de símbolos completas
- Watch tables de testing

---

### **10.2 Documentación**

✅ **Manual de usuario PLC** (documento Word/PDF):

**Contenido mínimo**:
1. Descripción general sistema SCMTA
2. Modos de operación (Auto/Manual, Local/Remoto)
3. Secuencias transferencia (Red↔GD)
4. Deslastre cargas (criterios y prioridades)
5. Lista completa de alarmas con descripción
6. Parámetros editables (tabla con rangos y defaults)
7. Mapeo I/O completo (direcciones físicas)
8. Direcciones Modbus equipos
9. Troubleshooting (problemas comunes)

✅ **Reporte de testing**:
- Escenarios probados
- Resultados (PASS/FAIL)
- Observaciones y ajustes realizados
- Firma responsable técnico

✅ **Lista de parámetros para HMI**:

| Tag HMI | Dirección PLC | Tipo | R/W | Descripción |
|---------|---------------|------|-----|-------------|
| MODE_AUTO | DB_GLOBAL_STATUS.MODE_AUTO | Bool | R | Modo automático activo |
| SCMTA_STATE | DB_GLOBAL_STATUS.SCMTA_STATE | Int | R | Estado máquina (0-20) |
| V_MIN_PCT | DB_PARAMS.V_MIN_PCT | Real | R/W | Umbral subtensión [%] |
| ... | ... | ... | ... | ... |

---

### **10.3 Diagramas**

✅ **Diagrama de estados SCMTA** (PDF):
- 21 estados con transiciones (incluyendo failover GD1↔GD2)
- Timeouts indicados
- Condiciones de transición

✅ **Diagrama arquitectura software**:
- Relación entre FBs
- Flujo de datos
- Prioridades árbitro

✅ **Esquema Modbus RTU**:
- Topología red (daisy chain)
- Direcciones equipos
- Configuración puerto (baudrate, parity, etc.)

---

### **10.4 Backup y Versionado**

✅ **Control de versiones**:

```
📁 Backups/
├── v1.0_2026-02-04_inicial.zap18
├── v1.1_2026-02-10_ajuste_timeouts.zap18
├── v1.2_2026-02-15_modbus_integrado.zap18
└── v2.0_2026-02-20_comisionamiento.zap18
```

✅ **Changelog** (archivo de texto):

```
v2.0 - 2026-02-20 - Comisionamiento completado
- Ajuste T_GRID_STABLE a 120s según pruebas campo
- Modificación SHED_ORDER según operación
- Agregado timeout Modbus a 5s
- Corrección alarma interlock

v1.2 - 2026-02-15 - Integración Modbus
- Implementación MB_CLIENT en drivers
- Testing comunicación MTZ/NSX
- Ajuste REQ 2 segundos

v1.1 - 2026-02-10 - Ajuste timeouts
- T_GD_COOLDOWN reducido a 60s
- SHED_ON_PCT ajustado a 90%

v1.0 - 2026-02-04 - Versión inicial
- Código base completo
- Testing en simulación OK
```

---

### **10.5 Capacitación**

✅ **Sesión capacitación para operación**:
- Duración: 2-4 horas
- Temas: Modos operación, HMI, alarmas, emergencias
- Material: Presentación PowerPoint + demostración en vivo

✅ **Sesión capacitación para mantenimiento**:
- Duración: 4-8 horas
- Temas: Arquitectura PLC, Modbus, troubleshooting, modificaciones
- Material: Código comentado + ejercicios prácticos

---

## 11) Checklist Final Antes de Entrega

### **Pre-Entrega**

- [ ] Código compila sin errores ni warnings
- [ ] Mapeo I/O completo y verificado con listado oficial
- [ ] Parámetros ajustados según especificaciones
- [ ] Direcciones Modbus configuradas correctamente
- [ ] Testing en simulación: todos los escenarios PASS
- [ ] Testing con hardware real: comunicación Modbus OK
- [ ] Comisionamiento en campo: transferencias probadas
- [ ] Deslastre probado (si condiciones lo permiten)
- [ ] Enclavamientos verificados funcionando
- [ ] Alarmas probadas y textos correctos

### **Documentación**

- [ ] Manual de usuario completo
- [ ] Reporte testing firmado
- [ ] Diagramas actualizados con ajustes finales
- [ ] Lista parámetros HMI entregada
- [ ] Changelog actualizado

### **Entregables**

- [ ] Proyecto TIA Portal (.zap18) en USB + nube
- [ ] Backup múltiples versiones
- [ ] Documentación PDF impresa + digital
- [ ] Capacitación operación realizada
- [ ] Capacitación mantenimiento realizada
- [ ] Acta entrega firmada

---

## 12) Contactos y Soporte

**Proyecto**: Sistema SCMTA TGBT  
**Cliente**: [Nombre empresa]  
**Integrador**: [Nombre integrador]  

**Responsables técnicos**:
- Ingeniero proyecto: [Nombre]
- Programador PLC: [Tu nombre]
- Supervisor eléctrico: [Nombre]
- Operación cliente: [Nombre]

**Soporte técnico**:
- Siemens Argentina: +54 11 xxxx-xxxx
- Schneider Electric Argentina: +54 11 xxxx-xxxx

---

## ✅ ¡Éxito en el Proyecto!

Este documento debería darte una visión completa del sistema SCMTA y una guía clara de trabajo. Cualquier duda, consulta la documentación detallada en la carpeta [`03_DOCS/`](../03_DOCS/).

**Recuerda**: La seguridad es lo primero. Siempre verifica los enclavamientos antes de cualquier maniobra.

---

**Fecha**: 10 de febrero de 2026  
**Versión documento**: 3.0  
**Próxima revisión**: Post-comisionamiento
