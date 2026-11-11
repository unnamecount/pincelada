# Pincelada

App de dibujo y pintura para tablet, móvil y ordenador: 27 pinceles (lápices, tinta, acuarela que mezcla colores, óleo…), gomas, rueda de color, paletas sin límite, capas, fotos, texto y modo 3D.

**Abrir e instalar:** https://unnamecount.github.io/pincelada/

- **Android / Chrome / Edge:** abre el enlace y pulsa «Instalar Pincelada» (o «Instalar app» en el menú del navegador).
- **iPad / iPhone (Safari):** botón Compartir → «Añadir a pantalla de inicio».

Una vez instalada funciona sin internet. Los dibujos se guardan en el propio aparato; desde «Mis obras» se puede guardar y restaurar una copia de seguridad.

## Cómo se actualiza

La app instalada comprueba sola si hay versión nueva y muestra un aviso con el botón **Actualizar** (guarda la obra abierta antes de recargar). No hace falta volver a instalarla.

Para publicar una versión:

1. Cambia `pincelada.html` (es la fuente; también es el artefacto de Claude).
2. Añade una entrada **arriba** en `cambios.json` con la versión nueva y sus novedades.
3. `python build.py` → genera `index.html`, `sw.js` y `version.json`.
4. `git add -A && git commit -m "..." && git push`. GitHub Pages la publica en uno o dos minutos.

`iconos.py` vuelve a dibujar los iconos si hace falta.
