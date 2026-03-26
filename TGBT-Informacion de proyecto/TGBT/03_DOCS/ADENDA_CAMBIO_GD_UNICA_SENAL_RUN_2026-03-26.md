# Adenda tecnica - Cambio GD con unica senal RUN

Fecha: 2026-03-26
Alcance: GD1 y GD2

## Resumen de cambio

Se eliminan del control automatico las senales externas por generador:

- READY
- RUNNING
- ALARM

La orden al generador sigue siendo la salida existente de marcha/parada:

- GD1 RUN: `%Q1.0`
- GD2 RUN: `%Q1.1`

## Nuevo criterio de disponibilidad para transferencia a generador

Para cerrar `QG1` o `QG2`, SCMTA exige en AUTO:

1. Medicion Modbus del medidor del GD correspondiente OK (`GDx_MEASUREMENT_OK = TRUE`).
2. Tension trifasica del GD dentro de rango (`V_MIN_PCT` a `V_MAX_PCT`).
3. Frecuencia del GD dentro de rango (`FREQ_MIN` a `FREQ_MAX`).
4. Condiciones 1-3 sostenidas durante `T_GD_STABILIZATION = 30 s`.

Si las condiciones no se logran en `T_GD_READY_TIMEOUT`, se genera falla de arranque.

## Interlocks

Se mantiene sin cambios la filosofia de seguridad de fuente unica:

- Nunca cerrar dos de `QT1`, `QG1`, `QG2` simultaneamente.

## Sirena

La salida de alarma/sirena se mapea a `%Q1.2`.

## Impacto en HMI

- Los estados READY/RUNNING/ALARM externos de GD dejan de ser criterio de control.
- El estado de transferencia/falla se informa por estado SCMTA y `FAULT_CODE`.
