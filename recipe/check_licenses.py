# -*- coding: utf-8 -*-

""" Verify that cargo dependency licenses are present.

    mostly copied from:
    https://github.com/conda-forge/pysyntect-feedstock/blob/master/recipe/check_licenses.py

    If this fails, you'll probably need to:
    - ensure the magic-named file(s) exist in library_licenses
    - ensure the magic-named file is included in meta.yaml#/license_file
"""

import json
import os
import sys
import re
import ruamel_yaml
from pathlib import Path

# handles at least:
#
#   library_licenses/<crate-name>-LICEN(S|C)E-(|-MIT|-APACHE|-ZLIB)
#
# COPYING is not a license, but some of the manually-built files need it for
# clarification
BASE_GLOB = "{crate}-LICEN*"
PATTERN = r"# BEGIN LICENSES(.*)# END LICENSES"

# first-party crates are covered by LICENSE
IGNORE = {os.environ["PKG_NAME"], "jsonrpc-derive", "jsonrpc"}

# paths
RECIPE_DIR = Path(os.environ["RECIPE_DIR"])
SRC_DIR = Path(os.environ["SRC_DIR"])
DEPENDENCIES = json.loads((
    SRC_DIR /
    f"""{os.environ["PKG_NAME"]}-{os.environ["PKG_VERSION"]}-cargo-dependencies.json"""
).read_text(encoding="utf-8"))
LIBRARY_LICENSES = RECIPE_DIR / "library_licenses"

# semi-surpisingly, this is the post-rendered recipe
META = ruamel_yaml.safe_load((RECIPE_DIR / "meta.yaml").read_text("utf-8"))
LICENSE_FILES = META["about"]["license_file"]


def main():
    missing = []
    unpackaged = []

    for pkg in DEPENDENCIES:
        matches = list(LIBRARY_LICENSES.glob(BASE_GLOB.format(crate=pkg["name"])))

        if pkg["name"] in IGNORE:
            continue

        if not matches:
            missing.append(pkg)

        for match in matches:
            if "{}/{}".format(LIBRARY_LICENSES.name, match.name) not in LICENSE_FILES:
                unpackaged.append(pkg)

    if missing:
        print('\nLicenses for the following dependencies are missing:\n')
        print(ruamel_yaml.safe_dump(missing), flush=True)
    else:
        print("\nNo missing licenses.", flush=True)

    if unpackaged:
        print('\nLicenses for the following dependencies are not in license_file:\n')
        print(ruamel_yaml.safe_dump(unpackaged), flush=True)
    else:
        print("\nNo unpackaged licenses.", flush=True)

    return len(missing + unpackaged)


if __name__ == "__main__":
    sys.exit(main())
