# ANALISIS GUIADO DEL SCL ACTUAL (V4)

> Fecha: 2026-03-13  
> Fuente de verdad: `01_SCL/`  
> Objetivo: entender como corre el sistema en V4 leyendo el codigo real, no solo la documentacion historica.

---

## 1. Idea central del proyecto

El sistema esta armado como un ciclo repetitivo de `OB1` que:

1. lee entradas fisicas y las normaliza
2. decide la secuencia de transferencia
3. arbitra comandos para que no haya maniobras peligrosas
4. convierte comandos logicos en pulsos fisicos
5. actualiza mediciones, pilotos y variables HMI

La foto mas fiel de esa secuencia esta en [`../01_SCL/10_OB1_MAIN.scl`](../01_SCL/10_OB1_MAIN.scl).

### Flujo real V4

```text
DI fisicas
  -> FB_IO_NORMALIZE
  -> DATA_BUFF
  -> FB_SCMTA
  -> FB_CMD_ARBITER
  -> FB_PULSE_EXPANDER
  -> %Q fisicas / ordenes a GD

En paralelo:
MODBUS_MANAGER -> mediciones PM5350P -> DATA_BUFF
OUTPUTS -> pilotos y textos HMI
```

### Ojo con la documentacion vieja

En el repo conviven documentos de V3 y V4. Para entender el comportamiento actual:

- tomar como verdad el codigo de [`../01_SCL`](../01_SCL)
- usar [`README_TEST.md`](../07_TEST/README_TEST.md) como respaldo funcional de V4
- leer las docs viejas solo como contexto historico

En V4 hay tres cambios que pueden confundir si uno se guia solo por docs anteriores:

- el control principal de QT1, QG1, QG2 y Q22 se hace por E/S digitales
- `06_FB_MODBUS_MANAGER` queda enfocado en lectura de medidores PM5350P
- `07_FB_MTZ_DRIVER.scl` sigue existiendo en el repo, pero no participa del `OB1` actual

---

## 2. Como pensar el scan de OB1

[`10_OB1_MAIN.scl`](../01_SCL/10_OB1_MAIN.scl) es el orquestador. Cada network cumple un papel puntual.

### Network 1: `01_FB_IO_NORMALIZE`

Archivo base: [`01_FB_IO_NORMALIZE.scl`](../01_SCL/01_FB_IO_NORMALIZE.scl)

Este bloque toma DI crudas y las pasa a un formato logico uniforme:

- `DI_QT1_CLOSE` pasa a `QT1_CLOSED`
- `QT1_OPEN` se calcula como `NOT QT1_CLOSED`
- `DI_QT1_REMOTE` pasa a `QT1_REMOTE`
- `DI_GD1_READY`, `DI_GD1_RUNNING`, `DI_GD1_ALARM` pasan a `GD_READY`, `GD_RUNNING`, `GD_ALARM`

En V4 esta version ya no hace debounce de pulsadores ni genera pedidos manuales desde botonera. Es una version simplificada orientada a estados por DI y mando manual via HMI/DB.

### Network 2: `02_FB_SCMTA`

Archivo base: [`02_FB_SCMTA.scl`](../01_SCL/02_FB_SCMTA.scl)

Es el corazon del sistema. Lee:

- modo automatico
- estado de interruptores por DI
- calidad de red
- estado de los grupos diesel
- tiempos y umbrales desde `DB_PARAMS`

Y produce:

- `STATE` y `STATE_NAME`
- `REQ_SCMTA_OPEN_*` / `REQ_SCMTA_CLOSE_*`
- `DO_GD_START`, `DO_GD2_START`
- banderas de estado global como `IS_ON_GRID`, `IS_ON_GD`, `GRID_FAIL`, `FAULT_CODE`

Importante: estos `REQ_*` son pedidos logicos de un solo scan. Todavia no son salidas fisicas.

### Network 3: `03_FB_SHED`

