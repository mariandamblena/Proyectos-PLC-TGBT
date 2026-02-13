# Arquitectura de Control de Deslastre V2.0

**Versión**: 2.0  
**Fecha**: 2026-02-10  
**Origen**: Reunión de avances del proyecto  
**Autor**: Sistema SCMTA TGBT

---

## 1. Resumen del Cambio

### Antes (V1.0)
- Deslastre **solo operaba con GD** (Grupo Diésel)
- Trigger único: `GD_LoadPct > 90%` Y `IS_ON_GD = TRUE`
- Reenganche solo al volver a RED
- Sin clasificación de cargas

### Ahora (V2.0)
- Deslastre opera **tanto en RED como en GD**
- Feeders clasificados como **ESENCIALES** o **NO-ESENCIALES**
- En GD: no-esenciales **inician desacopladas**, acoplamiento escalonado verificando carga
- En RED: deslastre **reactivo** de no-esenciales si carga cercana al límite del transformador
- Esenciales **nunca** se deslastan en ningún modo

---

## 2. Clasificación de Feeders

### Array `FEEDER_ESSENTIAL[1..18]`
| Valor | Clasificación | Comportamiento |
|-------|--------------|----------------|
| `TRUE` | **Esencial** | Siempre activo. Nunca se desacopla ni se deslasta. Permanece cerrado durante la transferencia RED→GD |
| `FALSE` | **No-esencial** | Se desacopla al pasar a GD. Se puede deslastar en RED si la carga supera el umbral |

### Configuración
- Parametrizable desde HMI (nivel ADMIN)
- Almacenado en `DB_PARAMS` (RETAIN)
- `FEEDER_ESSENTIAL` tiene **prioridad** sobre `SHED_ENABLE`

### Ejemplos de cargas esenciales
- Iluminación de emergencia
- Bombas contra incendio
- Sistemas de seguridad
- Servidores/comunicaciones críticas
- Ventilación salas de tableros

### Ejemplos de cargas no-esenciales
- Aire acondicionado
- Iluminación general
- Ascensores
- Proceso industrial no crítico

---

## 3. Modos de Operación del Deslastre (SHED_MODE)

| Modo | Valor | Descripción | Trigger |
|------|-------|-------------|---------|
| **IDLE** | 0 | Sin actividad | Sistema estable |
| **GRID_SHED** | 1 | Deslastre reactivo en RED | `TR_LoadPct > GRID_SHED_ON` (85%) |
| **GD_INITIAL_SHED** | 2 | Desacople inicial al transferir a GD | Flanco `TRANSFER_TO_GD` |
| **GD_RECONNECT** | 3 | Acoplamiento escalonado en GD | Flanco `IS_ON_GD` |
| **GD_REACTIVE_SHED** | 4 | Deslastre reactivo en GD | `GD_LoadPct > GD_SHED_ON` (90%) |
| **GRID_RECONNECT** | 5 | Reenganche al volver a RED | Flanco `IS_ON_GRID` |

---

## 4. Comportamiento Detallado por Escenario

### 4.1 Operando con RED (NORMAL_ON_GRID)

```
Estado normal: Todos los feeders cerrados (esenciales + no-esenciales)

SI TR_LoadPct > GRID_SHED_ON (85%) por más de T_LOAD_FILTER (2s):
  → SHED_MODE = GRID_SHED (modo 1)
  → Deslastre REACTIVO: abrir no-esenciales según SHED_ORDER[]
  → Las ESENCIALES nunca se tocan
  → Escalonado con T_SHED_STEP (5s) entre cada paso

SI TR_LoadPct < GRID_SHED_OFF (70%):
  → Cancelar deslastre
  → SHED_MODE = GRID_RECONNECT (modo 5)
  → Reenganchar no-esenciales según RECONNECT_ORDER[]
```

### 4.2 Transferencia RED→GD

```
SCMTA entra en OPEN_QT1 (estado 3):
  → TRANSFER_TO_GD = TRUE
  → SHED detecta flanco ascendente
  → SHED_MODE = GD_INITIAL_SHED (modo 2)
  → ABRE todas las no-esenciales INMEDIATAMENTE (no escalonado)
  → Las ESENCIALES permanecen cerradas

El GD arranca con POCA carga (solo esenciales)
→ Menor estrés en el arranque
→ Mayor seguridad para el GD
```

### 4.3 Operando con GD (ON_GD)

