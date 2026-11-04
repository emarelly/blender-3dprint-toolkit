"""
Starts Blender Lab's MCP server (the one Claude Desktop installed as the "Blender" extension) for
Claude Code.

Why this file exists: the extension lives inside Claude Desktop's packaged (virtualized) app data, and
its own launcher blender-mcp.exe cannot resolve its paths when started from outside the app ("Failed
to canonicalize script path"). This script runs the extension's code with the interpreter that
belongs to it, using the real on-disk locations.

Run with the extension's base Python:   <PYTHON> blender_mcp_launcher.py
(registered for Claude Code with `claude mcp add blender -- <PYTHON> <this file>`).
If Claude Desktop updates the extension or Python, adjust the two paths below.
"""
import os
import site
import sys

ROAMING = os.path.expandvars(r"%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming")
EXT = os.path.join(ROAMING, "Claude", "Claude Extensions", "ant.dir.gh.blender.blender-mcp")

site.addsitedir(os.path.join(EXT, ".venv", "Lib", "site-packages"))   # processes pywin32 .pth files
sys.path.insert(0, EXT)

from blmcp import main  # noqa: E402

if __name__ == "__main__":
    main()
