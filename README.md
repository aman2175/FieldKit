# Fieldkit

Multi-tenant **field-service product**: jobs, technicians, SLAs, a **dispatch engine**
(score → auto-assign or exception queue), an **event + dbt warehouse**, and a
**governed AI clerk** (drafts jobs, reads metrics — never assigns a tech).

This is a **product / portfolio system** aimed at a strong mid-level AI/Data +
backend role. It is **not** a tutorial, not a ServiceTitan clone, not a chatbot
on a spreadsheet.

**Agents:** open this folder in Cursor and follow [`AGENTS.md`](AGENTS.md) first.
That file is the contract. Do not “simplify” it.

---

## Problem

Field shops run on email + spreadsheets. Two dispatchers send two trucks. The
weekly “late jobs” number does not match the board. A second brand must not see
the first brand’s customers.

Fieldkit is the system of record for the job, the engine that schedules the
boring majority, and one warehouse number for the week.

## What the AI does

- Turns a messy email into a **draft** job (human or policy confirm).
- Answers “% auto-assigned / SLA this week” via **metrics tools** only.

It does **not** pick the technician. That is the dispatch engine.

## Hire bar (must all be true)

| Layer | Must exist |
|---|---|
| Backend | FastAPI, Postgres, **RLS**, job lock, audit |
| Engine | **Scoring, auto-assign policy, exception queue, `% auto-assigned`** |
| DE | **Events** (Kafka/Redpanda), lake, **Dagster, dbt**, SLA metrics |
| Cloud | **Terraform** on Azure, HTTPS, Key Vault, CI gates |
| AI | Draft + `get_metric` only, golden evals, no `run_sql` |

Full rules, forbidden shortcuts, and build order: **[AGENTS.md](AGENTS.md)**.

## Demo (10 minutes)

Create/ingest job → event on the bus → dbt row → score or auto-assign or
exception → ask the assistant → number matches warehouse → tenant B sees nothing.

## Stack

Python 3.12, FastAPI, Postgres 16 + RLS, Redis, Redpanda, dbt, Dagster, React,
Azure + Terraform, Azure OpenAI (GPT-4o / 4.1, or gpt-4o-mini for drafts).

## How to work in Cursor

1. File → Open Folder → this `Fieldkit` directory (not Permit Tracker).
2. New chat: *“Read AGENTS.md. Pair with me. Teach. Do not scaffold a starter.
   First slice: tenancy + RLS + isolation test.”*
3. You type the code after he explains. Say **do it now** only when you want
   him to write a slice.

## License

Private portfolio unless you add one later.
