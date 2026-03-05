# LISTADO DE ENTRADAS Y SALIDAS — TGBT SCMTA V4.0

> **Versión:** 4.0  
> **Fecha:** 2026-03-03  
> **CPU:** Siemens S7-1215C DC/DC/Rly (14 DI / 10 DO integradas)  
> **Módulo expansión:** SM 1223 8DI/8DO (o equivalente)  
> **Cambio de alcance:** Eliminación Modbus MTZ. Control QT1/QG1/QG2/Q22 por E/S digitales. Modbus solo para PM5350P.

---

## 1. Resumen de I/O

| Tipo               | Usadas | Hardware                     |
|--------------------|--------|------------------------------|
| DI CPU             | 14     | %I0.0..%I0.7 + %I1.0..%I1.5 |
| DI EXP             | 6 asig + 2 spare | %I8.0..%I8.7           |
| DO CPU             | 10     | %Q0.0..%Q0.7 + %Q1.0..%Q1.1 |
| DO EXP             | 0 asig + 7 spare | %Q8.0..%Q8.7 (1L0.0 N/C) |
| Modbus RTU         | 7 PM5350P | Puerto CM 1241 RS-485       |

---

## 2. Entradas Digitales — CPU (%I0.x / %I1.x)

| Dir TIA | Borne (campo) | Señal interna        | Descripción                                                       |
|---------|---------------|----------------------|-------------------------------------------------------------------|
| %I0.0   | CPU 1M0.0     | DI_QT1_REMOTE        | QT1 selector REMOTO activo (TRUE = REMOTO, FALSE = LOCAL)        |
| %I0.1   | CPU 1M0.1     | DI_QT1_CLOSE         | QT1 cerrado (TRUE = CERRADO, FALSE = ABIERTO)                    |
| %I0.2   | CPU 1M0.2     | DI_QT1_FAULT         | QT1 en falla / disparado                                          |
| %I0.3   | CPU 1M0.3     | DI_QT1_UV_OV         | QT1 bajo/sobre tensión — DO del PM5350P C02 (señal backup)       |
| %I0.4   | CPU 1M0.4     | DI_BUSBAR_UV_OV      | Busbar bajo/sobre tensión — DO del PM5350P aguas arriba QT1 (indicador) |
| %I0.5   | CPU 1M0.5     | DI_QG1_REMOTE        | QG1 selector REMOTO activo                                        |
| %I0.6   | CPU 1M0.6     | DI_QG1_CLOSE         | QG1 cerrado                                                       |
| %I0.7   | CPU 1M0.7     | DI_QG1_FAULT         | QG1 en falla / disparado                                          |
| %I1.0   | CPU 1M1.0     | DI_QG1_UV_OV         | QG1 bajo/sobre tensión — DO del PM5350P C01-QG1                   |
| %I1.1   | CPU 1M1.1     | DI_QG2_REMOTE        | QG2 selector REMOTO activo                                        |
| %I1.2   | CPU 1M1.2     | DI_QG2_CLOSE         | QG2 cerrado                                                       |
| %I1.3   | CPU 1M1.3     | DI_QG2_FAULT         | QG2 en falla / disparado                                          |
| %I1.4   | CPU 1M1.4     | DI_QG2_UV_OV         | QG2 bajo/sobre tensión — DO del PM5350P C01-QG2                   |
| %I1.5   | CPU 1M1.5     | DI_GD1_READY         | GD1 listo para transferir (contacto aux. generador)               |

---

## 3. Entradas Digitales — Módulo Expansión (%I8.x)

| Dir TIA | Borne (campo) | Señal interna        | Descripción                                                       |
|---------|---------------|----------------------|-------------------------------------------------------------------|
| %I8.0   | EXP 1M0.0     | DI_GD1_RUNNING       | GD1 en marcha                                                     |
| %I8.1   | EXP 1M0.1     | DI_GD1_ALARM         | GD1 en alarma / falla                                             |
| %I8.2   | EXP 1M0.2     | DI_GD2_READY         | GD2 listo para transferir                                         |
| %I8.3   | EXP 1M0.3     | DI_GD2_RUNNING       | GD2 en marcha                                                     |
| %I8.4   | EXP 1M0.4     | DI_GD2_ALARM         | GD2 en alarma / falla                                             |
| %I8.5   | EXP 1M0.5     | DI_Q22_REMOTE        | Q22 selector REMOTO activo (asignado desde SPARE)                 |
| %I8.6   | EXP 1M0.6     | — (SPARE)            | Libre                                                             |
| %I8.7   | EXP 1M0.7     | — (SPARE)            | Libre                                                             |

