---
title: "TRUNCATE TABLE – DDL vs DML – deep dive in operations and practical tips"
slug: "sql-server-truncate-vs-delete-dml-or-ddl"
date: 2025-05-26T14:14:32+02:00
lastmod: 2025-06-08T11:05:44+02:00
draft: false
categories: ["Sql Server", "TSql"]
tags: ["PERFORMANCE", "ROLLBACK", "TABLE", "TRANSACTION", "TRUNCATE"]
summary: "Recently, I stumbled across a LinkedIn post about truncate vs. delete, just like many others out there. Typically, random members post simple SQL Server tips, nicely packaged in graphics and kept general. Although for beginners this is absolutely legitimate – since these simple entry points can help many newcomers understand and provide a great starting"
aliases:
  - ../sql-server-truncate-vs-delete-dml-or-ddl-en/
cover:
  image: "logo_truncVSdel.png"
  alt: "Truncate vs. Delete"
  relative: true
---

Recently, I stumbled across a LinkedIn post about truncate vs. delete, just like many others out there. Typically, random members post simple SQL Server tips, nicely packaged in graphics and kept general. Although for beginners this is absolutely legitimate – since these simple entry points can help many newcomers understand and provide a great starting point – nevertheless, the fact that the same topics then go viral across various accounts is clearly another matter entirely.

Anyway. If you’re a bit further along in the topic and already know that the pronunciation isn’t „SQL“ but „sequel“ 😊, you should fundamentally question these posts, as they mostly generalize.

This was also the case in a post about the top 3 SQL mistakes that „everyone“ makes. And here we are, getting to the point.

