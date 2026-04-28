"""
CS50P Final Project

This program simulates a restaurant closing workflow.
It includes inventory checks, restock decisions, and tip parsing.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def calculate_shrinkage(starting_inv, sold, waste, physical_count, unit_price):
    """
    Compare expected inventory to physical count and calculate shrinkage.
    """
    if any(v < 0 for v in [starting_inv, sold, waste, physical_count]):
        raise ValueError("Inventory counts cannot be negative.")

    unit_price = Decimal(str(unit_price))
    expected_remaining = starting_inv - sold - waste

    if physical_count < expected_remaining:
        missing_qty = expected_remaining - physical_count
        shrinkage_loss = (missing_qty * unit_price).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )
    else:
        missing_qty = 0
        shrinkage_loss = Decimal("0.00")

    return {
        "missing_qty": missing_qty,
        "shrinkage_loss": shrinkage_loss,
        "expected_remaining": expected_remaining,
    }


def validate_audit_entry(sold, waste, physical_count, starting_inv):
    """
    Check if sold + waste + physical is possible based on starting inventory.
    """
    if any(v < 0 for v in [sold, waste, physical_count, starting_inv]):
        return False

    return (sold + waste + physical_count) <= starting_inv


def parse_tip(tip_input, bill_total):
    """
    Parse a tip string.
    Accepts flat dollars like "$5.00" and percentages like "20%".
    """
    bill_total = Decimal(str(bill_total))

    try:
        cleaned = str(tip_input).strip()

        if "%" in cleaned:
            numeric_part = cleaned.replace("%", "").replace("$", "").strip()
            percentage = Decimal(numeric_part)
            return (bill_total * percentage / 100).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )

        numeric_part = cleaned.replace("$", "").replace(",", "").strip()
        tip = Decimal(numeric_part)

        if tip < 0:
            return Decimal("0.00")

        return tip.quantize(Decimal("0.01"), ROUND_HALF_UP)

    except (InvalidOperation, ValueError, ArithmeticError):
        return Decimal("0.00")


def generate_restock_actions(inventory_items):
    """
    Build prep and shopping lists for items below par.
    """
    prep_list = []
    shopping_list = []

    for item in inventory_items:
        physical = item["physical_count"]
        par = item["par_level"]

        if physical < par:
            shortage = par - physical
            back_stock = item["walk_in_inv"] + item["freezer_inv"]

            if back_stock >= shortage:
                prep_list.append({"name": item["name"], "qty": shortage})
            else:
                shopping_list.append({"name": item["name"], "qty": shortage})

    return {
        "prep_list": prep_list,
        "shopping_list": shopping_list,
    }


def main():
    """
    Run a simple end-of-day restaurant audit demo.
    """
    print("=" * 55)
    print("Restaurant Closing Audit")
    print("CS50P Final Project")
    print("=" * 55)

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

    print("\nPhase 1: Inventory Audit\n")

    for item in sample_inventory:
        print(f"{item['name']} (started with {item['starting_inv']} units)")
        print(f"    Unit price: ${item['unit_price']}")

        while True:
            try:
                sold = int(input("    Sold today: "))
                waste = int(input("    Waste/comps: "))
                physical = int(input("    Physical count now: "))
            except ValueError:
                print("    Please enter whole numbers only.\n")
                continue

            if not validate_audit_entry(sold, waste, physical, item["starting_inv"]):
                print(
                    f"    Invalid numbers: sold({sold}) + waste({waste}) + "
                    f"on-hand({physical}) = {sold + waste + physical}, "
                    f"but started with only {item['starting_inv']}. Try again.\n"
                )
                continue

            break

        result = calculate_shrinkage(
            item["starting_inv"], sold, waste, physical, item["unit_price"]
        )

        item["physical_count"] = physical

        if result["missing_qty"] > 0:
            print(
                f"    Shrinkage: {result['missing_qty']} units missing "
                f"(${result['shrinkage_loss']} loss)"
            )
        else:
            print("    No shrinkage detected.")

        audit_results.append({"item": item["name"], **result, "sold": sold, "waste": waste})
        print()

    print("-" * 55)
    print("Phase 2: Restock Actions\n")

    restock = generate_restock_actions(sample_inventory)

    if restock["prep_list"]:
        print("Prep pull (move from back storage to line):")
        for entry in restock["prep_list"]:
            print(f"    → {entry['name']}: pull {entry['qty']} units")
    else:
        print("Prep pull: nothing needed.")

    print()

    if restock["shopping_list"]:
        print("Shopping list (order from vendors):")
        for entry in restock["shopping_list"]:
            print(f"    → {entry['name']}: order {entry['qty']} units")
    else:
        print("Shopping list: nothing to order.")

    print("\n" + "-" * 55)
    print("Phase 3: Tip Demo\n")

    total_revenue = sum(
        r["sold"] * Decimal(str(
            next(i["unit_price"] for i in sample_inventory if i["name"] == r["item"])
        ))
        for r in audit_results
    )

    print(f"    Tonight's gross sales: ${total_revenue}")
    tip_input = input("    Enter sample tip (e.g. '5.00', '$20', '18%'): ").strip()

    tip_amount = parse_tip(tip_input, total_revenue)
    print(f"    Calculated tip: ${tip_amount}")

    total_shrinkage = sum(r["shrinkage_loss"] for r in audit_results)
    total_missing = sum(r["missing_qty"] for r in audit_results)

    print("\n" + "=" * 55)
    print("End of Shift Summary")
    print("=" * 55)
    print(f"    Gross Sales:       ${total_revenue:>10}")
    print(f"    Tip Collected:     ${tip_amount:>10}")
    print(f"    Total Shrinkage:   ${total_shrinkage:>10}  ({total_missing} units)")
    print(f"    Prep Pulls:        {len(restock['prep_list']):>10} items")
    print(f"    Shopping Orders:   {len(restock['shopping_list']):>10} items")
    print("=" * 55)
    print("    Audit complete.\n")


if __name__ == "__main__":
    main()
