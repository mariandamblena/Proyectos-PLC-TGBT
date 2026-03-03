# Definición de Pantallas HMI — SCMTA TGBT

> **Versión:** 1.0  
> **Fecha:** 2026-02-23  
> **Sistema:** SCMTA V3.0 — S7-1215C + KTP/Comfort Panel  
> **Pantallas totales:** 6

---

## Resumen de Pantallas

| # | Nombre | Acceso | Función Principal |
|---|--------|--------|-------------------|
| 1 | **SINÓPTICO** | Todos | Unifilar general, estado fuentes, carga, modo sistema |
| 2 | **FEEDERS** | Todos (comandos: Admin) | Estado y comando de los 19 feeders Modbus |
| 3 | **MEDICIONES** | Todos | Tensiones, corrientes, potencias, frecuencia RED/GD/Trafo |
| 4 | **ALARMAS** | Todos (ACK: Admin) | Listado de alarmas activas e historial |
| 5 | **PARÁMETROS** | Solo Admin | Umbrales, tiempos, clasificación esencial, orden deslastre |
| 6 | **DIAGNÓSTICO** | Solo Admin | Comisionado, debug, Modbus, forzados, estados internos |

---

## Sistema de Roles

| Rol | User | Password | Permisos |
|-----|------|----------|----------|
| **Operador** | `oper` | (definir) | Visualización completa. Sin comandos ni cambio de parámetros |
| **Admin** | `admin` | (definir) | Todo: comandos de maniobra, cambio parámetros, ACK alarmas, forzado debug |

> En TIA Portal se configura con **User Administration** en el panel HMI. Cada botón de comando se protege con nivel de acceso "Admin".

---

## Navegación

```
┌─────────────┐
│  SINÓPTICO  │◄──── Pantalla de inicio (Home)
│  (Pantalla 1)│
└──────┬──────┘
       │
  ┌────┴────┬───────────┬───────────┬───────────┐
  ▼         ▼           ▼           ▼           ▼
FEEDERS  MEDICIONES  ALARMAS  PARÁMETROS  DIAGNÓSTICO
 (P2)      (P3)       (P4)     (P5-🔒)    (P6-🔒)
```

- Barra de navegación fija en la parte inferior de todas las pantallas (5 botones + Home)
- Barra de estado fija en la parte superior: modo (AUTO/MANUAL), fuente activa, alarma activa (icono parpadeante), hora, rol usuario

---

## Barra Superior Global (todas las pantallas)

| Elemento | Variable | Descripción |
|----------|----------|-------------|
| Indicador modo | `DATA_BUFF.MODE_AUTO` | **AUTO** (verde) / **MANUAL** (amarillo) |
| Fuente activa | `DATA_BUFF.IS_ON_GRID`, `IS_ON_GD`, `IS_ON_GD2` | **EN RED** / **EN GD1** / **EN GD2** / **TRANSFERENCIA** |
| Estado SCMTA | `DATA_BUFF.SCMTA_STATE_NAME` | Texto del estado actual |
| Icono alarma | `DATA_BUFF.HMI_ALARM_ACTIVE` | Campana parpadeante si hay alarma. Toque → va a P4 |
| Icono deslastre | `DATA_BUFF.SHED_ACTIVE` | Triángulo amarillo si hay deslastre activo |
| Reloj | `Fecha/Hora sistema` | HH:MM:SS DD/MM/YYYY |
| Usuario | Sesión HMI | Rol actual (Operador / Admin) |

---

---

## Pantalla 1 — SINÓPTICO (Home)

