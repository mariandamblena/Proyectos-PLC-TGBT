# PROMPT BASE - NUEVO PROYECTO PLC

## Objetivo

Este prompt sirve para iniciar un nuevo proyecto de PLC siguiendo el mismo criterio de trabajo usado en este proyecto:

- separar el proyecto TIA Portal "vivo" de la carpeta de ingenieria/documentacion;
- mantener el codigo fuente exportable fuera de TIA;
- documentar arquitectura, I/O, equipos, HMI, comunicaciones y pruebas;
- dejar trazable el orden de importacion, validacion y comisionamiento.

---

## Estructura recomendada

### 1. Carpeta raiz del proyecto

```text
<PROYECTO_RAIZ>/
|- <CODIGO_PROYECTO>_V1-0/                      <- proyecto TIA Portal vivo
|- <CODIGO_PROYECTO>_V1-0.backup/               <- backups zip del proyecto TIA
|- <CODIGO_PROYECTO>-Informacion de proyecto/
|  \- <CODIGO_PROYECTO>/
|     |- README.md
|     |- 01_SCL/
|     |- 02_LADDER/
|     |- 03_DOCS/
|     |- 04_UML/
|     |- 05_MANUALES/
|     |- 06_CONFIG/
|     \- 07_TEST/
\- README_INICIO.md                              <- opcional, acceso rapido
```

### 2. Proyecto TIA Portal vivo

La carpeta del proyecto TIA Portal debe conservar la estructura que genera TIA. No se arma a mano salvo `UserFiles/` si hay paginas web del PLC.

```text
<CODIGO_PROYECTO>_V1-0/
|- <CODIGO_PROYECTO>_V1-0.ap18
|- <CODIGO_PROYECTO>_V1-0.info
|- AdditionalFiles/
|- IM/
|- Logs/
|- System/
|- TMP/
|- UserFiles/            <- solo si hay webserver HTML/AWP
|- Vci/
\- XRef/
```

### 3. Carpeta de ingenieria/documentacion

```text
<CODIGO_PROYECTO>-Informacion de proyecto/<CODIGO_PROYECTO>/
|- README.md
|- 01_SCL/               <- fuentes SCL exportables/importables
|- 02_LADDER/            <- equivalencias LADDER o referencias visuales
|- 03_DOCS/              <- documentacion funcional, tecnica y operativa
|- 04_UML/               <- diagramas PlantUML
|- 05_MANUALES/          <- manuales de fabricante y registros
|- 06_CONFIG/            <- planos, listado de equipos, listado I/O, PDFs base
\- 07_TEST/              <- pruebas para PLCSIM, SAT/FAT y casos de falla
```

---

## Contenido minimo por carpeta

### `01_SCL/`

Archivos sugeridos:

- `01_FB_IO_NORMALIZE.scl`
- `02_FB_<LOGICA_PRINCIPAL>.scl`
- `03_FB_<SECUENCIA_AUX>.scl`
- `04_FB_CMD_ARBITER.scl`
- `05_FB_OUTPUTS.scl`
- `06_FB_<COMUNICACION>.scl`
- `07_FB_<DRIVER_EQUIPO>.scl`
- `08_DB_GLOBAL_STATUS.scl`
- `09_DB_PARAMS.scl`
- `10_OB1_MAIN.scl`
- `11_INSTANCE_DBS.scl`

Convencion recomendada:

- usar nombres numerados para fijar orden de lectura/importacion;
- mantener un DB global compartido tipo `DATA_BUFF`;
- mantener un DB de parametros tipo `DB_PARAMS`;
- separar `OB1` en un archivo propio;
- separar instance DBs en un archivo propio;
- guardar todos los `.scl` en UTF-8 con BOM si van a importarse en TIA Portal.

### `02_LADDER/`

Usar solo si hace falta:

- conversiones de FB criticos a LADDER;
- documentacion visual para mantenimiento;
- equivalencias de rungs para tecnicos de campo.

### `03_DOCS/`

Documentos minimos:

- `INDEX.md`
- `RESUMEN_PROYECTO.md`
- `LISTADO_EQUIPOS.md`
- `LISTADO_IO.md`
- `README_<SIGLA>.md`
- `INTRODUCCION_TECNICA_INGENIERO.md`
- `VALIDACION_SCL_TIA_<VERSION>.md`
- `ARQUITECTURA_<SISTEMA>.md`
- `DEFINICION_PANTALLAS_HMI.md` si hay HMI
- `MANUAL_USUARIO_HMI.md` si hay HMI
- `GUIA_OPERADOR_TURNO.md` si hay operacion diaria
- `CAMBIOS_<REQ>.md` si hubo cambios de alcance

