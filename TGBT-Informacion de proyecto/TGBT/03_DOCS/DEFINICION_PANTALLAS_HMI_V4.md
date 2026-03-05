# DEFINICIÓN DE PANTALLAS HMI — V4.0
## TGBT SCMTA — Sistema de Conmutación Manual con Transferencia Automática

**Proyecto:** TGBT IND-26-PTE-15  
**Versión:** 4.0 (Cambio de alcance: E/S Digitales para interruptores, PM5350P solo lectura)  
**Panel:** TIA Portal V18 — KTP700 Basic Color PN (o compatible)  
**Fecha de revisión:** 2026  

---

## ÍNDICE DE PANTALLAS

| # | Nombre | Descripción |
|---|--------|-------------|
| 1 | Sinóptico Principal | Vista general del sistema, estado de interruptores |
| 2 | Estado SCMTA | Máquina de estados, fallas, modo AUTO/MANUAL |
| 3 | Mediciones PM5350P | Lecturas por Tablero (C02, C01-GD1/GD2, C03–C06) |
| 4 | Control Manual | Botones de apertura/cierre en MANUAL |
| 5 | Parámetros del Sistema | Umbrales de tensión/frecuencia, tiempos, habilitaciones |
| 6 | Alarmas y Eventos | Historial de alarmas, reconocimiento |

---

## PANTALLA 1 — SINÓPTICO PRINCIPAL

