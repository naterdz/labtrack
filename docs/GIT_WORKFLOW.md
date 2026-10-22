# Flujo Git

`main` conserva las entregas verificadas; `develop` integra las tareas.
Cada tarea nace desde `develop` en su rama `feature/f<fase>-<tarea>-*`, se verifica,
se registra con commit convencional y se integra con `git merge --no-ff`.

## Cierre de fase

1. Verificar pruebas, migración, interfaz, documentación y archivos privados.
2. Registrar el reporte y todos los cambios antes de liberar.
3. Integrar `develop` en `main` con `--no-ff` y crear el tag anotado de fase (`v0.1.0` para F1, `v0.2.0` para F2).
4. Volver a `develop` y actualizarla con `git merge --ff-only main`.
5. Comprobar tag, ramas y árbol limpio. No publicar ni configurar remoto.

El plan original incluye el tag dentro del gate que autoriza crearlo. Se interpreta
como comprobación posterior a la liberación; las pruebas son el gate previo.
Los hashes de tareas anteriores se registran en la siguiente tarea; el hash de
la tarea de cierre se obtiene con `git rev-parse feature/f1-06-qa` o `git rev-parse feature/f2-05-qa`, evitando
la autorreferencia de un commit que intentara contener su propio hash.
Los informes siempre se incluyen en un commit antes de liberar.

Las pruebas que esperan 501 pertenecen al hito F1. Al implementar cada endpoint
en F2 se reemplazan sus expectativas por las del contrato funcional; el tag F1
conserva las pruebas originales. No se omiten pruebas de autenticación.