> **Nota RESET_FAULT / ACK_ALARM:** Pueden asignarse desde HMI (bit de DB) o ocupar las últimas DI spare si se decide usar pulsador físico.

---

## 4. Salidas Digitales — CPU (%Q0.x / %Q1.x)

> ⚠️ **Todas las DO de comando son PULSOS de duración `T_CMD_PULSE` (default 300 ms).**  
> Replican el comportamiento de los pulsadores físicos en puerta de tablero.  
> El PLC confirma la acción leyendo la DI de posición correspondiente.

| Dir TIA | Borne (campo) | Señal interna        | Descripción                                                       |
|---------|---------------|----------------------|-------------------------------------------------------------------|
| %Q0.0   | CPU 1L0.0     | DO_QT1_CLOSE_CMD     | QT1 — pulso CERRAR                                                |
| %Q0.1   | CPU 1L0.1     | DO_QT1_OPEN_CMD      | QT1 — pulso ABRIR                                                 |
| %Q0.2   | CPU 1L0.2     | DO_QG1_CLOSE_CMD     | QG1 — pulso CERRAR                                                |
| %Q0.3   | CPU 1L0.3     | DO_QG1_OPEN_CMD      | QG1 — pulso ABRIR                                                 |
| %Q0.4   | CPU 1L0.4     | DO_QG2_CLOSE_CMD     | QG2 — pulso CERRAR                                                |
| %Q0.5   | CPU 1L0.5     | DO_QG2_OPEN_CMD      | QG2 — pulso ABRIR                                                 |
| %Q0.6   | CPU 1L0.6     | DO_Q22_CLOSE_CMD     | Q22 — pulso CERRAR                                                |
| %Q0.7   | CPU 1L0.7     | DO_Q22_OPEN_CMD      | Q22 — pulso ABRIR                                                 |
| %Q1.0   | CPU 2L0.0     | DO_GD1_RUN           | GD1 — arranque (sostenido mientras deba estar en marcha)          |
| %Q1.1   | CPU 2L0.1     | DO_GD2_RUN           | GD2 — arranque                                                    |

---

## 5. Salidas Digitales — Módulo Expansión (%Q8.x)

| Dir TIA | Borne (campo) | Señal interna      | Descripción     |
|---------|---------------|--------------------|-----------------|
| %Q8.0   | EXP 1L0.0     | — (N/C en listado) | Sin asignar     |
| %Q8.1   | EXP 1L0.1     | — (SPARE)          | Libre           |
| %Q8.2   | EXP 1L0.2     | — (SPARE)          | Libre           |
| %Q8.3   | EXP 1L0.3     | — (SPARE)          | Libre           |
| %Q8.4   | EXP 1L0.4     | — (SPARE)          | Libre           |
| %Q8.5   | EXP 1L0.5     | — (SPARE)          | Libre           |
| %Q8.6   | EXP 1L0.6     | — (SPARE)          | Libre           |
| %Q8.7   | EXP 1L0.7     | — (SPARE)          | Libre           |

> **Etapa 2:** Los pilotos físicos de tablero (EN RED, EN GRUPO, FALLA) deberían ocupar estas salidas spare cuando se monte el hardware de señalización.

---

## 6. Comunicación Modbus RTU — PM5350P (7 dispositivos)

> Propósito: lectura de mediciones (V, I, P, F) y alarmas (subtensión, sobretensión, pérdida de fase) de cada tablero. **Sin escritura de comandos.**

| Slave ID | Tablero | Interruptor asociado | Descripción                         |
|----------|---------|----------------------|-------------------------------------|
| 10       | C02     | QT1                  | Medidor red / fuente transformador  |
| 11       | C01     | QG1                  | Medidor GD1                         |
| 12       | C01     | QG2                  | Medidor GD2                         |
| 13       | C03     | —                    | Monitoreo C03 (feeders, sin control)|
| 14       | C04     | —                    | Monitoreo C04                       |
| 15       | C05     | —                    | Monitoreo C05                       |
| 16       | C06     | Q22                  | Monitoreo C06 (incluye Q22)         |

### 6.1 Registros PM5350P relevantes

> **Fuente verificada:** `PM51xx_PM53xx_PMC Register List_v2011_v2021_R01.xls`  
> Todos los registros de medición son **FLOAT32** (2 registros Modbus = 32 bits IEEE 754).  
> **Sin factor de escala** — los valores leídos ya están en las unidades indicadas.  
> Lectura única sugerida: `DATA_ADDR=3000, DATA_LEN=120` → cubre regs 3000..3119.

