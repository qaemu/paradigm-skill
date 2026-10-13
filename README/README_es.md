<div align="center">

<img alt="PARADIGMA: mapeá cómo cambiaron las restricciones de un campo en dos décadas y encontrá lo que acaba de volverse posible" src="../assets/banner.svg" width="100%">

<br>

**Una skill para agentes que mapea cómo cambiaron las restricciones de un campo en dos décadas,<br>para encontrar dónde acaba de volverse posible un nuevo producto, emprendimiento o línea de investigación.**

[English](../README.md) | **Español** | [简体中文](README_cn.md)


[Inicio rápido](#inicio-rápido) · [Por qué](#por-qué-restricciones) · [Cómo funciona](#cómo-funciona) · [Qué obtenés](#qué-obtenés) · [Instalación](#instalación) · [Uso](#uso) · [Modelos](#con-qué-modelo-usarlo) · [La matemática](#la-matemática) · [Límites](#límites) · [Preguntas](#preguntas-frecuentes)

</div>

---

## Inicio rápido

```bash
npx skills add qaemu/paradigm-skill
```

Después, en tu agente:

```text
/paradigma mantenimiento industrial
```

Más o menos una hora después tenés un informe con fuentes y una planilla de datos: qué restricciones del mantenimiento industrial cayeron, cuáles se están endureciendo, quién construye sobre cada una y dónde están los huecos.

> [!NOTE]
> PARADIGMA te da un mapa, no una predicción. Muestra dónde se movieron las restricciones y quién lo notó. Decidir cuándo actuar, y sobre qué, sigue siendo trabajo tuyo.

## Por qué restricciones

Los grandes cambios casi nunca son ideas que nadie tuvo antes. El dinero digital se intentó durante veinte años antes de Bitcoin. Las redes neuronales existieron durante décadas antes de que las GPU baratas y los grandes conjuntos de datos las hicieran funcionar. Lo que suele cambiar está debajo: algo se vuelve 10× más barato, vence una patente, entra en vigencia una ley, una habilidad deja de ser escasa, cambia una norma social. Un supuesto que toda la industria da por fijo deja de ser cierto.

Esos cambios suelen ser públicos, así que seguirlos por sí solo no da ventaja. La ventaja aparece al compararlos con quién está construyendo realmente sobre ellos. PARADIGMA hace esa comparación para cualquier campo que le indiques.

| Es | No es |
|---|---|
| Un panorama con fuentes de lo que cambió en un campo | Un generador de ideas |
| Tendencias robustas calculadas en código, con notas de confianza | Números estimados en prosa |
| Un mapa de quién construye sobre cada cambio y hasta dónde llegó | Una lista de startups de moda |
| Explícito sobre los huecos en sus propios datos | Un reemplazo de tu criterio |

## Cómo funciona

<img alt="Ocho pasos: mapear el campo, curvas de precio, barrido no económico, escaneo de actividad, matriz de huecos, chequeo de por qué no, verificación independiente, informe" src="../assets/pipeline.svg" width="100%">

| Paso | Qué pasa |
|---|---|
| **1. Mapear el campo** | Divide el campo en 12–25 restricciones: componentes, fabricación, software e IA, datos, mano de obra, distribución, cumplimiento normativo, confianza. Después un barrido PESTEL capta las políticas, económicas, sociales, tecnológicas, ambientales y legales. |
| **2. Curvas de precio** | Agentes auxiliares reúnen datos históricos en paralelo, cada uno con su enlace. El motor toma la mediana de cada año, quita la inflación y ajusta una tendencia robusta que un valor erróneo no puede mover. |
| **3. Barrido no económico** | Boletines oficiales, organismos de normas, patentes que vencen ahora, estadísticas de salarios y escasez, encuestas de adopción, controles de exportación. Cada cambio queda fechado y marcado como aflojando o endureciendo. |
| **4. Escaneo de actividad** | Cuenta empresas, financiamiento, patentes, papers y lanzamientos por restricción, con las mismas búsquedas para todas. Cada empresa queda marcada como `announced` (anunciada), `deployed` (desplegada) o `paying` (con clientes que pagan), con evidencia. |
| **5. Matriz de huecos** | Grafica cuánto cayó cada restricción frente a cuántos construyen sobre ella. |
| **6. Chequeo de por qué no** | Antes de llamar oportunidad a un hueco, busca intentos fallidos y bloqueos que siguen en pie. |
| **7. Verificación independiente** | Un agente nuevo, que no hizo la investigación, vuelve a abrir las fuentes y revisa cada valor. El informe indica la tasa de aprobación. |
| **8. Informe** | Un panorama de una página, una ficha por restricción, una línea de tiempo de cambios con fecha, un mapa de empresas y una planilla con cada dato y su enlace. |

### Reglas que no rompe

1. **Sin fuente, no hay número.** Lo que no se encuentra se informa como faltante, nunca se estima.
2. **Toda la matemática corre en el motor** ([`paradigma.py`](../skills/paradigma/scripts/paradigma.py)), no en la prosa del modelo.
3. **Una ronda de inversión no es tracción.** Cada empresa lleva un estado y la evidencia que lo respalda.
4. **Nada se llama espacio en blanco hasta que pasó el chequeo de por qué no.**
5. **La investigación la verifica un agente que no la hizo.**

## Qué obtenés

<div align="center">
<img alt="Matriz de huecos con cuatro cuadrantes: espacio en blanco, saturado, dormido, riesgo de hype" src="../assets/gap-matrix.svg" width="78%">
<br>
<sub>Ilustración de la matriz de huecos. Una corrida real grafica las restricciones de tu campo.</sub>
</div>

<br>

| Cuadrante | Significado | Qué hace el informe |
|---|---|---|
| **Espacio en blanco** (White space) | La restricción cayó mucho y pocos construyen sobre ella | Corre el chequeo de por qué no y clasifica cada caso como *no intentado*, *intentado demasiado temprano* (con las empresas que fallaron y las fechas) o *bloqueado* |
| **Saturado** (Crowded) | Cayó mucho y muchos construyen | Lista las empresas y hasta dónde llegó cada una. Es el panorama de consenso |
| **Riesgo de hype** (Hype risk) | Cambió poco, pero muchos construyen igual | Lo señala explícitamente |
| **Dormido** (Dormant) | Poco cambio y poca actividad | Queda como referencia |

**Entregables**

- **Informe.** Primero el panorama: las mayores caídas, las restricciones que se endurecen, los espacios en blanco, las zonas saturadas, los riesgos de hype y los cambios con fecha en los próximos 1–5 años, como leyes que entran en vigencia y patentes que vencen. Después, una ficha por restricción con su curva, el cambio anual y su margen de error, cuántas veces cambió, la forma de la tendencia, la nota, los umbrales, las empresas y la etiqueta de por qué no. Termina con método, confianza y fuentes.
- **Planilla.** `constraints`, `points`, `periods`, `curves`, `noncost`, `companies`, `activity`, `gap_matrix`, `whynot` y `verification`. Cada fila tiene su enlace a la fuente.
- **Gráficos.** Una curva en escala logarítmica por restricción, más la matriz de huecos.

## Instalación

PARADIGMA sigue el formato abierto [Agent Skills](https://agentskills.io): un `SKILL.md` más un motor en Python. Cualquier agente que pueda navegar la web, correr Python e, idealmente, lanzar agentes auxiliares puede usarlo.

### Cualquier agente (skills CLI)

```bash
npx skills add qaemu/paradigm-skill                    # proyecto actual
npx skills add qaemu/paradigm-skill -g                 # todos los proyectos
npx skills add qaemu/paradigm-skill -a claude-code -a opencode
```

Usa la [skills CLI](https://github.com/vercel-labs/skills), compatible con Claude Code, OpenCode, Codex, Cursor y muchos más.

### Claude Code

Como plugin, que te da actualizaciones a través de `/plugin`:

```text
/plugin marketplace add qaemu/paradigm-skill
/plugin install paradigma@paradigma
```

Las skills de plugins llevan prefijo, así que se ejecuta como `/paradigma:paradigma <campo>`.

O como skill personal, que se ejecuta como `/paradigma <campo>`:

```bash
git clone https://github.com/qaemu/paradigm-skill.git
mkdir -p ~/.claude/skills && cp -r paradigm-skill/skills/paradigma ~/.claude/skills/
```

### Apps de Claude (web, escritorio, móvil)

1. Descargá [`dist/paradigma.zip`](../dist/paradigma.zip). Contiene la carpeta `paradigma` con el `SKILL.md` y el motor.
2. Activá **Code execution and file creation** en **Settings → Capabilities**.
3. Andá a **Customize → Skills**, hacé clic en **+**, después **Create skill → Upload a skill**, y elegí el ZIP.

Guía de Anthropic: [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

### OpenCode

```bash
git clone https://github.com/qaemu/paradigm-skill.git
mkdir -p ~/.config/opencode/skills && cp -r paradigm-skill/skills/paradigma ~/.config/opencode/skills/
```

OpenCode también lee `~/.claude/skills/`, así que una instalación de Claude Code funciona ahí también. Primero comprobá que la búsqueda web funcione con tu proveedor. Sin ella, PARADIGMA no puede reunir datos.

### Requisitos

| Necesita | Para qué |
|---|---|
| Búsqueda web y lectura de páginas | Cada número sale de una fuente |
| Python 3.10+ con `pandas`, `numpy`, `matplotlib` (`scipy` opcional) | El motor de análisis |
| Agentes auxiliares (opcional) | Investigación en paralelo y la verificación independiente. Sin ellos trabaja paso a paso y marca la verificación como autoverificada |
| `OPENALEX_API_KEY` (opcional, [gratis](https://openalex.org)) | Conteo de papers cuando se agota la cuota gratuita compartida. Sin ella esas columnas quedan vacías y el informe lo dice |

## Uso

```text
/paradigma <campo> [región] [ventana] [standard|deep]
```

| Argumento | Por defecto | Notas |
|---|---|---|
| `campo` | obligatorio | Si es muy amplio, como *hardware* o *salud*, PARADIGMA primero sugiere 3–4 subcampos más acotados. Los campos acotados dan resultados mucho mejores |
| `región` | global | Indica dónde los datos están centrados en EE. UU. o la UE |
| `ventana` | 20 años hasta el último año completo | |
| profundidad | `standard` | `standard` cubre 12–25 restricciones. `deep` cubre hasta 40, con curvas más densas y chequeo de por qué no en cada candidato |

```text
/paradigma maquinaria agrícola
/paradigma fabricación en lotes pequeños América Latina
/paradigma instrumental de laboratorio 2010-2025 deep
```

> [!IMPORTANT]
> Una corrida estándar lleva alrededor de una hora, con varios agentes trabajando en paralelo, y consume una parte importante del uso de un plan. `deep` tarda más. Elegí el campo antes de empezar.

## Con qué modelo usarlo

Lo que importa en esta tarea es la confiabilidad en tareas largas y la disciplina con las fuentes. Un modelo rápido que llena una tabla con números verosímiles es justamente la falla a evitar.

| Rol | Recomendado | Esfuerzo |
|---|---|---|
| Corrida principal (planificación, matriz de huecos, por qué no, informe) | Claude Opus 5.5 | high |
| Agentes de recolección de datos | Claude Sonnet 5.5 | medium–high |
| Verificación independiente | Opus 5.5, o Claude Fable 5.1 para corridas `deep` | high |

Evitá los modelos chicos y "flash" para la corrida principal. Para probar cualquier modelo, incluidos los gratuitos, hacelo correr con 3 restricciones de datos bien publicados, como precios de packs de baterías de ion-litio y de módulos solares, y abrí cada enlace que devuelva. **Si inventa aunque sea un enlace o un número, no pasa.**

## La matemática

<details>
<summary><b>Cómo se calculan las curvas</b></summary>

<br>

1. **Normalizar.** Los valores se expresan por unidad de prestación ($/kWh, $ por canal de sensor, $/kg de carga útil). Los valores en USD se pasan a dólares constantes con el IPC de EE. UU. de FRED. Los valores en otras monedas necesitan un tipo de cambio citado; si no, se rechazan.
2. **Agrupar.** Los datos se agrupan por año, o por trimestre cuando hay suficiente densidad: al menos 3 puntos en al menos el 60% de los trimestres, y al menos 8 trimestres. Cada período guarda su mediana, su rango intercuartil y su cantidad, y se marcan los períodos con menos de 3 puntos.
3. **Ajustar.** Se ajusta una recta de Theil–Sen sobre el log₁₀ de las medianas de cada período, así cada período tiene un voto y los valores atípicos casi no la mueven. La pendiente da el cambio porcentual anual con un intervalo de confianza del 95%. El motor nunca informa como tendencia el porcentaje entre el primer y el último punto.
4. **Forma.** Se comparan los últimos 5 años con toda la ventana para clasificar la tendencia como acelerando, estable o desacelerando.
5. **Clasificar.** Cada curva queda como *mejoró ≥10×*, *mejorando*, *plana / incierta* o *empeorando (la restricción se endurece)*. La dirección depende de si para esa métrica es mejor más bajo o más alto.
6. **Nota.**

| Nota | Requiere |
|---|---|
| A | ≥ 8 períodos, ≥ 3 fuentes independientes, ≤ 20% de períodos flojos, intervalo de confianza estrecho |
| B | ≥ 5 períodos, ≥ 2 fuentes |
| C | utilizable pero débil. No alcanza para una afirmación principal |
| D | menos de 3 períodos. No se calcula tendencia |

</details>

<details>
<summary><b>Cómo se puntúa la matriz de huecos</b></summary>

<br>

- **Puntaje de caída.** El percentil de la mejora por década de cada restricción (log₁₀ de cuántas veces cambió). Las restricciones no económicas se puntúan de 0 a 3 según la evidencia, con una justificación escrita. Cruzar un umbral de viabilidad suma un bonus.
- **Puntaje de actividad.** El promedio de los percentiles, en escala logarítmica, de empresas, financiamiento, patentes, lanzamientos y avisos de empleo disponibles. Las señales que faltan se omiten, no se cuentan como cero.
- **Investigación adelantada a las empresas.** Papers de los últimos 3 años divididos por (empresas + 1). Cuando la investigación va muy adelante de las empresas, sube el puntaje de hueco.
- **Puntaje de hueco** = puntaje de caída × (1 − puntaje de actividad), ponderado por la investigación adelantada. Los cuadrantes se dividen en la mediana.

Estos puntajes son relativos. Ordenan las restricciones de un campo entre sí, no contra una escala absoluta.

</details>

<details>
<summary><b>Correr el motor por separado</b></summary>

<br>

```bash
cd skills/paradigma/scripts
python3 paradigma.py cpi                  # promedios anuales del IPC de EE. UU. desde FRED
python3 paradigma.py curves --plots       # points.csv -> curves.csv, periods.csv, plots/
python3 paradigma.py papers --start 2005 --end 2025   # conteo de papers en OpenAlex
python3 paradigma.py gap --plots          # curvas + actividad -> gap_matrix.csv, plots/gap_matrix.png
```

Los esquemas de los CSV están en [`SKILL.md`, Appendix B](../skills/paradigma/SKILL.md#appendix-b-csv-schemas).

</details>

## Fuentes de datos

Todas las fuentes que usa PARADIGMA son gratuitas. El informe indica dónde agregarían más las bases de datos pagas.

| Necesidad | Usado por PARADIGMA (gratis) | Lo que suman los profesionales (pago) |
|---|---|---|
| Curvas de costo | Our World in Data, Santa Fe Performance Curve Database, BLS / FRED, USGS, NREL, IEA, listas de precios + Wayback Machine | BloombergNEF, firmas de desarme técnico (teardown) |
| Empresas y financiamiento | Comunicados de prensa, páginas gratuitas de Crunchbase / Dealroom, directorios de startups | PitchBook, CB Insights, Crunchbase Pro |
| Patentes | Google Patents, Lens.org | PatSnap, Derwent |
| Papers científicos | OpenAlex | Scopus, Web of Science |
| Regulación | Boletines oficiales (Federal Register, EUR-Lex, boletines nacionales), ISO / IEC / SAE | Servicios de seguimiento legal |

## Límites

- **Los datos de financiamiento son la señal más débil.** Las fuentes gratuitas no captan rondas no divulgadas ni muchas empresas fuera de EE. UU.
- **Las estadísticas se inclinan a EE. UU. y la UE.** El informe señala el sesgo regional.
- **Llegar demasiado temprano se ve igual que equivocarse.** Las caídas de menos de 3 años se marcan como *tempranas*.
- **La actividad especulativa no es adopción.** El informe separa el hype de los usuarios con una necesidad real.
- **Estado: v0.1, experimental.** El motor pasa un conjunto de pruebas sin conexión con datos sintéticos de respuesta conocida. Todavía no se publicó una corrida real completa. La primera se agregará a `examples/`.

## Preguntas frecuentes

**¿Toca mis archivos o cuentas?**
No. Lee sitios web públicos y escribe solo en su propia carpeta de trabajo. No inicia sesión en ningún lado.

**¿Por qué no pedirle directamente a un modelo un informe de mercado?**
Porque te va a dar uno, con números incluidos, y no vas a poder saber cuáles inventó. PARADIGMA exige una fuente para cada número, hace la matemática en código y hace que otro agente revise el trabajo.

**¿Puedo usarlo con un modelo gratuito?**
Sí, si el modelo pasa la prueba de [Con qué modelo usarlo](#con-qué-modelo-usarlo). Revisá antes la política de datos de cada proveedor, porque algunos modelos gratuitos entrenan con tus prompts.

**¿En qué se diferencia de un informe de mercado de una consultora?**
Un informe de mercado mide el tamaño de un mercado. PARADIGMA pregunta qué supuestos detrás de ese mercado dejaron de ser ciertos, y quién lo notó.

## Repositorio

```text
paradigm-skill/
├── .claude-plugin/          manifiestos de marketplace y plugin de Claude Code
├── skills/paradigma/
│   ├── SKILL.md             instrucciones que sigue el agente
│   └── scripts/paradigma.py motor de análisis (curvas, matriz de huecos, IPC, papers)
├── tests/test_engine.py     prueba sin conexión con respuestas conocidas
├── dist/paradigma.zip       skill lista para subir a las apps de Claude (tools/package.sh)
├── tools/                   make_assets.py (gráficos del README), package.sh (regenera el ZIP)
├── README/                  traducciones del README
└── assets/                  banner, proceso y matriz de huecos
```

```bash
python3 tests/test_engine.py   # deberían salir 10 líneas PASS
```

## Contribuir

Issues y pull requests son bienvenidos, sobre todo:

- corridas reales que quieras compartir en `examples/`
- mejores fuentes de datos gratuitas para un campo o región
- casos en que un hueco que informó PARADIGMA resultó equivocado, y por qué

Mantené las reglas: cada número lleva su fuente y toda la matemática queda en el motor.

## Licencia

[MIT](../LICENSE) © 2026 qaemu

<div align="center">
<br>
<sub>Hecho por <a href="https://github.com/qaemu">qaemu</a>. Del mismo autor: <a href="https://github.com/qaemu/phasentic">Phasentic</a>, identificación de fases por difracción de rayos X en polvo, de código abierto.</sub>
</div>
