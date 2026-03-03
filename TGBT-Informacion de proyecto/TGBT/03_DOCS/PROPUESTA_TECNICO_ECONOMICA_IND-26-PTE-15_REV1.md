# PROPUESTA TECNICO-ECONOMICA

## PROGRAMACION PLC Y HMI TGBT

**Cliente:** Frigorifico El Araucano  
**Contacto:** Jonathan Carrizo  
**Lugar:** Buenos Aires  
**Fecha:** 25/02/2026  
**Oferta:** IND-26-PTE-15-R1  
**Revision:** 1

---

## 1. Objeto de la revision

Se actualiza la propuesta original (Rev. 0) por cambio de alcance en la logica de deslastre:

- **Rev. 0:** deslastre contemplado solo durante operacion con grupos diesel.
- **Rev. 1:** se incorpora deslastre tambien durante operacion con red (sobrecarga de transformador), con histeresis y reenganche automatico.

---

## 2. Propuesta tecnica actualizada

En atencion a la solicitud de actualizacion, se presenta la propuesta tecnico-economica para programacion del sistema de control y supervision, conforme a la ingenieria provista por el cliente.

### 2.1 Programacion PLC

1. Logica de transferencia automatica Red / Grupo Diesel (GD01), con enclavamientos que impiden alimentacion simultanea.
2. Secuencias de arranque/parada del grupo segun condiciones de falta/retorno de red y criterios de estabilidad.
3. Modos de operacion: Automatico y Manual asistido, con validaciones e interlocks de seguridad.
4. Implementacion de prioridades de cargas/tableros (deslastre y restitucion por secuencia, con tiempos y permisos).
5. Manejo de fallas relevantes y condicion segura ante perdidas de senal/comunicacion.
6. **Ampliacion Rev.1:** deslastre reactivo en RED por sobrecarga de transformador, con umbrales parametrizables, filtro temporal, histeresis y reenganche escalonado.

### 2.2 Ingenieria de senales e IO

1. Consolidacion del listado de senales y asignacion de E/S (IO) del PLC.
2. Implementacion de senales de comando, estados y fallas, con validacion funcional.
3. Incorporacion de senales de carga necesarias para habilitar deslastre en RED.

### 2.3 Configuracion e integracion de interruptores por Modbus

1. Parametrizacion y puesta a punto de la comunicacion (direccionamiento, velocidad/ajustes, diagnostico).
2. Mapeo de registros para lectura de estados (abierto/cerrado/disparo/falla) y mediciones disponibles.
3. Implementacion de alarmas por falla de comunicacion y criterios de degradacion segura.
4. Pruebas funcionales de lectura/escritura donde aplique, y validacion de comportamiento en HMI/PLC.

### 2.4 Programacion HMI

1. Pantallas de supervision y comando del sistema (fuentes, interruptores, cargas, estados).
2. Gestion de usuarios con roles y permisos (Operacion / Mantenimiento / Administrador).
3. Visualizacion y reconocimiento de alarmas/eventos.
4. Ajuste de indicadores y diagnosticos para estado de deslastre en RED y GD.

### 2.5 Grupo electrogeno y prevision de segundo GE

1. Analisis de documentacion del GD01 para definir senales minimas, permisos, fallas y criterio de "grupo estable".
2. Arquitectura preparada para futura integracion de un segundo grupo electrogeno (GD02) sin rediseno de la logica base.

---

## 3. Propuesta economica actualizada

### 3.1 Desglose

| ITEM | DESCRIPCION | CANTIDAD | TIPO | PRECIO UNITARIO [USD] | PRECIO SUBTOTAL [USD] |
|---|---|---:|---|---:|---:|
| 1 | Programacion PLC + HMI (alcance Rev.0) | 1 | Gl. | 2000,00 | 2000,00 |
| 2 | Adicional por cambio de alcance: deslastre en RED (logica, parametros, HMI y pruebas) | 1 | Gl. | 400,00 | 400,00 |

**PRECIO TOTAL (SIN IVA): USD 2400,00**  
Son dolares estadounidenses: dos mil cuatrocientos (mas IVA).

**Referencia:** [Gl] Global Ingenieria.

---

## 4. Condiciones comerciales

### 4.1 Validez de la oferta

30 dias corridos a partir de la fecha de cotizacion.

### 4.2 Plazos de entrega

La ejecucion del trabajo se realizara una vez recibidos todos los materiales e informacion necesaria, en un plazo estimado de **25 dias habiles** posteriores a la confirmacion de disponibilidad, en coordinacion con el cliente.

### 4.3 Forma de pago

1. Anticipo del **15%** al inicio de los trabajos: **USD 360,00**.
2. Saldo del **85%** mediante certificaciones parciales segun avance: **USD 2040,00**.
3. Plazo maximo de pago: 30 dias corridos desde la fecha de factura.
4. Pago mediante transferencia bancaria a la cuenta a informar oportunamente.

### 4.4 Precios e impuestos

1. Los montos cotizados son en dolares estadounidenses y no incluyen IVA.
2. No incluyen percepciones ni retenciones impositivas (IIBB, Ganancias u otras), que seran a cargo del cliente segun normativa vigente.
3. Vencida la validez indicada, se debera recotizar.
4. La cotizacion del dolar se tomara segun BNA tipo billete vendedor a la fecha de facturacion.

### 4.5 Facturacion

Las facturas a emitir seran de tipo A.

---

## 5. Documentacion tecnica revisada para esta actualizacion

1. `03_DOCS/ARQUITECTURA_DESLASTRE_V2.md` (deslastre en RED y GD, modo GRID_SHED y umbrales).
2. `03_DOCS/README_SCMTA.md` (alcance funcional SHED V2.0 en modos RED/GD).
3. `07_TEST/TEST_FB_SYSTEM_VALIDATION.scl` (escenarios de validacion de deslastre reactivo en RED).

---

## 6. Exclusiones

No forman parte de la cotizacion:

1. Provision de licencias.
2. Tendido de cables.
3. Tramites municipales, provinciales, nacionales y vialidad.
4. Tramites ante colegio de ingenieros especialistas.
5. Medios de elevacion.
6. Programas de seguridad.
7. Seguros.
8. Cualquier trabajo no expresado en la presente oferta.

---

## 7. Informacion y contactos

**Oficina comercial**  
Cel.: (+54) 9 11 7238-4316 | (+54) 9 11 3653-0246  
Email: indgrade.ing@gmail.com

**Ubicacion**  
Suipacha 946, CABA, Argentina.

**Servicios**  
Ingenieria electrica. Automatizacion y control industrial.  
Gestion de proyectos industriales.  
Industria 4.0 e IoT.  
Sistemas de vision artificial.  
Instrumentacion areas clasificadas.

**Redes**  
Pagina web: https://www.indgrade.com/  
Instagram: indgrade.ing
