# GitHub Workflows

This directory contains GitHub Actions workflows for continuous integration and quality assurance.

## Workflows

### 🧪 Tests ([tests.yml](workflows/tests.yml))

**Trigger:** Push/PR to `main` or `develop`

Runs the full test suite across multiple platforms and Python versions:
- **Platforms:** Ubuntu, Windows, macOS
- **Python versions:** 3.10, 3.11, 3.12
- **Coverage:** Uploads to [Codecov](https://codecov.io/gh/Mandarinetto10/opc_ua_exporter)

**Badge:** ![Tests](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml/badge.svg?branch=main)

### 🎨 Code Quality ([code-quality.yml](workflows/code-quality.yml))

**Trigger:** Push/PR to `main` or `develop`

Enforces code style and quality standards:
- **Ruff linter:** Fast Python linter
- **Ruff formatter:** Code formatting check
- **Black formatter:** Additional formatting verification

**Badge:** ![Code Quality](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/code-quality.yml/badge.svg?branch=main)

### 🔍 Type Check ([type-check.yml](workflows/type-check.yml))

**Trigger:** Push/PR to `main` or `develop`

Static type checking with MyPy:
- **Python versions:** 3.10, 3.11, 3.12
- **Strict mode:** Optional strict type checking (non-blocking)

**Badge:** ![Type Check](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/type-check.yml/badge.svg?branch=main)

### 📚 Documentation ([docs.yml](workflows/docs.yml))

**Trigger:** Push/PR to `main` or `develop`

Validates documentation completeness:
- Checks for required documentation files (README, SETUP, LICENSE, CHANGELOG)
- Validates Python docstrings
- Verifies docs directory structure
- Checks README badges

**Badge:** ![Documentation](https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/docs.yml/badge.svg?branch=main)

## Badges

All workflow badges are displayed in the [main README](../README.md) header using HTML for better formatting:

```html
<p align="center">
  <a href="https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml">
    <img src="https://github.com/Mandarinetto10/opc_ua_exporter/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests" />
  </a>
  <!-- More badges... -->
</p>
```

### Coverage Badge

The coverage badge is provided by [Codecov](https://codecov.io):

```html
<a href="https://codecov.io/gh/Mandarinetto10/opc_ua_exporter">
  <img src="https://codecov.io/gh/Mandarinetto10/opc_ua_exporter/branch/main/graph/badge.svg" alt="Coverage" />
</a>
```

Configuration is in [`.codecov.yml`](../.codecov.yml).

## Local Testing

Run these commands before pushing to catch issues early:

```bash
# Run tests with coverage
pytest -v --cov=src/opc_browser --cov-report=term-missing

# Check code quality
ruff check src/ tests/
ruff format --check src/ tests/
black --check src/ tests/

# Type checking
mypy src/
```

## Secrets

The following secrets are configured in the repository:

- `CODECOV_TOKEN` (optional for public repos): Upload token for Codecov

## Permissions

All workflows use minimal permissions following the principle of least privilege:
- `contents: read` - Read repository content
- `pull-requests: read` - Read PR information

## Best Practices

1. **Workflow naming**: Use descriptive names matching the badge text
2. **Branch filtering**: Only run on `main` and `develop` branches
3. **Matrix testing**: Test across multiple OS and Python versions
4. **Job summaries**: Generate GitHub Step Summaries for better visibility
5. **Fail-fast**: Disabled for test matrix to see all failures
6. **Badge format**: Use `?branch=main` parameter for branch-specific badges
7. **Coverage precision**: Set to 2 decimal places in `.codecov.yml`

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.com/)
- [Shields.io Badge Documentation](https://shields.io/)
