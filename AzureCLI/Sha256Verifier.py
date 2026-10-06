#!/usr/local/autopkg/python
"""AutoPkg processor that checks a downloaded file against an expected SHA-256 digest."""

import hashlib

from autopkglib import Processor, ProcessorError

__all__ = ["Sha256Verifier"]


class Sha256Verifier(Processor):
    """Fails the recipe unless the file at input_path hashes to expected_sha256."""

    input_variables = {
        "input_path": {
            "required": True,
            "description": "Path to the file to verify.",
        },
        "expected_sha256": {
            "required": True,
            "description": "Expected SHA-256 digest, hex encoded.",
        },
    }
    output_variables = {}
    description = __doc__

    def main(self):
        path = self.env["input_path"]
        expected = self.env["expected_sha256"].strip().lower()
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        actual = digest.hexdigest()
        if actual != expected:
            raise ProcessorError(f"SHA-256 mismatch for {path}: expected {expected}, got {actual}")
        self.output(f"SHA-256 verified: {actual}")


if __name__ == "__main__":
    PROCESSOR = Sha256Verifier()
    PROCESSOR.execute_shell()
