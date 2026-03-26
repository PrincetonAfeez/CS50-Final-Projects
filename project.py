"""
HospitalityOS — CS50P Final Project
Author: Princeton Afeez

A restaurant operations engine that demonstrates core business logic
extracted from the full HospitalityOS system (github.com/PrincetonAfeez/HospitalityOS).

This module surfaces four testable functions that power the financial,
inventory, and tipping subsystems of a real restaurant simulator:

  - calculate_shrinkage:    Detects unknown inventory loss (theft/miscount)
  - validate_audit_entry:   Guards against impossible count submissions
  - parse_tip:              Handles "$5.00" flat and "20%" percentage tips
  - generate_restock_actions: Decides prep-pull vs. shopping-list per item
"""

import csv
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


# ── Business constants (mirrored from settings/restaurant_defaults.py) ──────

TAX_RATE = Decimal("0.0925")       # 9.25% sales tax
GRATUITY_RATE = Decimal("0.18")    # 18% auto-gratuity
GRATUITY_THRESHOLD = 6             # Party size that triggers auto-grat


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTION 1 — SHRINKAGE CALCULATOR
# Source logic: inventorymanager.py → run_inventory_audit() reconciliation block
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_shrinkage(starting_inv, sold, waste, physical_count, unit_price):
    """
    Determine unknown inventory loss by comparing what SHOULD remain
    against what a manager PHYSICALLY counted at end of shift.

    Args:
        starting_inv  (int):     Total units in the building at shift open
        sold          (int):     Units confirmed sold through POS
        waste         (int):     Units logged as waste (dropped, expired, etc.)
        physical_count(int):     Actual units the manager counted tonight
        unit_price    (Decimal): Menu price per unit (for dollar-loss calculation)

    Returns:
        dict with keys:
            "missing_qty"  (int):     Units unaccounted for (0 if none missing)
            "shrinkage_loss" (Decimal): Dollar value of missing units
            "expected_remaining" (int): What the math says should be left

    Raises:
        ValueError: If any count is negative
    """
    # Guard against garbage data — negative counts break the math
    if any(v < 0 for v in [starting_inv, sold, waste, physical_count]):
        raise ValueError("Inventory counts cannot be negative.")

    unit_price = Decimal(str(unit_price))

    # The core equation: what SHOULD be on the shelf after known removals
    expected_remaining = starting_inv - sold - waste

    # If physical count is less than expected, the gap is shrinkage
    if physical_count < expected_remaining:
        missing_qty = expected_remaining - physical_count
        shrinkage_loss = (missing_qty * unit_price).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )
    else:
        # Physical count meets or exceeds expectation — no shrinkage
        missing_qty = 0
        shrinkage_loss = Decimal("0.00")

    return {
        "missing_qty": missing_qty,
        "shrinkage_loss": shrinkage_loss,
        "expected_remaining": expected_remaining,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTION 2 — AUDIT ENTRY VALIDATOR (the "Impossibility Guard")
# Source logic: inventorymanager.py → InventoryError check inside audit loop
# ═══════════════════════════════════════════════════════════════════════════════

def validate_audit_entry(sold, waste, physical_count, starting_inv):
    """
    Verify that a manager's end-of-night counts don't violate physical reality.

    The rule: you cannot account for more units than the building held.
    If sold + waste + physical_count > starting_inv, somebody fat-fingered
    a number or double-counted — and the system must reject the entry.

    Args:
        sold           (int): Units the manager confirms were sold
        waste          (int): Units the manager confirms were wasted
        physical_count (int): Units physically remaining on shelves
        starting_inv   (int): Total units at shift open (line + walk-in + freezer)

    Returns:
        bool: True if the entry is logically valid, False if impossible
    """
    if any(v < 0 for v in [sold, waste, physical_count, starting_inv]):
        return False

    # The impossibility check: total accounted units cannot exceed supply
    return (sold + waste + physical_count) <= starting_inv


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTION 3 — TIP PARSER
# Source logic: models.py → Transaction.apply_tip() method
# ═══════════════════════════════════════════════════════════════════════════════

def parse_tip(tip_input, bill_total):
    """
    Convert a raw tip string into a Decimal dollar amount.

    Supports two formats servers encounter daily:
      - Flat dollar:  "5.00" or "$5.00"  → returns Decimal("5.00")
      - Percentage:   "20%" or "20 %"    → returns 20% of bill_total

    Args:
        tip_input  (str):     Raw string from the payment terminal
        bill_total (Decimal): Pre-tax subtotal the percentage applies to

    Returns:
        Decimal: Calculated tip amount rounded to the cent,
                 or Decimal("0.00") if the input cannot be parsed
    """
    bill_total = Decimal(str(bill_total))

    try:
        cleaned = str(tip_input).strip()

        # Handle percentage tips: "20%", "15.5%", "20 %"
        if "%" in cleaned:
            numeric_part = cleaned.replace("%", "").replace("$", "").strip()
            percentage = Decimal(numeric_part)
            return (bill_total * percentage / 100).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )

        # Handle flat dollar tips: "5.00", "$5.00", "$12"
        numeric_part = cleaned.replace("$", "").replace(",", "").strip()
        tip = Decimal(numeric_part)

        if tip < 0:
            return Decimal("0.00")

        return tip.quantize(Decimal("0.01"), ROUND_HALF_UP)

    except (InvalidOperation, ValueError, ArithmeticError):
        return Decimal("0.00")


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTION 4 — RESTOCK ACTION GENERATOR
# Source logic: inventorymanager.py → prep vs. shopping decision block
# ═══════════════════════════════════════════════════════════════════════════════

