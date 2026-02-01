#!/bin/bash
# rename_to_attune.sh
# Automated rename script for empathy-framework → attune-ai
#
# Usage:
#   cd /path/to/empathy-framework
#   chmod +x rename_to_attune.sh
#   ./rename_to_attune.sh
#
# IMPORTANT: Run on a feature branch, not main!
#   git checkout -b feature/rename-to-attune

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Empathy Framework → Attune-AI Migration Script            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Safety check
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}ERROR: pyproject.toml not found. Run from repo root.${NC}"
    exit 1
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "main" ]; then
    echo -e "${RED}ERROR: Don't run on main branch!${NC}"
    echo -e "Create a feature branch first:"
    echo -e "  git checkout -b feature/rename-to-attune"
    exit 1
fi

echo -e "${YELLOW}Current branch: $BRANCH${NC}"
echo -e "${YELLOW}Starting migration in 3 seconds... (Ctrl+C to cancel)${NC}"
sleep 3

# ============================================================================
# PHASE 1: Directory Renames
# ============================================================================
echo ""
echo -e "${GREEN}=== Phase 1: Directory Renames ===${NC}"

rename_dir() {
    if [ -d "$1" ]; then
        echo -e "  Moving: $1 → $2"
        mv "$1" "$2"
    else
        echo -e "  ${YELLOW}Skipped: $1 (not found)${NC}"
    fi
}

# Main module
rename_dir "src/empathy_os" "src/attune"

# Toolkit
rename_dir "empathy_llm_toolkit" "attune_llm"

# Plugins
rename_dir "empathy_healthcare_plugin" "attune_healthcare"
rename_dir "empathy_software_plugin" "attune_software"

# Config directory
rename_dir ".empathy" ".attune"

# ============================================================================
# PHASE 2: Python Import Updates
# ============================================================================
echo ""
echo -e "${GREEN}=== Phase 2: Python Import Updates ===${NC}"

# Detect OS for sed compatibility (macOS vs Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_INPLACE="sed -i ''"
else
    SED_INPLACE="sed -i"
fi

echo "  Updating Python imports..."

find . -name "*.py" -type f ! -path "./.git/*" ! -path "./venv/*" ! -path "./.venv/*" -print0 | while IFS= read -r -d '' file; do
    # Core module imports
    $SED_INPLACE \
        -e 's/from empathy_os/from attune/g' \
        -e 's/import empathy_os/import attune/g' \
        -e 's/empathy_os\./attune./g' \
        "$file" 2>/dev/null || true

    # LLM toolkit imports
    $SED_INPLACE \
        -e 's/from empathy_llm_toolkit/from attune_llm/g' \
        -e 's/import empathy_llm_toolkit/import attune_llm/g' \
        -e 's/empathy_llm_toolkit\./attune_llm./g' \
        "$file" 2>/dev/null || true

    # Plugin imports
    $SED_INPLACE \
        -e 's/from empathy_healthcare_plugin/from attune_healthcare/g' \
        -e 's/from empathy_software_plugin/from attune_software/g' \
        "$file" 2>/dev/null || true

    # Config references
    $SED_INPLACE \
        -e 's/empathy\.config/attune.config/g' \
        -e 's/\.empathy\//.attune\//g' \
        -e 's/"empathy_os"/"attune"/g' \
        -e "s/'empathy_os'/'attune'/g" \
        "$file" 2>/dev/null || true
done

# ============================================================================
# PHASE 3: Config File Updates
# ============================================================================
echo ""
echo -e "${GREEN}=== Phase 3: Config File Updates ===${NC}"

echo "  Updating YAML/JSON configs..."

