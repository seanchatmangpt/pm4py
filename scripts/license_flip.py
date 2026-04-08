#!/usr/bin/env python3
"""
License Flip Script: AGPL-3.0 → Apache 2.0

Updates all source files in the pm4py project from AGPL-3.0 to Apache 2.0 license.
This is a one-time migration script for Wave 1 of the pm4py-1000x initiative.
"""

import os
import re
from pathlib import Path

# Apache 2.0 header for Python files
APACHE_PYTHON_HEADER = '''\
"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""
'''

# Apache 2.0 header for Rust files
APACHE_RUST_HEADER = '''\
// PM4Py – A Process Mining Library for Python (POWL v2 WASM)
// Copyright (C) 2024 Process Intelligence Solutions
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
'''

# Pattern to detect AGPL license header
AGPL_PATTERN = re.compile(
    r'^[\'"]{3}.*?GNU Affero General Public License.*?[\'"]{3}',
    re.DOTALL | re.MULTILINE
)

# Pattern to detect alternative AGPL header format
AGPL_ALT_PATTERN = re.compile(
    r'^[\'"]{3}.*?This program is free software.*?GNU Affero General Public License.*?[\'"]{3}',
    re.DOTALL | re.MULTILINE
)

# Files to skip (generated, vendored, or external)
SKIP_PATTERNS = [
    '.venv/',
    'venv/',
    'env/',
    'node_modules/',
    'third_party/',
    'target/',
    '__pycache__/',
    '.pytest_cache/',
    '.mypy_cache/',
    'build/',
    'dist/',
    '*.egg-info/',
    '.git/',
]


def should_skip(path: Path) -> bool:
    """Check if a path should be skipped."""
    path_str = str(path)
    for pattern in SKIP_PATTERNS:
        if pattern.replace('/', os.sep) in path_str:
            return True
    return False


def update_python_file(file_path: Path) -> bool:
    """Update a Python file's license header."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return False

    # Check if already has Apache header
    if 'Apache License' in content[:500]:
        return False  # Already updated

    # Remove AGPL header if present
    new_content = content

    # Try pattern 1: Full AGPL header
    match = AGPL_PATTERN.search(new_content)
    if match:
        new_content = new_content[:match.start()] + new_content[match.end():]
    else:
        # Try pattern 2: Alternative AGPL header format
        match = AGPL_ALT_PATTERN.search(new_content)
        if match:
            new_content = new_content[:match.start()] + new_content[match.end():]

    # Add Apache header at the beginning (after shebang if present)
    if new_content.startswith('#!'):
        lines = new_content.split('\n', 1)
        new_content = lines[0] + '\n' + APACHE_PYTHON_HEADER + '\n' + lines[1]
    else:
        new_content = APACHE_PYTHON_HEADER + '\n' + new_content

    file_path.write_text(new_content, encoding='utf-8')
    return True


def update_rust_file(file_path: Path) -> bool:
    """Update a Rust file's license header."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return False

    # Check if already has Apache header
    if 'Apache License' in content[:500]:
        return False  # Already updated

    # Remove AGPL header if present
    new_content = content

    # Rust AGPL patterns
    for pattern in [
        re.compile(r'//.*?GNU Affero General Public License.*?(?=\n\n|//!|//|fn|mod|pub|use)', re.DOTALL),
        re.compile(r'//!.*?GNU Affero General Public License.*?(?=\n\n//!|//|fn|mod|pub)', re.DOTALL),
    ]:
        match = pattern.search(new_content)
        if match:
            new_content = new_content[:match.start()] + new_content[match.end():]
            break

    # Add Apache header at the beginning
    new_content = APACHE_RUST_HEADER + '\n' + new_content

    file_path.write_text(new_content, encoding='utf-8')
    return True


def main():
    """Execute the license flip."""
    root = Path(__file__).parent.parent
    updated = 0
    skipped = 0

    print("🔄 PM4Py License Flip: AGPL-3.0 → Apache 2.0")
    print("=" * 50)

    # Process Python files
    for py_file in root.rglob('*.py'):
        if should_skip(py_file):
            skipped += 1
            continue

        if update_python_file(py_file):
            print(f"  ✓ {py_file.relative_to(root)}")
            updated += 1

    # Process Rust files
    for rs_file in root.rglob('*.rs'):
        if should_skip(rs_file):
            skipped += 1
            continue

        if update_rust_file(rs_file):
            print(f"  ✓ {rs_file.relative_to(root)}")
            updated += 1

    print("=" * 50)
    print(f"✅ Updated {updated} files")
    print(f"⏭️  Skipped {skipped} files")
    print("\n🎯 Next steps:")
    print("  1. Review changes with: git diff")
    print("  2. Run tests: python tests/execute_tests.py")
    print("  3. Commit: git commit -m 'feat: migrate from AGPL-3.0 to Apache 2.0'")


if __name__ == '__main__':
    main()
