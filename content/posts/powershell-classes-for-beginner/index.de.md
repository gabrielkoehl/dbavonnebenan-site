---
title: "PowerShell Klassen für Anfänger – Strukturierter Code statt Funktions-Chaos"
slug: "powershell-classes-for-beginner"
date: 2025-06-14T19:33:32+02:00
lastmod: 2025-06-14T19:51:12+02:00
draft: false
categories: ["PowerShell"]
tags: ["Classes", "Klassen", "PowerShell", "TUTORIAL"]
summary: "Intro Seit eh und je nutze ich PowerShell nach Schema F, so ungefähr war auch mein Lernpfad entsprechend PowerShell Best Practices. Auf den letzten beiden Ebenen habe ich mich nun sehr lange bewegt, natürlich immer effizienter und allgemein wurde das PowerShell Wissen breiter. Während dieser Entwicklung merkte ich jedoch ein Problem: Ich bin ein sehr"
aliases:
  - /powershell-classes-for-beginner-de/
cover:
  image: "logo-powershell-meets-classes.png"
  alt: "PowerShell meets Classes"
  relative: true
---

## Intro

Seit eh und je nutze ich PowerShell nach Schema F, so ungefähr war auch mein Lernpfad entsprechend PowerShell Best Practices.

- Quick and Dirty Einzeiler in der Konsole, mittlerweile Terminal
- Nach und nach wurden aus den Einzeilern PowerShell Scripte mit besser organisierten Einzeilern
- Es kamen Variablen, dann Funktionen, die Wiederverwendbarkeit stieg
- Aus Funktionen wurden Module, persistente Datenhalden in Json und technologisch war das erstmal das Ende
- Das letzte HighLight war Threading und Runspaces

Auf den letzten beiden Ebenen habe ich mich nun sehr lange bewegt, natürlich immer effizienter und allgemein wurde das PowerShell Wissen breiter.

Während dieser Entwicklung merkte ich jedoch ein Problem: Ich bin ein sehr organisierter Mensch, zumindestens im beruflichen Umfeld 😉, und so soll auch mein Code sein, strukturiert. Von Clean Code halte ich nichts, Kommentare sind einfach punktuell wichtig, für mich, für andere, für meine Kunden. Neben Kommentaren ist aber auch die Struktur wichtig, was bringen mir Kommentare an einem ‚Bucket of Chars‘ ? Ebenfalls liebe ich symmetrischen Code, ja lacht ruhig, aber es macht sofort ersichtlich, was ist eine Variable, was eine Zusweisung und was der Value. Wenn ich sowas sehe…

```powershell
$userInfo = @{
   Name = $varSurename
   Address = $varStreet
   Data = $varRandomLongVar
}

$configSettings = @{
   ServerName = 'localhost'
   Port = 5432
   Database = 'mydb'
   Timeout = 30
}

$employee = @{
   Personal = @{
       FirstName = $varSurename
       LastName = 'Doe'
       Street = $varStreet
   }
   Work = @{
       Department = 'IT'
       Position = 'Developer'
   }
}
```

![](emote-4.png "emote")

… da kehrt sich mein Innerstes nach Außen 🤣 Ist vielleicht auch eine Krankheit. Dies ist eine normale Schreibweise, die als sauber gilt, ich weiß, aber das sollte doch so aussehen..

```powershell
$userInfo = @{
   Name 	= $varSurename
   Address 	= $varStreet
   Data 	= $varRandomLongVar
}

$configSettings = @{
   ServerName 	= 'localhost'
   Port 		= 5432
   Database 	= 'mydb'
   Timeout 		= 30
}

$employee = @{
   Personal = @{
       FirstName 	= $varSurename
       LastName 	= 'Doe'
       Street 		= $varStreet
   }
   Work 	= @{
       Department 	= 'IT'
       Position 	= 'Developer'
   }
}

$users = @(
   @{ Name = 'Alice'; 		Role = 'Admin' }
   @{ Name = $varSurename; 	Role = 'User' }
)
```

![](emote-5.png "emote")

Wie auch immer, darum solls hier nicht gehen. Es ist grundsätzlich so, dass die Struktur und Ordnung bei größeren Projekten nach und nach abnimmt und Klassen genau auf dieses Thema einspielen. Aber warum jetzt erst? Klassen gibt es seit PowerShell 5.0 .

## AI Assisted Coding

