# PROYECTO SCMTA - TGBT LADDER

## 📁 Estructura del Proyecto

Sistema de Control y Monitoreo de Transferencia Automática (SCMTA) para Tablero General de Baja Tensión.

---

## 📂 Organización de Carpetas

```
tgbt_ladder/
│
├── 01_SCL/                          ← Código fuente SCL (TIA Portal)
│   ├── 01_FB_IO_NORMALIZE.scl       → Normalización entradas físicas
│   ├── 02_FB_SCMTA.scl              → Máquina estados transferencia automática
│   ├── 03_FB_SHED.scl               → Deslastre y reenganche cargas
│   ├── 04_FB_CMD_ARBITER.scl        → Árbitro comandos con interlock
│   ├── 05_FB_OUTPUTS.scl            → Gestión pilotos y alarmas
│   ├── 06_FB_MODBUS_MANAGER.scl     → Scheduler Modbus RTU
│   ├── 07_FB_MTZ_DRIVER.scl         → Driver Schneider Command Interface
│   ├── 08_DB_GLOBAL_STATUS.scl      → Data Block estados (NON_RETAIN)
│   ├── 09_DB_PARAMS.scl             → Data Block parámetros (RETAIN)
│   └── 10_OB1_MAIN.scl              → Main cíclico (orquestación)
│
├── 02_LADDER/                       ← Conversiones LADDER (referencia)
│   ├── 01_FB_IO_NORMALIZE_LADDER.md → Documentación LADDER IO_NORMALIZE
│   ├── LADDER_01_FB_IO_NORMALIZE.md → Conversión completa LADDER
│   ├── LADDER_05_FB_OUTPUTS.md      → Conversión FB_OUTPUTS (mixto recomendado)
│   └── LADDER_10_OB1_MAIN.md        → OB1 en LADDER (visual)
│
├── 03_DOCS/                         ← Documentación técnica
│   ├── README_SCMTA.md              → Documentación completa sistema (25 págs)
│   ├── INDEX.md                     → Índice archivos proyecto
│   ├── VALIDACION_SCL_TIA_V18.md    → Validación código SCL (100% compatible)
│   ├── GUIA_COMPLETA_SCL_LADDER.md  → Comparación SCL vs LADDER + decisiones
│   └── CAMBIOS_REQ_2_SEGUNDOS.md    → Modificación REQ Modbus 2 segundos
│
├── 04_UML/                          ← Diagramas PlantUML
│   ├── 11_UML_SCMTA_StateMachine.puml    → Diagrama estados SCMTA (15 estados)
│   ├── 12_UML_MTZ_Driver_StateMachine.puml → Diagrama estados Driver Modbus
│   └── 13_UML_SHED_Activity.puml         → Diagrama actividad deslastre
│
├── 05_MANUALES/                     ← Manuales técnicos equipos
│   ├── 81318674_Programming_guideline_DOC_v16_en.pdf → Guía programación
│   ├── s71200_system_manual_en-US_en-US.pdf → Manual S7-1200
│   ├── s7_1500_compare_table_en_mnemo.pdf → Comparación S7-1500
│   ├── Escritura_MTZ.pdf            → Procedimiento escritura MTZ
│   ├── masterpact mtz1 y mtz2.pdf   → Especificaciones MTZ
│   ├── MTZ MANUAL.pdf               → Manual Masterpact MTZ
│   └── NSX MANUAL.pdf               → Manual Compact NSX
│
└── 06_CONFIG/                       ← Configuración TGBT
    ├── ET MONTAJE-TGBT.pdf          → Esquema montaje tablero
    ├── TGBT_Config - listado de entradas y salidas.pdf → Mapeo I/O
    ├── TGBT_Config - listado de equipos.pdf → Lista equipos
    └── TGBT_Config - pm5330.pdf     → Configuración PM5350
```

---

## 🎯 Inicio Rápido

### **1. Revisar Documentación Principal**
📖 [03_DOCS/README_SCMTA.md](03_DOCS/README_SCMTA.md) - Documentación completa del sistema (25 páginas)

### **2. Validación Código**
✅ [03_DOCS/VALIDACION_SCL_TIA_V18.md](03_DOCS/VALIDACION_SCL_TIA_V18.md) - Código SCL 100% compatible TIA Portal V18

### **3. Decisión SCL vs LADDER**
📊 [03_DOCS/GUIA_COMPLETA_SCL_LADDER.md](03_DOCS/GUIA_COMPLETA_SCL_LADDER.md) - Comparación técnica y recomendaciones

