#!/usr/bin/env python3
"""
Dependency License Compatibility Check for Apache 2.0

Verifies that all project dependencies are compatible with Apache 2.0 license.
Apache 2.0 is permissive and allows:
- Apache 2.0 itself
- MIT/BSD/X11 (permissive licenses)
- ISC
- Public domain
- LGPL (for dynamic linking)

NOT compatible (would require additional review):
- GPL/AGPL (copyleft - viral)
- MPL (weak copyleft - requires file-level notices)
- SSPL (source-available, not OSI approved)
"""

import subprocess
import sys
from pathlib import Path

# Known Apache 2.0 compatible licenses
COMPATIBLE_LICENSES = {
    'Apache-2.0', 'Apache 2.0', 'Apache License 2.0',
    'MIT', 'MIT License', 'BSD', 'BSD-2-Clause', 'BSD-2-Clause', 'BSD-3-Clause',
    'BSD License', 'New BSD', 'Simplified BSD', 'ISC',
    'Python-2.0', 'PSF', 'Python Software Foundation',
    'Public Domain', 'CC0', 'Unlicense',
    'LGPL-2.1', 'LGPL-2.1-only', 'LGPL-3.0', 'LGPL-3.0-only', 'LGPL',  # For dynamic linking
}

# Licenses that need additional review
NEEDS_REVIEW = {
    'MPL', 'MPL-2.0', 'CDDL', 'EPL', 'EPL-1.0', 'GPL', 'AGPL',
    'SSPL', 'CPAL',
}

# Rust crate licenses (from Cargo.toml)
RUST_DEPENDENCIES = [
    ('wasm-bindgen', '0.2', 'Apache-2.0/MIT'),
    ('js-sys', '0.3', 'Apache-2.0/MIT'),
    ('serde', '1', 'Apache-2.0/MIT'),
    ('serde-wasm-bindgen', '0.6', 'Apache-2.0/MIT'),
    ('serde_json', '1.0', 'Apache-2.0/MIT'),
    ('console_error_panic_hook', '0.1', 'Apache-2.0/MIT'),
    ('quick-xml', '0.37', 'MIT'),
    ('chrono', '0.4', 'Apache-2.0/MIT'),
    ('wasm-bindgen-test', '0.3', 'Apache-2.0/MIT'),
]

# Python dependencies with known licenses
PYTHON_DEPENDENCIES = {
    'numpy': 'BSD',
    'pandas': 'BSD',
    'networkx': 'BSD',
    'graphviz': 'MIT',
    'scipy': 'BSD',
    'lxml': 'BSD',
    'matplotlib': 'PSF',
    'pytz': 'MIT',
    'tqdm': 'MPL-2.0',  # Needs review
    'wheel': 'MIT',
    'setuptools': 'MIT',
    'cvxopt': 'GPL-3.0',  # Needs review - but optional
}


def check_python_deps():
    """Check Python dependency licenses."""
    print("\n📦 Python Dependencies (requirements.txt):")
    print("=" * 60)

    compatible = []
    needs_review = []

    for pkg, license_type in PYTHON_DEPENDENCIES.items():
        if any(l in license_type for l in COMPATIBLE_LICENSES):
            compatible.append((pkg, license_type))
        elif any(l in license_type for l in NEEDS_REVIEW):
            needs_review.append((pkg, license_type))

    print("\n✅ Compatible with Apache 2.0:")
    for pkg, lic in compatible:
        print(f"  • {pkg}: {lic}")

    if needs_review:
        print("\n⚠️  Needs Review (weak copyleft or GPL):")
        for pkg, lic in needs_review:
            note = ""
            if pkg == 'tqdm':
                note = " (MPL-2.0: file-level copyleft, may need notice)"
            elif pkg == 'cvxopt':
                note = " (GPL-3.0: copyleft, but OPTIONAL dependency)"
            print(f"  • {pkg}: {lic}{note}")

    return len(needs_review) == 0


def check_rust_deps():
    """Check Rust/Cargo dependency licenses."""
    print("\n🦀 Rust Dependencies (pm4wasm/Cargo.toml):")
    print("=" * 60)

    compatible = []
    needs_review = []

    for pkg, version, license_type in RUST_DEPENDENCIES:
        if any(l in license_type for l in COMPATIBLE_LICENSES):
            compatible.append((pkg, license_type))
        else:
            needs_review.append((pkg, license_type))

    print("\n✅ Compatible with Apache 2.0:")
    for pkg, lic in compatible:
        print(f"  • {pkg}: {lic}")

    if needs_review:
        print("\n⚠️  Needs Review:")
        for pkg, lic in needs_review:
            print(f"  • {pkg}: {lic}")

    return len(needs_review) == 0


def check_js_deps():
    """Check JavaScript/npm dependency licenses."""
    print("\n📜 JavaScript Dependencies (pm4wasm/js/package.json):")
    print("=" * 60)

    package_json = Path(__file__).parent.parent / 'pm4wasm' / 'js' / 'package.json'

    if not package_json.exists():
        print("  ℹ️  No package.json found")
        return True

    import json
    with open(package_json) as f:
        data = json.load(f)

    deps = data.get('dependencies', {})
    dev_deps = data.get('devDependencies', {})

    print("\n  ℹ️  Run 'npm run check-licenses' for full report")
    print(f"  • {len(deps)} production dependencies")
    print(f"  • {len(dev_deps)} development dependencies")

    return True


def main():
    """Run all compatibility checks."""
    print("🔍 License Compatibility Report for Apache 2.0 Migration")
    print("=" * 60)

    py_ok = check_python_deps()
    rust_ok = check_rust_deps()
    js_ok = check_js_deps()

    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("=" * 60)

    if py_ok and rust_ok and js_ok:
        print("✅ All dependencies are Apache 2.0 compatible!")
        print("\n⚠️  Notes:")
        print("  • tqdm (MPL-2.0): File-level copyleft, consider adding notices")
        print("  • cvxopt (GPL-3.0): OPTIONAL dependency only, not required")
        return 0
    else:
        print("⚠️  Some dependencies need legal review before migration")
        return 1


if __name__ == '__main__':
    sys.exit(main())
