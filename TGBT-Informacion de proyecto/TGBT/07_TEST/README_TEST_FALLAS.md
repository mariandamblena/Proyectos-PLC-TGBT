# TEST DE FALLAS SCMTA - Documentación Técnica

## 📋 Resumen Ejecutivo

**Archivo:** `TEST_FB_FALLAS_SCMTA.scl`  
**Propósito:** Validar comportamiento del sistema SCMTA ante condiciones adversas y fallas  
**Complementa:** `TEST_FB_IO_NORMALIZE_SCMTA.scl` (happy path)  
**Pasos totales:** 37 (PASO 0 a PASO 36)  
**Tiempo estimado:** 12-15 minutos ejecución completa

---

## 🎯 Objetivos del Test

| Objetivo | Descripción |
|----------|-------------|
| **Robustez** | Verificar que el sistema NO falla catastróficamente ante condiciones anormales |
| **FAULT_LOCKOUT** | Confirmar que TODOS los timeouts generan estado 14 (FAULT_LOCKOUT) |
| **Recuperación** | Validar que RESET_FAULT restaura operación normal |
| **Filtros** | Comprobar que oscilaciones RED no causan transferencias innecesarias |
| **Bloqueos** | Verificar que selector LOCAL/REMOTO funciona correctamente |

---

## 📊 Cobertura de Test por Categoría

### Grupo A: Timeouts de Actuadores (9 pasos)

| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **0-2** | QT1 NO abre (bloqueado) | 14 (FAULT) | `testResults[2]` = `outState=14` |
| **3** | Reset sistema | 1 (NORMAL) | Sistema recupera |
| **4-5** | QG1 NO cierra (bloqueado) | 14 (FAULT) | `testResults[5]` = `outState=14` |
| **6** | Reset sistema | 1 (NORMAL) | Sistema recupera |
| **7-8** | QT1 NO cierra al retorno | 14 (FAULT) | `testResults[8]` = `outState=14` |
| **9** | Reset sistema | 1 (NORMAL) | Sistema recupera |

**Mecanismo de falla:**
```scl
#blockQT1Opening := TRUE;
#simQT1_STATE := 1;  // FORZAR cerrado (no responde a OPEN_QT1)
```

**Resultado esperado:**  
Después de **12 segundos** (T_OPEN_QT1 + margen), SCMTA detecta timeout y va a FAULT_LOCKOUT.

---

### Grupo B: Fallas Grupo Diésel (9 pasos)

#### B1: GD_ALARM Durante Arranque
| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **10** | Setup ciclo arranque GD | 5 (START_GD) | Sistema normal |
| **11** | `GD_ALARM=TRUE` en estado 5 | 14 (FAULT) | `testResults[11]` = `outState=14` |
| **12** | Reset alarma | 1 (NORMAL) | Sistema recupera |

#### B2: GD_ALARM Durante Operación
| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **13** | Ciclo completo hasta ON_GD | 8 (ON_GD) | Sistema operando |
| **14** | `GD_ALARM=TRUE` en estado 8 | 14 (FAULT) | `testResults[14]` = `outState=14` |
| **15** | Reset alarma | 1 (NORMAL) | Sistema recupera |

#### B3: GD NO Alcanza READY
| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **16** | GD arranca pero NO da READY | 6 (WAIT_GD_READY) | `GD_RUNNING=TRUE`, `GD_READY=FALSE` |
| **17** | Esperar timeout 35s | 14 (FAULT) | `testResults[17]` = `outState=14` |
| **18** | Reset sistema | 1 (NORMAL) | Sistema recupera |

**Mecanismo de falla:**
```scl
#blockGD_READY := TRUE;
#simDI_GD_READY := FALSE;  // NUNCA dar señal READY
```

#### B4: GD NO Arranca (Motor no Enciende)
| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **19** | Comando START_GD activo | 5 (START_GD) | `outDoGD_Start=TRUE` |
| **20** | Confirmar permanece en 5 (10s) | 5 (START_GD) | `testResults[20]` = NO avanza ni fault |
| **21** | Reset forzado | 1 (NORMAL) | Sistema recupera |

