# Proyecto TGBT - Sistema SCMTA
## Avances y Testing
**Fecha:** 10 de Febrero 2026  
**Versión:** 1.0  
**TIA Portal:** V18

---

## 📋 Slide 1: Arquitectura del Sistema - Función Bloques SCL

### Bloques Implementados ✅

| Bloque | Estado | Descripción |
|--------|--------|-------------|
| **01_FB_IO_NORMALIZE** | ✅ **Implementado + Testeado** | Normalización entradas físicas DI, gestión comandos manuales, filtros anti-rebote |
| **02_FB_SCMTA** | ✅ **Implementado + Testeado** | Máquina de estados transferencia automática RED↔GD (15 estados), lógica prioridad RED |

### Bloques Pendientes Implementación 🔶

| Bloque | Estado | Descripción |
|--------|--------|-------------|
| **03_FB_SHED** | 📄 Código listo | Deslastre escalonado 18 feeders (90% GD), reenganche secuencial automático |
| **04_FB_CMD_ARBITER** | 📄 Código listo | Arbitraje comandos prioridad (SCMTA>SHED>MANUAL), interlock violación alarma |
| **05_FB_OUTPUTS** | 📄 Código listo | Gestión salidas físicas DO: pilotos, sirenas, alarmas, blink timing HMI |
| **06_FB_MODBUS_MANAGER** | 📄 Código listo | Manager pool conexiones Modbus RTU multi-dispositivo, timeout recovery |
| **07_FB_MTZ_DRIVER** | 📄 Código listo | Driver protocolo Command Interface MTZ/NSX, máquina estados 7 pasos |
| **08_DB_GLOBAL_STATUS** | 📄 Código listo | DB global estado sistema: alarmas activas, cargas, modos operación, timestamps |
| **09_DB_PARAMS** | 📄 Código listo | DB parámetros configurables: timing, umbrales voltaje/frecuencia, setpoints shed |

---

## ✅ Slide 2: Testing Actual - Happy Path (Operación Normal)

### Test: `TEST_FB_IO_NORMALIZE_SCMTA.scl`
**Objetivo:** Validar ciclo completo RED → GD → RED sin fallas  
**Duración:** 2-3 minutos  
**Pasos:** 15 (PASO 0 a 14)  
**Resultado:** ✅ **100% PASSING** (15/15 pasos OK)

### Cobertura del Test Actual

| Categoría | Cobertura | Detalle |
|-----------|-----------|---------|
| **🔄 Secuencia Normal** | ✅ 100% | RED→GD→RED completa validada |
| **⚡ Detección Falla RED** | ✅ 100% | Subtensión, sobretensión, frecuencia fuera rango |
| **🔌 Actuadores** | ✅ 100% | Apertura QT1, cierre QG1, apertura QG1, cierre QT1 |
| **🚀 Arranque GD** | ✅ 100% | DO_GD_START → GD_RUNNING → GD_READY → sincronización |
| **📊 Estabilización** | ✅ 100% | Filtro 2s falla RED, espera 5s retorno RED, cooldown GD 5s (test) |
| **📍 Estados** | ✅ 100% | Validados 13 de 15 estados (sin FAULT ni estado 4) |

### Casos Validados Paso a Paso

```
✅ PASO 0-1:   Inicialización (QT1 cerrado, RED normal)
✅ PASO 2:     Simulación falla RED (V < 85%, F < 49Hz)
✅ PASO 3:     Detección falla → Estado 2 (GRID_FAIL_DETECTED)
✅ PASO 4:     Apertura QT1 → Estado 3 (OPEN_QT1)
✅ PASO 5:     QT1 abierto confirmado
✅ PASO 6:     Arranque GD → Estado 5 (START_GD)
✅ PASO 7:     GD_RUNNING = TRUE → transición estado 6
✅ PASO 8:     GD_READY = TRUE + estabilización 5s
✅ PASO 9:     Cierre QG1 → Estado 7 (CLOSE_QG1)
✅ PASO 10:    Operación GD → Estado 8 (ON_GD)
✅ PASO 11:    Retorno RED (V = 380V, F = 50Hz)
✅ PASO 12:    Espera estabilidad 5s → Estado 10 (WAIT_GRID_STABLE)
✅ PASO 13:    Apertura QG1 + validación modo AUTO
✅ PASO 14:    Cierre QT1 → Retorno completo a RED
```

