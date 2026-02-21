# VALIDACIÓN SCL — TIA PORTAL V18 S7-1200

## RESUMEN EJECUTIVO

**Fecha compilación real**: 20 de febrero de 2026  
**Versión TIA Portal**: V18  
**PLC Target**: Siemens S7-1215C DC/DC/Rly  
**Lenguaje**: SCL (Structured Control Language)  
**Resultado**: **0 errores, 50 warnings**

---

## RESULTADO COMPILACIÓN

### Estado Final

| Tipo | Cantidad | Detalle |
|------|----------|---------|
| **Errores** | **0** | Todos los bloques compilan sin errores |
| **Warnings** | **50** | Variables de DATA_BUFF sin asignar (esperado hasta mapeo %I/%Q) |

Los 50 warnings corresponden a campos de DATA_BUFF que todavía no tienen asignación física de I/O. Esto es normal y esperado — se resolverán durante el mapeo %I/%Q en la etapa de comisionamiento.

---

## PROCESO DE IMPORTACIÓN VALIDADO

### Orden de importación (verificado)

```
1. 08_DB_GLOBAL_STATUS.scl  → genera DATA_BUFF (DB global)
2. 09_DB_PARAMS.scl         → genera DB_PARAMS (DB parámetros)
3. 01_FB_IO_NORMALIZE.scl   → FB normalización DI
4. 02_FB_SCMTA.scl          → FB máquina estados (21 estados)
5. 03_FB_SHED.scl            → FB deslastre (19 feeders, 6 modos)
6. 04_FB_CMD_ARBITER.scl    → FB arbitración comandos
7. 05_FB_OUTPUTS.scl        → FB salidas pilotos + HMI
8. 06_FB_MODBUS_MANAGER.scl → FB scheduler Modbus
9. 07_FB_MTZ_DRIVER.scl     → FB driver Modbus MTZ
10. 11_INSTANCE_DBS.scl      → 6 Instance DBs para FB 03-07
11. 10_OB1_MAIN.scl          → copiar contenido a OB1 Main existente
```

### Procedimiento exacto en TIA Portal V18

1. **Crear proyecto** → Agregar CPU S7-1215C DC/DC/Rly
2. Menú **External sources** → Add new external file
3. Importar archivos `.scl` en orden listado arriba
4. Click derecho sobre cada fuente → **Generate blocks from source**
5. Para OB1: copiar contenido SCL al bloque Main (OB1) existente
6. **Compilar** proyecto completo

---

## LECCIONES APRENDIDAS EN LA IMPORTACIÓN

### 1. Encoding: UTF-8 con BOM obligatorio

TIA Portal V18 **requiere** archivos SCL con encoding **UTF-8 con BOM** (Byte Order Mark). Sin BOM, los caracteres especiales (ñ, á, é, etc.) en comentarios causan errores de parsing.

**Solución PowerShell para convertir:**
```powershell
$files = Get-ChildItem -Path "01_SCL" -Filter "*.scl"
foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8
    [System.IO.File]::WriteAllText($f.FullName, $content, [System.Text.UTF8Encoding]::new($true))
}
```

### 2. DB_PARAMS: NON_RETAIN, no RETAIN

El DB de parámetros usa `NON_RETAIN` en lugar de `RETAIN`. Esto significa que los parámetros se inicializan a sus valores por defecto en cada arranque del PLC. La configuración persistente se maneja desde HMI.

**Formato correcto:**
```scl
DATA_BLOCK "DB_PARAMS"
{ S7_Optimized_Access := 'FALSE' }
VERSION : 0.1
NON_RETAIN
   VAR
      V_NOM : Real := 380.0;
      // ...
   END_VAR
BEGIN
END_DATA_BLOCK
```

> **Nota:** DB_PARAMS usa `S7_Optimized_Access := 'FALSE'` para permitir acceso simbólico desde HMI.

### 3. DATA_BUFF: Estructura VAR con NON_RETAIN

DATA_BUFF (DB global compartido) usa la estructura `VAR ... END_VAR` dentro del DATA_BLOCK, no `STRUCT`:

```scl
DATA_BLOCK "DATA_BUFF"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
NON_RETAIN
   VAR
      MODE_AUTO : Bool;
      QT1_STATE : Int;
      // ...
   END_VAR
BEGIN
END_DATA_BLOCK
```

### 4. Instance DBs: archivo separado necesario

Los FBs que se llaman desde OB1 necesitan Instance DBs explícitos. Estos se proporcionan en `11_INSTANCE_DBS.scl` que contiene 6 instancias:

| Instance DB | FB asociado |
|------------|-------------|
| 03_FB_SHED_DB | 03_FB_SHED |
| 04_FB_CMD_ARBITER_DB | 04_FB_CMD_ARBITER |
| 05_FB_OUTPUTS_DB | 05_FB_OUTPUTS |
| 07_FB_MTZ_DRIVER_DB_QT1 | 07_FB_MTZ_DRIVER |
| 07_FB_MTZ_DRIVER_DB_QG1 | 07_FB_MTZ_DRIVER |
| 07_FB_MTZ_DRIVER_DB_QG2 | 07_FB_MTZ_DRIVER |