### **4. Importar a TIA Portal**
```
1. Abrir TIA Portal V18
2. Crear proyecto nuevo
3. Agregar S7-1200 (CPU 1214C o superior)
4. Importar archivos de carpeta 01_SCL/
5. Compilar proyecto
6. Mapear direcciones físicas según 06_CONFIG/
```

---

## 📊 Tecnologías y Equipos

| Componente | Modelo | Protocolo |
|------------|--------|-----------|
| **PLC** | Siemens S7-1200 | - |
| **Interruptores Principales** | Schneider Masterpact MTZ1/MTZ2 | Modbus RTU |
| **Interruptores Generador** | Schneider Compact NSX Micrologic | Modbus RTU |
| **Medidores RED** | Schneider PowerLogic PM5350 | Modbus RTU |
| **Comunicación** | RS485 Modbus RTU 19200 baud | - |

---

## 🔧 Características Principales

### **Sistema SCMTA**
- ✅ Transferencia automática Red ↔ Grupo Diésel
- ✅ Máquina estados 15 estados con timeouts
- ✅ Detección falla red (tensión + frecuencia + fase)
- ✅ Retorno automático con estabilidad 120s
- ✅ Control marcha/parada GD
- ✅ Interlock fail-safe fuente única

### **Deslastre de Cargas**
- ✅ 18 feeders configurables
- ✅ Prioridad configurable (SHED_ORDER[1..18])
- ✅ Deslastre automático por sobrecarga GD/TR
- ✅ Reenganche escalonado automático

### **Comunicación Modbus RTU**
- ✅ Protocolo Schneider Command Interface
- ✅ Escritura comandos (registros 8000-8019)
- ✅ Lectura estados (registros 8020-8021, 32000-32001)
- ✅ REQ activo 2 segundos (compatible hardware)
- ✅ Scheduler multi-dispositivo

### **Seguridad**
- ✅ Enclavamiento absoluto (solo 1 fuente cerrada)
- ✅ Árbitro prioridad: SCMTA > SHED > MANUAL
- ✅ Permisos Local/Remoto por selector físico
- ✅ Fail-safe: falla → modo MANUAL
- ✅ Alarmas con ACK y lockout

---

## 🚀 Recomendación de Implementación

### **Opción 1: Proyecto 100% SCL** ⭐⭐⭐⭐⭐ RECOMENDADO

**Usar archivos de carpeta `01_SCL/` directamente**

**Ventajas**:
- ✅ Código validado y listo
- ✅ Óptimo para lógica compleja (máquinas estado, arrays, protocolos)
- ✅ Menor esfuerzo implementación
- ✅ Más mantenible largo plazo

**Importar en orden**:
```
1. 08_DB_GLOBAL_STATUS.scl
2. 09_DB_PARAMS.scl
3. 01_FB_IO_NORMALIZE.scl
4. 02_FB_SCMTA.scl
5. 03_FB_SHED.scl
6. 04_FB_CMD_ARBITER.scl
7. 05_FB_OUTPUTS.scl
8. 06_FB_MODBUS_MANAGER.scl
9. 07_FB_MTZ_DRIVER.scl
10. 10_OB1_MAIN.scl
```

### **Opción 2: Proyecto Híbrido SCL+LADDER** ⭐⭐⭐⭐

**Combinar según preferencia equipo**

**Usar LADDER para**:
- OB1_MAIN (ver `02_LADDER/LADDER_10_OB1_MAIN.md`)
- FB_IO_NORMALIZE (ver `02_LADDER/LADDER_01_FB_IO_NORMALIZE.md`)
- FB_OUTPUTS pilotos (ver `02_LADDER/LADDER_05_FB_OUTPUTS.md`)

**Mantener SCL para**:
- FB_SCMTA (máquina estados compleja)
- FB_SHED (arrays y loops)
- FB_CMD_ARBITER (árbitro complejo)
- Drivers Modbus (protocolo complejo)

---

## 📖 Documentación por Tema

### **Para Programadores**
1. [VALIDACION_SCL_TIA_V18.md](03_DOCS/VALIDACION_SCL_TIA_V18.md) - Validación código
2. [GUIA_COMPLETA_SCL_LADDER.md](03_DOCS/GUIA_COMPLETA_SCL_LADDER.md) - SCL vs LADDER
3. [README_SCMTA.md](03_DOCS/README_SCMTA.md) - Arquitectura completa