Natürlich war ich early Adopter der ganzen KI Chatbots und war erstaunt, was ChatGPT vor 2 Jahren schon konnte. Natürlich war der Code, egal welche Sprache, unbrauchbar, aber für Wissenserzeugung allemal nützlich. So wurde mit fortlaufender Qualität der Code besser und auch die Lösungswege wurden immer interessanter.

Irgendwann sind in den Vorschlägen Klassen aufgetaucht und ich habe es konsequent ignoriert 😝. Durch meine C# Reisen wusste ich, dass Klassen einfach der Standard sind, man aber schon grundlegend Wissen sollte, was ich damit machen will im Projekt, um diese sauber zu entwerfen. Und diesen Aufwand wollte ich mir nicht machen.

## Das neue Projekt

Es war an der Zeit, eine 4 Jahre alte Lösung an neue Anforderungen anzupassen, wie das halt manchmal so der Fall ist. Da mein Wissen ja auch nicht stehen bleibt, habe ich nach kurzem überfliegen des Codes entschieden:

**DAS FASSE ICH NICHT MEHR AN**, **DAS MUSS ALLES NEU!!**

Nun war ich in der entspannten Lage, dass für die Lösung alles vorhanden war

- Programmablaufplan (PAP)
- Funktionsbeschreibungen
- Programmatische Lösung der benötigten Funktionen auf unterster Ebene
- 4 Jahre Lessons learned

Somit musste ich mich nur um die Orchestrierung aller Schritte kümmern und habe entschieden, dass ich den Klassen mal eine Chance geben werde. In der Theorie ist dies nämlich die sauberste und strukturierteste Möglichkeit zu Coden.

Das Ergebnis hat meine Art zu Coden nicht völlig, aber nachhaltig verändert – aber dazu später mehr.

## Fazit nach 5 Wochen im Projekt {#powershell-classes-conclusion}

Klassen in PowerShell sind so unglaublich simpel, so strukturiert, so wunderschön❤️. Natürlich muss der UseCase passen, da die Implementierung initial mehr Struktur verlangt, aber wenn dieser gegeben ist, wird für mich kein Weg mehr an Klassen vorbei führen.

![I SAID PERFECTION](class-perfection.jpg "emote")

## Warum dieser Artikel, gibt doch genug?

Es gibt einige Artikel über Klassen in PowerShell und Objektorientierung aber trotzdem wird dieses Thema kaum in einem klassischen Tutorial behandelt. Es sind immer die Funktionen und man muss um dieses Thema wissen um es zu finden. Somit schreibe ich einfach noch einen Artikel, auch mal in deutsch, um vielleicht doch den ein oder anderen zusätzlich zu erreichen, weil…

![](powershell-classes-ftw.png)

---

## Hintergrundinfos zu PowerShell Klassen – OOP seit Version 5.0

Klassen gibt es in PowerShell seit PowerShell 5.0 also 2016… und ich habe vor einem Jahr erst davon erfahren 🤦‍♂️. PowerShell Klassen bringen objektorientierte Programmierkonzepte in PowerShell und haben somit auch haben alle grundlegenden Features einer Klasse.

- **Eigenschaften (Properties)**: Eigenschaften sind stark typisiert und unterstützen die meisten Validierungsattribute wie \[ValidateNotNull()\], \[ValidateRange()\] etc.
- **Methoden**: Methoden sind Funktionen, die an ein Objekt gebunden sind und explizit den Rückgabetyp definieren müssen
- **Konstruktoren**: Ermöglichen die Initialisierung von Objekten mit spezifischen Werten
- **Vererbung**: Erlaubt es, neue Klassen von bestehenden Klassen zu erstellen und deren Funktionalität zu erweitern

Eine Klasse ist nach dem Laden ein eigener Datentyp, später mehr dazu.

---

## Und wie funktioniert das jetzt?

Ich weiß noch, wie ich mich vor vielen Jahren mit OOP schwer tat und allgemein davon auszugehen ist, dass sich doch eher Admins als vollblut Software Entwickler initial mit PowerShell auseinander setzen. Somit versuche ich es mal total simpel.

![Explanation incoming](emotes_2.png "emote")

Ich nehme mal ein fiktives Modul, welche per Remoting Serverproperties abfragt und lokal auswertet, ein klassischer AdminTask.