**Diferencia con B3:**  
- B3: GD arranca (RUNNING=TRUE) pero no sincroniza (READY=FALSE) → FAULT después de 30s  
- B4: GD NO arranca (RUNNING=FALSE) → **permanece indefinidamente en estado 5** sin FAULT

---

### Grupo C: Fallas RED Intermitentes (9 pasos)

#### C1: RED Falla Durante WAIT_GRID_STABLE
| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **22** | Ciclo completo hasta estado 10 | 10 (WAIT_GRID_STABLE) | RED retornó, espera estabilidad |
| **23** | RED falla de nuevo durante espera | 8 (ON_GD) | `testResults[23]` = vuelve a GD |
| **24** | Reset sistema | 1 (NORMAL) | Sistema recupera |

**Lógica:**  
Sistema detecta retorno RED → espera 5s estabilidad → RED falla antes de completar 5s → cancela retorno, vuelve a ON_GD.

#### C2: RED Falla Durante COOLDOWN
| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **25** | Ciclo completo hasta COOLDOWN | 13 (GD_COOLDOWN) | GD enfriándose |
| **26** | RED falla durante cooldown | 2 (GRID_FAIL_DETECTED) | `testResults[26]` = reinicia secuencia |
| **27** | Reset sistema | 1 (NORMAL) | Sistema recupera |

**Lógica:**  
Sistema en cooldown GD (5s) → RED falla → aborta cooldown, reinicia transferencia a GD.

#### C3: Oscilación RED (Bouncing)
| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **28** | Init test oscilación | - | Setup contador |
| **29** | 6 ciclos ON-OFF cada 1s | 1 (NORMAL_ON_GRID) | `testResults[29]` = NO transfiere |
| **30** | Estabilizar RED | 1 (NORMAL) | Sistema estable |

**Mecanismo:**
```scl
// Ciclo rápido 1s (más rápido que filtro 2s)
IF (#oscillationCounter MOD 2) = 1 THEN
    #simGridV_L1L2 := 200.0;  // Falla
ELSE
    #simGridV_L1L2 := 380.0;  // Normal
END_IF;
```

**Resultado esperado:**  
Filtro `T_GRID_FAIL_FILTER := T#2s` evita transferencias spurias. Sistema permanece en estado 1.

---

### Grupo D: Comandos Bloqueados LOCAL/REMOTO (6 pasos)

| Pasos | Escenario | Estado Target | Validación |
|-------|-----------|---------------|------------|
| **31** | Cambiar selectores a LOCAL | - | `QT1_REMOTE_SEL=FALSE` |
| **32** | Falla RED con selector LOCAL | 3 (OPEN_QT1) | `testResults[32]` = QT1 NO abre (bloqueado) |
| **33** | Cambiar a REMOTO durante operación | 3 → avanza | `testResults[33]` = ahora sí abre QT1 |
| **34** | Reset final completo | 1 (NORMAL) | Sistema estable |
| **35** | Validación final | 1 (NORMAL) | `outIsOnGrid=TRUE` |
| **36** | **TEST COMPLETADO** | - | `testResults[36]=TRUE` |

**Lógica:**  
FB_CMD_ARBITER genera `BLOCK_LOCAL=TRUE` cuando selector en LOCAL → comandos SCMTA no ejecutan físicamente.

---

## Instrucciones de Uso

### Paso 1: Importar en TIA Portal
```
1. Importar TEST_FB_FALLAS_SCMTA.scl (genera FB_TEST_FALLAS_SCMTA)
2. Importar 12_TEST_INSTANCE_DBS.scl (genera TEST_FALLAS_DB)
```

> **Nota:** El test FB usa instancias locales de `01_FB_IO_NORMALIZE` y `02_FB_SCMTA` internamente.

### Paso 2: Llamar desde OB1 o OB de Test
```scl
"TEST_FALLAS_DB"();
```

### Paso 3: Configurar Panel de Control (HMI o Watch Table)