| Registro Modbus | Variable              | Tipo     | Unidad | Offset en rxBuffer (base 3000) |
|-----------------|-----------------------|----------|--------|--------------------------------|
| 3000            | Corriente A           | FLOAT32  | A      | [0..1]                         |
| 3002            | Corriente B           | FLOAT32  | A      | [2..3]                         |
| 3004            | Corriente C           | FLOAT32  | A      | [4..5]                         |
| 3020            | Tensión A-B (V L1-L2) | FLOAT32  | V      | [20..21] ← **usado en SCL**    |
| 3022            | Tensión B-C (V L2-L3) | FLOAT32  | V      | [22..23] ← **usado en SCL**    |
| 3024            | Tensión C-A (V L3-L1) | FLOAT32  | V      | [24..25] ← **usado en SCL**    |
| 3028            | Tensión A-N           | FLOAT32  | V      | [28..29]                       |
| 3036            | Tensión L-N Promedio  | FLOAT32  | V      | [36..37]                       |
| 3054            | Potencia Activa A     | FLOAT32  | kW     | [54..55]                       |
| 3060            | **P total activa**    | FLOAT32  | **kW** | **[60..61]** ← **usado en SCL**|
| 3068            | Q total reactiva      | FLOAT32  | kVAR   | [68..69]                       |
| 3076            | S total aparente      | FLOAT32  | kVA    | [76..77]                       |
| 3084            | FP total              | FLOAT32  | —      | [84..85]                       |
| 3110            | **Frecuencia**        | FLOAT32  | **Hz** | **[110..111]** ← **usado en SCL** |
| 3200+           | Alarmas (bitmap)      | —        | —      | fuera del rango de 120 regs    |

> ⚠️ **Nota:** Los registros anteriores (3019, 3053, 3109 con escalas INT) eran incorrectos.  
> Todos los valores del PM5350P son FLOAT32 sin escala según datasheet oficial.

---

## 7. Lógica de Posición de Interruptores (V4)

| Variable lógica    | Origen          | Notas                                              |
|--------------------|-----------------|-----------------------------------------------------|
| `QT1_CLOSED`       | DI %I0.1        | TRUE = cerrado                                     |
| `QT1_OPEN`         | NOT(%I0.1)      | Derivada, no hay DI separada de OPEN               |
| `QT1_FAULT`        | DI %I0.2        | TRUE = disparado / falla                           |
| `QT1_REMOTE`       | DI %I0.0        | TRUE = selector en REMOTO                          |
| `QT1_UV_OV_DI`     | DI %I0.3        | Backup de alarma (DO del PM5350P C02)              |

Ídem para QG1 (%I0.5..%I1.0) y QG2 (%I1.1..%I1.4).

---

## 8. Equipos sin control PLC en esta etapa (V4)

| Equipo       | Tablero | Acción PLC         | Monitoreo PM5350P |
|--------------|---------|--------------------|-------------------|
| Feeders C03  | C03     | Manual operador    | Sí (slave 13)     |
| Feeders C04  | C04     | Manual operador    | Sí (slave 14)     |
| Feeders C05  | C05     | Manual operador    | Sí (slave 15)     |
| Feeders C06* | C06     | Manual operador    | Sí (slave 16)     |
| Q22          | C06     | DO pulso + REMOTE  | Sí (slave 16)     |

*Excepto Q22 que sí tiene DO de comando y DI REMOTE en %I8.5.

---

## 9. Pendientes / Supuestos documentados

| # | Supuesto / Pendiente                                                                  | Acción requerida                              |
|---|--------------------------------------------------------------------------------------|-----------------------------------------------|
| 1 | Dirección %I8.x para EXP DI depende de la config de hardware en TIA Portal          | Verificar slot del módulo y ajustar si difiere|
| 2 | `RESET_FAULT` y `ACK_ALARM` mapeados desde HMI (bits de DB) por ahora              | Definir si se agrega pulsador físico          |
| 3 | Slave IDs PM5350P (10–16) son propuesta — confirmar con tablero y plano de red      | Ajustar en DB_PARAMS antes de comisionar      |
| 4 | DI_BUSBAR_UV_OV (1M0.4) se trata como indicador, no entra en lógica de control     | Revisar en etapa 2 si se necesita para control|
| 5 | QG2 no instalado aún → `ENABLE_QG2 = FALSE` en DB_PARAMS                           | Cambiar a TRUE cuando QG2 esté físicamente instalado |
| 6 | Deslastre FB_SHED compilado pero deshabilitado (`ENABLE_SHED = FALSE`)              | Habilitar en etapa 2 con los Modbus de feeders|
| 7 | Registros PM5350P a verificar con datasheet real (pm5350p.pdf en 06_CONFIG)         | Validar antes de primer arranque              |
