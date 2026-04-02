"""Visualization tools: color, surface, cartoon, zoom, labels, snapshots."""

from __future__ import annotations

from chimerax_mcp.client import ChimeraXClient

_cx = ChimeraXClient()


def _normalize_spec(spec: str) -> str:
    spec = spec.strip()
    if spec and spec[0].isalpha() and ":" in spec:
        spec = f"/{spec}"
    return spec


# ── Coloring ──────────────────────────────────────────────────────────

def color(spec: str, color_scheme: str) -> str:
    """Color atoms/residues by a scheme or named color.

    Supported schemes:
      - ``chain``   → ``color bychain``
      - ``bfactor`` → ``color byattribute bfactor ... palette blue:white:red``
      - ``rainbow`` → ``rainbow`` (separate top-level command)
      - Any named color (``red``, ``cornflowerblue``) or hex (``#FF0000``)

    For electrostatic or hydrophobicity coloring use the dedicated
    ``show_electrostatic_surface`` / ``show_hydrophobicity_surface`` tools.

    Aliases: colour, paint, set color, recolor.

    # Example
    # color("#1", "chain")
    # color("/A", "red")
    """
    spec = _normalize_spec(spec)
    scheme = color_scheme.strip().lower()

    if scheme == "chain":
        cmd = f"color bychain {spec}"
    elif scheme == "bfactor":
        cmd = f"color byattribute bfactor {spec} palette blue:white:red"
    elif scheme == "rainbow":
        cmd = f"rainbow {spec}"
    else:
        # Named / hex color
        cmd = f"color {spec} {color_scheme.strip()}"

    result = _cx.run(cmd)
    return f"Colored {spec} ({color_scheme}): {result['result']}"


def show_electrostatic_surface(
    spec: str = "#1",
    palette: str = "red:white:blue",
    range_: str = "-10,10",
) -> str:
    """Calculate and display Coulombic electrostatic potential on the surface.

    Runs ``coulombic`` — generates the surface automatically if needed.
    Aliases: electrostatics, ESP, charge surface, coulombic.

    # Example
    # show_electrostatic_surface("#1")
    """
    spec = _normalize_spec(spec)
    result = _cx.run(f"coulombic {spec} palette {palette} range {range_}")
    return f"Electrostatic surface for {spec}: {result['result']}"


def show_hydrophobicity_surface(spec: str = "#1") -> str:
    """Calculate and display Molecular Lipophilicity Potential (MLP) on the surface.

    Dark cyan = hydrophilic, dark goldenrod = hydrophobic.
    Aliases: hydrophobicity, lipophilicity, MLP, hydrophobic surface.

    # Example
    # show_hydrophobicity_surface("#1")
    """
    spec = _normalize_spec(spec)
    result = _cx.run(f"mlp {spec}")
    return f"Hydrophobicity surface for {spec}: {result['result']}"


# ── Surface & representation ─────────────────────────────────────────

def show_surface(spec: str = "all", opacity: float = 1.0) -> str:
    """Show molecular surface.

    Aliases: surface, display surface, solvent-accessible surface.

    # Example
    # show_surface("#1", 0.7)
    """
    spec = _normalize_spec(spec) if spec != "all" else spec
    cmds = [f"surface {spec}"]
    if opacity < 1.0:
        cmds.append(f"transparency {spec} {int((1 - opacity) * 100)} target s")
    results = _cx.run_many(cmds)
    return f"Surface shown for {spec}: {results[-1]['result']}"


def hide_surface(spec: str = "all") -> str:
    """Hide molecular surface.

    Aliases: remove surface, surface off.

    # Example
    # hide_surface("#1")
    """
    spec = _normalize_spec(spec) if spec != "all" else spec
    result = _cx.run(f"surface hide {spec}")
    return f"Surface hidden for {spec}: {result['result']}"


def show_cartoon(spec: str = "all") -> str:
    """Show ribbon/cartoon representation.

    Aliases: ribbon, cartoon, secondary structure.

    # Example
    # show_cartoon("#1")
    """
    spec = _normalize_spec(spec) if spec != "all" else spec
    result = _cx.run(f"cartoon {spec}")
    return f"Cartoon shown for {spec}: {result['result']}"


def show_sticks(spec: str) -> str:
    """Show stick representation for a selection.

    Aliases: sticks, ball and stick, show bonds.

    # Example
    # show_sticks("/A:501")
    """
    spec = _normalize_spec(spec)
    results = _cx.run_many([f"show {spec} atoms", f"style {spec} stick"])
    return f"Sticks shown for {spec}: {results[-1]['result']}"


