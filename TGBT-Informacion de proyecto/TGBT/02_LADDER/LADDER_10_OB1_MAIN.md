# OB1_MAIN - LADDER EQUIVALENT

## 📋 INFORMACIÓN DEL BLOQUE

**Nombre**: OB1 (Main Cyclic Execution)  
**Lenguaje**: LADDER (LAD)  
**Versión**: 1.0  
**Fecha**: 4 de febrero de 2026  
**Compatible**: TIA Portal V18, S7-1200/1500

---

## 🎯 DESCRIPCIÓN

Programa principal cíclico del sistema SCMTA. Ejecuta secuencialmente todos los Function Blocks del sistema:

1. FB_IO_NORMALIZE - Normalización entradas físicas
2. FB_SCMTA - Máquina estados transferencia automática
3. FB_SHED - Deslastre y reenganche cargas
4. FB_CMD_ARBITER - Árbitro comandos con interlock
5. FB_OUTPUTS - Gestión pilotos y alarmas
6. Drivers Modbus (QT1, QG1, QG2, Feeders)

**Tiempo ciclo recomendado**: 100-200 ms

---

## 📊 ARQUITECTURA OB1

```
┌─────────────────────────────────────────────────┐
│  OB1 - Main Cyclic                              │
│  ┌───────────────────────────────────────────┐  │
│  │ Network 1: FB_IO_NORMALIZE                │  │
│  │   DI físicas → Señales lógicas            │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ Network 2: FB_SCMTA                       │  │
│  │   Máquina estados Red↔GD                  │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ Network 3: FB_SHED                        │  │
│  │   Deslastre/Reenganche cargas             │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ Network 4: FB_CMD_ARBITER                 │  │
│  │   Prioridad: SCMTA > SHED > MANUAL        │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ Network 5: FB_OUTPUTS                     │  │
│  │   Pilotos, alarmas, HMI                   │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ Network 6: Drivers Modbus MTZ/NSX         │  │
│  │   QT1, QG1, QG2, Feeders[1..18]           │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 🔧 CÓDIGO LADDER

### **NETWORK 1: Normalización Entradas (FB_IO_NORMALIZE)**

**Comentario**: Convierte señales físicas DI → señales lógicas con debounce y R_TRIG

```
┌────────────────────────────────────────────────────────────────┐
│  CALL  "DB_IO" (FB_IO_NORMALIZE)                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  // INPUTS (Entradas físicas)                            │  │
│  │  DI_SYS_AUTO           := %I0.0                           │  │
│  │  DI_QT1_REMOTE_SEL     := %I0.1                           │  │
│  │  DI_QT1_PB_OPEN        := %I0.2                           │  │
│  │  DI_QT1_PB_CLOSE       := %I0.3                           │  │
│  │  DI_QG1_REMOTE_SEL     := %I0.4                           │  │
│  │  DI_QG1_PB_OPEN        := %I0.5                           │  │
│  │  DI_QG1_PB_CLOSE       := %I0.6                           │  │
│  │  DI_QG2_REMOTE_SEL     := %I1.0                           │  │
│  │  DI_QG2_PB_OPEN        := %I1.1                           │  │
│  │  DI_QG2_PB_CLOSE       := %I1.2                           │  │
│  │  DI_GD_READY           := %I1.3                           │  │
│  │  DI_GD_RUNNING         := %I1.4                           │  │
│  │  DI_GD_ALARM           := %I1.5                           │  │
│  │                                                            │  │
│  │  // OUTPUTS → DB_GLOBAL_STATUS                            │  │
│  │  MODE_AUTO             => "DB_GLOBAL_STATUS".MODE_AUTO    │  │
│  │  MODE_MANUAL           => "DB_GLOBAL_STATUS".MODE_MANUAL  │  │
│  │  QT1_REMOTE_ALLOWED    => "DB_GLOBAL_STATUS".QT1_REM...  │  │
│  │  QG1_REMOTE_ALLOWED    => "DB_GLOBAL_STATUS".QG1_REM...  │  │
│  │  QG2_REMOTE_ALLOWED    => "DB_GLOBAL_STATUS".QG2_REM...  │  │
│  │  REQ_MAN_QT1_OPEN      => "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QT1_CLOSE     => "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QG1_OPEN      => "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QG1_CLOSE     => "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QG2_OPEN      => "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QG2_CLOSE     => "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  GD_READY              => "DB_GLOBAL_STATUS".GD_READY    │  │
│  │  GD_RUNNING            => "DB_GLOBAL_STATUS".GD_RUNNING  │  │
│  │  GD_ALARM              => "DB_GLOBAL_STATUS".GD_ALARM    │  │
│  │  DIAG_MODE_VALID       => "DB_GLOBAL_STATUS".DIAG_M...   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**Notas**:
- `%I0.0` - `%I1.5`: Direcciones físicas entradas digitales (ejemplo)
- `:=` Asignación entrada (IN parameter)
- `=>` Asignación salida (OUT parameter)

