# Test FB_IO_NORMALIZE + FB_SCMTA

## Descripción
Test automatizado con secuencia de validación paso a paso con delays configurados para poder observar y validar cada transición de estado del sistema SCMTA.

**Implementado como Function Block (FB)** con todas las variables inicializadas. Se llama desde el Main.

## Características
- **10 pasos** de test secuenciales
- **Delays programados** en cada paso para observación
- **Estados esperados** definidos para cada paso
- **Simulación automática** de entradas físicas y transiciones
- **Validación manual** observando variables en watch table
- **Timer interno** (VAR STAT) sin necesidad de DBs externos
- **Variables inicializadas** con valores por defecto

---

## Uso Rápido

### ⚙️ Configuración Inicial

1. **Importar** `TEST_FB_IO_NORMALIZE_SCMTA.scl` como **FB_TEST_SCMTA** en TIA Portal
2. **Crear instance DB** (ej: `DB_TEST_SCMTA`)
3. **Llamar desde Main (OB1):**
   ```scl
   "DB_TEST_SCMTA"();
   ```

### ▶️ Ejecución

1. **Compilar** y descargar a PLCSIM
2. **Activar** `DB_TEST_SCMTA.testEnable = TRUE` en watch table
3. **Observar** el avance automático a través de los pasos
4. **Monitorear** variables en el instance DB

---

## Variables de Control

### Control del Test
| Variable | Tipo | Descripción |
|----------|------|-------------|
| `testEnable` | Bool | **Activar para iniciar test** (cambiar a TRUE) |
| `testStep` | Int | Paso actual del test (0-10) |
| `testStatus` | String | Descripción del paso actual |
| `testExpectedState` | Int | Estado SCMTA esperado en este paso |
| `testExpectedResult` | String | Resultado esperado para validar |

### Outputs a Monitorear
| Variable | Tipo | Descripción |
|----------|------|-------------|
| `outState` | Int | Estado actual FB_SCMTA |
| `outStateName` | String | Nombre del estado actual |
| `outIsOnGrid` | Bool | Sistema operando con RED |
| `outIsOnGD` | Bool | Sistema operando con GD |
| `outGridOk` | Bool | RED OK (dentro de límites) |
| `outGridFail` | Bool | RED en falla |
| `outDoGD_Start` | Bool | Comando arranque GD |
| `outReqScmtaOpenQT1` | Bool | Comando apertura QT1 |
| `outReqScmtaCloseQG1` | Bool | Comando cierre QG1 |
| `outElapsedTime` | Time | Tiempo transcurrido en estado actual |

---

## Secuencia del Test

### Paso 0: Inicialización (5s)
**Configuración:**
- `simDI_SYS_AUTO = TRUE`
- `simQT1_STATE = 1` (cerrado)
- `simGridV_L1L2/L2L3/L3L1 = 380V`
- `simGridFreq = 50Hz`
- `simDI_GD_READY = FALSE`

**Validar:**
- ✅ `outState` debe llegar a 0 o 1 (INIT o NORMAL_ON_GRID)

---

### Paso 1: Operación Normal RED (3s)
**Descripción:** Sistema estabilizado operando con RED

**Validar:**
- ✅ `outState = 1` (NORMAL_ON_GRID)
- ✅ `outIsOnGrid = TRUE`
- ✅ `outGridOk = TRUE`

---

### Paso 2: Simulación Falla RED (4s)
**Acción automática:**
- Reduce tensiones a 200V
- Reduce frecuencia a 48Hz

**Validar:**
- ✅ `outGridFail = TRUE` (después de ~2s de filtro)
- ✅ `outState` transiciona a 2 o 3 (GRID_FAIL_DETECTED o WAIT_OPEN_QT1)

---

### Paso 3: Apertura QT1 (espera comando)
**Acción automática:**
- Detecta comando `outReqScmtaOpenQT1 = TRUE`
- Simula apertura cambiando `simQT1_STATE = 0`

**Validar:**
- ✅ `outReqScmtaOpenQT1 = TRUE`
- ✅ `outState = 3` (WAIT_OPEN_QT1)
- ✅ `simQT1_STATE` cambia a 0 después de 1s

---

### Paso 4: Arranque GD (2s)
**Acción automática:**
- Espera comando `outDoGD_Start = TRUE`
- Simula GD arranca: `simDI_GD_RUNNING = TRUE`

**Validar:**
- ✅ `outDoGD_Start = TRUE`
- ✅ `outState = 5` (START_GD)
- ✅ `simDI_GD_RUNNING = TRUE` después de 2s

---

### Paso 5: GD Estabilizando (3s)
**Acción automática:**
- Espera 3s de estabilización
- Activa `simDI_GD_READY = TRUE`

**Validar:**
- ✅ `outState = 6` (WAIT_GD_READY)
- ✅ `simDI_GD_READY = TRUE` después de 3s

---

### Paso 6: Cierre QG1 (6s)
**Acción automática:**
- Espera delay estabilización (5s en SCMTA)
- Detecta comando `outReqScmtaCloseQG1 = TRUE`
- Simula cierre: `simQG1_STATE = 1`

