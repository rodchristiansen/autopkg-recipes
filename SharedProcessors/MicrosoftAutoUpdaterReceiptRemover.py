#!/usr/local/autopkg/python
"""AutoPkg processor that removes the Microsoft AutoUpdate receipt from Munki pkginfo."""

import os

import yaml

from autopkglib import Processor, ProcessorError

__all__ = ["MicrosoftAutoUpdaterReceiptRemover"]

AUTOUPDATER_RECEIPT_ID = "com.microsoft.package.Microsoft_AutoUpdate.app"
RECEIPTS_TO_REMOVE = {
    AUTOUPDATER_RECEIPT_ID,
    "com.microsoft.pkg.licensing",
}


class MicrosoftAutoUpdaterReceiptRemover(Processor):
    """Removes the Microsoft AutoUpdate receipt from a Munki pkginfo YAML file.

    Runs after MunkiImporter to strip the AutoUpdate package receipt so it is not
    tracked alongside individual Office app receipts.
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

        receipts = pkginfo.get("receipts", [])
        filtered = [r for r in receipts if r.get("packageid") not in RECEIPTS_TO_REMOVE]

        if len(filtered) == len(receipts):
            self.output("No matching receipts found in pkginfo — no changes made.")
            return

        removed = [r.get("packageid") for r in receipts if r.get("packageid") in RECEIPTS_TO_REMOVE]

        pkginfo["receipts"] = filtered

        with open(path, "w", encoding="utf-8") as fh:
            yaml.dump(pkginfo, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)

        self.output(f"Removed receipts from {os.path.basename(path)}: {', '.join(removed)}")


if __name__ == "__main__":
    processor = MicrosoftAutoUpdaterReceiptRemover()
    processor.execute_shell()