### Descripción
Vista de una línea del tablero TGBT. Permite supervisar el estado de todos los interruptores y el modo de operación activo sin necesidad de navegar a otras pantallas.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  TGBT SCMTA  [●AUTOMÁTICO]  [○MANUAL]        [!] ALARMAS  [?] INFO │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   RED (C02)          BUS BARRA            GD1 (C01)  GD2 (C01)    │
│   ──●──              ─────────            ──●──      ──○──         │
│   [QT1]              ═══════════          [QG1]      [QG2]*        │
│   ──●──              ║       ║            ──●──      ──○──         │
│    ▼CERRADO          ║       ║             ▼CERRADO   ▼ABIERTO     │
│                      ║   ║   ║                                     │
│                     C03 C04 C05-C06                                │
│                      ║   ║   ║                                     │
│                     [Q22: ABIERTO / REMOTO]                        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ESTADO: NORMAL_ON_GRID          [CÓDIGO FALLA: ---]         │   │
│  │ ■ EN RED   □ EN GD   □ TRANSFIRIENDO   □ FALLA              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  [MEDICIONES]  [PARÁMETROS]  [ALARMAS]  [CONTROL]                  │
└─────────────────────────────────────────────────────────────────────┘
* GD2 / QG2 aparece en gris si ENABLE_QG2 = FALSE
```

### Variables HMI vinculadas

| Elemento Visual | Variable DB | Tipo | Descripción |
|-----------------|-------------|------|-------------|
| Símbolo QT1 | `DATA_BUFF.QT1_CLOSED` | Bool | Verde=cerrado, gris=abierto |
| Símbolo QT1 FAULT | `DATA_BUFF.QT1_FAULT` | Bool | Rojo parpadeante |
| Símbolo QT1 REMOTE | `DATA_BUFF.QT1_REMOTE` | Bool | Icono candado abierto/cerrado |
| Símbolo QG1 | `DATA_BUFF.QG1_CLOSED` | Bool | Verde=cerrado |
| Símbolo QG1 FAULT | `DATA_BUFF.QG1_FAULT` | Bool | Rojo parpadeante |
| Símbolo QG2* | `DATA_BUFF.QG2_CLOSED` | Bool | Visible solo si ENABLE_QG2 |
| Símbolo Q22 | `DATA_BUFF.Q22_REMOTE_ALLOWED` | Bool | Indica modo REMOTO |
| BUSBAR UV/OV | `DATA_BUFF.BUSBAR_UV_OV_DI` | Bool | Triángulo advertencia |
| Estado SCMTA | `DATA_BUFF.SCMTA_STATE_NAME` | WString | Texto estado actual |
| IS_ON_GRID | `DATA_BUFF.IS_ON_GRID` | Bool | Barra estado verde |
| IS_ON_GD | `DATA_BUFF.IS_ON_GD` | Bool | Barra estado azul |
| IS_IN_TRANSFER | `DATA_BUFF.IS_IN_TRANSFER` | Bool | Barra estado amarillo |
| IS_FAULT | `DATA_BUFF.IS_FAULT` | Bool | Barra estado rojo |

### Indicadores de color de interruptor

| Condición | Color |
|-----------|-------|
| CLOSED=TRUE, FAULT=FALSE | Verde sólido |
| CLOSED=FALSE, FAULT=FALSE | Gris sólido |
| FAULT=TRUE | Rojo parpadeante (1 Hz) |
| Sin señal REMOTE | Fondo naranja |

---

## PANTALLA 2 — ESTADO SCMTA

### Descripción
Detalle completo de la máquina de estados. Incluye estado actual, tiempo transcurrido, código de falla, y botones de acción en modo MANUAL/AUTO.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  ◄ INICIO     ESTADO SCMTA V4                    [RESET FALLA]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Estado actual:  ┌─────────────────────────┐                       │
│                  │  NORMAL_ON_GRID          │  ◄ WString            │
│                  └─────────────────────────┘                       │
│  Tiempo en estado: [   00:01:23  ]  hh:mm:ss                       │
│  Código de falla:  [     ---     ]                                  │
│                                                                     │
│  ┌──────────── MODO ──────────────┐                                 │
│  │  [●] AUTOMÁTICO  [○] MANUAL    │  Toggle bit MODE_AUTO           │
│  └────────────────────────────────┘                                 │
│                                                                     │
│  ┌──────────── ESTADO GD ─────────────────────┐                    │
│  │  GD1: [LISTO ●] [CORRIENDO ●] [ALARMA ○]   │                    │
│  │  GD2: [LISTO ○] [CORRIENDO ○] [ALARMA ○]   │ *gris si !ENABLE   │
│  └────────────────────────────────────────────┘                    │
│                                                                     │
│  ┌──────────── FLAGS SCMTA ───────────────────┐                    │
│  │  □ IS_ON_GRID     □ IS_ON_GD                │                    │
│  │  □ IS_ON_GD1      □ IS_ON_GD2               │                    │
│  │  □ IS_IN_TRANSFER □ GRID_OK                 │                    │
│  │  □ GRID_FAIL      □ SHED_ACTIVE             │                    │
│  └────────────────────────────────────────────┘                    │
│                                                                     │
│  Última transferencia: [  00:04:11  ]  hh:mm:ss                    │
│  GD1 disponible: [●]    GD2 disponible: [○]                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Variables HMI vinculadas

| Elemento | Variable | Tipo | Acción |
|----------|----------|------|--------|
| Nombre estado | `DATA_BUFF.SCMTA_STATE_NAME` | WString | Solo lectura |
| Número estado | `DATA_BUFF.SCMTA_STATE` | Int | Solo lectura |
| Tiempo en estado | `DATA_BUFF.ELAPSED_TIME` | Time | Formato hh:mm:ss |
| Código falla | `DATA_BUFF.FAULT_CODE` | Int | Solo lectura (--- si 0) |
| Botón RESET FALLA | `DATA_BUFF.RESET_FAULT` | Bool | Pulso al soltar |
| Toggle AUTO | `DATA_BUFF.MODE_AUTO` | Bool | Escritura bit |
| GD1 READY | `DATA_BUFF.GD_READY` | Bool | Indicador |
| GD1 RUNNING | `DATA_BUFF.GD_RUNNING` | Bool | Indicador |
| GD1 ALARM | `DATA_BUFF.GD_ALARM` | Bool | Indicador rojo |
| GD2 READY | `DATA_BUFF.GD2_READY` | Bool | Solo si ENABLE_QG2 |
| GD2 ALARM | `DATA_BUFF.GD2_ALARM` | Bool | Solo si ENABLE_QG2 |
| IS_ON_GRID | `DATA_BUFF.IS_ON_GRID` | Bool | Indicador |
| IS_ON_GD | `DATA_BUFF.IS_ON_GD` | Bool | Indicador |
| GRID_OK | `DATA_BUFF.GRID_OK` | Bool | Indicador |
| GRID_FAIL | `DATA_BUFF.GRID_FAIL` | Bool | Indicador rojo |
| Última transferencia | `DATA_BUFF.DIAG_LAST_TRANSFER_TIME` | Time | |
| GD1 disponible | `DATA_BUFF.GD1_AVAILABLE` | Bool | |
| GD2 disponible | `DATA_BUFF.GD2_AVAILABLE` | Bool | Solo si ENABLE_QG2 |

### Tabla de estados SCMTA para referencia HMI

| STATE (Int) | STATE_NAME | Color sugerido |
|-------------|-----------|----------------|
| 0 | INIT | Gris |
| 1 | NORMAL_ON_GRID | Verde |
| 2 | GRID_FAIL_DETECTED | Amarillo |
| 3 | OPEN_QT1 | Amarillo parpadeante |
| 4 | START_GD1_DELAY | Azul claro |
| 5 | START_GD1 | Azul |
| 6 | WAIT_GD1_READY | Azul |
| 7 | CLOSE_QG1 | Azul parpadeante |
| 8 | ON_GD1 | Azul sólido |
| 9 | GRID_RETURN_DETECTED | Verde parpadeante |
| 10 | WAIT_GRID_STABLE | Verde parpadeante |
| 11 | OPEN_ACTIVE_GD | Amarillo parpadeante |
| 12 | CLOSE_QT1 | Amarillo parpadeante |
| 13 | GD_COOLDOWN | Azul claro |
| 14 | FAULT_LOCKOUT | Rojo |
| 15 | START_GD2_DELAY | Violeta claro |
| 16 | START_GD2 | Violeta |
| 17 | WAIT_GD2_READY | Violeta |
| 18 | CLOSE_QG2 | Violeta parpadeante |
| 19 | ON_GD2 | Violeta sólido |
| 20 | OPEN_GD_FOR_SWITCH | Violeta parpadeante |

---

## PANTALLA 3 — MEDICIONES PM5350P

### Descripción
Lecturas de los 7 medidores PM5350P conectados via Modbus RTU. Permite verificar calidad de red y estado de comunicaciones.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  ◄ INICIO     MEDICIONES PM5350P                   Estado Modbus:  │
│                                                    [COMM: OK ●]    │
├──────────┬──────────┬──────────┬──────────┬────────────────────────┤
│ Tablero  │ V L1-L2  │ V L2-L3  │ V L3-L1  │  FREQ    P_TOTAL  COM │
├──────────┼──────────┼──────────┼──────────┼──────────┬───────┬─────┤
│ C02 (RED)│  4160 V  │  4160 V  │  4160 V  │  60.0 Hz │ --- kW│ ● │
│ C01-GD1  │  4140 V  │  4142 V  │  4138 V  │  59.9 Hz │  85 kW│ ● │
│ C01-GD2  │   --- V  │   --- V  │   --- V  │  --- Hz  │ --- kW│ ○ │
│ C03      │  4158 V  │  4160 V  │  4159 V  │  60.0 Hz │  40 kW│ ● │
│ C04      │  4155 V  │  4157 V  │  4156 V  │  60.0 Hz │  55 kW│ ● │
│ C05      │  4150 V  │  4153 V  │  4152 V  │  60.0 Hz │  30 kW│ ● │
│ C06/Q22  │  4145 V  │  4148 V  │  4147 V  │  59.9 Hz │  20 kW│ ● │
└──────────┴──────────┴──────────┴──────────┴──────────┴───────┴─────┘
                                                  ● = Comunicación OK
                                                  ○ = Sin comunicación

  GRID_MEAS_OK: [●]   Dispositivo activo: [ 3 ]
```