Archivo base: [`03_FB_SHED.scl`](../01_SCL/03_FB_SHED.scl)

El bloque de deslastre sigue presente para compatibilidad de arquitectura, pero en V4 se llama con:

- `ENABLE := "DB_PARAMS".ENABLE_SHED`
- `ENABLE_SHED := FALSE` por defecto en [`09_DB_PARAMS.scl`](../01_SCL/09_DB_PARAMS.scl)

Eso significa que hoy no es parte activa de la secuencia principal de transferencia.

### Network 4: `04_FB_CMD_ARBITER`

Archivo base: [`04_FB_CMD_ARBITER.scl`](../01_SCL/04_FB_CMD_ARBITER.scl)

Este bloque decide si un pedido realmente puede ejecutarse.

Hace tres cosas clave:

- elige fuente de pedido segun modo (`SCMTA` en AUTO, `MANUAL` en MANUAL)
- bloquea maniobras si el equipo esta en LOCAL
- aplica enclavamiento de fuente unica para que no puedan cerrarse dos fuentes a la vez

Resultado: transforma `REQ_*` en `CMD_*`.

### Network 5: `12_FB_PULSE_EXPANDER`

Archivo base: [`../01_SCL/12_FB_PULSE_EXPANDER.scl`](../01_SCL/12_FB_PULSE_EXPANDER.scl)

Convierte comandos de un scan en pulsos DO sostenidos de `T_CMD_PULSE`.

Ese patron resuelve esta necesidad:

- `CMD_CLOSE_QT1` vive un scan
- la bobina fisica necesita un pulso mas largo
- el `PULSE_EXPANDER` mantiene `%Q0.x` activo durante 300 ms por defecto

### Network 6: `06_FB_MODBUS_MANAGER`

Archivo base: [`06_FB_MODBUS_MANAGER.scl`](../01_SCL/06_FB_MODBUS_MANAGER.scl)

En V4 este bloque ya no gobierna los interruptores principales. Su rol practico es:

- configurar una vez el puerto RS-485 con `MB_COMM_LOAD`
- recorrer 7 medidores PM5350P
- leer tension, frecuencia y potencia
- copiar esas mediciones a `DATA_BUFF`

Por eso el SCMTA toma la calidad de red desde estas mediciones, pero confirma estados de interruptores por DI fisica.

### Network 7: `05_FB_OUTPUTS`

Archivo base: [`05_FB_OUTPUTS.scl`](../01_SCL/05_FB_OUTPUTS.scl)

Genera:

- pilotos de sistema
- pilotos OPEN/CLOSED/FAULT por interruptor
- baliza de alarma
- textos HMI

No decide maniobras: solo traduce estados a salidas de indicacion.

### Network 8: calculos auxiliares

OB1 calcula porcentajes de carga usando la potencia medida y la potencia nominal configurada en `DB_PARAMS`.

---

## 3. `DATA_BUFF` como blackboard del sistema

Archivo: [`08_DB_GLOBAL_STATUS.scl`](../01_SCL/08_DB_GLOBAL_STATUS.scl)

`DATA_BUFF` es el punto comun donde todos los bloques leen y escriben. Conviene pensarlo como el tablero interno de memoria compartida del PLC.

Dentro de `DATA_BUFF` conviven:

- modo y permisos: `MODE_AUTO`, `MODE_MANUAL`, `RESET_FAULT`, `ACK_ALARM`
- estados fisicos: `QT1_CLOSED`, `QG1_CLOSED`, `QG2_CLOSED`, fallas y remotos
- estado de generadores: `GD_READY`, `GD_RUNNING`, `GD_ALARM`
- mediciones: tensiones, frecuencia, potencia, calidad de comunicacion
- estado SCMTA: `SCMTA_STATE`, `SCMTA_STATE_NAME`, `IS_ON_GRID`, `IS_FAULT`, `FAULT_CODE`
- alarmas e HMI: `HMI_ALARM_ACTIVE`, `HMI_ALARM_TEXT`
- pilotos: `PILOT_ON_GRID`, `PILOT_QT1_OPEN`, etc.

