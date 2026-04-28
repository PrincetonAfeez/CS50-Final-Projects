"""
HospitalityOS — CS50P Final Project Tests
Author: Princeton Afeez

Pytest suite covering all four core functions in project.py.
Run with: pytest test_project.py -v
"""

import pytest
from decimal import Decimal
from project import calculate_shrinkage, validate_audit_entry, parse_tip, generate_restock_actions


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FOR: calculate_shrinkage
# ═══════════════════════════════════════════════════════════════════════════════

class TestCalculateShrinkage:
    """Verify shrinkage detection across normal, zero, and edge-case scenarios."""

    def test_normal_shrinkage(self):
        """Started with 30, sold 10, wasted 2, counted 15 → 3 missing."""
        result = calculate_shrinkage(30, 10, 2, 15, Decimal("24.00"))
        assert result["missing_qty"] == 3
        assert result["shrinkage_loss"] == Decimal("72.00")
        assert result["expected_remaining"] == 18

    def test_no_shrinkage(self):
        """Physical count matches expected — zero loss."""
        result = calculate_shrinkage(30, 10, 2, 18, Decimal("24.00"))
        assert result["missing_qty"] == 0
        assert result["shrinkage_loss"] == Decimal("0.00")

    def test_no_shrinkage_surplus(self):
        """Physical count EXCEEDS expected (found extra stock) — still zero loss."""
        result = calculate_shrinkage(30, 10, 2, 20, Decimal("24.00"))
        assert result["missing_qty"] == 0
        assert result["shrinkage_loss"] == Decimal("0.00")

    def test_total_loss(self):
        """Everything is gone — sold 0, wasted 0, counted 0. All 30 missing."""
        result = calculate_shrinkage(30, 0, 0, 0, Decimal("10.00"))
        assert result["missing_qty"] == 30
        assert result["shrinkage_loss"] == Decimal("300.00")

    def test_all_sold_no_shrinkage(self):
        """Sold every unit, none left, none wasted — clean shift."""
        result = calculate_shrinkage(20, 20, 0, 0, Decimal("15.00"))
        assert result["missing_qty"] == 0
        assert result["shrinkage_loss"] == Decimal("0.00")

    def test_all_wasted(self):
        """Entire stock was wasted (e.g., cooler failure), none missing."""
        result = calculate_shrinkage(10, 0, 10, 0, Decimal("5.00"))
        assert result["missing_qty"] == 0
        assert result["shrinkage_loss"] == Decimal("0.00")

    def test_unit_price_as_string(self):
        """Unit price passed as string should still work (Decimal conversion)."""
        result = calculate_shrinkage(20, 5, 3, 10, "12.50")
        assert result["missing_qty"] == 2
        assert result["shrinkage_loss"] == Decimal("25.00")

    def test_single_unit_missing(self):
        """Edge case: exactly 1 unit of shrinkage."""
        result = calculate_shrinkage(10, 5, 2, 2, Decimal("8.00"))
        assert result["missing_qty"] == 1
        assert result["shrinkage_loss"] == Decimal("8.00")

    def test_negative_count_raises(self):
        """Negative inputs should raise ValueError — counts can't be negative."""
        with pytest.raises(ValueError):
            calculate_shrinkage(-1, 5, 2, 3, Decimal("10.00"))

    def test_negative_sold_raises(self):
        with pytest.raises(ValueError):
            calculate_shrinkage(30, -5, 2, 20, Decimal("10.00"))

    def test_zero_inventory_zero_everything(self):
        """Item with zero starting stock — nothing to lose."""
        result = calculate_shrinkage(0, 0, 0, 0, Decimal("99.00"))
        assert result["missing_qty"] == 0
        assert result["shrinkage_loss"] == Decimal("0.00")


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FOR: validate_audit_entry
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidateAuditEntry:
    """Verify the impossibility guard catches bad manager entries."""

    def test_valid_entry(self):
        """10 sold + 2 waste + 18 on hand = 30, which equals starting. Valid."""
        assert validate_audit_entry(10, 2, 18, 30) is True

    def test_valid_entry_under_total(self):
        """Accounted units less than starting (shrinkage exists but entry is valid)."""
        assert validate_audit_entry(10, 2, 15, 30) is True

    def test_impossible_entry(self):
        """Accounted units exceed starting — someone miscounted."""
        assert validate_audit_entry(20, 5, 10, 30) is False

    def test_exact_match(self):
        """Every unit accounted for perfectly — valid."""
        assert validate_audit_entry(5, 5, 10, 20) is True

    def test_just_over_by_one(self):
        """Off by one — classic fat-finger scenario."""
        assert validate_audit_entry(10, 2, 19, 30) is False

    def test_all_sold(self):
        """Sold everything, nothing wasted, nothing left — valid."""
        assert validate_audit_entry(30, 0, 0, 30) is True

    def test_all_wasted(self):
        """Everything wasted (cooler broke), nothing sold or remaining — valid."""
        assert validate_audit_entry(0, 30, 0, 30) is True

    def test_all_remaining(self):
        """Nothing sold or wasted, all still on shelf — valid."""
        assert validate_audit_entry(0, 0, 30, 30) is True

    def test_zero_starting_with_counts(self):
        """Can't sell what you don't have."""
        assert validate_audit_entry(1, 0, 0, 0) is False

    def test_zero_everything(self):
        """Zero across the board — trivially valid."""
        assert validate_audit_entry(0, 0, 0, 0) is True

    def test_negative_sold_invalid(self):
        """Negative values are always invalid."""
        assert validate_audit_entry(-1, 0, 5, 10) is False

    def test_negative_starting_invalid(self):
        assert validate_audit_entry(0, 0, 0, -5) is False


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FOR: parse_tip
# ═══════════════════════════════════════════════════════════════════════════════

