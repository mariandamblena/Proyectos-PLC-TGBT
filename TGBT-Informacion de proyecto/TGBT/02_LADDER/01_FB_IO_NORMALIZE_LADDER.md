# FB_IO_NORMALIZE - IMPLEMENTACIÓN LADDER

## DESCRIPCIÓN GENERAL
Este Function Block normaliza las entradas físicas (DI) del sistema TGBT a señales lógicas internas que serán consumidas por FB_SCMTA, FB_SHED y FB_CMD_ARBITER.

---

## RUNGS DETALLADOS (LADDER)

### **NETWORK 1: Normalización Modo AUTO/MANUAL**

```
Título: "Determinación modo operativo del sistema"

Rung 1.1: MODE_AUTO
    |--[ DI_SYS_AUTO ]--|--( MODE_AUTO )--|

Rung 1.2: MODE_MANUAL
    |--|/[DI_SYS_AUTO ]--|--( MODE_MANUAL )--|

Rung 1.3: Diagnóstico validez modo
    |--[ ]--|--( DIAG_MODE_VALID )--|
    (Siempre TRUE por ahora; en futuro agregar redundancia)
```

**Lógica:**
- `MODE_AUTO = DI_SYS_AUTO`
- `MODE_MANUAL = NOT DI_SYS_AUTO`
- Fail-safe: si selector indefinido/roto → FALSE → MANUAL

---

### **NETWORK 2: Normalización Local/Remoto**

```
Título: "Permisos de control remoto por interruptor"

Rung 2.1: QT1 Remote Allowed
    |--[ DI_QT1_REMOTE_SEL ]--|--( QT1_REMOTE_ALLOWED )--|

Rung 2.2: QG1 Remote Allowed
    |--[ DI_QG1_REMOTE_SEL ]--|--( QG1_REMOTE_ALLOWED )--|

Rung 2.3: QG2 Remote Allowed
    |--[ DI_QG2_REMOTE_SEL ]--|--( QG2_REMOTE_ALLOWED )--|
```

**Lógica:**
- Selector en REMOTO (TRUE) → PLC puede comandar interruptor
- Selector en LOCAL (FALSE) → PLC solo monitorea, FB_CMD_ARBITER bloqueará comandos

---

### **NETWORK 3: Debounce Pulsadores (50ms)**

```
Título: "Filtro anti-rebote mecánico en pulsadores"

Rung 3.1: Debounce QT1_PB_OPEN
    |--[ DI_QT1_PB_OPEN ]--|--[TON: tonDebounce_QT1_Open, PT:=T#50ms]--|
                              |
                              |--[ Q ]--|--( QT1_PB_Open_DB )--|

Rung 3.2: Debounce QT1_PB_CLOSE
    |--[ DI_QT1_PB_CLOSE ]--|--[TON: tonDebounce_QT1_Close, PT:=T#50ms]--|
                               |
                               |--[ Q ]--|--( QT1_PB_Close_DB )--|

Rung 3.3: Debounce QG1_PB_OPEN
    |--[ DI_QG1_PB_OPEN ]--|--[TON: tonDebounce_QG1_Open, PT:=T#50ms]--|
                              |
                              |--[ Q ]--|--( QG1_PB_Open_DB )--|

Rung 3.4: Debounce QG1_PB_CLOSE
    |--[ DI_QG1_PB_CLOSE ]--|--[TON: tonDebounce_QG1_Close, PT:=T#50ms]--|
                               |
                               |--[ Q ]--|--( QG1_PB_Close_DB )--|

Rung 3.5: Debounce QG2_PB_OPEN
    |--[ DI_QG2_PB_OPEN ]--|--[TON: tonDebounce_QG2_Open, PT:=T#50ms]--|
                              |
                              |--[ Q ]--|--( QG2_PB_Open_DB )--|

Rung 3.6: Debounce QG2_PB_CLOSE
    |--[ DI_QG2_PB_CLOSE ]--|--[TON: tonDebounce_QG2_Close, PT:=T#50ms]--|
                               |
                               |--[ Q ]--|--( QG2_PB_Close_DB )--|
```