### **Para Diseño**
1. Diagramas UML en carpeta `04_UML/`
2. [README_SCMTA.md](03_DOCS/README_SCMTA.md) - Sección "Arquitectura"

### **Para Instalación**
1. `06_CONFIG/ET MONTAJE-TGBT.pdf` - Esquema montaje
2. `06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf` - Mapeo I/O
3. `06_CONFIG/TGBT_Config - listado de equipos.pdf` - Lista equipos

### **Para Configuración Modbus**
1. [CAMBIOS_REQ_2_SEGUNDOS.md](03_DOCS/CAMBIOS_REQ_2_SEGUNDOS.md) - REQ Modbus 2s
2. `05_MANUALES/Escritura_MTZ.pdf` - Procedimiento escritura MTZ
3. `05_MANUALES/MTZ MANUAL.pdf` - Protocolo Schneider

---

## ⚙️ Parámetros Configurables

**Archivo**: `01_SCL/09_DB_PARAMS.scl`

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| V_NOM | 380V | Tensión nominal L-L |
| V_MIN_PCT | 85% | Umbral subtensión |
| FREQ_NOM | 50Hz | Frecuencia nominal |
| T_GRID_STABLE | 120s | Estabilidad red antes retorno |
| T_GD_COOLDOWN | 60s | Cooldown antes parar GD |
| SHED_ON_PCT | 90% | Umbral activación deslastre |
| RECONNECT_PCT | 70% | Umbral reenganche cargas |
| SHED_ORDER[1..18] | [1,2,3...18] | Prioridad deslastre |

---

## 🔍 Mapeo Direcciones Físicas

**Referencia**: `06_CONFIG/TGBT_Config - listado de entradas y salidas.pdf`

Ajustar en `01_SCL/10_OB1_MAIN.scl`:

```scl
// Ejemplo (verificar con listado real):
DI_SYS_AUTO := %I0.0,           // Selector Auto/Manual
DI_QT1_REMOTE_SEL := %I0.1,     // QT1 Local/Remoto
DO_GD_START => %Q0.0,           // Marcha GD
DO_PILOT_ON_GRID => %Q1.0,      // LED verde "EN RED"
// ... resto mapeo según configuración
```

---

## 📞 Soporte y Contacto

**Proyecto**: Sistema SCMTA TGBT  
**Fecha**: 4 de febrero de 2026  
**Versión**: 1.0  
**TIA Portal**: V18  
**PLC**: Siemens S7-1200

---

## 📝 Estado del Proyecto

| Etapa | Estado | Fecha |
|-------|--------|-------|
| Análisis y diseño | ✅ Completado | 04/02/2026 |
| Desarrollo código SCL | ✅ Completado | 04/02/2026 |
| Validación TIA Portal V18 | ✅ Completado | 04/02/2026 |
| Conversión LADDER (ref.) | ✅ Completado | 04/02/2026 |
| Documentación | ✅ Completado | 04/02/2026 |
| Importación TIA Portal | ⏳ Pendiente | - |
| Mapeo I/O físico | ⏳ Pendiente | - |
| Testing en banco | ⏳ Pendiente | - |
| Comisionamiento | ⏳ Pendiente | - |

---

## ✅ Próximos Pasos

1. ✅ **Decidir estrategia**: SCL puro (recomendado) o Híbrida
2. ✅ **Importar archivos** `01_SCL/` a TIA Portal V18
3. ✅ **Mapear direcciones** físicas %I/%Q según `06_CONFIG/`
4. ✅ **Compilar** proyecto sin errores
5. ✅ **Crear DB instances** para cada FB
6. ✅ **Configurar Modbus** RTU (19200 baud, parity=2)
7. ✅ **Testear** en banco antes de campo
8. ✅ **Ajustar parámetros** según pruebas

---

## 🎓 Recursos Adicionales

- **TIA Portal Help**: F1 en TIA Portal V18
- **S7-1200 Manual**: `05_MANUALES/s71200_system_manual_en-US_en-US.pdf`
- **Programming Guide**: `05_MANUALES/81318674_Programming_guideline_DOC_v16_en.pdf`
- **Schneider MTZ**: `05_MANUALES/MTZ MANUAL.pdf`
- **Schneider NSX**: `05_MANUALES/NSX MANUAL.pdf`

---

**¡Proyecto listo para implementación en TIA Portal V18!** 🚀