```
Al entrar en ON_GD (estado 8):
  → SHED detecta flanco ascendente IS_ON_GD
  → SHED_MODE = GD_RECONNECT (modo 3)
  → Iniciar acoplamiento ESCALONADO de no-esenciales

Acoplamiento escalonado:
  1. Verificar GD_LoadPct < GD_SHED_ON (90%)
  2. Cerrar siguiente no-esencial según RECONNECT_ORDER[]
  3. Esperar T_LOAD_CHECK_DELAY (3s) para estabilización
  4. Verificar carga post-acople
     - Si GD_LoadPct < 90%: continuar al siguiente
     - Si GD_LoadPct >= 90%: PARAR acoplamiento
  5. Repetir hasta completar o alcanzar límite

Si GD_LoadPct > GD_SHED_ON (90%) durante operación:
  → SHED_MODE = GD_REACTIVE_SHED (modo 4)
  → Deslastre reactivo: abrir no-esenciales por SHED_ORDER[]
  → Si carga baja < GD_SHED_OFF (70%): retomar acoplamiento
```

### 4.4 Retorno GD→RED

```
SCMTA detecta GRID_OK y espera 120s (WAIT_GRID_STABLE)
Transfiere: OPEN_QG1 → CLOSE_QT1 → GD_COOLDOWN

Al entrar en NORMAL_ON_GRID:
  → SHED detecta flanco ascendente IS_ON_GRID
  → SHED_MODE = GRID_RECONNECT (modo 5)
  → Reenganchar todas las no-esenciales según RECONNECT_ORDER[]
  → Verificar TR_LoadPct < GRID_SHED_ON antes de cada acople
  → Escalonado con T_RECONNECT_STEP (5s) entre cada paso
```

---

## 5. Parámetros Configurables

### Umbrales de Carga

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `GD_SHED_ON` | 90.0% | Umbral deslastre en GD |
| `GD_SHED_OFF` | 70.0% | Histéresis fin deslastre GD |
| `GRID_SHED_ON` | 85.0% | Umbral deslastre en RED (carga trafo) |
| `GRID_SHED_OFF` | 70.0% | Histéresis fin deslastre RED |

### Tiempos

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `T_SHED_STEP` | 5s | Tiempo entre pasos de deslastre |
| `T_RECONNECT_STEP` | 5s | Tiempo entre pasos de reenganche |
| `T_LOAD_FILTER` | 2s | Filtro anti-bouncing para mediciones |
| `T_LOAD_CHECK_DELAY` | 3s | Delay verificación carga post-acoplamiento |

### Arrays

| Parámetro | Tamaño | Descripción |
|-----------|--------|-------------|
| `FEEDER_ESSENTIAL[1..18]` | Bool | Clasificación esencial/no-esencial |
| `SHED_ORDER[1..18]` | Int | Orden de deslastre (prioridad) |
| `RECONNECT_ORDER[1..18]` | Int | Orden de reenganche/acoplamiento |
| `SHED_ENABLE[1..18]` | Bool | Habilitación individual por feeder |

---

## 6. Señalización entre FBs

### FB_SCMTA → FB_SHED
| Señal | Tipo | Descripción |
|-------|------|-------------|
| `IS_ON_GD` | Bool | Operando con GD (flanco → inicio acoplamiento) |
| `IS_ON_GRID` | Bool | Operando con RED (flanco → reenganche) |
| `IS_IN_TRANSFER` | Bool | Transferencia en curso |
| `TRANSFER_TO_GD` | Bool | **NUEVA** - TRUE desde OPEN_QT1 hasta ON_GD (flanco → desacople inicial) |

### FB_SHED → FB_CMD_ARBITER
| Señal | Tipo | Descripción |
|-------|------|-------------|
| `REQ_SHED_OPEN[1..18]` | Bool | Solicitud abrir feeder (deslastre/desacople) |
| `REQ_SHED_CLOSE[1..18]` | Bool | Solicitud cerrar feeder (reenganche/acoplamiento) |

### FB_SHED → HMI/Diagnóstico
| Señal | Tipo | Descripción |
|-------|------|-------------|
| `SHED_MODE` | Int | Modo actual (0-5) |
| `FEEDERS_SHED` | Int | No-esenciales actualmente abiertas |
| `FEEDERS_ESSENTIAL_COUNT` | Int | Cantidad de esenciales configuradas |
| `DIAG_GD_LOAD_OK` | Bool | Carga GD permite acoplar más |
| `DIAG_GRID_LOAD_OK` | Bool | Carga RED dentro de límites |

---

## 7. Secuencia Temporal Ejemplo