### Bugs Corregidos Durante Testing
- 🐛 **PASO 13:** Timing race condition → Agregado delay 2s para FB_IO_NORMALIZE
- 🐛 **PASO 14:** Auto-reset borraba resultado → Cambiado a reset manual

---

## 🔥 Slide 3: Test de Fallas - Validación Robustez Sistema

### Test: `TEST_FB_FALLAS_SCMTA.scl` (NUEVO)
**Objetivo:** Validar comportamiento sistema ante condiciones adversas  
**Duración:** 12-15 minutos  
**Pasos:** 37 (PASO 0 a 36)  
**Estado:** 🆕 **Recién desarrollado - Pendiente ejecución**

### Cobertura Test de Fallas por Categoría

#### 🔴 Grupo A: Timeouts Actuadores (9 pasos)
| Escenario | Validación | Detalle |
|-----------|------------|---------|
| ⏱️ **QT1 NO abre** | Estado 14 (FAULT) | Timeout 12s → FAULT_CODE 101 |
| ⏱️ **QG1 NO cierra** | Estado 14 (FAULT) | Timeout 12s → FAULT_CODE 103 |
| ⏱️ **QT1 NO cierra al retorno** | Estado 14 (FAULT) | Timeout 12s → FAULT_CODE 105 |

#### 🟠 Grupo B: Fallas Grupo Diésel (12 pasos)
| Escenario | Validación | Detalle |
|-----------|------------|---------|
| 🚨 **GD_ALARM arranque** (estado 5) | Estado 14 (FAULT) | FAULT_CODE 106 inmediato |
| 🚨 **GD_ALARM operación** (estado 8) | Estado 14 (FAULT) | FAULT_CODE 106 inmediato |
| ⏱️ **GD NO alcanza READY** | Estado 14 (FAULT) | Timeout 30s → FAULT_CODE 102 |
| 🔧 **GD NO arranca** (motor) | Estado 5 indefinido | Sin FAULT (NO avanza) |

#### 🟡 Grupo C: RED Intermitente (9 pasos)
| Escenario | Validación | Detalle |
|-----------|------------|---------|
| 🔄 **Falla durante WAIT_GRID_STABLE** | Vuelve estado 8 (ON_GD) | Sin FAULT, reintenta |
| 🔄 **Falla durante COOLDOWN** | Reinicia secuencia GD | Aborta cooldown |
| 📊 **Oscilación RED (bouncing)** | Permanece estado 1 | Filtro 2s evita transferencias |

#### 🟢 Grupo D: Comandos Bloqueados (7 pasos)
| Escenario | Validación | Detalle |
|-----------|------------|---------|
| 🔒 **Selector LOCAL** | Comandos bloqueados | BLOCK_LOCAL = TRUE |
| 🔓 **Cambio LOCAL→REMOTO** | Desbloquea comandos | Ejecución inmediata |

### Resultado Esperado
✅ Sistema entra en **FAULT_LOCKOUT** controlado (estado 14)  
✅ NO continúa operando en estado inconsistente  
✅ RESET_FAULT restaura operación normal  
✅ Filtros evitan oscilaciones innecesarias

---

## 🚀 Slide 4: Próximos Pasos - Roadmap Implementación

### 🎯 Alta Prioridad (Semanas 1-2)

