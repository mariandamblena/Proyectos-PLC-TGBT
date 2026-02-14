# CORRECCIONES APLICADAS AL OB1_MAIN

**Fecha:** 2026-02-14  
**Versión:** 3.0 Corregida  
**Estado:** LISTO PARA IMPORTAR

---

## PROBLEMA DETECTADO

El archivo `10_OB1_MAIN.scl` tenía nombres de DBs **genéricos** que NO coincidían con los nombres reales del proyecto TIA Portal.

### Nombres incorrectos (antes):
- `"DB_IO"` ❌
- `"DB_SCMTA"` ❌
- `"DB_SHED"` ❌
- `"DB_ARBITER"` ❌
- `"DB_OUTPUTS"` ❌
- `"DB_GLOBAL_STATUS"` ❌ (no existía en el proyecto)
- `"DB_QT1_DRV"`, `"DB_QG1_DRV"`, `"DB_QG2_DRV"` ❌

---

## SOLUCIÓN APLICADA

### ✅ Nombres corregidos (ahora):

| FB llamado en OB1 | Instance DB generado automáticamente |
|---|---|
| `"01_FB_IO_NORMALIZE_DB"` | Se crea automático al compilar |
| `"02_FB_SCMTA_DB"` | Se crea automático al compilar |
| `"03_FB_SHED_DB"` | Se crea automático al compilar |
| `"04_FB_CMD_ARBITER_DB"` | Se crea automático al compilar |
| `"05_FB_OUTPUTS_DB"` | Se crea automático al compilar |
| `"07_FB_MTZ_DRIVER_DB_QT1"` | Se crea automático al compilar |
| `"07_FB_MTZ_DRIVER_DB_QG1"` | Se crea automático al compilar |
| `"07_FB_MTZ_DRIVER_DB_QG2"` | Se crea automático al compilar |

### ✅ Global DBs:

| DB Global | Descripción | Tipo |
|---|---|---|
| **`DATA_BUFF`** | Estado actual de TODO el sistema (antes llamado DB_GLOBAL_STATUS) | NON_RETAIN |
| **`DB_PARAMS`** | Parámetros configurables del sistema | RETAIN |

> **IMPORTANTE:** Según tu proyecto, ya tenés `DATA_BUFF [DB23]`. Si querés usar el nombre `DB_GLOBAL_STATUS` en vez de `DATA_BUFF`, tenés que renombrarlo en TIA Portal o hacer un último reemplazo masivo en el OB1.

---

## PASOS PARA IMPLEMENTAR EN TIA PORTAL

### 1️⃣ **Crear/Verificar los Global DBs**

#### Opción A: Usar DATA_BUFF existente
- Ya tenés `DATA_BUFF [DB23]` en tu proyecto
- Verificá que tenga la estructura de `08_DB_GLOBAL_STATUS.scl`
- Si no tiene la estructura correcta:
  1. Eliminá `DATA_BUFF` del proyecto
  2. Importá `08_DB_GLOBAL_STATUS.scl` como Global DB
  3. Renombralo a `DATA_BUFF` en TIA Portal

#### Opción B: Crear DB_GLOBAL_STATUS nuevo
1. Importá `08_DB_GLOBAL_STATUS.scl` como Global DB
2. Se creará como `DB_GLOBAL_STATUS`
3. Modificá el OB1 reemplazando todas las referencias `"DATA_BUFF"` por `"DB_GLOBAL_STATUS"`

#### Crear DB_PARAMS:
1. Click derecho en **Program blocks** → **Add new block** → **Data block**
2. Tipo: **Global DB**
3. Nombre: **`DB_PARAMS`**
4. ✅ Marcar: **Optimized block access**
5. ✅ Marcar: **RETAIN** (crítico para que mantenga valores después de reset)
6. Copiar/pegar la estructura de `09_DB_PARAMS.scl` o importar el archivo

---

### 2️⃣ **Verificar que existan todos los FBs**

Asegurate de tener estos FBs creados (ya los tenés según la imagen):

