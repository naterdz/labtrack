# Comprobación de UI · F2

Estado actual: **NOT_RUN por bloqueo del entorno**. La ejecución real de
`.venv/bin/python scripts/verify_browser.py` falla al crear el socket temporal
con `PermissionError: [Errno 1] Operation not permitted`. Tampoco hay Chromium/
Playwright instalado; registry.npmjs.org no se resuelve desde este aislamiento.
No se reutilizan las capturas ni los resultados históricos de F1 como prueba de F2.

## Ejecución automática pendiente

En un entorno con loopback habilitado, Node y Playwright/Chromium:

```bash
npm install --prefix .tools/browser playwright
./.tools/browser/node_modules/.bin/playwright install chromium
PLAYWRIGHT_MODULE="$PWD/.tools/browser/node_modules/playwright" .venv/bin/python scripts/verify_browser.py
```

El script usa SQLite temporal migrada y un servidor en puerto libre; no toca
la base local. `scripts/smoke_browser.cjs` ahora comprueba registro, login,
creación de proyecto y experimento, filtro por modelo (con y sin coincidencias),
edición, recarga, 409 al borrar proyecto con hijos, cancelación y confirmación
de borrados, conteos y logout. Genera capturas de escritorio y móvil y reporte
en `artifacts/`. Debe completarse y revisarse visualmente antes de liberar F2.

## Revisión manual pendiente

1. Registrar cuenta y entrar. Ver cero proyectos/experimentos.
2. Crear proyecto con descripción y seleccionarlo.
3. Crear experimento con dataset, modelo, notas y una métrica como 42.5.
4. Filtrar por modelo sin distinguir mayúsculas; probar búsqueda y sin coincidencias.
5. Editar proyecto y experimento; recargar y comprobar persistencia.
6. Intentar eliminar proyecto con experimento: mostrar HTTP 409 y conservar datos.
7. Cancelar eliminación; después confirmar borrado de experimento y proyecto.
8. Comprobar conteos y logout; recargar sin sesión.
9. Repetir con teclado y pantallas de 1366, 390 y 320 px; revisar foco de diálogos,
   labels, texto largo y scroll interno de tabla. Los nombres deben verse como texto.

Las pruebas de API y la revisión de sintaxis JavaScript no sustituyen esta revisión.
