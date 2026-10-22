---
title: "Automate SQL Server HA: AD, SPN, and Cluster Setup"
slug: "automate-sql-server-ha-ad-spn-and-cluster-setup"
date: 2026-02-06T12:47:28+01:00
lastmod: 2026-02-06T12:50:38+01:00
draft: false
categories: ["PowerShell", "Sql Server"]
tags: ["AD", "AlwaysOn", "Deployment", "GMSA", "SPN", "WSFC"]
summary: "Production-Ready Windows Cluster Deployment: Automation of Failover Cluster, gMSA, Kerberos and local rights via PowerShell."
aliases:
  - ../automate-sql-server-ha-ad-spn-and-cluster-setup_en/
cover:
  image: "sqlserver_ha_cluster_deploy.png"
  alt: "Sql Server HA Cluster Deployment"
  relative: true
---

[GitHub – gabrielkoehl/DBAScriptBox: Useful stuff for DBAs](https://github.com/gabrielkoehl/DBAScriptBox "Useful stuff for DBAs. Contribute to gabrielkoehl/DBAScriptBox development by creating an account on GitHub.")

## Intro {#0-intro}

Who hasn’t been there? Before you can even start installing SQL Server, you’ve either repetitively clicked through pages of bad GUIs or, if available, juggled a loose collection of scripts to semi-automatically set up all dependencies and best practices.

Even worse is the case when, as a consultant, you don’t have Domain Admin access (which is how it should be) and you have to guide the customer — who may have never done this before — via Teams & Co. If this isn’t already a planned installation with knowledge transfer, something like this creates pain. 🤭

![PAIN Emote](emote-4.png "emote")

Accordingly, I’ve now gathered all my loose scripts and developed a function for each topic area that automates all these tasks and logs them for archival purposes. Thanks also to Claude for the support. Nobody reviews and documents code better than Claude. 😋

Now you might ask: Aren’t there dbatools and DSC? Sure, I like using those too. But transparent, traceable scripts without framework overhead convey knowledge better — especially when aspiring DBAs lack the big-picture perspective. Operating SQL Server starts at the bare metal, goes through storage, Windows Server, Active Directory, and ends at a Certificate Authority. And for critical infrastructure companies or small mid-sized businesses with 3 clusters, I don’t want to start a fundamental discussion about dbatools or DSC right from the beginning.

Let’s start with a production-ready Windows Server Failover Cluster — including CNO/VCO permissions, DNS registration, and quorum configuration. Everything repeatable, everything logged, everything traceable.

## The Lab Scenario {#1-das-lab-szenario}

To make the steps tangible, the following environment and naming conventions are used

- **Nodes**
  - `LAB-NODE01` (192.168.100.12)
  - `LAB-NODE02` (192.168.100.13)
- **Cluster Name**
  - `MSSQL-CL-01` (192.168.100.14)
- **SQL Instance**
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

The WSFC forms the foundation for AlwaysOn Availability Groups. The script manages the entire lifecycle from feature installation to witness configuration.

### Feature Installation & Cluster Creation {#3-feature-installation-amp-cluster-erstellung}

First, the `Failover-Clustering` feature is installed on the individual nodes and the cluster is created. An important aspect of automation is the Cluster Name Object (CNO): It needs write permissions in DNS and Active Directory to be able to automatically create listener records later.

```powershell
.\cluster_manageSQLCluster.ps1 `
    -Operation InstallFeature `
    -Nodes "LAB-NODE01","LAB-NODE02" `
    -LogPath "C:\Temp\Cluster_Feature_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

Afterwards, the cluster is created. The script additionally sets the corresponding permissions in AD and DNS.

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

For a 2-node cluster, a witness is mandatory to avoid split-brain scenarios. Here, a file share on the domain controller (`\\LAB-DC\quorum$`) is used.

**Manual Intermediate Step**  
The Cluster Computer Object (`MSSQL-CL-01$`) requires **Full Control** at both the share and NTFS permission level of the witness path (`\\LAB-DC\quorum$`). This must be ensured before running the following command.

```powershell
.\cluster_manageSQLCluster.ps1 `
    -Operation SetWitness `
    -ClusterName "MSSQL-CL-01" `
    -WitnessShare "\\LAB-DC\quorum$" `
    -LogPath "C:\Temp\Cluster_Witness_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

### Microsoft Cmdlets Used {#5-verwendete-microsoft-cmdlets}

The script primarily uses the [`FailoverClusters`](https://learn.microsoft.com/en-us/powershell/module/failoverclusters/) module

- `New-Cluster`
  - Creates the cluster, adds the nodes, and sets the management IP
- `Set-ClusterQuorum`
  - Configures the witness mode (here: File Share Witness)
- `Install-WindowsFeature`
  - Installs the RSAT tools and the cluster service

---

## Identity Management: gMSA {#GMSA}

⚒️ [`security_createGMSA.ps1`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_createGMSA.ps1)

📓 [`security_createGMSA.md`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_createGMSA.md)

Using standard users as service accounts can lead to expired passwords and downtime. The recommended method for SQL Server is [`Group Managed Service Accounts (gMSA)`](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview). Here, the Key Distribution Service (KDS) of Active Directory handles password rotation; nobody needs to know the password.

### KDS Root Key

Before the first gMSA can be created, a KDS Root Key must exist once per forest. If a key already exists, the creation will be skipped.

```powershell
.\security_createGMSA.ps1 `
    -InitializeKDS `
    -LogPath "C:\Temp\KDS_Init.log"
```

### gMSA Creation

Instead of assigning servers directly to a gMSA, it is best practice to create a security group (`SQL_LAB_CL01`) that contains the computer accounts of the cluster nodes. In addition to setting up the actual gMSA, this script can also create the security groups and handle the assignments. And always keep the descriptions of AD objects well-maintained.

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

After this step, a restart of the nodes is required for the new group membership to take effect.

### Local Registration

After creation, the gMSAs must be registered locally on the nodes. The following script can be used for this purpose.

```powershell
# Required for local setup (Local Admin)
Add-WindowsFeature -Name RSAT-AD-PowerShell

$gMSAs = @(
    'g-LAB22A-oltp',
    'g-LAB22A-agnt'
)

foreach ($gMSA in $gMSAs) {

    if (Test-ADServiceAccount -Identity $gMSA -ErrorAction SilentlyContinue) {
        try {
            Install-ADServiceAccount -Identity $gMSA -ErrorAction Stop
            Write-Host "$gMSA installed" -ForegroundColor Green
        } catch {
            Write-Host "$gMSA - Installation error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "$gMSA does not exist" -ForegroundColor Yellow
    }
}
```

After this step, a restart of the nodes is required for the new group membership to take effect.

### Microsoft Cmdlets Used {#5-verwendete-microsoft-cmdlets}

The script primarily uses the [`ActiveDirectory`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2025-ps) module

- `Add-KdsRootKey`
  - Creates the root key for the Group Key Distribution Service
- `New-ADServiceAccount`
  - Creates the gMSA object in AD
- `Set-ADServiceAccount`
  - Configures which computers (PrincipalsAllowedToRetrieveManagedPassword) are allowed to read the password

---

## Kerberos and Service Principal Names (SPN) {#KERBEROS}

⚒️ [`security_setSqlSpn.ps1`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_setSqlSpn.ps1)

📓 [`security_setSqlSpn.md`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_setSqlSpn.md)

A gMSA does not have the right to write its own SPNs in AD by default. When the SQL service starts, the registration often fails, leading to NTLM fallbacks. Even though I prefer to set SPNs in a controlled and manual manner, the automatic registration must be technically possible to avoid fallbacks.

The script solves this problem by granting the gMSA the rights in AD to manage its own SPNs, in addition to creating the SPNs. It sets ACLs on the nodes for `Read`, `Write`, and `Validated write` on the `servicePrincipalName` attribute.

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

### Microsoft Cmdlets Used {#5-verwendete-microsoft-cmdlets}

On one hand, [`setspn.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setspn) is used for SPN management, and on the other hand, the [`ActiveDirectory`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/?view=windowsserver2025-ps) module is used again to verify accounts and extract SIDs.

Since none of the modules can manipulate Active Directory permissions, the .NET Framework [`System.DirectoryServices`](https://learn.microsoft.com/en-us/dotnet/api/system.directoryservices?view=windowsdesktop-10.0) is used directly for this purpose, which provides various classes to completely turn AD inside out.

---

## Local Security Policies {#LSP}

⚒️ [`security_setSqlLocalSec.ps1`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_setSqlLocalSec.ps1)

📓 [`security_setSqlLocalSec.md`](https://github.com/gabrielkoehl/DBAScriptBox/blob/main/windows/security/security_setSqlLocalSec.md)

As everywhere in IT, SQL Server should also follow the [`PoLP`](https://en.wikipedia.org/wiki/Principle_of_least_privilege), which is why no service account gets local administrator privileges. For SQL Server to still run flawlessly and performantly, the service account needs specific rights in the operating system („User Rights Assignment“). Anyone who has done this manually a few times will be very happy about this solution. This must be executed locally on the respective node.

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

### Microsoft Cmdlets Used

Since PowerShell has no native cmdlets for editing local security policies, the Windows tool [`secedit.exe`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/secedit) is used and its export is manipulated.

---

## Summary

With these four building blocks, the foundation for a SQL Server installation has been laid. It wasn’t just an installation that was performed, but a valid, documented configuration that considers identity (gMSA), network (DNS/SPN), and OS performance. In the next step, the actual SQL Server instance can be installed.

Also check out the linked MD files — they contain background information on best practices and further articles from Microsoft

![good to know emote](emotes_2.png)