class TestParseTip:
    """Verify tip parsing handles real-world payment terminal inputs."""

    def test_flat_dollar(self):
        """Simple flat amount: '5.00' on any bill."""
        assert parse_tip("5.00", Decimal("50.00")) == Decimal("5.00")

    def test_flat_with_dollar_sign(self):
        """'$5.00' — some terminals prepend the symbol."""
        assert parse_tip("$5.00", Decimal("50.00")) == Decimal("5.00")

    def test_flat_whole_number(self):
        """'10' without decimals should still work."""
        assert parse_tip("10", Decimal("80.00")) == Decimal("10.00")

    def test_percentage_20(self):
        """'20%' of $50 = $10.00."""
        assert parse_tip("20%", Decimal("50.00")) == Decimal("10.00")

    def test_percentage_18(self):
        """'18%' of $100 = $18.00."""
        assert parse_tip("18%", Decimal("100.00")) == Decimal("18.00")

    def test_percentage_15_point_5(self):
        """'15.5%' of $80 = $12.40."""
        assert parse_tip("15.5%", Decimal("80.00")) == Decimal("12.40")

    def test_percentage_with_space(self):
        """'20 %' — some people add a space before the symbol."""
        assert parse_tip("20 %", Decimal("50.00")) == Decimal("10.00")

    def test_zero_tip(self):
        """'0' is a valid (if disappointing) tip."""
        assert parse_tip("0", Decimal("50.00")) == Decimal("0.00")

    def test_zero_percent(self):
        """'0%' — also valid."""
        assert parse_tip("0%", Decimal("50.00")) == Decimal("0.00")

    def test_garbage_input(self):
        """Random text should return $0.00, not crash."""
        assert parse_tip("asdf", Decimal("50.00")) == Decimal("0.00")

    def test_empty_string(self):
        """Empty input should return $0.00."""
        assert parse_tip("", Decimal("50.00")) == Decimal("0.00")

    def test_negative_tip_returns_zero(self):
        """Negative tips are rejected — returns $0.00."""
        assert parse_tip("-5.00", Decimal("50.00")) == Decimal("0.00")

    def test_percentage_on_zero_bill(self):
        """20% of $0 is $0 — shouldn't crash."""
        assert parse_tip("20%", Decimal("0.00")) == Decimal("0.00")

    def test_large_flat_tip(self):
        """Big tipper — $100 flat."""
        assert parse_tip("100.00", Decimal("200.00")) == Decimal("100.00")

    def test_comma_in_amount(self):
        """'1,000' with comma — some people type this way."""
        assert parse_tip("1,000", Decimal("5000.00")) == Decimal("1000.00")

    def test_penny_rounding(self):
        """'15%' of $33.33 = $5.00 (rounded from 4.9995)."""
        result = parse_tip("15%", Decimal("33.33"))
        assert result == Decimal("5.00")


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FOR: generate_restock_actions
# ═══════════════════════════════════════════════════════════════════════════════

