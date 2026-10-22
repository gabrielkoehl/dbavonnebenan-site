# CLAUDE.md: Migration dbavonnebenan.de von WordPress auf Hugo

## 1. Ziel

Die bestehende WordPress-Seite https://dbavonnebenan.de wird auf eine statische Hugo-Seite migriert.
Hosting zunächst GitHub Pages (öffentliches Repo), später ggf. EU-Hoster per rsync. Die Domain bleibt bei IONOS.

Prioritäten in dieser Reihenfolge:

1. Schreiben muss einfach sein: Artikel = Markdown in Obsidian, Veröffentlichen = `git push`.
2. Alle bestehenden URLs und Artikel bleiben erreichbar.
3. Design ähnlich zur Live-Seite, ohne Überengineering. 80 Prozent Ähnlichkeit reichen.
4. Wenig Wartung: keine unnötigen Abhängigkeiten, Versionen pinnen.

## 2. Arbeitsregeln

- Antworte auf Deutsch, per Du, direkt, ohne Einleitungsfloskeln. Keine Emojis, keine Em Dashes.
- Echte Umlaute und ß verwenden (ä, ö, ü, ß), keine Umschreibungen.
- Code-Kommentare auf Englisch, Erklärungen auf Deutsch.
- Arbeite phasenweise (Abschnitt 6). Nach jeder Phase: Ergebnis kurz zusammenfassen und auf Freigabe warten.
- Bei fehlenden Informationen oder echten Entscheidungen erst fragen, dann handeln.
- Nicht ohne Rückfrage: `git push`, Force-Operationen, globale Pakete installieren, Dateien in `_import/` löschen, DNS oder Hosting-Einstellungen anfassen.
- Keine Secrets, Tokens oder private Daten committen
- Entwürfe (`draft: true`) nie auf `main` pushen. Arbeit auf Feature-Branches, `main` enthält nur Veröffentlichtes.
- Inhalte der Artikel nicht umschreiben. Erlaubt sind technische Korrekturen der Konvertierung (Formatierung, Code-Fences, Bildpfade). Inhaltliche oder sprachliche Änderungen nur auf ausdrücklichen Wunsch.
- Aktuelle Hugo- und PaperMod-Syntax gegen die installierte Version und die offizielle Doku prüfen. Die Configs unten sind Vorlagen, keine Garantie.
- Rechtstexte (Impressum, Datenschutz) nur 1:1 übernehmen, nie selbst formulieren.
- Als Vergleich dient die Live-Seite: Bei Zweifeln an der Konvertierung die gerenderte Seite unter der alten URL abrufen und mit dem Markdown vergleichen.

## 3. Ausgangslage (von der Live-Seite)

