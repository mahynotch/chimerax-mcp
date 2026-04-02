# ChimeraX MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

An MCP server that connects any MCP-compatible AI coding tool to UCSF ChimeraX via its REST API, enabling natural-language protein editing with real-time visual feedback.

## Demos

**Load & Visualize** -- Load a 12-chain portal protein, isolate a monomer, apply publication styling:

![Structure workflow](assets/promo_3lj5.gif)

**Mutate Residue** -- Zoom to a site, mutate Thr->Lys, inspect the change:

![Mutation workflow](assets/promo_mutation.gif)

**Electrostatic & Hydrophobicity Surfaces** -- Coulombic ESP and Molecular Lipophilicity Potential:

![Electrostatic surface](assets/promo_electrostatic.gif)

## Features

- **39 tools** covering structure loading, editing, visualization, measurement, selection, and video recording
- **Auto-launches ChimeraX** -- no manual setup needed, just install and go
- **Works with any MCP client** -- Claude Code, Cursor, Windsurf, VS Code Copilot, Cline, OpenCode, Continue, Claude Desktop
- **Built-in agent instructions** -- AI agents automatically learn ChimeraX spec syntax and common workflows
- **Security hardened** -- command injection prevention, dangerous command blocking, script path validation
- **Accepts flexible input** -- both `A:48` and `/A:48` spec formats, both 1-letter and 3-letter amino acid codes
- **Video recording** -- capture sessions as MP4, record turntable spins
- **Run custom scripts** -- execute `.cxc` and `.py` scripts with path validation

## Prerequisites

- **UCSF ChimeraX** installed ([download](https://www.cgl.ucsf.edu/chimerax/download.html))
- **Python 3.10+**

ChimeraX will be **launched automatically** when the first tool is called. No need to start it manually or enable the REST API yourself.

<details>
<summary>Manual setup (if auto-launch doesn't work)</summary>

Open ChimeraX and run in its command line:

```
remotecontrol rest start port 8765
```

To use a custom ChimeraX install location, set the `CHIMERAX_BIN` environment variable:

```bash
export CHIMERAX_BIN="/path/to/ChimeraX"
```
</details>

## Installation

```bash
pip install git+https://github.com/mahynotch/chimerax-mcp.git
```

<details>
<summary>Other install methods</summary>

From PyPI (once published):

```bash
pip install chimerax-mcp
```

From source (development):

```bash
git clone https://github.com/mahynotch/chimerax-mcp.git
cd chimerax-mcp
pip install -e .
```
</details>

## MCP Configuration

After installing, add the server to your AI coding tool:

<details open>
<summary><strong>Claude Code</strong></summary>

```bash
claude mcp add -s user chimerax -- chimerax-mcp
```
</details>

<details>
<summary><strong>Claude Desktop</strong></summary>

Edit config file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "chimerax-mcp",
      "args": []
    }
  }
}
```
</details>

<details>
<summary><strong>Cursor</strong></summary>

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project):

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "chimerax-mcp",
      "args": []
    }
  }
}
```
</details>

<details>
<summary><strong>Windsurf</strong></summary>

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "chimerax-mcp",
      "args": []
    }
  }
}
```
</details>

<details>
<summary><strong>VS Code (Copilot)</strong></summary>

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "chimerax": {
      "type": "stdio",
      "command": "chimerax-mcp"
    }
  }
}
```
</details>

<details>
<summary><strong>Cline</strong></summary>

Use the "Edit MCP Settings" button in the Cline panel, or edit directly:
- macOS: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Windows: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "chimerax-mcp",
      "args": [],
      "disabled": false
    }
  }
}
```
</details>

<details>
<summary><strong>OpenCode</strong></summary>

Add to `~/.config/opencode/opencode.json` or project `opencode.json`:

```json
{
  "mcp": {
    "chimerax": {
      "type": "local",
      "command": ["chimerax-mcp"],
      "enabled": true
    }
  }
}
```
</details>

<details>
<summary><strong>Continue</strong></summary>

Add to `.continue/config.yaml`:

```yaml
mcpServers:
  - name: chimerax
    type: stdio
    command: chimerax-mcp
