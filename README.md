# HospitalityOS
#### Video Demo: <URL HERE>
#### Description:

HospitalityOS is a text-based restaurant operations simulator built entirely in Python. It models the core systems that power a real restaurant — front desk seating, point-of-sale ordering, inventory management, labor cost auditing, and nightly shrinkage detection — all orchestrated through a single-process CLI with file-backed state persistence.

This project was born from firsthand experience. I have spent over two decades as a Restaurant General Manager, and I built HospitalityOS to bridge the gap between the operational knowledge I carry every day and the system design skills I am developing as I transition into a career in software architecture. Every feature in this system reflects a real workflow I have performed thousands of times: seating a walk-in party during a Friday rush, running a POS checkout with modifiers and loyalty redemptions, reconciling end-of-night inventory against what the register says should be left, and catching shrinkage that points to theft or miscount.

The CS50P final project submission surfaces four core functions in `project.py` that extract the testable business logic from the larger HospitalityOS system. These functions represent the financial and operational engine that sits underneath the interactive CLI.

## What Each File Does

**project.py** — The CS50P entry point. Contains four top-level functions and a `main()` that ties them into an interactive nightly audit demo. The functions are:

- `calculate_shrinkage()` takes the starting inventory count, confirmed sales, confirmed waste, a physical count, and the item's unit price. It returns a dictionary containing the number of missing units, the dollar value of that loss, and what the expected remaining count should have been. This logic was extracted from the reconciliation block inside `inventorymanager.py`, where it was originally tangled with `input()` calls and print statements. Isolating it makes it testable and reusable.

- `validate_audit_entry()` is the impossibility guard. In a real restaurant, a manager entering end-of-night counts can fat-finger a number — claiming 20 sold, 5 wasted, and 10 remaining when the building only held 30 units total. That adds up to 35, which is physically impossible. This function catches that before it corrupts the data. It returns a simple boolean: valid or not.

- `parse_tip()` handles the two formats servers encounter on payment terminals every night: flat dollar amounts like `"$5.00"` and percentage-based tips like `"20%"`. It strips dollar signs and commas, detects the percentage symbol, calculates accordingly, and returns a rounded Decimal. Invalid input returns zero gracefully instead of crashing the checkout flow. This logic was extracted from the `Transaction.apply_tip()` method in `models.py`.

- `generate_restock_actions()` implements the prep-pull versus shopping-list decision that every closing manager makes. For each menu item below its par level, the function checks whether the walk-in cooler and freezer have enough back stock to cover the shortage. If they do, the item goes on the prep list (an internal move). If they do not, it goes on the shopping list (an external vendor order). This mirrors exactly how I have made these decisions for years — you never order what you already have in the building.

**test_project.py** — Fifty-five pytest cases organized into four test classes, one per function. Tests cover normal operations, edge cases (zero inventory, items at exact par level, surplus counts), boundary conditions (back stock exactly covering a shortage versus falling one unit short), error handling (negative inputs, garbage tip strings, empty lists), and real-world scenarios (comma-formatted dollar amounts, penny rounding on percentage tips). Each test class uses descriptive method names that read as plain-English specifications of the business rules.

**main.py** — The master orchestrator for the full HospitalityOS system. Handles boot sequence, staff login (ID-based, demo-only authentication), and the main menu loop that dispatches to the front desk, service floor POS, waitlist, and manager office. Uses `atexit` to ensure state is saved even on unexpected exits.

**digitalpos.py** — The point-of-sale ordering engine. Supports fuzzy menu item lookup (exact match, case-insensitive, substring, and token-based search), modifier attachments with configurable limits, real-time bill display with tax and auto-gratuity for large parties, loyalty point redemption, and a full checkout flow that records transactions to the daily ledger and security log. Manager-gated actions (void, comp, inventory adjust) require PIN authentication through a decorator pattern.

**inventorymanager.py** — The nightly inventory and shrinkage auditor. Loads the menu catalog from CSV, pulls POS sales data from the shared JSON state file, walks the manager through a physical count for each item, detects unknown loss (shrinkage), calculates financial impact, generates prep and shopping lists, and appends a permanent audit trail to a log file. Includes a duplicate-proof shopping list writer using regex checks against existing entries.

