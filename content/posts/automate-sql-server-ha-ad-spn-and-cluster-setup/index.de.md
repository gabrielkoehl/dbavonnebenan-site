---
title: "SQL Server HA: AD, SPN und Cluster Setup automatisieren"
slug: "automate-sql-server-ha-ad-spn-and-cluster-setup"
date: 2026-02-06T12:20:00+01:00
lastmod: 2026-02-06T12:28:07+01:00
draft: false
categories: ["PowerShell", "Sql Server"]
tags: ["AD", "AlwaysOn", "Deployment", "GMSA", "SPN", "WSFC"]
summary: "Production-Ready Windows Cluster Deployment: Automatisierung von Failover Cluster, gMSA, Kerberos und lokalen Rechten via PowerShell."
aliases:
  - /automate-sql-server-ha-ad-spn-and-cluster-setup_de/
cover:
  image: "sqlserver_ha_cluster_deploy.png"
  alt: "Sql Server HA Cluster Deployment"
  relative: true
---

[GitHub – gabrielkoehl/DBAScriptBox: Useful stuff for DBAs](https://github.com/gabrielkoehl/DBAScriptBox "Useful stuff for DBAs. Contribute to gabrielkoehl/DBAScriptBox development by creating an account on GitHub.")

## Intro {#0-intro}

Wer kennt es nicht? Bevor man überhaupt mit der Installation von SQL Server loslegen kann, hat man sich entweder repetitiv durch seitenweise schlechte GUIs geklickt oder wenn verfügbar, mit einer losen Sammlung an Scripten jongliert und semiautomatisch alle Abhängigkeiten und Best Practices eingerichtet.

Noch schlimmer ist der Fall, wenn man als Berater gar keinen Domain Admin hat (was auch so sein sollte) und man den Kunden, der dies vielleicht noch nie gemacht hat, per Teams & Co anleiten muss. Wenn dies nicht eh eine geplante Installation mit Know-how-Transfer ist, erzeugt so etwas Schmerz. 🤭

![PAIN Emote](emote-4.png "emote")

Dementsprechend habe ich nun mal all meine losen Scripte zusammengewürfelt und für jeden Themenbereich eine recht umfangreiche Funktion entwickelt, welche all diese Tasks automatisiert und für Archivzwecke loggt. Danke auch an Claude für die Unterstützung. Keiner kontrolliert und dokumentiert Code besser als Claude. 😋

Nun könnte man sich fragen: Es gibt doch dbatools und DSC? Klar, nutze ich auch gerne. Aber transparente, nachvollziehbare Scripts ohne Framework-Overhead vermitteln Wissen besser – gerade wenn angehenden DBAs der Blick fürs Ganze fehlt. Betrieb von SQL Server fängt auf dem Blech an, geht über Storage, Windows Server, Active Directory und hört bei einer Certificate Authority auf. Und bei KRITIS-Unternehmen oder kleinen Mittelständlern mit 3 Clustern will ich zu Beginn keine Grundsatzdiskussion über dbatools oder DSC führen.

Los geht’s mit einem Production-Ready Windows Server Failover Cluster – inklusive CNO/VCO-Berechtigungen, DNS-Registrierung und Quorum-Konfiguration. Alles wiederholbar, alles geloggt, alles nachvollziehbar.

## Das Lab Szenario {#1-das-lab-szenario}

Um die Schritte greifbar zu machen, wird folgende Umgebung und Naming-Conventions genutzt

- **Nodes**
  - `LAB-NODE01` (192.168.100.12)
  - `LAB-NODE02` (192.168.100.13)
- **Cluster Name**
  - `MSSQL-CL-01` (192.168.100.14)
- **SQL Instanz**
  - `LAB22A`
- **Domain**
  - `lab.local`
- **Service Accounts** Group Managed Service Accounts (gMSA)
  - `g-LAB22A-oltp`
  - `g-LAB22A-agnt`

---

## Windows Server Failover Cluster Deployment {#WSFC}

⚒️ [`cluster_manageSQLCluster.ps1`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/system/cluster_manageSQLCluster.ps1)

📓 [`cluster_manageSQLCluster.md`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/system/cluster_manageSQLCluster.md)

Der WSFC bildet das Fundament für AlwaysOn Availability Groups. Das Script steuert den gesamten Lifecycle von der Feature-Installation bis zur Witness-Konfiguration.

### Feature Installation & Cluster Erstellung {#3-feature-installation-amp-cluster-erstellung}

Zunächst wird das Feature `Failover-Clustering` auf den einzelnen Nodes installiert und der Cluster erstellt. Ein wichtiger Aspekt bei der Automatisierung ist das Cluster-Objekt (CNO): Es benötigt Schreibrechte im DNS und Active Directory um später automatisiert Listener-Records anlegen zu können.

```powershell
.\cluster_manageSQLCluster.ps1 `
    -Operation InstallFeature `
    -Nodes "LAB-NODE01","LAB-NODE02" `
    -LogPath "C:\Temp\Cluster_Feature_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

Anschließend wird der Cluster erstellt. Das Script setzt zusätzlich die entsprechenden Berechtigungen in AD und DNS.

```powershell
.\cluster_manageSQLCluster.ps1 `
    -Operation CreateCluster `
    -ClusterName "MSSQL-CL-01" `
    -Nodes "LAB-NODE01","LAB-NODE02" `
    -StaticIP "192.168.100.14" `
    -DnsDomain "lab.local" `
    -TargetOU "OU=lab_computer,DC=lab,DC=local" `
    -LogPath "C:\Temp\Cluster_Create_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

### File Share Witness (Quorum) {#4-file-share-witness-quorum}

Für einen 2-Node Cluster ist ein Witness zwingend erforderlich, um Split-Brain-Szenarien zu vermeiden. Hier wird ein File Share auf dem Domain Controller (`\\LAB-DC\quorum$`) genutzt.

**Manueller Zwischenschritt**  
Das Cluster-Computer-Objekt (`MSSQL-CL-01$`) benötigt **Full Control** auf Ebene der Share- und NTFS-Berechtigungen des Witness-Pfads (`\\LAB-DC\quorum$`). Dies muss vor dem folgenden Befehl sichergestellt sein.

```powershell
.\cluster_manageSQLCluster.ps1 `
    -Operation SetWitness `
    -ClusterName "MSSQL-CL-01" `
    -WitnessShare "\\LAB-DC\quorum$" `
    -LogPath "C:\Temp\Cluster_Witness_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

### Verwendete Microsoft Cmdlets {#5-verwendete-microsoft-cmdlets}

Das Script nutzt primär das [`FailoverClusters`](https://learn.microsoft.com/en-us/powershell/module/failoverclusters/) Modul

- `New-Cluster`
  - Erstellt den Cluster, bindet die Nodes ein und setzt die Management-IP
- `Set-ClusterQuorum`
  - Konfiguriert den Witness-Modus (hier: File Share Witness)
- `Install-WindowsFeature`
  - Installiert die RSAT-Tools und den Cluster-Dienst

---

## Identity Management: gMSA {#GMSA}

⚒️ [`security_createGMSA.ps1`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_createGMSA.ps1)

📓 [`security_createGMSA.md`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_createGMSA.md)

Die Nutzung von Standard-Usern als Service Accounts kann zu abgelaufenen Passwörtern und Downtime führen. Die empfohlene Methode für SQL Server sind [`Group Managed Service Accounts (gMSA)`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview). Hierbei übernimmt der Key Distribution Service (KDS) des Active Directory die Passwortrotation; Niemand muss das Passwort kennen.

### KDS Root Key

Bevor der erste gMSA erstellt werden kann, muss einmalig pro Forest ein KDS Root Key existieren. Sollte bereits ein Key existieren, wird die Erstellung übersprungen.

```powershell
.\security_createGMSA.ps1 `
    -InitializeKDS `
    -LogPath "C:\Temp\KDS_Init.log"
```

### gMSA Erstellung

Anstatt Server direkt einem gMSA zuzuordnen, ist es Best Practice, eine Security Group zu erstellen (`SQL_LAB_CL01`), welche die Computerkonten der Cluster-Nodes enthält. Neben der Einrichtung der eigentlichen gMSA kann dieses Script auch die Security Gruppen erstellen und die Zuordnungen vornehmen. Und immer schön die Beschreibungen bei AD-Objekten pflegen.

```powershell
.\security_createGMSA.ps1 `
    -AccountName @( `
        @("g-LAB22A-oltp", "SQL Server Engine Account for LAB22A"), `
        @("g-LAB22A-agnt", "SQL Server Agent Account for LAB22A") ) `
    -SecurityGroupName "SQL_LAB_CL01" `
    -SecurityGroupDescription "SQL Server Cluster CL01 gMSA Group" `
    -ServerNames "LAB-NODE01","LAB-NODE02" `
    -CreateSecurityGroup `
    -SecurityGroupOU "OU=lab_secgrp,DC=lab,DC=local" `
    -PasswordIntervalDays 90 `
    -LogPath "C:\Temp\gMSA_Creation_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

Nach diesem Schritt ist ein Neustart der Nodes erforderlich, damit die neue Gruppenmitgliedschaft wirksam wird.

### Lokale Registrierung

Nach der Erstellung müssen die gMSA lokal auf den Nodes registriert werden. Hierzu kann folgendes Script genutzt werden.

```powershell
# Wichtig für lokale Einrichtung ( Local Admin )
Add-WindowsFeature -Name RSAT-AD-PowerShell

$gMSAs = @(
    'g-LAB22A-oltp',
    'g-LAB22A-agnt'
)

foreach ($gMSA in $gMSAs) {

    if (Test-ADServiceAccount -Identity $gMSA -ErrorAction SilentlyContinue) {
        try {
            Install-ADServiceAccount -Identity $gMSA -ErrorAction Stop
            Write-Host "$gMSA installiert" -ForegroundColor Green
        } catch {
            Write-Host "$gMSA - Fehler bei Installation: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "$gMSA existiert nicht" -ForegroundColor Yellow
    }
}
```

Nach diesem Schritt ist ein Neustart der Nodes erforderlich, damit die neue Gruppenmitgliedschaft (TGT) wirksam wird.

### Verwendete Microsoft Cmdlets {#5-verwendete-microsoft-cmdlets}

Das Script nutzt primär das [`ActiveDirectory`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2025-ps) Modul

- `Add-KdsRootKey`
  - Erzeugt den Root Key für den Group Key Distribution Service
- `New-ADServiceAccount`
  - Erstellt das gMSA Objekt im AD
- `Set-ADServiceAccount`
  - Konfiguriert, welche Computer (PrincipalsAllowedToRetrieveManagedPassword) das Passwort lesen dürfen

---

## Kerberos und Service Principal Names (SPN) {#KERBEROS}

⚒️ [`security_setSqlSpn.ps1`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_setSqlSpn.ps1)

📓 [`security_setSqlSpn.md`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_setSqlSpn.md)

Ein gMSA besitzt standardmäßig nicht das Recht, seine eigenen SPNs im AD zu schreiben. Startet der SQL Dienst, schlägt die Registrierung oft fehl, was zu NTLM-Fallbacks führt. Auch wenn ich SPNs bevorzugt kontrolliert und manuell setze, muss die automatische Registrierung technisch möglich sein, um Fallbacks zu vermeiden.

Das Script löst dieses Problem, indem es zusätzlich zur SPN Erstellung dem gMSA die Rechte im AD gewährt, seine eigenen SPNs zu verwalten. Es setzt ACLs der Nodes für `Read`, `Write` und `Validated write` auf das Attribut `servicePrincipalName`.

```powershell
.\security_setSqlSpn.ps1 `
    -ServiceAccount "LAB\g-LAB22A-oltp" `
    -InstanceName "LAB22A" `
    -Port 51101 `
    -Hostnames "LAB-NODE01","LAB-NODE02" `
    -Domain "lab.local" `
    -IsGMSA `
    -SetADPermissions `
    -LogPath "C:\Temp\SPN_AlwaysOn_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

### Verwendete Microsoft Cmdlets {#5-verwendete-microsoft-cmdlets}

Zum einen wird [`setspn.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setspn) für Verwaltung der SPN genutzt, zum anderen wieder das [`ActiveDirectory`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2025-ps) Modul, um Accounts zu verifizieren und die SIDs zu extrahieren.

