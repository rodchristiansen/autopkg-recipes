#!/usr/local/autopkg/python
"""AutoPkg processor that sets version to an upstream version plus a package revision."""

from autopkglib import Processor

__all__ = ["VersionRevisioner"]


class VersionRevisioner(Processor):
    """Sets version to base_version.revision, so a repackage of the same upstream release
    reads as newer to Munki and to the version pre-check that skips releases already imported."""

    input_variables = {
        "base_version": {
            "required": True,
            "description": "Upstream version, such as 2.91.0.",
        },
        "revision": {
            "required": True,
            "description": "Package revision appended to base_version, such as 1.",
        },
    }
    output_variables = {
        "version": {
            "description": "base_version and revision joined with a dot.",
        },
    }
    description = __doc__

    def main(self):
        self.env["version"] = f"{self.env['base_version']}.{self.env['revision']}"
        self.output(f"version: {self.env['version']}")


if __name__ == "__main__":
    PROCESSOR = VersionRevisioner()
    PROCESSOR.execute_shell()
