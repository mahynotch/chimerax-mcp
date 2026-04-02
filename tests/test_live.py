"""Live integration tests for chimerax-mcp.

Requires a running ChimeraX instance with REST API enabled on port 8765.
Run with:  python -m pytest tests/test_live.py -v
Or directly: python tests/test_live.py
"""

from __future__ import annotations

import os
import sys
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

from chimerax_mcp.client import (
    ChimeraXClient,
    ChimeraXCommandError,
    sanitize_command,
    validate_script_path,
)
from chimerax_mcp.tools import structure, edit, view, measure, select


def _chimerax_available() -> bool:
    try:
        cx = ChimeraXClient(auto_launch=False)
        cx.run("version")
        return True
    except Exception:
        return False


requires_chimerax = pytest.mark.skipif(
    not _chimerax_available(),
    reason="ChimeraX REST API not reachable on localhost:8765",
)


# ---------------------------------------------------------------------------
# Security tests (no ChimeraX needed)
# ---------------------------------------------------------------------------

class TestSecurity:
    def test_block_semicolon(self):
        with pytest.raises(ChimeraXCommandError, match="forbidden characters"):
            sanitize_command("version ; runscript evil.py")

    def test_block_newline(self):
        with pytest.raises(ChimeraXCommandError, match="forbidden characters"):
            sanitize_command("version\nrunscript evil.py")

    def test_block_exec(self):
        with pytest.raises(ChimeraXCommandError, match="blocked for security"):
            sanitize_command("exec import os")

    def test_block_shell(self):
        with pytest.raises(ChimeraXCommandError, match="blocked for security"):
            sanitize_command("shell dir")

    def test_block_system(self):
        with pytest.raises(ChimeraXCommandError, match="blocked for security"):
            sanitize_command("system calc")

    def test_allow_runscript(self):
        result = sanitize_command("runscript /some/file.cxc")
        assert result == "runscript /some/file.cxc"

    def test_allow_normal_commands(self):
        for cmd in ["open 1aki", "color bychain #1", "view", "save /tmp/x.pdb #1"]:
            assert sanitize_command(cmd) == cmd

    def test_reject_bad_script_extension(self):
        with pytest.raises(ChimeraXCommandError, match="only"):
            validate_script_path("evil.exe")

    def test_reject_missing_script(self):
        with pytest.raises(ChimeraXCommandError, match="not found"):
            validate_script_path("nonexistent.cxc")

    def test_accept_valid_script(self):
        with tempfile.NamedTemporaryFile(suffix=".cxc", delete=False) as f:
            f.write(b"version\n")
            path = f.name
        try:
            result = validate_script_path(path)
            assert result.endswith(".cxc")
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Live ChimeraX tests
# ---------------------------------------------------------------------------

@requires_chimerax
class TestStructure:
    def setup_method(self):
        structure.close_structure("all")

    def test_open_structure(self):
        result = structure.open_structure("1aki")
        assert "Opened" in result

    def test_list_models(self):
        structure.open_structure("1aki")
        result = structure.list_models()
        assert "models" in result.lower() or result

    def test_get_sequence(self):
        structure.open_structure("1aki")
        result = structure.get_sequence("/A")
        assert "Sequence" in result

    def test_save_structure(self):
        structure.open_structure("1aki")
        with tempfile.NamedTemporaryFile(suffix=".pdb", delete=False) as f:
            path = f.name
        try:
            result = structure.save_structure(path, "#1")
            assert "Saved" in result
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_close_structure(self):
        structure.open_structure("1aki")
        result = structure.close_structure("all")
        assert "Closed" in result


@requires_chimerax
class TestSelect:
    def setup_method(self):
        structure.close_structure("all")
        structure.open_structure("1aki")

    def test_select(self):
        result = select.select("/A:50")
        assert "Selected" in result

    def test_select_chain(self):
        result = select.select_chain("A")
        assert "Selected" in result

    def test_select_near(self):
        result = select.select_near("/A:50", 5.0)
        assert "Selected" in result

    def test_name_selection(self):
        select.select("/A:50")
        result = select.name_selection("test_sel")
        assert "Named" in result

    def test_invert_selection(self):
        select.select("/A:50")
        result = select.invert_selection()
        assert "inverted" in result.lower()


@requires_chimerax
class TestEdit:
    def setup_method(self):
        structure.close_structure("all")
        structure.open_structure("1aki")

    def test_mutate_residue_1letter(self):
        result = edit.mutate_residue("/A:50", "K")
        assert "Mutated" in result

    def test_mutate_residue_3letter(self):
        result = edit.mutate_residue("/A:51", "ALA")
        assert "Mutated" in result

    def test_mutate_residue_normalizes_spec(self):
        result = edit.mutate_residue("A:52", "G")
        assert "Mutated" in result

    def test_add_hydrogen(self):
        result = edit.add_hydrogen("#1")
        assert "Added" in result

    def test_delete_atoms(self):
        result = edit.delete_atoms("/A:129")
        assert "Deleted" in result

    def test_minimize_energy(self):
        result = edit.minimize_energy(10, "#1")
        assert "Minimized" in result