Esto explica por que el proyecto se deja leer mejor si uno sigue los nombres de `DATA_BUFF` de un bloque a otro.

---

## 4. `DB_PARAMS`: donde vive la parametrizacion

Archivo: [`09_DB_PARAMS.scl`](../01_SCL/09_DB_PARAMS.scl)

Este DB no contiene logica; contiene criterios de operacion.

Los grupos mas importantes son:

- calidad de red: `V_NOM`, `V_MIN_PCT`, `V_MAX_PCT`, `FREQ_MIN`, `FREQ_MAX`
- tiempos de transferencia: `T_OPEN_QT1`, `T_START_GD_DELAY`, `T_GD_READY_TIMEOUT`, `T_CLOSE_QG1`
- retorno a red: `T_GRID_STABLE`, `T_OPEN_QG1`, `T_CLOSE_QT1`, `T_GD_COOLDOWN`
- actuacion fisica: `T_CMD_PULSE`, `T_CMD_CONFIRM`
- proteccion de motor: `T_MIN_GD_STAY`
- flags de etapa: `ENABLE_SCMTA`, `ENABLE_SHED`, `ENABLE_QG2`

Si queres entender por que el SCMTA espera o falla, casi siempre la respuesta esta en este DB.

---

## 5. Lectura guiada de `FB_SCMTA`

Archivo: [`02_FB_SCMTA.scl`](../01_SCL/02_FB_SCMTA.scl)

### 5.1 Lo primero que hace: decidir si la red esta bien o mal

El bloque calcula primero una condicion interna de red sana:

```scl
#gridFailRaw := NOT #gridOkRaw;
#tonGridFailFilter(IN := #gridFailRaw, PT := #T_GRID_FAIL_FILTER, Q => #GRID_FAIL);
```

Eso significa:

- `#gridOkRaw` = "ahora mismo la red parece OK"
- `#gridFailRaw` = "ahora mismo la red parece fallada"
- `#GRID_FAIL` no cambia enseguida: pasa por un filtro temporizado para evitar falsos disparos

Entonces el texto que tenias seleccionado, `#gridFailRaw := N...`, en realidad forma parte de la idea:

```text
si la red no esta OK ahora mismo, marco falla cruda;
si esa falla dura el tiempo configurado, recien ahi declaro GRID_FAIL.
```

### 5.2 Despues resetea pedidos de maniobra

Antes de entrar al `CASE`, el bloque pone todos los `REQ_SCMTA_*` en `FALSE`.

Eso le da a la salida este comportamiento:

- cada request dura un scan
- si el estado sigue necesitando la maniobra, la vuelve a emitir en un scan posterior segun la logica del estado

### 5.3 El `CASE #STATE OF` es la maquina de estados

El `CASE` es la parte mas importante para aprender a leer SCL en este proyecto.

Cada rama representa un estado del proceso. Ejemplo de lectura mental:

1. `ST_NORMAL_ON_GRID`
2. si hay `GRID_FAIL` y estamos en AUTO, pasar a `ST_GRID_FAIL_DETECTED`
3. pedir abrir QT1
4. abrir Q22
5. esperar y arrancar GD1
6. cuando GD esta listo, cerrar QG1
7. quedar en `ST_ON_GD1`
8. cuando la red vuelve y permanece estable, abrir el GD activo
9. cerrar QT1
10. cerrar Q22
11. hacer cooldown y volver a `ST_NORMAL_ON_GRID`

### 5.4 Estados que conviene memorizar primero