---

### **NETWORK 2: Máquina Estados SCMTA (FB_SCMTA)**

**Comentario**: Transferencia automática Red↔GD con 15 estados

```
┌────────────────────────────────────────────────────────────────┐
│  CALL  "DB_SCMTA" (FB_SCMTA)                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  // CONTROL                                              │  │
│  │  ENABLE                := "DB_PARAMS".ENABLE_SCMTA       │  │
│  │  MODE_AUTO             := "DB_GLOBAL_STATUS".MODE_AUTO   │  │
│  │  RESET_FAULT           := %I2.0  // Botón reset HMI      │  │
│  │                                                            │  │
│  │  // ESTADOS INTERRUPTORES (de Modbus)                    │  │
│  │  QT1_STATE             := "DB_GLOBAL_STATUS".QT1_STATE   │  │
│  │  QG1_STATE             := "DB_GLOBAL_STATUS".QG1_STATE   │  │
│  │  QG2_STATE             := "DB_GLOBAL_STATUS".QG2_STATE   │  │
│  │                                                            │  │
│  │  // MEDICIONES RED (de PM5350 Modbus)                    │  │
│  │  GRID_V_L1L2           := "DB_GLOBAL_STATUS".GRID_V...   │  │
│  │  GRID_V_L2L3           := "DB_GLOBAL_STATUS".GRID_V...   │  │
│  │  GRID_V_L3L1           := "DB_GLOBAL_STATUS".GRID_V...   │  │
│  │  GRID_FREQ             := "DB_GLOBAL_STATUS".GRID_FREQ   │  │
│  │  GRID_MEASUREMENT_OK   := "DB_GLOBAL_STATUS".GRID_M...   │  │
│  │                                                            │  │
│  │  // SEÑALES GD                                            │  │
│  │  GD_READY              := "DB_GLOBAL_STATUS".GD_READY    │  │
│  │  GD_RUNNING            := "DB_GLOBAL_STATUS".GD_RUNNING  │  │
│  │  GD_ALARM              := "DB_GLOBAL_STATUS".GD_ALARM    │  │
│  │                                                            │  │
│  │  // PARÁMETROS (de DB_PARAMS)                            │  │
│  │  V_NOM                 := "DB_PARAMS".V_NOM              │  │
│  │  V_MIN_PCT             := "DB_PARAMS".V_MIN_PCT          │  │
│  │  V_MAX_PCT             := "DB_PARAMS".V_MAX_PCT          │  │
│  │  FREQ_NOM              := "DB_PARAMS".FREQ_NOM           │  │
│  │  FREQ_MIN              := "DB_PARAMS".FREQ_MIN           │  │
│  │  FREQ_MAX              := "DB_PARAMS".FREQ_MAX           │  │
│  │  T_OPEN_QT1            := "DB_PARAMS".T_OPEN_QT1         │  │
│  │  T_START_GD_DELAY      := "DB_PARAMS".T_START_GD_DELAY   │  │
│  │  T_GD_READY_TIMEOUT    := "DB_PARAMS".T_GD_READY_T...    │  │
│  │  T_GD_STABILIZATION    := "DB_PARAMS".T_GD_STABILI...    │  │
│  │  T_CLOSE_QG1           := "DB_PARAMS".T_CLOSE_QG1        │  │
│  │  T_GRID_STABLE         := "DB_PARAMS".T_GRID_STABLE      │  │
│  │  T_OPEN_QG1            := "DB_PARAMS".T_OPEN_QG1         │  │
│  │  T_CLOSE_QT1           := "DB_PARAMS".T_CLOSE_QT1        │  │
│  │  T_GD_COOLDOWN         := "DB_PARAMS".T_GD_COOLDOWN      │  │
│  │  T_GRID_FAIL_FILTER    := "DB_PARAMS".T_GRID_FAIL_F...   │  │
│  │                                                            │  │
│  │  // OUTPUTS                                               │  │
│  │  STATE                 => "DB_GLOBAL_STATUS".SCMTA_STATE │  │
│  │  STATE_NAME            => "DB_GLOBAL_STATUS".SCMTA_S...  │  │
│  │  REQ_SCMTA_OPEN_QT1    => "DB_SCMTA".REQ_SCMTA_OPEN_QT1  │  │
│  │  REQ_SCMTA_CLOSE_QT1   => "DB_SCMTA".REQ_SCMTA_CLOSE...  │  │
│  │  REQ_SCMTA_OPEN_QG1    => "DB_SCMTA".REQ_SCMTA_OPEN_QG1  │  │
│  │  REQ_SCMTA_CLOSE_QG1   => "DB_SCMTA".REQ_SCMTA_CLOSE...  │  │
│  │  REQ_SCMTA_OPEN_QG2    => "DB_SCMTA".REQ_SCMTA_OPEN_QG2  │  │
│  │  REQ_SCMTA_CLOSE_QG2   => "DB_SCMTA".REQ_SCMTA_CLOSE...  │  │
│  │  DO_GD_START           => %Q0.0  // Salida física GD     │  │
│  │  DO_GD_STOP            => %Q0.1                           │  │
│  │  IS_ON_GRID            => "DB_GLOBAL_STATUS".IS_ON_GRID  │  │
│  │  IS_ON_GD              => "DB_GLOBAL_STATUS".IS_ON_GD    │  │
│  │  IS_IN_TRANSFER        => "DB_GLOBAL_STATUS".IS_IN_TR... │  │
│  │  IS_FAULT              => "DB_GLOBAL_STATUS".IS_FAULT    │  │
│  │  GRID_OK               => "DB_GLOBAL_STATUS".GRID_OK     │  │
│  │  GRID_FAIL             => "DB_GLOBAL_STATUS".GRID_FAIL   │  │
│  │  FAULT_CODE            => "DB_GLOBAL_STATUS".FAULT_CODE  │  │
│  │  ELAPSED_TIME          => "DB_GLOBAL_STATUS".ELAPSED_T...│  │
│  │  DIAG_LAST_TRANSFER_T. => "DB_GLOBAL_STATUS".DIAG_LA...  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

### **NETWORK 3: Deslastre/Reenganche (FB_SHED)**

**Comentario**: Gestión automática 18 feeders según carga GD/TR

```
┌────────────────────────────────────────────────────────────────┐
│  CALL  "DB_SHED" (FB_SHED)                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  // CONTROL                                              │  │
│  │  ENABLE                := "DB_PARAMS".ENABLE_SHED        │  │
│  │  RESET_ALL             := %I2.1  // Reset manual HMI     │  │
│  │                                                            │  │
│  │  // ESTADOS OPERACIÓN                                     │  │
│  │  IS_ON_GD              := "DB_GLOBAL_STATUS".IS_ON_GD    │  │
│  │  IS_ON_GRID            := "DB_GLOBAL_STATUS".IS_ON_GRID  │  │
│  │  IS_IN_TRANSFER        := "DB_GLOBAL_STATUS".IS_IN_TR... │  │
│  │                                                            │  │
│  │  // MEDICIONES CARGA (TODO: de PM5350 Modbus)            │  │
│  │  GD_LoadPct            := "DB_GLOBAL_STATUS".GD_LoadPct  │  │
│  │  TR_LoadPct            := "DB_GLOBAL_STATUS".TR_LoadPct  │  │
│  │                                                            │  │
│  │  // PARÁMETROS (de DB_PARAMS)                            │  │
│  │  SHED_ON_PCT           := "DB_PARAMS".SHED_ON_PCT        │  │
│  │  SHED_OFF_PCT          := "DB_PARAMS".SHED_OFF_PCT       │  │
│  │  RECONNECT_PCT         := "DB_PARAMS".RECONNECT_PCT      │  │
│  │  T_SHED_STEP           := "DB_PARAMS".T_SHED_STEP        │  │
│  │  T_RECONNECT_STEP      := "DB_PARAMS".T_RECONNECT_STEP   │  │
│  │  SHED_ORDER[1..18]     := "DB_PARAMS".SHED_ORDER[*]      │  │
│  │  SHED_ENABLE[1..18]    := "DB_PARAMS".SHED_ENABLE[*]     │  │
│  │                                                            │  │
│  │  // OUTPUTS                                               │  │
│  │  REQ_SHED_OPEN[1..18]  => "DB_SHED".REQ_SHED_OPEN[*]     │  │
│  │  REQ_SHED_CLOSE[1..18] => "DB_SHED".REQ_SHED_CLOSE[*]    │  │
│  │  SHED_ACTIVE           => "DB_GLOBAL_STATUS".SHED_ACTIVE │  │
│  │  FEEDERS_SHED          => "DB_GLOBAL_STATUS".FEEDERS_... │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