- CMS: WordPress, Block-Theme. Titel: "DBA von Nebenan | Sql Server, Performance & PowerShell Automation".
- Autor: Gabriel Köhl. Thema: SQL Server, T-SQL, PowerShell, Performance.
- Zweisprachig: Zu jedem Thema gibt es einen deutschen und einen englischen Artikel. Aktuell getrennt über die Tags `de` und `eng`. Englische Slugs enden teils auf `_en`, z. B. `/sql-server-disk-latency-en/`.
- URL-Schema der Artikel: `https://dbavonnebenan.de/<slug>/`.
- Kategorien: PowerShell, Sql Server, TSql. Dazu viele Tags.
- Seiten: `/about/`, `/impressum/`, `/privacy-policy/`.
- Menü: LinkedIn, GitHub (github.com/gabrielkoehl), E-Mail, Artikel englisch, Artikel deutsch, AboutMe, extern "SqlServerBuilds" (https://sqlserverbuilds.blogspot.com).
- Kopfbereich zeigt ein Logo und ein Opitz-Consulting-Logo (Link auf https://opitz-consulting.com/).
- Vorhandene Verifizierungs-Meta-Tags: Google Site Verification und `msvalidate.01` (Bing). Die Werte stehen im HTML-Head der Live-Seite und werden in die Config übernommen.
- Bekannte Tippfehler in der Meta-Description ("Perfomance Tunng", "Tips"): in der neuen Config korrigieren.
- Referenzmaterial liegt in `_import/` (nicht committen): `wordpress-export.xml`, `design/` (Screenshots), `brand/` (Logos)
- Referenzmaterial liegt in `_import/` (nicht committen): `wordpress-export.xml`, `uploads/` (Originalbilder per SFTP, Struktur JJJJ/MM), `design/` (Screenshots), `brand/` (Logos). Weitere Logos und Grafiken liegen in `uploads/`, z. B. `2025/04/full_logo_new-1.png` (Haupt-Logo) und `2026/02/oc_logo.png` (Opitz-Logo).
- 

## 4. Zielarchitektur

- Hugo extended, Version pinnen (siehe `hugo version`, in der GitHub Action identisch eintragen).
- Theme PaperMod als Git-Submodule, auf einen Release-Tag fixiert.
- Eine Content-Struktur mit **Page Bundles**: ein Ordner pro Thema, darin `index.de.md`, `index.en.md` und die gemeinsamen Bilder. Hugo verknüpft die Übersetzungen über den gemeinsamen Ordner automatisch, der Sprachumschalter funktioniert ohne `translationKey`.
- Sprachen: `de` ist Standard und liegt im Root, `en` liegt unter `/en/`.
- Obsidian-Vault = Ordner `content/`.
- Bilder: zuerst in `_import/uploads/` suchen (Originale per SFTP gesichert, Struktur `JJJJ/MM/datei`), nur falls nicht vorhanden von der Live-Seite laden. WordPress legt skalierte Varianten mit Größen-Suffix an (z. B. `bild-300x200.png`, `bild-scaled.png`). Das Original ist die Datei ohne Suffix. Das Original ins Bundle kopieren, Pfade relativ umschreiben, Alt-Texte übernehmen. Nicht benötigte Varianten nicht importieren. Kein Bild darf auf die alte Domain zeigen.

```text
dbavonnebenan-site/
  CLAUDE.md
  hugo.toml
  archetypes/
    posts/
      index.de.md
      index.en.md
  assets/css/extended/custom.css
  content/                      # Obsidian vault root
    posts/
      sql-server-disk-latency/
        index.de.md
        index.en.md
        disklat_logo.png
    about/
      index.de.md
      index.en.md
    impressum/index.de.md
    privacy-policy/index.de.md
    search.de.md
    search.en.md
  static/
    brand/
  themes/PaperMod/              # git submodule
  .github/workflows/hugo.yml
  _import/                      # gitignored raw material
```

## 5. Vorlagen

### 5.1 hugo.toml

````toml
baseURL = "https://dbavonnebenan.de/"   # override with --baseURL for preview deployments
title = "DBA von Nebenan"
theme = "PaperMod"

defaultContentLanguage = "de"
defaultContentLanguageInSubdir = false
enableRobotsTXT = true
enableGitInfo = true
enableEmoji = false
ignoreFiles = ['\.obsidian', '\.canvas$']   # keep Obsidian metadata out of the build

[pagination]
  pagerSize = 10

# Keep old article URLs: /<slug>/ instead of /posts/<slug>/
[permalinks.page]
  posts = "/:slug/"

[outputs]
  home = ["HTML", "RSS", "JSON"]   # JSON feeds the PaperMod search

[markup.highlight]
  noClasses = false   # use CSS classes from the theme
  lineNos = false
  guessSyntax = false

[markup.goldmark.renderer]
  unsafe = false

[params]
  env = "production"
  defaultTheme = "auto"
  ShowReadingTime = true
  ShowCodeCopyButtons = true
  ShowToc = true
  TocOpen = false
  ShowPostNavLinks = true
  ShowBreadCrumbs = false
  ShowShareButtons = false
  ShowLastMod = true
  comments = false

  [params.assets]
    favicon = "brand/favicon.png"        # from cropped-www_logo
    favicon16x16 = "brand/favicon.png"
    favicon32x32 = "brand/favicon.png"
    apple_touch_icon = "brand/favicon.png"

  [params.label]
    text = "DBA von Nebenan"
    icon = "brand/logo.png"
    iconHeight = 32

  # site verification (values taken from the live site head)
  [params.analytics.google]
    SiteVerificationTag = "v5tYngBsjJHNV_q24JH2dv7uNtkgdKx1QdSQ0mIdbWw"
  [params.analytics.bing]
    SiteVerificationTag = "938f6c1e7ac08d7ea209c43c65b6a3a4"

  [params.fuseOpts]
    isCaseSensitive = false
    shouldSort = true
    location = 0
    distance = 1000
    threshold = 0.4
    minMatchCharLength = 0
    keys = ["title", "permalink", "summary", "content"]

# Language: German (default)
[languages.de]
  languageName = "Deutsch"
  languageCode = "de-DE"
  weight = 1
  title = "DBA von Nebenan"

  [languages.de.params]
    description = "Lach- und Sachgeschichten aus dem Alltag eines SQL-Server-Beraters. Wissen und Tipps zu T-SQL, PowerShell und Performance-Tuning."
    author = "Gabriel Köhl"

    [languages.de.params.homeInfoParams]
      Title = "DBA von Nebenan"
      Content = "Lach- und Sachgeschichten aus dem Alltag eines SQL-Server-Beraters."

    [[languages.de.params.socialIcons]]
      name = "github"
      url = "https://github.com/gabrielkoehl"
    [[languages.de.params.socialIcons]]
      name = "linkedin"
      url = "https://www.linkedin.com/in/gabrielkoehl/"
    [[languages.de.params.socialIcons]]
      name = "email"
      url = "mailto:TODO_READ_FROM_LIVE_SITE"

  [[languages.de.menu.main]]
    identifier = "posts"
    name = "Artikel"
    url = "/posts/"
    weight = 10
  [[languages.de.menu.main]]
    identifier = "categories"
    name = "Kategorien"
    url = "/categories/"
    weight = 20
  [[languages.de.menu.main]]
    identifier = "search"
    name = "Suche"
    url = "/search/"
    weight = 30
  [[languages.de.menu.main]]
    identifier = "about"
    name = "Über mich"
    url = "/about/"
    weight = 40
  [[languages.de.menu.main]]
    identifier = "builds"
    name = "SqlServerBuilds (ext)"
    url = "https://sqlserverbuilds.blogspot.com"
    weight = 50

# Language: English
[languages.en]
  languageName = "English"
  languageCode = "en-US"
  weight = 2
  title = "DBA von Nebenan"

  [languages.en.params]
    description = "Tales and tips from the daily life of a SQL Server consultant. T-SQL, PowerShell and performance tuning."
    author = "Gabriel Köhl"

    [languages.en.params.homeInfoParams]
      Title = "DBA von Nebenan"
      Content = "Tales and tips from the daily life of a SQL Server consultant."

    [[languages.en.params.socialIcons]]
      name = "github"
      url = "https://github.com/gabrielkoehl"
    [[languages.en.params.socialIcons]]
      name = "linkedin"
      url = "https://www.linkedin.com/in/gabrielkoehl/"
    [[languages.en.params.socialIcons]]
      name = "email"
      url = "mailto:TODO_READ_FROM_LIVE_SITE"

  [[languages.en.menu.main]]
    identifier = "posts"
    name = "Articles"
    url = "/posts/"
    weight = 10
  [[languages.en.menu.main]]
    identifier = "categories"
    name = "Categories"
    url = "/categories/"
    weight = 20
  [[languages.en.menu.main]]
    identifier = "search"
    name = "Search"
    url = "/search/"
    weight = 30
  [[languages.en.menu.main]]
    identifier = "about"
    name = "About"
    url = "/about/"
    weight = 40
  [[languages.en.menu.main]]
    identifier = "builds"
    name = "SqlServerBuilds (ext)"
    url = "https://sqlserverbuilds.blogspot.com"
    weight = 50
````

Hinweise: Parameternamen und Struktur gegen die aktuelle PaperMod-Doku und die installierte Hugo-Version verifizieren (z. B. `pagination.pagerSize` statt altem `paginate`). Die `TODO_READ_FROM_LIVE_SITE`-Platzhalter vor dem Commit ersetzen: E-Mail-Adresse von der Live-Seite lesen und den Nutzer fragen, ob sie so öffentlich bleiben soll.

### 5.2 Archetype (Page Bundle, zweisprachig)

Verzeichnis `archetypes/posts/` mit zwei Dateien. Aufruf: `hugo new content posts/<ordnername>`.

`archetypes/posts/index.de.md`:

````markdown
---
title: ""
slug: ""
date: {{ .Date }}
lastmod: {{ .Date }}
draft: true
categories: []   # one of: PowerShell, Sql Server, TSql
tags: []
summary: ""
cover:
  image: ""      # file in this folder, optional
  alt: ""
  relative: true
---

## Problem

## Lösung

## Code

```powershell
# example
```

## Fazit
````

`archetypes/posts/index.en.md`:

````markdown
---
title: ""
slug: ""
date: {{ .Date }}
lastmod: {{ .Date }}
draft: true
categories: []   # one of: PowerShell, Sql Server, TSql
tags: []
summary: ""
cover:
  image: ""      # file in this folder, optional
  alt: ""
  relative: true
---

## Problem

## Solution

## Code

```powershell
# example
```

## Wrap-up
````

Prüfen, ob `hugo new content posts/test` beide Dateien erzeugt. Falls nicht: stattdessen ein kleines zsh-Skript `new-post.sh` bauen, das den Ordner anlegt und beide Vorlagen kopiert.

### 5.3 Search-Seiten

`content/search.de.md`:

````markdown
---
title: "Suche"
layout: "search"
summary: "search"
placeholder: "Artikel durchsuchen"
---
````

`content/search.en.md` analog mit `title: "Search"` und `placeholder: "Search articles"`.

### 5.4 Obsidian-Einstellungen (dokumentieren, Nutzer setzt sie)

- Vault öffnen auf `content/`.
- Dateien und Links: Wikilinks AUS, Markdown-Links AN, neue Links als relativer Pfad.
- Standardordner für neue Anhänge: "Gleicher Ordner wie die aktuelle Datei". Damit landen eingefügte Bilder im Bundle-Ordner.
- `.obsidian/` ist in `.gitignore` und in `ignoreFiles` eingetragen.
- Ein kurzes `docs/schreiben.md` im Repo anlegen: Ablauf "neuer Artikel" in 5 Schritten (siehe Phase 2).

### 5.5 GitHub Actions

Die aktuelle offizielle Vorlage von https://gohugo.io/host-and-deploy/host-on-github-pages/ holen und anpassen. Anforderungen:

- Checkout mit Submodulen
- Hugo extended in der gepinnten Version
- Build: `hugo --gc --minify --baseURL "<aus Pages-Konfiguration>/"`
- Artefakt-Upload und Deploy über die offiziellen Pages-Actions
- Alle Actions auf feste Versionen pinnen
- Pages-Quelle im Repo: "GitHub Actions" (setzt der Nutzer)

## 6. Phasen

Nach jeder Phase stoppen und Freigabe abwarten.

### Phase 0: Inventur

- Inhalt von `_import/` auflisten. Fehlt etwas Wichtiges, sagen.
- Alle Artikel und Seiten der Live-Seite erfassen. Quelle bevorzugt `wp-json/wp/v2/posts` und `wp-json/wp/v2/pages` (mit `per_page=100`), sonst `_import/wordpress-export.xml`. Zusätzlich die WordPress-Sitemap (`/wp-sitemap.xml`) als Referenz der Live-URLs.
- Ergebnis: `_import/inventar.md` als Tabelle mit Slug, Titel, Datum, Sprache (de oder eng), Kategorien, Tags.
- Vorschlag für die DE/EN-Paarung pro Thema, mit Bundle-Ordnernamen. Unsichere Paare markieren.
- Hugo-Version, PaperMod-Version und Abweichungen der Vorlagen aus Abschnitt 5 melden.
- Stopp: Nutzer bestätigt die Paarung.

### Phase 1: Gerüst und Config

- `hugo new site` im Repo-Root (ohne bestehende Dateien zu überschreiben), PaperMod als Submodule auf einen Release-Tag.
- `hugo.toml` aus 5.1 anlegen, Platzhalter ersetzen, Tippfehler korrigieren.
- Logos aus `_import/brand/` nach `static/brand/` (`logo.png`, `favicon.png`).
- Search-Seiten aus 5.3.
- Akzeptanz: `hugo server` läuft ohne Warnungen, Startseite DE und EN erreichbar, Sprachumschalter sichtbar.

### Phase 2: Archetype und Schreib-Workflow

- Archetype aus 5.2 anlegen und mit `hugo new content posts/test` prüfen.
- `docs/schreiben.md` erstellen: neuer Artikel in 5 Schritten (Ordner erzeugen, DE und EN ausfüllen, Bilder einfügen, `hugo server` prüfen, `draft: false` setzen und committen).
- Obsidian-Einstellungen aus 5.4 dokumentieren.
- Testartikel wieder entfernen.
- Stopp: Nutzer schreibt selbst einen Testartikel. Das ist das Abbruchkriterium aus der Vorbereitung.

### Phase 3: Import der Artikel

Quellenpriorität:

1. WordPress REST API oder XML-Export. Sie liefern exakt Slug, Datum, Änderungsdatum, Kategorien, Tags und den gerenderten Inhalt.
2. Obsidian-Clips in `_import/clips/` nur als Vergleich. Der Clipper konvertiert die gerenderte Seite und bringt typischerweise Theme-Reste mit, verliert die Sprache der Code-Blöcke und kennt weder Slug noch Datum.

Vorgehen:

1. **Erst ein Testpaar** (ein Thema, DE und EN) komplett importieren. Nutzer prüft im Browser. Erst nach Freigabe den Rest.
2. HTML zu Markdown mit pandoc (`-t gfm --wrap=none`) oder einem gleichwertigen Konverter. Skript im Repo unter `tools/import_posts.*` ablegen, damit der Import wiederholbar ist.
3. Code-Blöcke: Sprache aus der WordPress-Klasse (z. B. `language-powershell`) in den Fence übernehmen. Fehlt sie, anhand des Inhalts (T-SQL, PowerShell) setzen und im Bericht listen.
4. Bilder von `/wp-content/uploads/...` herunterladen, in den Bundle-Ordner legen, Pfade relativ umschreiben, Alt-Texte übernehmen. Kein Bild darf auf die alte Domain zeigen.
5. Front Matter nach Schema:
   - `title`, `date`, `lastmod`, `draft: false`
   - `slug`: **exakt der alte Slug**. Ausnahme: englische Slugs mit Suffix `_en` bekommen den Slug ohne Suffix, und der alte Pfad kommt als Alias dazu.
   - `aliases`: alle alten Pfade, die sich ändern (z. B. `/sql-server-disk-latency-en/` für die englische Seite, die unter `/en/sql-server-disk-latency/` liegt).
   - `categories`: exakt wie bisher (PowerShell, Sql Server, TSql).
   - `tags`: wie bisher, aber ohne die Sprach-Tags `de` und `eng`. Die Sprache steckt jetzt im Dateinamen.
   - `summary`: aus dem Excerpt.
6. Interne Links auf die alte Domain in relative Links der neuen Struktur umschreiben.
7. Seiten: About zweisprachig, Impressum und Datenschutz 1:1 aus der Live-Seite übernehmen.
8. Bericht `_import/import-bericht.md`: Artikel, Abweichungen, offene Punkte.

Akzeptanz:

- `hugo --gc --minify` ohne Warnungen
- Anzahl importierter Artikel gleich Anzahl in Phase 0
- Kein `wp-content` mehr im Output
- Jeder Code-Block mit Sprache, Stichprobe von 5 Artikeln visuell geprüft

### Phase 4: Design-Angleichung

- Referenz: Screenshots in `_import/design/`.
- Nur PaperMod-Parameter und `assets/css/extended/custom.css` verwenden. Kein Eingriff in den Theme-Ordner und keine eigenen Layouts, außer es geht nicht anders (dann begründen).
- Logo im Kopf, Favicon, Farben grob angleichen. Opitz-Logo optional: Nutzer fragen, ob es im Kopf, im Footer oder gar nicht erscheinen soll.
- Hell und Dunkel (`defaultTheme = "auto"`) prüfen, Desktop und Mobil.
- Stopp: Nutzer gibt das Design frei.

### Phase 5: Deployment

- Workflow aus 5.5 anlegen.
- Mit dem Nutzer: Pages-Quelle auf "GitHub Actions" stellen (macht der Nutzer).
- Erster Deploy auf die `github.io`-URL mit passender `--baseURL`. Die produktive `baseURL` in der `hugo.toml` bleibt `https://dbavonnebenan.de/`.
- Akzeptanz: Seite unter der `github.io`-URL vollständig erreichbar, Bilder und Suche funktionieren.

### Phase 6: Qualitätsprüfung vor der Umschaltung

- **URL-Abgleich:** Alle Live-URLs aus Phase 0 (Sitemap) gegen die neue Sitemap und die Aliases prüfen. Ergebnis `_import/redirect-check.md`. Jede alte Artikel-URL muss auflösen. Bekannte Verluste (alte Tag- und Kategorie-Seiten unter `/tag/...` und `/category/...`, neu `/tags/...` und `/categories/...`) als "akzeptiert" listen.
- Linkprüfung (z. B. `lychee`) auf das gebaute `public/`: keine toten internen Links.
- Jede Sprachseite hat einen `hreflang`-Verweis auf ihr Gegenstück.
- Sitemap unter `/sitemap.xml` und `robots.txt` vorhanden.
- Verifizierungs-Meta-Tags (Google, Bing) im Head der Startseite vorhanden.
- Lighthouse oder gleichwertig: Stichprobe Startseite und ein Artikel.

### Phase 7: Umschaltung (Checkliste, der Nutzer führt aus)

Nur als Anleitung ausgeben, nichts davon selbst ausführen:

1. Custom Domain im Repo eintragen und HTTPS erzwingen. Die aktuellen DNS-Werte (A-Records und CNAME für `www`) aus der offiziellen GitHub-Doku zur Custom Domain lesen und dem Nutzer nennen.
2. Einen Tag vorher die TTL der DNS-Einträge bei IONOS senken.
3. DNS bei IONOS umstellen. WordPress bleibt als Fallback 2 Wochen bestehen.
4. Search Console und Bing: Eigentum prüfen (Meta-Tag ist bereits in der Seite), Sitemap einreichen.
5. Datenschutzerklärung anpassen (Hosting über GitHub Pages).
6. Nach 2 Wochen ohne Probleme: WordPress-Paket kündigen oder downgraden.

## 7. Nicht im Umfang

- Kommentare, Kontaktformular, Newsletter, Tracking
- Eigene Layouts oder ein eigenes Theme
- Inhaltliche Überarbeitung der Artikel
- Änderungen an DNS, IONOS oder GitHub-Kontoeinstellungen

## 8. Definition of Done

- Alle Artikel zweisprachig als Page Bundles, alte URLs erreichbar
- `hugo --gc --minify` ohne Warnungen, Deployment per `git push` auf `main`
- `docs/schreiben.md` vorhanden, Testartikel vom Nutzer selbst erfolgreich veröffentlicht
- `_import/redirect-check.md` ohne ungeklärte Lücken