**Lógica:**
- TON (Timer On-Delay) con PT=50ms filtra rebotes mecánicos de contactos
- Señal debe estar estable 50ms antes de reconocerla como válida

---

### **NETWORK 4: Detección Flanco Positivo → Requests Manuales**

```
Título: "Generación de pulsos (1 scan) al presionar pulsadores"

Rung 4.1: Request Manual QT1 OPEN
    |--[ QT1_PB_Open_DB ]--|--|/[memQT1_PB_Open]--|--( REQ_MAN_QT1_OPEN )--|
    |--[ QT1_PB_Open_DB ]--|--( memQT1_PB_Open )--|

Rung 4.2: Request Manual QT1 CLOSE
    |--[ QT1_PB_Close_DB ]--|--|/[memQT1_PB_Close]--|--( REQ_MAN_QT1_CLOSE )--|
    |--[ QT1_PB_Close_DB ]--|--( memQT1_PB_Close )--|

Rung 4.3: Request Manual QG1 OPEN
    |--[ QG1_PB_Open_DB ]--|--|/[memQG1_PB_Open]--|--( REQ_MAN_QG1_OPEN )--|
    |--[ QG1_PB_Open_DB ]--|--( memQG1_PB_Open )--|

Rung 4.4: Request Manual QG1 CLOSE
    |--[ QG1_PB_Close_DB ]--|--|/[memQG1_PB_Close]--|--( REQ_MAN_QG1_CLOSE )--|
    |--[ QG1_PB_Close_DB ]--|--( memQG1_PB_Close )--|

Rung 4.5: Request Manual QG2 OPEN
    |--[ QG2_PB_Open_DB ]--|--|/[memQG2_PB_Open]--|--( REQ_MAN_QG2_OPEN )--|
    |--[ QG2_PB_Open_DB ]--|--( memQG2_PB_Open )--|

Rung 4.6: Request Manual QG2 CLOSE
    |--[ QG2_PB_Close_DB ]--|--|/[memQG2_PB_Close]--|--( REQ_MAN_QG2_CLOSE )--|
    |--[ QG2_PB_Close_DB ]--|--( memQG2_PB_Close )--|
```

**Lógica R_TRIG (Rising Edge):**
- `REQ_MAN_* = (señal_actual AND NOT señal_anterior)`
- Genera pulso de 1 scan al detectar transición 0→1
- Memoria se actualiza cada scan con estado actual
- FB_CMD_ARBITER consumirá estos pulsos y resetará a FALSE

---

### **NETWORK 5: Normalización señales GD (Passthrough)**

```
Título: "Señales estado Grupo Diésel"

Rung 5.1: GD Ready
    |--[ DI_GD_READY ]--|--( GD_READY )--|

Rung 5.2: GD Running
    |--[ DI_GD_RUNNING ]--|--( GD_RUNNING )--|

Rung 5.3: GD Alarm
    |--[ DI_GD_ALARM ]--|--( GD_ALARM )--|
```

**Lógica:**
- Passthrough directo de señales DI → señales normalizadas
- FB_SCMTA usará `GD_READY` para estado 6 (WAIT_GD_READY)

---

## TABLA DE TAGS

### **INPUTS (VAR_INPUT)**

