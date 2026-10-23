"""Wit Grocery Planning Preview 0.1.0: supplied inputs only, no API calls."""
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 iJaspers. See LICENSE.
import json
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation

ID = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
UNITS = {"g", "ml", "each"}
MAX_INPUT_BYTES = 1024 * 1024
MAX_DEPTH = 32

def money(value):
    whole, part = divmod(value, 100)
    return f"{whole}.{part:02d}"

def load_input(path):
    with open(path, 'rb') as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise InputError('Input exceeds 1 MiB UTF-8 limit')
    text = raw.decode('utf-8'); depth = 0; quoted = False; escaped = False
    for char in text:
        if quoted:
            if escaped: escaped = False
            elif char == chr(92): escaped = True
            elif char == '"': quoted = False
        elif char == '"': quoted = True
        elif char in '[{':
            depth += 1
            if depth > MAX_DEPTH: raise InputError('JSON nesting exceeds 32 levels')
        elif char in ']}': depth -= 1
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj: raise InputError('Duplicate JSON object key')
            obj[key] = value
        return obj
    return json.loads(text, object_pairs_hook=unique)


class InputError(ValueError):
    pass


def whole(x, label, allow_zero=True):
    if isinstance(x, bool) or not isinstance(x, int) or x < (0 if allow_zero else 1) or x > 1000000:
        raise InputError(f"{label} must be a bounded nonnegative integer")
    return x


def ident(x, label):
    if not isinstance(x, str) or not ID.fullmatch(x):
        raise InputError(f"{label} invalid identifier")
    return x


def cents(x, label):
    if not isinstance(x, str) or len(x) > 64:
        raise InputError(f"{label} must be a decimal string of at most 64 characters")
    try:
        n = Decimal(x)
    except (InvalidOperation, ValueError):
        raise InputError(f"{label} invalid money") from None
    if not n.is_finite() or n < 0 or n > 100000 or n.as_tuple().exponent < -2:
        raise InputError(f"{label} invalid CAD amount")
    return int(n * 100)


def calculate(doc):
    if not isinstance(doc, dict):
        raise InputError("root must be an object")
    limits = {'recipes': 100, 'plan': 100, 'pantry': 1000, 'offers': 1000}
    for key, limit in limits.items():
        if key not in doc or not isinstance(doc[key], list):
            raise InputError(f'{key} must be an explicitly supplied list')
        if len(doc[key]) > limit:
            raise InputError(f'{key} exceeds {limit} entries')
        if key in {'recipes', 'plan'} and not doc[key]:
            raise InputError(f'{key} must not be empty')
        if any(not isinstance(row, dict) for row in doc[key]):
            raise InputError(f'{key} entries must be objects')
    budget = cents(doc.get("budget_cad"), "budget_cad")
    pantry = {}
    for entry in doc.get("pantry", []):
        name = ident(entry["item"], "pantry item")
        unit = entry["unit"]
        if unit not in UNITS:
            raise InputError("unsupported unit")
        key = (name, unit)
        if key in pantry:
            raise InputError("duplicate pantry entry")
        pantry[key] = whole(entry["qty"], "pantry qty")
    recipes = {}
    for entry in doc.get("recipes", []):
        name = ident(entry["id"], "recipe id")
        if name in recipes:
            raise InputError("duplicate recipe")
        ingredients = entry.get('ingredients')
        if not isinstance(ingredients, list) or not ingredients or len(ingredients) > 100:
            raise InputError('recipe ingredients require 1 to 100 entries')
        if any(not isinstance(ing, dict) for ing in ingredients):
            raise InputError('ingredients must be objects')
        needs = defaultdict(int)
        for ing in ingredients:
            item = ident(ing["item"], "ingredient")
            unit = ing["unit"]
            if unit not in UNITS:
                raise InputError("unsupported unit")
            needs[(item, unit)] += whole(ing["qty"], "ingredient qty", False)
        recipes[name] = needs
    required = defaultdict(int)
    for meal in doc.get("plan", []):
        name = ident(meal["recipe"], "plan recipe")
        if name not in recipes:
            raise InputError(f"unknown recipe {name}")
        count = whole(meal["count"], "meal count", False)
        for key, qty in recipes[name].items():
            required[key] += qty * count
    offers = defaultdict(list)
    for row in doc.get("offers", []):
        item = ident(row["item"], "offer item")
        unit = row["unit"]
        if unit not in UNITS:
            raise InputError("unsupported unit")
        qty = whole(row["pack_qty"], "pack_qty", False)
        cost = cents(row["price_cad"], "price_cad")
        vendor = ident(row["store"], "store")
        offers[(item, unit)].append((qty, cost, vendor))
    lines, missing = [], []
    known_total = 0
    for (item, unit), needed in sorted(required.items()):
        in_stock = min(needed, pantry.get((item, unit), 0))
        buy_qty = needed - in_stock
        if buy_qty == 0:
            lines.append({"item": item, "unit": unit, "needed": needed, "pantry_used": in_stock,
                          "buy_qty": 0, "store": None, "packs": 0, "cost_cad": "0.00"})
            continue
        options = []
        for pack_qty, price, store in offers.get((item, unit), []):
            pack_count = (buy_qty + pack_qty - 1) // pack_qty
            options.append((price * pack_count, pack_qty * pack_count - buy_qty, store, pack_count))
        if not options:
            missing.append({"item": item, "unit": unit, "buy_qty": buy_qty})
            lines.append({"item": item, "unit": unit, "needed": needed, "pantry_used": in_stock,
                          "buy_qty": buy_qty, "store": None, "packs": None, "cost_cad": None})
            continue
        cost, surplus, store, packs = min(options)
        known_total += cost
        lines.append({"item": item, "unit": unit, "needed": needed, "pantry_used": in_stock,
                      "buy_qty": buy_qty, "store": store, "packs": packs,
                      "excess_qty": surplus, "cost_cad": money(cost)})
    status = "UNKNOWN_MISSING_PRICE" if missing else ("WITHIN_BUDGET" if known_total <= budget else "OVER_BUDGET")
    return {"status": status, "budget_cad": money(budget),
            "known_basket_total_cad": money(known_total),
            "total_is_complete": not missing, "missing_prices": missing,
            "lines": lines, "disclaimer": "Supplied offers only; not independently verified live pricing or measured savings."}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tool.py fixture.json")
    try:
        obj = load_input(sys.argv[1])
        result = calculate(obj)
    except (InputError, KeyError, TypeError, ValueError, RecursionError, OSError) as ex:
        print(json.dumps({"error": str(ex)}), file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
