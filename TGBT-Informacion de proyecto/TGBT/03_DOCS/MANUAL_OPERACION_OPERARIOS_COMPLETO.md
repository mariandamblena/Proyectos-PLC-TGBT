# Manual Completo de Operacion SCADA/HMI - Sistema de Transferencia SCMTA

## 1. Alcance
Este manual describe la operacion del sistema de transferencia de la planta (RED <-> GENERADOR) desde HMI/SCADA para operarios y supervisores de mantenimiento.

Incluye:
- Navegacion de pantallas.
- Criterios de operacion en automatico y manual.
- Maniobras de transferencia.
- Significado de estados e indicadores.
- Uso de alarmas y reset de fallas.

## 2. Control de acceso
Para ingresar a pantallas restringidas (Parametros, Interruptores, Alarmas) se debe autenticar como Jefe de mantenimiento:

- Usuario: admin
- Contrasenia: 1234567890

Recomendacion operativa:
- No compartir credenciales fuera del personal autorizado.
- Registrar en turno cuando se realizaron cambios de parametros.

## 3. Descripcion de pantallas HMI

### 3.1 Pantalla Principal
Muestra en tiempo real:
- Fuente activa de alimentacion de planta:
  - En RED (ruta por QT1).
  - En GENERADOR (ruta por QG1).
- Estado del sistema de transferencia.
- Indicador de FALLA.
- Indicador TRANSFIRIENDO.
- Modo del sistema: AUTOMATICO o MANUAL.
- Boton RESETEAR FALLA.

Interpretacion basica:
- FALLA apagado + TRANSFIRIENDO apagado: operacion estable.
- TRANSFIRIENDO encendido: secuencia de maniobra en curso.
- FALLA encendido: condicion anormal; revisar pantalla Alarmas y estado de interruptores.

### 3.2 Pantalla Parametros
Permite visualizar/ajustar:
- Limites electricos:
  - V_NOM: tension nominal de referencia del sistema (base para evaluar calidad de red y generador).
  - V_MIN_PCT: porcentaje minimo permitido respecto de V_NOM. Por debajo de este valor, la fuente se considera fuera de rango.
  - V_MAX_PCT: porcentaje maximo permitido respecto de V_NOM. Por encima de este valor, la fuente se considera fuera de rango.
  - FREQ_NOM: frecuencia nominal de referencia del sistema.
  - FREQ_MIN: limite inferior de frecuencia aceptable para validar la fuente.
  - FREQ_MAX: limite superior de frecuencia aceptable para validar la fuente.
- Tiempos de secuencia SCMTA:
  - T_GRID_FAIL_FILTER: tiempo de filtro para confirmar falla de red y evitar disparos por ruido/microcortes.
  - T_START_GD_DELAY: espera antes de iniciar la secuencia de arranque del generador.
  - T_GD_READY_TIMEOUT: tiempo maximo para que el generador quede disponible antes de generar falla.
  - T_GD_STABILIZATION: tiempo que el generador debe permanecer estable antes de cerrar interruptor y tomar carga.
  - T_GRID_STABLE: tiempo que la red debe permanecer estable antes de habilitar el retorno desde generador.
  - T_GD_COOLDOWN: tiempo de enfriamiento del generador luego de transferir nuevamente a red.
  - Tiempos de apertura/cierre de interruptores y pulsos de comando: definen timeout de maniobra (T_OPEN_*, T_CLOSE_*) y duracion de pulsos de salida (T_CMD_PULSE / T_CMD_CONFIRM).
- Flags de habilitacion:
  - ENABLE_SCMTA: habilita o inhibe la logica automatica de transferencia.
  - ENABLE_AUTO_RETURN: permite retorno automatico a red cuando la red vuelve y se cumplen condiciones de estabilidad.
  - ENABLE_QG2: habilita la ruta de operacion con segundo generador (QG2) si esta instalado.
  - ENABLE_SHED: habilita la logica de deslastre automatico por prioridad de cargas.

Aclaraciones:
- ENABLE_SHED: la funcion de deslastre esta programada pero actualmente deshabilitada hasta incorporar el hardware necesario.
- ENABLE_QG2: habilita el uso de un segundo generador (si la instalacion lo posee).