- `01_FB_IO_NORMALIZE` [FB1] ✅
- `02_FB_SCMTA` [FB2] ✅
- `03_FB_SHED` [FB3] ✅
- `04_FB_CMD_ARBITER` [FB5] ✅
- `05_FB_OUTPUTS` [FB6] ✅
- `06_FB_MODBUS_MANAGER` [FB7] (no se llama en OB1 todavía)
- `07_FB_MTZ_DRIVER` [FB8] ✅

---

### 3️⃣ **Importar/Reemplazar el OB1 corregido**

1. **Backup del OB1 actual:**
   - Click derecho en `Main [OB1]` → **Export**
   - Guardá como `Main_OB1_BACKUP_2026-02-14.scl`

2. **Importar el OB1 corregido:**
   - Click derecho en **Program blocks** → **External source** → **Generate blocks from source**
   - Seleccioná `10_OB1_MAIN.scl` (el archivo corregido)
   - TIA Portal generará automáticamente los **Instance DBs** que faltan:
     - `01_FB_IO_NORMALIZE_DB` [DBx]
     - `02_FB_SCMTA_DB` [DBx]
     - `03_FB_SHED_DB` [DBx]
     - `04_FB_CMD_ARBITER_DB` [DBx]
     - `05_FB_OUTPUTS_DB` [DBx]
     - `07_FB_MTZ_DRIVER_DB_QT1` [DBx]
     - `07_FB_MTZ_DRIVER_DB_QG1` [DBx]
     - `07_FB_MTZ_DRIVER_DB_QG2` [DBx]

3. **Si hay conflictos:**
   - TIA Portal puede decirte que el OB1 ya existe
   - Podés:
     - Sobreescribirlo (recomendado, si hiciste backup)
     - Importarlo con otro nombre temporal y después comparar

---

### 4️⃣ **Compilar el proyecto**

1. Click derecho en **PLC_1 [CPU 1215C]** → **Compile** → **Software (rebuild all)**
2. Revisá errores en la ventana **Info → Compile**
3. Errores comunes esperados:
   - ❌ **"DB_PARAMS no tiene el campo X"**: Falta agregar esa variable en DB_PARAMS
   - ❌ **"DATA_BUFF no tiene el campo Y"**: Falta agregar esa variable en DATA_BUFF
   - ❌ **"FB_X no tiene el VAR_INPUT Z"**: El FB no tiene esa interfaz definida

---

### 5️⃣ **Mapear entradas/salidas físicas (TODO)**

El OB1 tiene ejemplos con direcciones absolutas tipo `%I0.0`, `%Q0.0`. Tenés que:
1. Revisar tu configuración de hardware (Device configuration)
2. Actualizar todas las referencias `%Ix.y` y `%Qx.y` según tu tablero físico
3. Alternativa: crear variables globales en **PLC tags** con nombres descriptivos

---

## ARQUITECTURA FINAL DEL FLUJO DE DATOS

```
┌─────────────────────────────────────────────────────────────────┐
│                         OB1 (Main)                              │
│                         Ciclo: 100-200ms                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                            │                            │
    ▼                            ▼                            ▼
DB_PARAMS                   DATA_BUFF                    Instance DBs
(Parámetros)               (Estado global)         (Memoria interna FBs)
RETAIN                      NON_RETAIN
                                 │
    ├───────────────────────────┼───────────────────────────┤
    │                           │                           │
    ▼                           ▼                           ▼
Network 1:              Network 2:                  Network 3:
FB_IO_NORMALIZE         FB_SCMTA                    FB_SHED
    │                           │                           │
    │     escribe      ┌────────┴────────┐   escribe      │
    └─────────────────►│   DATA_BUFF     │◄───────────────┘
                       │  (pizarrón      │
Network 4:             │   compartido)   │          Network 5:
FB_CMD_ARBITER────────►│                 │◄─────────FB_OUTPUTS
    │                  └────────┬────────┘                 │
    │ lee                       │ lee                      │
    │                           │                          │
    ▼                           ▼                          ▼
Network 6:              HMI LEE TODO            DO físicas
Drivers MTZ         de DATA_BUFF             (pilotos, alarmas)
(QT1, QG1, QG2)      y DB_PARAMS
```

---

## CAMBIOS CRÍTICOS REALIZADOS