**Propósito:** Vista general tipo unifilar eléctrico simplificado. Ver de un vistazo el estado completo del sistema.

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [BARRA SUPERIOR GLOBAL]                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│          ═══╦═══RED═══╦═════════════╦═══GD1═══╦═══GD2═══       │
│             ║         ║             ║         ║         ║       │
│           ┌─╨─┐     ┌─╨─┐        ┌─╨─┐    ┌─╨─┐    ┌─╨─┐     │
│           │QT1│     │ T │        │   │    │QG1│    │QG2│     │
│           └─╥─┘     │   │        │GD1│    └─╥─┘    └─╥─┘     │
│             ║       └───┘        │   │      ║        ║       │
│             ║                    └───┘      ║        ║       │
│     ════════╩═══════BARRA PRINCIPAL═════════╩════════╝       │
│             │                                                   │
│     ┌───┬───┬───┬───┬───┬───┬───┐                              │
│     │F1 │F2 │...│F10│...│F18│F19│  ← bloques feeders           │
│     └───┴───┴───┴───┴───┴───┴───┘                              │
│                                                                 │
│  ┌────────────────────┐  ┌────────────────────┐                 │
│  │ CARGA RED: 62.3%   │  │ CARGA GD:  --.-% │                 │
│  │ ████████░░░░░░░░░  │  │ ░░░░░░░░░░░░░░░░  │                 │
│  └────────────────────┘  └────────────────────┘                 │
│                                                                 │
│  Transferencias: 12   Fallas: 2   Uptime: 48d 12h              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [HOME] [FEEDERS] [MEDICIONES] [ALARMAS] [PARAMS🔒] [DIAG🔒]  │
└─────────────────────────────────────────────────────────────────┘
```

### Elementos detallados

#### Interruptores fuente (QT1, QG1, QG2)

Cada interruptor se representa con un símbolo que cambia de color:

| Estado | Color símbolo | Indicación |
|--------|---------------|------------|
| Abierto | Verde | Contacto abierto |
| Cerrado | Rojo | Contacto cerrado |
| Tripped | Ámbar parpadeante | Disparado por protección |
| En transición | Gris parpadeante | Maniobra en curso |

| Variable | Fuente |
|----------|--------|
| Estado QT1 | `DATA_BUFF.QT1_STATE` (0=abierto, 1=cerrado, 3=transición) |
| Falla QT1 | `DATA_BUFF.QT1_TRIPPED` |
| Resorte QT1 | `DATA_BUFF.QT1_READY` |
| (ídem para QG1 y QG2) | |

**Toque sobre interruptor (Admin):** Abre pop-up de comando → ver sección Pop-ups.

#### Grupo Electrógeno (GD1 / GD2)

| Indicador | Variable | Representación |
|-----------|----------|----------------|
| 🟢 Listo | `DATA_BUFF.GD_READY` / `GD2_READY` | LED verde |
| 🔵 En marcha | `DATA_BUFF.GD_RUNNING` / `GD2_RUNNING` | LED azul |
| 🔴 Alarma | `DATA_BUFF.GD_ALARM` / `GD2_ALARM` | LED rojo parpadeante |
| Disponible | `DATA_BUFF.GD1_AVAILABLE` / `GD2_AVAILABLE` | Texto "DISP" / "NO DISP" |

#### Barra de feeders (resumen visual)

Fila de 19 rectángulos pequeños en la parte inferior del unifilar:

| Color del rectángulo | Significado |
|---------------------|-------------|
| Verde | Feeder abierto |
| Rojo | Feeder cerrado |
| Ámbar parpadeante | Feeder en falla/tripped |
| Azul | Feeder esencial (borde azul) |
| Gris | Feeder desacoplado por deslastre |

**Toque sobre feeder:** Navega a Pantalla 2 (FEEDERS) con scroll al feeder tocado.

#### Barras de carga

| Barra | Variable | Rango colores |
|-------|----------|---------------|
| Carga RED (trafo) | `DATA_BUFF.TR_LoadPct` | 0-70% verde, 70-85% amarillo, >85% rojo |
| Carga GD | `DATA_BUFF.GD_LoadPct` | 0-70% verde, 70-90% amarillo, >90% rojo |

#### Contadores inferiores

| Dato | Variable |
|------|----------|
| Transferencias | `DATA_BUFF.TRANSFER_COUNT` |
| Fallas | `DATA_BUFF.FAULT_COUNT` |
| Uptime | `DATA_BUFF.SYSTEM_UPTIME` |

---

---

## Pantalla 2 — FEEDERS

**Propósito:** Estado detallado y comando de los 19 feeders con Modbus. Tabla scrolleable.

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [BARRA SUPERIOR GLOBAL]                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Modo deslastre: GD_RECONNECT (3)    Feeders shed: 4           │
│                                                                 │
│  ┌────┬──────┬────────┬───────┬───────┬──────┬──────┬─────────┐│
│  │ #  │ ID   │ Estado │ Falla │ Alarm │ Esen │ Shed │ Comando ││
│  ├────┼──────┼────────┼───────┼───────┼──────┼──────┼─────────┤│
│  │  1 │ Q3.1 │ 🔴CERR │       │       │  ★   │      │ [A][C] ││
│  │  2 │ Q3.2 │ 🟢ABRT │       │       │      │  ⬇   │ [A][C] ││
│  │  3 │ Q3.3 │ 🔴CERR │       │       │  ★   │      │ [A][C] ││
│  │  4 │ Q3.4 │ ⚠️TRIP │  ⚠️   │       │      │      │ [A][C] ││
│  │ .. │ ...  │  ...   │  ...  │  ...  │ ...  │ ...  │  ...   ││
│  │ 19 │ Q23  │ 🔴CERR │       │       │      │      │ [A][C] ││
│  └────┴──────┴────────┴───────┴───────┴──────┴──────┴─────────┘│
│                                                                 │
│  ┌─ Detalle Feeder Seleccionado ──────────────────────────────┐ │
│  │ Feeder #4 — Q3.4 (Tipo b — sin pulsadores)                │ │
│  │ Estado: TRIPPED    Corriente: L1=12.3A L2=11.8A L3=12.1A  │ │
│  │ Esencial: NO       Habilitado shed: SI    Orden shed: 4   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [HOME] [FEEDERS] [MEDICIONES] [ALARMAS] [PARAMS🔒] [DIAG🔒]  │
└─────────────────────────────────────────────────────────────────┘
```

### Columnas de la tabla