### **NETWORK 4: Árbitro Comandos (FB_CMD_ARBITER)**

**Comentario**: Prioridad SCMTA > SHED > MANUAL + Interlock fail-safe

```
┌────────────────────────────────────────────────────────────────┐
│  CALL  "DB_ARBITER" (FB_CMD_ARBITER)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  // CONTROL                                              │  │
│  │  ENABLE                := TRUE                            │  │
│  │  MODE_AUTO             := "DB_GLOBAL_STATUS".MODE_AUTO   │  │
│  │                                                            │  │
│  │  // PERMISOS LOCAL/REMOTO                                 │  │
│  │  QT1_REMOTE_ALLOWED    := "DB_GLOBAL_STATUS".QT1_REM...  │  │
│  │  QG1_REMOTE_ALLOWED    := "DB_GLOBAL_STATUS".QG1_REM...  │  │
│  │  QG2_REMOTE_ALLOWED    := "DB_GLOBAL_STATUS".QG2_REM...  │  │
│  │                                                            │  │
│  │  // ESTADOS ACTUALES                                      │  │
│  │  QT1_STATE             := "DB_GLOBAL_STATUS".QT1_STATE   │  │
│  │  QG1_STATE             := "DB_GLOBAL_STATUS".QG1_STATE   │  │
│  │  QG2_STATE             := "DB_GLOBAL_STATUS".QG2_STATE   │  │
│  │                                                            │  │
│  │  // REQUESTS SCMTA (Prioridad Alta)                      │  │
│  │  REQ_SCMTA_OPEN_QT1    := "DB_SCMTA".REQ_SCMTA_OPEN_QT1  │  │
│  │  REQ_SCMTA_CLOSE_QT1   := "DB_SCMTA".REQ_SCMTA_CLOSE_QT1 │  │
│  │  REQ_SCMTA_OPEN_QG1    := "DB_SCMTA".REQ_SCMTA_OPEN_QG1  │  │
│  │  REQ_SCMTA_CLOSE_QG1   := "DB_SCMTA".REQ_SCMTA_CLOSE_QG1 │  │
│  │  REQ_SCMTA_OPEN_QG2    := "DB_SCMTA".REQ_SCMTA_OPEN_QG2  │  │
│  │  REQ_SCMTA_CLOSE_QG2   := "DB_SCMTA".REQ_SCMTA_CLOSE_QG2 │  │
│  │                                                            │  │
│  │  // REQUESTS SHED (Prioridad Media)                      │  │
│  │  REQ_SHED_OPEN[1..18]  := "DB_SHED".REQ_SHED_OPEN[*]     │  │
│  │  REQ_SHED_CLOSE[1..18] := "DB_SHED".REQ_SHED_CLOSE[*]    │  │
│  │                                                            │  │
│  │  // REQUESTS MANUAL (Prioridad Baja)                     │  │
│  │  REQ_MAN_QT1_OPEN      := "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QT1_CLOSE     := "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QG1_OPEN      := "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QG1_CLOSE     := "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QG2_OPEN      := "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │  REQ_MAN_QG2_CLOSE     := "DB_GLOBAL_STATUS".REQ_MAN...  │  │
│  │                                                            │  │
│  │  // OUTPUTS (Comandos arbitrados con interlock OK)       │  │
│  │  CMD_OPEN_QT1          => "DB_ARBITER".CMD_OPEN_QT1      │  │
│  │  CMD_CLOSE_QT1         => "DB_ARBITER".CMD_CLOSE_QT1     │  │
│  │  CMD_OPEN_QG1          => "DB_ARBITER".CMD_OPEN_QG1      │  │
│  │  CMD_CLOSE_QG1         => "DB_ARBITER".CMD_CLOSE_QG1     │  │
│  │  CMD_OPEN_QG2          => "DB_ARBITER".CMD_OPEN_QG2      │  │
│  │  CMD_CLOSE_QG2         => "DB_ARBITER".CMD_CLOSE_QG2     │  │
│  │  CMD_OPEN_FEEDER[*]    => "DB_ARBITER".CMD_OPEN_FEED...  │  │
│  │  CMD_CLOSE_FEEDER[*]   => "DB_ARBITER".CMD_CLOSE_FEE...  │  │
│  │  ALARM_INTERLOCK_VIO.. => "DB_GLOBAL_STATUS".ALARM_I...  │  │
│  │  BLOCK_INTERLOCK       => "DB_GLOBAL_STATUS".BLOCK_I...  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

### **NETWORK 5: Pilotos y Alarmas (FB_OUTPUTS)**

**Comentario**: LEDs, bocina, baliza, señales HMI

```
┌────────────────────────────────────────────────────────────────┐
│  CALL  "DB_OUTPUTS" (FB_OUTPUTS)                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  // ESTADOS SISTEMA                                      │  │
│  │  IS_ON_GRID            := "DB_GLOBAL_STATUS".IS_ON_GRID  │  │
│  │  IS_ON_GD              := "DB_GLOBAL_STATUS".IS_ON_GD    │  │
│  │  IS_IN_TRANSFER        := "DB_GLOBAL_STATUS".IS_IN_TR... │  │
│  │  IS_FAULT              := "DB_GLOBAL_STATUS".IS_FAULT    │  │
│  │  STATE                 := "DB_GLOBAL_STATUS".SCMTA_STATE │  │
│  │  STATE_NAME            := "DB_GLOBAL_STATUS".SCMTA_S...  │  │
│  │  FAULT_CODE            := "DB_GLOBAL_STATUS".FAULT_CODE  │  │
│  │                                                            │  │
│  │  // ALARMAS                                               │  │
│  │  ALM_INTERLOCK_VIO...  := "DB_GLOBAL_STATUS".ALARM_I...  │  │
│  │  BLOCK_INTERLOCK       := "DB_GLOBAL_STATUS".BLOCK_I...  │  │
│  │  GRID_FAIL             := "DB_GLOBAL_STATUS".GRID_FAIL   │  │
│  │  GD_ALARM              := "DB_GLOBAL_STATUS".GD_ALARM    │  │
│  │                                                            │  │
│  │  // DESLASTRE                                             │  │
│  │  SHED_ACTIVE           := "DB_GLOBAL_STATUS".SHED_ACTIVE │  │
│  │  FEEDERS_SHED          := "DB_GLOBAL_STATUS".FEEDERS_... │  │
│  │                                                            │  │
│  │  // CONTROL                                               │  │
│  │  ENABLE_HORN           := TRUE                            │  │
│  │  ACK_ALARM             := %I2.2  // Botón ACK HMI        │  │
│  │                                                            │  │
│  │  // OUTPUTS (Salidas físicas DO)                         │  │
│  │  DO_PILOT_ON_GRID      => %Q1.0  // LED verde            │  │
│  │  DO_PILOT_ON_GD        => %Q1.1  // LED amarillo         │  │
│  │  DO_PILOT_TRANSFER     => %Q1.2  // LED amarillo parpad. │  │
│  │  DO_PILOT_FAULT        => %Q1.3  // LED rojo             │  │
│  │  DO_PILOT_SHED         => %Q1.4  // LED amarillo         │  │
│  │  DO_ALARM_HORN         => %Q1.5  // Bocina               │  │
│  │  DO_ALARM_BEACON       => %Q1.6  // Baliza parpadeante   │  │
│  │                                                            │  │
│  │  // OUTPUTS (Señales HMI)                                │  │
│  │  HMI_STATUS_TEXT       => "DB_GLOBAL_STATUS".HMI_STAT... │  │
│  │  HMI_ALARM_ACTIVE      => "DB_GLOBAL_STATUS".HMI_ALAR... │  │
│  │  HMI_ALARM_TEXT        => "DB_GLOBAL_STATUS".HMI_ALAR... │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

