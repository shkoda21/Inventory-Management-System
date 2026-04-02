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

See [ARCHITECTURE.md](./spirit_inventory/ARCHITECTURE.md) for deeper design discussion.

---

## Deployment

```
Client → Nginx (reverse proxy) → Gunicorn (WSGI) → Django → PostgreSQL
```

See [DEPLOYMENT.md](./spirit_inventory/DEPLOYMENT.md) for full setup details.

---

## Screenshots

> All data shown is fictional. Any resemblance to real businesses or individuals is accidental.

### Dashboard

![Dashboard](spirit_inventory/screenshots/dashboard.png)
*Overview showing total bottles in stock, total bottles produced, number of batches,
and number of retailers. Includes a list of recent sell orders and low-stock alerts
by batch and bottle capacity.*

### Inventory

![Type list](spirit_inventory/screenshots/type_list.png)
*Product type list with type names and batch count. Filterable by name.*

![Barcode list](spirit_inventory/screenshots/barcode_list.png)
*Barcode list showing name, code, and bottle count.
Filterable by name, partial code, or exact code.*

![Batch list](spirit_inventory/screenshots/batch_list.png)
*Batch list showing product type, alcohol volume, bottles in stock, bottles produced,
and start/end dates. Filterable by name, type, and date range.*

![Batch detail](spirit_inventory/screenshots/batch_detail.png)
*Individual batch view showing base info, ingredients, and all tracked bottles.*

![Product list](spirit_inventory/screenshots/product_list.png)
*Bottle list showing type, batch, bottle number, capacity, stock status, production date,
and price. Filterable by bottle number, type, capacity, stock status, and date.*

![Product detail](spirit_inventory/screenshots/product_detail.png)
*Individual bottle view showing base info and full operation history for that bottle.*

### Sales

![Sell order list](spirit_inventory/screenshots/sell_order_list.png)
*Sell order list with summary totals: gross revenue, total returns, and net profit.
Each row shows retailer name, date, item count, order total, return amount, and payment status.
Filterable by retailer name, order number, status, and date range.*

![Sell order detail](spirit_inventory/screenshots/sell_order_detail.png)
*Individual sell order view showing base info, invoice, payment details, sold items,
and any associated return orders.*

![Sell order create](spirit_inventory/screenshots/sell_order_create.png)
*Sell order create form.*

![Sell order — add items](spirit_inventory/screenshots/sell_order_add_items.png)
*Item selection view: add bottles by range or individually.
Filterable by type, capacity, batch, and bottle number. Updates without page refresh.*

### Invoices

![Invoice list](spirit_inventory/screenshots/invoice_list.png)
*Invoice list showing number, date, organization, store name, total, and payment status.
Filterable by invoice number, organization or store name, status, and date range.*

![Invoice detail](spirit_inventory/screenshots/invoice_detail.png)
*Individual invoice view showing retailer info (snapshot at creation), line items,
and full payment history.*

![Generate invoice](spirit_inventory/screenshots/invoice_create.png)
*Invoice create form.*

![Invoice — DOCX export](spirit_inventory/screenshots/invoice_docx.png)
*Example of a generated invoice exported to DOCX format.*

### Returns

![Return order list](spirit_inventory/screenshots/return_order_list.png)
*Return order list showing sell order number, retailer, return date, item count, and total.*

![Return order detail](spirit_inventory/screenshots/return_order_detail.png)
*Individual return order view showing base info, return total, and returned bottles.*

![Return order create](spirit_inventory/screenshots/return_order_create.png)
*Return order create form, pre-populated with eligible items from the original sell order.*

### Write-offs

![Write-off list](spirit_inventory/screenshots/write_off_list.png)
*Write-off list showing total write-off cost and all written-off items.
Filterable by reason, bottle number, type, batch, capacity, and date range.*

![Write-off detail](spirit_inventory/screenshots/write_off_detail.png)
*Individual write-off order view showing base info and affected bottles.*

![Write-off create — item selection](spirit_inventory/screenshots/write_off_create.png)
*Write-off create form with bottle selection.
Filterable by type, batch, capacity, and bottle number.*

### Expenses & Analysis

![Expenses](spirit_inventory/screenshots/expenses_part1.png) (spirit_inventory/screenshots/expenses_part2.png)
*Expense tracker showing total cost, filterable expense list,
and a breakdown chart by type and date.*

![Analysis](spirit_inventory/screenshots/analysis.png)
*Financial summary showing gross revenue, total returns, net revenue, total expenses,
and trend graphs.*

### Compliance & Audit

![Audit log](spirit_inventory/screenshots/audit.png)
*Audit log with filtering and a full list of recorded system actions.*

![TTB report](spirit_inventory/screenshots/ttb_report_part1.png) (spirit_inventory/screenshots/ttb_report_part2.png)
*TTB regulatory report with filtering by date range and alcohol volume.*

![TTB export — by volume](spirit_inventory/screenshots/ttb_export_report.xlsx)
*Example TTB export file aggregated by alcohol volume and bottle capacity.*

![TTB export — by retailer](spirit_inventory/screenshots/ttb_export_retailer.png)
*Example TTB export file aggregated by retailer.*

![TTB export — additional retailer breakdown](spirit_inventory/screenshots/ttb_export_retailer_detail.png)
*Additional retailer breakdown report.*

---

## Note on source code

This is a portfolio-safe version of a production system. Some business-critical logic has been intentionally simplified or removed (advanced reporting internals, financial calculations, export implementation details) to protect proprietary business logic. Screenshots illustrate the removed sections.

---

## About

This system was designed and built as a real production application for an operating business — not as a practice project. It handles live inventory, real invoices, and regulatory reporting requirements.
