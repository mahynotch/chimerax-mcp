"""Structure loading, saving, and model management tools."""

from __future__ import annotations

from chimerax_mcp.client import ChimeraXClient, validate_script_path

_cx = ChimeraXClient()


def open_structure(source: str) -> str:
    """Open a molecular structure in ChimeraX.

    Accepts a PDB ID (e.g. ``6VXX``), a local file path, or a URL.
    Aliases: load, fetch, import, read structure.

    # Example
    # open_structure("6VXX")
    """
    result = _cx.run(f"open {source}")
    return f"Opened {source}: {result['result']}"


def close_structure(model_id: str = "all") -> str:
    """Close one or all open models.

    Aliases: remove model, delete model, unload.

    # Example
    # close_structure("#1")
    """
    spec = model_id if model_id == "all" else model_id
    result = _cx.run(f"close {spec}")
    return f"Closed {spec}: {result['result']}"


def save_structure(path: str, model_id: str = "#1") -> str:
    """Save a model to a file (PDB, mmCIF, or mol2).

    Aliases: export, write structure, download.

    # Example
    # save_structure("/tmp/model.pdb", "#1")
    """
    result = _cx.run(f"save {path} {model_id}")
    return f"Saved {model_id} to {path}: {result['result']}"


def list_models() -> str:
    """List all open models with their IDs and names.

    Aliases: show models, what's open, loaded structures.

    # Example
    # list_models()
    """
    result = _cx.run("info models")
    return f"Open models:\n{result['result']}"


def get_sequence(chain_spec: str) -> str:
    """Return the amino acid sequence for a chain.

    ``chain_spec`` can be e.g. ``/A`` or ``#1/A``.
    Aliases: sequence, residues, chain sequence.

    # Example
    # get_sequence("/A")
    """
    result = _cx.run(f"sequence chain {chain_spec}")
    return f"Sequence for {chain_spec}:\n{result['result']}"


def run_script(path: str) -> str:
    """Run a ChimeraX command script (.cxc) or Python script (.py).

    The file must exist and have a ``.cxc`` or ``.py`` extension.
    Aliases: execute script, run cxc, run python script, source.

    # Example
    # run_script("/path/to/setup.cxc")
    # run_script("/path/to/analysis.py")
    """
    safe_path = validate_script_path(path)
    result = _cx.run(f"runscript {safe_path}")
    return f"Script {safe_path} executed: {result['result']}"
