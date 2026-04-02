"""ChimeraX MCP Server — bridges Claude Code to ChimeraX via its REST API."""

from __future__ import annotations

from fastmcp import FastMCP

from chimerax_mcp.client import ChimeraXError
from chimerax_mcp.tools import structure, edit, view, measure, select

_INSTRUCTIONS = """\
You are controlling UCSF ChimeraX, a molecular visualization program, through \
MCP tools. Here is what you need to know to use them effectively.

## ChimeraX specifier syntax

Atoms and residues are identified by "spec strings":
- `#1` — model 1
- `#1/A` — chain A of model 1
- `/A:501` — residue 501 of chain A (any model)
- `/A:501@CA` — the CA (alpha-carbon) atom of residue 501, chain A
- `/A:100-200` — residues 100 through 200 of chain A
- `#1/A,B` — chains A and B of model 1

You can use either `/A:48` or `A:48` — both are accepted (auto-normalized).

## Amino acid codes

Mutation tools accept both formats:
- 1-letter: A, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, V, W, Y
- 3-letter: ALA, CYS, ASP, GLU, PHE, GLY, HIS, ILE, LYS, LEU, MET, ASN, \
PRO, GLN, ARG, SER, THR, VAL, TRP, TYR

## Common workflows

**Basic visualization:**
1. `open_structure("6VXX")` — load from RCSB by PDB ID
2. `hide_atoms("#1")` — hide all atoms
3. `show_cartoon("#1")` — show ribbon
4. `color_structure("#1", "chain")` — color by chain

**Mutation analysis:**
1. `open_structure("6VXX")`
2. `zoom_to("/A:501")` — focus on the residue
3. `show_sticks("/A:501")` — show side chain
4. `mutate_residue("/A:501", "K")` — mutate to Lysine
5. `label_residues("/A:501")` — label it

**Surface analysis:**
- `show_surface("#1")` — plain molecular surface
- `show_electrostatic_surface("#1")` — Coulombic ESP (red=negative, blue=positive)
- `show_hydrophobicity_surface("#1")` — MLP (cyan=hydrophilic, goldenrod=hydrophobic)

**Measurement:**
- `measure_distance("/A:501@CA", "/B:31@CA")` — distance between two atoms
- `find_contacts("/A:501", 4.0)` — residues within 4 Angstroms
- `align_and_rmsd("#1/A", "#2/A")` — superpose and get RMSD

**Recording video:**
1. `start_recording()` — begin capture
2. (perform visualization changes)
3. `spin("y", 360, 180)` — optional turntable
4. `stop_recording("/path/to/output.mp4")` — save video
- Or use `record_spin("/path/to/turntable.mp4")` for a one-shot turntable video.

## Tips
- PDB IDs are 4 characters (e.g. `6VXX`, `1AKI`). Use `open_structure` with just the ID.
- After loading, the model is usually `#1` (or `#2`, `#3`, etc. for subsequent loads).
- Use `list_models()` to see what's currently open.
- For publication figures: `set_background("white")`, then `take_snapshot("/path/to/fig.png")`.
- `run_script` can execute .cxc command files or .py Python scripts for advanced workflows.
"""

mcp = FastMCP("chimerax", instructions=_INSTRUCTIONS)


# ---------------------------------------------------------------------------
# Helper: wrap every tool so ChimeraX errors become user-friendly messages
# ---------------------------------------------------------------------------

def _safe(fn, **kwargs):
    try:
        return fn(**kwargs)
    except ChimeraXError as exc:
        return f"ChimeraX error: {exc}"
    except Exception as exc:
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Structure tools
# ---------------------------------------------------------------------------

@mcp.tool()
def open_structure(source: str) -> str:
    """Open a molecular structure from PDB ID, file path, or URL.
    Aliases: load, fetch, import, read structure.
    # Example: open_structure("6VXX")
    """
    return _safe(structure.open_structure, source=source)


@mcp.tool()
def close_structure(model_id: str = "all") -> str:
    """Close one or all open models.
    Aliases: remove model, delete model, unload.
    # Example: close_structure("#1")
    """
    return _safe(structure.close_structure, model_id=model_id)