### 1. Renombrado de Instance DBs:
**Antes:** `"DB_IO"`, `"DB_SCMTA"`, etc.  
**Ahora:** `"01_FB_IO_NORMALIZE_DB"`, `"02_FB_SCMTA_DB"`, etc.  
**Por qué:** Para coincidir con los nombres reales generados por TIA Portal

### 2. DB_GLOBAL_STATUS → DATA_BUFF:
**Antes:** `"DB_GLOBAL_STATUS".MODE_AUTO`  
**Ahora:** `"DATA_BUFF".MODE_AUTO`  
**Por qué:** En tu proyecto ya existe `DATA_BUFF [DB23]`

### 3. Instance DBs de drivers MTZ:
**Antes:** `"DB_QT1_DRV"`, `"DB_QG1_DRV"`, `"DB_QG2_DRV"`  
**Ahora:** `"07_FB_MTZ_DRIVER_DB_QT1"`, `"07_FB_MTZ_DRIVER_DB_QG1"`, `"07_FB_MTZ_DRIVER_DB_QG2"`  
**Por qué:** Nomenclatura consistente con el resto del proyecto

---

## VERIFICACIÓN POST-COMPILACIÓN

1. ✅ **Sin errores de compilación**
2. ✅ **DATA_BUFF contiene todas las variables usadas en OB1**
3. ✅ **DB_PARAMS contiene todos los parámetros referenciados**
4. ✅ **Los 8 Instance DBs se crearon automáticamente**
5. ✅ **HMI puede leer/escribir en DATA_BUFF y DB_PARAMS**

---

## PARA EL HMI

**Todas las variables para el HMI ahora se leen/escriben desde:**
- **`DATA_BUFF`** (antes DB_GLOBAL_STATUS) → Estados, mediciones, alarmas (solo lectura)
- **`DB_PARAMS`** → Parámetros configurables (lectura/escritura nivel ADMIN)

**Ejemplo:**
```
Tensión Red L1-L2:  "DATA_BUFF".GRID_V_L1L2
Modo AUTO:          "DATA_BUFF".MODE_AUTO
Umbral deslastre:   "DB_PARAMS".GD_SHED_ON
```

---

## PREGUNTAS FRECUENTES

### ¿Por qué ahora se llama DATA_BUFF y no DB_GLOBAL_STATUS?
Porque en tu proyecto TIA Portal ya existe `DATA_BUFF [DB23]`. Podés renombrarlo en TIA Portal o hacer un reemplazo masivo en el OB1.

### ¿Los Instance DBs se crean automáticamente?
Sí. Al compilar el OB1, TIA Portal detecta los FBs llamados y crea sus Instance DBs automáticamente con los nombres que pusiste entre comillas.

### ¿Qué pasa con los DBs viejos (DB2, DB4, DB6, DB8, etc.)?
Si tienen nombres distintos a los del OB1 corregido, quedarán huérfanos y podés borrarlos. TIA Portal creará los nuevos con los nombres correctos.

### ¿El HMI se rompe con este cambio?
Solo si el HMI ya estaba conectado a variables del PLC. Tendrás que actualizar las referencias en las pantallas HMI:
- Buscar: `"DB_GLOBAL_STATUS"` → Reemplazar: `"DATA_BUFF"`

---

## PRÓXIMOS PASOS (TODO)

1. ⬜ Mapear todas las DI físicas (`%I0.0`, `%I0.1`, etc.) según hardware real
2. ⬜ Mapear todas las DO físicas (`%Q0.0`, `%Q1.0`, etc.) según hardware real
3. ⬜ Configurar direcciones Modbus Slave ID reales en `DB_PARAMS`
4. ⬜ Configurar arrays `FEEDER_ESSENTIAL[1..18]` según cargas críticas
5. ⬜ Configurar arrays `SHED_ORDER[1..18]` según prioridades reales
6. ⬜ Implementar FB_MODBUS_MANAGER (polling PM5350, drivers NSX)
7. ⬜ Testear secuencia completa en simulación
8. ⬜ Crear las 6 pantallas HMI según documento de variables

---

**Autor:** GitHub Copilot  
**Archivo corregido:** `10_OB1_MAIN.scl` (3.0 Corregida)  
**Fecha corrección:** 2026-02-14
