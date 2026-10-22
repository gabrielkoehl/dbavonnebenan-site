# Neuen Artikel schreiben

Jeder Artikel ist ein Ordner unter `content/posts/` (Page Bundle). Darin liegen die deutsche Fassung `index.de.md`, die englische Fassung `index.en.md` und alle Bilder des Artikels. Hugo verknüpft beide Sprachen über den gemeinsamen Ordner.

Der Ordnername ist gleichzeitig die URL: `content/posts/sql-server-tempdb/` wird zu `https://dbavonnebenan.de/sql-server-tempdb/` und `https://dbavonnebenan.de/en/sql-server-tempdb/`. Kleinbuchstaben und Bindestriche verwenden.

## Ablauf in 5 Schritten

1. **Branch und Ordner anlegen** (im Repo-Root):

   ```bash
   git switch -c artikel/sql-server-tempdb
   hugo new content posts/sql-server-tempdb
   ```

   Das legt `index.de.md` und `index.en.md` mit Front Matter und Gliederung an, beide mit `draft: true`.

2. **DE und EN ausfüllen** in Obsidian: `title`, `categories` (eine oder mehrere aus PowerShell, Sql Server, TSql), `tags`, `summary` und den Text. Code-Blöcke immer mit Sprache versehen (` ```powershell `, ` ```sql `).

3. **Bilder einfügen:** Bild per Drag and Drop oder Einfügen in Obsidian. Es landet automatisch im Artikelordner, der Link ist relativ (`![Beschreibung](bild.png)`). Optional ein Titelbild im Front Matter unter `cover.image` eintragen (nur Dateiname).

4. **Lokal prüfen:**

   ```bash
   hugo server -D
   ```

   Vorschau unter http://localhost:1313/. `-D` zeigt auch Entwürfe.

5. **Veröffentlichen:** In beiden Dateien `draft: false` setzen, committen, nach `main` übernehmen und pushen. GitHub baut und veröffentlicht die Seite automatisch.

   ```bash
   git add content/posts/sql-server-tempdb
   git commit -m "Artikel: SQL Server tempdb"
   git switch main
   git merge artikel/sql-server-tempdb
   git push
   ```

Entwürfe (`draft: true`) kommen nie auf `main`.

## Änderungsdatum

Das Änderungsdatum (`lastmod`) ermittelt Hugo aus dem letzten Git-Commit der Datei. Steht `lastmod` explizit im Front Matter, hat dieser Wert Vorrang. Die importierten Artikel nutzen das, um ihr Datum aus WordPress zu behalten.

## Obsidian-Einstellungen

- Vault öffnen auf den Ordner `content/`.
- Einstellungen, Dateien und Links:
  - "Wikilinks verwenden": aus
  - "Neue Links im Format": relativer Pfad zur Datei
  - "Standardort für neue Anhänge": im selben Ordner wie die aktuelle Datei
- Der Ordner `.obsidian/` ist in `.gitignore` eingetragen und wird von Hugo ignoriert.
