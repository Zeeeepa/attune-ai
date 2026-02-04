"""Dependency Check Workflow

Audits dependencies for vulnerabilities, updates, and licensing issues.
Parses lockfiles and checks against known vulnerability patterns.

Stages:
1. inventory (CHEAP) - Parse requirements.txt, package.json, pyproject.toml, lockfiles
2. assess (CAPABLE) - Check for known vulnerabilities using pip-audit/npm audit
3. report (CAPABLE) - Generate risk assessment and recommendations

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import logging
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from .base import BaseWorkflow, ModelTier
from .step_config import WorkflowStepConfig

logger = logging.getLogger(__name__)

# Define step configurations for executor-based execution
DEPENDENCY_CHECK_STEPS = {
    "report": WorkflowStepConfig(
        name="report",
        task_type="analyze",  # Capable tier task
        tier_hint="capable",
        description="Generate dependency security report with remediation steps",
        max_tokens=3000,
    ),
}

# Cache directory for offline advisory data
CACHE_DIR = Path.home() / ".attune" / "advisory_cache"


def _get_cache_path() -> Path:
    """Get path to advisory cache file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / "pip_audit_cache.json"


def _load_cached_advisories() -> dict[str, list[dict]]:
    """Load cached advisories for offline mode.

    Returns:
        Dict mapping package names to list of vulnerability dicts.
    """
    cache_path = _get_cache_path()
    if not cache_path.exists():
        return {}

    try:
        age_days = (time.time() - cache_path.stat().st_mtime) / 86400
        if age_days > 7:
            logger.warning(f"Advisory cache is {age_days:.0f} days old - consider updating")

        return json.loads(cache_path.read_text())
    except Exception as e:
        logger.warning(f"Could not load advisory cache: {e}")
        return {}


def _save_advisory_cache(advisories: dict[str, list[dict]]) -> None:
    """Save advisories to cache for offline use."""
    try:
        cache_path = _get_cache_path()
        cache_path.write_text(json.dumps(advisories, indent=2))
        logger.info(f"Advisory cache updated: {len(advisories)} packages")
    except Exception as e:
        logger.warning(f"Could not save advisory cache: {e}")


def _run_pip_audit(target_path: Path) -> list[dict]:
    """Run pip-audit for real vulnerability data.

    Args:
        target_path: Directory containing requirements files

    Returns:
        List of vulnerability dicts from pip-audit
    """
    # Check for requirements file
    req_file = target_path / "requirements.txt"
    if not req_file.exists():
        # Try pyproject.toml
        pyproject = target_path / "pyproject.toml"
        if pyproject.exists():
            req_file = pyproject
        else:
            logger.info("No requirements.txt or pyproject.toml found for pip-audit")
            return []

    try:
        cmd = [
            "pip-audit",
            "--format=json",
            "--desc=on",
            "-r" if req_file.suffix == ".txt" else "--requirement",
            str(req_file),
        ]

        # For pyproject.toml, pip-audit needs different handling
        if req_file.suffix == ".toml":
            cmd = ["pip-audit", "--format=json", "--desc=on", "--local"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=target_path,
        )

        if result.stdout:
            data = json.loads(result.stdout)
            vulnerabilities = data.get("dependencies", [])

            # Update cache with results
            cache_update = {}
            for vuln in vulnerabilities:
                pkg_name = vuln.get("name", "").lower()
                if pkg_name and vuln.get("vulns"):
                    cache_update[pkg_name] = vuln.get("vulns", [])
            if cache_update:
                existing = _load_cached_advisories()
                existing.update(cache_update)
                _save_advisory_cache(existing)

            return vulnerabilities

    except FileNotFoundError:
        logger.warning(
            "pip-audit not installed. Install with: pip install pip-audit. "
            "Falling back to cached advisories."
        )
    except subprocess.TimeoutExpired:
        logger.warning("pip-audit timed out after 120s")
    except json.JSONDecodeError as e:
        logger.warning(f"pip-audit returned invalid JSON: {e}")
    except Exception as e:
        logger.warning(f"pip-audit failed: {e}")

    return []