### Variables HMI vinculadas

| Elemento | Variable | Índice | Nota |
|----------|----------|--------|------|
| V_L1L2 C02 | `06_FB_MODBUS_MANAGER_DB.PM_V_L1L2[1]` | 1=C02 | Muestra en V |
| V_L1L2 C01-GD1 | `06_FB_MODBUS_MANAGER_DB.PM_V_L1L2[2]` | 2=C01-GD1 | |
| V_L1L2 C01-GD2 | `06_FB_MODBUS_MANAGER_DB.PM_V_L1L2[3]` | 3=C01-GD2 | |
| V_L1L2 C03 | `06_FB_MODBUS_MANAGER_DB.PM_V_L1L2[4]` | | |
| V_L1L2 C04 | `06_FB_MODBUS_MANAGER_DB.PM_V_L1L2[5]` | | |
| V_L1L2 C05 | `06_FB_MODBUS_MANAGER_DB.PM_V_L1L2[6]` | | |
| V_L1L2 C06 | `06_FB_MODBUS_MANAGER_DB.PM_V_L1L2[7]` | | |
| FREQ C02 | `06_FB_MODBUS_MANAGER_DB.PM_FREQ[1]` | | Hz |
| P_TOTAL C01-GD1 | `06_FB_MODBUS_MANAGER_DB.PM_P_TOTAL[2]` | | kW |
| P_TOTAL C01-GD2 | `06_FB_MODBUS_MANAGER_DB.PM_P_TOTAL[3]` | | kW |
| COMM_OK[1] | `06_FB_MODBUS_MANAGER_DB.PM_COMM_OK[1]` | | Bool |
| GRID_MEAS_OK | `DATA_BUFF.GRID_MEASUREMENT_OK` | | Bool |
| Disp. activo | `DATA_BUFF.MODBUS_ACTIVE_DEVICE` | | Int |