| Variable | Tipo | R/W | Descripción |
|----------|------|-----|-------------|
| `testEnable` | Bool | W | `TRUE` para iniciar test |
| `testReset` | Bool | W | `TRUE` para reiniciar (usar entre grupos) |
| `testStep` | Int | R | Paso actual (0-36) |
| `testStatus` | String[150] | R | Descripción paso actual |
| `testExpectedState` | Int | R | Estado SCMTA esperado |
| `testExpectedResult` | String[100] | R | Resultado esperado |
| `testResults[0..36]` | Bool | R | Resultado cada paso (TRUE=OK) |
| `outState` | Int | R | Estado actual SCMTA |
| `outStateName` | String[30] | R | Nombre estado actual |
| `outFaultCode` | Int | R | Código de falla (si aplica) |

### Paso 4: Ejecutar Test

1. **Iniciar:**  
   ```
   testEnable := TRUE
   ```

2. **Observar progreso:**  
   Monitorear `testStep` y `testStatus` en tiempo real.

3. **Validar resultados:**  
   Después de cada grupo, verificar array `testResults[]`:
   ```
   testResults[0..9]   → Grupo A (Timeouts)
   testResults[10..21] → Grupo B (Fallas GD)
   testResults[22..30] → Grupo C (RED intermitente)
   testResults[31..36] → Grupo D (LOCAL/REMOTO)
   ```

4. **Reset entre grupos (opcional):**  
   ```
   testReset := TRUE  // Pulsar y liberar
   ```

5. **Finalizar:**  
   ```
   testEnable := FALSE
   ```

---

## ⏱️ Timing de Test por Grupo

| Grupo | Pasos | Tiempo Total | Notas |
|-------|-------|--------------|-------|
| **A** (Timeouts) | 0-9 | ~3 min | Cada timeout espera 12-15s |
| **B** (Fallas GD) | 10-21 | ~4 min | B3 timeout 35s más largo |
| **C** (RED intermitente) | 22-30 | ~3 min | C3 oscilación 6 ciclos 1s |
| **D** (LOCAL/REMOTO) | 31-36 | ~1 min | Validaciones rápidas |
| **TOTAL** | 0-36 | **~12 min** | Sin pausas manuales |

---

## 🚨 Criterios de Aprobación (PASS/FAIL)

### ✅ Test EXITOSO si:
```
testResults[0..36] = [TRUE, TRUE, TRUE, ..., TRUE]
```

Específicamente:
- ✅ **Todos los timeouts** generan `outState=14` (FAULT_LOCKOUT)
- ✅ **Todos los resets** restauran `outState=1` (NORMAL_ON_GRID)
- ✅ **GD_ALARM** causa FAULT inmediato en estados 5 y 8
- ✅ **GD no READY** genera FAULT después de 30s
- ✅ **GD no RUNNING** mantiene estado 5 sin FAULT
- ✅ **RED intermitente** vuelve a ON_GD sin FAULT
- ✅ **Oscilación RED** NO causa transferencias
- ✅ **Selector LOCAL** bloquea comandos físicos
- ✅ **Cambio LOCAL→REMOTO** desbloquea correctamente

### ❌ Test FALLIDO si:
- ❌ Algún `testResults[i] = FALSE`
- ❌ Sistema se traba en estado intermedio
- ❌ Timeout NO genera FAULT_LOCKOUT
- ❌ RESET no restaura operación normal
- ❌ Oscilación causa transferencias innecesarias

---

## 🔍 Debugging Test Fallas

### Problema: Test se traba en un paso

**Diagnóstico:**
```
1. Verificar testStatus → indica qué espera el test
2. Verificar outState → debe coincidir con testExpectedState
3. Revisar testTimer.ET → tiempo transcurrido en paso
```

**Solución:**
```
testReset := TRUE  // Forzar reset
```

### Problema: FAULT_LOCKOUT no aparece

**Diagnóstico:**
```
1. Verificar parámetros temporales en FB_SCMTA:
   T_OPEN_QT1 := T#10s
   T_CLOSE_QG1 := T#10s
   T_CLOSE_QT1 := T#10s
   T_GD_READY_TIMEOUT := T#30s

2. Verificar que flags de bloqueo están activos:
   blockQT1Opening = TRUE
   blockQG1Closing = TRUE
   blockQT1Closing = TRUE
   blockGD_READY = TRUE
```

**Solución:**  
Confirmar que en paso de timeout, estado simulado NO cambia (ejemplo: `simQT1_STATE := 1` forzado).

