# Manual de Operacion SCADA SCMTA (Resumido)

## 1. Objetivo
Este manual resume como operar el sistema de transferencia desde el HMI/SCADA para personal de turno.

## 2. Acceso a pantallas restringidas
Para ingresar a pantallas de Parametros, Interruptores y Alarmas:

- Usuario: admin
- Contrasenia: 1234567890
- Perfil: Jefe de mantenimiento

## 3. Navegacion de pantallas
- Principal: estado general del sistema y fuente de alimentacion activa.
- Parametros: ajustes de tiempos y limites electricos del SCMTA.
- Medidores: valores electricos por tablero (tension, frecuencia, corrientes, potencia, estado).
- Alarmas: eventos, avisos y registro historico.
- Interruptores: estado y mando de QT1, QG1, QG2, Q22.

## 4. Pantalla principal: que mirar
En la pantalla principal se visualiza:

- Si la planta esta en RED (QT1) o en GENERADOR (QG1).
- Estado del sistema (por ejemplo: INIT, NORMAL_ON_GRID, ON_GD1, TRANSFERENCIA, FALLA).
- Selector de modo AUTOMATICO / MANUAL.
- Indicador de FALLA.
- Indicador TRANSFIRIENDO.
- Boton RESETEAR FALLA.

## 5. Modo automatico: condiciones minimas
Para que la transferencia automatica funcione correctamente:

- El sistema debe estar en modo AUTOMATICO.
- QT1, QG1, QG2 y Q22 deben estar en REMOTO.
- Los interruptores no deben estar en falla.
- Los selectores fisicos de tablero deben permitir control remoto.

Si un interruptor no esta en remoto, el sistema puede bloquear una maniobra automatica.

## 6. Indicadores importantes
- FALLA encendida: existe condicion de falla activa. Revisar pantalla Alarmas.
- TRANSFIRIENDO encendida: el sistema esta ejecutando una secuencia de cambio de fuente.

## 7. RESETEAR FALLA: cuando usar
Usar solo cuando:

- La causa de la falla ya fue corregida.
- Los interruptores estan en condicion segura.
- Se verifico en Alarmas que no haya interlocks activos.

No resetear fallas en forma repetitiva sin diagnostico.

## 8. Parametros principales (pantalla Parametros)
- Tension nominal (V_NOM).
- Tension minima y maxima permitida (V_MIN_PCT, V_MAX_PCT).
- Frecuencia nominal, minima y maxima (FREQ_NOM, FREQ_MIN, FREQ_MAX).
- Tiempos de transferencia SCMTA (apertura/cierre, delays, estabilizacion, cooldown, etc.).

Notas:
- Funcion SHED (deslastre): programada pero deshabilitada hasta disponer de hardware de control.
- ENABLE_QG2: habilita operacion con segundo generador.

## 9. Pantalla interruptores
Se observa por cada interruptor (QT1, QG1, QG2, Q22):

- Estado abierto/cerrado.
- REMOTE: verde si esta en remoto (habilitado para mando HMI/automatico), rojo si no.
- FALLA: indicacion de falla (puede titilar en naranja segun configuracion de HMI).
- Botones ABRIR/CERRAR para operacion manual desde HMI.

## 10. Transferencia manual (resumen)
Puede hacerse:

- Desde botonera de tablero (selectores en LOCAL).
- Desde HMI (interruptores en REMOTO y sistema en MANUAL).

### 10.1 De RED a GENERADOR (corte de luz)
1. Verificar QT1 abierto (si no, abrir QT1).
2. Arrancar generador manualmente (si aplica).
3. Cerrar QG1.
4. Confirmar alimentacion en generador.

### 10.2 De GENERADOR a RED (retorno de red)
1. Verificar red restablecida.
2. Abrir QG1.
3. Cerrar QT1.
4. Confirmar alimentacion en red.

## 11. Reglas de seguridad operativa
- No cerrar dos fuentes en paralelo sin permiso de ingenieria/protecciones.
- Confirmar posicion real de interruptores antes de cada maniobra.
- Ante duda, dejar el sistema en condicion segura y escalar a mantenimiento.
- Registrar toda maniobra relevante en libro de turno.