- `INIT`: detecta en que situacion arranca el PLC
- `NORMAL_ON_GRID`: estado estable con red
- `GRID_FAIL_DETECTED`: detecto falla y empiezo secuencia
- `START_GD1` / `WAIT_GD1_READY`: arranque del generador
- `CLOSE_QG1`: transferencia efectiva a GD1
- `ON_GD1`: operacion estable en grupo
- `WAIT_GRID_STABLE`: espero red estable antes de volver
- `OPEN_ACTIVE_GD` y `CLOSE_QT1`: retorno a red
- `GD_COOLDOWN`: enfriamiento antes de volver a normal
- `FAULT_LOCKOUT`: secuencia detenida por falla

### 5.5 El papel de Q22 en V4

Q22 aparece en la secuencia, pero su feedback todavia esta incompleto en el cableado/logica actual.

Por eso en `FB_SCMTA` los estados `OPEN_Q22` y `CLOSE_Q22` tienen esta idea:

- si llega confirmacion, avanzar
- si no llega y vence el tiempo, avanzar igual

Eso deja claro que Q22 hoy esta modelado como una maniobra tolerante a falta de feedback duro.

### 5.6 Fault lockout

`FAULT_LOCKOUT` es el estado de proteccion:

- memoriza `FAULT_CODE`
- corta las ordenes de arranque de GD
- espera intervencion o una condicion segura de recuperacion

Es una buena muestra de por que SCL sirve bien para esta logica: combina estados, timers, alarmas y prioridades sin volverse ilegible.

---

## 6. El patron mas importante del proyecto

El patron clave para leer casi todo el sistema es este:

```text
Estado o accion deseada
  -> REQ_*      (pedido logico)
  -> CMD_*      (pedido validado)
  -> OUT_%Q     (pulso fisico sostenido)
  -> DI_%I      (feedback real del campo)
  -> DATA_BUFF  (estado actualizado)
```

Ejemplo con QT1:

1. `FB_SCMTA` emite `REQ_SCMTA_OPEN_QT1`
2. `FB_CMD_ARBITER` verifica remoto, conflictos e interlock
3. si corresponde, genera `CMD_OPEN_QT1`
4. `FB_PULSE_EXPANDER` sostiene `%Q0.1`
5. la DI de posicion cambia
6. `FB_IO_NORMALIZE` vuelve a escribir `QT1_CLOSED` / `QT1_OPEN`
7. `FB_SCMTA` ve el nuevo estado en el siguiente scan

Eso es el ciclo completo de mando y realimentacion.

---

## 7. Mini guia para leer SCL en este proyecto

### `#variable`

El prefijo `#` indica una variable local del bloque actual.

Ejemplos:

- `#gridFailRaw`
- `#STATE`
- `#cmdSent`

No son tags globales. Existen dentro de esa instancia del FB.

### `:=`

Es asignacion.

Ejemplos:

```scl
#MODE_AUTO := #DI_SYS_AUTO;
#STATE := #ST_FAULT_LOCKOUT;
```

Se usa tanto para mover valores como para cambiar de estado.

### `=>`

Se usa al conectar una salida de bloque hacia una variable externa.

Ejemplo en `OB1`:

```scl
DO_GD_START => %Q1.0
```

Eso significa: la salida `DO_GD_START` del FB se escribe en la salida fisica `%Q1.0`.

### `CASE #STATE OF`

Es la forma estructurada de implementar una maquina de estados.

Cada rama es un estado. Cada `IF` dentro de la rama define transiciones o acciones del estado actual.

### Instancias `TON_TIME`, `R_TRIG`, `MB_MASTER`

El proyecto usa instrucciones IEC como objetos con memoria propia.

Ejemplos:

- `TON_TIME` para filtros y timeouts
- `R_TRIG` para detectar flancos
- `MB_MASTER` para transacciones Modbus

Eso es importante: cada instancia recuerda su estado entre scans.

### Instance DBs

Cuando ves una llamada como:

```scl
"02_FB_SCMTA_DB"(...)
```

significa que el FB se ejecuta con una memoria de instancia persistente.

