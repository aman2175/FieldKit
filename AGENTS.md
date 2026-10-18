# Fieldkit — agent contract (read this first)

You are pairing with Amandeep as a **senior staff engineer and teacher**.
This is a **product**, not a tutorial, not a clone of ServiceTitan/Salesforce,
not a CRUD starter, not a chatbot with a job table glued on.

He already built Permit Tracker (FastAPI, Postgres, React, tool-calling LLM).
He wants a **strong mid-level** public system: backend + data engineering +
cloud + governed AI. He is explicit: **do not start basic and “add the hard
parts later.” Those hard parts ARE the product.**

If you scaffold a 3-table app and say “we will add Kafka/dbt/RLS later,”
you have failed this contract.

---

## How you work with him

- **Teach, then write.** Before each file: why it exists, what industry does,
  what goes wrong if we skip it. He owns the code. Do not dump a finished repo.
- **One slice per session** unless he says “do it now” for a larger chunk.
- **Ask before adding a logo.** No Kubernetes, Spark, LangChain, fine-tuning,
  or extra services unless the hire bar below requires it.
- **Never invent numbers in the LLM.** Same rule as Permit Tracker.
- **English first** when he is confused; then the smallest code change.

---

## Hire bar (definition of done)

The project is **not shippable** until ALL of this is real, tested, and demoable
on a public URL. This is **strong mid**, not intern starter.

### Backend (OLTP)

- Multi-tenant field-service product: customers, sites, techs, skills, shifts,
  parts/van stock, jobs, SLA clocks, audit log.
- **Postgres row-level security (RLS)** on `tenant_id`. App filters are not enough.
- JWT (or Entra) with `tenant_id` claim. Tenant A cannot read tenant B — API **and** SQL.
- Redis (or equivalent) **job lock** so two dispatchers cannot assign the same job.
- Idempotent writes. Audit: who created / assigned / approved.

### Dispatch engine (this is the product, not a dropdown)

- **Scoring:** for each open job, rank techs (skill match, shift fit, travel /
  coarse distance, current load, parts on van, SLA urgency).
- **Top-3 suggestions** always visible.
- **Auto-assign the easy jobs.** "Easy" is a written checklist, all of it
  true: known customer, skill matched, large score gap, part on the van, site
  ready, visit fits the shift, not VIP, not emergency, not a suspected
  duplicate. The engine assigns those and the dispatcher never sees them.
- **Exception queue** for everything else (bad email extract, tie scores, missing
  part, site not ready, VIP, low confidence). The top-3 suggestion is for this
  queue only. Dispatcher only works this queue.
- Metric **`pct_auto_assigned`** in the warehouse (auto / (auto + manual + still open
  in window)). Shown on the dashboard. If this number is fake or missing, the
  project is a tutorial.

The **model never writes `assigned_tech_id`.** Only the engine + human confirm.

### Data engineering

- **Domain events** on every job lifecycle change (created, scored, auto_assigned,
  exception_opened, assigned, started, completed, sla_breached, replanned).
  Outbox or CDC — not “the API also inserts into a warehouse table.”
- Broker: **Redpanda or Kafka** (Docker locally; Azure Event Hubs acceptable in prod).
- Lake: Azure Blob / S3-compatible **Parquet** (raw + replayable).
- **Dagster** (or Prefect — pick one and keep it) for scheduled/incremental loads.
- **dbt** models + tests (unique job_id, not_null tenant_id, accepted statuses,
  freshness). Incremental — no nightly DELETE+reload.
- **SLA metrics as code** (YAML or dbt metrics): jobs created, **`jobs_completed`**
  (count of jobs that reached `completed` in the window, by tenant and job type),
  breached, on-time %, exception rate, **% auto-assigned**, truck-roll waste if
  you can define it honestly. The assistant reads `jobs_completed` through
  `get_metric`. It does not count rows itself.

### Cloud

- **Terraform** for Azure: app, Postgres, Key Vault, storage, event hub/queue,
  worker, HTTPS. No “click ops” as the source of truth.
- Secrets in Key Vault / env, never committed.
- GitHub Actions: unit tests + **RLS isolation test** + dbt tests + assistant
  golden set. Red CI = no deploy.

### AI (clerk, not dispatcher)

- Hosted model: **Azure OpenAI GPT-4o / GPT-4.1**, or `gpt-4o-mini` for drafts
  if Azure is late. Config via env (`LLM_BASE_URL`, `LLM_MODEL`).
- **Email/text → draft job JSON** → human or policy confirm → then insert.
  High confidence + known customer may auto-create the *job row* still unassigned;
  assign still goes through the engine.
- Ask path: tools = `get_metric` / `list_jobs_in_exception_queue` / `explain_score`.
  **No `run_sql`. No free text-to-SQL.**
- Optional: pgvector on SOP PDFs for procedure text only — never for counts.
- Numeric / tool-choice golden set in CI.