**ACHTUNG:** Natürlich ist dieses Beispiel sehr konstruiert und nicht zwingend praktikabel aber es zeigt meiner Meinung nach die Zusammenhänge recht gut.

Dieses PowerShell Klassen Tutorial zeigt dir die wichtigsten Konzepte für objektorientierte Programmierung mit PowerShell.

### Eigenschaften (Properties)

Eine Klasse hat zu jeder Zeit ein fest definierten Satz an Eigenschaften. Dieser kann zur Laufzeit nicht geändert werden, sondern muss in der Definition der Klasse beschrieben werden.

### Die Klasse

```powershell
class Server {
# All Possible properties for the Server class
    [string]        $ServerName
    [string]        $Status
    [ipaddress]     $IP
    [string]        $Location
    [datetime]      $LastBootTime
    [string]        $OperatingSystem
# -------------------------------------------
}
```

### Konstruktoren

Ein Konstruktor erzeugt die Instanz einer Klasse. Dabei kann die Klasse default Values erhalten, oder der Konstruktor erwartet Parameter. In unserem Fall ist ein Servername sinnvoll. Somit gebe ich der Property **ServerName** direkt beim Laden einen Wert.

```powershell
class Server {
# All Possible properties for the Server class
    [string]        $ServerName
    [string]        $Status
    [ipaddress]     $IP
    [string]        $Location
    [datetime]      $LastBootTime
    [string]        $OperatingSystem
# -------------------------------------------

    # Constructor
    Server([string]$name) {
        $this.ServerName = $name
    }
}
```

Nun haben wir zwar ein Klasse aber wie bekommen wir nun einen Server da rein? Indem wir die Klasse in eine Variable laden und am besten auch noch dynamisch für alle Server.

```powershell
class Server {
# All Possible properties for the Server class
    [string]        $ServerName
    [string]        $Status
    [ipaddress]     $IP
    [string]        $Location
    [datetime]      $LastBootTime
    [string]        $OperatingSystem
# -------------------------------------------

    # Constructor
    Server([string]$name) {
        $this.ServerName = $name
    }
}

$serverlist = @('Server1','Server2','Server3')

foreach ( $server in $serverlist ) {

    # Create a new Server object for each server name
    New-Variable -Name "obj_$server" -Value ([Server]::new($server)) -Force

}
```

### Methoden

Methoden machen meiner Meinung nach die Klassen erst richtig interessant. Methoden sind die Funktionen mit denen ich Eigenschaften der Klassen manipulieren kann oder auf Basis von Argumenten, welche ich dem Aufruf hinzufüge, RETURNS erzeugen kann. Hierbei gebe ich bereits in der Methodendefintion den Typ der Rückgabe an. **VOID** erzeugt somit logischerweise keine Rückgabe.

```powershell
class Server {
    [string]        $ServerName
    [string]        $Status
    [ipaddress]     $IP
    [string]        $Location
    [datetime]      $LastBootTime
    [string]        $OperatingSystem

    Server([string]$name) {
        $this.ServerName = $name
    }

    [void] GetServerInfo() {

        try {

            $osInfo = Invoke-Command -ComputerName $this.ServerName -ScriptBlock {
                Get-CimInstance Win32_OperatingSystem | Select-Object Caption, LastBootUpTime
            } -ErrorAction Stop

            $this.IP = Invoke-Command -ComputerName $this.ServerName -ScriptBlock {
                (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike '169.*'} | Select-Object -First 1).IPAddress
            } -ErrorAction Stop

            $this.OperatingSystem = $osInfo.Caption
            $this.LastBootTime    = $osInfo.LastBootUpTime
            $this.Status          = "Online"

        } catch {

            $this.Status = "Offline"

        }
    }
}

$serverlist = @('Server1','Server2','Server3')

foreach ($server in $serverlist) {
    New-Variable -Name "obj_$server" -Value ([Server]::new($server)) -Force
}

$obj_Server1.GetServerInfo()
$obj_Server2.GetServerInfo()
$obj_Server3.GetServerInfo()
```

Hier habe ich die Methode **GetServerInfo()** eingefügt, die nun die Informationen zum Server sammelt. Dabei muss ich weder ein Argument mitgeben oder ein Cmdlet starten, da die Instanz (Servername) der Klasse (Server) alles vererbt bekommen hat. Ich brauche keine externen Funktionen, Variablen oder sonst was, alles in der Klasse vorhanden. ❤️ Folgend ein Beispiel aus dem LAB

