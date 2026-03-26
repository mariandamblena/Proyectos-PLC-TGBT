# Suite de Tests SCMTA TGBT V4

## Actualizacion 2026-03-26 (GD1/GD2 con unica senal RUN)

Se elimina el uso de senales externas `READY/RUNNING/ALARM` por generador en la logica de transferencia automatica.

Nuevo criterio para permitir cierre de QG1/QG2:

- `DO_GD_START` o `DO_GD2_START` activo (senal RUN existente)
- `GDx_MEASUREMENT_OK = TRUE` (Modbus medidor GDx OK)
- `GDx_V_L1L2/L2L3/L3L1` dentro de rango
- `GDx_FREQ` dentro de rango
- Condiciones anteriores sostenidas durante `T_GD_STABILIZATION = 30 s`

Si no se detecta fuente valida en el tiempo de arranque (`T_GD_READY_TIMEOUT`), SCMTA entra en falla de arranque.
La sirena queda mapeada a `%Q1.2` (salida siguiente a `GD2 RUN` en `%Q1.1`).

---

## Tests solicitados para este cambio

### Test A - Operacion normal RED -> GD -> RED (exitoso)

Objetivo: validar transferencia completa con el nuevo criterio de medicion/modbus.

1. Estado inicial: RED estable, `QT1` cerrado, `QG1/QG2` abiertos.
2. Forzar condicion de transferencia (falla de RED).
3. Verificar que SCMTA activa `DO_GD_START` (`%Q1.0`).
4. Simular en GD1: `GD1_MEASUREMENT_OK=TRUE`, tension y frecuencia en rango.
5. Verificar espera de 30 s continuos (`T_GD_STABILIZATION`).
6. Confirmar cierre de `QG1` y estado `ON_GD1`.
7. Restaurar RED y esperar retorno automatico segun temporizaciones.
8. Verificar estado final: `ON_GRID`, `QT1` cerrado, `QG1/QG2` abiertos, sin falla.

Criterio de aceptacion:

- No se cierran dos fuentes a la vez (exclusion QT1/QG1/QG2 siempre valida).
- La transferencia a GD ocurre solo despues de 30 s de medicion GD valida + Modbus OK.
- El retorno a RED conserva interlocks existentes.

### Test B - Falla de arranque a GD por ausencia de tension

Objetivo: validar que el sistema falla correctamente si no aparece fuente electrica del GD.

1. Estado inicial en RED estable.
2. Forzar condicion de transferencia (falla de RED).
3. Verificar `DO_GD_START = TRUE` (`%Q1.0`).
4. Mantener `GD1_MEASUREMENT_OK=FALSE` o tension/frecuencia fuera de rango.
5. Esperar vencimiento de `T_GD_READY_TIMEOUT`.
6. Verificar entrada a `FAULT_LOCKOUT` con codigo de falla de arranque GD.
7. Verificar activacion de sirena `%Q1.2`.

Criterio de aceptacion:

- No se cierra `QG1` ni `QG2` sin criterio electrico valido.
- Se genera alarma/falla de arranque.
- La salida de sirena `%Q1.2` se activa en falla.

## Descripcion
Suite de tests automatizados y simulacion interactiva para el sistema SCMTA TGBT V4.
Interfaz Bool DI, un solo generador (GD1), sin SHED, sin GD2 failover.

---

## Archivos

| Archivo | Descripcion |
|---------|-------------|
| `TEST_FB_HAPPY_PATH_V4.scl` | Test automatico: ciclo completo RED→GD1→RED (13 pasos) |
| `TEST_FB_FALLAS_V4.scl` | Test automatico: 7 escenarios de falla (grupos A-G) |
| `TEST_FB_MIN_STAY_AND_INTERLOCKS.scl` | Test automatico: T_MIN_GD_STAY + interlocks manual |
| `TEST_FB_HMI_MANUAL_SIM.scl` | Simulacion interactiva: operacion manual desde HMI con PLCSIM |
| `12_TEST_INSTANCE_DBS.scl` | Instance DBs para los 4 test FBs |
| `13_OB1_TEST_MAIN.scl` | OB1 alternativo para ejecutar tests |

---

## Orden de Importacion en TIA Portal V18

1. `DATA_BUFF` (DB global) + `DB_PARAMS`
2. FBs produccion: `01_FB_IO_NORMALIZE` .. `12_FB_PULSE_EXPANDER`
3. Instance DBs produccion: `11_INSTANCE_DBS.scl`
4. Test FBs: los 4 archivos `TEST_*.scl`
5. Test Instance DBs: `12_TEST_INSTANCE_DBS.scl`
6. OB1 de test: `13_OB1_TEST_MAIN.scl`