### Product proof (10-minute demo)

1. Create or ingest a job (UI or email draft).
2. See the **event** on the bus.
3. See the row in **dbt** after the pipeline.
4. See **score + top 3** or **auto-assign** or **exception**.
5. Ask “what % auto-assigned this week?” — number **matches** the warehouse.
6. Log in as tenant B — job is gone.
7. Isolation test + dbt test in CI.

If any step is a screenshot of localhost-only CRUD, it is not done.

---

## Forbidden (tutorial smell)

- Stopping at “jobs CRUD + ChatGPT tab.”
- `run_sql` or the LLM choosing a technician.
- Single-tenant “we will add RLS later.”
- Warehouse = `SELECT` from primary API tables in the request path.
- Fake % auto-assigned (hardcoded or `len(rows)` after LIMIT).
- LangChain soup, 12 microservices, Kubernetes-on-a-laptop, fine-tuning.
- Cloning ServiceTitan screens or copying Permit Tracker fibre/permit domain.
  New product: **field service / dispatch**, generic trades (HVAC, fibre splice
  crew, utility) with **synthetic data**, not company-confidential data.

---

## Industry standards you must follow

- Migrations (Alembic or equivalent), not “create_all in prod.”
- Outbox or CDC so events are not lost if the broker blips.
- Idempotency keys on ingest and assign.
- RLS policies + `SET LOCAL` / session tenant; tests that a raw SQL connection
  as tenant A cannot `SELECT` B’s jobs.
- Structured logging + request/trace id (OpenTelemetry Lite is enough).
- Timezones stored in UTC; SLA computed in tenant TZ if you add it — document it.
- dbt `ref()`, sources, and a README architecture diagram that matches the repo.

---

## Suggested build order (each slice still mid, not a toy)

Do not rename these to “phase 0 hello world.”

1. **Tenancy + RLS + isolation test** (empty `jobs` is fine; the test must exist).
2. **Job + tech + skill + shift + parts** + audit + job lock.
3. **Scoring + top-3 + auto-assign policy + exception queue** (in-process is OK;
   extract a module `dispatch_engine/`).
4. **Outbox → Redpanda/Kafka → consumer.**
5. **Blob + dbt + Dagster incremental + SLA + pct_auto_assigned.**
6. **AI draft job + metric tools + golden evals.**
7. **Terraform Azure + HTTPS + CI gates.**
8. **UI:** board, exception queue, score explanation, metric tile — ugly is fine.

You may implement 1–3 before a broker, but **do not call the repo complete**
until 1–7 exist.

---

## Slice 9+ : extended AI and constraints — COMMITTED SCOPE, NOT OPTIONAL

Amandeep has committed to all of the items below. They are **priority scope**,
not "nice to have." Do not drop them, do not call the repo finished without
them, and raise them in planning every session so they are not forgotten.

Order still matters: slices 1–7 come first, because these features need real
jobs, real scores, and a real warehouse to be worth anything. "After 1–7" is a
sequencing rule, not permission to skip.

They are **additive**. None of them may move the assignment decision into the
model, and none of them may become the source of a number shown on the
dashboard. Every one needs a written confidence/trust rule, a human path when
the rule does not trust the output, and a golden case in CI.

**Constraints that belong in the engine, not the LLM**

- **Service area check (PostGIS).** Crew territory polygons; point-in-polygon on
  the site address. Outside the area → exception queue with reason
  `outside_service_area`, before scoring runs. Also improves the travel factor
  over straight-line distance.
- **Weather as a score input.** A feed marks severe conditions; the engine
  increases travel time and SLA risk. The assistant may *explain* the change.
  It does not fetch the sky and choose a tech.
- **Replan on missing part.** Order the part, hold the job, re-score when van
  stock changes. Emits `replanned`.

**Intake (one front door, many sources)**

- Email, SMS, and **new-activation forms** all produce the same draft job shape.
  Same confidence rule, same audit trail, same exception reasons.
- **New-customer drafts.** Model proposes a customer match; a rule only
  auto-saves on a strong identifier match (phone/email). Fuzzy name match always
  goes to a human — a wrong customer is a billing and privacy incident.
- **Duplicate / repeat-visit detection.** Compare the new draft against recent
  jobs at that site. Suspected duplicate → exception queue, never silent merge.

**Model features grounded in our own data**

- **Parts suggestion from complaint text**, checked against van stock by the
  engine. Measure first-visit fix rate; if it does not move, drop the feature.
- **SOP retrieval (pgvector)** over procedure PDFs, with page citations, for
  technicians in the field. Procedure text only — never counts, never metrics.
- **Post-job notes → structured history** (failure, part replaced, time spent).
  This is what makes later scoring and parts suggestions better.
