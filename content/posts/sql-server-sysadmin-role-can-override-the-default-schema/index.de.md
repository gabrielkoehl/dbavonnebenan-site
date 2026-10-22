---
title: "SysAdmin Role ignoriert das Default User Schema – Eine verwirrende Fehlersuche"
slug: "sql-server-sysadmin-role-can-override-the-default-schema"
date: 2025-05-08T11:13:05+02:00
lastmod: 2025-06-08T11:14:29+02:00
draft: false
categories: ["TSql"]
tags: ["DBO", "schema", "SYSADMIN"]
summary: "Heute hatte ich wieder einen Fall auf dem Tisch, bei dem eine Fehlermeldung einer Anwendung besagte, dass auf ein Objekt in der SQL Server DB nicht zugegriffen werden kann. Der Hersteller behauptete „Verbindungsproblem“, ich sagte „DB oder zumindest Server-Problem“, Kunde sagt „früher hat alles funktioniert“. Die Extended Events waren schnell aufgesetzt, „Remote Procedure Call Starting“"
aliases:
  - /sql-server-sysadmin-role-can-override-the-default-schema-de/
cover:
  image: "schema_logo.png"
  alt: "SCHEMA NAME"
  relative: true
---

Heute hatte ich wieder einen Fall auf dem Tisch, bei dem eine Fehlermeldung einer Anwendung besagte, dass auf ein Objekt in der SQL Server DB nicht zugegriffen werden kann. Der Hersteller behauptete „Verbindungsproblem“, ich sagte „DB oder zumindest Server-Problem“, Kunde sagt „früher hat alles funktioniert“.

Die Extended Events waren schnell aufgesetzt, „Remote Procedure Call Starting“ zeigt mir ein Statement ohne vollqualifizierten Tabellennamen. Das Zielobjekt liegt in der Database unter dem db_owner Schema. Najaaa, das ist schon fragwürdig, aber OK. Warum nicht als dbo belassen?

Jedenfalls war mir das Verhalten an diesem Punkt wirklich unverständlich, da alles korrekt konfiguriert war: Default Schema des Users, db_owner auf der DB. Und der SysAdmin. Das war mir aufgefallen, aber nun ja, Entscheidung des Kunden. Sowas notiere ich mir in einer Session, ändere aber nichts, um gewachsene Abhängigkeiten nicht zu gefährden.

Nach langem Suchen gab ich fast auf, verwies an den Vendor und beendete den Call. Leider kann ich solche Sachen nicht loslassen, also feuerte ich das Lab an, baute die Umgebung nach und siehe da, fand den Fehler.

Das Problem ist die SysAdmin-Rolle. Sie mappt den Login direkt auf den dbo-User der Database – egal ob der eigentliche User existiert oder nicht, erbt somit das Default Schema von dbo. Mindblowing, wusste ich nicht. 🙂

## SysAdmin Role inaktiv

![](2025-05-08_11-49_1.png "emote")

## SysAdmin Role aktiv

![](2025-05-08_11-50.png "emote")

![](2025-05-08_11-13.png "emote")

---

{{< details summary="T-SQL CODE für die Screenshots" >}}

```sql
DECLARE @IsSysAdmin INT
SELECT @IsSysAdmin = IS_SRVROLEMEMBER('sysadmin')

SELECT SYSTEM_USER AS CurrentLoginName;

SELECT
    'Current User'  AS Info,
    USER_NAME()     AS Username,
    SCHEMA_NAME()   AS CurrentSchema,
    CASE WHEN @IsSysAdmin = 1 THEN 'Yes' ELSE 'No' END
                    AS IsSysAdmin

SELECT
    'Default Schema'        AS Info,
    dp.name                 AS Username,
    dp.default_schema_name AS DefaultSchema
FROM
    sys.database_principals dp
WHERE
    dp.name = USER_NAME()

SELECT
    'DB Role Membership'    AS Info,
    USER_NAME()             AS Username,
    r.name                  AS RoleName
FROM
    sys.database_principals u
JOIN
    sys.database_role_members m ON u.principal_id = m.member_principal_id
JOIN
    sys.database_principals r ON m.role_principal_id = r.principal_id
WHERE
    u.name = USER_NAME()

--------------------

-- select * from [customSchema].[userTable] <<<<< ALWAYS WORKING !!!!!

 select * from [userTable]
```

{{< /details >}}

---

- Verwende immer vollqualifizierte Objektnamen, irgendwann wirst du froh sein, dass du es getan hast. Das kannst du in vielen Blogs lesen.
- Arbeite immer nach POLP ([Principle of Least Privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege)), ein App-User sollte keine SysAdmin-Rechte haben! 🙂

![](2025-05-08_11-43.png "emote")

**Gabriel, der DBAvonNebenan**