| Columna | Variable | Descripción |
|---------|----------|-------------|
| # | Índice 1-19 | Número de feeder |
| ID | Fijo (Q3.1, Q3.2...) | Designación en tablero |
| Estado | `DATA_BUFF.FEEDER_STATE[i]` | 🔴 CERRADO / 🟢 ABIERTO / ⚠️ TRIPPED / ❓ DESC |
| Falla | `DATA_BUFF.FEEDER_TRIPPED[i]` | Icono ⚠️ si tripped |
| Alarm | `DATA_BUFF.FEEDER_ALARM[i]` | Icono ⚠️ si alarma |
| Esen | `DB_PARAMS.FEEDER_ESSENTIAL[i]` | ★ si esencial (azul), vacío si no |
| Shed | Lógica: feeder abierto por shed | ⬇ si fue deslastado |
| Comando | Botones **[A]brir** / **[C]errar** | Solo visible con rol Admin + Remoto |

### Botones de comando (Admin)

- **[A]brir**: Escribe `DATA_BUFF.REQ_MAN_FEEDER_OPEN[i] := TRUE`
- **[C]errar**: Escribe `DATA_BUFF.REQ_MAN_FEEDER_CLOSE[i] := TRUE`
- Botones deshabilitados (grises) si:
  - Rol no es Admin
  - Selector sistema en LOCAL (no remoto en ese feeder)
  - Feeder ya está en el estado solicitado

### Panel detalle (al seleccionar fila)

| Dato | Variable |
|------|----------|
| Corriente L1 | `DATA_BUFF.FEEDER_I_L1[i]` |
| Corriente L2 | `DATA_BUFF.FEEDER_I_L2[i]` |
| Corriente L3 | `DATA_BUFF.FEEDER_I_L3[i]` |
| Es esencial | `DB_PARAMS.FEEDER_ESSENTIAL[i]` |
| Shed habilitado | `DB_PARAMS.SHED_ENABLE[i]` |
| Orden de deslastre | `DB_PARAMS.SHED_ORDER[i]` |
| Tipo (a/b) | Fijo por configuración |

---

---

## Pantalla 3 — MEDICIONES

**Propósito:** Visualización de todas las magnitudes eléctricas de RED, Grupo Diésel y Transformador.

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [BARRA SUPERIOR GLOBAL]                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌── RED (Medidor PM5350) ───────────────────────────────────┐  │
│  │ V L1-L2: 381.2 V   V L2-L3: 380.5 V   V L3-L1: 379.8 V │  │
│  │ I L1:  452.1 A     I L2:  448.3 A     I L3:  450.7 A    │  │
│  │ Frecuencia: 50.01 Hz                                      │  │
│  │ P total: 285.3 kW    Q total: 98.2 kVAr   S: 302.1 kVA  │  │
│  │ FP: 0.94             Energía: 12548.2 kWh                │  │
│  │ Medición OK: ✅       Carga trafo: 62.3%                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌── GRUPO ELECTRÓGENO ──────────────────────────────────────┐  │
│  │ V L1-L2: ---.-- V   V L2-L3: ---.-- V   V L3-L1: ---.-- │  │
│  │ I L1:  ---.-- A     I L2:  ---.-- A     I L3:  ---.-- A  │  │
│  │ Frecuencia: ---.-- Hz                                     │  │
│  │ P total: ---.-- kW         Carga GD: --.--%              │  │
│  │ Medición OK: ❌       GD activo: NINGUNO                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌── TRANSFORMADOR ──────────────────────────────────────────┐  │
│  │ I L1: 452.1 A   I L2: 448.3 A   I L3: 450.7 A           │  │
│  │ P total: 285.3 kW   Carga: 62.3%   Medición OK: ✅       │  │
│  │ Nominal: 1000 kVA   I nominal: 1520 A                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [HOME] [FEEDERS] [MEDICIONES] [ALARMAS] [PARAMS🔒] [DIAG🔒]  │
└─────────────────────────────────────────────────────────────────┘
```

### Variables por sección

#### RED

| Campo | Variable DATA_BUFF |
|-------|--------------------|
| V L1-L2, L2-L3, L3-L1 | `GRID_V_L1L2`, `GRID_V_L2L3`, `GRID_V_L3L1` |
| I L1, L2, L3 | `GRID_I_L1`, `GRID_I_L2`, `GRID_I_L3` |
| Frecuencia | `GRID_FREQ` |
| P total | `GRID_P_TOTAL` |
| Q total | `GRID_Q_TOTAL` |
| S total | `GRID_S_TOTAL` |
| Factor de potencia | `GRID_PF` |
| Energía acumulada | `GRID_ENERGY` |
| Medición OK | `GRID_MEASUREMENT_OK` |

#### Grupo Electrógeno

| Campo | Variable DATA_BUFF |
|-------|--------------------|
| V L1-L2, L2-L3, L3-L1 | `GD_V_L1L2`, `GD_V_L2L3`, `GD_V_L3L1` |
| I L1, L2, L3 | `GD_I_L1`, `GD_I_L2`, `GD_I_L3` |
| Frecuencia | `GD_FREQ` |
| P total | `GD_P_TOTAL` |
| Carga GD | `GD_LoadPct` |
| Medición OK | `GD_MEASUREMENT_OK` |
| GD activo | `ACTIVE_GD` (0=ninguno, 1=GD1, 2=GD2) |

#### Transformador

| Campo | Variable DATA_BUFF |
|-------|--------------------|
| I L1, L2, L3 | `TR_I_L1`, `TR_I_L2`, `TR_I_L3` |
| P total | `TR_P_TOTAL` |
| Carga | `TR_LoadPct` |
| Medición OK | `TR_MEASUREMENT_OK` |
| Nominal P | `DB_PARAMS.TR_POWER_NOMINAL` |
| Nominal I | `DB_PARAMS.TR_CURRENT_NOMINAL` |

---

---

## Pantalla 4 — ALARMAS

**Propósito:** Visualización de alarmas activas y registro histórico. Reconocimiento de alarmas.

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [BARRA SUPERIOR GLOBAL]                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌── ALARMA ACTIVA ──────────────────────────────────────────┐  │
│  │  🔴 TIMEOUT: No se pudo abrir QT1 (Código: 101)          │  │
│  │  Desde: 23/02/2026 14:32:15                               │  │
│  │                                           [ACK ALARMA 🔒] │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌── HISTORIAL ──────────────────────────────────────────────┐  │
│  │ Fecha/Hora          │ Código │ Descripción         │ ACK  │  │
│  │ 23/02 14:32:15      │ 101    │ TIMEOUT abrir QT1   │  ⬜  │  │
│  │ 23/02 10:15:02      │ 106    │ Falla Grupo Diésel  │  ✅  │  │
│  │ 22/02 22:45:30      │ 107    │ Violación enclav.   │  ✅  │  │
│  │ 22/02 18:12:44      │ 102    │ GD no alcanzó READY │  ✅  │  │
│  │ ...                 │        │                     │      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌── INDICADORES ────────────────────────────────────────────┐  │
│  │ Falla activa: SI       Código: 101                        │  │
│  │ Interlock violado: NO                                     │  │
│  │ Alarma GD1: NO         Alarma GD2: NO                    │  │
│  │ Baliza: ACTIVA          ACK pendiente: SI                 │  │
│  │ Total fallas acumuladas: 2                                │  │
│  │ Última falla: 23/02/2026 14:32:15                         │  │
│  │ Última transferencia: 23/02/2026 14:30:03                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [HOME] [FEEDERS] [MEDICIONES] [ALARMAS] [PARAMS🔒] [DIAG🔒]  │
└─────────────────────────────────────────────────────────────────┘
```

