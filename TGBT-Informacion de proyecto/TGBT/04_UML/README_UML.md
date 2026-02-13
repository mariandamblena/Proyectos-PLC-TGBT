# Diagramas UML - Sistema TGBT SCMTA

## 📊 Catálogo de Diagramas

### 1. State Machine Diagrams (Máquinas de Estados)

#### 11_UML_SCMTA_StateMachine.puml
**Descripción:** Máquina de estados principal del sistema SCMTA (transferencia automática RED↔GD)  
**Estados:** 15 estados (0-14)  
**Configuración:** 1 GD (QG1 únicamente)  
**Casos de uso:**
- Operación normal RED → falla → transferencia GD → retorno RED
- Timeouts de actuadores (QT1, QG1)
- Fallas GD (ALARM, NO READY)
- Estados FAULT_LOCKOUT

**Estados principales:**
```
0:  INIT
1:  NORMAL_ON_GRID
2:  GRID_FAIL_DETECTED
3:  OPEN_QT1
5:  START_GD
6:  WAIT_GD_READY
7:  CLOSE_QG1
8:  ON_GD
9:  GRID_RETURN_DETECTED
10: WAIT_GRID_STABLE
11: OPEN_QG1
12: CLOSE_QT1
13: GD_COOLDOWN
14: FAULT_LOCKOUT
```

---

#### 14_UML_SCMTA_GD2_StateMachine.puml ⭐ NUEVO
**Descripción:** Máquina de estados SCMTA con redundancia N+1 (2 grupos diésel)  
**Estados:** 15+ estados (incluye GD1 y GD2)  
**Configuración:** 2 GD (QG1 primario + QG2 backup)  
**Casos de uso:**
- Failover automático GD1 → GD2 si GD1_ALARM
- Transferencia GD2 → GD1 si GD2_ALARM y GD1_AVAILABLE
- Prioridad: RED > GD1 > GD2
- Enclavamiento triple: solo UNO cerrado (QT1 XOR QG1 XOR QG2)

**Estados adicionales GD2:**
```
START_GD2_DELAY:      Delay antes arranque GD2 (failover)
START_GD2:            Arranque GD2 (backup)
WAIT_GD2_READY:       Espera GD2_READY + estabilización
CLOSE_QG2:            Cierre QG2
ON_GD2:               Operación con GD2 (backup activo)
SWITCH_GD1_TO_GD2:    Transferencia GD1→GD2 (falla GD1)
SWITCH_GD2_TO_GD1:    Transferencia GD2→GD1 (falla GD2)
OPEN_ACTIVE_GD:       Apertura GD activo (QG1 o QG2)
```

**Lógica failover:**
```
GD1 (primario) con ALARM → intenta arrancar GD2
GD2 (backup) con ALARM → intenta volver a GD1 si disponible
Si ambos GD no disponibles → FAULT_LOCKOUT (código 209)
```

---

#### 12_UML_MTZ_Driver_StateMachine.puml
**Descripción:** Driver Modbus RTU para interruptores MTZ/NSX (Command Interface)  
**Estados:** 7 estados driver  
**Protocolo:** Siemens MTZ/NSX Command Interface (registros 8000-8021, 32000-32001)  
**Casos de uso:**
- Comando OPEN interruptor
- Comando CLOSE interruptor
- Comando RESET alarmas
- Polling respuesta (timeout 5s)
- Confirmación estado físico (OF/SD/PF bits)

**Estados driver:**
```
IDLE:            Esperando comando (lectura cíclica 32000-32001)
BUILD_BUFFER:    Construir buffer comando (8000-8019)
WRITE_CMD:       Escribir FC16 Multiple Registers
POLL_RESPONSE:   Polling 8020-8021 (max 5s)
CONFIRM_STATE:   Confirmar estado físico (max 2s)
DONE:            Comando completado OK
ERROR:           Falla operación (timeout/error code)
```

**Password:** "3333" (ASCII en registros 8004-8005)

---

### 2. Activity Diagrams (Diagramas de Actividad)

#### 13_UML_SHED_Activity.puml
**Descripción:** Diagrama de actividad deslastre y reenganche automático (18 feeders)  
**Trigger:** Sobrecarga GD > 90% o Trafo > 95%  
**Proceso:**
1. Filtro señal 2s (anti-bouncing)
2. Deslastre escalonado según SHED_ORDER[1..18]
3. Delay T_SHED_STEP (3-5s) entre pasos
4. Histéresis: reconectar si carga < 70%
5. Reenganche después retorno RED

