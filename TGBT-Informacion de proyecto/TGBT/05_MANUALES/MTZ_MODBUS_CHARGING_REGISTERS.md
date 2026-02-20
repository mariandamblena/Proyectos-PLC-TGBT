# MTZ Modbus Register Information: Charging / Spring / Ready to Close

## Source PDFs Analyzed
1. **MTZ MANUAL.pdf** (Schneider DOCA0105ES-10 - MasterPact MTZ Comunicación Modbus) - 304 pages
2. **Escritura_MTZ.pdf** (Internal project document - Registros a escribir MTZ) - 6 pages

---

## 1. REGISTER 32001 — Estado del interruptor automático (Breaker Status)

**Address:** 0x7D00  
**Type:** INT16U (Read-only)  
**Calidad (Quality):** Registro 32000 (bit-by-bit quality flags for each bit in 32001)

### Complete Bit Map of Register 32001:

| Bit | Signal | Description | Values |
|-----|--------|-------------|--------|
| **0** | **OF** (Contacto de indicación de estado) | Posición del interruptor | **0** = Abierto, **1** = Cerrado (válido solo si 32000.bit0=1) |
| **1** | **SD** (Contacto de indicación de disparo) | Disparo por problema eléctrico | **0** = No disparado, **1** = Disparado (por falla eléctrica, shunt trip, o pulsar-para-disparo). Siempre 0 en MasterPact/ComPacT NS con mando eléctrico |
| **2** | **SDE** (Contacto de indicación de disparo incorrecto) | Disparo por problema eléctrico específico | **0** = No disparado por problema eléctrico, **1** = Disparado por problema eléctrico (incluye prueba de defecto a tierra y prueba diferencial) |
| **3** | **CH** (Contacto de resorte cargado) | **RESORTE / SPRING CHARGING** — Solo MasterPact | **0** = Resorte descargado (spring NOT charged), **1** = Resorte cargado (spring charged). Siempre 0 en MasterPact/ComPacT NS con mando eléctrico |
| **4** | — | Reservado | — |
| **5** | **PF** (Contacto PF preparado para cerrarse) | **READY TO CLOSE** — Solo MasterPact | **0** = No preparado para cerrarse (NOT ready to close), **1** = Preparado para cerrarse (ready to close). Siempre 0 en MasterPact/ComPacT NS con mando eléctrico |
| **6-14** | — | Reservado | — |
| **15** | — | Disponibilidad de los datos | Si = 1, todos los demás bits del registro NO son significativos |

### Quality Register 32000 (Calidad de cada bit de 32001):
- bit N of 32000 = calidad del bit N de 32001
- **0** = Dato no válido
- **1** = Dato válido

### Reading Logic:
| Condition | Meaning |
|-----------|---------|
| 32000.bit0 = 1 AND 32001.bit0 = 0 | Breaker **ABIERTO** |
| 32000.bit0 = 1 AND 32001.bit0 = 1 | Breaker **CERRADO** |
| 32000.bit0 = 0 | Indicación OF **NO VÁLIDA** |
| 32001.bit3 = 1 | **Resorte CARGADO** (Spring Charged) |
| 32001.bit3 = 0 | **Resorte DESCARGADO** (Spring NOT Charged) |
| 32001.bit5 = 1 | **LISTO para cerrar** (Ready to Close - muelle cargado, sin bloqueos) |
| 32001.bit5 = 0 | **NO listo para cerrar** |

---

## 2. REGISTER 32341 — Orden de bloqueo de cierre (Close Inhibit Status)

**Address:** 0x7E54  
**Type:** INT16U (Read-only)  
**Quality:** Register 32340

| Bit | Description | Values |
|-----|-------------|--------|
| **0** | Cierre de interruptor inhibido por el módulo IO | 0 = Deshabilitado, 1 = Habilitado (inhibido) |
| **1** | Cierre de interruptor inhibido por comunicación | 0 = Deshabilitado, 1 = Habilitado (inhibido) |
| **2-15** | Reservado | — |

> **Nota:** Ambos bits (0 y 1) deben estar en 0 para permitir cierre remoto.

---

## 3. COMMAND REGISTERS (8000–8021) — Apertura/Cierre

### Command Structure (registers 8000–8019):