### Alarma activa

| Elemento | Variable |
|----------|----------|
| Texto alarma | `DATA_BUFF.HMI_ALARM_TEXT` |
| Alarma activa | `DATA_BUFF.HMI_ALARM_ACTIVE` |
| Código falla | `DATA_BUFF.FAULT_CODE` |

### Tabla de códigos de alarma

| Código | Descripción | Severidad |
|--------|-------------|-----------|
| 101 | TIMEOUT: No se pudo abrir QT1 | FALLA |
| 102 | TIMEOUT: GD no alcanzó estado READY | FALLA |
| 103 | TIMEOUT: No se pudo cerrar QG1 | FALLA |
| 104 | TIMEOUT: No se pudo abrir QG1 | FALLA |
| 105 | TIMEOUT: No se pudo cerrar QT1 | FALLA |
| 106 | ALARMA: Falla en Grupo Diésel | FALLA |
| 107 | ALARMA: Violación enclavamiento fuente única | CRITICA |
| 108 | FALLA: Estado máquina desconocido | CRITICA |
| — | Múltiples fuentes cerradas simultáneamente | CRITICA |
| — | Falla en Grupo Diésel 1 | ALARMA |
| — | Falla en Grupo Diésel 2 | ALARMA |

### Botón ACK

- Solo visible/habilitado para Admin
- Escribe `DATA_BUFF.ACK_ALARM := TRUE` (pulso)
- La baliza se apaga solo si la condición de alarma desaparece (ACK no apaga baliza, silencia la alarma en HMI)

### Historial

- Usar **Alarm Logging** de TIA Portal (ProDiag o HMI Alarms)
- Buffer circular de al menos 200 eventos
- Columnas: Timestamp, código, texto, estado ACK

### Indicadores complementarios

| Indicador | Variable |
|-----------|----------|
| Falla activa | `DATA_BUFF.IS_FAULT` |
| Código | `DATA_BUFF.FAULT_CODE` |
| Interlock violado | `DATA_BUFF.ALM_INTERLOCK_VIOLATION` |
| Alarma GD1 | `DATA_BUFF.GD_ALARM` |
| Alarma GD2 | `DATA_BUFF.GD2_ALARM` |
| Baliza | `DATA_BUFF.DO_ALARM_BEACON` (reflejo) |
| Total fallas | `DATA_BUFF.FAULT_COUNT` |
| Última falla | `DATA_BUFF.LAST_FAULT_TIMESTAMP` |
| Última transferencia | `DATA_BUFF.LAST_TRANSFER_TIMESTAMP` |

