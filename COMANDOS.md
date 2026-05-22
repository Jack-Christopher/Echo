# Echo — comandos de voz (frases exactas)

Mantén **Win+Espacio** (o el círculo azul) **pulsado**, di la frase, suelta. Mira la **ventana de terminal** donde lanzaste Echo.

## Arrancar Echo

```powershell
cd C:\Users\User\OneDrive\Desktop\Echo
.\run_echo.bat
```

## Qué verás en la terminal

Ejemplo al decir *abre youtube*:

```
[Echo] Escuchando... (mantén pulsado y habla)
[Echo] Procesando audio...
[Echo] Transcribiendo: C:\Users\...\tmpXXXX.wav
[Echo] Texto entendido: "abre youtube"
[Echo] Comando normalizado: "abre youtube"
[Echo] Intent: open_website
[Echo] Resultado: Abriendo youtube (ok)
```

- **Texto entendido** = lo que Whisper oyó (sin editar).
- **Comando normalizado** = texto tras quitar acentos/rellenos (para comparar con la tabla).
- Si no coincide con ningún patrón: `Intent: unknown` y `No entendi`.

---

## Navegador

En **Configuracion** (bandeja o clic derecho en el círculo azul) elige:

| Opción | Ejecutable típico |
|--------|-------------------|
| Brave | `brave.exe` |
| Google Chrome | `chrome.exe` |
| Microsoft Edge | `msedge.exe` |
| Mozilla Firefox | `firefox.exe` |
| Opera | `opera.exe` |
| Opera GX | `opera.exe` (carpeta Opera GX) |

Campo **Ruta al .exe**: solo si no se detecta solo (ej. `C:\Program Files\Google\Chrome\Application\chrome.exe`).

### Cómo Echo abre pestañas

1. **Nueva pestaña por línea de comandos** (lo principal):
   - Chromium (Brave, Chrome, Edge, Opera): `navegador.exe --new-tab https://...`
   - Firefox: `firefox.exe -new-tab https://...`
   - Si el navegador ya está abierto, Windows suele reutilizar la ventana y añadir la pestaña.

2. **Búsquedas** (`busca ...`): enfoca el navegador y usa **Ctrl+L** (barra de direcciones), escribe y Enter.

3. **Reserva** si falla lo anterior: **Ctrl+T** (nueva pestaña vacía), escribe la URL y Enter.

---

## Sitios web

Alias por defecto en `echo/config/defaults.json`: `youtube`, `whatsapp`, `gmail`.

| Di exactamente (o muy parecido) | Acción |
|--------------------------------|--------|
| `abre youtube` | Abre YouTube |
| `abre whatsapp` | Abre WhatsApp Web |
| `abre gmail` | Abre Gmail |
| `abrir youtube` | Igual (variante) |
| `quiero youtube` | Igual |
| `pon youtube` | Igual |
| `ve a youtube` | Igual |
| `ir a gmail` | Igual |

Puedes añadir más sitios en **Configuracion** (bandeja o clic derecho en el círculo). Luego funcionan como `abre <alias>`.

---

## Buscar en la web (rutas configurables)

Tras `busca ...` Echo elige destino según **Sitios custom** + **Rutas generales** (Configuracion → **Busquedas**). En terminal: `Ruta: ... -> URL`.

| Di exactamente | Ruta por defecto |
|----------------|------------------|
| `busca pelicula matrix` | Google: `matrix site:m.ok.ru` |
| `busca serie avatar` | Google: `avatar site:m.ok.ru` |
| `busca serie breaking bad` | Google: `serie breaking bad site:m.ok.ru` |
| `busca cuevana matrix` | Cuevana: `cuevanapro.org/search?s=matrix` |
| `busca tutorial soldar` | YouTube |
| `busca recetas pollo` | Google (recetas) |
| `busca gemini que es python` | Gemini |
| `busca clima madrid` | Google (fallback) |

### Sitios custom (`custom_site_searches`)

Para OK.ru y sitios similares usa **`resolve_mode": "site"`** + **`site_domain": "m.ok.ru"`** → busqueda en el motor por defecto con `texto site:m.ok.ru` al final.

Para sitios con URL propia (Cuevana, etc.):

```json
{
  "id": "cuevana",
  "resolve_mode": "template",
  "template": "https://cuevanapro.org/search?s={query}",
  "terms": ["cuevana"],
  "match": "leading",
  "priority": 158
}
```