**models.py** — The financial brain of the system. Built on Pydantic v2 for automatic field validation. Contains the `MenuItem` model (with inventory tracking across line, walk-in, and freezer storage), the `Cart` model (with computed properties for subtotal, tax, auto-gratuity, loyalty discount, and grand total using Decimal math to avoid floating-point drift), the `Transaction` model, the `DailyLedger` for rolling revenue and tip totals, the `Staff` model with shift clock and simplified overtime pay calculation, and the append-only `SecurityLog` for audit events.

**validator.py** — Centralized input validation utilities shared across all modules. Provides type-safe input loops for integers, decimals, staff IDs, names, emails, dates, times, and yes/no prompts. Includes a high-value verification function that asks twice when a number exceeds a configurable threshold, and a Pydantic-based health check runner that validates data dictionaries against model schemas.

**app_context.py** — Defines `SessionContext`, the composition root that bundles the menu catalog, daily ledger, floor map, and authenticated user into a single object passed through the system. Each session gets a unique `run_id` for audit correlation across log entries.

**hospitality_models.py** — Domain models for the front-of-house: `Guest` (with loyalty points, feedback, and tax-exempt flags), `FloorMap` (20-table layout with status tracking), `WaitlistManager`, and table seating logic.

**database.py** — Persistence layer that reads and writes the CSV catalogs (`menu.csv`, `staff.csv`) and the JSON state file (`restaurant_state.json`). Handles integrity checks on boot to ensure required data files exist before the system starts.

**laborcostauditor.py** — Manager-only labor reporting tools for shift pay estimation and staffing analysis.

**launcher.py** — Splash screen and preflight checks before handing off to `main.py`.

**setup_os.py** — First-run setup script that creates required directories, seeds sample data files, and generates a settings template.

## Design Decisions

**Decimal over float for all money.** Every financial calculation in HospitalityOS uses Python's `Decimal` type rather than `float`. This is not academic — floating-point arithmetic produces rounding errors that accumulate in real POS systems. A restaurant processing hundreds of transactions per day cannot tolerate a register that is off by pennies, because those pennies compound into audit discrepancies that look like theft.

**CSV and JSON over a database.** This is a deliberate non-goal documented in `docs/non-goals.md`. The system uses flat files for persistence because the project's purpose is to demonstrate architectural thinking, not database administration. The trade-off is explicitly acknowledged: CSV catalogs are human-readable, easy to seed, and sufficient for a single-process demo. A production system would use PostgreSQL — and I document exactly where that boundary sits.

**Composition root pattern.** Rather than passing five or six objects through every function call, the system bundles shared state into a `SessionContext` object created at boot. This keeps function signatures clean and makes the dependency graph visible. It is the same pattern used in real dependency injection frameworks, simplified for a CLI application.

**Manager authentication via decorator.** Sensitive operations (voiding items, comping tables, adjusting inventory) are gated by a `@require_manager_auth` decorator that checks credentials before the function body executes. This separates the authorization concern from the business logic — the `void_item` function does not need to know how authentication works, only that it has been satisfied.

**Append-only security log.** Every sensitive action (payments, voids, comps, inventory adjustments) writes to an append-only log file with a timestamp, staff ID, authorizing manager ID, action type, and a unique run ID for correlation. This mirrors how real POS systems maintain audit trails for loss prevention teams.

**Extracting testable functions for CS50P.** The four functions in `project.py` were not invented for this submission — they are the same logic that powers the full system, pulled out of interactive loops and stripped of `input()` calls so that pytest can exercise them with controlled inputs and deterministic outputs. This approach lets the submission stand alone while the complete HospitalityOS project continues to serve as a system architecture portfolio piece.

## Architecture Documentation

The full project includes an architecture documentation suite in the `/docs` directory: C4 diagrams at four levels of detail, Architecture Decision Records for every major design choice, a non-functional requirements table, a threat model sketch, module boundary documentation, and an observability strategy explaining the run ID correlation system. These documents are intended as a system architect portfolio and go well beyond what CS50P requires, but they represent the larger goal this project serves.