---

---

## Pantalla 5 — PARÁMETROS (Solo Admin 🔒)

**Propósito:** Configuración de todos los parámetros del sistema. Protegida con login Admin.

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [BARRA SUPERIOR GLOBAL]                       🔒 ADMIN REQUERIDO│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Tab: UMBRALES]  [Tab: TIEMPOS]  [Tab: FEEDERS]  [Tab: SIST.] │
│                                                                 │
│  ═══════════ Tab UMBRALES ═══════════════════════════════════   │
│  ┌─ Deslastre GD ──────────────┐  ┌─ Deslastre RED ──────────┐ │
│  │ GD_SHED_ON:    [90.0] %     │  │ GRID_SHED_ON:  [85.0] %  │ │
│  │ GD_SHED_OFF:   [70.0] %     │  │ GRID_SHED_OFF: [70.0] %  │ │
│  └─────────────────────────────┘  └───────────────────────────┘ │
│                                                                 │
│  ═══════════ Tab TIEMPOS ════════════════════════════════════   │
│  T_SHED_STEP:        [5000] ms    T_RECONNECT_STEP:  [5000] ms │
│  T_LOAD_FILTER:      [2000] ms    T_LOAD_CHECK_DELAY:[3000] ms │
│  T_GRID_FAIL_FILTER: [2000] ms    T_GRID_STABLE:   [120000] ms │
│  T_OPEN_QT1:         [2000] ms    T_CLOSE_QT1:       [2000] ms │
│  T_OPEN_QG1:         [2000] ms    T_CLOSE_QG1:       [2000] ms │
│  T_OPEN_QG2:         [2000] ms    T_CLOSE_QG2:       [2000] ms │
│  T_GD_READY_TIMEOUT: [30000] ms   T_GD_COOLDOWN:   [60000] ms  │
│  T_START_GD_DELAY:   [3000] ms    T_GD_STABILIZATION:[5000] ms │
│                                                                 │
│  ═══════════ Tab FEEDERS ════════════════════════════════════   │
│  (ver sección detallada abajo)                                  │
│                                                                 │
│  ═══════════ Tab SISTEMA ════════════════════════════════════   │
│  V_NOM: [380.0] V   FREQ_NOM: [50.0] Hz                       │
│  V_MIN_PCT: [85.0]%  V_MAX_PCT: [110.0]%                      │
│  FREQ_MIN: [49.0] Hz  FREQ_MAX: [51.0] Hz                     │
│  GD_POWER_NOMINAL: [1000.0] kVA                                │
│  TR_POWER_NOMINAL: [1000.0] kVA                                │
│  ☑ ENABLE_SCMTA   ☑ ENABLE_SHED   ☑ ENABLE_AUTO_RETURN        │
│                                                                 │
│                                          [GUARDAR] [RESTAURAR]  │
├─────────────────────────────────────────────────────────────────┤
│  [HOME] [FEEDERS] [MEDICIONES] [ALARMAS] [PARAMS🔒] [DIAG🔒]  │
└─────────────────────────────────────────────────────────────────┘
```

### Tab FEEDERS — Configuración de deslastre por feeder

Esta es la pantalla clave para definir qué feeders son **esenciales** y el **orden de deslastre/reenganche**.

```
┌────┬──────┬────────────┬──────────────┬───────────────┬──────────────────┐
│ #  │ ID   │ Esencial   │ Shed Habilt. │ Orden Deslast │ Orden Reenganche │
├────┼──────┼────────────┼──────────────┼───────────────┼──────────────────┤
│  1 │ Q3.1 │ [☑] SI     │ [☐] NO       │ [-]           │ [-]              │
│  2 │ Q3.2 │ [☐] NO     │ [☑] SI       │ [3]           │ [17]             │
│  3 │ Q3.3 │ [☑] SI     │ [☐] NO       │ [-]           │ [-]              │
│  4 │ Q3.4 │ [☐] NO     │ [☑] SI       │ [1]           │ [19]             │
│  5 │ Q3.5 │ [☐] NO     │ [☑] SI       │ [2]           │ [18]             │
│  6 │ Q3.6 │ [☐] NO     │ [☑] SI       │ [4]           │ [16]             │
│ .. │ ...  │    ...     │     ...      │     ...       │       ...        │
│ 19 │ Q23  │ [☐] NO     │ [☑] SI       │ [15]          │ [5]              │
└────┴──────┴────────────┴──────────────┴───────────────┴──────────────────┘

Nota: Si "Esencial = SI", las columnas Shed Habilt / Orden se deshabilitan
automáticamente (un feeder esencial nunca se deslasta).