| Register (dec) | Address (hex) | Value | Description |
|----------------|---------------|-------|-------------|
| **8000** | 0x1F3F | **904** (Abrir) / **905** (Cerrar) / **906** (Reset) | Código de comando |
| **8001** | 0x1F40 | **10** | Longitud de parámetros (bytes) |
| **8002** | 0x1F41 | **5377** (0x1501) | Destino del comando |
| **8003** | 0x1F42 | **1** | Tipo de seguridad (1 = con contraseña) |
| **8004** | 0x1F43 | ASCII password (2 chars) | Contraseña (2 MSB chars) — default L3: "33" → 0x3333 |
| **8005** | 0x1F44 | ASCII password (2 chars) | Contraseña (2 LSB chars) — default L3: "33" → 0x3333 |
| **8006–8015** | 0x1F45–0x1F4E | **0** | Parámetros adicionales (0 para abrir/cerrar) |
| **8016** | 0x1F4F | **0** | Reservado |
| **8017** | 0x1F50 | **8019** | Reservado (constante) |
| **8018** | 0x1F51 | **8020** | Reservado (constante) |
| **8019** | 0x1F52 | **8021** | Reservado (constante) |

### Command Response:

| Register | Description |
|----------|-------------|
| **8020** | Eco del código de comando (debe coincidir con 8000) |
| **8021** | Estado del comando: **0x0003** = en proceso; **LSB = 0** = éxito; **LSB ≠ 0** = error |

### Command Error Codes (8021 LSB):

| Code | Meaning |
|------|---------|
| 0x00 | Éxito |
| 0x01 | Contraseña incorrecta (derechos insuficientes) |
| 0x02 | Violación de acceso (candado cerrado) |
| 0x98 (152) | Breaker ya estaba cerrado |
| 0x99 (153) | Breaker ya estaba abierto |
| 0x9B (155) | Actuador en modo manual, comando rechazado |

### Command Codes:

| Code | Action |
|------|--------|
| **904** | Abrir interruptor (Trip/Open) |
| **905** | Cerrar interruptor (Close) |
| **906** | Reset (liberar mecanismo de disparo) |
| **910** | Inhibir cierre |

---

## 4. KEY FINDINGS: Charging / Spring / Ready Signals

### From MTZ MANUAL.pdf (Page 79):
- **Bit 3 of Register 32001** = **"Contacto de resorte CH cargado (sólo con MasterPact)"**
  - 0 = Resorte descargado (Spring NOT charged)  
  - 1 = Resorte cargado (Spring IS charged)

- **Bit 5 of Register 32001** = **"Contacto de PF preparado para cerrarse (sólo con MasterPact)"**
  - 0 = No preparado para cerrarse  
  - 1 = Preparado para cerrarse (Ready to Close)

### From Escritura_MTZ.pdf (Page 2):
> "Bit 5: PF (Ready to Close) – Indica si el interruptor está listo para cerrar (muelle cargado, sin bloqueos). En Masterpact NT/NW/MTZ este bit es significativo (1 = listo para cerrar), mientras que en dispositivos que no tienen resorte de cierre (ej. Compact NSX sin motor) este bit puede no aplicar (en NSX aparece siempre en 0)"

### Summary for PLC Logic:
- **To check if spring is charged:** Read register 32001, check **bit 3** (CH)
- **To check if breaker is ready to close:** Read register 32001, check **bit 5** (PF) — this includes spring charged + no blockages
- **Quality validation:** Always check corresponding bit in register 32000 first
- **Close inhibit check:** Read register 32341, verify bits 0 and 1 are both 0

---

## 5. STANDARD DATA SET ADDRESS RANGES

The standard data set occupies registers **32000–32341** and requires 3 read requests:

| Request | Registers | Address Start | Count |
|---------|-----------|---------------|-------|
| 1 | 32000–32123 | 0x7CFF | 124 |
| 2 | 32124–32241 | 0x7D7B | 118 |
| 3 | 32340–32435 | 0x7E53 | 96 |

---

## 6. PREREQUISITI / CONFIGURATION NOTES (from Escritura_MTZ.pdf)

- **Interface required:** IFM Modbus-SL (RS-485) — la IFE es para comunicación TCP
- **Remote control:** Verificar que no haya perilla de mando remoto deshabilitada
- **Accessories needed:** Bobina de disparo MX (apertura remota) + Bobina de cierre XF (cierre remoto)
- **Modbus lock:** El candado de bloqueo de Modbus debe estar en posición abierta para comandos de control remoto