![LAB Result of simple powershell class](powershell_classes_lab.png)

*LAB Results*

## Und jetzt, wo ist der Nutzen?

Natürlich ist das nicht der optimalste Use Case, dafür verständlich. Eine Möglichkeit wäre, eine LoggingKlasse zu erstellen. Anbei aus meinem Projekt:

```powershell
class PatchLogger {
     [string]        $ServerName
     [string]        $LogPathServer
     [string]        $LogLevel = 'INFO'
     [hashtable]     $LogTargets
     [bool]          $ConsoleOutput
     [bool]          $StreamOutput
     [string]        $VerbosePreference
     [string]        $DebugPreference

     # Constructor
     PatchLogger(	[string]$LogPathServer,
					[string]$ServerName,
					[string]$MessageFile,
					[string]$ErrorFile,
					[string]$VerboseFile,
					[string]$DebugFile,
					[string]$SqlServerFile,
					[bool]$ConsoleOutput 	= $true,
					[bool]$StreamOutput 	= $false) {

          $this.LogPathServer   = $LogPathServer
          $this.ServerName      = $ServerName
          $this.ConsoleOutput   = $ConsoleOutput
          $this.StreamOutput    = $StreamOutput
          $this.LogTargets      = @{
               Main           = $MessageFile
               Error          = $ErrorFile
               Verbose        = $VerboseFile
               Debug          = $DebugFile
               SqlServer      = $SqlServerFile
          }

          $this.VerbosePreference = $Global:VerbosePreference
          $this.DebugPreference   = $Global:DebugPreference

          if ( -not (Test-Path $this.LogPathServer) ) {
               New-Item -Path $this.LogPathServer -ItemType Directory -Force | Out-Null
          }
    }

}
```

Eine Instanz der Klasse wird direkt beim Laden des Moduls in die Variable **$PatchLogger** geladen und ab jetzt kann ich mit **$PatchLogger.Info($message)** schon direkt loslegen. Wie? So ein kurzer Befehl bei einer so komplexen Klasse? Kommen wir zum letzten, was meiner Meinung nach der Vorteil schlechthin ist: **Überladung**.

## Überladung

Überladung heisst nichts anderes als die Anzahl der Argumente, die ich einer Methode übergebe. Anhand der Anzahl kann die Engine unterscheiden, welche Methode genutzt wird, da ich mehrer mit den gleichen Namen haben kann. Der Fachbegriff wäre Method Overloading.

Der Mehrwert liegt darin, dass ich nicht wie bei Funktionen mit BoundParams, Switch oder IF SChleifen arbeiten muss. Wenn eine Helfer Methode mit nur einem Argument aufgerufen wird, werden intern die fehlenden Argumente aufgefüllt und die Hauptmethode aufgerufen.

Nehmen wir das Beispiel **$PatchLogger.Info($message)**

```powershell
# Hauptmethode
[hashtable] WriteLog([string]$Level, [string]$Message, [string]$MessageCode, [int]$Severity, [string]$Target, [bool]$ReturnObject) {...}

# Helfermethode
[hashtable] Info([string]$Message) {
      return $this.WriteLog('INFO', $Message, $null, 0, 'Main', $true)
}

# Helfermethode 2
[hashtable] Info([string]$Message, [string]$MessageCode) {
      return $this.WriteLog('INFO', $Message, $MessageCode, 0, 'Main', $true)
}
```

Was wird das meiste sein, was ich ich einem großen Modul benötige? Eine einfache Message ins Main Log, ohne Messagecode und SchnickSchnack. Somit ruft die Helfermethode die Hauptmethode mit den Defaultwerten auf, die genau das bewirken.

Schauen wir uns Helfermethode 2 an. Diese erwartet 2 Argumente, nämlich einen MessageCode. Schon kann ich mit **$PatchLogger.Info(„Prozess XY abgeschlossen“,“I0002″)** eine registrierte Message schreiben.

Natürlich kann ich das auch alles mit Funktionen realisieren aber ich denke nicht so strukturiert und hübsch.

{{< details summary="Gesamte PatchLogger Klasse" >}}

