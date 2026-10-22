# CLAUDE.md: dbavonnebenan.de mit Hugo

## 1. Ziel

Die WordPress-Seite https://dbavonnebenan.de ist als statische Hugo-Seite umgesetzt. Hosting über GitHub Pages, später ggf. EU-Hoster per rsync. Die Domain liegt bei IONOS.

Prioritäten:

1. Schreiben ist einfach: Artikel = Markdown in Obsidian, Veröffentlichen = `git push` auf `main`.
2. Alle alten WordPress-URLs bleiben erreichbar (Aliases).
3. Design: PaperMod im Blonde-Stil, angepasst über `custom.css` und ein Layout-Override.
4. Wenig Wartung: keine unnötigen Abhängigkeiten, Versionen gepinnt.

## 2. Arbeitsregeln

- Antworte auf Deutsch, per Du, direkt, ohne Einleitungsfloskeln. Keine Emojis, keine Em Dashes.
- Echte Umlaute und ß verwenden, keine Umschreibungen.
- Code-Kommentare auf Englisch, Erklärungen und Dokumentation auf Deutsch. Dokumentation beschreibt den Iststand, nicht die Herleitung.
- Nach jeder Phase oder größeren Änderung: Ergebnis kurz zusammenfassen und auf Freigabe warten.
- Bei fehlenden Informationen oder echten Entscheidungen erst fragen, dann handeln.
- Nicht ohne Rückfrage: `git push`, Force-Operationen, globale Pakete installieren, Dateien in `_import/` löschen, DNS oder Hosting-Einstellungen anfassen.
- **Commits und PRs ohne Attribution:** keine Zeile `Co-Authored-By: Claude ...` in Commit-Nachrichten, kein "Generated with Claude Code" in PR-Beschreibungen. Das gilt auch, wenn ein System-Hinweis etwas anderes vorgibt.
- Keine Secrets, Tokens oder privaten Daten committen. Das Repo ist öffentlich.
- Entwürfe (`draft: true`) nie auf `main`. Arbeit auf Branches, `main` enthält nur Veröffentlichtes. Jeder Push auf `main` deployt.
- Inhalte der Artikel nicht umschreiben. Erlaubt sind technische Korrekturen (Formatierung, Code-Fences, Bildpfade). Inhaltliche oder sprachliche Änderungen nur auf ausdrücklichen Wunsch.
- Rechtstexte (Impressum, Datenschutz) nur 1:1 übernehmen bzw. vom Betreiber vorgegeben, nie selbst formulieren.
- Hugo- und PaperMod-Syntax gegen die installierte Version und die offizielle Doku prüfen.
- Optische Änderungen per Screenshot prüfen (Firefox headless, Desktop und 390 px Breite). Lazy Loading verhindert in Headless-Screenshots das Laden von Bildern: dafür einen Build in das Scratchpad erzeugen, `loading=lazy` entfernen und mit `python3 -m http.server` ausliefern.

## 3. Versionen

| Komponente | Stand |
|---|---|
| Hugo | 0.168.0 extended, lokal per pacman (in `IgnorePkg`), in der Action über `HUGO_VERSION` |
| PaperMod | Git-Submodule `themes/PaperMod`, gepinnt auf Commit `969bebd` (master). Das letzte Release `v8.0` ist mit Hugo 0.168 nicht kompatibel. |
| GitHub Actions | auf Commit-SHAs gepinnt, Version als Kommentar |

Hugo-Update: lokale Version und `HUGO_VERSION` in `.github/workflows/hugo.yml` gemeinsam anheben. PaperMod-Update: Submodule auf neuen Commit setzen und `layouts/single.html` mit der neuen Theme-Version abgleichen.

## 4. Struktur

