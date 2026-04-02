For a feature overview and deployment summary, see README.md. This document covers design decisions and trade-offs.

# 🏗️ Architecture Overview

## 1. Core Design Principle

The system is built around a **non-standard inventory model**:

> Each product is a unique, trackable entity (1 row = 1 bottle)

This differs from traditional inventory systems where:

* 1 row = quantity

---

## 2. Bottle-Level Tracking

### Why?

Alcohol production requires:

* traceability
* compliance
* precise reporting

### Trade-offs

| Advantage          | Cost            |
| ------------------ | --------------- |
| Full traceability  | Higher DB size  |
| Accurate reporting | Complex queries |
| Auditability       | More joins      |

---

## 3. Invoice Design

### Problem

Retailer data may change over time.

### Solution

Snapshot fields:

* `org_name_snapshot`
* `license_snapshot`
* `address_snapshot`

### Result

Invoices remain legally valid even if retailer data changes.

---

## 4. TTB Reporting Logic

TTB reports aggregate data by:

* alcohol volume (per batch)
* bottle capacity

### Key Insight

Same product type can have:

* different batches
* different alcohol %

👉 Must group by batch-level data, not product type alone.

---

## 5. Role-Based Access Control

Instead of Django Groups:

* Custom role system implemented

### Reason

* strict control over actions
* easier mapping to business roles
* predictable permission logic

---

## 6. Audit Logging Strategy

### Chosen Approach

Explicit logging via function calls in views.

### Why NOT signals?

* hidden behavior
* harder debugging
* less control

### Result

* transparent system behavior
* easier debugging
* predictable logs

---

## 7. Service Boundaries

Apps are separated by responsibility:

* `inventory` → core domain
* `operations` → business actions
* `invoices` → financial layer
* `reports` → analytics
* `audit` → cross-cutting concern

---

## 8. Scalability Considerations

* PostgreSQL for relational integrity
* modular app structure
* separation of concerns
* ability to extract services if needed

---

## 9. Security Considerations

* role-based permissions
* protected views
* audit logging
* environment-based settings

---