> **Nota:** FB_IO_NORMALIZE y FB_SCMTA usan instancias locales en OB1 (no necesitan Instance DB separado). FB_MTZ_DRIVER tiene 3 instancias (una por interruptor ACB).

### 5. OB1 no se importa como external source

OB1 (Main) ya existe como bloque del sistema. El código SCL de `10_OB1_MAIN.scl` debe **copiarse** al bloque Main existente, no importarse como fuente externa.

### 6. TON_TIME con pragmas (timers en FBs)

Los FBs exportados de TIA Portal usan `TON_TIME` con pragmas de instrucción:
```scl
tonStateTimer {InstructionName := 'TON_TIME'; LibVersion := '1.0'; S7_SetPoint := 'False'} : TON_TIME;
```

Esto es equivalente a `TON` pero usa el tipo `Time` nativo. El código actual mantiene esta convención para compatibilidad con TIA export/import.

---

## BLOQUES VALIDADOS

### Function Blocks (7)

| Bloque | Versión | Estados/Modos | Arrays | Resultado |
|--------|---------|---------------|--------|-----------|
| 01_FB_IO_NORMALIZE | 2.0 | — | [1..19] feeders | ✅ Compila OK |
| 02_FB_SCMTA | 3.0 | 21 estados | — | ✅ Compila OK |
| 03_FB_SHED | 2.0 | 6 modos | [1..19] feeders | ✅ Compila OK |
| 04_FB_CMD_ARBITER | 2.0 | — | [1..19] feeders | ✅ Compila OK |
| 05_FB_OUTPUTS | 3.0 | — | [1..19] feeders | ✅ Compila OK |
| 06_FB_MODBUS_MANAGER | 0.1 | 4 estados | — | ✅ Compila OK |
| 07_FB_MTZ_DRIVER | 1.1 | 7 estados | — | ✅ Compila OK |

### Data Blocks (2)

| Bloque | Tipo | Optimized | RETAIN | Resultado |
|--------|------|-----------|--------|-----------|
| DATA_BUFF | DB global | TRUE | NON_RETAIN | ✅ Compila OK |
| DB_PARAMS | DB parámetros | FALSE | NON_RETAIN | ✅ Compila OK |

### Instance DBs (6)

Todos compilan OK con formato `NON_RETAIN` + `S7_Optimized_Access := 'TRUE'`.

### OB1 Main

Compila OK después de copiar código SCL al bloque Main existente.

---

## MÉTRICAS ACTUALIZADAS

| Métrica | Valor |
|---------|-------|
| Function Blocks | 7 |
| Data Blocks globales | 2 (DATA_BUFF + DB_PARAMS) |
| Instance DBs | 6 |
| Organization Blocks | 1 (OB1 Main) |
| **Total bloques** | **16** |
| Estados SCMTA | **21** (0-14 GD1 + 15-20 GD2) |
| Estados MTZ_DRIVER | 7 |
| Modos SHED | 6 |
| Feeders gestionados | **19** (Array[1..19]) |
| Timers TON_TIME | ~25 |
| Pilotos DO totales | 74 (4 sistema + 12 ACB + 57 feeders + 1 baliza) |

---

## TEST FBs DISPONIBLES

5 test FBs preparados para importar a TIA Portal y ejecutar en PLCSIM:

| Test FB | Pasos | Cobertura |
|---------|-------|-----------|
| FB_TEST_SCMTA | 15 | Happy path RED→GD1→RED |
| FB_TEST_FALLAS_SCMTA | 37 | Timeouts, fallas GD, grid intermitente, LOCAL |
| FB_TEST_SHED | 20 | Deslastre dual RED/GD, 19 feeders |
| FB_TEST_GD2_FAILOVER | 25 | Failover GD1↔GD2 completo |
| FB_TEST_SYSTEM_VALIDATION | 50 | Integración 5 FBs, happy + fault path |

Los tests usan instancias locales de los FBs de producción y no requieren acceso a hardware. Se importan igual que los FBs de producción, con sus propios Instance DBs (`07_TEST/12_TEST_INSTANCE_DBS.scl`).

---

## CONCLUSIÓN

El código SCL compila exitosamente en TIA Portal V18 para S7-1215C con **0 errores y 50 warnings** (todos esperados). Los warnings se resolverán durante la etapa de mapeo I/O y comisionamiento.

**Próximos pasos:**
1. Ejecutar tests en PLCSIM
2. Mapear %I/%Q a módulos físicos
3. Completar FB_MODBUS_MANAGER
4. Testing en hardware real

---

*Documento actualizado: 21 de febrero de 2026 — Resultado de compilación real en TIA Portal V18*