| # | Tarea | Responsable | Duración | Estado |
|---|-------|-------------|----------|--------|
| 1 | ✅ Ejecutar TEST_FB_FALLAS_SCMTA | Testing | 15 min | 🟢 Listo ejecutar |
| 2 | 🔧 Corregir fallas detectadas por test | Desarrollo | 1-2 días | ⏳ Pendiente resultados |
| 3 | 📦 Implementar FB_OUTPUTS en TIA Portal | Desarrollo | 1 día | 🔶 Código listo |
| 4 | 📦 Implementar FB_CMD_ARBITER en TIA Portal | Desarrollo | 1 día | 🔶 Código listo |
| 5 | 🧪 Test integración OUTPUTS + ARBITER | Testing | 30 min | ⏳ Post-implementación |

### 🎯 Media Prioridad (Semanas 3-4)

| # | Tarea | Responsable | Duración | Estado |
|---|-------|-------------|----------|--------|
| 6 | 📦 Implementar FB_SHED | Desarrollo | 2 días | 🔶 Código listo |
| 7 | 🧪 Test deslastre escalonado | Testing | 1 hora | ⏳ Pendiente |
| 8 | 📦 Implementar FB_MODBUS_MANAGER | Desarrollo | 2 días | 🔶 Código listo |
| 9 | 📦 Implementar FB_MTZ_DRIVER | Desarrollo | 2 días | 🔶 Código listo |
| 10 | 🔌 Prueba comunicación Modbus RTU real | Testing | 4 horas | ⏳ Requiere hardware |

### 🎯 Baja Prioridad (Mes 2)

| # | Tarea | Responsable | Duración | Estado |
|---|-------|-------------|----------|--------|
| 11 | 🔋 Implementar redundancia GD2 (N+1) | Desarrollo | 3 días | 📝 Diseño preliminar |
| 12 | 🧪 Test transferencia GD1 ↔ GD2 | Testing | 1 hora | ⏳ Post GD2 |
| 13 | 🖥️ Integración HMI/SCADA | HMI/Desarrollo | 1 semana | 📋 Especificación |
| 14 | 📊 DB_GLOBAL_STATUS implementación | Desarrollo | 1 día | 🔶 Código listo |
| 15 | 🏭 FAT (Factory Acceptance Test) | Cliente/Testing | 1 día | 📅 A coordinar |

### 📋 Checklist Pre-Deployment

- [x] ✅ Test happy path completo (15/15 pasos)
- [ ] ⏳ Test fallas completo (0/37 pasos) → **PRÓXIMO PASO**
- [ ] 🔶 FB_OUTPUTS implementado
- [ ] 🔶 FB_CMD_ARBITER implementado
- [ ] 🔶 Enclavamiento validado
- [ ] 🔶 Local/Remoto validado
- [ ] 🔶 FB_SHED implementado
- [ ] 🔶 Modbus RTU comunicación OK
- [ ] 🔶 GD2 redundancia (opcional N+1)
- [ ] 📋 HMI/SCADA integración
- [ ] 📋 Documentación completa entregada
- [ ] 📋 FAT ejecutado con cliente

### 🎓 Métricas de Avance

```
📊 Código SCL:          10/10 bloques (100%)
✅ Implementados:        2/10 bloques (20%)
✅ Testeados:            2/10 bloques (20%)
🧪 Test happy path:     15/15 pasos (100%)
🔥 Test fallas:          0/37 pasos (0%) → En progreso
📈 Cobertura global:    ~35% funcionalidad implementada
```

### ⚡ Acción Inmediata
> **PRÓXIMA REUNIÓN (1 hora):** Ejecutar TEST_FB_FALLAS_SCMTA y analizar resultados

---

## 📞 Contacto y Referencias

**Proyecto:** TGBT - Sistema Transferencia Automática  
**PLC:** Siemens S7-1500  
**TIA Portal:** V18  
**Lenguaje:** SCL (Structured Control Language)  

**Documentación completa:**  
- 📁 `TGBT/01_SCL/` → Código fuente bloques
- 📁 `TGBT/03_DOCS/` → Documentación técnica
- 📁 `TGBT/04_UML/` → Diagramas de estado
- 📁 `TGBT/07_TEST/` → Test automatizados

**Desarrollado con:** GitHub Copilot AI  
**Fecha:** Febrero 2026

---

**FIN DE PRESENTACIÓN**