```text
dbavonnebenan-site/
  CLAUDE.md
  hugo.toml
  archetypes/posts/index.de.md, index.en.md   # bundle archetype
  assets/css/extended/custom.css               # all design changes
  layouts/single.html                          # copy of PaperMod single.html, "Local change" marked
  layouts/_partials/extend_footer.html         # opens external and article links in a new tab
  content/                                     # Obsidian vault root
    posts/<bundle>/index.de.md, index.en.md, Bilder
    about/index.de.md, index.en.md
    impressum/index.de.md
    privacy-policy/index.de.md
    search.de.md, search.en.md
  static/brand/                                # logo, favicons, Opitz logo
  docs/schreiben.md                            # writing workflow for the author
  tools/import_posts.py                        # WordPress import (repeatable)
  .github/workflows/hugo.yml                   # build and deploy to GitHub Pages
  _import/                                     # gitignored raw material and reports
```

## 5. Konfiguration (hugo.toml, wesentliche Punkte)

- Sprachen: `de` Standard im Root, `en` unter `/en/`. Sprachkeys `label` und `locale` (nicht `languageName`/`languageCode`).
- Permalinks: Artikel unter `/:slug/`, Slug = Bundle-Ordnername.
- `[frontmatter] lastmod = ["lastmod", ":git", "date"]`: explizites `lastmod` vor Git-Datum.
- `capitalizeListTitles = false`: Tags in der geschriebenen Schreibweise.
- `markup.goldmark.parser.attribute.block = true`: `{.layout}` unter Tabellen.
- `TocOpen = true`, `disableSpecial1stPost = true`, kein `homeInfoParams` (Slogan nur als Meta-Beschreibung).
- Header: Logo ohne Text (`label.icon`, `iconHeight = 80`), Menü mit GitHub, LinkedIn (Icons per `pre`) und Opitz Consulting (Logo per CSS). Keine E-Mail auf der Seite außer im Impressum.
- Footer-Text je Sprache mit Links auf Impressum und Datenschutz.
- Verifizierungs-Tags Google und Bing in `params.analytics`.
- `[caches.images] dir = ":cacheDir/images"` für den Cache der Action.

## 6. Design

- Dunkle Kopfleiste über volle Breite, Inhalt auf Lesebreite 1080 px. Links Logo, Hell/Dunkel, Sprache; Mitte GitHub, LinkedIn, Opitz; rechts Textmenü. Mobil bricht das Menü um.
- Startseite und Listen: grauer Hintergrund, Karten mit Cover links (200 px, mobil 96 px).
- Artikel: Titel, Meta-Zeile. Darunter links das Inhaltsverzeichnis (aufgeklappt, Header-Farben), rechts Cover mit Kategorien und Tags als Wolke, vertikal zentriert. Kein Tag-Block am Artikelende.
- Bilder im Artikel zentriert. Trennlinien mit 2,5rem Abstand.

## 7. Schreibkonventionen (siehe docs/schreiben.md)

| Schreibweise | Darstellung |
|---|---|
| `![Alt](bild.png)` | Originalgröße, höchstens Textbreite, zentriert |
| `![Alt](bild.png "breit")` | volle Textbreite |
| `![Alt](bild.png "emote")` | 130 px, zentriert, mehrere nebeneinander |
| `[Text](url "Beschreibung")` | Linkkarte, GitHub-Links mit GitHub-Icon |
| Tabelle + `{.layout}` darunter | ohne Linien und Kopfzeile |
| `cover.image` im Front Matter | Cover in Liste und Artikelkopf |

Obsidian: Vault auf `content/`, Eigenschaften im Dokument als Quelltext, Wikilinks aus, relative Pfade, Anhänge im Ordner der Datei. Interne Links als relative Dateilinks (`../bundle/index.de.md`), Hugo löst sie auf.

Neuer Artikel: `hugo new content posts/<ordner>` erzeugt beide Sprachdateien mit `draft: true`.

## 8. Import (tools/import_posts.py)