> **Nota:** Los registros de V y FREQ del tabiero C02 son los que alimentan la lógica de detección de falla RED en FB_SCMTA. Si GRID_MEAS_OK=FALSE, la lógica cae en modo DI de respaldo (BUSBAR_UV_OV_DI).

---

## PANTALLA 4 — CONTROL MANUAL

### Descripción
Disponible solo cuando MODE_MANUAL=TRUE. Permite operar individualmente cada interruptor. Todos los comandos requieren activo MODE_MANUAL y que el interruptor esté en REMOTE.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  ◄ INICIO     CONTROL MANUAL               MODO: [MANUAL ●]        │
├─────────────────────────────────────────────────────────────────────┤
│  ⚠ ATENCIÓN: Modo manual inhibe la transferencia automática         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  QT1  Estado: [CERRADO ●]  REMOTE: [●]  FAULT: [○]                 │
│       [ABRIR QT1]                [CERRAR QT1]                       │
│                                                                     │
│  QG1  Estado: [ABIERTO ○]  REMOTE: [●]  FAULT: [○]                 │
│       [ABRIR QG1]                [CERRAR QG1]                       │
│                                                                     │
│  QG2  Estado: [ABIERTO ○]  REMOTE: [●]  FAULT: [○]    *Inhabilitado│
│       [ABRIR QG2]                [CERRAR QG2]           si !ENABLE  │
│                                                                     │
│  Q22  Estado: [ABIERTO ○]  REMOTE: [●]                             │
│       [ABRIR Q22]                [CERRAR Q22]                       │
│                                                                     │
│  GD1  [ARRANCAR GD1]             [DETENER GD1]                      │
│  GD2  [ARRANCAR GD2]             [DETENER GD2]        *si ENABLE_QG2│
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ BLOQUEOS ACTIVOS:                                           │    │
│  │ □ BLOCK_INTERLOCK   □ BLOCK_CONFLICT   □ BLOCK_LOCAL       │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Variables HMI vinculadas