---

## Test 1: Happy Path V4 (TEST_HAPPY_PATH_DB)

**Valida el ciclo completo de transferencia automatica.**

### Secuencia (13 pasos)
| Paso | Descripcion | Validacion |
|------|-------------|------------|
| 0 | Inicializacion (5s) | Estado 0 o 1 |
| 1 | Operacion normal RED | Estado=1, IS_ON_GRID, GRID_OK |
| 2 | Falla RED: V=200V, F=48Hz | GRID_FAIL despues de filtro 2s |
| 3 | SCMTA abre QT1 → simula QT1_CLOSED=FALSE | IS_IN_TRANSFER |
| 4 | Arranque GD1 → simula GD_RUNNING=TRUE | DO_GD_START |
| 5 | GD1 listo → simula GD_READY=TRUE (5s delay) | Estado >= 5 |
| 6 | SCMTA cierra QG1 → simula QG1_CLOSED=TRUE | Estado >= 7 |
| 7 | Operando con GD1 (5s) | Estado=8, IS_ON_GD1 |
| 8 | Retorno RED: V=380V, F=50Hz | GRID_OK |
| 9 | SCMTA abre QG1 → simula QG1_CLOSED=FALSE | Estado=11 |
| 10 | SCMTA cierra QT1 → simula QT1_CLOSED=TRUE | Estado=12 |
| 11 | GD_COOLDOWN | Estado=1 (retorno completo) |
| 12 | Validacion final | Estado=1, IS_ON_GRID, sin FAULT |

### Variables de Control
```
TEST_HAPPY_PATH_DB.testEnable := TRUE   // Iniciar
TEST_HAPPY_PATH_DB.testReset := TRUE    // Reiniciar
TEST_HAPPY_PATH_DB.testStep             // Paso actual (0-12)
TEST_HAPPY_PATH_DB.testStatus           // Descripcion del paso
TEST_HAPPY_PATH_DB.testResults[0..12]   // PASS/FAIL por paso
TEST_HAPPY_PATH_DB.testAllPassed        // TRUE si todos OK
```

### Timeouts Reducidos
- `T_GRID_STABLE = 5s` (prod: 120s)
- `T_GD_COOLDOWN = 5s` (prod: 60s)
- `T_MIN_GD_STAY = 5s` (prod: 10min)

---

## Test 2: Escenarios de Falla V4 (TEST_FALLAS_DB)

**Valida todos los escenarios de falla del SCMTA con FAULT_LOCKOUT.**

### Grupos de Test
| Grupo | Falla | FAULT_CODE | Descripcion |
|-------|-------|------------|-------------|
| A | Timeout QT1 OPEN | 101 | QT1 no abre despues de T_OPEN_QT1 |
| B | GD1 ALARM arranque | 106 | Alarma GD1 durante arranque |
| C | GD1 NOT READY | 102 | GD1 no listo en T_GD_READY_TIMEOUT |
| D | Timeout CLOSE QG1 | 103 | QG1 no cierra despues de T_CLOSE_QG1 |
| E | GD1 ALARM ON_GD1 | 106 | Alarma GD1 durante operacion |
| F | QT1 NOT REMOTE | 111 | QT1 en LOCAL cuando se necesita abrir |
| G | Oscilacion RED | — | Bounce <2s NO dispara transferencia |

### Variables de Control
```
TEST_FALLAS_DB.testEnable := TRUE       // Iniciar
TEST_FALLAS_DB.testReset := TRUE        // Reiniciar
TEST_FALLAS_DB.testGroup                // Grupo actual (0-6 = A-G)
TEST_FALLAS_DB.testSubStep              // Sub-paso dentro del grupo
TEST_FALLAS_DB.testStatus               // Descripcion del estado
TEST_FALLAS_DB.testGroupResults[0..6]   // PASS/FAIL por grupo
TEST_FALLAS_DB.testAllPassed            // TRUE si todos OK
```

### Timeouts Reducidos
- `T_GD_READY_TIMEOUT = 5s` (prod: 30s)
- `T_GRID_STABLE = 3s` (prod: 120s)
- `T_GD_COOLDOWN = 3s` (prod: 60s)

---

## Test 3: Min Stay + Interlocks (TEST_MIN_STAY_DB)

**Valida T_MIN_GD_STAY y enclavamientos de fuente unica en modo manual.**

### Sub-tests
- **TEST_A**: Tiempo minimo en GD1 y GD2, alarma bypasea espera
- **TEST_B**: Interlocks manuales (B1-B7): fuente unica, LOCAL block, conflict
- **TEST_C**: Integracion completa