**Validar:**
- ✅ `outReqScmtaCloseQG1 = TRUE`
- ✅ `outState = 7` (WAIT_CLOSE_QG1)
- ✅ `simQG1_STATE = 1` después de delay

---

### Paso 7: Operando con GD (5s)
**Descripción:** Sistema estabilizado operando con GD

**Validar:**
- ✅ `outState = 8` (NORMAL_ON_GD)
- ✅ `outIsOnGD = TRUE`
- ✅ `outIsOnGrid = FALSE`

---

### Paso 8: Retorno de RED (3s)
**Acción automática:**
- Restaura tensiones a 380V
- Restaura frecuencia a 50Hz

**Validar:**
- ✅ `outGridOk = TRUE` (después de ~2s de filtro)
- ✅ `outState` transiciona a 9 o 10 (GRID_RETURN_DETECTED o WAIT_OPEN_QG1)
- ✅ Debe iniciar secuencia de retransferencia a RED

---

### Paso 9: Test Pulsadores Manuales (10s)
**Acción automática:**
- Cambia a modo manual: `simDI_SYS_AUTO = FALSE`
- Genera pulsos en `simDI_QT1_PB_OPEN` cada 2s

**Validar:**
- ✅ `outReqManQT1_Open` debe pulsar cuando detecta rising edge
- ✅ Sistema debe responder a comandos manuales

---

### Paso 10: Test Completado
**Acción automática:**
- Detiene el test: `testEnable = FALSE`

**Revisión Final:**
- ✅ Todos los pasos completados sin errores
- ✅ Transiciones de estado correctas
- ✅ Comandos de salida activados en momentos esperados

---

## Watch Table Recomendada

### Grupo 1: Control Test
```
testEnable
testStep
testStatus
testExpectedState
testExpectedResult
```

### Grupo 2: Estado SCMTA
```
outState
outStateName
outIsOnGrid
outIsOnGD
outGridOk
outGridFail
outElapsedTime
```

### Grupo 3: Comandos Salida
```
outReqScmtaOpenQT1
outReqScmtaCloseQT1
outReqScmtaOpenQG1
outDoGD_Start
outDoGD_Stop
outReqManQT1_Open
```

### Grupo 4: Simulación (opcional)
```
simQT1_STATE
simQG1_STATE
simGridV_L1L2
simGridFreq
simDI_GD_READY
simDI_GD_RUNNING
```

---

## Notas Importantes

⚠️ **Observación Manual:** Aunque el test es automático, debes observar las variables en la watch table para validar cada paso.

⚠️ **Tiempos de Filtro:** Los cambios en RED tienen filtros de 2s (tonGridFailFilter, tonGridStableFilter), por eso algunos pasos tienen delays de 3-4s.

⚠️ **Delays en SCMTA:** El delay de estabilización GD es de 5s antes de cerrar QG1, configurado en el paso 6.

⚠️ **Modo Manual:** El paso 9 prueba comandos manuales, debe generar pulsos en `outReqManQT1_Open`.

✅ **Test Reproducible:** Puedes reiniciar el test en cualquier momento poniendo `testEnable = FALSE` y luego `TRUE` nuevamente.

---

## Troubleshooting

**El test no avanza:**
- Verificar `testEnable = TRUE`
- Observar `testStep` y `testStatus`
- Revisar si el estado SCMTA coincide con `testExpectedState`

**Falla en un paso específico:**
- Leer `testExpectedResult` para saber qué validar
- Comparar `outState` con `testExpectedState`
- Verificar que las condiciones del FB_SCMTA se cumplan

**Test muy rápido:**
- Aumentar los tiempos PT en los `testTimer(IN := TRUE, PT := T#Xs)`
- Cada paso tiene su delay configurable

**Quiero pausar en un paso:**
- Cambiar `testEnable = FALSE` cuando llegue al paso deseado
- Observar variables el tiempo necesario
- Reactivar `testEnable = TRUE` para continuar

---

## Ejemplo de Ejecución

```
[00:00] testStep=0, testStatus="PASO 0: Inicializando test..."
[00:05] testStep=1, testStatus="PASO 1: Operación normal RED"
        ✅ outState=1, outIsOnGrid=TRUE
[00:08] testStep=2, testStatus="PASO 2: Falla RED"
        Tensión baja a 200V, Frecuencia a 48Hz
[00:10] ✅ outGridFail=TRUE
[00:12] testStep=3, testStatus="PASO 3: Comando OPEN_QT1"
        ✅ outReqScmtaOpenQT1=TRUE
[00:13] simQT1_STATE=0 (abierto)
[00:15] testStep=4, testStatus="PASO 4: START_GD"
        ✅ outDoGD_Start=TRUE
[00:17] simDI_GD_RUNNING=TRUE
...
[00:50] testStep=10, testStatus="PASO 10: TEST COMPLETADO"
        testEnable=FALSE (detenido)
```

---

**Autor**: Sistema SCMTA TGBT  
**Fecha**: 5 de febrero de 2026