def generate_restock_actions(inventory_items):
    """
    For each item below par level, decide: pull from back storage (prep)
    or add to the external shopping list (order from vendor).

    Business rule from real restaurant ops:
      - If walk-in + freezer stock covers the shortage → PREP (internal move)
      - If back storage is insufficient → SHOP (external purchase needed)
      - If item is at or above par → no action needed

    Args:
        inventory_items (list of dict): Each dict must have keys:
            "name"         (str): Item display name
            "physical_count" (int): Current units on the line
            "par_level"    (int): Minimum units needed for next service
            "walk_in_inv"  (int): Units in walk-in cooler
            "freezer_inv"  (int): Units in freezer storage

    Returns:
        dict with keys:
            "prep_list"     (list of dict): Items to pull from back storage
                Each entry: {"name": str, "qty": int}
            "shopping_list" (list of dict): Items to order from vendors
                Each entry: {"name": str, "qty": int}
    """
    prep_list = []
    shopping_list = []

    for item in inventory_items:
        physical = item["physical_count"]
        par = item["par_level"]

        # Only act if the line is below the minimum needed for service
        if physical < par:
            shortage = par - physical
            back_stock = item["walk_in_inv"] + item["freezer_inv"]

            if back_stock >= shortage:
                # We have enough in back — just move it to the line
                prep_list.append({"name": item["name"], "qty": shortage})
            else:
                # Back storage can't cover it — need to order
                shopping_list.append({"name": item["name"], "qty": shortage})

    return {
        "prep_list": prep_list,
        "shopping_list": shopping_list,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — Interactive demo tying all four functions together
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Run an interactive nightly manager audit that demonstrates all four
    core functions in a realistic restaurant closing workflow.
    """
    print("═" * 55)
    print(f"{'HOSPITALITYOS v4.0 — NIGHTLY AUDIT ENGINE':^55}")
    print(f"{'CS50P Final Project — Princeton Afeez':^55}")
    print("═" * 55)

    # ── Load sample inventory (simulates menu.csv data) ──────────────────
    sample_inventory = [
        {"name": "Wagyu Burger", "unit_price": Decimal("24.00"),
         "starting_inv": 30, "physical_count": 0, "par_level": 15,
         "walk_in_inv": 10, "freezer_inv": 5},
        {"name": "Truffle Fries", "unit_price": Decimal("12.00"),
         "starting_inv": 50, "physical_count": 0, "par_level": 25,
         "walk_in_inv": 5, "freezer_inv": 0},
        {"name": "Caesar Salad", "unit_price": Decimal("16.00"),
         "starting_inv": 20, "physical_count": 0, "par_level": 10,
         "walk_in_inv": 12, "freezer_inv": 0},
        {"name": "NY Strip Steak", "unit_price": Decimal("42.00"),
         "starting_inv": 15, "physical_count": 0, "par_level": 8,
         "walk_in_inv": 2, "freezer_inv": 1},
    ]

    audit_results = []

    print("\n[ PHASE 1: SHIFT RECONCILIATION ]\n")

    for item in sample_inventory:
        print(f"📋  {item['name'].upper()}  (started with {item['starting_inv']} units)")
        print(f"    Unit price: ${item['unit_price']}")

        # ── Collect manager input with validation loop ───────────────
        while True:
            try:
                sold = int(input("    Sold today: "))
                waste = int(input("    Waste/comps: "))
                physical = int(input("    Physical count now: "))
            except ValueError:
                print("    ⚠️  Please enter whole numbers only.\n")
                continue

            # FUNCTION 2: Validate before accepting
            if not validate_audit_entry(sold, waste, physical, item["starting_inv"]):
                print(
                    f"    ❌  IMPOSSIBLE: sold({sold}) + waste({waste}) + "
                    f"on-hand({physical}) = {sold + waste + physical}, "
                    f"but building only held {item['starting_inv']}. Re-count.\n"
                )
                continue

            break

        # FUNCTION 1: Calculate shrinkage
        result = calculate_shrinkage(
            item["starting_inv"], sold, waste, physical, item["unit_price"]
        )

        # Update physical count for restock logic
        item["physical_count"] = physical

        if result["missing_qty"] > 0:
            print(
                f"    🔴  SHRINKAGE: {result['missing_qty']} units missing "
                f"(${result['shrinkage_loss']} loss)"
            )
        else:
            print("    ✅  No shrinkage detected.")

        audit_results.append({"item": item["name"], **result, "sold": sold, "waste": waste})
        print()

    # ── PHASE 2: Restock decisions ───────────────────────────────────────
    print("─" * 55)
    print("[ PHASE 2: RESTOCK ACTIONS ]\n")

    # FUNCTION 4: Generate prep and shopping lists
    restock = generate_restock_actions(sample_inventory)

    if restock["prep_list"]:
        print("🧊  PREP PULL (move from back storage to line):")
        for entry in restock["prep_list"]:
            print(f"    → {entry['name']}: pull {entry['qty']} units")
    else:
        print("🧊  PREP PULL: Nothing needed — line is stocked.")

    print()

    if restock["shopping_list"]:
        print("🛒  SHOPPING LIST (order from vendors):")
        for entry in restock["shopping_list"]:
            print(f"    → {entry['name']}: order {entry['qty']} units")
    else:
        print("🛒  SHOPPING LIST: Nothing to order tonight.")

    # ── PHASE 3: Tip calculation demo ────────────────────────────────────
    print("\n" + "─" * 55)
    print("[ PHASE 3: TIP PROCESSING DEMO ]\n")

    # Sum up total revenue from what was sold
    total_revenue = sum(
        r["sold"] * Decimal(str(
            next(i["unit_price"] for i in sample_inventory if i["name"] == r["item"])
        ))
        for r in audit_results
    )

    print(f"    Tonight's gross sales: ${total_revenue}")
    tip_input = input("    Enter sample tip (e.g. '5.00', '$20', '18%'): ").strip()

    # FUNCTION 3: Parse the tip
    tip_amount = parse_tip(tip_input, total_revenue)
    print(f"    💰  Calculated tip: ${tip_amount}")

    # ── Final summary ────────────────────────────────────────────────────
    total_shrinkage = sum(r["shrinkage_loss"] for r in audit_results)
    total_missing = sum(r["missing_qty"] for r in audit_results)

    print("\n" + "═" * 55)
    print(f"{'END OF SHIFT SUMMARY':^55}")
    print("═" * 55)
    print(f"    Gross Sales:       ${total_revenue:>10}")
    print(f"    Tip Collected:     ${tip_amount:>10}")
    print(f"    Total Shrinkage:   ${total_shrinkage:>10}  ({total_missing} units)")
    print(f"    Prep Pulls:        {len(restock['prep_list']):>10} items")
    print(f"    Shopping Orders:   {len(restock['shopping_list']):>10} items")
    print("═" * 55)
    print("    ✅  Audit complete. Goodnight, Chef.\n")


if __name__ == "__main__":
    main()
