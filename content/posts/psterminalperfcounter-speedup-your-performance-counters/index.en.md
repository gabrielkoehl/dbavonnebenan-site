---
title: "psTerminalPerfCounter – SpeedUp your Performance Counters in Terminal"
slug: "psterminalperfcounter-speedup-your-performance-counters"
date: 2025-07-26T17:07:18+02:00
lastmod: 2026-06-11T11:32:16+02:00
draft: false
categories: ["PowerShell"]
tags: ["counter", "PERFORMANCE", "PowerShell", "TERMINAL"]
summary: "Visualize Windows Performance Counters directly in terminal with psTerminalPerfCounter. Language-independent templates, maximum customization. Perfect for quick AdHoc monitoring."
aliases:
  - ../psterminalperfcounter-speedup-your-performance-counters_en/
cover:
  image: "perfcounter_logo.png"
  alt: ""
  relative: true
---

## Current Release ( 2026-06-08 )

[psTerminalPerfCounter 0.4.0](https://www.powershellgallery.com/packages/psTerminalPerfCounter "A PowerShell module for displaying real-time graphs of Windows Performance Counters directly in the terminal console. This module provides an easy way to visualize system performance metrics without requiring external graphing tools or GUI applications by using templates and multilanguage support.")

- [Changelog](https://github.com/gabrielkoehl/psTerminalPerfCounter/blob/main/CHANGELOG.md)
- [Documentation](https://github.com/gabrielkoehl/psTerminalPerfCounter/tree/main?tab=readme-ov-file#documentation)

## Intro

Windows Performance Counters are absolutely powerful, but when I need something quick or monitoring tailored to a specific problem, I get frustrated fast. Usually I fall back on other options – PowerShell native Get-Counter, CIM, or existing monitoring solutions at my clients. But that’s never truly ad-hoc either, and I’ve accepted it.

Recently I had the chance to join Uwe Ricken’s Performance Tuning Workshop at DataSaturday, and he clearly named Performance Counters as a must-have in every DBA’s toolkit. What I didn’t know until then: SQL Server creates individual counters like **Compile/sec**, **AdHoc Queries/sec**, etc.

![MINDBLOWING](mindblowing.png)

The possibilities to visualize dependencies directly – endless. But how long should I sit there configuring that in Windows Performance Monitor, especially ad-hoc at a client site?

Uwe showed the capabilities in Windows Admin Center, which enables templates you can use flexibly across servers. For systems or environments where Admin Center is used strategically, definitely a great choice.  
But two problems remain: As a consultant, I can’t install software at every client, and if Admin Center happens to be running, my English templates fail on German systems.

Still, I was so incredibly hooked by the template idea and the SQL Server possibilities that 4 weeks of after-work crunchtime were spinning in my head. So let me introduce my first module in the PowerShell Gallery:

**psTerminalPerfCounter 0.1.0-preview** A PowerShell module for displaying real-time graphs of Windows Performance Counters directly in the terminal console. This module provides an easy way to visualize system performance metrics without requiring external graphing tools or GUI applications by using templates and multilanguage support.

[psTerminalPerfCounter 0.1.0-preview](https://www.powershellgallery.com/packages/psTerminalPerfCounter/0.1.0-preview "A PowerShell module for displaying real-time graphs of Windows Performance Counters directly in the terminal console. This module provides an easy way to visualize system performance metrics without requiring external graphing tools or GUI applications by using templates and multilanguage support.")

You’ll find all technical details and development status in the repository – I just want to show the different possibilities here.

## Main Features

### 100% PowerShell

- no external dependencies

### Terminal Graphics

- obviously it’s not a real engine, the more counters the choppier it gets, but it’s sufficient
- The foundation comes from [Prateek Singh](https://github.com/PrateekKumarSingh/Graphical) solution. Without finding this, I would have had to solve this problem first, for which I probably wouldn’t have had time. THANKS!!!

![](perfcounter_example_cpu.png)

### Configuration Templates

- every output element is controlled via configuration files
- flexible, portable

### Data Output Customization

- each counter in the configuration file can use its own output
  - Table, Graph, or Both
- arbitrary axis scaling in steps and max values
- arbitrary value coloring based on user-defined ColorMap per counter
- value conversion via configuration file (Byte -> KB -> MB -> GB)

### Language Independent

- configuration files are based on counter IDs, not paths
  - portable, regardless of system language translation from ID to counter path happens at runtime
  - no external dependencies
- I had no idea this was possible with Windows built-in tools. Here too I stumbled across a blog at [PowerShell.ONE](https://powershell.one/tricks/performance/performance-counters) by chance. Again, a big THANKS!!! My original solution had multiple language variants (DE, EN, FR, ES) which would be set by reading system locale.

## Demo with CPU Configuration

```powershell
# Install module with required dependency (GripDevJsonSchemaValidator)
Install-Module -Name psTerminalPerfCounter -AllowPrerelease

# Import the module
Import-Module psTerminalPerfCounter

# Start Default Cpu Configuration
Start-tpcMonitor -ConfigName CPU
```

When loading the configuration, counter IDs are translated to counter paths and tested

![](perfcounter_load.png "emote")

If successful, the first samples are collected so a graph can be displayed

![](perfcounter_sample.png "emote")

Thats IT!

Within 10 seconds, 2 Performance Counters running, no installation, no language issues.

![](perfcounter_run.png "emote")

## Demo Counter Translation

```powershell
# Translate ID -> Path
Get-tpcPerformanceCounterInfo 238-6
```

![](perfmon_translate_id.png)

```powershell
# Search Counter -> Including ID
Get-tpcPerformanceCounterInfo "Queue"
```

![](perfmon_translate_search1.png)

*Output is heavily truncated since the ResultSet is enormous*

```powershell
# Search Counter -> Including ID
Get-tpcPerformanceCounterInfo "Processor Queue"
```

![](perfmon_translate_search2.png)

## What’s next?

The foundation works, the planned feature list is long, and what I really need for SQL Server is still far off. I hope I haven’t solved a problem that doesn’t exist, but this module simply addresses all the issues I’ve always had with Performance Counters, as mentioned above.

Furthermore, this is my first larger project that I’m developing publicly, so GitHub might not always meet expected standards. I’m always happy about feedback and suggestions.

![happy](emotes_standing_1.png "emote")

[GitHub – gabrielkoehl/psTerminalPerfCounter: psTerminalPerfCounter is a PowerShell module that provides predefined, language-independent performance counter configurations for real-time terminal-based monitoring, enabling admins to quickly deploy tailored system performance presets with graphical visualization instead of manually configuring Windows Performance Monitor.](https://github.com/gabrielkoehl/psTerminalPerfCounter "psTerminalPerfCounter is a PowerShell module that provides predefined, language-independent performance counter configurations for real-time terminal-based monitoring, enabling admins to quickly de…")
