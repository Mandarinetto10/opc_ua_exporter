# GitHub Workflows

This directory contains GitHub Actions workflows for continuous integration and quality assurance.

## Workflows

### 🧪 Tests ([tests.yml](workflows/tests.yml))

**Trigger:** Push/PR to `main` or `develop`

Runs the full test suite across multiple platforms and Python versions:
- **Platforms:** Ubuntu, Windows, macOS
- **Python versions:** 3.10, 3.11, 3.12

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

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Shields.io Badge Documentation](https://shields.io/)