```powershell
class PatchLogger {
     [string]        $ServerName
     [string]        $LogPathServer
     [string]        $LogLevel = 'INFO'
     [hashtable]     $LogTargets
     [bool]          $ConsoleOutput
     [bool]          $StreamOutput
     [string]        $VerbosePreference
     [string]        $DebugPreference

     # Constructor
     PatchLogger([string]$LogPathServer, [string]$ServerName, [string]$MessageFile, [string]$ErrorFile, [string]$VerboseFile, [string]$DebugFile, [string]$SqlServerFile, [bool]$ConsoleOutput = $true, [bool]$StreamOutput = $false) {
          $this.LogPathServer   = $LogPathServer
          $this.ServerName      = $ServerName
          $this.ConsoleOutput   = $ConsoleOutput
          $this.StreamOutput    = $StreamOutput
          $this.LogTargets      = @{
               Main           = $MessageFile
               Error          = $ErrorFile
               Verbose        = $VerboseFile
               Debug          = $DebugFile
               SqlServer      = $SqlServerFile
          }

          $this.VerbosePreference = $Global:VerbosePreference
          $this.DebugPreference   = $Global:DebugPreference

          if ( -not (Test-Path $this.LogPathServer) ) {
               New-Item -Path $this.LogPathServer -ItemType Directory -Force | Out-Null
          }
     }

     [void] UpdatePreferences([string]$VerbosePreference, [string]$DebugPreference) {
          $this.VerbosePreference = $VerbosePreference
          $this.DebugPreference   = $DebugPreference
     }

     # Central WriteLog method - all other methods call this one
     [object] WriteLog([string]$Level, [string]$Message, [string]$MessageCode, [int]$Severity, [string]$Target, [bool]$ReturnObject) {

          $timestamp          = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
          $severityText       = if ($Severity -ne 9999) { "S$Severity" } else { "" }
          $messageCodeText    = if ($MessageCode) { " $MessageCode" } else { "" }

          $paddedLevel        = "{0,-9}" -f "[$Level]"

          $additionalInfo     = "$severityText$messageCodeText"
          $logEntry           = if ( $level -eq 'BLANK' ) {
                                   ""
                                } elseif ( $Level -notin @('VERBOSE','DEBUG') -and -not [string]::IsNullOrEmpty($additionalInfo) ) {
                                   "[$timestamp] $paddedLevel [$($this.ServerName)] $Message ($additionalInfo)"
                                } else {
                                   "[$timestamp] $paddedLevel [$($this.ServerName)] $Message"
                              }

          $targetFile = $this.LogTargets[$Target]
          if ( $targetFile ) {
               try {
                    Add-Content -Path $targetFile -Value $logEntry -Encoding UTF8

                    $verboseFile = $this.LogTargets['Verbose']
                    if ( $verboseFile -and $Level -ne 'VERBOSE' ) {
                         Add-Content -Path $verboseFile -Value $logEntry -Encoding UTF8 # for unbroken verbose stream
                    }

               } catch {
                    Invoke-ScriptError $_
               }
          }

          if ( $this.ConsoleOutput ) {
               switch ( $Level ) {
                    'ERROR'        { Write-Host $logEntry -ForegroundColor Red }
                    'WARNING'      { Write-Host $logEntry -ForegroundColor Yellow }
                    'INFO'         { Write-Host $logEntry -ForegroundColor Green }
                    'BLANK'        { Write-Host $logEntry}
                    'VERBOSE'      {
                         if ( $this.VerbosePreference -ne 'SilentlyContinue' ) {
                              Write-Host $logEntry -ForegroundColor Cyan
                         }
                    }
                    'DEBUG'        {
                         if ( $this.DebugPreference -ne 'SilentlyContinue' ) {
                              Write-Host $logEntry -ForegroundColor Magenta
                         }
                    }
               }
          }

          # PowerShell streams for integration - only if explicitly enabled
          if ( $this.StreamOutput ) {
               switch ($Level) {
                    'ERROR'   { Write-Error       $Message -ErrorAction Continue }
                    'WARNING' { Write-Warning     $Message }
                    'VERBOSE' { Write-Verbose     $Message }
                    'DEBUG'   { Write-Debug       $Message }
               }
          }

          # Return object only when requested
          if ( $ReturnObject ) {
               return @{
                    HasError    = $Level -eq 'ERROR'
                    HasWarning  = $Level -eq 'WARNING'
                    MessageCode = if ( $MessageCode ) { $MessageCode } else { $null }
                    Message     = $Message
                    Severity    = $Severity
                    Level       = $Level
                    Target      = $Target
               }
          }

          return $null
     }

     # BLANK Line
     [void] BlankLine() {
          $this.WriteLog('BLANK', '', $null, 0, 'Main', $false)
     }

     # INFO Methods - standard return hashtable
     [hashtable] Info([string]$Message) {
          return $this.WriteLog('INFO', $Message, $null, 0, 'Main', $true)
     }

     [hashtable] Info([string]$Message, [string]$MessageCode) {
          return $this.WriteLog('INFO', $Message, $MessageCode, 0, 'Main', $true)
     }

     # INFO NoReturn
     [void] InfoNoReturn([string]$Message) {
          $this.WriteLog('INFO', $Message, $null, 0, 'Main', $false)
     }

     [void] InfoNoReturn([string]$Message, [string]$MessageCode) {
          $this.WriteLog('INFO', $Message, $MessageCode, 0, 'Main', $false)
     }

     # WARNING Methods - standard return hashtable
     [hashtable] Warning([string]$Message) {
          return $this.WriteLog('WARNING', $Message, $null, 1, 'Main', $true)
     }

     [hashtable] Warning([string]$Message, [string]$MessageCode) {
          return $this.WriteLog('WARNING', $Message, $MessageCode, 1, 'Main', $true)
     }

     # WARNING NoReturn
     [void] WarningNoReturn([string]$Message) {
          $this.WriteLog('WARNING', $Message, $null, 1, 'Main', $false)
     }

     [void] WarningNoReturn([string]$Message, [string]$MessageCode) {
          $this.WriteLog('WARNING', $Message, $MessageCode, 1, 'Main', $false)
     }

     # ERROR Methods - standard return hashtable
     [hashtable] Error([string]$Message) {
          return $this.WriteLog('ERROR', $Message, $null, 2, 'Error', $true)
     }

     [hashtable] Error([string]$Message, [string]$MessageCode) {
          return $this.WriteLog('ERROR', $Message, $MessageCode, 2, 'Error', $true)
     }

     # ERROR NoReturn
     [void] ErrorNoReturn([string]$Message) {
          $this.WriteLog('ERROR', $Message, $null, 2, 'Error', $false)
     }

     [void] ErrorNoReturn([string]$Message, [string]$MessageCode) {
          $this.WriteLog('ERROR', $Message, $MessageCode, 2, 'Error', $false)
     }

     # VERBOSE & DEBUG - NoReturn
     [void] Verbose([string]$Message) {
          $this.WriteLog('VERBOSE', $Message, $null, 0, 'Verbose', $false)
     }

     [void] Debug([string]$Message) {
          $this.WriteLog('DEBUG', $Message, $null, 0, 'Debug', $false)
     }

     # Step/SQL/AG Methods - NoReturn
     [void] StepStart([int]$Step, [string]$StepName) {
          $this.BlankLine()
          $message = "========================= STEP $Step START: $StepName ========================="
          $this.WriteLog('INFO', $message, $null, 9999, 'Main', $false)
     }

     [void] StepEnd([int]$Step, [string]$StepName, [bool]$Success) {
          $status   = if ( $Success ) { "SUCCESS" } else { "FAILED" }
          $message  = "========================= STEP $Step END: $StepName - $status ========================="
          $this.WriteLog('INFO', $message, $null, 9999, 'Main', $false)
          $this.BlankLine()
     }

}
```

{{< /details >}}

## Zusammenfassung

PowerShell Klassen revolutionieren die Art, wie du größere Projekte strukturierst. Seit PowerShell 5.0 verfügbar, bieten sie objektorientierte Programmierung mit Eigenschaften, Methoden, Konstruktoren und Method Overloading. Der anfängliche Mehraufwand zahlt sich durch sauberen, wartbaren Code aus – besonders bei Modulen und komplexeren Funktionssammlungen.

**Die wichtigsten Vorteile auf einen Blick**

- Stark typisierte Properties mit Validierung
- gekapselte Funktionalität durch Methoden
- elegante Überladung statt komplexer Parameter-Logik und eine Struktur, die auch nach Monaten noch verständlich bleibt

Für Daily-Doing-Scripts bleibt der klassische Ansatz praktischer, aber sobald Wiederverwendbarkeit und Struktur wichtig werden, führt für mich kein Weg mehr an Klassen vorbei. 🫡

![PowerShell meets Classes](logo-powershell-meets-classes.png)
