"""Keep the interactive deployment enabled and reject zero-replica release success."""

import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
INTERACTIVE = ("dify-api", "dify-web", "dify-nginx", "dify-plugin-daemon")
BACKGROUND = ("dify-worker", "dify-worker-beat", "dify-sandbox")


def test_interactive_manifests_keep_background_work_disabled():
    deployments = REPO_ROOT / "deploy/production/deployment"
    for name in INTERACTIVE:
        manifest = yaml.safe_load((deployments / f"{name}.yml").read_text())
        assert manifest["spec"]["replicas"] == 1
    for name in BACKGROUND:
        manifest = yaml.safe_load((deployments / f"{name}.yml").read_text())
        assert manifest["spec"]["replicas"] == 0


@pytest.mark.parametrize(("desired", "available", "should_succeed"), [(1, 1, True), (0, 0, False), (1, 0, False)])
def test_release_verification_requires_available_interactive_replicas(tmp_path, desired, available, should_succeed):
    kubectl = tmp_path / "kubectl"
    kubectl.write_text(
        """#!/usr/bin/env python3
import os
import sys

args = sys.argv[1:]
if args[0] == '-n':
    args = args[2:]
if args[:2] == ['get', 'deployment']:
    expression = args[-1]
    if '.spec.replicas' in expression:
        print(os.environ['TEST_DESIRED'], end='')
    elif '.status.availableReplicas' in expression:
        print(os.environ['TEST_AVAILABLE'], end='')
    elif '.image' in expression:
        image = 'dify-web' if args[2] == 'dify-web' else 'dify-api'
        print(f'ghcr.io/acedatacloud/{image}:95', end='')
"""
    )
    kubectl.chmod(0o755)
    result = subprocess.run(
        ["sh", str(REPO_ROOT / "deploy/verify-release.sh")],
        env={
            **os.environ,
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "BUILD_NUMBER": "95",
            "TEST_DESIRED": str(desired),
            "TEST_AVAILABLE": str(available),
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert (result.returncode == 0) is should_succeed, result.stdout + result.stderr
