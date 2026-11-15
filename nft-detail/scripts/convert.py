#!/usr/bin/env python3
"""Convert a crypto/fiat amount to IDR, for the nft-detail skill.

Usage: convert.py <amount> <rate_idr_per_unit>
Example: convert.py 0.001 13739998.35  -> 13739.99835
The caller must supply the rate from a quoted, current source and
state that rate and its time in the final answer; this script only
does the arithmetic, it does not fetch a rate.
"""
import sys


def convert(amount: float, rate: float) -> float:
    return amount * rate


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert.py <amount> <rate_idr_per_unit>", file=sys.stderr)
        sys.exit(2)
    print(convert(float(sys.argv[1]), float(sys.argv[2])))
