# MANUAL DE USUARIO HMI
## TGBT SCMTA V4.0 - Operacion de Pantallas y Maniobras

**Proyecto:** TGBT IND-26-PTE-15  
**Sistema:** SCMTA (Sistema de Conmutacion Manual con Transferencia Automatica)  
**Base documental:** DEFINICION_PANTALLAS_HMI_V4 + logica SCL real V4 + evidencia visual de pantallas (`03_DOCS/Untitled presentation.pdf`)  
**Version manual:** 1.0  
**Fecha:** 2026-03-24

---

## 1. Objetivo del manual

Este manual explica como operar el HMI del TGBT SCMTA en campo:

- Donde encontrar cada informacion clave.
- Como navegar pantalla por pantalla.
- Como operar en AUTO y en MANUAL.
- Como hacer una transferencia manual RED <-> GD.
- Como actuar frente a fallas, bloqueos e interlocks.

El enfoque es operativo (operador/tecnico), no de programacion.

---

## 2. Alcance y criterio de operacion V4

En V4 el control principal de interruptores se hace por E/S digitales:

- QT1, QG1, QG2 y Q22 se confirman por DI de posicion.
- Los comandos salen como pulsos DO de 300 ms.
- Modbus se usa para medidores PM5350P (lectura de calidad de red y potencia).

Importante para operacion:

- Enclavamiento de fuente unica: no se permite cerrar dos fuentes a la vez.
- Modo AUTO: la secuencia la manda SCMTA.
- Modo MANUAL: los comandos manuales se arbitran y se bloquean si hay condiciones inseguras.
- Si un interruptor no esta en REMOTO, el comando desde HMI queda bloqueado.

---

## 3. Roles de usuario recomendados

| Rol | Uso principal | Pantallas | Permisos recomendados |
|-----|---------------|-----------|-----------------------|
| Operador | Supervisar estado y alarmas | 1, 2, 3, 6 | Solo lectura + ACK alarmas segun politica |
| Tecnico | Maniobras y ajustes | Todas | Maniobras manuales + parametros |
| Administrador | Mantenimiento y comisionamiento | Todas | Total |

---

## 4. Reglas de seguridad antes de maniobrar

1. Verificar permiso operativo y procedimiento interno de seguridad del sitio.
2. Confirmar que los interruptores a maniobrar estan en REMOTO.
3. Verificar en sinoptico que solo una fuente este cerrada (enclavamiento).
4. Confirmar estado del generador antes de transferir a GD:
   - GD READY = TRUE
   - GD RUNNING = TRUE
   - GD ALARM = FALSE
5. No operar en MANUAL sin necesidad operacional clara.
6. Si hay FAULT activa, identificar codigo de falla antes de resetear.

---

## 5. Mapa de navegacion HMI

| Pantalla | Para que sirve | Cuando usarla |
|----------|----------------|---------------|
| 1. Sinoptico Principal | Vista general del sistema y fuente activa | Monitoreo continuo |
| 2. Estado SCMTA | Estado de maquina, flags y falla | Diagnostico de secuencia |
| 3. Mediciones PM5350P | Tensiones, frecuencia, potencia, comunicacion | Verificar calidad de red/GD |
| 4. Control Manual | Comandos de apertura/cierre en MANUAL | Maniobra asistida |
| 5. Parametros del Sistema | Umbrales y tiempos | Ajustes tecnicos |
| 6. Alarmas y Eventos | Alarmas activas, ACK y reset | Atencion de eventos |

## 5.1 Validacion visual contra PDF de pantallas

Se valido este manual con el documento visual de referencia:

- `03_DOCS/Untitled presentation.pdf` (9 paginas de pantallas HMI)

Puntos de coherencia confirmados con ese PDF:

- Uso de estados de color para condicion de interruptores y permisos de operacion.
- Restriccion de operacion remota cuando el selector no esta en REMOTO.
- Navegacion por modo (AUTO/MANUAL), pantalla de parametros, mediciones y alarmas.
- Logica de operacion manual por botones de abrir/cerrar condicionada al modo y permisos.

Si en campo hubiera diferencia entre HMI cargado y este manual, prevalece la pantalla en runtime y se debe registrar la discrepancia para actualizar este documento.

---

## 6. Pantalla 1 - Sinoptico Principal (lectura rapida)

## 6.1 Que mirar primero (orden recomendado)

