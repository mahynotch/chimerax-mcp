"""Measurement tools: distance, angle, RMSD, contacts, B-factors, buried area."""

from __future__ import annotations

from chimerax_mcp.client import ChimeraXClient

_cx = ChimeraXClient()


def _normalize_spec(spec: str) -> str:
    spec = spec.strip()
    if spec and spec[0].isalpha() and ":" in spec:
        spec = f"/{spec}"
    return spec


def measure_distance(atom1: str, atom2: str) -> str:
    """Measure the distance between two atoms (in Angstroms) and add a visual annotation.

    Aliases: distance, how far, length between.

    # Example
    # measure_distance("/A:501@CA", "/A:31@CA")
    """
    atom1 = _normalize_spec(atom1)
    atom2 = _normalize_spec(atom2)
    result = _cx.run(f"distance {atom1} {atom2}")
    return f"Distance {atom1} — {atom2}: {result['result']}"


def measure_angle(atom1: str, atom2: str, atom3: str) -> str:
    """Measure the bond angle defined by three atoms (in degrees).

    Aliases: angle, bond angle.

    # Example
    # measure_angle("/A:501@N", "/A:501@CA", "/A:501@C")
    """
    atom1 = _normalize_spec(atom1)
    atom2 = _normalize_spec(atom2)
    atom3 = _normalize_spec(atom3)
    result = _cx.run(f"angle {atom1} {atom2} {atom3}")
    return f"Angle: {result['result']}"


def align_and_rmsd(spec: str, to_spec: str) -> str:
    """Align one selection to another and report the RMSD.

    Uses ``align ... to ...`` — ChimeraX has no ``measure rmsd`` subcommand.
    Aliases: align, superpose, RMSD, overlay, structural alignment.

    # Example
    # align_and_rmsd("#1/A", "#2/A")
    """
    spec = _normalize_spec(spec)
    to_spec = _normalize_spec(to_spec)
    result = _cx.run(f"align {spec} to {to_spec}")
    return f"Alignment {spec} → {to_spec}: {result['result']}"


def find_contacts(spec: str, distance: float = 4.0) -> str:
    """Find residues within a given distance (Angstroms) of a selection.

    Aliases: contacts, neighbors, nearby residues, clashes.

    # Example
    # find_contacts("/A:501", 4.0)
    """
    spec = _normalize_spec(spec)
    results = _cx.run_many([
        f"select {spec} :< {distance}",
        f"contacts {spec} distance {distance}",
    ])
    return f"Contacts within {distance} A of {spec}:\n{results[-1]['result']}"


def get_bfactors(spec: str) -> str:
    """Return B-factors for the selected atoms.

    Aliases: B-factor, temperature factor, displacement.

    # Example
    # get_bfactors("/A:501")
    """
    spec = _normalize_spec(spec)
    result = _cx.run(f"info atoms {spec}")
    return f"B-factors for {spec}:\n{result['result']}"


def measure_buried_area(spec1: str, spec2: str) -> str:
    """Measure the buried solvent-accessible surface area between two atom sets.

    Uses ``measure buriedarea {spec1} withAtoms2 {spec2}`` — the ``withAtoms2``
    keyword is required.
    Aliases: buried area, interface area, binding interface.

    # Example
    # measure_buried_area("#1/A", "#1/B")
    """
    spec1 = _normalize_spec(spec1)
    spec2 = _normalize_spec(spec2)
    result = _cx.run(f"measure buriedarea {spec1} withAtoms2 {spec2}")
    return f"Buried area {spec1} / {spec2}: {result['result']}"