find . \( -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.toml" \) \
    -type f ! -path "./.git/*" ! -path "./venv/*" -print0 | while IFS= read -r -d '' file; do
    $SED_INPLACE \
        -e 's/empathy_os/attune/g' \
        -e 's/empathy-framework/attune-ai/g' \
        -e 's/empathy\.config/attune.config/g' \
        -e 's/empathy_llm_toolkit/attune_llm/g' \
        -e 's/empathy_healthcare_plugin/attune_healthcare/g' \
        -e 's/empathy_software_plugin/attune_software/g' \
        "$file" 2>/dev/null || true
done

# ============================================================================
# PHASE 4: Documentation Updates
# ============================================================================
echo ""
echo -e "${GREEN}=== Phase 4: Documentation Updates ===${NC}"

echo "  Updating Markdown docs..."

find . -name "*.md" -type f ! -path "./.git/*" -print0 | while IFS= read -r -d '' file; do
    $SED_INPLACE \
        -e 's/empathy-framework/attune-ai/g' \
        -e 's/empathy_os/attune/g' \
        -e 's/empathy_llm_toolkit/attune_llm/g' \
        -e 's/pip install empathy-framework/pip install attune-ai/g' \
        -e 's/from empathy_os/from attune/g' \
        -e 's/import empathy_os/import attune/g' \
        "$file" 2>/dev/null || true
done

# ============================================================================
# PHASE 5: Rename Config Files
# ============================================================================
echo ""
echo -e "${GREEN}=== Phase 5: Rename Config Files ===${NC}"

rename_file() {
    if [ -f "$1" ]; then
        echo -e "  Renaming: $1 → $2"
        mv "$1" "$2"
    fi
}

rename_file "empathy.config.example.json" "attune.config.example.json"
rename_file "empathy.config.example.yml" "attune.config.example.yml"
rename_file "empathy.config.json" "attune.config.json"
rename_file "empathy.config.yml" "attune.config.yml"

# ============================================================================
# PHASE 6: Update pyproject.toml
# ============================================================================
echo ""
echo -e "${GREEN}=== Phase 6: Update pyproject.toml ===${NC}"

if [ -f "pyproject.toml" ]; then
    echo "  Updating package name and scripts..."

    # Package name
    $SED_INPLACE 's/name = "empathy-framework"/name = "attune-ai"/g' pyproject.toml

    # Version bump (major version for rename)
    # This is a simple bump - you may want to do this manually
    $SED_INPLACE 's/version = "1\./version = "2.0./g' pyproject.toml

    # Scripts/entry points
    $SED_INPLACE \
        -e 's/empathy-scan/attune-scan/g' \
        -e 's/empathy = "/attune = "/g' \
        -e 's/empathy_os\./attune./g' \
        pyproject.toml

    # Package discovery
    $SED_INPLACE 's/include = \["empathy_os\*"\]/include = ["attune*"]/g' pyproject.toml

    # URLs
    $SED_INPLACE 's/Smart-AI-Memory\/empathy-framework/Smart-AI-Memory\/attune-ai/g' pyproject.toml
fi

# ============================================================================
# PHASE 7: Update CI/CD
# ============================================================================
echo ""
echo -e "${GREEN}=== Phase 7: Update CI/CD Workflows ===${NC}"

if [ -d ".github/workflows" ]; then
    find .github/workflows -name "*.yml" -o -name "*.yaml" | while read file; do
        echo "  Updating: $file"
        $SED_INPLACE \
            -e 's/empathy-framework/attune-ai/g' \
            -e 's/empathy_os/attune/g' \
            "$file" 2>/dev/null || true
    done
fi

# ============================================================================
# PHASE 8: Cleanup and Report
# ============================================================================
echo ""
echo -e "${GREEN}=== Phase 8: Cleanup ===${NC}"

# Remove sed backup files (macOS creates these)
find . -name "*''" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Migration Complete!                                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Review changes:  ${YELLOW}git diff${NC}"
echo -e "  2. Check for missed references:"
echo -e "     ${YELLOW}grep -r 'empathy_os' --include='*.py' .${NC}"
echo -e "     ${YELLOW}grep -r 'empathy-framework' --include='*.md' .${NC}"
echo -e "  3. Run tests:       ${YELLOW}pytest${NC}"
echo -e "  4. Commit:          ${YELLOW}git add -A && git commit -m 'feat: rename empathy-framework to attune-ai'${NC}"
echo -e "  5. Update pyproject.toml version manually if needed"
echo ""
echo -e "${YELLOW}Manual updates still needed:${NC}"
echo -e "  - README.md hero section / badges"
echo -e "  - CHANGELOG.md (add 2.0.0 entry)"
echo -e "  - Any hardcoded URLs"
echo -e "  - GitHub repository rename (Settings → General)"
echo -e "  - PyPI publish (build + twine upload)"