1. Modo actual: AUTO o MANUAL.
2. Fuente activa:
   - IS_ON_GRID = en red.
   - IS_ON_GD = en generador.
3. Estado textual SCMTA (STATE_NAME).
4. Codigo de falla (si existe).
5. Estado visual de QT1, QG1, QG2, Q22.

## 6.2 Como interpretar colores de interruptores

| Condicion | Significado operativo |
|-----------|-----------------------|
| Verde solido | Cerrado sin falla |
| Gris solido | Abierto sin falla |
| Rojo parpadeante | Falla del interruptor |
| Naranja (sin remoto) | Bloqueado para mando remoto |

## 6.3 Dato clave de decision

Si estas por maniobrar manualmente, desde esta pantalla validas:

- Que no haya alarma activa critica.
- Que la fuente actual sea la esperada.
- Que el equipo a operar tenga REMOTO habilitado.

---

## 7. Pantalla 2 - Estado SCMTA (diagnostico de secuencia)

Esta pantalla es la referencia para entender que esta haciendo la logica automatica.

## 7.1 Campos clave

| Campo | Que indica |
|-------|------------|
| STATE_NAME | Estado actual de la maquina de transferencia |
| ELAPSED_TIME | Tiempo en el estado actual |
| FAULT_CODE | Codigo de falla actual |
| MODE_AUTO | Seleccion AUTO/MANUAL |
| GRID_OK / GRID_FAIL | Calidad de red evaluada por logica |
| IS_IN_TRANSFER | Secuencia de conmutacion en curso |
| IS_ON_GRID / IS_ON_GD | Fuente activa |

## 7.2 Estados operativos mas importantes

| Estado | Significado practico |
|--------|-----------------------|
| NORMAL_ON_GRID | Operacion estable en red |
| GRID_FAIL_OPEN_QT1 | Inicio transferencia por falla de red |
| WAIT_GD1_READY / WAIT_GD2_READY | Espera disponibilidad de generador |
| CLOSE_QG1 / CLOSE_QG2 | Cierre de fuente GD |
| ON_GD1 / ON_GD2 | Operacion estable en generador |
| WAIT_GRID_STABLE | Espera red estable para retorno |
| CLOSE_QT1 | Retorno a red en proceso |
| FAULT_LOCKOUT | Bloqueo por falla; requiere atencion |

## 7.3 Cuando usar RESET FALLA

Usar RESET FALLA solo cuando:

1. Ya se identifico y corrigio la causa.
2. Las condiciones de red/fuente son seguras.
3. El personal de operacion autoriza reintento.

---

## 8. Pantalla 3 - Mediciones PM5350P

## 8.1 Donde ver calidad de red

La referencia principal de red es C02 (RED):

- V L1-L2, V L2-L3, V L3-L1
- FREQ
- COMM_OK

## 8.2 Como interpretar en operacion

1. Si GRID_MEAS_OK = TRUE, SCMTA usa medicion PM5350 para calidad de red.
2. Si GRID_MEAS_OK = FALSE, la logica usa respaldo por DI UV/OV.
3. Si COMM de un medidor esta en OFF, tratar la lectura como no confiable para decision operativa.

## 8.3 Uso recomendado antes de transferir a GD

- Confirmar que la red realmente esta fuera de rango o inestable, o que la transferencia manual es requerida por procedimiento.
- Confirmar mediciones validas del tablero asociado al GD objetivo (si aplica).

---

## 9. Pantalla 4 - Control Manual (maniobras)

Disponible solo en modo MANUAL.

## 9.1 Condiciones de habilitacion de botones

Un comando solo se ejecuta si se cumplen todas las condiciones:

1. MODE_MANUAL = TRUE
2. Interruptor objetivo en REMOTO
3. Sin conflicto OPEN+CLOSE simultaneo
4. Sin violacion de enclavamiento de fuente unica

## 9.2 Bloqueos que puede mostrar

| Bloqueo | Causa tipica | Accion |
|---------|--------------|--------|
| BLOCK_LOCAL | Interruptor en LOCAL | Pasar selector a REMOTO |
| BLOCK_INTERLOCK | Cierre inseguro por otra fuente cerrada | Abrir primero la fuente activa que bloquea |
| BLOCK_CONFLICT | Se pidio abrir y cerrar a la vez | Repetir comando unico |

## 9.3 Alcance de maniobra manual en HMI