@requires_chimerax
class TestView:
    def setup_method(self):
        structure.close_structure("all")
        structure.open_structure("1aki")

    def test_hide_atoms(self):
        result = view.hide_atoms("#1")
        assert "hidden" in result.lower()

    def test_show_cartoon(self):
        result = view.show_cartoon("#1")
        assert "Cartoon" in result

    def test_color_chain(self):
        result = view.color("#1", "chain")
        assert "Colored" in result

    def test_color_bfactor(self):
        result = view.color("#1", "bfactor")
        assert "Colored" in result

    def test_color_rainbow(self):
        result = view.color("#1", "rainbow")
        assert "Colored" in result

    def test_color_named(self):
        result = view.color("#1/A", "red")
        assert "Colored" in result

    def test_show_sticks(self):
        result = view.show_sticks("/A:50")
        assert "Sticks" in result

    def test_show_surface(self):
        result = view.show_surface("#1", 0.5)
        assert "Surface" in result

    def test_hide_surface(self):
        view.show_surface("#1")
        result = view.hide_surface("#1")
        assert "hidden" in result.lower()

    def test_zoom_to(self):
        result = view.zoom_to("/A:50")
        assert "Zoomed" in result

    def test_set_background(self):
        result = view.set_background("white")
        assert "Background" in result

    def test_label_residues_default(self):
        result = view.label_residues("/A:50")
        assert "Labeled" in result

    def test_label_residues_custom(self):
        result = view.label_residues("/A:51", "MUT")
        assert "Labeled" in result

    def test_clear_labels(self):
        view.label_residues("/A:50")
        result = view.clear_labels()
        assert "cleared" in result.lower()

    def test_reset_view(self):
        result = view.reset_view()
        assert "reset" in result.lower()

    def test_take_snapshot(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            result = view.take_snapshot(path)
            assert "Snapshot" in result
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)


@requires_chimerax
class TestSurfaceAnalysis:
    def setup_method(self):
        structure.close_structure("all")
        structure.open_structure("1aki")

    def test_electrostatic_surface(self):
        result = view.show_electrostatic_surface("#1")
        assert "Electrostatic" in result

    def test_hydrophobicity_surface(self):
        result = view.show_hydrophobicity_surface("#1")
        assert "Hydrophobicity" in result


@requires_chimerax
class TestMeasure:
    def setup_method(self):
        structure.close_structure("all")
        structure.open_structure("1aki")

    def test_measure_distance(self):
        result = measure.measure_distance("/A:50@CA", "/A:60@CA")
        assert "Distance" in result

    def test_measure_angle(self):
        result = measure.measure_angle("/A:50@N", "/A:50@CA", "/A:50@C")
        assert "Angle" in result

    def test_find_contacts(self):
        result = measure.find_contacts("/A:50", 4.0)
        assert "Contacts" in result

    def test_get_bfactors(self):
        result = measure.get_bfactors("/A:50")
        assert "factors" in result.lower()


@requires_chimerax
class TestMultiModel:
    def setup_method(self):
        structure.close_structure("all")
        structure.open_structure("1aki")
        structure.open_structure("1lz1")

    def test_align_and_rmsd(self):
        result = measure.align_and_rmsd("#1/A", "#2/A")
        assert "Alignment" in result

    def test_measure_buried_area(self):
        result = measure.measure_buried_area("#1/A", "#2/A")
        assert "Buried" in result


@requires_chimerax
class TestVideo:
    def test_record_spin(self):
        structure.close_structure("all")
        structure.open_structure("1aki")
        view.show_cartoon("#1")
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            path = f.name
        try:
            result = view.start_recording()
            assert "Recording" in result
            result = view.spin("y", 90, 30)
            assert "Spun" in result
            result = view.stop_recording(path, 30)
            assert "Movie" in result
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_record_spin_oneliner(self):
        structure.close_structure("all")
        structure.open_structure("1aki")
        view.show_cartoon("#1")
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            path = f.name
        try:
            result = view.record_spin(path, "y", 90, 30, 30)
            assert "Spin movie" in result
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

@requires_chimerax
class TestCleanup:
    def test_close_all(self):
        result = structure.close_structure("all")
        assert "Closed" in result


# ---------------------------------------------------------------------------
# Direct runner (no pytest needed)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