| Tag | Tipo | Dirección Física (Ejemplo) | Descripción |
|-----|------|----------------------------|-------------|
| `DI_SYS_AUTO` | BOOL | %I0.0 | Selector Auto/Manual (TRUE=Auto) |
| `DI_QT1_REMOTE_SEL` | BOOL | %I0.1 | Selector Local/Remoto QT1 (TRUE=Remoto) |
| `DI_QT1_PB_OPEN` | BOOL | %I0.2 | Pulsador Open QT1 (NA, 24VDC) |
| `DI_QT1_PB_CLOSE` | BOOL | %I0.3 | Pulsador Close QT1 (NA, 24VDC) |
| `DI_QG1_REMOTE_SEL` | BOOL | %I0.4 | Selector Local/Remoto QG1 |
| `DI_QG1_PB_OPEN` | BOOL | %I0.5 | Pulsador Open QG1 |
| `DI_QG1_PB_CLOSE` | BOOL | %I0.6 | Pulsador Close QG1 |
| `DI_QG2_REMOTE_SEL` | BOOL | %I1.0 | Selector Local/Remoto QG2 |
| `DI_QG2_PB_OPEN` | BOOL | %I1.1 | Pulsador Open QG2 |
| `DI_QG2_PB_CLOSE` | BOOL | %I1.2 | Pulsador Close QG2 |
| `DI_GD_READY` | BOOL | %I1.3 | GD listo para transferir |
| `DI_GD_RUNNING` | BOOL | %I1.4 | GD en marcha |
| `DI_GD_ALARM` | BOOL | %I1.5 | GD en alarma/falla |

### **OUTPUTS (VAR_OUTPUT)**

| Tag | Tipo | Consumido por | Descripción |
|-----|------|---------------|-------------|
| `MODE_AUTO` | BOOL | FB_SCMTA, FB_SHED | TRUE = Modo Automático activo |
| `MODE_MANUAL` | BOOL | FB_CMD_ARBITER | TRUE = Modo Manual (inhibe secuencias) |
| `QT1_REMOTE_ALLOWED` | BOOL | FB_CMD_ARBITER | TRUE = PLC puede comandar QT1 |
| `QG1_REMOTE_ALLOWED` | BOOL | FB_CMD_ARBITER | TRUE = PLC puede comandar QG1 |
| `QG2_REMOTE_ALLOWED` | BOOL | FB_CMD_ARBITER | TRUE = PLC puede comandar QG2 |
| `REQ_MAN_QT1_OPEN` | BOOL | FB_CMD_ARBITER | Pulso solicitud manual abrir QT1 |
| `REQ_MAN_QT1_CLOSE` | BOOL | FB_CMD_ARBITER | Pulso solicitud manual cerrar QT1 |
| `REQ_MAN_QG1_OPEN` | BOOL | FB_CMD_ARBITER | Pulso solicitud manual abrir QG1 |
| `REQ_MAN_QG1_CLOSE` | BOOL | FB_CMD_ARBITER | Pulso solicitud manual cerrar QG1 |
| `REQ_MAN_QG2_OPEN` | BOOL | FB_CMD_ARBITER | Pulso solicitud manual abrir QG2 |
| `REQ_MAN_QG2_CLOSE` | BOOL | FB_CMD_ARBITER | Pulso solicitud manual cerrar QG2 |
| `GD_READY` | BOOL | FB_SCMTA | GD listo (normalizado) |
| `GD_RUNNING` | BOOL | FB_SCMTA | GD en marcha (normalizado) |
| `GD_ALARM` | BOOL | FB_SCMTA | GD en alarma (normalizado) |
| `DIAG_MODE_VALID` | BOOL | HMI | Diagnóstico validez modo |

---

## LLAMADA EN OB1 (EJEMPLO)