Da keines der Module Active Directory Permsission manipulieren kann, wird hierfür direkt das .NET Framework [`System.DirectoryServices`](https://learn.microsoft.com/en-us/dotnet/api/system.directoryservices?view=windowsdesktop-10.0) genutzt, welches diverse Klassen bereitstellt, um das AD komplett auf Links zu drehen.

---

## Lokale Sicherheitsrichtlinien (Local Security Policies) {#LSP}

⚒️ [`security_setSqlLocalSec.ps1`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_setSqlLocalSec.ps1)

📓 [`security_setSqlLocalSec.md`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_setSqlLocalSec.md)

Wie überall in der IT sollte auch beim Sql Server nach dem [`PoLP`](https://en.wikipedia.org/wiki/Principle_of_least_privilege) gearbeitet werden, weshalb kein Service Account den lokalen Administrator bekommt.Damit SQL Server trotzdem fehlerfrei und performant läuft, benötigt der Service Account spezifische Rechte im Betriebssystem („User Rights Assignment“). Wer dies ein paar mal manuell gemacht hat, wird sich sehr über diese Lösung freuen. Diese muss lokal auf dem jeweiligen Node ausgeführt werden.

```powershell
# ===== Set Engine Permissions for gMSA =====

    .\security_setSqlLocalSec.ps1 `
        -ServiceAccount "g-LAB22A-oltp$" `
        -ServiceType "engine" `
        -IsGMSA `
        -LogPath "C:\Temp\LAB22A_Engine_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# ===== Set Agent Permissions for gMSA =====

    .\security_setSqlLocalSec.ps1 `
        -ServiceAccount "g-LAB22A-agnt$" `
        -ServiceType "agent" `
        -IsGMSA `
        -LogPath "C:\Temp\LAB22A_Agent_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

### Verwendete Microsoft Cmdlets

Da PowerShell keine nativen Cmdlets besitzt, um lokale Sicherheitsrichtlinien (LSA) zu bearbeiten, wird das Windows-Tool [`secedit.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/secedit) genutzt und der Export manipuliert.

---

## Summary

Mit diesen vier Bausteinen wurde das Fundament für eine Sql Server Installation gelegt. Es wurde nicht nur eine Installation durchgeführt, sondern eine valide, dokumentierte Konfiguration geschaffen, die Identität (gMSA), Netzwerk (DNS/SPN) und OS-Performance (LSA) berücksichtigt. Im nächsten Schritt kann die eigentliche SQL Server Instanz installiert werden.

Schaut euch auch die verlinkten MD-Files an, dort stehen Hintergrundinfos zu den Best Practices und weiterführende Artikel von Microsoft

![good to know emote](emotes_2.png)