Comandos manuales disponibles en HMI V4:

- ABRIR/CERRAR QT1
- ABRIR/CERRAR QG1
- ABRIR/CERRAR QG2 (si ENABLE_QG2)
- ABRIR/CERRAR Q22

Nota operativa:

- El estado de GD (READY/RUNNING/ALARM) se monitorea en HMI.
- Si el arranque/parada de GD no esta implementado como comando HMI en tu proyecto de panel, hacerlo desde el sistema del generador segun procedimiento de planta.

---

## 10. Pantalla 5 - Parametros del Sistema

Pantalla de uso tecnico.

## 10.1 Parametros que mas impactan la operacion

| Parametro | Efecto en campo |
|-----------|-----------------|
| T_GRID_FAIL_FILTER | Evita transferencias por perturbaciones breves |
| T_GD_READY_TIMEOUT | Tiempo maximo de espera de GD listo |
| T_GRID_STABLE | Tiempo de red estable antes del retorno |
| T_CMD_PULSE | Duracion del pulso de mando a interruptor |
| ENABLE_QG2 | Habilita o deshabilita camino GD2 |
| ENABLE_SCMTA | Habilita automatismo de transferencia |

## 10.2 Buenas practicas

1. Cambiar parametros solo por personal autorizado.
2. Registrar valor anterior y valor nuevo (trazabilidad).
3. Probar cambios en ventana controlada cuando sea posible.
4. No modificar multiples tiempos criticos al mismo tiempo durante una emergencia.

---

## 11. Pantalla 6 - Alarmas y Eventos

## 11.1 Uso operativo

1. Detectar alarma activa.
2. Leer codigo y descripcion.
3. Ejecutar accion correctiva en campo.
4. Reconocer alarma (ACK).
5. Resetear falla solo cuando corresponda.

## 11.2 Codigos de falla mas frecuentes

| Codigo | Diagnostico rapido | Accion recomendada |
|--------|--------------------|--------------------|
| 101 | QT1 no abrio en tiempo | Revisar remoto, mecanismo y confirmacion DI |
| 102 | GD1 no listo en tiempo | Revisar arranque, combustible, alarmas GD |
| 103 | QG1 no cerro en tiempo | Revisar interlock y estado del interruptor |
| 105 | QT1 no cerro en retorno | Revisar remoto/permiso y estado mecanico |
| 111 | QT1 no en remoto | Poner QT1 en REMOTO |
| 112 | QG1 no en remoto | Poner QG1 en REMOTO |
| 202 | GD2 no listo en tiempo | Revisar disponibilidad GD2 |
| 203 | QG2 no cerro en tiempo | Revisar QG2 e interlocks |
| 209 | Ambos GD no disponibles | Intervencion tecnica prioritaria |

---

## 12. Procedimiento - Transferencia manual RED -> GD1

Este procedimiento se usa cuando se decide maniobra manual asistida por HMI.

## 12.1 Precondiciones

1. Permiso de maniobra autorizado.
2. Modo del sistema en MANUAL.
3. QT1, QG1 y Q22 en REMOTO.
4. Sin alarma activa que impida maniobra segura.
5. GD1 disponible (READY/RUNNING sin ALARM).

## 12.2 Secuencia recomendada

1. Desde pantalla 2, confirmar MODE_MANUAL = TRUE.
2. Desde pantalla 1 o 4, verificar QT1 actualmente cerrado (si se esta en red).
3. En pantalla 4, ejecutar ABRIR QT1.
4. Confirmar por DI que QT1 quedo abierto.
5. Ejecutar ABRIR Q22 (segun estrategia de acople de tu tablero).
6. Confirmar GD1 en marcha estable (READY + RUNNING).
7. Ejecutar CERRAR QG1.
8. Confirmar QG1 cerrado.
9. Verificar estado global:
   - IS_ON_GD = TRUE
   - IS_ON_GRID = FALSE
10. Registrar hora y resultado de maniobra.

## 12.3 Criterios de detencion

Detener maniobra y pasar a diagnostico si ocurre cualquiera de estos:

- BLOCK_INTERLOCK persistente.
- Falla de interruptor (rojo parpadeante / codigo activo).
- Perdida de remoto en equipo objetivo.
- Condicion anomala de generador.

---

## 13. Procedimiento - Transferencia manual GD -> RED

## 13.1 Precondiciones