def hide_atoms(spec: str) -> str:
    """Hide atoms for a selection.

    Aliases: hide, conceal atoms.

    # Example
    # hide_atoms("/A:501")
    """
    spec = _normalize_spec(spec)
    result = _cx.run(f"hide {spec} atoms")
    return f"Atoms hidden for {spec}: {result['result']}"


# ── Camera & labels ──────────────────────────────────────────────────

def zoom_to(spec: str) -> str:
    """Zoom the camera to center on a selection.

    Aliases: focus, center on, look at, zoom in.

    # Example
    # zoom_to("/A:501")
    """
    spec = _normalize_spec(spec)
    result = _cx.run(f"view {spec}")
    return f"Zoomed to {spec}: {result['result']}"


def set_background(color: str) -> str:
    """Set the background color.

    Aliases: background, bg color.

    # Example
    # set_background("white")
    """
    result = _cx.run(f"set bgColor {color}")
    return f"Background set to {color}: {result['result']}"


def label_residues(spec: str, label: str = "default") -> str:
    """Add text labels to residues.

    ``label="default"`` uses residue name + number.
    Aliases: annotate, tag residues, show labels.

    # Example
    # label_residues("/A:501")
    """
    spec = _normalize_spec(spec)
    if label == "default":
        cmd = f"label {spec} residues"
    else:
        cmd = f"label {spec} residues text {label}"
    result = _cx.run(cmd)
    return f"Labeled {spec}: {result['result']}"


def clear_labels() -> str:
    """Remove all labels.

    Aliases: delete labels, hide labels, unlabel.

    # Example
    # clear_labels()
    """
    result = _cx.run("label delete")
    return f"Labels cleared: {result['result']}"


def reset_view() -> str:
    """Reset to the default camera view.

    Aliases: home view, reset camera, default view.

    # Example
    # reset_view()
    """
    result = _cx.run("view")
    return f"View reset: {result['result']}"


def take_snapshot(path: str) -> str:
    """Save a PNG screenshot of the current view.

    Aliases: screenshot, capture, save image, photo.

    # Example
    # take_snapshot("/tmp/snapshot.png")
    """
    result = _cx.run(f"save {path}")
    return f"Snapshot saved to {path}: {result['result']}"


# ── Movie / video ────────────────────────────────────────────────────

def start_recording(supersample: int = 3) -> str:
    """Start recording a movie of the ChimeraX session.

    Call this before making changes, then call ``stop_recording`` when done.
    ``supersample`` controls anti-aliasing quality (1 = none, 3 = good, 4 = best).
    Aliases: record, start movie, begin recording.

    # Example
    # start_recording()
    """
    result = _cx.run(f"movie record supersample {supersample}")
    return f"Recording started (supersample={supersample}): {result['result']}"


def stop_recording(path: str, framerate: int = 30) -> str:
    """Stop recording and save the movie to a file.

    Supported formats: .mp4, .webm, .mov, .avi (determined by file extension).
    Aliases: stop movie, save movie, end recording, save video.

    # Example
    # stop_recording("/tmp/session.mp4")
    """
    results = _cx.run_many([
        "movie stop",
        f"movie encode {path} framerate {framerate}",
    ])
    return f"Movie saved to {path}: {results[-1]['result']}"


def spin(axis: str = "y", degrees: float = 360, frames: int = 180) -> str:
    """Spin/rotate the model around an axis.

    Great for turntable animations when combined with recording.
    ``axis`` can be ``x``, ``y``, or ``z``.
    Aliases: rotate, turntable, orbit, spin around.

    # Example
    # spin("y", 360, 180)
    """
    rate = degrees / frames
    result = _cx.run(f"turn {axis} {rate} {frames}")
    return f"Spun {degrees}° around {axis} in {frames} frames: {result['result']}"


def record_spin(path: str, axis: str = "y", degrees: float = 360,
                frames: int = 180, framerate: int = 30) -> str:
    """Record a full turntable spin and save as video.

    Convenience tool that starts recording, spins, and encodes in one call.
    Aliases: turntable video, spin video, rotation movie, 360 video.

    # Example
    # record_spin("/tmp/turntable.mp4")
    """
    rate = degrees / frames
    results = _cx.run_many([
        "movie record supersample 3",
        f"turn {axis} {rate} {frames}",
        "movie stop",
        f"movie encode {path} framerate {framerate}",
    ])
    return f"Spin movie saved to {path}: {results[-1]['result']}"