| Botón | Variable (escritura bit) | Condición habilitado |
|-------|--------------------------|---------------------|
| ABRIR QT1 | `DATA_BUFF.REQ_MAN_QT1_OPEN` | MODE_MANUAL AND QT1_REMOTE |
| CERRAR QT1 | `DATA_BUFF.REQ_MAN_QT1_CLOSE` | MODE_MANUAL AND QT1_REMOTE |
| ABRIR QG1 | `DATA_BUFF.REQ_MAN_QG1_OPEN` | MODE_MANUAL AND QG1_REMOTE |
| CERRAR QG1 | `DATA_BUFF.REQ_MAN_QG1_CLOSE` | MODE_MANUAL AND QG1_REMOTE |
| ABRIR QG2 | `DATA_BUFF.REQ_MAN_QG2_OPEN` | MODE_MANUAL AND QG2_REMOTE AND ENABLE_QG2 |
| CERRAR QG2 | `DATA_BUFF.REQ_MAN_QG2_CLOSE` | MODE_MANUAL AND QG2_REMOTE AND ENABLE_QG2 |
| ABRIR Q22 | `DATA_BUFF.REQ_MAN_Q22_OPEN` | MODE_MANUAL AND Q22_REMOTE |
| CERRAR Q22 | `DATA_BUFF.REQ_MAN_Q22_CLOSE` | MODE_MANUAL AND Q22_REMOTE |

> **Todos los botones son de pulso único (on-press, reset on-release)**  
> Los comandos generan pulsos DO de 300ms hacia %Q0.0–%Q0.7  
> La confirmación es por DI de posición (QxT1_CLOSED)

---

## PANTALLA 5 — PARÁMETROS DEL SISTEMA

### Descripción
Configuración de umbrales de calidad de red, tiempos de transferencia y habilitaciones. Requiere nivel de acceso técnico (password).

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  ◄ INICIO     PARÁMETROS SISTEMA        [🔒 Nivel Técnico]          │
├─────────────────────┬───────────────────────────────────────────────┤
│  CALIDAD RED        │  TIEMPOS                                      │
│  V_NOM:   [4160] V  │  T_GRID_FAIL_FILTER:  [ 2000] ms             │
│  V_MIN%:  [  85] %  │  T_OPEN_QT1:          [ 2000] ms             │
│  V_MAX%:  [ 115] %  │  T_START_GD_DELAY:    [ 5000] ms             │
│  FREQ_NOM:[60.0] Hz │  T_GD_READY_TIMEOUT:  [30000] ms             │
│  FREQ_MIN:[58.0] Hz │  T_GD_STABILIZATION:  [ 3000] ms             │
│  FREQ_MAX:[62.0] Hz │  T_CLOSE_QG1:         [ 3000] ms             │
├─────────────────────┤  T_CLOSE_QG2:         [ 3000] ms             │
│  HABILITACIONES     │  T_GRID_STABLE:        [10000] ms             │
│  SCMTA:     [●]     │  T_OPEN_QG1:          [ 2000] ms             │
│  ENABLE_QG2:[○]     │  T_CLOSE_QT1:         [ 3000] ms             │
│  ENABLE_SHED:[○]    │  T_GD_COOLDOWN:       [30000] ms             │
│                     │  T_CMD_PULSE:         [  300] ms             │
│  GD1_POWER_NOM:     │  T_CMD_CONFIRM:       [ 2000] ms             │
│  [   500] kW        │                                               │
│  GD2_POWER_NOM:     │                                               │
│  [   500] kW        │                                               │
│                     │                                               │
└─────────────────────┴───────────────────────────────────────────────┘
                        [GUARDAR]   [RESTAURAR DEFAULTS]
