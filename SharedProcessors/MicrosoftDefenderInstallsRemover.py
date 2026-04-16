#!/usr/local/autopkg/python
"""AutoPkg processor that removes the installs array from the Microsoft Defender Munki pkginfo."""

import os

import yaml

from autopkglib import Processor, ProcessorError

__all__ = ["MicrosoftDefenderInstallsRemover"]


class MicrosoftDefenderInstallsRemover(Processor):
    """Removes the installs array from the Microsoft Defender Munki pkginfo YAML file.

    Runs after MunkiImporter to strip the installs array so Munki does not prompt
    users to quit Microsoft Defender before installation.
    """

    input_variables = {
        "pkginfo_repo_path": {
            "required": True,
            "description": "Path to the pkginfo file written by MunkiImporter.",
        },
    }
    output_variables = {}
    description = __doc__

    def main(self):
        path = self.env.get("pkginfo_repo_path", "")

        if not path:
            self.output("pkginfo_repo_path is not set — skipping.")
            return

        if not path.endswith(".yaml"):
            self.output(f"pkginfo at {path} is not a YAML file — skipping.")
            return

        if not os.path.exists(path):
            raise ProcessorError(f"pkginfo file not found: {path}")

        with open(path, "r", encoding="utf-8") as fh:
            pkginfo = yaml.safe_load(fh)

        changed = False

        if "installs" in pkginfo:
            del pkginfo["installs"]
            self.output("Removed installs array from pkginfo.")
            changed = True

        AUTOUPDATER_PACKAGE_ID = "com.microsoft.package.Microsoft_AutoUpdate.app"
        receipts = pkginfo.get("receipts", [])
        filtered = [r for r in receipts if r.get("packageid") != AUTOUPDATER_PACKAGE_ID]
        if len(filtered) < len(receipts):
            pkginfo["receipts"] = filtered
            self.output(f"Removed {AUTOUPDATER_PACKAGE_ID} from receipts.")
            changed = True

        if not changed:
            self.output("No changes needed — pkginfo already clean.")
            return

        with open(path, "w", encoding="utf-8") as fh:
            yaml.dump(pkginfo, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)

        self.output(f"Updated {os.path.basename(path)}")