1. Red disponible y estable segun mediciones.
2. Modo MANUAL activo.
3. QT1 y QG1 en REMOTO.
4. Sin falla bloqueante activa.

## 13.2 Secuencia recomendada

1. En pantalla 3, validar calidad de red (tension/frecuencia en rango).
2. En pantalla 4, ejecutar ABRIR QG1 (o QG2 si estaba activo).
3. Confirmar interruptor GD abierto.
4. Ejecutar CERRAR QT1.
5. Confirmar QT1 cerrado.
6. Ejecutar CERRAR Q22 si tu esquema lo requiere al retorno.
7. Verificar estado global:
   - IS_ON_GRID = TRUE
   - IS_ON_GD = FALSE
8. Confirmar que GD queda en condicion definida por procedimiento de planta.

---

## 14. Operacion en AUTO (resumen para operador)

## 14.1 Comportamiento esperado

1. En red normal: estado NORMAL_ON_GRID.
2. Si falla red (filtrada): abre QT1, abre Q22, arranca GD y cierra QGx.
3. En retorno: espera red estable, abre GD activo, cierra QT1, cierra Q22 y pasa a cooldown.

## 14.2 Que debe hacer el operador

- Supervisar, no intervenir salvo contingencia.
- Validar que la secuencia avance por estados coherentes.
- Atender alarmas y escalar si queda en FAULT_LOCKOUT.

---

## 15. Guia rapida de diagnostico

| Sintoma | Donde mirar | Posible causa |
|---------|-------------|---------------|
| No deja cerrar QT1/QG1/QG2 | Pantalla 4 + bloqueos | Interlock activo o equipo en LOCAL |
| Se queda en WAIT_GD_READY | Pantalla 2 + estado GD | GD no alcanza READY/RUNNING |
| Vuelve a GD durante retorno | Pantalla 2 (WAIT_GRID_STABLE) | Red inestable (GRID_OK no sostenido) |
| No responde comando manual | Pantalla 4 + REMOTO + alarmas | BLOCK_LOCAL, conflicto o falla activa |
| Alarmas recurrentes de timeout | Pantalla 6 + parametros | Tiempos cortos o confirmacion DI deficiente |

---

## 16. Checklist operativo

## 16.1 Antes de turno

1. Verificar estado sinoptico general.
2. Confirmar ausencia de fallas activas no resueltas.
3. Validar comunicacion PM5350 (si aplica).

## 16.2 Durante evento

1. Confirmar modo de operacion correcto.
2. Ejecutar maniobra segun secuencia aprobada.
3. Verificar feedback DI tras cada comando.

## 16.3 Cierre de evento

1. Confirmar fuente final correcta.
2. Revisar historial de alarmas/eventos.
3. Registrar incidencia y acciones realizadas.

---

## 17. Notas para capacitacion

Se recomienda formar a operadores con tres ejercicios:

1. Recorrido completo de pantallas y tags criticos.
2. Simulacion de transferencia manual RED -> GD.
3. Simulacion de falla con FAULT_LOCKOUT y recuperacion controlada.

---

## 18. Anexo rapido - Variables clave visibles en HMI

| Categoria | Variables clave |
|----------|-----------------|
| Modo | MODE_AUTO, MODE_MANUAL |
| Fuente activa | IS_ON_GRID, IS_ON_GD, IS_ON_GD1, IS_ON_GD2 |
| Calidad de red | GRID_OK, GRID_FAIL, GRID_MEASUREMENT_OK, GRID_FREQ |
| Estado SCMTA | SCMTA_STATE, SCMTA_STATE_NAME, ELAPSED_TIME |
| Fallas | IS_FAULT, FAULT_CODE, HMI_ALARM_ACTIVE, HMI_ALARM_TEXT |
| Bloqueos | BLOCK_LOCAL, BLOCK_INTERLOCK, BLOCK_CONFLICT |
| Maniobra manual | REQ_MAN_QT1_*, REQ_MAN_QG1_*, REQ_MAN_QG2_*, REQ_MAN_Q22_* |

---

## 19. Cierre

Este manual esta pensado para operacion diaria y contingencias reales.  
Si quieres, el siguiente paso es convertir este contenido en:

1. Version PDF para impresion (operador en sala electrica).
2. Version resumida de 2 paginas (chuleta de maniobras).
3. Version tipo presentacion para capacitacion de turno.
