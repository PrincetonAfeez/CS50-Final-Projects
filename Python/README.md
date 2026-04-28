# CS50P Final Project

## Description

This is a command-line Python app that acts like a restaurant closing checklist. You enter what was sold, wasted, and left on hand, and the program shows what is missing and how much that loss costs.

The app helps you close out a shift without guessing. It checks whether your numbers make sense, reads tips the way people actually enter them (like `"$5"` or `"20%"`), and tells you what to restock by separating quick prep pulls from items that need to be ordered.

The four functions are separate so each one does one clear job: shrinkage math, inventory sanity checks, tip parsing, and restock decisions. Keeping them split makes the code easier to read, easier to test, and easier to fix when one part changes. Money values use `Decimal` instead of `float` because tiny rounding errors add up over many transactions, and in a restaurant audit even a few cents off can look like missing cash.

## What the program does
- Calculates inventory shrinkage
- Checks if inventory counts make sense
- Parses tips like `"$5"` or `"20%"`
- Builds restock actions (`prep_list` and `shopping_list`)

## Demo flow in `main()`
1. Inventory input and shrinkage check
2. Restock actions
3. Tip parsing demo

At the end, it prints a short summary with sales, tip, shrinkage, and restock totals.

## Run It

```bash
python project.py
```

## Run Tests

```bash
pytest test_project.py
```
