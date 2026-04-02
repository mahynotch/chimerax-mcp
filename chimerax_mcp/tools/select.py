"""Selection helpers and named zones."""

from __future__ import annotations

from chimerax_mcp.client import ChimeraXClient

_cx = ChimeraXClient()


def _normalize_spec(spec: str) -> str:
    spec = spec.strip()
    if spec and spec[0].isalpha() and ":" in spec:
        spec = f"/{spec}"
    return spec


def select(spec: str) -> str:
    """Select atoms/residues by a ChimeraX specifier string.

    Aliases: pick, highlight, sel.

    # Example
    # select("/A:501")
    """
    spec = _normalize_spec(spec)
    result = _cx.run(f"select {spec}")
    return f"Selected {spec}: {result['result']}"


def select_near(spec: str, distance: float) -> str:
    """Select all atoms within a given distance (Angstroms) of a selection.

    Aliases: select nearby, zone, within distance.

    # Example
    # select_near("/A:501", 5.0)
    """
    spec = _normalize_spec(spec)
    result = _cx.run(f"select {spec} :< {distance}")
    return f"Selected within {distance} A of {spec}: {result['result']}"


def select_chain(chain: str) -> str:
    """Select an entire chain.

    Aliases: pick chain, highlight chain.

    # Example
    # select_chain("A")
    """
    chain = chain.strip().lstrip("/")
    result = _cx.run(f"select /{chain}")
    return f"Selected chain {chain}: {result['result']}"


def invert_selection() -> str:
    """Invert the current selection.

    Aliases: select inverse, flip selection.

    # Example
    # invert_selection()
    """
    result = _cx.run("select ~sel")
    return f"Selection inverted: {result['result']}"


def name_selection(name: str) -> str:
    """Save the current selection under a reusable name.

    Aliases: save selection, bookmark, name zone.

    # Example
    # name_selection("binding_site")
    """
    result = _cx.run(f"name sel {name}")
    return f"Named current selection '{name}': {result['result']}"