**Variables clave:**
```
SHED_ON:            90.0% (umbral activación)
SHED_OFF:           70.0% (histéresis desactivación)
SHED_ORDER[1..18]:  Prioridad deslastre (configurable)
RECONNECT_ORDER:    Prioridad reenganche (inverso)
T_SHED_STEP:        T#5s (delay entre pasos)
```

**Integración:**
- FB_SHED genera REQ_SHED_OPEN[feederID]
- FB_CMD_ARBITER verifica LOCAL/REMOTO
- FB_MTZ_DRIVER ejecuta comando Modbus

---

## 🔧 Herramientas para Visualización

### PlantUML
Todos los diagramas están en formato **PlantUML** (.puml).

**Opciones de renderizado:**

1. **VS Code Extension:**
   - Instalar: "PlantUML" (jebbs.plantuml)
   - `Alt+D` para preview

2. **Online:**
   - http://www.plantuml.com/plantuml/
   - Copiar/pegar código .puml

3. **CLI:**
   ```bash
   java -jar plantuml.jar *.puml
   ```

4. **Exportar PNG/SVG:**
   ```bash
   java -jar plantuml.jar -tpng 11_UML_SCMTA_StateMachine.puml
   java -jar plantuml.jar -tsvg 14_UML_SCMTA_GD2_StateMachine.puml
   ```

---

## 📋 Estado Implementación vs Diseño

| Diagrama | Estado Diseño | Estado Implementación | Testeado |
|----------|---------------|----------------------|----------|
| **11_UML_SCMTA_StateMachine** | ✅ Completo | ✅ Implementado (FB_SCMTA) | ✅ Happy path OK |
| **14_UML_SCMTA_GD2** | ✅ Completo | 🔶 Preparado (señales existen) | ❌ Sin lógica GD2 |
| **12_UML_MTZ_Driver** | ✅ Completo | 📄 Código listo | ❌ Sin hardware |
| **13_UML_SHED_Activity** | ✅ Completo | 📄 Código listo | ❌ Pendiente |

---

## 🔄 Actualizaciones Recientes

### 2026-02-10
- ✅ Creado **14_UML_SCMTA_GD2_StateMachine.puml** (redundancia N+1)
- ✅ Agregados estados: START_GD2, WAIT_GD2_READY, CLOSE_QG2, ON_GD2
- ✅ Agregadas transiciones failover: SWITCH_GD1_TO_GD2, SWITCH_GD2_TO_GD1
- ✅ Documentados códigos falla GD2: 202, 203, 204, 206, 209
- ✅ Lógica prioridad: RED > GD1 > GD2

### 2026-02-09
- ✅ Validado 11_UML_SCMTA_StateMachine con test happy path
- ✅ Confirmados timing parámetros (T_OPEN_QT1=2s, T_GRID_STABLE=120s)

---

## 🎯 Próximos Diagramas Sugeridos

| Diagrama | Tipo | Prioridad | Descripción |
|----------|------|-----------|-------------|
| **15_UML_CMD_ARBITER_Logic** | Activity | Media | Lógica arbitraje prioridad SCMTA>SHED>MANUAL |
| **16_UML_System_Architecture** | Component | Alta | Arquitectura completa: FBs + I/O + Modbus + HMI |
| **17_UML_Deployment_Topology** | Deployment | Baja | Topología física: PLC + MTZ + GD + RED |
| **18_UML_Sequence_Transfer** | Sequence | Media | Secuencia temporal transferencia RED→GD |

---

## 📝 Convenciones de Diagrama

### Colores Estados (futuro)
```plantuml
state NORMAL #lightgreen : Operación normal
state FAULT #red : Estado falla
state TRANSFER #yellow : En transferencia
state INIT #lightblue : Inicialización
```

### Iconos Estado (actual)
```
✓  Operación normal (NORMAL_ON_GRID, ON_GD)
⚠  Falla/alarma (FAULT_LOCKOUT)
🔄 Failover/transferencia (SWITCH_GD1_TO_GD2)
```

### Transiciones
- **Línea sólida:** Transición normal
- **Línea punteada:** Transición error/timeout (futuro)
- **Texto transición:** Condición trigger

---

## 📚 Referencias

**PlantUML Cheat Sheet:**  
https://plantuml.com/state-diagram

**Proyecto TGBT:**
- Código SCL: `TGBT/01_SCL/`
- Documentación: `TGBT/03_DOCS/`
- Test: `TGBT/07_TEST/`

**Estado implementación completo:**  
Ver `TGBT/03_DOCS/PRESENTACION_REUNION_2026-02-10.md`

---

**Última actualización:** 10 de Febrero 2026  
**Autor:** GitHub Copilot AI