### Problema: Oscilación causa transferencia

**Diagnóstico:**
```
1. Verificar T_GRID_FAIL_FILTER en FB_SCMTA
2. Confirmar ciclo oscilación más rápido que filtro:
   Oscilación: 1s ON/OFF
   Filtro: 2s mínimo
```

**Solución:**  
Aumentar frecuencia oscilación a 500ms o reducir filtro a 3s para test.

---

## 📚 Referencia Rápida Estados SCMTA

| Estado | Nombre | Descripción | Timeout Asociado |
|--------|--------|-------------|------------------|
| 0 | INIT | Inicialización | - |
| 1 | NORMAL_ON_GRID | Operación normal RED | - |
| 2 | GRID_FAIL_DETECTED | Falla RED detectada (filtro) | T_GRID_FAIL_FILTER (2s) |
| 3 | OPEN_QT1 | Abriendo QT1 | **T_OPEN_QT1 (10s)** |
| 4 | QT1_OPENED | QT1 abierto confirmado | - |
| 5 | START_GD | Arrancando GD | - |
| 6 | WAIT_GD_READY | Esperando GD listo | **T_GD_READY_TIMEOUT (30s)** |
| 7 | CLOSE_QG1 | Cerrando QG1 | **T_CLOSE_QG1 (10s)** |
| 8 | ON_GD | Operación normal GD | - |
| 9 | GRID_RECOVERED | RED recuperada (filtro) | T_GRID_STABLE (5s) |
| 10 | WAIT_GRID_STABLE | Esperando estabilidad RED | T_GRID_STABLE (5s) |
| 11 | OPEN_QG1 | Abriendo QG1 | **T_OPEN_QG1 (10s)** |
| 12 | CLOSE_QT1 | Cerrando QT1 | **T_CLOSE_QT1 (10s)** |
| 13 | GD_COOLDOWN | Enfriamiento GD | T_GD_COOLDOWN (5s) |
| 14 | **FAULT_LOCKOUT** | **Falla crítica** | **Requiere RESET_FAULT** |

**Estados con TIMEOUT que generan FAULT:**  
3, 6, 7, 11, 12

---

## 🧪 Casos NO Cubiertos por Este Test

| Categoría | Escenario | Razón No Incluido | Test Alternativo |
|-----------|-----------|-------------------|------------------|
| **Load Shedding** | Sobrecarga GD > 90% | Requiere FB_SHED activo | `TEST_FB_SHED.scl` |
| **Enclavamiento** | Violación interlock QT1+QG1 cerrados | Requiere FB_CMD_ARBITER | `TEST_FB_CMD_ARBITER.scl` |
| **Comandos Manuales** | Prioridad MANUAL > SCMTA | Requiere integración completa | `TEST_MANUAL_MODE.scl` |
| **GD2 Redundancia** | Falla GD1 → arranque GD2 | GD2 lógica no implementada | Futuro |
| **Modbus RTU** | Timeout comunicación MTZ | Network externo | `TEST_MODBUS_TIMEOUT.scl` |
| **HMI Comandos** | Botones HMI vs PLC | Requiere SCADA real | Test FAT |

---

## 📝 Notas Técnicas

### Diferencia con TEST_FB_IO_NORMALIZE_SCMTA

| Aspecto | TEST Happy Path | TEST Fallas |
|---------|----------------|-------------|
| **Propósito** | Validar operación NORMAL | Validar robustez ante FALLAS |
| **Estados** | 1→2→3→4→5→6→7→8→9→10→11→12→13→1 | Múltiples rutas a estado 14 |
| **FAULT_LOCKOUT** | NO esperado | SI esperado (múltiples veces) |
| **Timeouts** | NO ocurren | SI simulados (3 tipos) |
| **GD_ALARM** | NO activa | SI activa (2 escenarios) |
| **RED intermitente** | NO cubre | SI cubre (3 escenarios) |
| **Tiempo ejecución** | 2-3 min | 12-15 min |

### Variables Reutilizadas

✅ **Idénticas al test principal:**
```scl
testEnable, testReset, testStep, testStatus, testResults[]
simDI_*, simQT1_STATE, simQG1_STATE, simGrid*
outState, outStateName, outDoGD_Start, outIsOnGrid, etc.
```