### Tipos de regla (`match`)

| match | Uso |
|-------|-----|
| `leading` | Empieza por: `pelicula`, `cuevana`, `receta`… |
| `exact` | Frase completa: `serie breaking bad` |
| `contains` | Contiene el termino |
| `fallback` | Si nada mas coincide |

| resolve_mode | Uso |
|--------------|-----|
| `site` | `{query} site:dominio` en `search_engine_template` |
| `template` | URL directa con `{query}` |

### Enlaces y protocolos (`link_handlers` + Sitios)

Cada sitio puede definir **opener**:

```json
"gemini": { "url": "https://gemini.google.com/app", "opener": "browser" },
"ftp_ejemplo": { "url": "ftp://servidor/carpeta", "opener": "browser" }
```

`link_handlers` define por protocolo: `http`, `https`, `ftp`, `mailto` → `browser` (navegador elegido), `shell` (app por defecto de Windows), o `custom` + ruta a un `.exe`.

---

## Reproductor / pestaña activa (teclas multimedia)

| Di exactamente | Acción |
|----------------|--------|
| `pausa` | Pausar |
| `reproducir` | Reproducir |
| `siguiente` | Siguiente pista |
| `siguiente video` | Siguiente |
| `anterior` | Anterior |
| `silencio` | Silenciar |
| `desilenciar` | Quitar silencio |

---

## Volumen y brillo

| Di exactamente | Acción |
|----------------|--------|
| `sube volumen` | Sube volumen |
| `baja volumen` | Baja volumen |
| `sube brillo` | Sube brillo |
| `baja brillo` | Baja brillo |
| `volumen` | Sube volumen (sin verbo = sube) |
| `brillo` | Sube brillo |
| `aumenta volumen` | Sube volumen |
| `reduce brillo` | Baja brillo |

---

## Carpetas de Windows

| Di exactamente | Acción |
|----------------|--------|
| `abre descargas` | Abre Descargas |
| `abre documentos` | Abre Documentos |
| `abre downloads` | Descargas (inglés) |

---

## Dictado (escribe lo que digas)

| Di exactamente | Acción |
|----------------|--------|
| `iniciar dictado` | Modo dictado ON |
| `empezar dictado` | Igual |
| `activar dictado` | Igual |
| `terminar dictado` | Modo dictado OFF |
| `finalizar dictado` | Igual |
| `parar dictado` | Igual |

Con dictado activo, **cualquier otra frase** se escribe como texto (no ejecuta comandos), salvo las frases de *terminar dictado*.

---

## Rutinas

| Di exactamente | Acción |
|----------------|--------|
| `modo noche` | Brillo bajo, volumen bajo, abre YouTube relax (rutina por defecto) |
| `rutina noche` | Igual |
| `activar noche` | Igual |

Otras rutinas solo si las defines en `config.json` → `routines`.

---

## Varios comandos seguidos

Separa con **y**, **luego** o **entonces**:

| Di exactamente | Acción |
|----------------|--------|
| `abre youtube y pausa` | Abre YouTube y envía pausa |
| `sube volumen luego abre gmail` | Dos pasos en orden |

Si una parte no se entiende, falla toda la cadena.

---

## Precision del reconocimiento de voz

En **Configuracion → Voz**:

| Opcion | Recomendacion |
|--------|----------------|
| **Modelo Whisper** | **Small** (mucho mejor que Base). Al **Guardar**, Echo descarga el modelo si falta (sin `setup.ps1` manual). |
| **Beam size** | **8** (mas precision, un poco mas lento). |
| **Pista de comandos** | **Si** — sesga Whisper hacia frases como *abre youtube*, *busca*, etc. |

Echo tambien **normaliza el audio** (quita silencios al inicio/fin y sube volumen) antes de transcribir.

### Consejos al hablar

1. **1–2 segundos** minimo, cerca del micro, sin musica de fondo fuerte.
2. Mira **Texto entendido** en la terminal; si falla, repite mas despacio.
3. Ruido o mic lejos → transcripcion vacia o texto incorrecto.
4. Umbral fuzzy **85**: frases parecidas a las de la tabla aun pueden ejecutarse (p. ej. *abre yutub*).

---

## Salir de Echo

- Clic derecho en el **círculo azul** → **Salir**
- O bandeja del sistema → **Salir**