Ahi quedan guardados sus temporizadores, memorias internas y variables estaticas entre un scan y el siguiente.

---

## 8. Tres escenarios para seguir el codigo sin perderse

### Escenario 1: happy path RED -> GD1 -> RED

Seguir este orden:

1. `OB1`
2. `FB_SCMTA`
3. `FB_CMD_ARBITER`
4. `FB_PULSE_EXPANDER`
5. `FB_IO_NORMALIZE`

Preguntas utiles:

- cuando decide que hay `GRID_FAIL`?
- cuando pide abrir QT1?
- cuando considera listo al GD?
- cuando vuelve a red?

### Escenario 2: falla de red filtrada 2 s

Ir directo a:

- calculo de `#gridOkRaw`
- asignacion de `#gridFailRaw`
- `tonGridFailFilter`

Ese tramo muestra muy bien como SCL mezcla booleanos y temporizadores sin necesidad de muchos rungs.

### Escenario 3: bloqueo por LOCAL o enclavamiento

Ir a [`04_FB_CMD_ARBITER.scl`](../01_SCL/04_FB_CMD_ARBITER.scl) y seguir:

- priorizacion de requests
- bloqueo local/remoto
- bloqueo por conflicto OPEN+CLOSE
- enclavamiento de fuente unica

Ese bloque explica por que no todo pedido termina en maniobra.

---

## 9. Como usar los tests para entender el sistema

Archivo guia: [`../07_TEST/README_TEST.md`](../07_TEST/README_TEST.md)

Los tests no son solo QA; tambien sirven como mapa de lectura.

Los tres recorridos mas utiles para estudiar el codigo actual son:

- happy path RED -> GD1 -> RED
- escenarios de falla y `FAULT_LOCKOUT`
- simulacion HMI/manual para ver `CMD_ARBITER` sin toda la secuencia automatica

Buena estrategia de estudio:

1. leer el escenario en `README_TEST.md`
2. ubicar que variables cambia el test
3. seguir esas mismas variables en `OB1`, `DATA_BUFF` y `FB_SCMTA`

---

## 10. Orden recomendado para estudiar el proyecto

Si queres entender el sistema rapido sin ahogarte en detalles, este orden funciona bien:

1. [`10_OB1_MAIN.scl`](../01_SCL/10_OB1_MAIN.scl)
2. [`08_DB_GLOBAL_STATUS.scl`](../01_SCL/08_DB_GLOBAL_STATUS.scl)
3. [`09_DB_PARAMS.scl`](../01_SCL/09_DB_PARAMS.scl)
4. [`02_FB_SCMTA.scl`](../01_SCL/02_FB_SCMTA.scl)
5. [`04_FB_CMD_ARBITER.scl`](../01_SCL/04_FB_CMD_ARBITER.scl)
6. [`12_FB_PULSE_EXPANDER.scl`](../01_SCL/12_FB_PULSE_EXPANDER.scl)
7. [`06_FB_MODBUS_MANAGER.scl`](../01_SCL/06_FB_MODBUS_MANAGER.scl)
8. [`05_FB_OUTPUTS.scl`](../01_SCL/05_FB_OUTPUTS.scl)
9. [`../07_TEST/README_TEST.md`](../07_TEST/README_TEST.md)

---

## 11. Resumen corto para llevarse

Si tuviera que resumir el proyecto en una sola idea:

> `OB1` llama bloques especializados que se comunican a traves de `DATA_BUFF`; el `SCMTA` decide, el `CMD_ARBITER` valida, el `PULSE_EXPANDER` actua, las DI devuelven el feedback real y el ciclo vuelve a empezar en el siguiente scan.

Y si tuviera que resumir el fragmento `#gridFailRaw := NOT #gridOkRaw;`:

> primero el bloque decide si la red parece sana o no; despues esa condicion cruda se filtra en el tiempo antes de convertirse en una falla valida para la secuencia automatica.