```
t=0s     RED alimentando, 18 feeders cerrados, TR_LoadPct = 60%
         SHED_MODE = IDLE

--- FALLA DE RED ---
t=10s    GRID_FAIL_DETECTED → OPEN_QT1
         TRANSFER_TO_GD = TRUE (flanco detectado)
         SHED_MODE = GD_INITIAL_SHED
         → Se abren 10 no-esenciales inmediatamente
         → 8 esenciales permanecen cerradas

t=12s    QT1 abierto confirmado → START_GD_DELAY
t=15s    START_GD → GD arrancando (solo esenciales = ~40% carga)
t=25s    GD_READY + estabilización → CLOSE_QG1
t=27s    ON_GD → IS_ON_GD flanco
         SHED_MODE = GD_RECONNECT
         GD_LoadPct = 40%

--- ACOPLAMIENTO ESCALONADO ---
t=27s    GD_LoadPct=40% < 90% → acoplar feeder no-esencial #1
t=30s    Verificación: GD_LoadPct=48% OK → siguiente
t=35s    GD_LoadPct=48% < 90% → acoplar feeder #2
t=38s    Verificación: GD_LoadPct=55% OK → siguiente
...
t=68s    GD_LoadPct=88% < 90% → acoplar feeder #8
t=71s    Verificación: GD_LoadPct=93% ≥ 90% → PARAR
         gdReconnectDone = TRUE, SHED_MODE = IDLE
         2 feeders no-esenciales quedan abiertos

--- RETORNO DE RED ---
t=180s   GRID_OK detectado → WAIT_GRID_STABLE
t=300s   120s cumplidos → OPEN_QG1 → CLOSE_QT1
t=304s   NORMAL_ON_GRID → IS_ON_GRID flanco
         SHED_MODE = GRID_RECONNECT
         → Reenganchar los 2 feeders que quedaban abiertos
t=314s   Todos los 18 feeders cerrados
         SHED_MODE = IDLE
```

---

## 8. Diagrama de Flujo Simplificado

```
                    ┌────────────────────┐
                    │   FUENTE: RED       │
                    │   18 feeders OK     │
                    └────────┬───────────┘
                             │
                    ┌────────▼───────────┐
                    │ TR_LoadPct > 85%?  │
                    └────────┬───────────┘
                        SÍ   │    NO
                    ┌────────▼──┐ ┌──▼────────┐
                    │GRID_SHED  │ │Todo OK     │
                    │Abrir      │ │IDLE        │
                    │no-esenc.  │ └────────────┘
                    └───────────┘

═══════════ FALLA RED ═══════════════════════════

                    ┌────────────────────┐
                    │ OPEN_QT1           │
                    │ TRANSFER_TO_GD=TRUE│
                    │ → Abrir TODAS      │
                    │   no-esenciales    │
                    └────────┬───────────┘
                             │
                    ┌────────▼───────────┐
                    │   FUENTE: GD       │
                    │   Solo esenciales  │
                    └────────┬───────────┘
                             │
                    ┌────────▼───────────┐
                    │ GD_LoadPct < 90%?  │
                    └────────┬───────────┘
                        SÍ   │    NO
                    ┌────────▼──┐ ┌──▼────────┐
                    │GD_RECON.  │ │Esperar    │
                    │Acoplar 1  │ │o deslastar│
                    │Verificar  │ │más        │
                    │carga      │ └────────────┘
                    └───────────┘

═══════════ RETORNO RED ═════════════════════════

                    ┌────────────────────┐
                    │ GRID_RECONNECT     │
                    │ Reenganchar todo   │
                    │ Verificar TR_Load  │
                    └────────────────────┘
```

---

## 9. Archivos Modificados

| Archivo | Versión | Cambio |
|---------|---------|--------|
| `03_FB_SHED.scl` | V2.0 | Reescritura completa: 6 modos operación, FEEDER_ESSENTIAL, deslastre RED+GD |
| `02_FB_SCMTA.scl` | V2.0 | Nuevo output `TRANSFER_TO_GD`, se activa en OPEN_QT1 |
| `09_DB_PARAMS.scl` | V2.0 | Nuevos: GD_SHED_ON, GD_SHED_OFF, GRID_SHED_ON, GRID_SHED_OFF, T_LOAD_CHECK_DELAY, FEEDER_ESSENTIAL[1..18] |
| `08_DB_GLOBAL_STATUS.scl` | V2.0 | Nuevos: SHED_MODE, FEEDERS_ESSENTIAL_COUNT, DIAG_GD_LOAD_OK, DIAG_GRID_LOAD_OK, TRANSFER_TO_GD |
| `10_OB1_MAIN.scl` | V2.0 | Actualización parámetros FB_SHED: nuevas entradas y salidas |
| `04_FB_CMD_ARBITER.scl` | V1.0 | Sin cambios (ya maneja REQ_SHED_OPEN/CLOSE) |

---

## 10. Reglas de Seguridad

1. **Esenciales NUNCA se deslastan** — en ningún modo de operación
2. **Enclavamiento fuente única** — QT1 XOR QG1 XOR QG2 (sin cambios)
3. **Desacople antes de arrancar GD** — reduce estrés del grupo, arranque seguro
4. **Verificación post-acople** — cada feeder acoplado en GD se verifica con delay de 3s
5. **Histéresis en todos los umbrales** — evita oscilación deslastre/reenganche
6. **Filtro anti-bouncing** — 2s en todas las mediciones de carga
7. **Prioridad SCMTA > SHED > MANUAL** — sin cambios en FB_CMD_ARBITER