```

### Variables HMI vinculadas

| Elemento | Variable | Tipo | Rango sugerido |
|----------|----------|------|----------------|
| V_NOM | `DB_PARAMS.V_NOM` | Real | 1000..15000 V |
| V_MIN_PCT | `DB_PARAMS.V_MIN_PCT` | Real | 70..95 % |
| V_MAX_PCT | `DB_PARAMS.V_MAX_PCT` | Real | 105..130 % |
| FREQ_NOM | `DB_PARAMS.FREQ_NOM` | Real | 50 o 60 Hz |
| FREQ_MIN | `DB_PARAMS.FREQ_MIN` | Real | 45..58 Hz |
| FREQ_MAX | `DB_PARAMS.FREQ_MAX` | Real | 62..66 Hz |
| ENABLE_SCMTA | `DB_PARAMS.ENABLE_SCMTA` | Bool | Toggle |
| ENABLE_QG2 | `DB_PARAMS.ENABLE_QG2` | Bool | Toggle |
| ENABLE_SHED | `DB_PARAMS.ENABLE_SHED` | Bool | Toggle |
| GD1_POWER_NOMINAL | `DB_PARAMS.GD1_POWER_NOMINAL` | Real | kW |
| GD2_POWER_NOMINAL | `DB_PARAMS.GD2_POWER_NOMINAL` | Real | kW |
| T_GRID_FAIL_FILTER | `DB_PARAMS.T_GRID_FAIL_FILTER` | Time | ms |
| T_START_GD_DELAY | `DB_PARAMS.T_START_GD_DELAY` | Time | ms |
| T_GD_READY_TIMEOUT | `DB_PARAMS.T_GD_READY_TIMEOUT` | Time | ms |
| T_GD_STABILIZATION | `DB_PARAMS.T_GD_STABILIZATION` | Time | ms |
| T_CLOSE_QG1 | `DB_PARAMS.T_CLOSE_QG1` | Time | ms |
| T_GRID_STABLE | `DB_PARAMS.T_GRID_STABLE` | Time | ms |
| T_GD_COOLDOWN | `DB_PARAMS.T_GD_COOLDOWN` | Time | ms |
| T_CMD_PULSE | `DB_PARAMS.T_CMD_PULSE` | Time | ms — solo lectura recomendado |
| T_CMD_CONFIRM | `DB_PARAMS.T_CMD_CONFIRM` | Time | ms |

---

## PANTALLA 6 — ALARMAS Y EVENTOS

### Descripción
Historial de alarmas generadas por el sistema. Permite reconocer alarmas pendientes y ver el historial de eventos.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  ◄ INICIO     ALARMAS Y EVENTOS                 [ACK TODAS]        │
├─────┬────────────────────────────────────────┬──────────┬──────────┤
│ ▲/▼ │ Descripción                            │ Hora     │ Estado   │
├─────┼────────────────────────────────────────┼──────────┼──────────┤
│ [!] │ FALLA 101 — QT1 no abrió en tiempo     │ 14:22:31 │ NO ACK ● │
│ [!] │ QT1 no en REMOTO (111)                 │ 09:15:44 │ ACK ○    │
│ [i] │ Transferencia a GD1 iniciada           │ 14:22:29 │ INFO     │
│ [i] │ Falla de RED detectada                 │ 14:22:27 │ INFO     │
│ [✓] │ Retorno a RED completado               │ 07:10:12 │ INFO     │
└─────┴────────────────────────────────────────┴──────────┴──────────┘

  Alarma activa: [ FAULT — CÓDIGO 101               ]
  Texto HMI:     [ QT1 NO ABRIO EN TIEMPO CONFIGURADO]

  [ACK ALARMA ACTIVA]    [LIMPIAR HISTORIAL]    [RESET FALLA]
```

### Variables HMI vinculadas