```
</details>

## Quick Start

Once configured, just talk naturally:

> "Open 6VXX, color by chain, show surface, zoom to residue A:501"

The AI will call MCP tools sequentially and ChimeraX renders each step in real time:

1. `open_structure("6VXX")` -- fetches the structure from RCSB
2. `color_structure("#1", "chain")` -- colors each chain differently
3. `show_surface("#1")` -- displays the molecular surface
4. `zoom_to("/A:501")` -- centers the view on residue 501 of chain A

## Available Tools (39)

### Structure (6)
| Tool | Description |
|------|-------------|
| `open_structure` | Open PDB ID, file path, or URL |
| `close_structure` | Close one or all models |
| `save_structure` | Save to PDB/mmCIF/mol2 |
| `list_models` | List all open models |
| `get_sequence` | Get amino acid sequence for a chain |
| `run_script` | Execute a `.cxc` or `.py` script |

### Editing (4)
| Tool | Description |
|------|-------------|
| `mutate_residue` | Swap residue using Dunbrack rotamer library |
| `delete_atoms` | Delete atoms or residues |
| `add_hydrogen` | Add hydrogens (protonate) |
| `minimize_energy` | Run energy minimization |

### Visualization (18)
| Tool | Description |
|------|-------------|
| `color_structure` | Color by scheme (`chain`, `bfactor`, `rainbow`) or named/hex color |
| `show_electrostatic_surface` | Coulombic ESP (red=negative, blue=positive) |
| `show_hydrophobicity_surface` | Molecular Lipophilicity Potential |
| `show_surface` | Show molecular surface with optional transparency |
| `hide_surface` | Hide molecular surface |
| `show_cartoon` | Show ribbon/cartoon |
| `show_sticks` | Show stick representation |
| `hide_atoms` | Hide atoms |
| `zoom_to` | Zoom camera to a selection |
| `set_background` | Set background color |
| `label_residues` | Add text labels to residues |
| `clear_labels` | Remove all labels |
| `reset_view` | Reset to default camera view |
| `take_snapshot` | Save PNG screenshot |
| `start_recording` | Begin recording session as video |
| `stop_recording` | Stop recording and save to MP4/WebM/MOV |
| `spin` | Rotate model around an axis |
| `record_spin` | Record a full turntable spin video |

### Measurement (6)
| Tool | Description |
|------|-------------|
| `measure_distance` | Distance between two atoms (Angstroms) |
| `measure_angle` | Bond angle from three atoms (degrees) |
| `align_and_rmsd` | Structural alignment with RMSD |
| `find_contacts` | Residues within N Angstroms of selection |
| `get_bfactors` | B-factor values for selection |
| `measure_buried_area` | Buried solvent-accessible surface area |

### Selection (5)
| Tool | Description |
|------|-------------|
| `select_atoms` | Select by ChimeraX specifier |
| `select_near` | Select within distance |
| `select_chain` | Select entire chain |
| `invert_selection` | Invert current selection |
| `name_selection` | Save selection under a reusable name |

## Security

Commands are sanitized before being sent to ChimeraX:

- **Command injection blocked** -- `;` and newlines rejected (ChimeraX uses these as command separators)
- **Dangerous commands blocked** -- `exec`, `shell`, `system` are rejected
- **Script execution validated** -- `run_script` only accepts existing `.cxc`/`.py` files with path validation
- **Local-only** -- REST API listens on `127.0.0.1` only, not exposed to the network

## Testing

Run the full test suite (53 tests) against a live ChimeraX instance:

```bash
pip install pytest
python -m pytest tests/test_live.py -v
```

Security tests run without ChimeraX. Live tests auto-skip if ChimeraX is not available.

## License

MIT -- see [LICENSE](LICENSE)