Esenciales: 4 de 19          No-esenciales con shed: 15 de 19
```

| Columna | Variable DB_PARAMS | Tipo |
|---------|-------------------|------|
| Esencial | `FEEDER_ESSENTIAL[i]` | Bool (checkbox) |
| Shed habilitado | `SHED_ENABLE[i]` | Bool (checkbox) |
| Orden deslastre | `SHED_ORDER[i]` | Int (1-19, input numérico) |
| Orden reenganche | `RECONNECT_ORDER[i]` | Int (1-19, input numérico) |

> **Regla:** Si `FEEDER_ESSENTIAL[i] = TRUE`, entonces `SHED_ENABLE[i]` se fuerza a FALSE y los campos de orden se muestran como "—" (deshabilitados).

### Botones

| Botón | Acción |
|-------|--------|
| **GUARDAR** | Escribe los valores editados en DB_PARAMS (RETAIN) |
| **RESTAURAR** | Recarga los valores actuales de DB_PARAMS descartando cambios |

---

---

## Pantalla 6 — DIAGNÓSTICO (Solo Admin 🔒)

**Propósito:** Comisionado en planta, debug del sistema, vista de estados internos, status Modbus, y herramienta de pruebas.

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [BARRA SUPERIOR GLOBAL]                       🔒 ADMIN REQUERIDO│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Tab: ESTADOS]  [Tab: MODBUS]  [Tab: FORZADOS]  [Tab: I/O]    │
│                                                                 │
│  ═══════════ Tab ESTADOS ════════════════════════════════════   │
│  (ver detalle abajo)                                            │
│                                                                 │
│  ═══════════ Tab MODBUS ═════════════════════════════════════   │
│  (ver detalle abajo)                                            │
│                                                                 │
│  ═══════════ Tab FORZADOS ═══════════════════════════════════   │
│  (ver detalle abajo)                                            │
│                                                                 │
│  ═══════════ Tab I/O ════════════════════════════════════════   │
│  (ver detalle abajo)                                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [HOME] [FEEDERS] [MEDICIONES] [ALARMAS] [PARAMS🔒] [DIAG🔒]  │
└─────────────────────────────────────────────────────────────────┘
```

### Tab ESTADOS — Máquina de estados interna

| Dato | Variable | Descripción |
|------|----------|-------------|
| SCMTA State | `DATA_BUFF.SCMTA_STATE` | Número de estado (0-20) |
| State Name | `DATA_BUFF.SCMTA_STATE_NAME` | Nombre texto |
| IS_ON_GRID | `DATA_BUFF.IS_ON_GRID` | Bool |
| IS_ON_GD | `DATA_BUFF.IS_ON_GD` | Bool |
| IS_ON_GD1 | `DATA_BUFF.IS_ON_GD1` | Bool |
| IS_ON_GD2 | `DATA_BUFF.IS_ON_GD2` | Bool |
| ACTIVE_GD | `DATA_BUFF.ACTIVE_GD` | 0/1/2 |
| IS_IN_TRANSFER | `DATA_BUFF.IS_IN_TRANSFER` | Bool |
| IS_FAULT | `DATA_BUFF.IS_FAULT` | Bool |
| TRANSFER_TO_GD | `DATA_BUFF.TRANSFER_TO_GD` | Bool |
| GRID_OK | `DATA_BUFF.GRID_OK` | Bool |
| GRID_FAIL | `DATA_BUFF.GRID_FAIL` | Bool |
| FAULT_CODE | `DATA_BUFF.FAULT_CODE` | Int |
| ELAPSED_TIME | `DATA_BUFF.ELAPSED_TIME` | Tiempo en estado actual |
| DIAG_LAST_TRANSFER | `DATA_BUFF.DIAG_LAST_TRANSFER_TIME` | Duración última transferencia |
| SHED_MODE | `DATA_BUFF.SHED_MODE` | 0=IDLE, 1=GRID_SHED, 2=GD_INIT, 3=GD_RECON, 4=GD_REACT, 5=GRID_RECON |
| SHED_STEP | `DATA_BUFF.SHED_STEP` | Paso actual deslastre |
| RECONNECT_STEP | `DATA_BUFF.RECONNECT_STEP` | Paso actual reenganche |
| FEEDERS_SHED | `DATA_BUFF.FEEDERS_SHED` | Feeders actualmente deslastados |
| FEEDERS_ESSENTIAL | `DATA_BUFF.FEEDERS_ESSENTIAL_COUNT` | Cantidad esenciales |
| DIAG_LOAD_OVER | `DATA_BUFF.DIAG_LOAD_OVER_LIMIT` | Carga sobre límite |
| DIAG_GD_LOAD_OK | `DATA_BUFF.DIAG_GD_LOAD_OK` | Carga GD en rango |
| DIAG_GRID_LOAD_OK | `DATA_BUFF.DIAG_GRID_LOAD_OK` | Carga RED en rango |
| GD1_AVAILABLE | `DATA_BUFF.GD1_AVAILABLE` | GD1 disponible |
| GD2_AVAILABLE | `DATA_BUFF.GD2_AVAILABLE` | GD2 disponible |

