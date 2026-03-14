# Cierre Tecnico SCMTA/Modbus y Tests

Fecha: 2026-03-14
Proyecto: TGBT V4 (SCL, TIA V18)

## 1) Resumen ejecutivo
Se consolidó la logica de transferencia automatica RED <-> GD con foco en:
- Robustez de arranque del estado SCMTA (incluyendo arranques inconsistentes).
- Pruebas de secuencia automatica en banco con OB de test dedicados.
- Simulacion de fallas de interruptores para validacion funcional.
- Parametrizacion de tiempos criticos para puesta en marcha.
- Trazabilidad de mediciones Modbus PM5350 por medidor en DATA_BUFF.

## 2) Definiciones y decisiones tomadas
1. SCMTA con confirmacion por DI de posicion de interruptores.
2. Retardo intencional antes de cerrar Q22 en retorno a red.
3. En test NO se fuerzan remotos (se usan DI reales de remoto).
4. Simulacion de falla de interruptor: al entrar en falla, el interruptor se abre de inmediato.
5. Habilitacion de ruta GD2 configurable (ENABLE_QG2 desde DB_PARAMS).
6. Mapeo completo de mediciones Modbus por medidor hacia DATA_BUFF para HMI/diagnostico.

## 3) Archivos actualizados
- 01_SCL/02_FB_SCMTA.scl
- 01_SCL/09_DB_PARAMS.scl
- 01_SCL/10_OB1_MAIN.scl
- 01_SCL/10_OB1_MAIN_TEST_IMPORT.scl
- 01_SCL/OB_TEST_AUTO.scl
- 01_SCL/TEST_AUTO_FB.scl
- 01_SCL/TEST_AUTO_DB.scl

## 4) Cambios funcionales implementados
### 4.1 SCMTA
- Se agrego T_DELAY_CLOSE_Q22 para esperar antes de emitir cierre de Q22 en estado CLOSE_Q22.
- Se corrigio sintaxis SCL del bloque CLOSE_Q22 para compilacion TIA.
- Se reforzo ST_INIT para no quedar bloqueado cuando QT1 arranca abierto.
- Se agrego recuperacion de arranque inconsistente: si QG1/QG2 arrancan cerrados sin generador corriendo, primero abre GD activo para liberar enclavamiento.

### 4.2 Produccion (OB1 + DB_PARAMS)
- Se agregaron parametros en DB_PARAMS:
  - T_OPEN_Q22
  - T_DELAY_CLOSE_Q22
  - T_CLOSE_Q22
- Se cablearon dichos parametros en la llamada de 02_FB_SCMTA desde OB1.
- Se completo mapeo Modbus de PM5350 por indice 1..7 a DATA_BUFF:
  - RED (C02): V L1L2/L2L3/L3L1, FREQ, estados de medicion.
  - GD1 (C01_GD1): V L1L2/L2L3/L3L1, FREQ, P_TOTAL, MEAS_OK.
  - GD2 (C01_GD2): V L1L2/L2L3/L3L1, FREQ, P_TOTAL, MEAS_OK.
  - C03..C06: V_L1L2, P_TOTAL, MEAS_OK.

### 4.3 Test automatico
- Se habilito camino de test con OB dedicado y Main de test importable.
- Se removio forzado de remotos; REMOTE_ALLOWED toma DI real de remoto.
- Se agregaron banderas de falla simulada de interruptores en TEST_AUTO_FB/DB:
  - FORCE_QT1_FAULT
  - FORCE_QG1_FAULT
  - FORCE_QG2_FAULT
  - FORCE_Q22_FAULT
- Se mantuvo delay de 10s para cierre de Q22 en los OB de test.

## 5) Tests ejecutados y validaciones realizadas
1. Secuencia base RED -> GD -> RED validada en entorno de test.
2. Validacion de no arranque en INIT con QT1 abierto: corregido.
3. Validacion de caso inconsistente al encender con QG1 cerrado: corregido via apertura inicial de GD activo.
4. Validacion de compilacion sin errores en archivos modificados (iteraciones de correccion incluidas).
5. Validacion de delay Q22 en test (10s) y habilitacion para produccion via DB_PARAMS.
6. Validacion de disponibilidad de datos Modbus por medidor en DATA_BUFF (mapeo completado en OB1).

## 6) Parametros recomendados para puesta en marcha real
Valores base (ajustar segun maniobra real en campo):
- T_GRID_FAIL_FILTER = 2s
- T_GRID_STABLE = 120s
- T_OPEN_QT1 = 3s
- T_OPEN_Q22 = 3s
- T_START_GD_DELAY = 3s
- T_GD_READY_TIMEOUT = 30s (subir si el grupo tarda mas)
- T_GD_STABILIZATION = 5s
- T_CLOSE_QG1 = 3s
- T_CLOSE_QG2 = 3s
- T_OPEN_QG1 = 3s
- T_OPEN_QG2 = 3s
- T_CLOSE_QT1 = 3s
- T_DELAY_CLOSE_Q22 = 10s
- T_CLOSE_Q22 = 3s
- T_GD_COOLDOWN = 60s
- T_MIN_GD_STAY = 10m
- T_CMD_PULSE = 300ms
- T_CMD_CONFIRM = 2s

## 7) Pendientes tecnicos por definir
1. Feedback de generadores:
- Confirmar criterio final de READY/RUNNING/ALARM para GD1 y GD2 (fuente DI real, prioridad, debounce y fallas intermitentes).

2. Criterio de control por medidores PM5350 (C02):
- Definir formalmente si GRID_OK/GRID_FAIL se gobierna primariamente por PM5350 C02 (Modbus) y en que condiciones se usa fallback por DI.
- Definir politica ante perdida de comunicacion Modbus (timeouts, degradacion, retencion de ultimo valor y alarmado).

3. Criterio de disponibilidad GD2 en operacion real:
- Confirmar momento de habilitar ENABLE_QG2 en DB_PARAMS y pruebas SAT asociadas.

## 8) Checklist previo a comisionamiento
1. Compilar proyecto completo sin errores.
2. Verificar direccionamiento de DI/DO reales en gabinete.
3. Verificar remotos fisicos habilitados (sin forzados de software).
4. Confirmar IDs Modbus 1..7 y parametros de puerto RS485.
5. Confirmar valores nominales de potencia GD1/GD2 y umbrales de carga.
6. Ejecutar prueba funcional escalonada:
- Arranque en red normal.
- Transferencia por falla de red.
- Retorno a red con delay Q22.
- Inyeccion de falla de interruptor.
- Escenario de arranque inconsistente.

## 9) Nota operacional
Si se usa OB de test, no ejecutar en paralelo con Main productivo. Debe existir un solo ciclo principal activo para evitar escrituras concurrentes sobre las mismas instancias.