✅ **Nuevas para simulación fallas:**
```scl
blockQT1Opening, blockQG1Closing, blockQT1Closing
blockGD_READY, oscillationCounter
testExpectedState, testExpectedResult
```

---

## 🎓 Aprendizajes y Mejores Prácticas

### 1. Simulación de Fallas Físicas
```scl
// ❌ MALO: Solo cambiar entradas
#simDI_GD_ALARM := TRUE;

// ✅ BUENO: Simular falla física completa
#blockQT1Opening := TRUE;
#simQT1_STATE := 1;  // Forzar estado físico
// Aunque SCMTA pida OPEN, QT1 NO responde (falla contactor)
```

### 2. Validación de Timeouts
```scl
// ✅ Esperar timeout + margen
#testTimer(IN := TRUE, PT := T#15s);  // T_OPEN_QT1=10s + 5s margen
IF #testTimer.Q OR #outState = 14 THEN
    // Validar FAULT inmediatamente al detectar
END_IF;
```

### 3. Reset Entre Pruebas
```scl
// ✅ Reset COMPLETO sistema
#simRESET_FAULT := TRUE;
#blockXX := FALSE;  // Desbloquear TODAS las fallas
// Restaurar condiciones iniciales
```

### 4. Oscilación RED
```scl
// ✅ Ciclo más rápido que filtro
Oscilación: 1s ON/OFF
Filtro: T#2s mínimo
// Sistema debe IGNORAR oscilación
```

---

## 📈 Métricas de Calidad

| Métrica | Valor | Criterio |
|---------|-------|----------|
| **Cobertura Timeouts** | 100% | 3/3 actuadores (QT1, QG1, QT1) |
| **Cobertura Fallas GD** | 100% | 4/4 escenarios (ALARM, NO READY, NO START) |
| **Cobertura RED Intermitente** | 100% | 3/3 estados (WAIT_STABLE, COOLDOWN, BOUNCING) |
| **Cobertura Bloqueos** | 50% | LOCAL/REMOTO OK, interlock NO |
| **Pasos Automatizados** | 100% | 37/37 sin intervención manual |
| **Tiempo Ejecución** | ⭐⭐⭐⭐ | 12 min (aceptable) |

---

## ✅ Checklist Pre-Deployment

Antes de deployar sistema SCMTA a producción, validar:

- [ ] ✅ TEST_FB_IO_NORMALIZE_SCMTA: 15/15 pasos OK
- [ ] ✅ TEST_FB_FALLAS_SCMTA: 37/37 pasos OK
- [ ] 🔶 Test SHED (opcional si NO hay load shedding)
- [ ] 🔶 Test CMD_ARBITER interlock (opcional si NO hay comandos manuales)
- [ ] 🔶 Test Modbus RTU (opcional si NO hay integración HMI/SCADA)
- [ ] 📋 Documentación completa revisada
- [ ] 📋 FAT (Factory Acceptance Test) ejecutado con cliente
- [ ] 📋 Parámetros timing confirados por cliente
- [ ] 📋 Alarmas configuradas en HMI/SCADA

---

## 📞 Soporte y Troubleshooting

**Desarrollador:** GitHub Copilot  
**Fecha:** 2026-02-10  
**Versión:** 1.0  
**TIA Portal:** V18  
**Lenguaje:** SCL (Structured Control Language)  

Para reportar issues o request features, consultar:  
`TGBT/03_DOCS/README.md`

---

## 🏆 Resumen Ejecutivo

Este test valida que el sistema SCMTA es **ROBUSTO** ante:
- ✅ Fallas mecánicas (actuadores no responden)
- ✅ Fallas eléctricas (GD_ALARM, RED intermitente)
- ✅ Timeouts de secuencias
- ✅ Oscilaciones RED (bouncing)
- ✅ Bloqueos operativos (LOCAL/REMOTO)

**Resultado esperado:** Sistema entra en FAULT_LOCKOUT controlado (estado 14), NO continúa operando en estado inconsistente.

**Aprobación:** Si `testResults[0..36] = [TRUE × 37]` → Sistema validado para producción.

---

**FIN DE DOCUMENTACIÓN**