@mcp.tool()
def save_structure(path: str, model_id: str = "#1") -> str:
    """Save a model to PDB, mmCIF, or mol2 file.
    Aliases: export, write structure, download.
    # Example: save_structure("/tmp/model.pdb", "#1")
    """
    return _safe(structure.save_structure, path=path, model_id=model_id)


@mcp.tool()
def list_models() -> str:
    """List all open models with IDs and names.
    Aliases: show models, what's open, loaded structures.
    # Example: list_models()
    """
    return _safe(structure.list_models)


@mcp.tool()
def get_sequence(chain_spec: str) -> str:
    """Return amino acid sequence for a chain.
    Aliases: sequence, residues, chain sequence.
    # Example: get_sequence("/A")
    """
    return _safe(structure.get_sequence, chain_spec=chain_spec)


@mcp.tool()
def run_script(path: str) -> str:
    """Run a ChimeraX command script (.cxc) or Python script (.py).
    File must exist locally with a .cxc or .py extension.
    Aliases: execute script, run cxc, run python script, source.
    # Example: run_script("/path/to/setup.cxc")
    """
    return _safe(structure.run_script, path=path)


# ---------------------------------------------------------------------------
# Edit tools
# ---------------------------------------------------------------------------

@mcp.tool()
def mutate_residue(spec: str, new_aa: str) -> str:
    """Mutate (swap) a residue to a different amino acid using the Dunbrack rotamer library.
    Accepts both 1-letter (K) and 3-letter (LYS) amino acid codes.
    Spec can be /A:48 or A:48 format.
    Aliases: swap, change residue, substitute, point mutation.
    # Example: mutate_residue("/A:501", "K")
    """
    return _safe(edit.mutate_residue, spec=spec, new_aa=new_aa)


@mcp.tool()
def delete_atoms(spec: str) -> str:
    """Delete atoms or residues matching the spec.
    Aliases: remove atoms, erase, cut.
    # Example: delete_atoms("/A:501")
    """
    return _safe(edit.delete_atoms, spec=spec)


@mcp.tool()
def add_hydrogen(spec: str = "all") -> str:
    """Add hydrogens to the structure.
    Aliases: protonate, add H, hydrogenate.
    # Example: add_hydrogen("#1")
    """
    return _safe(edit.add_hydrogen, spec=spec)


@mcp.tool()
def minimize_energy(steps: int = 200, model_id: str = "#1") -> str:
    """Run energy minimization on a model.
    Aliases: relax, optimize geometry, energy minimize.
    # Example: minimize_energy(100, "#1")
    """
    return _safe(edit.minimize_energy, steps=steps, model_id=model_id)


# ---------------------------------------------------------------------------
# View tools
# ---------------------------------------------------------------------------

@mcp.tool()
def color_structure(spec: str, color_scheme: str) -> str:
    """Color atoms/residues by scheme (chain, bfactor, rainbow) or a named/hex color.
    For electrostatic or hydrophobicity coloring use the dedicated surface tools.
    Aliases: colour, paint, set color, recolor.
    # Example: color_structure("#1", "chain")
    """
    return _safe(view.color, spec=spec, color_scheme=color_scheme)


@mcp.tool()
def show_electrostatic_surface(
    spec: str = "#1",
    palette: str = "red:white:blue",
    range_: str = "-10,10",
) -> str:
    """Calculate and display Coulombic electrostatic potential on the surface.
    Aliases: electrostatics, ESP, charge surface, coulombic.
    # Example: show_electrostatic_surface("#1")
    """
    return _safe(view.show_electrostatic_surface, spec=spec, palette=palette, range_=range_)


@mcp.tool()
def show_hydrophobicity_surface(spec: str = "#1") -> str:
    """Calculate and display Molecular Lipophilicity Potential on the surface.
    Dark cyan = hydrophilic, dark goldenrod = hydrophobic.
    Aliases: hydrophobicity, lipophilicity, MLP, hydrophobic surface.
    # Example: show_hydrophobicity_surface("#1")
    """
    return _safe(view.show_hydrophobicity_surface, spec=spec)