[![TRUNCATE cant rolled back](2025-05-26_09-15.png)](https://www.linkedin.com/posts/samiul-fahim_sql-dataengineering-techtips-activity-7328642722653786112-OBfj?utm_source=share&utm_medium=member_desktop&rcm=ACoAACt1yIMBIZu3k0gdHLx7c_luIAnHYYBMtuc)

[LinkedIn](https://www.linkedin.com/posts/samiul-fahim_sql-dataengineering-techtips-activity-7328642722653786112-OBfj?utm_source=share&utm_medium=member_desktop&rcm=ACoAACt1yIMBIZu3k0gdHLx7c_luIAnHYYBMtuc)

The same happened with [Vedran Kesegic](https://www.linkedin.com/in/vedrankesegic/), who gave the hint that TRUNCATE is apparently rollback-capable when encapsulated in a transaction. Then [Carsten Saastamoinen-Jakobsen](https://www.linkedin.com/in/saastamoinen/) jumped in and things got wild. So wild that the whole topic hooked me so much that I did a deep dive into it. Furthermore, so much knowledge dropped in this exchange that it would be a shame if it disappeared in a comment section.

## What to expect here

I compared the exchange and looked at the core statements. I also texted separately with both of them a bit more, and Carsten gave me excerpts from one of his publications where the topic is covered technically.

Technically speaking, both agree, even if they don’t say it 🤣. But what was really wild in the end was the question:

![DML or DDL ??](ddl_dml.png)

I can say it upfront. This question is an philosophical one. I was able to form an opinion based on my research, more on that later, but basically it’s up to everyone to decide for themselves.

![](emotes_standing_1.png "emote")

---

## The Discussion – DML or DDL ?

### Vedran Kesegic

**Core Position: TRUNCATE is DDL**

> „TRUNCATE modifies internal system tables sys.sysallocunits and sys.sysrowsets. DELETE modifies indexes and stats“

> „DML writes data (rows in user tables), while DDL writes metadata (rows in system tables, data that describes other/user objects). Truncate happens to write metadata (system tables) and thus is classified as DDL.“

**Technical Arguments**

- Uses SCH-M (Schema Modification) lock
- Modifies system metadata tables
- Microsoft documentation classifies it as DDL
- Logs page deallocations, not row deletions

**Key Statement**

> „TRUNCATE modifies internal system tables sys.sysallocunits and sys.sysrowsets. DELETE modifies indexes and stats – see attached“

### Carsten Saastamoinen-Jakobsen

**Core Position: TRUNCATE is DML**

> „It is not an argument to call TRUNCATE a DDL statement because a certain lock is used! When statements are categorized, it must be based on what happens and not how a given database system solves the task.“

> „We may have to recognize that a previous error categorization should not continue to call TRUNCATE a DDL, but recognize that it is a DML.“

**Logical Arguments**

- Data is deleted, structure is preserved
- No table definition changes occur
- Follows semantic rules of data manipulation
- Can delete only some partitions (not all data)

**Key Statement**

> „I say that MS is right in the documentations because they are not telling that TRUNCATE is as DDL, because they know that TRUNCATE is a DML!“
>
> *NOTE Gabriel*   
> *I think this is really a bit questionable because the documentation is absolutely clear* *on this point* –> ***DDL*** ([microsoft.com](https://learn.microsoft.com/en-us/sql/t-sql/statements/statements?view=sql-server-ver17#data-definition-language))

**Quote from publication**

> „As of version 2016, it is possible to delete only some of the data in a table with TRUNCATE, so it is even more cor­rect to call it manipulation than definition, because it is changing some of the data but not changing the structure.“

### Points of Agreement

- TRUNCATE can be rolled back in a transaction
  - general demo at [sqlauthority.com](https://blog.sqlauthority.com/2010/03/04/sql-server-rollback-truncate-command-in-transaction/)
  - deep dive demo [sqlshack.com](https://www.sqlshack.com/the-internals-of-sql-truncate-and-sql-delete-statements/)
- TRUNCATE is a logged operation
- TRUNCATE is faster than DELETE for large datasets
- Both understand the technical implementation

### Core Disagreement

- **Classification criteria**
  - Implementation details
- **Authority**
  - Vendor documentation (Vedran) vs. Logical reasoning (Carsten)
- **Perspective**
  - How it works internally (Vedran) vs. What it does functionally (Carsten)

### My 50 Cent

So as you can see, technically it fits, but how do you view the whole thing? Maybe it’s good that I’m not preloaded with as much knowledge as both of them because from my perspective it’s quite clear: **DDL!!**

Contrary to Carsten’s statement that no system tables are changed, Vedran’s statement is absolutely correct. See why…

![](emotes_1.png "emote")

… and of course because MS says it’s DDL 😊 ( [microsoft.com](https://learn.microsoft.com/en-us/sql/t-sql/statements/statements?view=sql-server-ver17#data-definition-language) )

And partitioning is DML… I don’t know, here too it’s at least system columns that define the partitioning.

---

## How TRUNCATE works

I’d like to say I’ll describe it simply, but that’s just my normal description. The topic is really complex ✌️

### 1 – TRUNCATE Command Initiated

```sql
TRUNCATE TABLE dbo.MyTable;
```

- **First action**: Acquire **SCH-M (Schema Modification)** lock on entire table
- **Effect**: Table is completely locked – no reads, no writes, nothing

### 2 – Identify Extents

- DEEP DIVE Extents –> [microsoft.com](https://learn.microsoft.com/en-us/sql/relational-databases/pages-and-extents-architecture-guide?view=sql-server-ver17)
- SQL Server reads IAM pages
- Lists all extents belonging to the table
- **Still holding**: SCH-M lock on table

### 3- Lock Individual Extents

- Places **X (Exclusive)** locks on each extent
- These are regular data locks, NOT schema locks
- **Now holding**:
  - SCH-M lock on table (prevents access)
  - X locks on extents (marks them for deallocation)

### 4 – Log the Operation

- Writes to transaction log: „Deallocate extents 8:8, 8:16, etc.“
- **Still holding**: Both lock types

### 5a – If COMMIT

- Updates IAM – marks extents as free
- **Releases** all X locks on extents
- **Releases** SCH-M lock on table
- Table is accessible again

### 5b – If ROLLBACK

- Discards deallocation markers
- **Releases** all X locks on extents
- **Releases** SCH-M lock on table
- Everything unchanged

### Why Two Different Lock Types?

**SCH-M Lock:**

- „Nobody touch this table AT ALL“
- Typical for DDL operations
- Prevents even metadata queries

**X Locks on Extents:**

- „These specific data blocks are being modified“
- Typical for data operations
- Ensures extents aren’t reused until commit/rollback by other sessions

### My humble Opinion

Given this knowledge, the case is actually clear for me, but how do you see it? Indeed, here no user data is being manipulated; instead, system-level assignments are being adjusted. Consequently, I’ll allow myself, despite my new half-knowledge, to make the following comparison:

„I also don’t say I’m deleting text in a Word document when I quick format the disk and only delete the block allocation.“

![](emotes_2.png "emote")

Yes, I think that’s a nice comparison… Case closed, now a few technically interesting aspects and solutions

---

## Technical Part, Hacks and How2

![](meme_trunc.jpg)

… practical, not technical 😉

### TRUNCATE with Survivor Table (Temporary Table)

Data that is still required is simply moved to a temporary table and retrieved after TRUNCATE

```sql
-- Step 1: Create temp table with rows to keep
	SELECT * INTO #SurvivorRows
	FROM
		MyTable
	WHERE
		DateColumn >= '2024-01-01'

-- Step 2: Truncate the entire table
	TRUNCATE TABLE MyTable

-- Step 3: Re-insert survivor rows
	INSERT INTO MyTable
	SELECT * FROM #SurvivorRows

-- Step 4: Clean up
	DROP TABLE #SurvivorRows
```

### TRUNCATE with PARTITION option (2016++)

Since SQL Server 2016 (every edition) it is possible to specify partitions or ranges of partitions

```sql
-- Truncate specific partitions
	TRUNCATE TABLE MyPartitionedTable
	     WITH (PARTITIONS (2, 4 TO 6))

-- Check partition status
	SELECT
		 partition_number
		,rows
	FROM
		sys.partitions
	WHERE
		OBJECT_NAME(OBJECT_ID) = 'MyPartitionedTable'
```

### TRUNCATE is always a transaction…

…. and must be considered during RESTORING. Carsten illustrated this whole thing very nicely in his publication. I’m just describing it, that has to suffice at this point 😝

Even though we only write **TRUNCATE TABLE**, SQL Server still uses **BEGIN** and **COMMIT TRANSACTION**, which of course is recorded in the TLog. Accordingly, during a POINT IN TIME RECOVERY, the data in the table remains available until the TLog with the corresponding TRANSACTION is restored, or the time of the TRUNCATE transaction has been exceeded.

So you can also restore the data 👌

### Continuously read Transaction log file data with fn_dblog and fn_dump_dblog

Vedran wrote in one of his posts that there’s an undocumented function where you can read log records at runtime. There’s also a very cool article about this on sqlshack.com

---

*NOT recommended for production but only for test / education.*

---

[How to continuously read Transaction log file data directly in a SQL Server database with fn_dblog and fn_dump_dblog](https://www.sqlshack.com/how-to-continuously-read-transaction-log-file-data-directly-in-a-sql-server-database-with-fn_dblog-and-fn_dump_dblog/ "Here we’ll discuss how to read SQL Server transaction logs and provide and insight into how the workload is being captured in the transaction log files.")

---

## Finally

Let’s get to my initially mentioned point that all these SQL Server tips from randoms should be questioned. Because the statement that **truncate is not rollback safe** is simply wrong. The path to this realization was long for me, initiated by the conversation between Vedran and Carsten. I really learned a lot left and right, which I also wanted to record here again for posterity.

![](emotes_3.png "emote")

In the end, it doesn’t matter whether it’s **DDL** or **DML**. In the general SQL Server standard, for example, it’s described as DML, most RDBMSs in dialect with DDL. We’ll just agree on **DDL** and that’s it. Much more exciting is what happens under the hood.

**Best comment from Vedran 🤣**

> „Or you are trying to argue with SQL Certified Master about SQL? Good luck Mr :)“

---

## Links from the text

[Transact-SQL statements – SQL Server](https://learn.microsoft.com/en-us/sql/t-sql/statements/statements?view=sql-server-ver17#data-definition-language "Transact-SQL statements")

[TRUNCATE TABLE (Transact-SQL) – SQL Server](https://learn.microsoft.com/en-us/sql/t-sql/statements/truncate-table-transact-sql?view=sql-server-ver17 "TRUNCATE TABLE removes all rows from a table or specified partitions of a table.")

[SQL SERVER – Rollback TRUNCATE Command in Transaction – SQL Authority with Pinal Dave](https://blog.sqlauthority.com/2010/03/04/sql-server-rollback-truncate-command-in-transaction/ "This is a very common concept that truncate cannot be rolled back. Let us learn in today’s blog post that Rollback TRUNCATE is possible.")

[The internals of SQL Truncate and SQL Delete statements](https://www.sqlshack.com/the-internals-of-sql-truncate-and-sql-delete-statements/ "This article gives you an insight into the SQL truncate and SQL delete commands behavior.")

[How to continuously read Transaction log file data directly in a SQL Server database with fn_dblog and fn_dump_dblog](https://www.sqlshack.com/how-to-continuously-read-transaction-log-file-data-directly-in-a-sql-server-database-with-fn_dblog-and-fn_dump_dblog/ "Here we’ll discuss how to read SQL Server transaction logs and provide and insight into how the workload is being captured in the transaction log files.")

[Truncate (SQL) – Wikipedia](https://en.wikipedia.org/wiki/Truncate_(SQL) "In SQL, the TRUNCATE TABLE statement is a data manipulation language (DML)[1] operation that deletes all rows of a table without causing a triggered action. The result of this operation quickly removes all data from a table, typically bypassing a number of integrity enforcing mechanisms. It was officially introduced in the SQL:2008 standard, as the optional feature F200, “TRUNCATE TABLE statement”.")

[Pages and Extents Architecture Guide – SQL Server](https://learn.microsoft.com/en-us/sql/relational-databases/pages-and-extents-architecture-guide?view=sql-server-ver17 "This guide describes the data structures that are used to manage pages and extents in all versions of SQL Server.")

---

## Full Conversation

{{< details summary="Expand" >}}

**Vedran Kesegic**

In sql server, truncate can be rolled back (if encapsulated within transaction). It is a logged operation.

**Carsten Saastamoinen-Jakobsen**

With DELETE we can specify the WHERE clause and some or all rows can be removed. All deleted rows are logged with BEFORE IMAGE/the data values. With TRUNCATE we can delete all rows or only the rows in one or more partitions, if we have a partition table. The only information logged is the pageid. The physical removing/releasing to unused pages happens in a background task after COMMIT. No data is stored in the log, so less and faster! And it is not possible to restore to point in time because no data is logged. The pageid in the log can already have being ‚released‘ to unused pages and therefore already used to data from another object – table/index. Before COMMIT the pages is still allocated to the table and still with data. If no explicit transaction is specified the transaction is already committed!

**Vedran Kesegic**

„No data is stored in the log“ and „not possible to restore to point in time“ is both incorrect for TRUNCATE. The difference is, truncate logs only deallocation of pages, which is multiple orders of magnitude less (basically insignifficant) compared to DELETE which logs data that is deleted. That is why truncate is „instant“. If you delete eg. 10GB of data, you wait for 10GB to be written to transaction log, which takes time. Truncate logs maybe 1KB for deallocation info, which is instant. If you do not want to delete all rows, you can still use TRUNCATE by storing survivor rows aside before truncating, and inserting them back after truncate. Even better, you can use SWITCH into some dummy table (even with not-partitioned tables) to remove rows quickly, and then insert survivor rows back from that dummy into original table. That is the fastest way to delete when a smaller percent of rows needs to survive.

**Vedran Kesegic**

Obvious difference is that truncate removes all rows from table („truncate table“) or from partition(s), when using „trancate table xy with partitions (…)“. You cannot choose which rows to delete, they all are gone. With delete you can have a WHERE clause to choose which rows to delete. Delete is more appropriate if you need to delete a small percentage of table rows (or partition rows).

**Vedran Kesegic**

Truncate is a metadata operation, requires a different lock (SCH_M, schema modification lock). If also has some restrictins regarding foreign keys etc. Check the documentation for the list of limitations: https://learn.microsoft.com/en-us/sql/t-sql/statements/truncate-table-transact-sql

**Carsten Saastamoinen-Jakobsen**

It is not an argument to call TRUNCATE a DDL statement because a certain lock is used! When statements are categorized, it must be based on what happens and not how a given database system solves the task. Data is deleted, the structure is preserved and only some data may be deleted. When one or more partitions are deleted, the condition is also well-known, but just limited. In previous versions of database systems – and perhaps still – a TRUNCATE was performed by a DROP TABLE + CREATE TABLE. Hence DDL rights. It just shows that it is problematic to categorize based on how it is performed and not based on what actually happens. If we look at the documentation for SQL Server, it is not mentioned that TRUNCATE is a DDL. We may have to recognize that a previous error categorization should not continue to call TRUNCATE a DDL, but recognize that it is a DML. We will also be free from erroneous claims about only deleting all rows, that space is not released, that the transaction cannot be rolled back, …. A DELETE operation without a user-defined transaction cannot be rolled back either! But DELETE is DML and not DDL. TRUNCATE is ‚created‘ for having af fast way of deleting rows, and extended for only deleting some of the rows – DML!!!

**Vedran Kesegic**

No, the SCH-M lock (the „king of all locks“) is not the sole reason why TRUNCATE is DDL. DML writes data (rows in user tables), while DDL writes metadata (rows in system tables, data that describes other/user objects). Truncate happens to write metadata (system tables) and thus is classified as DDL. See the doc: https://learn.microsoft.com/en-us/previous-versions/sql/sql-server-2012/ff848799(v=sql.110)

**Carsten Saastamoinen-Jakobsen**

Can you tell which data is written to the system tables that is not written when removing rows by DELETE? The only additional information is, that with TRUNCATE of all rows without specifying partitions is, that the ‚identity‘ is reset to the initial values. Removing some or all rows with specifying partitions, this value is not reset to the initial value. Empty page are handled in the same way as empty page after DELETE! All indexes are preserved, the table definition is NOT changed, ….

**Vedran Kesegic**

Better than that – you can see for yourself! The exact difference and details are present in transaction log records after you do TRUNCATE and compare that to log records that DELETE generates. Use fn_dblog() function, but only on the test system because it is undocumented and might have an impact.

Or you are trying to say that Microsoft is wrong in documentation? If so, report it to MS so doc can be fixed. But in this case there is nothing to fix.

Or you are trying to argue with SQL Certified Master about SQL? Good luck Mr 🙂

**Carsten Saastamoinen-Jakobsen**

I say that MS is right in the documentations because they are not telling that TRUNCATE is as DDL, because they know that TRUNCATE is a DML!. Of course there is less in the log – it is the idea wit TRUNCATE!!!!!!!! Just te functionality and te reason for implementing TRUNCATE as an alternative to DELETE. But the log is NOT the system tables!!!!! So please tell which system tables are updated as they are updated when CRAETE, ALTER and DROP but NOT updated when INSERT, DELETE or UPDATE.

**Vedran Kesegic**

TRUNCATE modifies internal system tables sys.sysallocunits and sys.sysrowsets. DELETE modifies indexes and stats – see attached pictures. You could do that yourself using fn_dblog as instructed, but I did that for you so you don’t have to. If you want to know more about deep SQL Server internals you can attend one of my trainings, or trainings of other SQL Masters like Brent Ozar, Paul Randal (sqlskills), etc.

**Carsten Saastamoinen-Jakobsen**

Of course they are modified as INSERT DELETE and UPDATE modify this informations. But INSERT, DELETE and UPDATE are still only DML and not DDL. And I am not impressed of your job by showing me this information. If you was showing the same for the other DML statements it would be fine. So maybe you should modify your course material and also shows the same for the other DML statements!!!!

{{< /details >}}