### 3.3 Pantalla Medidores
Muestra mediciones por tablero/fuente (segun instrumentacion disponible):
- Tensiones L-L
- Frecuencia
- Corrientes
- Potencia
- Estado de comunicacion/validez

Uso recomendado:
- Confirmar calidad de RED y de GENERADOR antes de maniobras manuales.
- Verificar comunicacion de medidores cuando haya fallas de disponibilidad.

### 3.4 Pantalla Alarmas
Muestra historico de eventos/fallas con fecha y hora.

Uso recomendado:
- Identificar causa raiz antes de resetear.
- Confirmar desaparicion de la condicion anormal luego de intervenir.
- Documentar eventos relevantes en bitacora de turno.

### 3.5 Pantalla Interruptores
Muestra para QT1, QG1, QG2, Q22:
- Estado abierto/cerrado.
- Estado REMOTO (verde) / no remoto (rojo).
- Estado de FALLA (indicacion visual, puede titilar naranja).
- Botones ABRIR/CERRAR (operacion manual desde HMI).

## 4. Filosofia de operacion

### 4.1 Operacion automatica
La transferencia automatica solo se ejecuta correctamente si:
- Modo sistema en AUTOMATICO.
- Interruptores requeridos en REMOTO.
- Sin fallas activas en los equipos de maniobra.
- Condiciones electricas validas segun parametros.

### 4.2 Operacion manual
Se utiliza para pruebas, mantenimiento o contingencias.

Puede ejecutarse de dos formas:
- Desde botonera de tablero (selectores en LOCAL).
- Desde HMI (sistema en MANUAL y equipos a controlar en REMOTO).

Nota:
- Definir una sola autoridad de mando (tablero o HMI) por maniobra para evitar ordenes cruzadas.

## 5. Estados operativos del SCMTA (vista de operador)
Estados tipicos que pueden verse en pantalla principal:

- INIT: inicializacion del sistema.
- NORMAL_ON_GRID: planta alimentada por RED.
- GRID_FAIL_OPEN_QT1: deteccion de falla de RED e inicio de transferencia.
- START_GD1_DELAY / START_GD1: secuencia de arranque de generador.
- WAIT_GD1_READY: espera de disponibilidad de generador.
- CLOSE_QG1: cierre de interruptor de generador.
- ON_GD1: planta alimentada por generador.
- GRID_RETURN / WAIT_GRID_STABLE: red recuperada y validacion de estabilidad.
- OPEN_ACTIVE_GD / CLOSE_QT1 / CLOSE_Q22: maniobra de retorno a red.
- GD_COOLDOWN: enfriamiento de generador luego de transferencia a red.
- FAULT_LOCKOUT: bloqueo por falla hasta recuperacion/accion de operador.

## 6. Indicadores FALLA y TRANSFIRIENDO

### 6.1 Cuando se enciende FALLA
Se enciende cuando el sistema entra en condicion de error (FAULT_LOCKOUT) por ejemplo:
- Timeout de apertura/cierre de interruptores.
- Generador no disponible dentro de tiempo esperado.
- Equipo no en remoto cuando la secuencia lo requiere.
- Violacion de interlock.

### 6.2 Cuando se enciende TRANSFIRIENDO
Se enciende durante estados de maniobra, por ejemplo:
- Apertura/cierre de interruptores para pasar de RED a GD.
- Apertura/cierre para retorno de GD a RED.

## 7. Codigos de falla (referencia operativa)