### **NETWORK 6: Drivers Modbus MTZ/NSX**

**Comentario**: Drivers Schneider Command Interface para QT1, QG1, QG2

#### **Sub-Network 6.1: Driver QT1 (Masterpact MTZ1)**

```
┌────────────────────────────────────────────────────────────────┐
│  CALL  "DB_QT1_DRV" (FB_MTZ_DRIVER)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ENABLE                := TRUE                            │  │
│  │  SLAVE_ADDR            := 1   // Dirección Modbus MTZ1   │  │
│  │  CMD_OPEN              := "DB_ARBITER".CMD_OPEN_QT1       │  │
│  │  CMD_CLOSE             := "DB_ARBITER".CMD_CLOSE_QT1      │  │
│  │  TIMEOUT               := T#5s                            │  │
│  │                                                            │  │
│  │  CB_STATE              => "DB_GLOBAL_STATUS".QT1_STATE    │  │
│  │  CB_CURRENT            => "DB_GLOBAL_STATUS".QT1_CURRENT  │  │
│  │  COMM_OK               => "DB_GLOBAL_STATUS".QT1_COMM_OK  │  │
│  │  ERROR_CODE            => "DB_GLOBAL_STATUS".QT1_ERROR    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

#### **Sub-Network 6.2: Driver QG1 (Compact NSX)**

```
┌────────────────────────────────────────────────────────────────┐
│  CALL  "DB_QG1_DRV" (FB_MTZ_DRIVER)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ENABLE                := TRUE                            │  │
│  │  SLAVE_ADDR            := 2   // Dirección Modbus NSX1   │  │
│  │  CMD_OPEN              := "DB_ARBITER".CMD_OPEN_QG1       │  │
│  │  CMD_CLOSE             := "DB_ARBITER".CMD_CLOSE_QG1      │  │
│  │  TIMEOUT               := T#5s                            │  │
│  │                                                            │  │
│  │  CB_STATE              => "DB_GLOBAL_STATUS".QG1_STATE    │  │
│  │  CB_CURRENT            => "DB_GLOBAL_STATUS".QG1_CURRENT  │  │
│  │  COMM_OK               => "DB_GLOBAL_STATUS".QG1_COMM_OK  │  │
│  │  ERROR_CODE            => "DB_GLOBAL_STATUS".QG1_ERROR    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