Opcionales:

- `WEBSERVER_<DB>.html`
- `WEBSERVER_<DB>_AWP.html`
- adendas de alcance;
- cierre tecnico;
- checklist de comisionamiento.

### `04_UML/`

Diagramas minimos:

- arquitectura general del sistema;
- maquina de estados principal;
- diagrama de actividad del proceso critico;
- diagrama del driver/protocolo si hay comunicaciones;
- `README_UML.md`.

### `05_MANUALES/`

Guardar:

- manual CPU PLC;
- manual HMI;
- manuales de equipos de potencia;
- manuales de comunicaciones;
- tablas de registros Modbus u otro protocolo;
- guidelines de programacion del fabricante.

### `06_CONFIG/`

Guardar la documentacion base del proyecto:

- listado original de equipos;
- listado original de entradas y salidas;
- planos o esquema de montaje;
- topologia de red/comunicaciones;
- PDFs de configuracion de medidores, variadores, breakers, etc.

### `07_TEST/`

Minimo recomendado:

- pruebas happy path;
- pruebas de fallas;
- pruebas de interlocks;
- pruebas HMI/manual;
- instance DBs de test;
- OB1 de test;
- `README_TEST.md`.

---

## Pipeline de trabajo recomendado

### Etapa 1. Relevar base del proyecto

Reunir antes de programar:

- objetivo funcional;
- secuencia operativa;
- reglas de seguridad e interlocks;
- listado de equipos;
- listado I/O;
- protocolo de comunicacion;
- planos del tablero;
- alcance HMI/webserver/SCADA;
- criterios de aceptacion FAT y SAT.

### Etapa 2. Crear estructura del proyecto

- crear carpeta raiz;
- crear proyecto TIA Portal inicial;
- crear carpeta de informacion del proyecto;
- copiar a `06_CONFIG/` toda la documentacion base;
- copiar a `05_MANUALES/` los manuales de fabricante.

### Etapa 3. Definir la arquitectura

- escribir `RESUMEN_PROYECTO.md`;
- escribir `README_<SIGLA>.md` con arquitectura y secuencias;
- definir si la arquitectura usara `DATA_BUFF` + `DB_PARAMS`;
- definir FBs principales y responsabilidades;
- definir naming de equipos, arrays y estados.

### Etapa 4. Modelar antes de codificar

- crear UML de arquitectura;
- crear UML de maquina de estados;
- crear UML de actividades del proceso critico;
- documentar prioridades de comando e interlocks.

### Etapa 5. Programar fuentes SCL exportables

- crear `01_SCL/` con bloques numerados;
- mantener OB1 separado;
- mantener instance DBs separados;
- mantener comentarios utiles;
- preparar archivos importables por TIA.

### Etapa 6. Importar y validar en TIA Portal

- crear CPU y hardware base;
- importar DBs primero;
- importar FBs luego;
- importar instance DBs;
- copiar codigo de `10_OB1_MAIN.scl` al OB1 existente;
- compilar;
- documentar errores, warnings y lecciones aprendidas.

### Etapa 7. Mapear hardware real

- asignar `%I`, `%Q`, `%M`, hardware y comunicaciones;
- documentar diferencias entre plano y montaje real;
- ajustar `LISTADO_IO.md`;
- validar selectores, pulsadores, pilotos y feedbacks.

### Etapa 8. Integrar HMI o webserver

- definir pantallas;
- definir tags a `DATA_BUFF` y `DB_PARAMS`;
- si aplica, crear pagina AWP/HTML y copiarla tambien a `UserFiles/`;
- documentar pantallas, alarmas y permisos.

### Etapa 9. Preparar pruebas

- crear tests de simulacion;
- crear checklist de precomisionamiento;
- preparar watch tables recomendadas;
- definir criterios de aceptacion.

### Etapa 10. Cerrar trazabilidad

- generar backup zip del TIA;
- registrar version del proyecto;
- dejar documentados pendientes, riesgos y TODOs;
- actualizar indice maestro.

---

## Reglas tecnicas que conviene conservar

- TIA Portal debe ser tratado como proyecto binario/vivo; el codigo fuente mantenible debe vivir aparte.
- Los `.scl` importables deben guardarse en UTF-8 con BOM.
- `OB1` conviene mantenerlo como archivo de referencia, pero en TIA normalmente se copia al bloque `Main` existente.
- Si se usa arquitectura blackboard, todo lo operativo debe pasar por `DATA_BUFF`.
- Los parametros ajustables deben concentrarse en `DB_PARAMS`.
- Las pruebas deben existir fuera del flujo productivo y tener su propio `OB1` de test.
- Si hay HMI, todas las variables deben salir de una fuente clara y estable.
- Si hay webserver, la version fuente del HTML/AWP debe quedar en `03_DOCS/` y la version operativa en `UserFiles/`.