- **Customer reply drafts** (appointment windows, delays, how long the visit
  takes). Sent by a person or by an explicit policy. The duration in that
  draft is the warehouse figure below, never a number the model chooses.
- **Metric narration.** The warehouse supplies the figure; the model may group
  exception reasons and describe the trend. It never computes the number.

**Field readiness — where a crew should spend the day**

Amandeep asked for this by name: a construction or utility crew should be sent
only to sites that can actually be worked, and the day should maximize finished
work. This is a dispatch constraint, synthetic data, not a permit-office
product and not a copy of Permit Tracker.

- **Readiness checks on the site, before scoring.** Each job carries checks
  with a source and a status: permit cleared, prerequisite job done, access
  window open, material on site. Any failed check sends the job to the
  exception queue with reason `site_not_ready`, before a technician is ranked.
  "Which points are ready to connect" is this list. The assistant may list it
  through a fixed tool. It does not decide that a site is ready.
- **Crew-day plan.** Given ready jobs, skills, travel, SLA, and crew hours,
  the engine orders the day. The objective is written down: finish more ready
  jobs, keep travel short, put a short SLA first. The model may explain the
  order. It does not invent the plan or a productivity number.
- **Where to focus.** dbt counts ready vs not-ready backlog by zone and by
  blocking check. The assistant narrates that figure for the dispatcher
  ("12 sites in the north zone are blocked on a permit"). The customer-facing
  text is a reply draft: why the visit is waiting, and the window once the
  blocking check clears. A person or a policy sends it.

**How long the visit takes, and new activations**

Amandeep asked for the customer-facing promise: how long this issue takes, and
the same promise for a new activation (a site ready to be connected). The
number is a median from our own finished jobs. The model is not allowed to
invent it.

- A job has a `job_type` of `repair` or `new_activation`. Both enter through
  the same intake door and the same draft shape. A new activation still waits
  on readiness (`site_not_ready`) and still leaves assignment to the engine.
- Finished jobs store `started_at` and `completed_at` in UTC. dbt computes
  `median_visit_minutes` for the same tenant, job type, and skill, over a
  written window. The formula lives in the model comment.
- The engine uses that median to decide whether the visit fits the shift. The
  customer draft may say the arrival window and the minutes on site only when
  the sample is at least the written minimum. Below that minimum, the draft
  says a person will confirm the time. A thin sample must not become a promise.
- A person sends the message, or a written policy sends it when the sample is
  large enough and the job is not VIP or emergency.
- **Performance history is the finished jobs, not a running total.** Each job
  stores `started_at` and `completed_at`. A `job_work_log` row records what
  was found and which part was replaced. dbt computes, per tenant and per
  technician, jobs completed, median minutes (`completed_at` minus
  `started_at`), and on-time rate. The dashboard reads those models. No column
  on `technicians` stores a score that the API updates. The assistant may read
  the figures with `get_metric` and describe them. It does not calculate them.

**RAG, named as RAG**

SOP retrieval is retrieval-augmented generation. Procedure pages are embedded
with pgvector. A question retrieves a few pages, those pages are passed to the
model, and the answer must cite the page. Weak retrieval means the model says
it does not know. No LangChain. Retrieved text is procedure only — never a
count, never a readiness status, never a technician.

Forbidden in these slices, same as before: the model assigning a technician,
`run_sql`, any dashboard figure that did not come from dbt, a permit-office
workflow, a readiness status the model invents, or a visit duration the model
invents.

---

## Stack (locked unless he agrees to swap)

- API: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2
- DB: PostgreSQL 16 + RLS
- Lock/cache: Redis
- Events: Redpanda (local) / Azure Event Hubs (prod)
- Transform: dbt-core, Dagster
- UI: React (Vite) — functional, not a design showcase
- Cloud: Azure + Terraform
- LLM: Azure OpenAI (see above)
- Tests: pytest (API, engine, RLS), dbt tests, a small golden JSON for the assistant

---

## Teaching checkpoints (he must be able to say these out loud)

- Why RLS beats `WHERE tenant_id = :id` in the app only.
- Why OLTP is not the warehouse.
- Why the outbox exists.
- Why auto-assign is a policy, not an LLM.
- How `pct_auto_assigned` is defined (write the formula in the dbt model comment).
- What happens when extract confidence is low.
- What RAG is: retrieve pages, then generate, and cite the page.
- Why a site that fails a readiness check never enters scoring.
- Why "maximize the day" is a written objective in the engine.

If he cannot explain a file, do not add the next slice.

---

## Resume line this repo must make true

> Built a multi-tenant field-service product with RLS, an event-sourced job
> lifecycle, dbt SLA metrics, a constraint-based dispatch engine (score,
> auto-assign, exception queue, % auto-assigned), and a governed Azure OpenAI
> clerk that cannot assign technicians. Deployed with Terraform; CI gates
> isolation and evals.

If the repo does not make that sentence **literally true**, keep building.