| Elemento | Variable | Tipo |
|----------|----------|------|
| Alarma activa | `DATA_BUFF.IS_FAULT` | Bool |
| Código 3de falla | `DATA_BUFF.FAULT_CODE` | Int |
| Texto alarma activo | `DATA_BUFF.HMI_ALARM_TEXT` | WString |
| ACK alarma | `DATA_BUFF.ACK_ALARM` | Bool (pulso) |
| HMI alarm active | `DATA_BUFF.HMI_ALARM_ACTIVE` | Bool |
| RESET FALLA | `DATA_BUFF.RESET_FAULT` | Bool (pulso) |

### Tabla de alarmas y códigos

| Código | Descripción | Causa probable | Acción operador |
|--------|-------------|----------------|-----------------|
| 0 | Sin falla | — | — |
| 101 | QT1 no abrió en tiempo | Falla mecánica, no en REMOTE | Inspeccionar QT1, verificar REMOTE |
| 102 | GD1 no listo en tiempo | GD1 no arranca, avería | Inspeccionar GD1, verificar alimentación |
| 103 | QG1 no cerró en tiempo | Falla mecánica QG1, interlocking | Inspeccionar QG1 |
| 104 | QGx no abrió (retorno) | Falla mecánica | Inspeccionar interruptor activo |
| 105 | QT1 no cerró (retorno) | Falla mecánica QT1 | Inspeccionar QT1 |
| 108 | GD2 no listo en tiempo | GD2 no arranca | Inspeccionar GD2 |
| 109 | QG2 no cerró en tiempo | Falla mecánica QG2 | Inspeccionar QG2 |
| 110 | Ambos GD no disponibles | GD1 y GD2 averiados | Intervención urgente |
| 111 | QT1 no en REMOTO | Selector en LOCAL | Poner QT1 en REMOTO |
| 112 | QG1 no en REMOTO | Selector en LOCAL | Poner QG1 en REMOTO |
| 113 | QG1 falla eléctrica | Trip protection | Inspeccionar QG1 |
| 114 | QG2 falla eléctrica | Trip protection | Inspeccionar QG2 |

---

## NOTAS DE IMPLEMENTACIÓN TIA PORTAL

### Configuración recomendada del panel KTP700
- **Resolución:** 800×480 px
- **Idioma:** Español
- **Actualización cíclica:** 500 ms para indicadores de estado
- **Actualización rápida:** 100 ms para bits FAULT / IS_IN_TRANSFER
- **Tiempo parpadeo:** 1 Hz para estados de falla

### Seguridad de acceso HMI

| Nivel | Pantallas accesibles | Password |
|-------|----------------------|----------|
| Operador (0) | 1, 2, 3, 6 | Sin password |
| Técnico (1) | Todas | Password técnico |
| Administrador (2) | Todas + diagnóstico | Password admin |

### Avisos de interlocking para operador
- Si botón control MANUAL está inhabilitado → mostrar tooltip "Interruptor no en REMOTO"
- Si MODE_AUTO=TRUE y operador toca CONTROL → mostrar diálogo "Cambiar a MANUAL primero"
- Si ENABLE_QG2=FALSE → ocultar/atenuar todo lo relacionado con GD2 y QG2

### Conexión variables con DATA_BUFF y DB_PARAMS
- Todos los tags HMI deben crearse en la tabla de tags del panel apuntando al **DB_GLOBAL_STATUS (DATA_BUFF)** y **DB_PARAMS**
- Usar **acceso absoluto** (sin optimización) si el panel no soporta acceso simbólico optimizado
- El nombre de instancia `"06_FB_MODBUS_MANAGER_DB"` debe ser accesible como DB estático para leer arrays PM desde HMI

---

*Documento generado para TGBT SCMTA V4 — Diciembre 2026*  
*Ref: ADENDA_CAMBIO_ALCANCE_IND-26-PTE-15*