| Codigo | Descripcion | Accion recomendada |
|---|---|---|
| 101 | Timeout apertura QT1 | Verificar mando ABRIR QT1, estado remoto y realimentacion de posicion. Corregir y resetear falla. |
| 102 | GD1 no listo dentro del timeout | Revisar disponibilidad GD1 (tension, frecuencia, comunicacion y run). Ajustar tiempos solo si corresponde y resetear. |
| 103 | Timeout cierre QG1 | Verificar orden de cierre, estado remoto QG1, enclavamientos y realimentacion de cierre. |
| 104 | Timeout apertura QG1 | Verificar orden de apertura, estado remoto QG1 y realimentacion de apertura. |
| 105 | Timeout cierre QT1 | Verificar estado remoto QT1, permisivos de cierre y realimentacion de posicion. |
| 106 | GD1 no disponible durante operacion | Confirmar estado del generador (run/medicion/frecuencia) y continuidad de comunicacion. |
| 107 | Violacion de interlock | Detener maniobra, revisar logica de enclavamiento y posicion real de interruptores antes de resetear. |
| 108 | Estado desconocido | Revisar diagnostico del PLC/HMI, validar version de programa y reinicializar en condicion segura. |
| 111 | QT1 no esta en remoto | Pasar QT1 a remoto (si se requiere control automatico/HMI) y confirmar en pantalla Interruptores. |
| 112 | QG1 no esta en remoto | Pasar QG1 a remoto (si se requiere control automatico/HMI) y confirmar en pantalla Interruptores. |
| 202 | Timeout cierre QG2 | Verificar orden de cierre QG2, estado remoto, enclavamientos y realimentacion. |
| 203 | Timeout apertura QG2 | Verificar orden de apertura QG2, estado remoto y realimentacion. |
| 204 | GD2 no listo dentro del timeout | Revisar disponibilidad GD2 (medicion, frecuencia, tension y run). |
| 206 | GD2 no disponible durante operacion | Verificar estado operativo GD2 y calidad electrica durante servicio. |
| 209 | Ambos generadores no disponibles | Revisar condiciones de GD1 y GD2, suministro de combustible, arranque y mediciones. |
| 210 | Timeout en secuencia de cambio GD1->GD2 | Verificar tiempos y feedback de maniobra de cambio entre generadores. |
| 211 | Timeout apertura Q22 | Verificar mando de apertura Q22, estado remoto y feedback (o cableado de posicion). |

Accion general ante cualquier falla:
1. Verificar causa en Alarmas y estado real en Interruptores.
2. Corregir la condicion de campo (remoto/local, enclavamiento, equipo, medicion).
3. Usar RESETEAR FALLA solo cuando la causa desaparecio.
4. Confirmar retorno a estado estable y registrar evento en turno.

## 8. Boton RESETEAR FALLA
Usar solamente cuando:
- La causa de falla fue eliminada.
- No hay riesgo electrico ni mecanico.
- Se confirmo estado correcto de equipos y permisos de mando.

No usar como solucion sin diagnostico.

## 9. Procedimientos operativos

### 9.1 Transferencia manual RED -> GENERADOR (ante corte)
Precondiciones:
- Confirmar corte o mala calidad de RED.
- Definir punto de mando (tablero u HMI).

Pasos:
1. Verificar QT1 abierto.
   - Si esta cerrado, abrir QT1.
2. Arrancar generador manualmente (si corresponde segun logica local del grupo).
3. Verificar tension/frecuencia del grupo estables.
4. Cerrar QG1.
5. Confirmar que la planta queda alimentada por generador.

### 9.2 Transferencia manual GENERADOR -> RED (retorno de red)
Precondiciones:
- Confirmar red restablecida y estable.

Pasos:
1. Abrir QG1.
2. Cerrar QT1.
3. Confirmar alimentacion por RED.
4. Mantener secuencia de enfriamiento del generador segun controlador del grupo.

## 10. Criterios de mando local/remoto

### 10.1 Si se opera desde botonera de tablero
- Selectores de interruptores en LOCAL.
- No ejecutar mando simultaneo desde HMI.

### 10.2 Si se opera desde HMI
- Sistema en MANUAL para mandos manuales.
- Interruptores a maniobrar en REMOTO.
- Confirmar realimentacion de estado luego de cada orden.

## 11. Notas sobre tiempos y estabilidad
- Los tiempos deben mantenerse coherentes entre HMI, PLC y controlador del generador.
- En pruebas de ajuste, registrar valores modificados y resultado.
- Una vez validados, consolidar valores de arranque y descargar al PLC.

## 12. Buenas practicas para operarios
- Verificar siempre estado real de interruptores antes de maniobrar.
- No forzar secuencias si hay fallas activas.
- Priorizar seguridad de personal y equipos.
- Dejar evidencia de eventos importantes en libro de guardia.
- Escalar a mantenimiento/ingenieria ante comportamientos no esperados.

## 13. Checklist rapido de turno
1. Modo correcto (AUTO/MANUAL) segun estrategia vigente.
2. Interruptores en REMOTO si se espera transferencia automatica.
3. Sin fallas activas en pantalla principal/alarmas.
4. Medidores con comunicacion y valores coherentes.
5. Parametros sin cambios no autorizados.