> Referir a `TEST_FB_MIN_STAY_AND_INTERLOCKS.scl` para detalles de cada sub-test.

---

## Test 4: Simulacion HMI Manual (HMI_SIM_DB)

**Simulacion interactiva para operar el sistema desde el HMI en modo manual con PLCSIM.**

### Que hace
- Reemplaza entradas fisicas (%I) con valores simulados
- Ejecuta IO_NORMALIZE → CMD_ARBITER → OUTPUTS internamente
- **NO ejecuta SCMTA** (modo manual puro, sin transferencia automatica)
- **NO ejecuta MODBUS_MANAGER** (sin comunicacion real)
- Cuando CMD_ARBITER envia un comando, el feedback DI se actualiza automaticamente con delay

### Como usar

1. En `13_OB1_TEST_MAIN.scl`: comentar todos los otros tests, descomentar `"HMI_SIM_DB"();`
2. Compilar y descargar a PLCSIM
3. Abrir Runtime HMI (KTP700 Basic)
4. Observar posiciones de interruptores en la pantalla del HMI
5. Presionar botones ABRIR/CERRAR desde el HMI → ver el feedback automatico

### Toggles de Simulacion (watch table)
| Variable | Efecto |
|----------|--------|
| `HMI_SIM_DB.SIM_GRID_FAIL` | Simula perdida RED (V=200V, F=48Hz) |
| `HMI_SIM_DB.SIM_GD_START` | Simula arranque GD1 (running + ready con delay 3s) |
| `HMI_SIM_DB.SIM_QT1_LOCAL` | Pone QT1 en LOCAL (bloquea comandos remotos) |
| `HMI_SIM_DB.SIM_QG1_LOCAL` | Pone QG1 en LOCAL |
| `HMI_SIM_DB.SIM_GD_ALARM` | Simula alarma GD1 |
| `HMI_SIM_DB.SIM_QT1_FAULT` | Simula falla/disparo QT1 |
| `HMI_SIM_DB.SIM_QG1_FAULT` | Simula falla/disparo QG1 |

### Parametros Configurables
| Variable | Default | Descripcion |
|----------|---------|-------------|
| `T_FEEDBACK` | 500ms | Delay entre CMD y cambio de posicion DI |
| `T_GD_WARMUP` | 3s | Delay entre GD_RUNNING y GD_READY |

### Flujo de Datos
```
HMI presiona boton → DATA_BUFF.REQ_MAN_xx_OPEN/CLOSE
→ CMD_ARBITER verifica interlocks
→ CMD_OPEN/CLOSE_xx sale
→ R_TRIG detecta flanco → TON feedback delay (500ms)
→ simQT1_CLOSED / simQG1_CLOSED se actualiza
→ IO_NORMALIZE procesa nuevo estado
→ Se escribe a DATA_BUFF → HMI muestra nueva posicion
```

### Que se puede probar
- Abrir/cerrar QT1 y QG1 desde HMI en modo manual
- Verificar que interlock evita cerrar QT1 si QG1 esta cerrado (y viceversa)
- Verificar que LOCAL bloquea comandos remotos
- Simular falla RED con toggle y ver indicadores HMI
- Arrancar GD1 con toggle y ver indicadores de estado
- Probar secuencia manual completa: abrir QT1 → arrancar GD → cerrar QG1

---

## Watch Table Recomendada

Para monitorear cualquier test, crear una watch table con:

```
// Control test
"TEST_xxx_DB".testEnable
"TEST_xxx_DB".testReset
"TEST_xxx_DB".testStep / testGroup
"TEST_xxx_DB".testStatus
"TEST_xxx_DB".testAllPassed

// Estado SCMTA (tests 1-3)
"TEST_xxx_DB".outState
"TEST_xxx_DB".outIsOnGrid
"TEST_xxx_DB".outIsOnGD1
"TEST_xxx_DB".outIsFault
"TEST_xxx_DB".outFaultCode
"TEST_xxx_DB".outGridOk
"TEST_xxx_DB".outGridFail

// Simulacion HMI (test 4)
"HMI_SIM_DB".SIM_GRID_FAIL
"HMI_SIM_DB".SIM_GD_START
"HMI_SIM_DB".simQT1_CLOSED
"HMI_SIM_DB".simQG1_CLOSED
"DATA_BUFF".BLOCK_LOCAL
"DATA_BUFF".BLOCK_INTERLOCK
"DATA_BUFF".ALM_INTERLOCK_VIOLATION
```
