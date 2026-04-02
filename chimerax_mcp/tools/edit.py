"""Molecular editing tools: mutate, delete, hydrogens, minimization."""

from __future__ import annotations

from chimerax_mcp.client import ChimeraXClient

_cx = ChimeraXClient()

# Mapping from 1-letter amino acid codes to 3-letter codes
_AA1_TO_3: dict[str, str] = {
    "A": "ALA", "C": "CYS", "D": "ASP", "E": "GLU", "F": "PHE",
    "G": "GLY", "H": "HIS", "I": "ILE", "K": "LYS", "L": "LEU",
    "M": "MET", "N": "ASN", "P": "PRO", "Q": "GLN", "R": "ARG",
    "S": "SER", "T": "THR", "V": "VAL", "W": "TRP", "Y": "TYR",
}


def _normalize_aa(code: str) -> str:
    """Convert 1-letter or 3-letter amino acid code to 3-letter uppercase."""
    code = code.strip().upper()
    if len(code) == 1:
        if code not in _AA1_TO_3:
            raise ValueError(f"Unknown 1-letter amino acid code: {code}")
        return _AA1_TO_3[code]
    if len(code) == 3:
        return code
    raise ValueError(f"Invalid amino acid code: {code}")


def _normalize_spec(spec: str) -> str:
    """Ensure spec starts with ``/`` if it looks like a chain:residue spec."""
    spec = spec.strip()
    # If it looks like A:48 (no leading / or #), prepend /
    if spec and spec[0].isalpha() and ":" in spec:
        spec = f"/{spec}"
    return spec


def mutate_residue(spec: str, new_aa: str) -> str:
    """Mutate (swap) a residue to a different amino acid using the Dunbrack rotamer library.

    ``spec`` is a ChimeraX residue specifier like ``/A:48`` or ``A:48``.
    ``new_aa`` can be a 1-letter code (e.g. ``K``) or 3-letter code (e.g. ``LYS``).
    Aliases: swap, change residue, substitute, point mutation.

    # Example
    # mutate_residue("/A:501", "LYS")
    # mutate_residue("A:501", "K")
    """
    spec = _normalize_spec(spec)
    aa3 = _normalize_aa(new_aa)
    result = _cx.run(f"swapaa {spec} {aa3}")
    return f"Mutated {spec} to {aa3}: {result['result']}"


def delete_atoms(spec: str) -> str:
    """Delete atoms or residues matching the spec.

    Aliases: remove atoms, erase, cut.

    # Example
    # delete_atoms("/A:501")
    """
    spec = _normalize_spec(spec)
    result = _cx.run(f"delete {spec}")
    return f"Deleted {spec}: {result['result']}"


def add_hydrogen(spec: str = "all") -> str:
    """Add hydrogens to the structure.

    Aliases: protonate, add H, hydrogenate.

    # Example
    # add_hydrogen("#1")
    """
    spec = _normalize_spec(spec) if spec != "all" else spec
    result = _cx.run(f"addh {spec}")
    return f"Added hydrogens to {spec}: {result['result']}"


def minimize_energy(steps: int = 200, model_id: str = "#1") -> str:
    """Run energy minimization on a model.

    Aliases: relax, optimize geometry, energy minimize.

    # Example
    # minimize_energy(100, "#1")
    """
    result = _cx.run(f"minimize steps {steps} {model_id}")
    return f"Minimized {model_id} for {steps} steps: {result['result']}"