Representación visual recomendada: diagrama de la máquina de estados con el estado actual resaltado en color, o al menos una lista con el estado actual marcado y flechas indicando transiciones posibles.

### Tab MODBUS — Status comunicación

| Dato | Variable | Descripción |
|------|----------|-------------|
| COMM_OK | `DATA_BUFF.COMM_OK` | Comunicación general OK |
| COMM_ERRORS | `DATA_BUFF.COMM_ERRORS` | Contador errores acumulados |
| ACTIVE_DEVICE | `DATA_BUFF.ACTIVE_DEVICE` | Dispositivo siendo polleado ahora |

Incluir tabla de 22 dispositivos con status individual:

| Dispositivo | Slave ID | Último poll | Status | Errores |
|-------------|----------|-------------|--------|---------|
| QT1 | `DB_PARAMS.SLAVE_ID_QT1` | (timestamp) | OK / TIMEOUT / ERROR | count |
| QG1 | `DB_PARAMS.SLAVE_ID_QG1` | (timestamp) | OK / TIMEOUT / ERROR | count |
| QG2 | `DB_PARAMS.SLAVE_ID_QG2` | (timestamp) | OK / TIMEOUT / ERROR | count |
| Feeder 1-19 | `DB_PARAMS.SLAVE_ID_FEEDER[i]` | (timestamp) | OK / TIMEOUT / ERROR | count |
| PM5350 Grid | `DB_PARAMS.SLAVE_ID_PM5350_GRID` | (timestamp) | OK / TIMEOUT / ERROR | count |
| PM5350 GD | `DB_PARAMS.SLAVE_ID_PM5350_GD` | (timestamp) | OK / TIMEOUT / ERROR | count |
| PM5350 TR | `DB_PARAMS.SLAVE_ID_PM5350_TR` | (timestamp) | OK / TIMEOUT / ERROR | count |

> **Nota:** Para tener el status individual por dispositivo, hay que agregar un array en DATA_BUFF (ej. `MODBUS_DEV_STATUS[1..22]` y `MODBUS_DEV_ERRORS[1..22]`). Esto es una propuesta de extensión del DB.

### Tab FORZADOS — Comandos manuales de debug

**⚠️ PELIGRO: Solo para comisionado en planta. Usar con precaución.**

| Grupo | Comando | Variable destino | Acción |
|-------|---------|-----------------|--------|
| **Interruptores** | ABRIR QT1 | `DATA_BUFF.REQ_MAN_QT1_OPEN` | Pulso |
| | CERRAR QT1 | `DATA_BUFF.REQ_MAN_QT1_CLOSE` | Pulso |
| | ABRIR QG1 | `DATA_BUFF.REQ_MAN_QG1_OPEN` | Pulso |
| | CERRAR QG1 | `DATA_BUFF.REQ_MAN_QG1_CLOSE` | Pulso |
| | ABRIR QG2 | `DATA_BUFF.REQ_MAN_QG2_OPEN` | Pulso |
| | CERRAR QG2 | `DATA_BUFF.REQ_MAN_QG2_CLOSE` | Pulso |
| **Reset** | RESET FALLA | Pulso `RESET_FAULT` vía HMI | Resetea estado FAULT de SCMTA |
| **Sistema** | ENABLE_SCMTA | `DB_PARAMS.ENABLE_SCMTA` | Toggle ON/OFF |
| | ENABLE_SHED | `DB_PARAMS.ENABLE_SHED` | Toggle ON/OFF |
| | ENABLE_AUTO_RETURN | `DB_PARAMS.ENABLE_AUTO_RETURN` | Toggle ON/OFF |

Cada botón de comando debe tener **confirmación doble** (pop-up "¿Está seguro?") para evitar maniobras accidentales.

### Tab I/O — Vista cruda de entradas/salidas

Vista de todas las DI y DO físicas con su estado en tiempo real:

**Entradas Digitales:**

| Dirección | Señal | Estado |
|-----------|-------|--------|
| %I0.0 | DI_SYS_AUTO | 🟢 ON / ⚪ OFF |
| %I0.1 | DI_QT1_REMOTE_SEL | 🟢 / ⚪ |
| %I0.2 | DI_QT1_PB_OPEN | 🟢 / ⚪ |
| %I0.3 | DI_QT1_PB_CLOSE | 🟢 / ⚪ |
| %I0.4 | DI_QG1_REMOTE_SEL | 🟢 / ⚪ |
| %I0.5 | DI_QG1_PB_OPEN | 🟢 / ⚪ |
| %I0.6 | DI_QG1_PB_CLOSE | 🟢 / ⚪ |
| %I1.0 | DI_QG2_REMOTE_SEL | 🟢 / ⚪ |
| %I1.1 | DI_QG2_PB_OPEN | 🟢 / ⚪ |
| %I1.2 | DI_QG2_PB_CLOSE | 🟢 / ⚪ |
| %I1.3 | DI_GD_READY | 🟢 / ⚪ |
| %I1.4 | DI_GD_RUNNING | 🟢 / ⚪ |
| %I1.5 | DI_GD_ALARM | 🟢 / ⚪ |
| %I1.6 | DI_GD2_READY | 🟢 / ⚪ |
| %I1.7 | DI_GD2_RUNNING | 🟢 / ⚪ |
| %I2.0 | RESET_FAULT | 🟢 / ⚪ |
| %I2.1 | DI_GD2_ALARM / ACK_ALARM | 🟢 / ⚪ |

