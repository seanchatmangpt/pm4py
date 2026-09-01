import os
import networkx as nx
import time
import requests
import json
from packaging.version import Version, InvalidVersion

REMOVE_DEPS_AT_END = True
UPDATE_LICENSE_FILE = True
INCLUDE_BETAS = False


def get_version(package):
    url = "https://pypi.org/pypi/" + package + "/json"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    # your debug dump
    #json.dump(data, open("temp2.txt", "w"), indent=2)

    # ---- license (same as before) ----
    license = "Unspecified"
    for classi in data["info"].get("classifiers", []):
        if classi.startswith("License ::"):
            license = classi.split(":: ")[-1]

    releases = data.get("releases", {})

    versions = []
    for s in releases.keys():
        try:
            versions.append(Version(s))
        except InvalidVersion:
            # skip weird/non-PEP 440 tags
            continue

    if not versions:
        # fallback: behave like before, use info["version"]
        version = data["info"]["version"]
        time.sleep(0.1)
        return package, url, version, license

    versions.sort(reverse=True)

    # latest stable (non-pre-release)
    stable_versions = [v for v in versions if not v.is_prerelease]
    latest_stable = stable_versions[0] if stable_versions else None

    # latest beta/RC (pre-release; you can restrict to 'b' and 'rc')
    prereleases = [v for v in versions if v.is_prerelease]

    # Only beta and rc; drop alphas if you don't want them
    beta_rc_versions = [
        v for v in prereleases
        if v.pre is not None and v.pre[0] in ("b", "rc")
    ]
    latest_beta_rc = beta_rc_versions[0] if beta_rc_versions else None

    # ---- version choice logic with INCLUDE_BETAS ----
    if not INCLUDE_BETAS:
        # always stable if possible
        if latest_stable is not None:
            chosen = latest_stable
        else:
            # no stable versions, fall back to newest overall
            chosen = versions[0]
    else:
        # prefer beta/rc only if it is *newer* than latest stable
        if latest_beta_rc is not None and latest_stable is not None:
            chosen = latest_beta_rc if latest_beta_rc > latest_stable else latest_stable
        elif latest_beta_rc is not None:
            # no stable, but we do have beta/rc
            chosen = latest_beta_rc
        elif latest_stable is not None:
            chosen = latest_stable
        else:
            # extremely weird case: only unparseable vs; fall back
            chosen = versions[0]

    version = str(chosen)

    time.sleep(0.1)
    return package, url, version, license


def elaborate_single_python_package(package_name, deps, include_self=False):
    os.system("pipdeptree -p "+package_name+" >deps.txt")

    F = open("deps.txt", "r")
    content = F.readlines()
    F.close()

    if REMOVE_DEPS_AT_END:
        os.remove("deps.txt")

    G = nx.DiGraph()
    i = 1
    dep_level = {}
    blocked = False
    blocked_level = -1
    while i < len(content):
        #row = content[i].replace("└──", "- ").replace("├──", "- ").split("- ")
        #print(row)
        #level = round(len(row[0]) / 2)
        #dep = row[1].split(" ")[0]
        row = content[i].split(" ")
        row = [zz for zz in row if zz]
        dep = None
        level = None
        j = 0
        while j < len(row):
            if row[j].startswith("["):
                break
            j = j + 1
        j = j - 1
        dep = row[j]
        level = (j-1)
        if True:
            if blocked and blocked_level == level:
                blocked = False
            if dep == "pm4pycvxopt":
                blocked = True
                blocked_level = level
            if not blocked:
                dep_level[level] = dep
                if level > 1:
                    G.add_edge(dep_level[level - 1], dep_level[level])
                else:
                    G.add_node(dep_level[level])
        i = i + 1
    edges = list(G.edges)
    while len(edges) > 0:
        left = set(x[0] for x in edges)
        right = set(x[1] for x in edges)
        diff = sorted([x for x in right if x not in left])
        for x in diff:
            if not x in deps:
                deps.append(x)
            G.remove_node(x)
        edges = list(G.edges)
    nodes = sorted(list(G.nodes))
    for x in nodes:
        if not x in deps:
            deps.append(x)

    if "cvxopt" in deps:
        del deps[deps.index("cvxopt")]

    if include_self:
        if package_name not in deps:
            deps.append(package_name)

    deps = sorted(deps, key=lambda x: x.lower())

    return deps


def get_all_third_party_dependencies(package_name, deps, packages_dictio, include_self=False):
    deps = elaborate_single_python_package(package_name, deps, include_self=include_self)
    packages = []
    for x in deps:
        if x not in packages_dictio:
            packages_dictio[x] = get_version(x)
        packages.append(packages_dictio[x])
    return deps, packages


deps = []
packages_dictio = {}
deps, packages = get_all_third_party_dependencies("pm4py", deps, packages_dictio, include_self=False)

if UPDATE_LICENSE_FILE:
    F = open("LICENSES_TRANSITIVE.md", "w")
    F.write("""# PM4Py Third Party Dependencies
    
    PM4Py depends on third party libraries to implement some functionality. This document describes which libraries
    PM4Py depends upon. This is a best effort attempt to describe the library's dependencies, it is subject to change as
    libraries are added/removed.
    
    | Name | URL | License | Version |
    | --------------------------- | ------------------------------------------------------------ | --------------------------- | ------------------- |
    """)
    for x in packages:
        F.write("| %s | %s | %s | %s |\n" % (x[0].strip(), x[1].strip(), x[3].strip(), x[2].strip()))
    F.close()
