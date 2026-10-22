---
title: "psTerminalPerfCounter – Performance Counter im Terminal – HowTo"
slug: "psterminalperfcounter-counter-in-terminal-handson"
date: 2026-06-14T21:02:34+02:00
lastmod: 2026-06-14T21:02:35+02:00
draft: false
categories: ["PowerShell"]
tags: ["counter", "PERFORMANCE", "PowerShell", "TERMINAL"]
summary: "Hands-on zu psTerminalPerfCounter: Windows Performance Counter im Terminal überwachen, inklusive TUI, Multiserver-Monitoring sowie CSV- und HTML-Export."
aliases:
  - /psterminalperfcounter-counter-in-terminal-handson_de/
cover:
  image: "perfcounter_logo.png"
  alt: ""
  relative: true
---

# Intro

**[psTerminalPerfCounter](https://github.com/gabrielkoehl/psTerminalPerfCounter)**

![Solid black square placeholder with no visible content.](GitHub_Invertocat_Black.png "emote")

Im vorherigen Artikel habe ich einen kurzen Abriss in die [Geschichte und Funktionsweise](../windows-performance-counters-how-the-os-monitors-itself/index.de.md) der Windows Performance Counter gemacht, jetzt folgt das Hands-on. Grundlage ist Release 0.4.1, das ganz im Zeichen von Visualisierung und Datenexport steht. Neu dabei: CSV-Export, eine Terminal GUI als Ablösung der textbasierten Ansicht und der HTML-Export via PSWriteHTML. Klingt spannend… ist es auch 🙂 Ich denke das siehst du genau so, sonst würdest du nicht mehr lesen. 🙂

# Installation

Installation eines PowerShell Moduls, nichts besonderes

```powershell
# Install psTerminalPerfcounter
Install-Module psTerminalPerfCounter

# List Cmdlets
Get-Command -Module psTerminalPerfCounter

# Install PSWriteHtml, required for HTML Export
Install-Module PSWriteHtml
```

# Grundlegender Aufbau, Counterconfigs

psTerminalPerfCounter arbeitet mit Konfigurationsdateien, in denen die Counter-Sets und deren Konfiguration beschrieben sind: Counter-IDs, Instanzen (ob zum Beispiel alle CPU-Cores oder nur Core 3 und 4 überwacht werden sollen), Wertkonvertierung, Units und die farbliche Kodierung der Graphen über die sogenannte ColorMap, die allerdings nur die Legacy-Visualisierung unterstützt.

Counterconfigs können in beliebigen Pfaden gespeichert und von dort aufgerufen werden. Alternativ lassen sich Pfade registrieren, was den Aufruf einfach über denConfignamen ermöglicht. Der Default-Pfad ist der Config-Ordner im Modul selbst, der bereits einige vordefinierte Configs mitbringt.

```powershell
# List all registered paths
Get-tpcConfigPaths

# Add custom path
Add-tpcConfigPath -Path 'C:\tpcConfig'
```

![](IMG-20260611184010109.png)

```powershell
# List all Counterconfigs and details in all paths
Test-tpcAvailableCounterConfig
```

![](IMG-20260611184610947.png)

# Single Server Monitoring

Die schnellste Methode ist ein einzelner Server, lokal oder remote.

```powershell
# Use CPU Config locally
Start-tpcMonitor -Configname CPU
Start-tpcMonitor -Confipath 'C:\Users\labadmin\Documents\PowerShell\Modules\psterminalperfcounter\0.4.0\Config\tpc_CPU.json'

# Use CPU Config remote
Start-tpcMonitor -Computername 'dev-node1' -Configname CPU
Start-tpcMonitor -Computername 'dev-node1' -Confipath 'C:\Users\labadmin\Documents\PowerShell\Modules\psterminalperfcounter\0.4.0\Config\tpc_CPU.json'

# Use CPU Config rmeote with different credentials
Start-tpcMonitor -Computername 'dev-node1' -Credentials $(Get-Credential) -Configname CPU
```

![](IMG-20260611185126524.png)

Da die Legacy-Visualisierung spätestens bei Multiserver-Umgebungen an ihre Grenzen kommt, nutze ich für dieses Hands-on den `-TUI` Switch.

```powershell
# Use CPU Config locally with TUI
Start-tpcMonitor -Configname CPU -TUI
```

![](IMG-20260611190144159.png)

# Multi Server Monitoring

Das Multiserver-Monitoring funktioniert ebenfalls über Konfigurationsdateien, wobei mir beim Schreiben dieser Zeilen auffällt: Warum habe ich nie daran gedacht, einfach eine Counterconfig gegen eine Serverliste laufen zu lassen? Ab ins Backlog damit. Wie auch immer, in der Environment-Konfiguration lassen sich beliebig viele Server mit verschiedenen Configs definieren. Da ich zuletzt noch Probleme hatte, die Sparklines in der TUI scrollbar zu machen, sind diese in der Multiserver-Ansicht deaktiviert.

```powershell
# Start multi server monitoring
Start-tpcEnvironmentMonitor -EnvConfigPath 'C:\tpcConfig\ENV_SERVER_EXAMPLE.json' -TUI
```

![](IMG-20260611191606127.png)

*LAB-NODE03 ist in dem Fall ein deutsche Installation*

Die Spalte Duration zeigt die Zeit, die die Funktion auf dem jeweiligen Server gebraucht hat, um alle Werte einzusammeln. Den finalen Timestamp des gesamten Datensatzes definiert immer der langsamste Server, nur so ist eine homogene Zeitreihe möglich. Eine Varianz von in diesem Fall 1,3 Sekunden lässt sich dabei nicht vermeiden.

Das wars auch schon zur Auführung, da dieses Modul nur das Framework bereitstellt. Das eigentliche Leben kommt mit den Counterconfigs. Wie diese erstellt werden schauen wir uns jetzt an.

# Erstellung von Counterconfigs

Am Anfang ist der Performance Counter. Bevor wir die Konfiguration schreiben können, brauchen wir die Counter-IDs statt der lokalisierten Namen. Dafür gibt es `Get-tpcPerformanceCounterInfo`, das in beide Richtungen funktioniert: Counterpath zu ID und umgekehrt.

```powershell
# List all counter and counter objects containing 'processor time'
Get-tpcPerformanceCounterInfo -ComputerName 'dev-node1' -SearchTerm 'processor time'
```

![](IMG-20260612082832650.png)

Wichtig sind die letzten beiden Spalten. Es gibt Single-Instance-Counter mit nur einem Wert, aber auch Multi-Instance-Counter wie das Processor-Counterset, bei dem jede Instanz einem Core entspricht, oder halt gesamt (`_Total`).

Genauso lässt sich mit dem Cmdlet herausfinden, welcher Counter sich hinter einer Composite-ID verbirgt.

```powershell
# Show counter name of composite ID
Get-tpcPerformanceCounterInfo -ComputerName 'dev-node1' -SearchTerm '238-6'
```

![](IMG-20260612083119093.png)

Oder auf einem deutschen System

![](IMG-20260612083431840.png)

Nehmen wir noch Counter, die nicht standardmäßig auf einem Windows-System vorhanden sind: SQL Server. DEV22A ist in diesem Fall die erste Instanz auf dem System.

```powershell
# "Out-String -Stream" converts PowerShell's internal formatting objects into actual strings line by
# line, enabling string operations like `Select-String` to work on them.

Get-tpcPerformanceCounterInfo -ComputerName 'dev-node1' -SearchTerm 'dev22a' |
		Out-String -Stream |
		Select-String "lookup"
```

![](IMG-20260612081940564.png)

Nehmen wir zum Testen `Page lookups/sec` –> 12222-12272

```powershell
Get-tpcPerformanceCounterInfo -ComputerName 'dev-node1' -SearchTerm 'dev22a' |
		Out-String -Stream |
		Select-String "log flushes"
```

![](IMG-20260612082340599.png)

Und `log flush/sec` auf der Instanz TempDB –> 12352-12446

Die minimale Config sieht dann so aus. Bei den SQL-Server-Countern fehlen einige Werte, das ist aber nicht SQL-Server-spezifisch, sondern zeigt, dass die meisten Felder Defaults bekommen. Details dazu finden sich in der Doku im Repo. Erwähnenswert noch: bei CPU nutze ich `"counterInstance": "1|2"`, wodurch automatisch zwei Counter erstellt werden, und bei den Page Lookups die Konvertierung durch 1000, damit die Zahlen lesbar bleiben.\\

```json
{
	"name": "CPU and Sql Server Page Usage",
	"description": "CPU Usage",
	"counters": [
		{
			"title": "CPU Usage",
			"unit": "%",
			"conversionFactor": 1,
			"conversionExponent": 1,
			"conversionType": "D",
			"format": "table",
			"counterID": "238-6",
			"counterSetType": "MultiInstance",
			"counterInstance": "0|1",
			"colorMap": {
				"20": "Green",
				"50": "Yellow",
				"70": "RED"
			}
		},
		{
			"title": "Sql DEV22A Page Lookups/s",
			"unit": "#K",
			"conversionFactor": 1000,
			"conversionExponent": 1,
			"conversionType": "D",
			"counterID": "12222-12272",
			"counterSetType": "SingleInstance",
			"counterInstance": ""
		},
		{
			"title": "Sql DEV22A TempDB Log Flushes/s",
			"unit": "#",
			"counterID": "12352-12446",
			"counterSetType": "MultiInstance",
			"counterInstance": "tempdb"
		}

	]
}
```

Das Ganze dann in einem registrierten Pfad speichern mit dem Präfix `tpc_NAME.json` und los geht’s.

![](IMG-20260612090849880.png)

# Monitoring einer Umgebung mit Environment File

Auch hier keine Magic. Es können Confignamen oder Pfade angegeben werden. Eine noch nicht vollständig dokumentierte Funktion ist die Nutzung von SecretVaults: Über die PowerShell-Konnektoren lassen sich Credentials aus fast allen gängigen Lösungen laden, womit auch Nicht-Admins die Möglichkeit gegeben werden kann, Systeme zu überwachen.

```json
[
    {
        "name": "SQL_ENVIRONMENT_001",
        "description": "SQL Server Environment Production",
        "interval": 2,
        "secretvaultname": "SecretStore",
        "credentialname": "integrated",
        "servers": [
            {
                "computername": "DEV-NODE1",
                "comment": "Sql Server Node A Production",
                "counterConfig": [
                    "SQLDEMO"
                ]
            },
            {
                "computername": "DEV-NODE2",
                "comment": "Sql Server Node B Production",
                "counterConfig": [
                    "C:\Users\devadmin\Desktop\tpc_SQLDEMO.json"
                ]
            }
        ]
    }
]
```

```powershell
# without TUI
Start-tpcEnvironmentMonitor -EnvConfigPath "C:\Users\devadmin\Desktop\ENV_SERVER_EXAMPLE2.json"
```

![](IMG-20260612092052078.png)

# Datenexport

## CSV

![](IMG-20260612092726885.png)

Um die Zeitreihen weiterzuverwenden, kann nach CSV exportiert werden. Achtung, aktuell noch ein bekannter Bug: der Export ist kommasepariert, Werte mit Komma werden dadurch ebenfalls getrennt, in 0.4.1 gefixt.

```powershell
# -CsvPath is default desktop
	Start-tpcEnvironmentMonitor -EnvConfigPath "C:\Users\devadmin\Desktop\ENV_SERVER_EXAMPLE2.json" -ExportCsv
```

# HTML Report

Eine alternative Visualisierung als HTML, nützlich wenn ich eine Zeitreihe weitergeben möchte ohne Excel oder weitere Tools zu bemühen. Gruppiert werden kann nach Counter oder nach Server, je nachdem ob ich bei mehreren Servern alle Counter eines Servers in einem Diagramm sehen möchte, oder einen bestimmten Counter über mehrere Server hinweg. Details dazu finden sich in den Docs im Repo.

Zu beachten: das HTML enthält ein rollendes Datenset, das an die maximale Sample-Anzahl gebunden ist. Je mehr Samples, desto träger wird das HTML. Für große Zeitreihen lieber CSV nutzen.

```powershell
# -HTMLPath is default desktop
	Start-tpcEnvironmentMonitor -EnvConfigPath "C:\Users\devadmin\Desktop\ENV_SERVER_EXAMPLE2.json" -ExportHTML
```

![](IMG-20260612093443448.png)

Das war’s als Schnelleinstieg, mehr Details zu den einzelnen Funktionen finden sich wie immer in den Docs und der [README](https://github.com/gabrielkoehl/psTerminalPerfCounter/blob/main/README.md)im Repository.

![](2025-04-21_16-19.png "emote")