def _run_npm_audit(target_path: Path) -> list[dict]:
    """Run npm audit for Node.js vulnerability data.

    Args:
        target_path: Directory containing package.json

    Returns:
        List of vulnerability dicts from npm audit
    """
    package_json = target_path / "package.json"
    if not package_json.exists():
        return []

    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=target_path,
        )

        # npm audit returns non-zero if vulnerabilities found
        if result.stdout:
            data = json.loads(result.stdout)
            vulnerabilities = []

            # Parse npm audit format
            for vuln_id, vuln_data in data.get("vulnerabilities", {}).items():
                vulnerabilities.append(
                    {
                        "name": vuln_data.get("name", vuln_id),
                        "severity": vuln_data.get("severity", "unknown"),
                        "via": vuln_data.get("via", []),
                        "range": vuln_data.get("range", ""),
                        "fixAvailable": vuln_data.get("fixAvailable", False),
                    }
                )

            return vulnerabilities

    except FileNotFoundError:
        logger.debug("npm not installed, skipping npm audit")
    except subprocess.TimeoutExpired:
        logger.warning("npm audit timed out")
    except Exception as e:
        logger.warning(f"npm audit failed: {e}")

    return []


class DependencyCheckWorkflow(BaseWorkflow):
    """Audit dependencies for security and updates.

    Scans dependency files to identify vulnerable, outdated,
    or potentially problematic packages.
    """

    name = "dependency-check"
    description = "Audit dependencies for vulnerabilities and updates"
    stages = ["inventory", "assess", "report"]
    tier_map = {
        "inventory": ModelTier.CHEAP,
        "assess": ModelTier.CAPABLE,
        "report": ModelTier.CAPABLE,
    }

    def __init__(self, **kwargs: Any):
        """Initialize dependency check workflow.

        Args:
            **kwargs: Additional arguments passed to BaseWorkflow

        """
        super().__init__(**kwargs)

    async def run_stage(
        self,
        stage_name: str,
        tier: ModelTier,
        input_data: Any,
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "inventory":
            return await self._inventory(input_data, tier)
        if stage_name == "assess":
            return await self._assess(input_data, tier)
        if stage_name == "report":
            return await self._report(input_data, tier)
        raise ValueError(f"Unknown stage: {stage_name}")

    async def _inventory(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Parse dependency files to build inventory.

        Supports requirements.txt, pyproject.toml, package.json,
        and their lockfiles.
        """
        target_path = input_data.get("path", ".")
        target = Path(target_path)

        dependencies: dict[str, list[dict]] = {
            "python": [],
            "node": [],
        }
        files_found: list[str] = []

        # Parse Python dependencies
        req_files = ["requirements.txt", "requirements-dev.txt", "requirements-test.txt"]
        for req_file in req_files:
            req_path = target / req_file
            if req_path.exists():
                files_found.append(str(req_path))
                deps = self._parse_requirements(req_path)
                dependencies["python"].extend(deps)

        # Parse pyproject.toml
        pyproject_path = target / "pyproject.toml"
        if pyproject_path.exists():
            files_found.append(str(pyproject_path))
            deps = self._parse_pyproject(pyproject_path)
            dependencies["python"].extend(deps)

        # Parse package.json
        package_json = target / "package.json"
        if package_json.exists():
            files_found.append(str(package_json))
            deps = self._parse_package_json(package_json)
            dependencies["node"].extend(deps)

        # Parse lockfiles for exact versions (more reliable for vuln checking)
        poetry_lock = target / "poetry.lock"
        if poetry_lock.exists():
            files_found.append(str(poetry_lock))
            lockfile_deps = self._parse_poetry_lock(poetry_lock)
            # Lockfile deps have pinned=True and override manifest versions
            dependencies["python"].extend(lockfile_deps)

        package_lock = target / "package-lock.json"
        if package_lock.exists():
            files_found.append(str(package_lock))
            lockfile_deps = self._parse_package_lock_json(package_lock)
            dependencies["node"].extend(lockfile_deps)

        # Deduplicate
        for ecosystem in dependencies:
            seen = set()
            unique = []
            for dep in dependencies[ecosystem]:
                name = dep["name"].lower()
                if name not in seen:
                    seen.add(name)
                    unique.append(dep)
            dependencies[ecosystem] = unique

        total_count = sum(len(deps) for deps in dependencies.values())

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(dependencies)) // 4

        return (
            {
                "dependencies": dependencies,
                "files_found": files_found,
                "total_dependencies": total_count,
                "python_count": len(dependencies["python"]),
                "node_count": len(dependencies["node"]),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _parse_requirements(self, path: Path) -> list[dict]:
        """Parse requirements.txt format using packaging library.

        Properly handles:
        - Version specifiers (>=, ==, ~=, etc.)
        - Extras ([dev], [test], etc.)
        - Environment markers (; python_version >= "3.8")
        - Comments and blank lines
        """
        deps = []
        try:
            from packaging.requirements import Requirement
        except ImportError:
            logger.warning("packaging library not installed, using fallback parser")
            return self._parse_requirements_fallback(path)

        try:
            content = path.read_text()
            for line in content.splitlines():
                line = line.strip()

                # Skip empty lines, comments, and options
                if not line or line.startswith("#") or line.startswith("-"):
                    continue

                # Skip URLs and local paths
                if line.startswith("http://") or line.startswith("https://"):
                    continue
                if line.startswith(".") or line.startswith("/"):
                    continue

                try:
                    req = Requirement(line)
                    deps.append(
                        {
                            "name": req.name,
                            "version": str(req.specifier) if req.specifier else "any",
                            "extras": list(req.extras) if req.extras else [],
                            "source": str(path),
                            "ecosystem": "python",
                        },
                    )
                except Exception as e:
                    logger.debug(f"Skipping unparseable requirement '{line}': {e}")

        except OSError as e:
            logger.warning(f"Cannot read {path}: {e}")

        return deps

    def _parse_requirements_fallback(self, path: Path) -> list[dict]:
        """Fallback parser if packaging library not available."""
        deps = []
        try:
            content = path.read_text()
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue

                # Basic regex parsing
                match = re.match(r"^([a-zA-Z0-9_-]+)\s*([<>=!~]+\s*[\d.]+)?", line)
                if match:
                    name = match.group(1)
                    version = match.group(2).strip() if match.group(2) else "any"
                    deps.append(
                        {
                            "name": name,
                            "version": version,
                            "source": str(path),
                            "ecosystem": "python",
                        },
                    )
        except OSError:
            pass
        return deps

    def _parse_pyproject(self, path: Path) -> list[dict]:
        """Parse pyproject.toml for dependencies using tomllib.

        Supports:
        - PEP 621 [project.dependencies]
        - Poetry [tool.poetry.dependencies]
        - Optional dependencies
        """
        deps = []

        # Try tomllib (Python 3.11+) or tomli as fallback
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                logger.warning("tomllib/tomli not available, using fallback parser")
                return self._parse_pyproject_fallback(path)

        try:
            from packaging.requirements import Requirement
        except ImportError:
            Requirement = None  # type: ignore

        try:
            with path.open("rb") as f:
                data = tomllib.load(f)

            # PEP 621: [project.dependencies]
            for dep_str in data.get("project", {}).get("dependencies", []):
                if Requirement:
                    try:
                        req = Requirement(dep_str)
                        deps.append(
                            {
                                "name": req.name,
                                "version": str(req.specifier) if req.specifier else "any",
                                "source": str(path),
                                "ecosystem": "python",
                            },
                        )
                    except Exception as e:
                        logger.debug(f"Skipping unparseable dependency '{dep_str}': {e}")
                else:
                    # Basic extraction without packaging
                    match = re.match(r"^([a-zA-Z0-9_-]+)", dep_str)
                    if match:
                        deps.append(
                            {
                                "name": match.group(1),
                                "version": "any",
                                "source": str(path),
                                "ecosystem": "python",
                            },
                        )

            # Poetry: [tool.poetry.dependencies]
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for name, spec in poetry_deps.items():
                if name == "python":
                    continue  # Skip Python version constraint

                if isinstance(spec, str):
                    version = spec
                elif isinstance(spec, dict):
                    version = spec.get("version", "any")
                else:
                    version = "any"

                deps.append(
                    {
                        "name": name,
                        "version": version,
                        "source": str(path),
                        "ecosystem": "python",
                    },
                )

            # Poetry dev dependencies
            poetry_dev = data.get("tool", {}).get("poetry", {}).get("dev-dependencies", {})
            for name, spec in poetry_dev.items():
                version = spec if isinstance(spec, str) else spec.get("version", "any")
                deps.append(
                    {
                        "name": name,
                        "version": version,
                        "source": str(path),
                        "ecosystem": "python",
                        "dev": True,
                    },
                )

        except Exception as e:
            logger.warning(f"Cannot parse {path}: {e}")

        return deps

    def _parse_pyproject_fallback(self, path: Path) -> list[dict]:
        """Fallback parser if tomllib not available."""
        deps = []
        try:
            content = path.read_text()
            in_deps = False
            for line in content.splitlines():
                if "dependencies" in line and "=" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith("]"):
                        in_deps = False
                        continue
                    match = re.search(r'"([a-zA-Z0-9_-]+)([<>=!~]+[\d.]+)?"', line)
                    if match:
                        name = match.group(1)
                        version = match.group(2) if match.group(2) else "any"
                        deps.append(
                            {
                                "name": name,
                                "version": version,
                                "source": str(path),
                                "ecosystem": "python",
                            },
                        )
        except OSError:
            pass
        return deps

    def _parse_package_json(self, path: Path) -> list[dict]:
        """Parse package.json for dependencies."""
        deps = []
        try:
            with open(path) as f:
                data = json.load(f)

            for dep_type in ["dependencies", "devDependencies"]:
                for name, version in data.get(dep_type, {}).items():
                    deps.append(
                        {
                            "name": name,
                            "version": version,
                            "source": str(path),
                            "ecosystem": "node",
                            "dev": dep_type == "devDependencies",
                        },
                    )
        except (OSError, json.JSONDecodeError):
            pass
        return deps

    def _parse_poetry_lock(self, path: Path) -> list[dict]:
        """Parse poetry.lock for pinned dependency versions.

        Lockfiles provide exact versions for reproducible vulnerability findings.
        """
        deps = []

        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                logger.debug("tomllib/tomli not available for poetry.lock parsing")
                return deps

        try:
            with path.open("rb") as f:
                data = tomllib.load(f)

            for pkg in data.get("package", []):
                deps.append(
                    {
                        "name": pkg.get("name", ""),
                        "version": f"=={pkg.get('version', '')}",  # Pinned version
                        "source": str(path),
                        "ecosystem": "python",
                        "pinned": True,
                    },
                )

        except Exception as e:
            logger.warning(f"Cannot parse poetry.lock: {e}")

        return deps

    def _parse_package_lock_json(self, path: Path) -> list[dict]:
        """Parse package-lock.json for pinned Node.js versions."""
        deps = []
        try:
            with open(path) as f:
                data = json.load(f)

            # npm v7+ format (packages)
            packages = data.get("packages", {})
            for pkg_path, pkg_data in packages.items():
                if not pkg_path or pkg_path == "":  # Root package
                    continue

                name = pkg_path.replace("node_modules/", "").split("/")[-1]
                version = pkg_data.get("version", "")
                if name and version:
                    deps.append(
                        {
                            "name": name,
                            "version": f"=={version}",
                            "source": str(path),
                            "ecosystem": "node",
                            "pinned": True,
                        },
                    )

            # npm v6 format (dependencies)
            if not packages:
                for name, pkg_data in data.get("dependencies", {}).items():
                    version = pkg_data.get("version", "")
                    deps.append(
                        {
                            "name": name,
                            "version": f"=={version}",
                            "source": str(path),
                            "ecosystem": "node",
                            "pinned": True,
                        },
                    )

        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Cannot parse package-lock.json: {e}")

        return deps

    async def _assess(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Check dependencies for vulnerabilities using real advisory sources.

        Uses pip-audit for Python and npm audit for Node.js packages.
        Falls back to cached advisories if tools are unavailable.
        """
        target_path = Path(input_data.get("path", "."))
        dependencies = input_data.get("dependencies", {})

        vulnerabilities: list[dict] = []
        outdated: list[dict] = []
        data_source = "none"

        # Run pip-audit for Python vulnerabilities
        pip_audit_results = _run_pip_audit(target_path)
        if pip_audit_results:
            data_source = "pip-audit"
            for result in pip_audit_results:
                for vuln in result.get("vulns", []):
                    vulnerabilities.append(
                        {
                            "package": result.get("name", "unknown"),
                            "current_version": result.get("version", "unknown"),
                            "fixed_versions": vuln.get("fix_versions", []),
                            "severity": self._map_severity(vuln.get("id", "")),
                            "cve": vuln.get("id", ""),
                            "description": vuln.get("description", "")[:200],
                            "ecosystem": "python",
                            "source": "pip-audit",
                        },
                    )

        # Run npm audit for Node.js vulnerabilities
        npm_audit_results = _run_npm_audit(target_path)
        if npm_audit_results:
            data_source = "pip-audit+npm" if data_source == "pip-audit" else "npm-audit"
            for vuln in npm_audit_results:
                severity = vuln.get("severity", "unknown")
                vulnerabilities.append(
                    {
                        "package": vuln.get("name", "unknown"),
                        "current_version": vuln.get("range", "unknown"),
                        "fixed_versions": [],
                        "severity": severity,
                        "cve": "",
                        "description": str(vuln.get("via", []))[:200],
                        "ecosystem": "node",
                        "source": "npm-audit",
                        "fixAvailable": vuln.get("fixAvailable", False),
                    },
                )

        # If no real audit data, try cached advisories
        if not vulnerabilities:
            cached = _load_cached_advisories()
            if cached:
                data_source = "cached"
                for ecosystem, deps in dependencies.items():
                    for dep in deps:
                        name_lower = dep["name"].lower()
                        if name_lower in cached:
                            for vuln in cached[name_lower]:
                                vulnerabilities.append(
                                    {
                                        "package": dep["name"],
                                        "current_version": dep["version"],
                                        "severity": self._map_severity(vuln.get("id", "")),
                                        "cve": vuln.get("id", ""),
                                        "ecosystem": ecosystem,
                                        "source": "cached",
                                    },
                                )

        # Check for potentially outdated packages (heuristic)
        for ecosystem, deps in dependencies.items():
            for dep in deps:
                version = dep.get("version", "")
                # Flag pre-release and very old-looking versions
                if version.startswith("^0.") or version.startswith("~0."):
                    outdated.append(
                        {
                            "package": dep["name"],
                            "current_version": version,
                            "status": "potentially_outdated",
                            "ecosystem": ecosystem,
                        },
                    )

        # Categorize by severity
        critical = [v for v in vulnerabilities if v.get("severity") == "critical"]
        high = [v for v in vulnerabilities if v.get("severity") == "high"]
        medium = [v for v in vulnerabilities if v.get("severity") == "medium"]
        low = [v for v in vulnerabilities if v.get("severity") == "low"]

        assessment = {
            "vulnerabilities": vulnerabilities,
            "outdated": outdated,
            "vulnerability_count": len(vulnerabilities),
            "critical_count": len(critical),
            "high_count": len(high),
            "medium_count": len(medium),
            "low_count": len(low),
            "outdated_count": len(outdated),
            "data_source": data_source,
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(assessment)) // 4

        return (
            {
                "assessment": assessment,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _map_severity(self, vuln_id: str) -> str:
        """Map vulnerability ID to severity level.

        Uses heuristics based on CVE/GHSA patterns.
        """
        vuln_id_lower = vuln_id.lower()

        # GHSA typically includes severity in metadata, but we can't get it from ID alone
        # CVEs don't encode severity in the ID
        # Default to "medium" as a conservative estimate
        # In practice, pip-audit provides severity in the response

        if "critical" in vuln_id_lower:
            return "critical"
        if "high" in vuln_id_lower:
            return "high"

        # Default to medium - actual severity should come from the audit tool
        return "medium"

    async def _report(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Generate risk assessment and recommendations using LLM.

        Creates actionable report with remediation steps.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        assessment = input_data.get("assessment", {})
        vulnerabilities = assessment.get("vulnerabilities", [])
        outdated = assessment.get("outdated", [])
        target = input_data.get("path", "")

        # Calculate risk score
        risk_score = (
            assessment.get("critical_count", 0) * 25
            + assessment.get("high_count", 0) * 10
            + assessment.get("medium_count", 0) * 3
            + assessment.get("outdated_count", 0) * 1
        )
        risk_score = min(100, risk_score)

        risk_level = (
            "critical"
            if risk_score >= 75
            else "high" if risk_score >= 50 else "medium" if risk_score >= 25 else "low"
        )

        # Build vulnerability summary for LLM
        vuln_summary = []
        for v in vulnerabilities[:15]:
            vuln_summary.append(
                f"- {v.get('package')}@{v.get('current_version')}: "
                f"{v.get('cve')} ({v.get('severity')})",
            )

        # Build input payload for prompt
        input_payload = f"""Target: {target or "codebase"}

Total Dependencies: {input_data.get("total_dependencies", 0)}
Risk Score: {risk_score}/100
Risk Level: {risk_level}

Vulnerabilities ({len(vulnerabilities)}):
{chr(10).join(vuln_summary) if vuln_summary else "None found"}

Outdated Packages: {len(outdated)}

Severity Summary:
- Critical: {assessment.get("critical_count", 0)}
- High: {assessment.get("high_count", 0)}
- Medium: {assessment.get("medium_count", 0)}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt
            user_message = self._render_xml_prompt(
                role="security engineer specializing in dependency management",
                goal="Generate a comprehensive dependency security report with remediation steps",
                instructions=[
                    "Analyze the vulnerability findings and their severity",
                    "Prioritize remediation actions by risk level",
                    "Provide specific upgrade recommendations",
                    "Identify potential breaking changes from upgrades",
                    "Suggest a remediation timeline",
                ],
                constraints=[
                    "Focus on actionable recommendations",
                    "Prioritize critical and high severity issues",
                    "Include version upgrade targets where possible",
                ],
                input_type="dependency_vulnerabilities",
                input_payload=input_payload,
                extra={
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                },
            )
            system = None  # XML prompt includes all context
        else:
            # Use legacy plain text prompts
            system = """You are a security engineer specializing in dependency management.
Analyze the vulnerability findings and generate a comprehensive remediation report.

Focus on:
1. Prioritizing by severity
2. Specific upgrade recommendations
3. Potential breaking changes
4. Remediation timeline"""

            user_message = f"""Generate a dependency security report:

{input_payload}

Provide actionable remediation recommendations."""

        # Try executor-based execution first (Phase 3 pattern)
        if self._executor is not None or self._api_key:
            try:
                step = DEPENDENCY_CHECK_STEPS["report"]
                response, input_tokens, output_tokens, cost = await self.run_step_with_executor(
                    step=step,
                    prompt=user_message,
                    system=system,
                )
            except Exception:
                # Fall back to legacy _call_llm if executor fails
                response, input_tokens, output_tokens = await self._call_llm(
                    tier,
                    system or "",
                    user_message,
                    max_tokens=3000,
                )
        else:
            # Legacy path for backward compatibility
            response, input_tokens, output_tokens = await self._call_llm(
                tier,
                system or "",
                user_message,
                max_tokens=3000,
            )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        # Generate basic recommendations for backwards compatibility
        recommendations: list[dict] = []

        for vuln in vulnerabilities:
            recommendations.append(
                {
                    "priority": 1 if vuln["severity"] == "critical" else 2,
                    "action": "upgrade",
                    "package": vuln["package"],
                    "reason": f"Fix {vuln['cve']} ({vuln['severity']} severity)",
                    "suggestion": f"Upgrade {vuln['package']} to latest version",
                },
            )

        for dep in outdated[:10]:  # Top 10 outdated
            recommendations.append(
                {
                    "priority": 3,
                    "action": "review",
                    "package": dep["package"],
                    "reason": "Potentially outdated version",
                    "suggestion": f"Review and update {dep['package']}",
                },
            )

        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])

        result = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "total_dependencies": input_data.get("total_dependencies", 0),
            "vulnerability_count": len(vulnerabilities),
            "outdated_count": len(outdated),
            "recommendations": recommendations[:20],
            "security_report": response,
            "summary": {
                "critical": assessment.get("critical_count", 0),
                "high": assessment.get("high_count", 0),
                "medium": assessment.get("medium_count", 0),
            },
            "model_tier_used": tier.value,
        }

        # Merge parsed XML data if available
        if parsed_data.get("xml_parsed"):
            result.update(
                {
                    "xml_parsed": True,
                    "report_summary": parsed_data.get("summary"),
                    "findings": parsed_data.get("findings", []),
                    "checklist": parsed_data.get("checklist", []),
                },
            )

        # Add formatted report for human readability
        result["formatted_report"] = format_dependency_check_report(result, input_data)

        return (result, input_tokens, output_tokens)


def format_dependency_check_report(result: dict, input_data: dict) -> str:
    """Format dependency check output as a human-readable report.

    Args:
        result: The report stage result
        input_data: Input data from previous stages

    Returns:
        Formatted report string

    """
    lines = []

    # Header with risk level
    risk_score = result.get("risk_score", 0)

    if risk_score >= 75:
        risk_icon = "🔴"
        risk_text = "CRITICAL"
    elif risk_score >= 50:
        risk_icon = "🟠"
        risk_text = "HIGH RISK"
    elif risk_score >= 25:
        risk_icon = "🟡"
        risk_text = "MEDIUM RISK"
    else:
        risk_icon = "🟢"
        risk_text = "LOW RISK"

    lines.append("=" * 60)
    lines.append("DEPENDENCY SECURITY REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Risk Level: {risk_icon} {risk_text}")
    lines.append(f"Risk Score: {risk_score}/100")
    lines.append("")

    # Inventory summary
    total_deps = result.get("total_dependencies", 0)
    python_count = input_data.get("python_count", 0)
    node_count = input_data.get("node_count", 0)
    files_found = input_data.get("files_found", [])

    lines.append("-" * 60)
    lines.append("DEPENDENCY INVENTORY")
    lines.append("-" * 60)
    lines.append(f"Total Dependencies: {total_deps}")
    if python_count:
        lines.append(f"  Python: {python_count}")
    if node_count:
        lines.append(f"  Node.js: {node_count}")
    if files_found:
        lines.append(f"Files Scanned: {len(files_found)}")
        for f in files_found[:5]:
            lines.append(f"  • {f}")
    lines.append("")

    # Vulnerability summary
    summary = result.get("summary", {})
    vuln_count = result.get("vulnerability_count", 0)
    outdated_count = result.get("outdated_count", 0)

    lines.append("-" * 60)
    lines.append("SECURITY FINDINGS")
    lines.append("-" * 60)
    lines.append(f"Vulnerabilities: {vuln_count}")
    lines.append(f"  🔴 Critical: {summary.get('critical', 0)}")
    lines.append(f"  🟠 High: {summary.get('high', 0)}")
    lines.append(f"  🟡 Medium: {summary.get('medium', 0)}")
    lines.append(f"Outdated Packages: {outdated_count}")
    lines.append("")

    # Vulnerabilities detail
    assessment = input_data.get("assessment", {})
    vulnerabilities = assessment.get("vulnerabilities", [])
    if vulnerabilities:
        lines.append("-" * 60)
        lines.append("VULNERABLE PACKAGES")
        lines.append("-" * 60)
        for vuln in vulnerabilities[:10]:
            severity = vuln.get("severity", "unknown").upper()
            pkg = vuln.get("package", "unknown")
            version = vuln.get("current_version", "?")
            cve = vuln.get("cve", "N/A")
            sev_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(severity, "⚪")
            lines.append(f"  {sev_icon} {pkg}@{version}")
            lines.append(f"      CVE: {cve} | Severity: {severity}")
        if len(vulnerabilities) > 10:
            lines.append(f"  ... and {len(vulnerabilities) - 10} more")
        lines.append("")

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("-" * 60)
        lines.append("REMEDIATION ACTIONS")
        lines.append("-" * 60)
        priority_labels = {1: "🔴 URGENT", 2: "🟠 HIGH", 3: "🟡 REVIEW"}
        for rec in recommendations[:10]:
            priority = rec.get("priority", 3)
            pkg = rec.get("package", "unknown")
            suggestion = rec.get("suggestion", "")
            label = priority_labels.get(priority, "⚪ LOW")
            lines.append(f"  {label}: {pkg}")
            lines.append(f"      {suggestion}")
        lines.append("")

    # Security report from LLM (if available)
    security_report = result.get("security_report", "")
    if security_report and not security_report.startswith("[Simulated"):
        lines.append("-" * 60)
        lines.append("DETAILED ANALYSIS")
        lines.append("-" * 60)
        # Truncate if very long
        if len(security_report) > 1500:
            lines.append(security_report[:1500] + "...")
        else:
            lines.append(security_report)
        lines.append("")

    # Footer
    lines.append("=" * 60)
    model_tier = result.get("model_tier_used", "unknown")
    lines.append(f"Scanned {total_deps} dependencies using {model_tier} tier model")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """CLI entry point for dependency check workflow."""
    import asyncio

    async def run():
        workflow = DependencyCheckWorkflow()
        result = await workflow.execute(path=".")

        print("\nDependency Check Results")
        print("=" * 50)
        print(f"Provider: {result.provider}")
        print(f"Success: {result.success}")

        report = result.final_output.get("report", {})
        print(f"Risk Level: {report.get('risk_level', 'N/A')}")
        print(f"Risk Score: {report.get('risk_score', 0)}/100")
        print(f"Total Dependencies: {report.get('total_dependencies', 0)}")
        print(f"Vulnerabilities: {report.get('vulnerability_count', 0)}")
        print(f"Outdated: {report.get('outdated_count', 0)}")

        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        savings = result.cost_report.savings
        pct = result.cost_report.savings_percent
        print(f"  Savings: ${savings:.4f} ({pct:.1f}%)")

    asyncio.run(run())


if __name__ == "__main__":
    main()
