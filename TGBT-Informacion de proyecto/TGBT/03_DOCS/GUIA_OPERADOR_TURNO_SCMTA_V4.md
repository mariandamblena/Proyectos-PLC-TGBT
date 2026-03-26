# GUIA OPERADOR DE TURNO
## SCMTA TGBT V4.0 - Operacion Rapida en Sala

**Proyecto:** TGBT IND-26-PTE-15  
**Sistema:** SCMTA (Conmutacion Manual con Transferencia Automatica)  
**Perfil:** Operador de Turno  
**Version:** 1.0  
**Fecha:** 2026-03-24

---

## 1. Objetivo de esta guia

Esta guia es para uso en turno:

- Ver rapido el estado del sistema.
- Ejecutar maniobras seguras en MANUAL.
- Responder a alarmas sin perder secuencia.

No reemplaza procedimientos de seguridad de planta.

---

## 2. Regla de oro del sistema

**Nunca deben quedar dos fuentes cerradas al mismo tiempo.**

Antes de cerrar una fuente, verificar que la otra este abierta.

---

## 3. Secuencia corta de verificacion al inicio de turno (2 minutos)

1. Ir a **Pantalla 1 - Sinoptico Principal**.
2. Confirmar modo actual:
   - AUTO o MANUAL.
3. Confirmar fuente activa:
   - EN RED o EN GD.
4. Confirmar que no haya alarma activa critica.
5. Ir a **Pantalla 3 - Mediciones** y validar:
   - Frecuencia y tension dentro de rango esperado.
6. Ir a **Pantalla 6 - Alarmas y Eventos**:
   - Revisar si hay alarmas sin atender del turno anterior.

---

## 4. Que mirar en cada pantalla (operador)

## Pantalla 1 - Sinoptico Principal

Mirar siempre en este orden:

1. Modo: AUTO/MANUAL.
2. Fuente activa: IS_ON_GRID o IS_ON_GD.
3. Estado SCMTA (texto).
4. Falla activa (si hay codigo).
5. Estado visual QT1, QG1, QG2, Q22.

Semaforo visual:

- Verde: cerrado OK.
- Gris: abierto OK.
- Rojo parpadeando: falla.
- Naranja: no remoto (bloqueado para HMI).

## Pantalla 2 - Estado SCMTA

Usar para entender por que avanza o se detiene la secuencia.

Campos clave:

- STATE_NAME
- ELAPSED_TIME
- FAULT_CODE
- GRID_OK / GRID_FAIL
- IS_IN_TRANSFER

## Pantalla 3 - Mediciones PM5350P

Usar para confirmar calidad de red antes de maniobra:

- V L1-L2, V L2-L3, V L3-L1
- FREQ
- COMM_OK

Si GRID_MEAS_OK = FALSE, considerar la lectura como degradada y avisar a tecnico.

## Pantalla 4 - Control Manual

Solo usar cuando el procedimiento pida MANUAL.

Botones disponibles:

- ABRIR/CERRAR QT1
- ABRIR/CERRAR QG1
- ABRIR/CERRAR QG2 (si habilitado)
- ABRIR/CERRAR Q22

## Pantalla 5 - Parametros

Solo referencia para operador. Cambios: solo personal tecnico autorizado.

## Pantalla 6 - Alarmas y Eventos

Secuencia operador:

1. Leer codigo y descripcion.
2. Corregir condicion en campo.
3. ACK.
4. RESET FALLA solo si condicion corregida.

---

## 5. Bloqueos tipicos y accion inmediata

| Mensaje/Bloqueo | Significa | Que hacer |
|-----------------|-----------|-----------|
| BLOCK_LOCAL | Interruptor en LOCAL | Pasar selector a REMOTO |
| BLOCK_INTERLOCK | Cierre inseguro por otra fuente cerrada | Abrir fuente bloqueante primero |
| BLOCK_CONFLICT | Se pidio abrir y cerrar juntos | Repetir un solo comando |
| FAULT_LOCKOUT | Sistema bloqueado por falla | Revisar causa + corregir + reset autorizado |

---

## 6. Maniobra rapida: Transferencia manual RED -> GD1

**Precondiciones obligatorias:**

1. Permiso de maniobra autorizado.
2. Modo en MANUAL.
3. QT1, QG1 y Q22 en REMOTO.
4. GD1 READY y RUNNING sin ALARM.

**Pasos:**

1. Pantalla 4: ABRIR QT1.
2. Confirmar QT1 abierto por estado/DI.
3. Pantalla 4: ABRIR Q22 (si aplica a tu esquema).
4. Confirmar GD1 estable.
5. Pantalla 4: CERRAR QG1.
6. Confirmar QG1 cerrado.
7. Validar en pantalla 1:
   - IS_ON_GD = TRUE
   - IS_ON_GRID = FALSE

**Si falla un paso:**

- No continuar la secuencia.
- Revisar bloqueo/alarma en pantallas 2 y 6.
- Escalar a tecnico si no se resuelve de inmediato.

---

## 7. Maniobra rapida: Transferencia manual GD -> RED

**Precondiciones obligatorias:**

1. Red estable confirmada en pantalla 3.
2. Modo MANUAL.
3. QT1 y QG1 en REMOTO.

**Pasos:**

1. Pantalla 4: ABRIR QG1 (o QG2 si estaba activo).
2. Confirmar fuente GD abierta.
3. Pantalla 4: CERRAR QT1.
4. Confirmar QT1 cerrado.
5. Pantalla 4: CERRAR Q22 (si aplica).
6. Validar en pantalla 1:
   - IS_ON_GRID = TRUE
   - IS_ON_GD = FALSE

---

## 8. Alarmas mas comunes (accion de turno)

| Codigo | Causa probable | Accion operador |
|--------|----------------|-----------------|
| 101 | QT1 no abrio en tiempo | Verificar remoto y posicion real QT1 |
| 102 | GD1 no listo en tiempo | Revisar estado de grupo y avisar tecnico |
| 103 | QG1 no cerro en tiempo | Revisar interlock y estado QG1 |
| 105 | QT1 no cerro en retorno | Verificar remoto/permiso de QT1 |
| 111 | QT1 no en remoto | Pasar QT1 a REMOTO |
| 112 | QG1 no en remoto | Pasar QG1 a REMOTO |
| 209 | Ambos GD no disponibles | Escalar inmediato a tecnico/mantenimiento |

---

## 9. Checklist de cierre de turno

1. Registrar fuente final del tablero (RED o GD).
2. Registrar si hubo transferencia manual o automatica.
3. Registrar alarmas activas/no resueltas.
4. Entregar novedades al siguiente turno.

---

## 10. Reglas de escalamiento

Escalar a tecnico o mantenimiento cuando:

1. Repite el mismo timeout mas de una vez.
2. Hay FAULT_LOCKOUT recurrente.
3. Hay perdida de comunicacion de medicion critica.
4. No se puede recuperar remoto de un interruptor.

---

## 11. Nota de seguridad

Ante duda operativa, detener la maniobra y escalar.  
Prioridad: seguridad del personal, del tablero y continuidad controlada.

---

## 12. Referencia completa

Para detalle tecnico y explicaciones ampliadas, ver:

- MANUAL_USUARIO_HMI_SCMTA_V4.md