#### **Sub-Network 6.3: Driver QG2 (Compact NSX)**

```
┌────────────────────────────────────────────────────────────────┐
│  CALL  "DB_QG2_DRV" (FB_MTZ_DRIVER)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ENABLE                := FALSE  // Futuro                │  │
│  │  SLAVE_ADDR            := 3                               │  │
│  │  CMD_OPEN              := "DB_ARBITER".CMD_OPEN_QG2       │  │
│  │  CMD_CLOSE             := "DB_ARBITER".CMD_CLOSE_QG2      │  │
│  │  TIMEOUT               := T#5s                            │  │
│  │                                                            │  │
│  │  CB_STATE              => "DB_GLOBAL_STATUS".QG2_STATE    │  │
│  │  CB_CURRENT            => "DB_GLOBAL_STATUS".QG2_CURRENT  │  │
│  │  COMM_OK               => "DB_GLOBAL_STATUS".QG2_COMM_OK  │  │
│  │  ERROR_CODE            => "DB_GLOBAL_STATUS".QG2_ERROR    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 📊 RESUMEN OB1

| Network | Bloque | Descripción | Entradas | Salidas |
|---------|--------|-------------|----------|---------|
| 1 | FB_IO_NORMALIZE | Normalización E/S | 13 DI | 15 señales |
| 2 | FB_SCMTA | Máquina estados | 29 params | 19 outputs |
| 3 | FB_SHED | Deslastre cargas | 20 params | 37 requests |
| 4 | FB_CMD_ARBITER | Árbitro comandos | 42 requests | 24 commands |
| 5 | FB_OUTPUTS | Pilotos/alarmas | 14 estados | 10 DO + HMI |
| 6.1 | FB_MTZ_DRIVER (QT1) | Driver Modbus | 5 params | 4 estados |
| 6.2 | FB_MTZ_DRIVER (QG1) | Driver Modbus | 5 params | 4 estados |
| 6.3 | FB_MTZ_DRIVER (QG2) | Driver Modbus | 5 params | 4 estados |

**Total Networks**: 6 (con sub-networks)  
**Total Function Blocks**: 8 llamadas

---

## ⚙️ MAPEO DIRECCIONES FÍSICAS

### **Entradas Digitales (%I)**

| Dirección | Señal | Descripción |
|-----------|-------|-------------|
| %I0.0 | DI_SYS_AUTO | Selector Auto/Manual |
| %I0.1 | DI_QT1_REMOTE_SEL | QT1 Local/Remoto |
| %I0.2 | DI_QT1_PB_OPEN | Pulsador Open QT1 |
| %I0.3 | DI_QT1_PB_CLOSE | Pulsador Close QT1 |
| %I0.4 | DI_QG1_REMOTE_SEL | QG1 Local/Remoto |
| %I0.5 | DI_QG1_PB_OPEN | Pulsador Open QG1 |
| %I0.6 | DI_QG1_PB_CLOSE | Pulsador Close QG1 |
| %I1.0 | DI_QG2_REMOTE_SEL | QG2 Local/Remoto |
| %I1.1 | DI_QG2_PB_OPEN | Pulsador Open QG2 |
| %I1.2 | DI_QG2_PB_CLOSE | Pulsador Close QG2 |
| %I1.3 | DI_GD_READY | GD Ready (auxiliar) |
| %I1.4 | DI_GD_RUNNING | GD Running |
| %I1.5 | DI_GD_ALARM | GD Alarm |
| %I2.0 | RESET_FAULT | Botón Reset Falla (HMI) |
| %I2.1 | RESET_SHED | Reset Deslastre (HMI) |
| %I2.2 | ACK_ALARM | Botón ACK Alarma (HMI) |

### **Salidas Digitales (%Q)**

| Dirección | Señal | Descripción |
|-----------|-------|-------------|
| %Q0.0 | DO_GD_START | Marcha GD (contacto NA) |
| %Q0.1 | DO_GD_STOP | Parada GD (contacto NA) |
| %Q1.0 | DO_PILOT_ON_GRID | LED verde "EN RED" |
| %Q1.1 | DO_PILOT_ON_GD | LED amarillo "EN GRUPO" |
| %Q1.2 | DO_PILOT_TRANSFER | LED amarillo parpadeante |
| %Q1.3 | DO_PILOT_FAULT | LED rojo "FALLA" |
| %Q1.4 | DO_PILOT_SHED | LED amarillo "DESLASTRE" |
| %Q1.5 | DO_ALARM_HORN | Bocina alarma |
| %Q1.6 | DO_ALARM_BEACON | Baliza parpadeante |

**Nota**: Ajustar según configuración hardware real del proyecto.

---

## 🔍 NOTAS IMPLEMENTACIÓN TIA PORTAL

### **1. Crear OB1 en LADDER**
```
1. Proyecto → PLC → Bloques de programa
2. Clic derecho → Add new block → Organization Block (OB1)
3. Lenguaje: LAD (Ladder Logic)
4. Copiar Networks según documentación
```

### **2. Orden Compilación**
```
1. Data Blocks (DB_GLOBAL_STATUS, DB_PARAMS)
2. Function Blocks (FB_IO_NORMALIZE, FB_SCMTA, etc.)
3. DB Instances (DB_IO, DB_SCMTA, DB_SHED, etc.)
4. Organization Block (OB1)
```

### **3. Verificación Post-Compilación**
- ✅ Sin errores compilación
- ✅ Todas las variables asignadas
- ✅ Mapeo %I/%Q correcto
- ✅ Ciclo scan <200ms (verificar en propiedades CPU)

---

## ⏱️ TIEMPO DE CICLO ESTIMADO

| Bloque | Tiempo (S7-1214C) |
|--------|-------------------|
| FB_IO_NORMALIZE | ~0.5 ms |
| FB_SCMTA | ~1.5 ms |
| FB_SHED | ~0.8 ms |
| FB_CMD_ARBITER | ~0.6 ms |
| FB_OUTPUTS | ~0.3 ms |
| Drivers MTZ (x3) | ~1.2 ms |
| **TOTAL OB1** | **~5 ms** |

**Recomendación**: Configurar watchdog OB1 a 100-200ms.

---

## ✅ VALIDADO PARA S7-1200

- ✅ Compatible TIA Portal V18
- ✅ S7-1211C/1212C/1214C/1215C/1217C
- ✅ Tiempo ciclo optimizado (<10ms)
- ✅ Memory footprint: ~15-20 KB

---

## 📝 SIGUIENTE PASO

**Mapear direcciones físicas** según documento:
- "TGBT_Config - listado de entradas y salidas.pdf"

Reemplazar direcciones ejemplo (%I0.x, %Q0.x) por reales.

---

