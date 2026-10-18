#!/usr/local/autopkg/python
"""AutoPkg processor that renames the pkginfo MunkiImporter just wrote."""

import os

from autopkglib import Processor, ProcessorError

__all__ = ["PkginfoRenamer"]


class PkginfoRenamer(Processor):
    """Renames the imported pkginfo to pkginfo_name, keeping its directory and extension.

    MunkiImporter names a pkginfo name-version and adds __1 when that file exists, which is
    what two per-architecture imports of one version produce. Giving each its own name, such
    as AzureCLI-arm64-2.91.0.1, keeps both readable. Does nothing when nothing was imported."""

    input_variables = {
        "pkginfo_repo_path": {
            "required": False,
            "default": "",
            "description": "Path MunkiImporter wrote the pkginfo to; empty when nothing was imported.",
        },
        "pkginfo_name": {
            "required": True,
            "description": "File name for the pkginfo, without extension, such as AzureCLI-arm64-2.91.0.1.",
        },
    }
    output_variables = {
        "pkginfo_repo_path": {
            "description": "Path of the renamed pkginfo.",
        },
    }
    description = __doc__

    def main(self):
        current = self.env.get("pkginfo_repo_path") or ""
        if not current:
            self.output("Nothing imported; no pkginfo to rename.")
            return
        directory, filename = os.path.split(current)
        extension = os.path.splitext(filename)[1]
        target = os.path.join(directory, self.env["pkginfo_name"] + extension)
        if target == current:
            return
        if os.path.exists(target):
            raise ProcessorError(f"{target} already exists; not overwriting it with {current}")
        os.rename(current, target)
        self.env["pkginfo_repo_path"] = target
        summary = self.env.get("munki_importer_summary_result", {}).get("data", {})
        if summary.get("pkginfo_path"):
            summary["pkginfo_path"] = os.path.join(
                os.path.dirname(summary["pkginfo_path"]), os.path.basename(target)
            )
        self.output(f"Renamed pkginfo to: {target}")


if __name__ == "__main__":
    PROCESSOR = PkginfoRenamer()
    PROCESSOR.execute_shell()