@mcp.tool()
def show_surface(spec: str = "all", opacity: float = 1.0) -> str:
    """Show molecular surface.
    Aliases: surface, display surface, solvent-accessible surface.
    # Example: show_surface("#1", 0.7)
    """
    return _safe(view.show_surface, spec=spec, opacity=opacity)


@mcp.tool()
def hide_surface(spec: str = "all") -> str:
    """Hide molecular surface.
    Aliases: remove surface, surface off.
    # Example: hide_surface("#1")
    """
    return _safe(view.hide_surface, spec=spec)


@mcp.tool()
def show_cartoon(spec: str = "all") -> str:
    """Show ribbon/cartoon representation.
    Aliases: ribbon, cartoon, secondary structure.
    # Example: show_cartoon("#1")
    """
    return _safe(view.show_cartoon, spec=spec)


@mcp.tool()
def show_sticks(spec: str) -> str:
    """Show stick representation for a selection.
    Aliases: sticks, ball and stick, show bonds.
    # Example: show_sticks("/A:501")
    """
    return _safe(view.show_sticks, spec=spec)


@mcp.tool()
def hide_atoms(spec: str) -> str:
    """Hide atoms for a selection.
    Aliases: hide, conceal atoms.
    # Example: hide_atoms("/A:501")
    """
    return _safe(view.hide_atoms, spec=spec)


@mcp.tool()
def zoom_to(spec: str) -> str:
    """Zoom the camera to center on a selection.
    Aliases: focus, center on, look at, zoom in.
    # Example: zoom_to("/A:501")
    """
    return _safe(view.zoom_to, spec=spec)


@mcp.tool()
def set_background(color: str) -> str:
    """Set the background color (white, black, hex).
    Aliases: background, bg color.
    # Example: set_background("white")
    """
    return _safe(view.set_background, color=color)


@mcp.tool()
def label_residues(spec: str, label: str = "default") -> str:
    """Add text labels to residues. Default shows residue name + number.
    Aliases: annotate, tag residues, show labels.
    # Example: label_residues("/A:501")
    """
    return _safe(view.label_residues, spec=spec, label=label)


@mcp.tool()
def clear_labels() -> str:
    """Remove all labels.
    Aliases: delete labels, hide labels, unlabel.
    # Example: clear_labels()
    """
    return _safe(view.clear_labels)


@mcp.tool()
def reset_view() -> str:
    """Reset to the default camera view.
    Aliases: home view, reset camera, default view.
    # Example: reset_view()
    """
    return _safe(view.reset_view)


@mcp.tool()
def take_snapshot(path: str) -> str:
    """Save a PNG screenshot of the current view.
    Aliases: screenshot, capture, save image, photo.
    # Example: take_snapshot("/tmp/snapshot.png")
    """
    return _safe(view.take_snapshot, path=path)


@mcp.tool()
def start_recording(supersample: int = 3) -> str:
    """Start recording a movie of the ChimeraX session.
    Call this before making visual changes, then stop_recording when done.
    Aliases: record, start movie, begin recording.
    # Example: start_recording()
    """
    return _safe(view.start_recording, supersample=supersample)


@mcp.tool()
def stop_recording(path: str, framerate: int = 30) -> str:
    """Stop recording and save movie to file (.mp4, .webm, .mov, .avi).
    Aliases: stop movie, save movie, end recording, save video.
    # Example: stop_recording("/tmp/session.mp4")
    """
    return _safe(view.stop_recording, path=path, framerate=framerate)


@mcp.tool()
def spin(axis: str = "y", degrees: float = 360, frames: int = 180) -> str:
    """Spin/rotate the model around an axis (x, y, or z).
    Great for turntable animations when combined with recording.
    Aliases: rotate, turntable, orbit, spin around.
    # Example: spin("y", 360, 180)
    """
    return _safe(view.spin, axis=axis, degrees=degrees, frames=frames)