**Salidas Digitales** (primeras 16):

| Dirección | Señal | Estado |
|-----------|-------|--------|
| %Q1.0 | DO_PILOT_ON_GRID | 🟢 / ⚪ |
| %Q1.1 | DO_PILOT_ON_GD | 🟢 / ⚪ |
| %Q1.2 | DO_PILOT_FAULT | 🟢 / ⚪ |
| ... | ... | ... |
| %Q3.0 | DO_ALARM_BEACON | 🟢 / ⚪ |

---

---

## Pop-ups de Comando (usados desde P1 y P2)

### Pop-up Interruptor Fuente (QT1/QG1/QG2)

Aparece al tocar un interruptor en el sinóptico. Solo para Admin.

```
┌── Comando QT1 ──────────────────────┐
│                                      │
│  Estado actual: CERRADO              │
│  Tripped: NO     Ready: SI          │
│  Remoto: SI                          │
│                                      │
│  ┌──────────┐    ┌──────────┐       │
│  │  ABRIR   │    │  CERRAR  │       │
│  │  (verde) │    │  (rojo)  │       │
│  └──────────┘    └──────────┘       │
│                                      │
│               [CANCELAR]             │
└──────────────────────────────────────┘
```

- Botón ABRIR deshabilitado si ya está abierto
- Botón CERRAR deshabilitado si ya está cerrado o TRIPPED (requiere reset primero)
- Ambos deshabilitados si REMOTO = NO
- Confirmación: "¿Confirma ABRIR QT1?" → [SI] / [NO]

---

## Variables HMI adicionales sugeridas para DATA_BUFF

Para soportar completamente las pantallas diseñadas, se recomienda agregar estas variables al DB global:

```
// --- Extensiones propuestas para DATA_BUFF ---

// Comandos HMI → PLC (si no existen ya)
HMI_CMD_OPEN_QT1 : Bool;
HMI_CMD_CLOSE_QT1 : Bool;
HMI_CMD_OPEN_QG1 : Bool;
HMI_CMD_CLOSE_QG1 : Bool;
HMI_CMD_OPEN_QG2 : Bool;
HMI_CMD_CLOSE_QG2 : Bool;
HMI_CMD_FEEDER_OPEN : Array[1..19] of Bool;
HMI_CMD_FEEDER_CLOSE : Array[1..19] of Bool;
HMI_CMD_RESET_FAULT : Bool;
HMI_CMD_ACK_ALARM : Bool;

// Diagnóstico Modbus por dispositivo (22 dispositivos)
MODBUS_DEV_STATUS : Array[1..22] of Int;   // 0=OK, 1=TIMEOUT, 2=ERROR
MODBUS_DEV_ERRORS : Array[1..22] of Int;   // Contador errores por dispositivo

// Nombre descriptivo feeders (para display en HMI)
FEEDER_NAME : Array[1..19] of String[20]; // "Q3.1", "Q3.2", etc.
```

---

## Resumen de Tags HMI estimados

| Categoría | Tags aproximados |
|-----------|-----------------|
| Barra superior | ~10 |
| Sinóptico (P1) | ~40 |
| Feeders (P2) | ~120 (19 feeders × 6 campos + comandos) |
| Mediciones (P3) | ~35 |
| Alarmas (P4) | ~15 + alarma logging |
| Parámetros (P5) | ~90 (tiempos + umbrales + arrays feeders) |
| Diagnóstico (P6) | ~80 (estados + Modbus + I/O) |
| **Total estimado** | **~390 tags** |

> Para un Comfort Panel o KTP con licencia adecuada, 512 tags es suficiente.

---

## Notas de Implementación en TIA Portal

1. **User Administration:** Crear grupo "Admin" con nivel de acceso 1, grupo "Operador" con nivel 0. Proteger botones de comando y pantallas P5/P6 con nivel 1.
2. **Alarm Logging:** Usar HMI Alarms (clase "Errors" y "Warnings"). Configurar los triggers basados en `DATA_BUFF.FAULT_CODE` y las señales de alarma individuales.
3. **Trend Recording:** Considerar agregar trend de `TR_LoadPct` y `GD_LoadPct` en la pantalla de mediciones (gráfico temporal de las últimas 24h).
4. **Refresh rate:** Tags de estado → 500ms. Tags de medición → 1s. Tags de parámetros → on-demand.
5. **Comunicación:** Configurar conexión HMI↔PLC vía Ethernet (PUT/GET o HMI Connection integrada en TIA).
6. **Idioma:** Todas las pantallas en español. Considerar soporte bilingüe ES/EN si es requerido.