```ladder
NETWORK 1: "Normalización Entradas/Salidas"
    CALL "DB_IO"."FB_IO_NORMALIZE"
    (
        // Inputs - Mapeo DI físicas
        DI_SYS_AUTO := %I0.0,
        DI_QT1_REMOTE_SEL := %I0.1,
        DI_QT1_PB_OPEN := %I0.2,
        DI_QT1_PB_CLOSE := %I0.3,
        DI_QG1_REMOTE_SEL := %I0.4,
        DI_QG1_PB_OPEN := %I0.5,
        DI_QG1_PB_CLOSE := %I0.6,
        DI_QG2_REMOTE_SEL := %I1.0,
        DI_QG2_PB_OPEN := %I1.1,
        DI_QG2_PB_CLOSE := %I1.2,
        DI_GD_READY := %I1.3,
        DI_GD_RUNNING := %I1.4,
        DI_GD_ALARM := %I1.5,
        
        // Outputs - Variables globales o DB intermedios
        MODE_AUTO => "DB_GLOBAL_STATUS".MODE_AUTO,
        MODE_MANUAL => "DB_GLOBAL_STATUS".MODE_MANUAL,
        QT1_REMOTE_ALLOWED => "DB_GLOBAL_STATUS".QT1_REMOTE_ALLOWED,
        QG1_REMOTE_ALLOWED => "DB_GLOBAL_STATUS".QG1_REMOTE_ALLOWED,
        QG2_REMOTE_ALLOWED => "DB_GLOBAL_STATUS".QG2_REMOTE_ALLOWED,
        REQ_MAN_QT1_OPEN => "DB_GLOBAL_STATUS".REQ_MAN_QT1_OPEN,
        REQ_MAN_QT1_CLOSE => "DB_GLOBAL_STATUS".REQ_MAN_QT1_CLOSE,
        REQ_MAN_QG1_OPEN => "DB_GLOBAL_STATUS".REQ_MAN_QG1_OPEN,
        REQ_MAN_QG1_CLOSE => "DB_GLOBAL_STATUS".REQ_MAN_QG1_CLOSE,
        REQ_MAN_QG2_OPEN => "DB_GLOBAL_STATUS".REQ_MAN_QG2_OPEN,
        REQ_MAN_QG2_CLOSE => "DB_GLOBAL_STATUS".REQ_MAN_QG2_CLOSE,
        GD_READY => "DB_GLOBAL_STATUS".GD_READY,
        GD_RUNNING => "DB_GLOBAL_STATUS".GD_RUNNING,
        GD_ALARM => "DB_GLOBAL_STATUS".GD_ALARM,
        DIAG_MODE_VALID => "DB_GLOBAL_STATUS".DIAG_MODE_VALID
    );
```

---

## REGLAS DE SEGURIDAD

1. **Fail-safe Modo:** Si `DI_SYS_AUTO` indefinido → DEFAULT a MANUAL
2. **Debounce obligatorio:** Todos los pulsadores filtrados 50ms antes de procesar
3. **Pulsos de 1 scan:** `REQ_MAN_*` son pulsos momentáneos, NO se mantienen activos
4. **Selector Local:** Si `*_REMOTE_ALLOWED = FALSE`, FB_CMD_ARBITER bloqueará comandos Modbus

---

## NOTAS DE IMPLEMENTACIÓN TIA PORTAL

- **Lenguaje:** SCL proporcionado; alternativamente se puede implementar en Ladder puro siguiendo los rungs descritos arriba
- **Optimización:** `S7_Optimized_Access := TRUE` para rendimiento
- **TON:** Usar bloques estándar de TIA Portal (IEC Timer)
- **Direcciones:** Reemplazar `%I0.0, %I0.1, etc.` con direcciones reales del hardware según "TGBT_Config - listado de entradas y salidas.pdf"

---

## TESTING / VALIDACIÓN

| Caso de Test | Input | Salida Esperada |
|--------------|-------|-----------------|
| Selector en AUTO | `DI_SYS_AUTO=1` | `MODE_AUTO=1, MODE_MANUAL=0` |
| Selector en MANUAL | `DI_SYS_AUTO=0` | `MODE_AUTO=0, MODE_MANUAL=1` |
| QT1 en LOCAL | `DI_QT1_REMOTE_SEL=0` | `QT1_REMOTE_ALLOWED=0` |
| QT1 en REMOTO | `DI_QT1_REMOTE_SEL=1` | `QT1_REMOTE_ALLOWED=1` |
| Presionar PB_OPEN (50ms) | `DI_QT1_PB_OPEN: 0→1→1 (>50ms)` | `REQ_MAN_QT1_OPEN=1 por 1 scan` |
| Presionar PB_CLOSE (rebote <50ms) | `DI_QT1_PB_CLOSE: 0→1→0→1 (<50ms)` | `REQ_MAN_QT1_CLOSE=0` (filtrado) |

---

**✅ PARTE 1 COMPLETADA: FB_IO_NORMALIZE**