@mcp.tool()
def record_spin(path: str, axis: str = "y", degrees: float = 360,
                frames: int = 180, framerate: int = 30) -> str:
    """Record a full turntable spin and save as video in one step.
    Aliases: turntable video, spin video, rotation movie, 360 video.
    # Example: record_spin("/tmp/turntable.mp4")
    """
    return _safe(view.record_spin, path=path, axis=axis, degrees=degrees,
                 frames=frames, framerate=framerate)


# ---------------------------------------------------------------------------
# Measure tools
# ---------------------------------------------------------------------------

@mcp.tool()
def measure_distance(atom1: str, atom2: str) -> str:
    """Measure distance between two atoms in Angstroms with visual annotation.
    Aliases: distance, how far, length between.
    # Example: measure_distance("/A:501@CA", "/A:31@CA")
    """
    return _safe(measure.measure_distance, atom1=atom1, atom2=atom2)


@mcp.tool()
def measure_angle(atom1: str, atom2: str, atom3: str) -> str:
    """Measure bond angle defined by three atoms in degrees.
    Aliases: angle, bond angle.
    # Example: measure_angle("/A:501@N", "/A:501@CA", "/A:501@C")
    """
    return _safe(measure.measure_angle, atom1=atom1, atom2=atom2, atom3=atom3)


@mcp.tool()
def align_and_rmsd(spec: str, to_spec: str) -> str:
    """Align one selection to another and report RMSD.
    Uses ChimeraX 'align' command (no 'measure rmsd' exists).
    Aliases: align, superpose, RMSD, overlay, structural alignment.
    # Example: align_and_rmsd("#1/A", "#2/A")
    """
    return _safe(measure.align_and_rmsd, spec=spec, to_spec=to_spec)


@mcp.tool()
def find_contacts(spec: str, distance: float = 4.0) -> str:
    """Find residues within N Angstroms of a selection.
    Aliases: contacts, neighbors, nearby residues, clashes.
    # Example: find_contacts("/A:501", 4.0)
    """
    return _safe(measure.find_contacts, spec=spec, distance=distance)


@mcp.tool()
def get_bfactors(spec: str) -> str:
    """Return B-factors for selected atoms.
    Aliases: B-factor, temperature factor, displacement.
    # Example: get_bfactors("/A:501")
    """
    return _safe(measure.get_bfactors, spec=spec)


@mcp.tool()
def measure_buried_area(spec1: str, spec2: str) -> str:
    """Measure buried solvent-accessible surface area between two atom sets.
    Aliases: buried area, interface area, binding interface.
    # Example: measure_buried_area("#1/A", "#1/B")
    """
    return _safe(measure.measure_buried_area, spec1=spec1, spec2=spec2)


# ---------------------------------------------------------------------------
# Select tools
# ---------------------------------------------------------------------------

@mcp.tool()
def select_atoms(spec: str) -> str:
    """Select atoms/residues by ChimeraX specifier string.
    Aliases: pick, highlight, sel, select.
    # Example: select_atoms("/A:501")
    """
    return _safe(select.select, spec=spec)


@mcp.tool()
def select_near(spec: str, distance: float) -> str:
    """Select all atoms within N Angstroms of a selection.
    Aliases: select nearby, zone, within distance.
    # Example: select_near("/A:501", 5.0)
    """
    return _safe(select.select_near, spec=spec, distance=distance)


@mcp.tool()
def select_chain(chain: str) -> str:
    """Select an entire chain.
    Aliases: pick chain, highlight chain.
    # Example: select_chain("A")
    """
    return _safe(select.select_chain, chain=chain)


@mcp.tool()
def invert_selection() -> str:
    """Invert the current selection.
    Aliases: select inverse, flip selection.
    # Example: invert_selection()
    """
    return _safe(select.invert_selection)


@mcp.tool()
def name_selection(name: str) -> str:
    """Save current selection under a reusable name.
    Aliases: save selection, bookmark, name zone.
    # Example: name_selection("binding_site")
    """
    return _safe(select.name_selection, name=name)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    mcp.run()


if __name__ == "__main__":
    main()
