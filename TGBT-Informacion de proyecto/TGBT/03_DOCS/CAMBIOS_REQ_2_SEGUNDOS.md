# MODIFICACIÓN: REQ Modbus Activo por 2 Segundos

## 📝 CAMBIOS REALIZADOS

Se ha modificado el proyecto SCMTA para que **REQ del Modbus Master se mantenga activo por 2 segundos** en lugar de ser un pulso de 1 scan, según requerimiento del hardware.

---

## 🔧 ARCHIVOS MODIFICADOS

### 1. **FB_MODBUS_MANAGER** (`06_FB_MODBUS_MANAGER.scl`)

**Cambios:**
- ✅ Agregada variable `tonReqActive : TON` (timer 2 segundos)
- ✅ Agregada variable `reqModbusActive : Bool` (REQ para Modbus Master)
- ✅ Lógica modificada para activar REQ por 2 segundos en cada ciclo de polling

**Funcionamiento:**
```
tonPollCycle (1s) → Q=1 → Activar reqModbusActive=TRUE
                                    ↓
                          tonReqActive (2s) → Mantener activo
                                    ↓
                          Al cumplirse 2s → reqModbusActive=FALSE
```

### 2. **FB_MTZ_DRIVER** (`07_FB_MTZ_DRIVER.scl`)

**Cambios:**
- ✅ Agregada variable `tonReqWrite : TON` (timer 2 segundos)
- ✅ Agregada variable `reqWriteActive : Bool` (REQ escritura comandos)
- ✅ Estado WRITE_CMD modificado para mantener REQ activo 2 segundos

**Funcionamiento en escritura comandos (8000-8019):**
```
BUILD_BUFFER → WRITE_CMD → reqWriteActive=TRUE por 2s
                                    ↓
                          Después de 2s → POLL_RESPONSE
```

---

## 🎯 CÓMO USAR EN TU CÓDIGO EXISTENTE

### **Para Lectura Modbus (Polling Cíclico)**

En tu **Main [OB1]**, conectar así:

```scl
// Network: Modbus Manager
"DB_MODBUS_MGR"(
    ENABLE := TRUE,
    T_POLL_CYCLE := T#3s,  // Cada 3 segundos (1s polling + 2s REQ activo)
    
    // Outputs
    // (ninguno por ahora, es gestor interno)
);

// Network: MB_MASTER para lectura registros
"MB_MASTER"(
    REQ := "DB_MODBUS_MGR".reqModbusActive,  // ← Conectar aquí (2s activo)
    MB_MODE := 0,  // FC3 Read Holding Registers
    ADDR := 43000,
    LEN := 120,
    // ... resto configuración
);
```

### **Para Escritura Comandos (MTZ/NSX)**

En llamada al driver MTZ:

```scl
// Network: Driver QT1
"DB_QT1_DRV"(
    ENABLE := TRUE,
    CMD_OPEN := "DB_ARBITER".CMD_OPEN_QT1,
    CMD_CLOSE := "DB_ARBITER".CMD_CLOSE_QT1,
    // ... resto parámetros
    
    CB_STATE => "DB_GLOBAL_STATUS".QT1_STATE
);

// Network: MB_CLIENT para escritura comandos
IF "DB_QT1_DRV".STATE = 2 THEN  // Estado WRITE_CMD
    "MB_CLIENT_QT1"(
        REQ := "DB_QT1_DRV".reqWriteActive,  // ← REQ activo 2s
        MB_MODE := 1,  // FC16 Write Multiple Registers
        ADDR := 8000,
        LEN := 20,
        DATA := "DB_QT1_DRV".cmdBuffer
    );
END_IF;
```

---

## ⏱️ DIAGRAMA TEMPORAL (REQ 2 Segundos)

```
Ciclo PLC:     |---|---|---|---|---|---|---|---|---|---|
Polling (3s):  0.......................3000ms...........
REQ:           _____██████████████████_________________
               ↑                      ↑
            Activo 2000ms        Desactiva

BUSY:          ______████████████████__________________
DONE:          ______________________█_________________
                                     ↑
                                Lectura OK
```

**Timing:**
- **T_POLL_CYCLE = T#3s**: Espera entre lecturas
- **REQ activo = T#2s**: Duración REQ (como requiere tu hardware)
- **Pausa = 1s**: Entre fin REQ y próximo ciclo

---

## 🔍 VENTAJAS DE ESTA IMPLEMENTACIÓN

1. ✅ **REQ activo 2 segundos** (compatible con tu hardware Modbus)
2. ✅ **No satura el bus** (ciclo de 3 segundos entre lecturas)
3. ✅ **Permite verificar DONE/ERROR** correctamente
4. ✅ **Arquitectura modular** (fácil ajustar tiempos)
5. ✅ **Compatible con múltiples dispositivos** (scheduler distribuye tiempo)

---

## ⚙️ PARÁMETROS AJUSTABLES

### En FB_MODBUS_MANAGER:
```scl
T_POLL_CYCLE := T#3s;   // Ajustar según velocidad deseada
                        // Mínimo recomendado: T#2.5s (2s REQ + 0.5s margen)
```

### En FB_MTZ_DRIVER (estado WRITE_CMD):
```scl
tonReqWrite(PT := T#2s);  // Duración REQ escritura
                          // Ajustar si tu hardware necesita más/menos tiempo
```

---

## 📊 COMPARACIÓN: ANTES vs DESPUÉS

| Aspecto | ANTES (Pulso 1 scan) | DESPUÉS (REQ 2s activo) |
|---------|----------------------|-------------------------|
| REQ duración | 1 ciclo PLC (~100ms) | 2000 ms |
| Compatibilidad HW | ❌ No funciona tu Modbus | ✅ Funciona correctamente |
| Saturación bus | ⚠️ Media (si ciclo muy rápido) | ✅ Baja (ciclo 3s) |
| Verificación DONE | ✅ Posible | ✅ Posible |
| Uso CPU PLC | ✅ Bajo | ✅ Bajo |

---

## 🚀 PRÓXIMOS PASOS

1. **Importar archivos modificados** a TIA Portal
2. **Conectar `reqModbusActive`** a entrada REQ de tu MB_MASTER
3. **Ajustar `T_POLL_CYCLE`** según necesidades (mínimo T#2.5s)
4. **Testear** con un dispositivo Modbus
5. **Verificar** que DONE se activa correctamente después de 2s

---

## 📝 NOTAS IMPORTANTES

- **T_POLL_CYCLE debe ser > 2s**: Para que REQ tenga tiempo de completarse
- **Recomendado T#3s**: Da margen de 1s entre fin REQ y próximo ciclo
- **Si necesitas más velocidad**: Reducir a T#2.5s (mínimo seguro)
- **Para múltiples lecturas**: FB_MODBUS_MANAGER distribuye tiempo entre dispositivos

---

¿Necesitas que ajuste algún timing específico o que agregue más lógica de reintentos en caso de ERROR?