class TestGenerateRestockActions:
    """Verify prep-pull vs. shopping-list decisions."""

    def test_prep_when_back_stock_sufficient(self):
        """Item below par but back storage covers it — prep pull only."""
        items = [
            {"name": "Wagyu Burger", "physical_count": 5, "par_level": 15,
             "walk_in_inv": 10, "freezer_inv": 5}
        ]
        result = generate_restock_actions(items)
        assert len(result["prep_list"]) == 1
        assert result["prep_list"][0]["name"] == "Wagyu Burger"
        assert result["prep_list"][0]["qty"] == 10
        assert len(result["shopping_list"]) == 0

    def test_shopping_when_back_stock_insufficient(self):
        """Item below par and back storage can't cover — shopping list."""
        items = [
            {"name": "Truffle Fries", "physical_count": 5, "par_level": 25,
             "walk_in_inv": 3, "freezer_inv": 0}
        ]
        result = generate_restock_actions(items)
        assert len(result["shopping_list"]) == 1
        assert result["shopping_list"][0]["name"] == "Truffle Fries"
        assert result["shopping_list"][0]["qty"] == 20
        assert len(result["prep_list"]) == 0

    def test_no_action_when_above_par(self):
        """Item at or above par level — no action needed."""
        items = [
            {"name": "Caesar Salad", "physical_count": 15, "par_level": 10,
             "walk_in_inv": 5, "freezer_inv": 0}
        ]
        result = generate_restock_actions(items)
        assert len(result["prep_list"]) == 0
        assert len(result["shopping_list"]) == 0

    def test_at_exact_par(self):
        """Exactly at par — no action."""
        items = [
            {"name": "House Salad", "physical_count": 10, "par_level": 10,
             "walk_in_inv": 5, "freezer_inv": 0}
        ]
        result = generate_restock_actions(items)
        assert len(result["prep_list"]) == 0
        assert len(result["shopping_list"]) == 0

    def test_mixed_items(self):
        """Multiple items: one needs prep, one needs shopping, one is fine."""
        items = [
            {"name": "Burger", "physical_count": 5, "par_level": 15,
             "walk_in_inv": 20, "freezer_inv": 0},
            {"name": "Lobster", "physical_count": 2, "par_level": 8,
             "walk_in_inv": 1, "freezer_inv": 0},
            {"name": "Fries", "physical_count": 30, "par_level": 20,
             "walk_in_inv": 10, "freezer_inv": 5},
        ]
        result = generate_restock_actions(items)
        assert len(result["prep_list"]) == 1
        assert result["prep_list"][0]["name"] == "Burger"
        assert len(result["shopping_list"]) == 1
        assert result["shopping_list"][0]["name"] == "Lobster"

    def test_empty_inventory_list(self):
        """No items to check — returns empty lists."""
        result = generate_restock_actions([])
        assert result["prep_list"] == []
        assert result["shopping_list"] == []

    def test_zero_physical_zero_back_stock(self):
        """Line is empty AND back storage is empty — must order."""
        items = [
            {"name": "Steak", "physical_count": 0, "par_level": 10,
             "walk_in_inv": 0, "freezer_inv": 0}
        ]
        result = generate_restock_actions(items)
        assert len(result["shopping_list"]) == 1
        assert result["shopping_list"][0]["qty"] == 10

    def test_back_stock_exactly_covers_shortage(self):
        """Back stock matches shortage exactly — prep, not shop."""
        items = [
            {"name": "Salmon", "physical_count": 3, "par_level": 8,
             "walk_in_inv": 3, "freezer_inv": 2}
        ]
        result = generate_restock_actions(items)
        assert len(result["prep_list"]) == 1
        assert result["prep_list"][0]["qty"] == 5
        assert len(result["shopping_list"]) == 0

    def test_back_stock_one_short(self):
        """Back stock is one unit short of covering — goes to shopping."""
        items = [
            {"name": "Salmon", "physical_count": 3, "par_level": 8,
             "walk_in_inv": 3, "freezer_inv": 1}
        ]
        result = generate_restock_actions(items)
        assert len(result["shopping_list"]) == 1
        assert len(result["prep_list"]) == 0

    def test_multiple_items_all_need_shopping(self):
        """Bad night — everything is low and no back stock."""
        items = [
            {"name": "Item A", "physical_count": 0, "par_level": 10,
             "walk_in_inv": 0, "freezer_inv": 0},
            {"name": "Item B", "physical_count": 1, "par_level": 5,
             "walk_in_inv": 0, "freezer_inv": 0},
        ]
        result = generate_restock_actions(items)
        assert len(result["shopping_list"]) == 2
        assert len(result["prep_list"]) == 0
