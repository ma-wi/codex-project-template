from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI_ROOT = ROOT / ".ai"
AI_TOOLS = AI_ROOT / "tools"
AI_CONFIG = AI_ROOT / "config"


def load_module(name: str, path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BootstrapTests(unittest.TestCase):
    bootstrap: types.ModuleType

    @classmethod
    def setUpClass(cls) -> None:
        cls.bootstrap = load_module("template_bootstrap", AI_TOOLS / "bootstrap.py")

    def test_generated_defaults_are_strict_and_reproducible(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        generated = self.bootstrap.generate_env(data)
        self.assertIn("REQUIRE_SETUP=1", generated)
        self.assertIn("REQUIRE_TEST=1", generated)
        self.assertIn("REQUIRE_SECURITY=1", generated)
        self.assertIn("uv sync --locked --all-groups", generated)
        self.assertIn("DEPENDENCY_SCAN_CMD", generated)
        self.assertIn("pip-audit", generated)
        self.assertNotIn("latest", generated)
        self.assertIn(
            'version: "0.11.29"',
            (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
        )

    def test_configuration_contains_only_project_choices(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        self.assertEqual(
            {
                "project": {"name": "CHANGE_ME"},
                "stacks": {
                    "python": {"enabled": True, "directory": "backend"},
                    "react": {
                        "enabled": False,
                        "directory": "frontend",
                        "package_manager": "npm",
                    },
                    "bash": {"enabled": False},
                    "dotnet": {
                        "enabled": False,
                        "solution": "",
                        "test_project": "",
                    },
                },
                "incremental_changes": {
                    "default_review_cadence": "batch",
                    "max_tasks_per_review_batch": 3,
                    "force_task_review_for": "migration public-api authentication authorization security dependency-change",
                },
                "engineering_knowledge": {"enabled": False},
                "documentation": {
                    "budgets": {
                        "agents_md_lines": 240,
                        "project_context_lines": 250,
                        "current_plan_lines": 35,
                        "next_steps_items": 10,
                        "active_work_item_lines": 180,
                    }
                },
            },
            data,
        )

    def test_quality_requirements_are_derived_not_configurable(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        generated = self.bootstrap.generate_env(data)
        for gate in (
            "SETUP",
            "FORMAT_CHECK",
            "LINT",
            "TEST",
            "SECURITY",
            "DEPENDENCY_POLICY",
            "DEPENDENCY_SCANNERS",
            "BUILD",
        ):
            self.assertIn(f"REQUIRE_{gate}=1", generated)

    def test_incremental_change_review_configuration_is_validated(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        data["incremental_changes"]["default_review_cadence"] = "continuous"
        with self.assertRaisesRegex(SystemExit, "default_review_cadence"):
            self.bootstrap.validate_config(data)

        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        data["incremental_changes"]["max_tasks_per_review_batch"] = 0
        with self.assertRaisesRegex(SystemExit, "max_tasks_per_review_batch"):
            self.bootstrap.validate_config(data)

    def test_unknown_configuration_keys_are_rejected(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        data["stacks"]["python"]["unused_switch"] = True
        with self.assertRaisesRegex(SystemExit, "unused_switch"):
            self.bootstrap.validate_config(data)

    def test_python_directory_is_importable_package_name(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        data["stacks"]["python"]["directory"] = "backend-api"
        with self.assertRaisesRegex(SystemExit, "importable Python package"):
            self.bootstrap.validate_config(data)
        data["stacks"]["python"]["directory"] = "src/backend"
        with self.assertRaisesRegex(SystemExit, "top-level importable Python package"):
            self.bootstrap.validate_config(data)

    def test_python_bootstrap_configures_setuptools_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pyproject = Path(temporary) / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "sample"\nversion = "0.1.0"\n',
                encoding="utf-8",
            )
            self.bootstrap.ensure_setuptools_package_discovery(pyproject, "backend")
            self.assertIn(
                '[tool.setuptools.packages.find]\ninclude = ["backend"]',
                pyproject.read_text(encoding="utf-8"),
            )

    def test_generated_python_gates_target_backend_directory(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        generated = self.bootstrap.generate_env(data)
        self.assertIn("uv run --locked mypy '\\''backend'\\'' tests", generated)
        self.assertIn("uv run --locked python -m pytest", generated)
        self.assertNotIn("mypy --exclude '^\\\\.ai/' .", generated)
        self.assertIn("uv run --locked bandit -q -r '\\''backend'\\''", generated)

    def test_dotnet_requires_explicit_test_project(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        data["stacks"]["python"]["enabled"] = False
        data["stacks"]["dotnet"]["enabled"] = True
        with self.assertRaisesRegex(SystemExit, "dotnet.test_project"):
            self.bootstrap.validate_config(data)
        data["stacks"]["dotnet"]["test_project"] = "tests/App.Tests/App.Tests.vbproj"
        self.bootstrap.validate_config(data)
        generated = self.bootstrap.generate_env(data)
        self.assertIn("dotnet test", generated)
        self.assertIn("tests/App.Tests/App.Tests.vbproj", generated)
        self.assertIn('total="[1-9][0-9]*"', generated)

    def test_powershell_files_require_a_pester_suite(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        for settings in data["stacks"].values():
            settings["enabled"] = False
        data["stacks"]["dotnet"]["enabled"] = True
        data["stacks"]["dotnet"]["test_project"] = "tests/App.Tests/App.Tests.vbproj"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "app.ps1").write_text("Write-Output 'sample'\n", encoding="utf-8")
            original_root = getattr(self.bootstrap, "ROOT")
            try:
                setattr(self.bootstrap, "ROOT", root)
                generated = self.bootstrap.generate_env(data)
            finally:
                setattr(self.bootstrap, "ROOT", original_root)
        self.assertIn("*.Tests.ps1", generated)
        self.assertNotIn("if (Test-Path tests/powershell)", generated)

    def test_react_package_managers_use_fixed_frozen_installs(self) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        data["stacks"]["react"]["enabled"] = True
        data["stacks"]["react"]["package_manager"] = "pnpm"
        generated = self.bootstrap.generate_env(data)
        self.assertIn("pnpm install --frozen-lockfile", generated)
        data["stacks"]["react"]["package_manager"] = "yarn"
        self.assertIn("yarn install --immutable", self.bootstrap.generate_env(data))

    def test_react_quality_setup_pins_project_package_manager(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            frontend = Path(temporary)
            (frontend / "src").mkdir()
            (frontend / "package.json").write_text("{}\n", encoding="utf-8")

            self.bootstrap.configure_react_quality(frontend, "pnpm")
            data = json.loads((frontend / "package.json").read_text(encoding="utf-8"))
            self.assertEqual(
                f"pnpm@{self.bootstrap.PNPM_VERSION}", data["packageManager"]
            )

            self.bootstrap.configure_react_quality(frontend, "yarn")
            data = json.loads((frontend / "package.json").read_text(encoding="utf-8"))
            self.assertEqual(
                f"yarn@{self.bootstrap.YARN_VERSION}", data["packageManager"]
            )

    def test_react_creator_is_explicitly_versioned(self) -> None:
        command, _, _ = self.bootstrap.package_manager_commands(
            "npm", "frontend", "react-ts", "9.1.1"
        )
        self.assertIn("vite@9.1.1", command)

    def test_react_quality_setup_creates_executable_smoke_test(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            frontend = Path(temporary)
            (frontend / "src").mkdir()
            (frontend / "package.json").write_text("{}\n", encoding="utf-8")
            self.bootstrap.configure_react_quality(frontend)
            smoke_test = (frontend / "src/App.test.tsx").read_text(encoding="utf-8")
            self.assertIn("renders the application shell", smoke_test)
            self.assertIn('import { expect, test } from "vitest"', smoke_test)

    def test_bash_test_gate_is_omitted_when_no_project_shell_scripts_exist(
        self,
    ) -> None:
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        data["stacks"]["python"]["enabled"] = False
        data["stacks"]["bash"]["enabled"] = True
        with tempfile.TemporaryDirectory() as temporary:
            original_root = getattr(self.bootstrap, "ROOT")
            try:
                setattr(self.bootstrap, "ROOT", Path(temporary))
                generated = self.bootstrap.generate_env(data)
            finally:
                setattr(self.bootstrap, "ROOT", original_root)
        self.assertNotIn("bats tests/shell", generated)
        self.assertIn("REQUIRE_LINT=1", generated)
        self.assertIn("REQUIRE_TEST=0", generated)

    def test_bash_test_gate_fails_when_scripts_exist_without_suite(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Generated Bash gate execution runs on the Unix CI job")
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        data["stacks"]["python"]["enabled"] = False
        data["stacks"]["bash"]["enabled"] = True
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            (root / "scripts/deploy.sh").write_text(
                "#!/usr/bin/env bash\nprintf 'deploy\\n'\n",
                encoding="utf-8",
            )
            original_root = getattr(self.bootstrap, "ROOT")
            try:
                setattr(self.bootstrap, "ROOT", root)
                generated = self.bootstrap.generate_env(data)
            finally:
                setattr(self.bootstrap, "ROOT", original_root)
        self.assertIn("test -d tests/shell", generated)
        self.assertNotIn("if [ -d tests/shell ]", generated)
        self.assertIn("Bash scripts were found", generated)
        self.assertIn("REQUIRE_TEST=1", generated)
        with tempfile.TemporaryDirectory() as temporary:
            defaults = Path(temporary) / "defaults.env"
            defaults.write_text(generated, encoding="utf-8")
            result = subprocess.run(
                [
                    shutil.which("bash") or "bash",
                    "-c",
                    'source "$1"; eval "${TEST_CMD}"',
                    "gate-test",
                    os.fspath(defaults),
                ],
                cwd=temporary,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("tests/shell is missing", result.stderr)

    def test_generated_stack_commands_fail_when_required_tools_are_missing(
        self,
    ) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Generated shell gate execution runs on the Unix CI job")
        scenarios = (
            ("python", "TEST_CMD"),
            ("python", "SECURITY_CMD"),
            ("python", "BUILD_CMD"),
            ("react", "TEST_CMD"),
            ("react", "DEPENDENCY_SCAN_CMD"),
            ("react", "BUILD_CMD"),
            ("dotnet", "TEST_CMD"),
            ("dotnet", "DEPENDENCY_SCAN_CMD"),
            ("dotnet", "BUILD_CMD"),
        )
        for stack, variable in scenarios:
            with self.subTest(stack=stack, variable=variable):
                data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
                for settings in data["stacks"].values():
                    settings["enabled"] = False
                data["stacks"][stack]["enabled"] = True
                if stack == "dotnet":
                    data["stacks"]["dotnet"]["test_project"] = (
                        "tests/App.Tests/App.Tests.vbproj"
                    )
                with tempfile.TemporaryDirectory() as temporary:
                    if stack == "react":
                        (Path(temporary) / "frontend").mkdir()
                    defaults = Path(temporary) / "defaults.env"
                    defaults.write_text(
                        self.bootstrap.generate_env(data), encoding="utf-8"
                    )
                    result = subprocess.run(
                        [
                            shutil.which("bash") or "bash",
                            "-c",
                            f'source "$1"; eval "${{{variable}}}"',
                            "gate-test",
                            os.fspath(defaults),
                        ],
                        cwd=temporary,
                        env={"PATH": ""},
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertNotEqual(0, result.returncode)

    def test_generated_python_test_gate_fails_with_zero_collected_tests(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Generated Python shell gate runs on the Unix CI job")
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        generated = self.bootstrap.generate_env(data)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_uv = fake_bin / "uv"
            fake_uv.write_text(
                "#!/usr/bin/env bash\n"
                'if [[ "$*" != "run --locked python -m pytest" ]]; then\n'
                '  printf "unexpected uv arguments: %s\\n" "$*" >&2\n'
                "  exit 127\n"
                "fi\n"
                "printf 'no tests ran\\n'\n"
                "exit 5\n",
                encoding="utf-8",
            )
            fake_uv.chmod(0o755)
            defaults = root / "defaults.env"
            defaults.write_text(generated, encoding="utf-8")
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
            result = subprocess.run(
                [
                    shutil.which("bash") or "bash",
                    "-c",
                    'source "$1"; eval "${TEST_CMD}"',
                    "gate-test",
                    os.fspath(defaults),
                ],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("no tests ran", result.stdout)

    def test_generated_dotnet_gate_requires_tests_and_pester_suite(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Generated .NET shell gate runs on the Unix CI job")
        data = self.bootstrap.load_yaml_subset(AI_ROOT / "project.yaml")
        for settings in data["stacks"].values():
            settings["enabled"] = False
        data["stacks"]["dotnet"]["enabled"] = True
        data["stacks"]["dotnet"]["test_project"] = "tests/App.Tests/App.Tests.vbproj"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "app.ps1").write_text("Write-Output 'sample'\n", encoding="utf-8")
            original_root = getattr(self.bootstrap, "ROOT")
            try:
                setattr(self.bootstrap, "ROOT", root)
                generated = self.bootstrap.generate_env(data)
            finally:
                setattr(self.bootstrap, "ROOT", original_root)

            defaults = root / "defaults.env"
            defaults.write_text(generated, encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_dotnet = fake_bin / "dotnet"
            fake_dotnet.write_text(
                "#!/usr/bin/env python3\n"
                "import os, pathlib, sys\n"
                "args = sys.argv[1:]\n"
                "result_dir = pathlib.Path(args[args.index('--results-directory') + 1])\n"
                "result_dir.mkdir(parents=True, exist_ok=True)\n"
                "total = os.environ['DOTNET_TEST_TOTAL']\n"
                "(result_dir / 'agent-template.trx').write_text(f'<Counters total=\"{total}\" />\\n')\n",
                encoding="utf-8",
            )
            fake_dotnet.chmod(0o755)
            fake_pwsh = fake_bin / "pwsh"
            fake_pwsh.write_text(
                "#!/usr/bin/env python3\nraise SystemExit(0)\n", encoding="utf-8"
            )
            fake_pwsh.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
            command = [
                shutil.which("bash") or "bash",
                "-c",
                'source "$1"; eval "${TEST_CMD}"',
                "gate-test",
                os.fspath(defaults),
            ]

            environment["DOTNET_TEST_TOTAL"] = "2"
            missing_pester = subprocess.run(
                command,
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, missing_pester.returncode)

            pester_dir = root / "tests/powershell"
            pester_dir.mkdir(parents=True)
            (pester_dir / "App.Tests.ps1").write_text(
                "Describe 'sample' {}\n", encoding="utf-8"
            )
            environment["DOTNET_TEST_TOTAL"] = "0"
            zero_dotnet_tests = subprocess.run(
                command,
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, zero_dotnet_tests.returncode)

            environment["DOTNET_TEST_TOTAL"] = "2"
            passing = subprocess.run(
                command,
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, passing.returncode, passing.stdout + passing.stderr)

    def test_paths_cannot_escape_repository(self) -> None:
        with self.assertRaises(SystemExit):
            self.bootstrap.validate_repository_path("../outside", "test.path")
        with self.assertRaises(SystemExit):
            self.bootstrap.validate_repository_path(
                str(Path(tempfile.gettempdir()) / "outside"), "test.path"
            )

    def test_bootstrap_generates_versioned_defaults_without_network_for_empty_stack_set(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai/tools").mkdir(parents=True)
            (root / ".ai/config").mkdir()
            shutil.copy2(AI_TOOLS / "bootstrap.py", root / ".ai/tools/bootstrap.py")
            shutil.copy2(AI_TOOLS / "_common.py", root / ".ai/tools/_common.py")
            config = (AI_ROOT / "project.yaml").read_text(encoding="utf-8")
            config = config.replace('name: "CHANGE_ME"', 'name: "sample"', 1)
            config = config.replace(
                "  python:\n    enabled: true", "  python:\n    enabled: false", 1
            )
            (root / ".ai/project.yaml").write_text(config, encoding="utf-8")
            shutil.copy2(
                AI_ROOT / "PROJECT_CONTEXT.md", root / ".ai/PROJECT_CONTEXT.md"
            )
            result = subprocess.run(
                [sys.executable, os.fspath(root / ".ai/tools/bootstrap.py")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue((root / "README.md").is_file())
            self.assertTrue((root / ".ai/DECISIONS.md").is_file())
            defaults = (root / ".ai/config/project.defaults.env").read_text(
                encoding="utf-8"
            )
            self.assertIn("Generated by .ai/tools/bootstrap.py", defaults)
            self.assertNotIn("project.env\n", result.stdout)

    def test_bootstrap_replaces_completed_bootstrap_next_step(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / ".ai/NEXT_STEPS.md"
            path.parent.mkdir()
            path.write_text(
                "# Next steps\n\n1. Run bootstrap and commit the generated files.\n",
                encoding="utf-8",
            )
            original_root = getattr(self.bootstrap, "ROOT")
            try:
                setattr(self.bootstrap, "ROOT", root)
                self.bootstrap.update_next_steps()
            finally:
                setattr(self.bootstrap, "ROOT", original_root)
            updated = path.read_text(encoding="utf-8")
            self.assertNotIn("Run bootstrap", updated)
            self.assertIn(".ai/PROJECT_CONTEXT.md", updated)
            self.assertIn(".ai/policies/QUALITY_GATES.md", updated)


class GateTests(unittest.TestCase):
    def test_join_with_and_chains_commands(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Bash gate test runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai/tools").mkdir(parents=True)
            shutil.copy2(AI_TOOLS / "lib.sh", root / ".ai/tools/lib.sh")
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source .ai/tools/lib.sh; join_with_and "a x" "b" "c"',
                ],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("a x && b && c", result.stdout)

    def test_detect_security_joins_multiple_tools_with_and(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Bash gate test runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai/tools").mkdir(parents=True)
            shutil.copy2(AI_TOOLS / "lib.sh", root / ".ai/tools/lib.sh")
            # Markers plus fake tools so more than one command is detected.
            (root / "requirements.txt").write_text("", encoding="utf-8")
            (root / "package.json").write_text("{}\n", encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            for tool in ("gitleaks", "npm", "pip-audit"):
                executable = fake_bin / tool
                executable.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
                executable.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
            result = subprocess.run(
                ["bash", "-c", "source .ai/tools/lib.sh; detect_security"],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn(" && ", result.stdout)
            self.assertIn("gitleaks", result.stdout)
            self.assertIn("pip-audit", result.stdout)

    def test_required_missing_command_fails(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Bash gate test runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai/tools").mkdir(parents=True)
            (root / ".ai/config").mkdir()
            for name in ("lib.sh", "format.sh"):
                shutil.copy2(AI_TOOLS / name, root / ".ai/tools" / name)
            (root / ".ai/config/project.defaults.env").write_text(
                "FORMAT_CHECK_CMD=''\nREQUIRE_FORMAT_CHECK=1\n", encoding="utf-8"
            )
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/format.sh"), "--check"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("required but no command", result.stderr)

    def test_local_override_cannot_disable_committed_required_gate(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Bash gate test runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai/tools").mkdir(parents=True)
            (root / ".ai/config").mkdir()
            for name in ("lib.sh", "format.sh"):
                shutil.copy2(AI_TOOLS / name, root / ".ai/tools" / name)
            (root / ".ai/config/project.defaults.env").write_text(
                "FORMAT_CHECK_CMD='true'\nREQUIRE_FORMAT_CHECK=1\n",
                encoding="utf-8",
            )
            (root / ".ai/config/project.env").write_text(
                "REQUIRE_FORMAT_CHECK=0\n", encoding="utf-8"
            )
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/format.sh"), "--check"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("cannot weaken committed policy", result.stderr)


class DependencyPolicyTests(unittest.TestCase):
    def make_repository(self, temporary: str) -> Path:
        root = Path(temporary)
        (root / ".ai/tools").mkdir(parents=True)
        (root / ".ai/config").mkdir()
        shutil.copy2(
            AI_TOOLS / "dependency_policy.py", root / ".ai/tools/dependency_policy.py"
        )
        (root / ".ai/config/dependency-allowlist.txt").write_text("", encoding="utf-8")
        (root / ".ai/config/dependency-denylist.txt").write_text("", encoding="utf-8")
        return root

    def run_policy(
        self, root: Path, **environment: str
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(environment)
        return subprocess.run(
            [sys.executable, os.fspath(root / ".ai/tools/dependency_policy.py")],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_nested_frontend_requires_adjacent_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            frontend = root / "frontend"
            frontend.mkdir()
            (frontend / "package.json").write_text(
                json.dumps({"dependencies": {"react": "^19.1.0"}}), encoding="utf-8"
            )
            result = self.run_policy(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("frontend/package.json", result.stderr)
            (frontend / "package-lock.json").write_text("{}\n", encoding="utf-8")
            result = self.run_policy(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("npm:react", result.stdout)

    def test_python_groups_require_uv_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            (root / "pyproject.toml").write_text(
                '[project]\nname="sample"\nversion="0.1.0"\ndependencies=[]\n'
                '[dependency-groups]\ndev=["pytest==8.4.1"]\n',
                encoding="utf-8",
            )
            result = self.run_policy(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("uv.lock", result.stderr)
            (root / "uv.lock").write_text("version = 1\n", encoding="utf-8")
            result = self.run_policy(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("pypi:pytest", result.stdout)

    def test_dotnet_stack_requires_package_lock_and_reads_central_version(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            project = root / "src/App"
            project.mkdir(parents=True)
            (root / "Directory.Packages.props").write_text(
                '<Project><ItemGroup><PackageVersion Include="Example.Package" Version="1.2.3" />'
                "</ItemGroup></Project>\n",
                encoding="utf-8",
            )
            (project / "App.vbproj").write_text(
                '<Project><ItemGroup><PackageReference Include="Example.Package" />'
                "</ItemGroup></Project>\n",
                encoding="utf-8",
            )
            result = self.run_policy(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("packages.lock.json", result.stderr)
            (project / "packages.lock.json").write_text("{}\n", encoding="utf-8")
            result = self.run_policy(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("nuget:Example.Package 1.2.3", result.stdout)

    def test_allowlist_mode_reaches_policy_process(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"react": "^19.1.0"}}), encoding="utf-8"
            )
            (root / "package-lock.json").write_text("{}\n", encoding="utf-8")
            result = self.run_policy(root, DEPENDENCY_ALLOWLIST_MODE="1")
            self.assertNotEqual(0, result.returncode)
            self.assertIn("not on allow-list", result.stderr)
            (root / ".ai/config/dependency-allowlist.txt").write_text(
                "npm:react\n", encoding="utf-8"
            )
            result = self.run_policy(root, DEPENDENCY_ALLOWLIST_MODE="1")
            self.assertEqual(0, result.returncode, result.stderr)

    def test_local_override_reaches_policy_through_shell_gate(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Shell gate test runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            for name in ("lib.sh", "check-dependencies.sh"):
                shutil.copy2(AI_TOOLS / name, root / ".ai/tools" / name)
            (root / ".ai/config/dependency-policy.conf").write_text(
                "DEPENDENCY_ALLOWLIST_MODE=0\nREQUIRE_LOCKFILES=1\nREJECT_FLOATING_VERSIONS=1\n",
                encoding="utf-8",
            )
            (root / ".ai/config/project.defaults.env").write_text(
                "REQUIRE_DEPENDENCY_POLICY=1\nREQUIRE_DEPENDENCY_SCANNERS=0\n",
                encoding="utf-8",
            )
            (root / ".ai/config/project.env").write_text(
                "DEPENDENCY_ALLOWLIST_MODE=1\n", encoding="utf-8"
            )
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"react": "^19.1.0"}}), encoding="utf-8"
            )
            (root / "package-lock.json").write_text("{}\n", encoding="utf-8")
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/check-dependencies.sh")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("not on allow-list", result.stderr)

    def test_unknown_requirement_syntax_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            (root / "requirements.txt").write_text(
                "--index-url https://example.invalid/simple\n"
                "example-package @ git+https://example.invalid/repo.git@main\n",
                encoding="utf-8",
            )
            result = self.run_policy(root, REQUIRE_LOCKFILES="0")
            self.assertNotEqual(0, result.returncode)
            self.assertIn("unsupported dependency syntax", result.stderr)

    def test_remote_npm_dependency_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            (root / "package.json").write_text(
                json.dumps(
                    {"dependencies": {"example": "github:owner/repository#main"}}
                ),
                encoding="utf-8",
            )
            (root / "package-lock.json").write_text("{}\n", encoding="utf-8")
            result = self.run_policy(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("remote or mutable source", result.stderr)

    def test_poetry_git_dependency_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            (root / "pyproject.toml").write_text(
                '[tool.poetry]\nname="sample"\nversion="0.1.0"\n'
                '[tool.poetry.dependencies]\npython="^3.13"\n'
                'evil={git="https://example.invalid/evil.git", branch="main"}\n',
                encoding="utf-8",
            )
            (root / "uv.lock").write_text("version = 1\n", encoding="utf-8")
            result = self.run_policy(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("remote or mutable source", result.stderr)

    def test_cargo_path_dependency_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_repository(temporary)
            (root / "Cargo.toml").write_text(
                '[package]\nname="sample"\nversion="0.1.0"\n'
                '[dependencies]\nevil={version="1.0.0", path="../evil"}\n',
                encoding="utf-8",
            )
            (root / "Cargo.lock").write_text("# lock\n", encoding="utf-8")
            result = self.run_policy(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("remote or mutable source", result.stderr)


class CopySafetyTests(unittest.TestCase):
    def make_copy_fixture(self, root: Path) -> Path:
        source = root / "source"
        (source / ".ai/tools").mkdir(parents=True)
        shutil.copy2(AI_TOOLS / "create-project.sh", source / ".ai/tools")
        shutil.copy2(AI_TOOLS / "create-project.ps1", source / ".ai/tools")
        (source / "README.md").write_text("template readme\n", encoding="utf-8")
        (source / "tests").mkdir()
        (source / "tests/template_test.py").write_text("template\n", encoding="utf-8")
        (source / ".ai/CURRENT_PLAN.md").write_text(
            "# Current work\n\n- Work directory: `.ai/work/template-task/`\n",
            encoding="utf-8",
        )
        (source / ".ai/work/template-task").mkdir(parents=True)
        (source / ".ai/work/template-task/PLAN.md").write_text(
            "template work\n", encoding="utf-8"
        )
        # Per-project scaffold that must be copied; and a local override that
        # must never leak into a copied project.
        (source / ".ai/DECISIONS.md").write_text(
            "# Operational decisions\n", encoding="utf-8"
        )
        (source / ".ai/config").mkdir(parents=True)
        shutil.copy2(AI_CONFIG / "copy-exclude.txt", source / ".ai/config")
        (source / ".ai/config/project.env").write_text("LOCAL=1\n", encoding="utf-8")
        (source / ".ai/config/project.env.example").write_text(
            "# example\n", encoding="utf-8"
        )
        (source / "config").mkdir()
        (source / "config/app.conf").write_text("project config\n", encoding="utf-8")
        (source / "scripts").mkdir()
        (source / "scripts/app.sh").write_text("project script\n", encoding="utf-8")
        template_spec = source / "docs/specifications/REQ-ai-control-plane-layout.md"
        template_spec.parent.mkdir(parents=True)
        template_spec.write_text("template migration\n", encoding="utf-8")
        template_adr = (
            source / "docs/architecture/decisions/ADR-0001-ai-control-plane.md"
        )
        template_adr.parent.mkdir(parents=True)
        template_adr.write_text("template migration\n", encoding="utf-8")
        nested = source / "docs/module"
        (nested / "tests").mkdir(parents=True)
        (nested / "README.md").write_text("nested readme\n", encoding="utf-8")
        (nested / "tests/keep.txt").write_text("nested tests\n", encoding="utf-8")
        for name in (
            ".git",
            ".idea",
            ".vscode",
            ".cursor",
            ".claude",
            ".codex",
            "node_modules",
            "__pycache__",
            "build",
        ):
            state = nested / name
            state.mkdir()
            (state / "private.txt").write_text("state\n", encoding="utf-8")
        return source

    def assert_fixture_copy_boundary(self, target: Path) -> None:
        self.assertFalse((target / "README.md").exists())
        self.assertFalse((target / "tests").exists())
        self.assertTrue((target / "docs/module/README.md").is_file())
        self.assertTrue((target / "docs/module/tests/keep.txt").is_file())
        self.assertTrue((target / "config/app.conf").is_file())
        self.assertTrue((target / "scripts/app.sh").is_file())
        self.assertFalse((target / ".ai/work").exists())
        # Local override and template-only operational decisions are excluded;
        # the project creates decisions during bootstrap when needed.
        self.assertFalse((target / ".ai/config/project.env").exists())
        self.assertTrue((target / ".ai/config/project.env.example").is_file())
        self.assertFalse((target / ".ai/DECISIONS.md").exists())
        self.assertEqual(
            "# Current work\n\nNo active requirement.\n",
            (target / ".ai/CURRENT_PLAN.md").read_text(encoding="utf-8"),
        )
        self.assertFalse(
            (target / "docs/specifications/REQ-ai-control-plane-layout.md").exists()
        )
        self.assertFalse(
            (
                target / "docs/architecture/decisions/ADR-0001-ai-control-plane.md"
            ).exists()
        )
        for name in (
            ".git",
            ".idea",
            ".vscode",
            ".cursor",
            ".claude",
            ".codex",
            "node_modules",
            "__pycache__",
            "build",
        ):
            with self.subTest(state=name):
                self.assertFalse((target / "docs/module" / name).exists())

    def assert_project_copy_boundary(self, target: Path) -> None:
        excluded = (
            "README.md",
            "CHANGELOG.md",
            "tests",
            ".ai/work",
            "docs/architecture/decisions/ADR-0001-ai-control-plane.md",
            "docs/specifications/REQ-ai-control-plane-layout.md",
            "docs/requirements/REQ-template-hardening.md",
            "docs/specifications/REQ-template-hardening.md",
            ".github/workflows/template-copy.yml",
            ".ai/DECISIONS.md",
            ".ai/tools/create-project.sh",
            ".ai/tools/create-project.ps1",
            ".ai/tools/verify-template.sh",
            ".ai/config/copy-exclude.txt",
        )
        for relative in excluded:
            with self.subTest(relative=relative):
                self.assertFalse((target / relative).exists())

        retained = (
            "AGENTS.md",
            ".ai/project.yaml",
            ".ai/policies/SECURITY_GUIDELINES.md",
            ".ai/templates/ADR.md",
            ".ai/templates/THREAT_MODEL.md",
            ".ai/templates/OWNERSHIP.md",
            ".ai/tools/_common.py",
            ".github/workflows/ci.yml",
            ".ai/tools/bootstrap.py",
            ".ai/tools/verify.sh",
        )
        for relative in retained:
            with self.subTest(relative=relative):
                self.assertTrue((target / relative).is_file())
        project_ci = (target / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertNotIn("windows-template-copy", project_ci)
        self.assertEqual(
            "# Current work\n\nNo active requirement.\n",
            (target / ".ai/CURRENT_PLAN.md").read_text(encoding="utf-8"),
        )
        work_state = subprocess.run(
            ["python3", os.fspath(target / ".ai/tools/check-work-state.py")],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            0, work_state.returncode, work_state.stdout + work_state.stderr
        )

    def test_shell_rejects_target_inside_template(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Shell copy test runs on the Unix CI job")
        target = ROOT / ".copy-safety-test-target"
        self.assertFalse(target.exists())
        result = subprocess.run(
            [str(AI_TOOLS / "create-project.sh"), os.fspath(target)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(target.exists())

    def test_shell_dry_run_does_not_create_target(self) -> None:
        if os.name == "nt" or not shutil.which("rsync"):
            self.skipTest("rsync is required for dry-run")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "preview-only"
            result = subprocess.run(
                [
                    str(AI_TOOLS / "create-project.sh"),
                    "--dry-run",
                    os.fspath(target),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse(target.exists())

    def test_shell_rsync_exclusions_are_root_aware(self) -> None:
        if os.name == "nt" or not shutil.which("rsync"):
            self.skipTest("rsync is required")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_copy_fixture(root)
            target = root / "target"
            result = subprocess.run(
                [os.fspath(source / ".ai/tools/create-project.sh"), os.fspath(target)],
                cwd=source,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assert_fixture_copy_boundary(target)

    def test_shell_tar_fallback_exclusions_are_root_aware(self) -> None:
        if os.name == "nt":
            self.skipTest("tar fallback test runs on Unix")
        required = ("bash", "dirname", "find", "mkdir", "python3", "tar")
        if any(not shutil.which(command) for command in required):
            self.skipTest("tar fallback prerequisites are unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_copy_fixture(root)
            target = root / "target"
            command_directory = root / "commands"
            command_directory.mkdir()
            for command in required:
                resolved = shutil.which(command)
                if resolved is None:
                    self.fail(f"Required command disappeared: {command}")
                os.symlink(resolved, command_directory / command)
            environment = os.environ.copy()
            environment["PATH"] = os.fspath(command_directory)
            result = subprocess.run(
                [
                    os.fspath(command_directory / "bash"),
                    os.fspath(source / ".ai/tools/create-project.sh"),
                    os.fspath(target),
                ],
                cwd=source,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assert_fixture_copy_boundary(target)

    def test_shell_force_preserves_unrelated_target_content(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Shell copy test runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target-project"
            protected = target / "build/keep.txt"
            protected.parent.mkdir(parents=True)
            protected.write_text("user data\n", encoding="utf-8")
            result = subprocess.run(
                [str(AI_TOOLS / "create-project.sh"), "--force", os.fspath(target)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("user data\n", protected.read_text(encoding="utf-8"))
            self.assert_project_copy_boundary(target)
            verification = subprocess.run(
                ["bash", os.fspath(target / ".ai/tools/verify.sh")],
                cwd=target,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, verification.returncode)
            self.assertIn("bootstrap is required", verification.stderr)

    def test_powershell_force_preserves_unrelated_target_content(self) -> None:
        if not shutil.which("pwsh"):
            self.skipTest("PowerShell is not installed")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target-project"
            protected = target / "build/keep.txt"
            protected.parent.mkdir(parents=True)
            protected.write_text("user data\n", encoding="utf-8")
            result = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    os.fspath(AI_TOOLS / "create-project.ps1"),
                    "-TargetDirectory",
                    os.fspath(target),
                    "-Force",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("user data\n", protected.read_text(encoding="utf-8"))
            self.assert_project_copy_boundary(target)

    def test_powershell_current_plan_is_byte_identical_to_shell(self) -> None:
        if not shutil.which("pwsh"):
            self.skipTest("PowerShell is not installed")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_copy_fixture(root)
            target = root / "target"
            result = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    os.fspath(source / ".ai/tools/create-project.ps1"),
                    "-TargetDirectory",
                    os.fspath(target),
                ],
                cwd=source,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            # Byte comparison catches CRLF/BOM drift that text-mode reads hide.
            self.assertEqual(
                b"# Current work\n\nNo active requirement.\n",
                (target / ".ai/CURRENT_PLAN.md").read_bytes(),
            )

    def test_powershell_exclusions_are_root_aware(self) -> None:
        if not shutil.which("pwsh"):
            self.skipTest("PowerShell is not installed")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_copy_fixture(root)
            target = root / "target"
            result = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    os.fspath(source / ".ai/tools/create-project.ps1"),
                    "-TargetDirectory",
                    os.fspath(target),
                ],
                cwd=source,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assert_fixture_copy_boundary(target)

    def test_powershell_rejects_linked_target_inside_source(self) -> None:
        if not shutil.which("pwsh"):
            self.skipTest("PowerShell is not installed")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_copy_fixture(root)
            inside = source / "linked-target"
            inside.mkdir()
            linked_target = root / "outside-link"
            if os.name == "nt":
                link_result = subprocess.run(
                    [
                        "cmd",
                        "/c",
                        "mklink",
                        "/J",
                        os.fspath(linked_target),
                        os.fspath(inside),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if link_result.returncode != 0:
                    self.skipTest("Could not create a Windows junction")
            else:
                linked_target.symlink_to(inside, target_is_directory=True)
            result = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    os.fspath(source / ".ai/tools/create-project.ps1"),
                    "-TargetDirectory",
                    os.fspath(linked_target),
                ],
                cwd=source,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("outside the template source", result.stderr)
            self.assertEqual([], list(inside.iterdir()))

    def test_powershell_whatif_does_not_create_target(self) -> None:
        if not shutil.which("pwsh"):
            self.skipTest("PowerShell is not installed")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "preview-only"
            result = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    os.fspath(AI_TOOLS / "create-project.ps1"),
                    "-TargetDirectory",
                    os.fspath(target),
                    "-WhatIf",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse(target.exists())

    def make_update_fixture(self, root: Path) -> Path:
        source = root / "source"
        (source / ".ai/tools").mkdir(parents=True)
        shutil.copy2(AI_TOOLS / "create-project.sh", source / ".ai/tools")
        (source / ".ai/config").mkdir(parents=True)
        shutil.copy2(AI_CONFIG / "copy-exclude.txt", source / ".ai/config")
        (source / "AGENTS.md").write_text("template agents\n", encoding="utf-8")
        (source / ".ai/policies").mkdir(parents=True)
        # Project-owned per the [update_protected] manifest section.
        (source / ".ai/project.yaml").write_text("name: template\n", encoding="utf-8")
        # Reusable control-plane file whose template content changed.
        (source / ".ai/policies/WORKFLOW.md").write_text(
            "workflow v2\n", encoding="utf-8"
        )
        # File that only exists in the newer template.
        (source / ".ai/policies/NEWFILE.md").write_text("brand new\n", encoding="utf-8")
        # Excluded from any copy or update.
        (source / "README.md").write_text("template readme\n", encoding="utf-8")
        return source

    def make_update_project(self, root: Path) -> Path:
        project = root / "project"
        (project / ".ai/policies").mkdir(parents=True)
        (project / "AGENTS.md").write_text("template agents\n", encoding="utf-8")
        (project / ".ai/project.yaml").write_text("name: myproject\n", encoding="utf-8")
        (project / ".ai/policies/WORKFLOW.md").write_text(
            "workflow v1\n", encoding="utf-8"
        )
        (project / "README.md").write_text("project readme\n", encoding="utf-8")
        return project

    def test_shell_update_writes_patch_without_touching_target(self) -> None:
        if os.name == "nt" or not shutil.which("bash") or not shutil.which("diff"):
            self.skipTest("Shell update test needs bash and diff")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_update_fixture(root)
            project = self.make_update_project(root)
            patch = root / "out.patch"
            result = subprocess.run(
                [
                    os.fspath(source / ".ai/tools/create-project.sh"),
                    "--update",
                    "--patch-file",
                    os.fspath(patch),
                    os.fspath(project),
                ],
                cwd=source,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            # The target is left completely untouched in patch mode.
            self.assertEqual(
                "workflow v1\n",
                (project / ".ai/policies/WORKFLOW.md").read_text(encoding="utf-8"),
            )
            self.assertFalse((project / ".ai/policies/NEWFILE.md").exists())
            self.assertEqual(
                "name: myproject\n",
                (project / ".ai/project.yaml").read_text(encoding="utf-8"),
            )
            patch_text = patch.read_text(encoding="utf-8")
            self.assertIn("b/.ai/policies/NEWFILE.md", patch_text)
            self.assertIn("b/.ai/policies/WORKFLOW.md", patch_text)
            self.assertNotIn("b/.ai/project.yaml", patch_text)
            manual = root / "out.manual.patch"
            self.assertIn("b/.ai/project.yaml", manual.read_text(encoding="utf-8"))

    def test_shell_update_apply_integrates_changes_and_protects_seed(self) -> None:
        if os.name == "nt" or not shutil.which("bash") or not shutil.which("diff"):
            self.skipTest("Shell update test needs bash and diff")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_update_fixture(root)
            project = self.make_update_project(root)
            patch = root / "out.patch"
            result = subprocess.run(
                [
                    os.fspath(source / ".ai/tools/create-project.sh"),
                    "--update",
                    "--apply",
                    "--patch-file",
                    os.fspath(patch),
                    os.fspath(project),
                ],
                cwd=source,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            # New and changed reusable files are integrated.
            self.assertEqual(
                "brand new\n",
                (project / ".ai/policies/NEWFILE.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                "workflow v2\n",
                (project / ".ai/policies/WORKFLOW.md").read_text(encoding="utf-8"),
            )
            # Project-owned and excluded files are preserved verbatim.
            self.assertEqual(
                "name: myproject\n",
                (project / ".ai/project.yaml").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                "project readme\n",
                (project / "README.md").read_text(encoding="utf-8"),
            )
            # The protected difference is still surfaced for manual merge.
            self.assertIn(
                "b/.ai/project.yaml",
                (root / "out.manual.patch").read_text(encoding="utf-8"),
            )

    def test_shell_update_rejects_non_template_target(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Shell update test runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_update_fixture(root)
            empty = root / "not-a-project"
            empty.mkdir()
            result = subprocess.run(
                [
                    os.fspath(source / ".ai/tools/create-project.sh"),
                    "--update",
                    os.fspath(empty),
                ],
                cwd=source,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("does not look like", result.stderr)


class LifecycleTests(unittest.TestCase):
    def test_repository_work_state_is_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, str(AI_TOOLS / "check-work-state.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS:", result.stdout)

    def make_lifecycle_repo(self, root: Path) -> None:
        (root / ".ai/tools").mkdir(parents=True)
        shutil.copy2(
            AI_TOOLS / "check-work-state.py",
            root / ".ai/tools/check-work-state.py",
        )
        shutil.copy2(AI_TOOLS / "_common.py", root / ".ai/tools/_common.py")

    def run_work_state(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, os.fspath(root / ".ai/tools/check-work-state.py")],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_idle_status_plan_is_treated_as_inactive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_lifecycle_repo(root)
            (root / ".ai/CURRENT_PLAN.md").write_text(
                "# Current work\n\n- Status: idle\n", encoding="utf-8"
            )
            result = self.run_work_state(root)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("no active temporary work", result.stdout)

    def test_discovery_phase_without_plan_pointer_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_lifecycle_repo(root)
            (root / ".ai/work/REQ-001").mkdir(parents=True)
            (root / ".ai/CURRENT_PLAN.md").write_text(
                "# Current work\n\n"
                "- Work directory: `.ai/work/REQ-001/`\n"
                "- Specification: `not-required`\n"
                "- Status: discovery\n",
                encoding="utf-8",
            )
            result = self.run_work_state(root)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_planning_phase_requires_plan_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_lifecycle_repo(root)
            (root / ".ai/work/REQ-001").mkdir(parents=True)
            (root / ".ai/CURRENT_PLAN.md").write_text(
                "# Current work\n\n"
                "- Work directory: `.ai/work/REQ-001/`\n"
                "- Specification: `not-required`\n"
                "- Status: planning\n",
                encoding="utf-8",
            )
            result = self.run_work_state(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("must contain a 'Plan' field", result.stdout)

    def test_significant_lifecycle_uses_durable_ready_specification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai/tools").mkdir(parents=True)
            shutil.copy2(
                AI_TOOLS / "check-work-state.py",
                root / ".ai/tools/check-work-state.py",
            )
            shutil.copy2(AI_TOOLS / "_common.py", root / ".ai/tools/_common.py")
            work = root / ".ai/work/REQ-001/tasks"
            work.mkdir(parents=True)
            specs = root / "docs/specifications"
            specs.mkdir(parents=True)
            (root / ".ai/CURRENT_PLAN.md").write_text(
                "# Current work\n\n"
                "- Requirement: `docs/requirements/REQ-001.md`\n"
                "- Work directory: `.ai/work/REQ-001/`\n"
                "- Specification: `docs/specifications/REQ-001.md`\n"
                "- Plan: `.ai/work/REQ-001/PLAN.md`\n"
                "- Status: implementation\n",
                encoding="utf-8",
            )
            (specs / "REQ-001.md").write_text(
                "# Specification\n\n- Status: ready-for-implementation\n"
                "- Ready for implementation: yes\n",
                encoding="utf-8",
            )
            (root / ".ai/work/REQ-001/PLAN.md").write_text(
                "# Plan\n\n- Change class: significant\n", encoding="utf-8"
            )
            (work / "T001.md").write_text(
                "# Task\n\n- Status: verified\n", encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, os.fspath(root / ".ai/tools/check-work-state.py")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("1 task file", result.stdout)

    def test_multiple_capability_specifications_are_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_lifecycle_repo(root)
            work = root / ".ai/work/REQ-001/tasks"
            work.mkdir(parents=True)
            specs = root / "docs/specifications"
            specs.mkdir(parents=True)
            for name in ("customer-management.md", "reporting.md"):
                (specs / name).write_text(
                    "# Capability\n\n"
                    "- Status: ready-for-implementation\n"
                    "- Ready for implementation: yes\n",
                    encoding="utf-8",
                )
            (root / ".ai/CURRENT_PLAN.md").write_text(
                "# Current work\n\n"
                "- Work directory: `.ai/work/REQ-001/`\n"
                "- Specifications: `docs/specifications/customer-management.md`, `docs/specifications/reporting.md`\n"
                "- Plan: `.ai/work/REQ-001/PLAN.md`\n"
                "- Status: implementation\n",
                encoding="utf-8",
            )
            (root / ".ai/work/REQ-001/PLAN.md").write_text(
                "# Plan\n\n- Change class: significant\n", encoding="utf-8"
            )
            result = self.run_work_state(root)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_work_directory_traversal_is_rejected_after_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai/tools").mkdir(parents=True)
            shutil.copy2(
                AI_TOOLS / "check-work-state.py",
                root / ".ai/tools/check-work-state.py",
            )
            shutil.copy2(AI_TOOLS / "_common.py", root / ".ai/tools/_common.py")
            escaped = root / ".ai/escaped"
            escaped.mkdir(parents=True)
            (escaped / "PLAN.md").write_text(
                "# Plan\n\n- Change class: normal\n", encoding="utf-8"
            )
            (root / ".ai/CURRENT_PLAN.md").write_text(
                "# Current work\n\n"
                "- Work directory: `.ai/work/../escaped/`\n"
                "- Specification: `not-required`\n"
                "- Plan: `.ai/work/../escaped/PLAN.md`\n"
                "- Status: implementation\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, os.fspath(root / ".ai/tools/check-work-state.py")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("below .ai/work", result.stdout)

    def test_specification_traversal_is_rejected_after_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".ai/tools").mkdir(parents=True)
            shutil.copy2(
                AI_TOOLS / "check-work-state.py",
                root / ".ai/tools/check-work-state.py",
            )
            shutil.copy2(AI_TOOLS / "_common.py", root / ".ai/tools/_common.py")
            work = root / ".ai/work/REQ-001"
            work.mkdir(parents=True)
            (work / "PLAN.md").write_text(
                "# Plan\n\n- Change class: significant\n", encoding="utf-8"
            )
            escaped_spec = root / "docs/escaped.md"
            escaped_spec.parent.mkdir()
            escaped_spec.write_text(
                "- Status: ready-for-implementation\n- Ready for implementation: yes\n",
                encoding="utf-8",
            )
            (root / ".ai/CURRENT_PLAN.md").write_text(
                "# Current work\n\n"
                "- Work directory: `.ai/work/REQ-001/`\n"
                "- Specification: `docs/specifications/../escaped.md`\n"
                "- Plan: `.ai/work/REQ-001/PLAN.md`\n"
                "- Status: implementation\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, os.fspath(root / ".ai/tools/check-work-state.py")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("below docs/specifications", result.stdout)


class IncrementalChangeTests(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        (root / ".ai/tools").mkdir(parents=True)
        shutil.copy2(
            AI_TOOLS / "check-change-impact.py",
            root / ".ai/tools/check-change-impact.py",
        )
        shutil.copy2(AI_TOOLS / "_common.py", root / ".ai/tools/_common.py")
        (root / ".ai/work/CHG-001/tasks").mkdir(parents=True)
        (root / ".ai/project.yaml").write_text(
            "incremental_changes:\n"
            '  default_review_cadence: "batch"\n'
            "  max_tasks_per_review_batch: 2\n"
            '  force_task_review_for: "migration security"\n',
            encoding="utf-8",
        )

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, os.fspath(root / ".ai/tools/check-change-impact.py")],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def write_valid_change(self, root: Path, *, cadence: str = "batch") -> None:
        work = root / ".ai/work/CHG-001"
        (root / ".ai/CURRENT_PLAN.md").write_text(
            "# Current work\n\n"
            "- Work type: incremental-change\n"
            "- Work directory: `.ai/work/CHG-001/`\n"
            "- Change request: `.ai/work/CHG-001/CHANGE.md`\n"
            "- Change impact: `.ai/work/CHG-001/IMPACT.md`\n"
            "- Plan: `.ai/work/CHG-001/PLAN.md`\n"
            "- Status: implementation\n",
            encoding="utf-8",
        )
        (work / "CHANGE.md").write_text(
            "# Change\n\n"
            "- Status: ready-for-implementation\n"
            "- Class: 1\n"
            "- DESIGN_DELTA.md required: no\n"
            "- Impact analysis accepted: yes\n"
            "- Ready for implementation: yes\n",
            encoding="utf-8",
        )
        (work / "IMPACT.md").write_text(
            "# Impact\n\n"
            "- Status: accepted\n"
            "- Impact analysis complete: yes\n"
            "- No relevant references remain unclassified: yes\n\n"
            "## Impact matrix\n\n"
            "| Layer or concern | Located artifact / current owner | Action | Required end state | Owning task | Verification evidence |\n"
            "|---|---|---|---|---|---|\n"
            "| UI | CustomerForm | modify | updated | T001 | test |\n",
            encoding="utf-8",
        )
        (work / "PLAN.md").write_text(
            "# Plan\n\n"
            f"- Cadence: {cadence}\n"
            "- Forced per-task review triggers present: none\n",
            encoding="utf-8",
        )
        (work / "tasks/T001.md").write_text(
            "# Task\n\n- Review batch: RB001\n", encoding="utf-8"
        )

    def test_incremental_discovery_allows_draft_change_without_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            work = root / ".ai/work/CHG-001"
            (root / ".ai/CURRENT_PLAN.md").write_text(
                "# Current work\n\n"
                "- Work type: incremental-change\n"
                "- Work directory: `.ai/work/CHG-001/`\n"
                "- Change request: `.ai/work/CHG-001/CHANGE.md`\n"
                "- Status: discovery\n",
                encoding="utf-8",
            )
            (work / "CHANGE.md").write_text(
                "# Change\n\n- Status: draft\n", encoding="utf-8"
            )
            result = self.run_check(root)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_incremental_change_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            self.write_valid_change(root)
            result = self.run_check(root)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("structurally valid", result.stdout)

    def test_unclassified_impact_row_fails_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            self.write_valid_change(root)
            impact = root / ".ai/work/CHG-001/IMPACT.md"
            impact.write_text(
                impact.read_text(encoding="utf-8").replace(
                    "| UI | CustomerForm | modify |",
                    "| UI | CustomerForm |  |",
                ),
                encoding="utf-8",
            )
            result = self.run_check(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("invalid or empty action", result.stdout)

    def test_design_class_two_requires_design_delta(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            self.write_valid_change(root)
            change = root / ".ai/work/CHG-001/CHANGE.md"
            change.write_text(
                change.read_text(encoding="utf-8")
                .replace("- Class: 1", "- Class: 2")
                .replace(
                    "- DESIGN_DELTA.md required: no",
                    "- DESIGN_DELTA.md required: yes",
                ),
                encoding="utf-8",
            )
            result = self.run_check(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("DESIGN_DELTA.md", result.stdout)

    def test_batch_size_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            self.write_valid_change(root)
            tasks = root / ".ai/work/CHG-001/tasks"
            for name in ("T002.md", "T003.md"):
                (tasks / name).write_text(
                    "# Task\n\n- Review batch: RB001\n", encoding="utf-8"
                )
            result = self.run_check(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("configured maximum is 2", result.stdout)

    def test_forced_trigger_requires_per_task_cadence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_repo(root)
            self.write_valid_change(root)
            plan = root / ".ai/work/CHG-001/PLAN.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "Forced per-task review triggers present: none",
                    "Forced per-task review triggers present: migration",
                ),
                encoding="utf-8",
            )
            result = self.run_check(root)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("forced per-task triggers", result.stdout)


class ConfiguredProjectVerificationTests(unittest.TestCase):
    def make_project(self, temporary: str, test_command: str = "true") -> Path:
        root = Path(temporary)
        shutil.copytree(AI_TOOLS, root / ".ai/tools")
        (root / ".ai/config").mkdir()
        config = (AI_ROOT / "project.yaml").read_text(encoding="utf-8")
        config = config.replace('name: "CHANGE_ME"', 'name: "configured-project"', 1)
        (root / ".ai/project.yaml").write_text(config, encoding="utf-8")
        for name in (
            "dependency-policy.conf",
            "dependency-allowlist.txt",
            "dependency-denylist.txt",
        ):
            shutil.copy2(AI_CONFIG / name, root / ".ai/config" / name)
        (root / ".ai/work").mkdir()
        (root / ".ai/CURRENT_PLAN.md").write_text(
            "# Current work\n\nNo active requirement.\n", encoding="utf-8"
        )
        (root / "README.md").write_text("# Configured project\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("# Project rules\n", encoding="utf-8")
        (root / ".ai/PROJECT_CONTEXT.md").write_text(
            "# Project context\n\n## Purpose\n\n"
            "- Product or service: configured test project\n"
            "- Primary users: template maintainers\n"
            "- Main outcome: verified project scaffolding\n",
            encoding="utf-8",
        )
        (root / ".ai/policies").mkdir()
        (root / ".ai/policies/QUALITY_GATES.md").write_text(
            "# Quality gates\n\n## Required project decisions\n\n"
            "- Minimum coverage policy: changed behavior is covered\n"
            "- Supported runtime matrix: CI runtime\n"
            "- Warning-as-error policy: enabled\n"
            "- Security severity threshold: high\n"
            "- Dependency update policy: reviewed updates\n"
            "- Flaky-test policy: quarantine is prohibited\n"
            "- CI required checks: verify\n",
            encoding="utf-8",
        )
        (root / ".ai/config/project.defaults.env").write_text(
            "SETUP_CMD='true'\nFORMAT_CHECK_CMD='true'\nFORMAT_APPLY_CMD='true'\nLINT_CMD='true'\n"
            f"TEST_CMD='{test_command}'\nSECURITY_CMD='true'\nDEPENDENCY_SCAN_CMD='true'\nBUILD_CMD='true'\n"
            "REQUIRE_SETUP=1\nREQUIRE_FORMAT_CHECK=1\nREQUIRE_LINT=1\nREQUIRE_TEST=1\nREQUIRE_SECURITY=1\n"
            "REQUIRE_DEPENDENCY_POLICY=1\nREQUIRE_DEPENDENCY_SCANNERS=1\nREQUIRE_BUILD=1\n",
            encoding="utf-8",
        )
        return root

    def test_all_configured_mandatory_gates_execute(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Project verification runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_project(temporary)
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/verify.sh")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertNotIn("SKIPPED", result.stdout)

    def test_missing_mandatory_test_command_fails_verification(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Project verification runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_project(temporary, test_command="")
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/verify.sh")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("tests: FAIL", result.stderr)

    def test_missing_mandatory_setup_command_fails_verification(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Project verification runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_project(temporary)
            defaults = root / ".ai/config/project.defaults.env"
            defaults.write_text(
                defaults.read_text(encoding="utf-8").replace(
                    "SETUP_CMD='true'", "SETUP_CMD=''"
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/verify.sh")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("setup: FAIL", result.stderr)

    def test_full_verification_ignores_local_command_override(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Project verification runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_project(temporary, test_command="false")
            (root / ".ai/config/project.env").write_text(
                "TEST_CMD='true'\n", encoding="utf-8"
            )
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/verify.sh")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("tests: FAIL", result.stderr)

    def test_incomplete_quality_decision_fails_documentation_gate(self) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Project verification runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_project(temporary)
            quality = root / ".ai/policies/QUALITY_GATES.md"
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "- Minimum coverage policy: changed behavior is covered",
                    "- Minimum coverage policy:",
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/verify.sh")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("quality decision field is incomplete", result.stdout)

    def test_incomplete_project_context_warns_without_failing_verification(
        self,
    ) -> None:
        if os.name == "nt" or not shutil.which("bash"):
            self.skipTest("Project verification runs on the Unix CI job")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.make_project(temporary)
            (root / ".ai/PROJECT_CONTEXT.md").write_text(
                "# Project context\n\n## Purpose\n\n"
                "- Product or service:\n"
                "- Primary users:\n"
                "- Main outcome:\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["bash", os.fspath(root / ".ai/tools/verify.sh")],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("WARN: project context field is incomplete", result.stdout)


if __name__ == "__main__":
    unittest.main()
