#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of cepces.
#
# cepces is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cepces is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cepces.  If not, see <http://www.gnu.org/licenses/>.
#
"""Check that version numbers are consistent across all files."""

import re
import sys
from pathlib import Path


def get_pyproject_version(root: Path) -> str | None:
    """Extract version from pyproject.toml."""
    path = root / "pyproject.toml"
    with open(path) as f:
        for line in f:
            if match := re.match(r'^version\s*=\s*"([^"]+)"', line):
                return match.group(1)
    return None


def get_init_version(root: Path) -> str | None:
    """Extract version from src/cepces/__init__.py."""
    path = root / "src" / "cepces" / "__init__.py"
    with open(path) as f:
        for line in f:
            if match := re.match(r'^__version__\s*=\s*"([^"]+)"', line):
                return match.group(1)
    return None


def get_selinux_version(root: Path) -> str | None:
    """Extract version from selinux/cepces.te."""
    path = root / "selinux" / "cepces.te"
    with open(path) as f:
        for line in f:
            if match := re.match(r"^policy_module\(cepces,\s*([^)]+)\)", line):
                return match.group(1)
    return None


def main() -> int:
    """Check version consistency across all files."""
    # Find the project root (where pyproject.toml is)
    root = Path(__file__).parent.parent

    versions = {
        "pyproject.toml": get_pyproject_version(root),
        "src/cepces/__init__.py": get_init_version(root),
        "selinux/cepces.te": get_selinux_version(root),
    }

    # Check for missing versions
    missing = [f for f, v in versions.items() if v is None]
    if missing:
        print("Could not extract version from:")
        for f in missing:
            print(f"  {f}")
        return 1

    # Check for mismatches
    unique = set(versions.values())
    if len(unique) != 1:
        print("Version mismatch detected:")
        for f, v in versions.items():
            print(f"  {f}: {v}")
        return 1

    version = unique.pop()
    print(f"All versions match: {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
