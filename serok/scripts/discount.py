#!/usr/bin/env python3
"""Hitung rasio dan diskon listing NFT terhadap floor.

Usage:
  python3 discount.py <listing_price> <floor_price> [max_ratio]

Contoh:
  python3 discount.py 0.01 20
  -> ratio 0.0005, discount 99.95 persen, flag True dengan ambang default 0.05

Keluar dengan kode 0 dan mencetak JSON. Argumen harus angka positif.
Tidak melakukan pembelian, tidak mengakses jaringan, dan tidak menyimpan rahasia.
"""
import json
import sys


def main(argv):
    if len(argv) not in (3, 4):
        print("usage: discount.py <listing_price> <floor_price> [max_ratio]", file=sys.stderr)
        return 2
    try:
        listing = float(argv[1])
        floor = float(argv[2])
        max_ratio = float(argv[3]) if len(argv) == 4 else 0.05
    except ValueError:
        print("error: harga harus angka", file=sys.stderr)
        return 2
    if listing <= 0 or floor <= 0 or max_ratio <= 0:
        print("error: harga dan ambang harus positif", file=sys.stderr)
        return 2
    ratio = listing / floor
    discount_pct = (1.0 - ratio) * 100.0
    print(json.dumps({
        "listing": listing,
        "floor": floor,
        "ratio": round(ratio, 6),
        "discount_pct": round(discount_pct, 2),
        "is_mispriced": ratio <= max_ratio,
        "max_ratio": max_ratio,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
