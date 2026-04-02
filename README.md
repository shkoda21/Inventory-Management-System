# Spirit Inventory System

A production-deployed Django inventory management system built for **batch-based alcohol manufacturing**. Unlike traditional quantity-based inventory systems, this one tracks every bottle as an individual entity — from production through sale, return, or write-off.

Built to satisfy real-world requirements: **TTB regulatory reporting**, **legal invoice compliance**, and **full financial auditability**.

> **Live deployment:** AWS Lightsail · Nginx · Gunicorn · PostgreSQL

---

## Why bottle-level tracking?

Most inventory systems store `product → quantity`. Alcohol manufacturing requires more:

- Each bottle belongs to a specific batch with its own alcohol volume (proof)
- TTB reporting must aggregate by proof *and* capacity — bottles from the same product type but different batches must be reported separately
- Invoices must remain legally valid even if a retailer's license or address changes later
- Every action — login, sale, return, write-off — must be auditable

This system is designed around those constraints from the ground up.

---

## Features

**Bottle-level inventory**
Each `Product` row is one physical bottle, identified by batch, capacity, and bottle number. All operations track individual bottles, not quantities.

**Full operational lifecycle**
Production batches → sales → returns → write-offs, all with complete audit trails.

**Multi-role access control**
Five roles with fine-grained permissions: Admin, Supervisor, Manager, Viewer, Reader. Implemented as a custom role system rather than Django Groups for predictable, business-aligned permission logic.

**Invoice system**
- Bottles are grouped by `(type, capacity, unit_price)` on invoices — bottle numbers intentionally excluded
- Retailer data (name, license, address) is snapshot-frozen at invoice creation for legal consistency
- Multiple payments per invoice supported, with partial payment tracking
- Export to DOCX

**TTB regulatory reporting**
Aggregates sales by `(alcohol_volume, capacity)` across batches. Because the same product type can span batches with different proofs, grouping by batch-level data — not product type — is essential for correct TTB reporting. Export to XLSX.

**Audit logging**
Explicit logging calls in views — no signals or middleware magic. Login/logout captured via Django signals. Every system action is transparent and debuggable.

**Expense tracking**
Internal cost tracking with reporting support.

**Retailer management**
One organization can have multiple store locations, each with its own license. Bulk import via XLSX.

---

## Roles & permissions

| Role       | Manage users | Admin panel | Write operations | Delete | Expenses | TTB export | Audit log |
|------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Admin      | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Supervisor | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manager    | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Viewer     | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Reader     | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django (Python) |
| Database | PostgreSQL (production) · SQLite (local dev) |
| Application server | Gunicorn |
| Web server | Nginx (reverse proxy) |
| Hosting | AWS Lightsail |

---

## Project structure

```
settings/
├── base.py          # Shared settings
├── local.py         # SQLite, DEBUG=True
└── production.py    # PostgreSQL, DEBUG=False

apps/
├── accounts/        # Custom user model + role system
├── inventory/       # Core domain: batches, bottles, product types
├── operations/      # Sales, returns, write-offs
├── invoices/        # Invoice generation, payments, DOCX export
├── expenses/        # Expense tracking
├── reports/         # TTB aggregation, XLSX export
└── audit/           # Action logging
```

---

## Architecture notes

**Service boundaries**
Apps are separated by responsibility. `inventory` owns the core domain. `operations` handles business actions against it. `invoices` is a separate financial layer. `reports` and `audit` are cross-cutting concerns with no write access to core domain models.

**Invoice snapshots**
Snapshot fields (`org_name_snapshot`, `license_snapshot`, `address_snapshot`) freeze retailer data at invoice creation. This ensures invoices remain legally valid even when retailer records are updated later.

**Audit logging design choice**
Signals were deliberately avoided. Explicit function calls in views make system behavior transparent — easier to debug, easier to reason about, no hidden side effects.

**Settings split**
`base.py → local.py / production.py` pattern allows clean environment separation without environment variable sprawl.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for deeper design discussion.

---

## Deployment

```
Client → Nginx (reverse proxy) → Gunicorn (WSGI) → Django → PostgreSQL
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for full setup details.

---

## Screenshots

> *(will Add later here)*

---

## Note on source code

This is a portfolio-safe version of a production system. Some business-critical logic has been intentionally simplified or removed (advanced reporting internals, financial calculations, export implementation details) to protect proprietary business logic. Screenshots illustrate the removed sections.

---

## About

This system was designed and built as a real production application for an operating business — not as a practice project. It handles live inventory, real invoices, and regulatory reporting requirements.