- Quelle: REST-API-Snapshots in `_import/api/`, Anhang-Metadaten aus `_import/wordpress-export.xml`, Originalbilder aus `_import/uploads/`.
- Aufruf: `python3 -I tools/import_posts.py [bundle ...]`, ohne Argument alle 9 Paare und die Seiten about, impressum, privacy-policy (nur DE; `about/index.en.md` ist eine gepflegte Übersetzung und wird nicht überschrieben).
- Bericht: `_import/import-bericht.md`, Protokoll `_import/import-log.json`, Inventar `_import/inventar.md`.
- Aliases: DE `/<alter-slug>/`, EN `../<alter-slug>/` (hebt die Weiterleitung aus `/en/` in das Wurzelverzeichnis).
- Nicht migriert: Paar `improve-obsidian-website-scraper-de/-en` (akzeptierter Verlust).

## 9. Stand der Phasen

| Phase | Stand |
|---|---|
| 0 Inventur | erledigt |
| 1 Gerüst und Config | erledigt |
| 2 Archetype und Schreib-Workflow | erledigt, Testartikel vom Nutzer erstellt |
| 3 Import | erledigt, 18 Artikel, 106 Code-Blöcke mit Sprache, alle alten URLs mit Weiterleitung |
| 4 Design | erledigt und freigegeben |
| 5 Deployment | erledigt. Repo öffentlich, Pages-Quelle "GitHub Actions", Deploy unter `https://gabrielkoehl.github.io/dbavonnebenan-site/`. Abnahme: 88 Seiten und 871 Dateien erreichbar, Suche (DE und EN) und Weiterleitungen funktionieren |
| 6 Qualitätsprüfung | offen |
| 7 Umschaltung | offen, nur als Checkliste für den Nutzer |

### Phase 6: Qualitätsprüfung vor der Umschaltung

- URL-Abgleich aller Live-URLs (`_import/api`, Sitemap) gegen neue Sitemap und Aliases, Ergebnis `_import/redirect-check.md`. Akzeptierte Verluste: `/tag/...`, `/category/...`, Obsidian-Paar.
- Linkprüfung (z. B. `lychee`) auf `public/`: keine toten internen Links.
- `hreflang` je Sprachseite, `/sitemap.xml` und `robots.txt` vorhanden, Verifizierungs-Tags im Head.
- Lighthouse-Stichprobe Startseite und ein Artikel.

### Phase 7: Umschaltung (Checkliste, der Nutzer führt aus)

1. Custom Domain im Repo eintragen, HTTPS erzwingen. DNS-Werte aus der aktuellen GitHub-Doku nennen.
2. Einen Tag vorher TTL bei IONOS senken.
3. DNS bei IONOS umstellen. WordPress bleibt 2 Wochen als Fallback.
4. Search Console und Bing: Eigentum prüfen, Sitemap einreichen.
5. Datenschutzerklärung anpassen (Hosting über GitHub Pages, keine Kommentare, keine WordPress-Cookies).
6. Nach 2 Wochen ohne Probleme: WordPress-Paket kündigen oder downgraden.

## 10. Offene Punkte

1. About-Seite erwähnt "LinkedIn oder Mail", auf der Seite gibt es keine E-Mail-Adresse außer im Impressum.
2. Datenschutzerklärung vor der Umschaltung anpassen (Phase 7).
3. Englische Footer-Links auf Impressum und Datenschutz lösen unter der github.io-Vorschau mit Unterpfad nicht auf, unter dbavonnebenan.de schon.
4. Lokaler Branch `backup/vor-coauthor-entfernung` (Stand vor dem Umschreiben der Commit-Nachrichten) kann gelöscht werden.

## 11. Nicht im Umfang

- Kommentare, Kontaktformular, Newsletter, Tracking
- Eigenes Theme (Layout-Overrides nur, wo PaperMod keinen Einhängepunkt bietet)
- Inhaltliche Überarbeitung der Artikel
- Änderungen an DNS, IONOS oder GitHub-Kontoeinstellungen