---

## Prompt listo para reutilizar

Copiar y pegar el siguiente prompt para iniciar un nuevo proyecto:

```text
Quiero que armes la base completa de un nuevo proyecto de programacion de PLC siguiendo el mismo criterio de ingenieria y documentacion usado en nuestro proyecto TGBT/SCMTA.

Necesito que trabajes como lider tecnico de automatizacion industrial y que propongas una estructura profesional de proyecto, pensada para TIA Portal, mantenimiento futuro, trazabilidad y comisionamiento.

Datos del nuevo proyecto:
- Nombre del proyecto: <NOMBRE_PROYECTO>
- Codigo corto: <CODIGO_PROYECTO>
- Cliente / planta: <CLIENTE>
- Tablero o proceso: <TABLERO_O_PROCESO>
- PLC: <MODELO_PLC>
- Version TIA Portal: <VERSION_TIA>
- HMI: <MODELO_HMI o NO>
- Webserver PLC: <SI/NO>
- Protocolos de comunicacion: <MODBUS RTU / TCP / PROFINET / etc>
- Equipos principales: <LISTA>
- Objetivo funcional principal: <DESCRIPCION>
- Modos de operacion: <AUTO / MANUAL / LOCAL / REMOTO / etc>
- Cantidad estimada de DI: <N>
- Cantidad estimada de DO: <N>
- Cantidad estimada de AI/AO: <N>
- Restricciones o interlocks criticos: <LISTA>
- Alcance de pruebas: <PLCSIM / FAT / SAT / CAMPO>

Quiero que la respuesta incluya, en este orden:

1. Una propuesta de pipeline de trabajo de punta a punta para este proyecto.
2. Un diagrama de carpetas recomendado, separando:
   - proyecto TIA Portal vivo;
   - backups;
   - carpeta de informacion/documentacion de proyecto.
3. El detalle de que debe contener cada carpeta.
4. La lista de documentacion minima necesaria para poder arrancar bien el proyecto.
5. La lista de documentos tecnicos y operativos que deberian generarse durante el desarrollo.
6. La lista de archivos SCL sugeridos, con nombres numerados y responsabilidad de cada bloque.
7. Las reglas de importacion y validacion en TIA Portal, incluyendo:
   - encoding recomendado;
   - orden de importacion;
   - tratamiento de OB1;
   - uso de DB global compartido tipo DATA_BUFF;
   - uso de DB_PARAMS;
   - manejo de instance DBs.
8. Los entregables opcionales si el proyecto tiene HMI o paginas web del PLC.
9. Un checklist de inicio del proyecto con lo que debe estar definido antes de escribir codigo.
10. Un checklist de cierre para dejar el proyecto listo para pruebas y comisionamiento.

Instrucciones de formato:
- responder en espanol tecnico claro;
- no inventar datos que no fueron dados;
- si falta informacion, marcarla como pendiente;
- proponer nombres de archivos concretos en formato Markdown y SCL;
- usar una estructura similar a:
  - 01_SCL
  - 02_LADDER
  - 03_DOCS
  - 04_UML
  - 05_MANUALES
  - 06_CONFIG
  - 07_TEST
- si corresponde, agregar `UserFiles/` dentro del proyecto TIA para webserver;
- priorizar mantenibilidad, claridad documental y facilidad de importacion en TIA Portal.
```

---

## Checklist rapido de arranque

Antes de arrancar el nuevo proyecto, deberiamos tener como minimo:

- nombre y codigo del proyecto;
- version de TIA Portal;
- CPU/HMI definidos;
- listado de equipos;
- listado I/O preliminar;
- reglas de enclavamiento y seguridad;
- secuencia funcional;
- protocolo de comunicacion y mapa de equipos;
- alcance real de HMI/webserver/SCADA;
- criterio de pruebas.

---

## Nota practica

Tomando como referencia este proyecto, las carpetas realmente obligatorias son:

- el proyecto TIA Portal;
- la carpeta `-Informacion de proyecto`;
- `01_SCL`;
- `03_DOCS`;
- `05_MANUALES`;
- `06_CONFIG`;
- `07_TEST`.

Las carpetas `02_LADDER`, `04_UML` y `UserFiles` no siempre son obligatorias, pero en la practica agregan mucho valor y conviene incluirlas desde el inicio.
