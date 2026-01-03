# CI/CD Pipeline Documentation

## 📋 Overview

This document describes the CI/CD (Continuous Integration / Continuous Deployment) pipeline for the Orders API service.

## 🚀 Pipeline Triggers

The CI/CD pipeline automatically triggers on:

- **Push** to branches:
  - `main` (production)
  - `develop` (development)
  - `feature/**` (feature branches)
  - `release/**` (release branches)

- **Pull Requests** to:
  - `main`
  - `develop`
  - `feature/**`
  - `release/**`

## 🔄 Pipeline Stages

The pipeline consists of 6 main stages that run in sequence with dependencies:

### 1. 🔍 Lint - Code Quality Check

**Purpose**: Analyze code syntax and style to identify errors and risky practices.

**Tools Used**:
- **flake8**: Python syntax and style checker
- **black**: Code formatter (check mode)
- **isort**: Import statement sorter
- **mypy**: Static type checker
- **bandit**: Security-focused static analyzer

**What it checks**:
- Python syntax errors
- Undefined variables
- Code style violations
- Import organization
- Type hints
- Security vulnerabilities in code

**Failure Criteria**:
- Syntax errors (E9, F63, F7, F82)
- Code complexity > 10
- Line length > 120 characters
- Unformatted code (black)
- Unsorted imports (isort)

**Artifacts**:
- `bandit-security-report.json` (retained for 30 days)

---

### 2. 🧪 Tests - Unit & Coverage

**Purpose**: Execute unit tests and verify code coverage exceeds 40% threshold.

**Requirements**:
- ✅ PostgreSQL 15 (test database)
- ✅ RabbitMQ 3 (message broker)

**Coverage Threshold**: **>40%** (configurable via `--cov-fail-under`)

**What it tests**:
- All unit tests in `tests/` directory
- API endpoints functionality
- Business logic
- Database operations
- Message queue interactions

**Failure Criteria**:
- Any test failure
- Coverage below 40%
- Critical test errors

**Artifacts**:
- `coverage.xml` (Codecov upload)
- `coverage-report-html/` (HTML coverage report, 30 days retention)

**Outputs**:
- Test results summary
- Line-by-line coverage report
- Missing coverage indicators

---

### 3. 🛡️ Security Scan

**Purpose**: Perform comprehensive security analysis on dependencies and code.

**Tools Used**:
- **Safety**: Checks dependencies against known vulnerabilities database
- **pip-audit**: Audits Python packages for known security issues
- **OWASP Dependency Check**: Scans for known vulnerabilities in project dependencies

**What it scans**:
- Third-party dependencies (requirements.txt)
- Known CVEs (Common Vulnerabilities and Exposures)
- Outdated packages with security fixes
- License compliance issues
- OWASP Top 10 vulnerabilities

**Failure Handling**:
- ⚠️ Security issues are reported but don't fail the build (continue-on-error: true)
- Allows developers to review and address vulnerabilities appropriately

**Artifacts**:
- `safety-report.json` (30 days retention)
- `pip-audit-report.json` (30 days retention)
- `owasp-dependency-check/` (HTML reports, 30 days retention)

---

### 4. 🏗️ Build - Docker Image

**Purpose**: Ensure the application compiles/builds correctly and Docker image creation succeeds.

**Dependencies**: Requires `test` and `security` stages to pass.

**Build Process**:
1. Create Docker image with:
   - Tag: `orders-api:${COMMIT_SHA}`
   - Tag: `orders-api:latest`
   - Build date metadata
   - Git commit reference

2. Test Docker image:
   - Verify Python imports work
   - Verify FastAPI app initializes
   - Check image functionality

**Failure Criteria**:
- Docker build errors
- Import failures
- Application initialization errors

**Outputs**:
- Docker image size
- Build metadata
- Import verification results

---

### 5. 🔗 Integration Tests (Conditional)

**Triggers**: Only runs on:
- Pull requests
- Pushes to `main` branch
- Pushes to `develop` branch

**Purpose**: Test end-to-end functionality with real services.

**Requirements**:
- PostgreSQL database
- RabbitMQ message broker
- Full application stack

**What it tests**:
- API integration tests
- Database connectivity
- Message queue operations
- Cross-service communication

---

### 6. 📋 CI/CD Summary

**Purpose**: Generate a comprehensive summary of all pipeline results.

**Always runs**: Even if previous stages fail.

**Summary includes**:
- Status of each pipeline stage (✅/❌)
- Branch name
- Commit SHA
- Trigger event (push/PR)

**Output**: GitHub Actions summary report

---

## 📊 Code Coverage Requirements

### Minimum Threshold: 40%

The pipeline enforces a minimum code coverage of **40%** across all tests.

**Coverage calculation**:
```python
coverage = (lines_covered / total_lines) * 100
```

**Exempted from coverage**:
- Test files (`*/tests/*`)
- Database migrations (`*/migrations/*`)
- Cache directories (`*/__pycache__/*`)
- Virtual environments (`*/venv/*`, `*/.venv/*`)

**Coverage reports include**:
- Overall percentage
- Per-module breakdown
- Missing lines indicators
- Branch coverage

---

## 🔧 Local Development

### Running Lint Checks Locally

```bash
cd api-orders

# Run flake8
flake8 app tests

# Format code with black
black app tests

# Sort imports
isort app tests

# Type check
mypy app --ignore-missing-imports

# Security scan
bandit -r app
```

### Running Tests Locally

```bash
cd api-orders

# Install test dependencies
pip install -r requirements-test.txt

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-fail-under=40

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Running Security Scans Locally

```bash
cd api-orders

# Check dependencies for vulnerabilities
safety check

# Audit with pip-audit
pip-audit

# Run bandit security scan
bandit -r app -ll
```

---

## 🚨 Troubleshooting

### Pipeline Failures

#### Lint Stage Fails

**Common causes**:
- Code formatting issues
- Unsorted imports
- Syntax errors
- Code complexity too high

**Solutions**:
```bash
# Fix formatting
black app tests

# Fix imports
isort app tests

# Check for syntax errors
flake8 app tests
```

#### Test Stage Fails

**Common causes**:
- Test failures
- Coverage below 40%
- Database connection issues
- Missing dependencies

**Solutions**:
```bash
# Run tests locally
pytest tests/ -v

# Check specific test
pytest tests/test_file.py::test_function -v

# Update coverage
# Add more tests or mark code as no cover
```

#### Security Stage Reports Issues

**Common causes**:
- Vulnerable dependencies
- Outdated packages
- Known CVEs

**Solutions**:
```bash
# Update dependencies
pip list --outdated
pip install --upgrade package_name

# Check specific vulnerability
safety check --full-report
```

#### Build Stage Fails

**Common causes**:
- Docker build errors
- Missing dependencies in requirements.txt
- Import errors

**Solutions**:
```bash
# Build locally
docker build -t orders-api:test .

# Test import
docker run --rm orders-api:test python -c "import app"

# Check Dockerfile syntax
docker build --no-cache -t orders-api:test .
```

---

## 📈 Continuous Improvement

### Recommended Practices

1. **Keep coverage above threshold**: Aim for 60-80% coverage
2. **Fix security issues promptly**: Review security reports regularly
3. **Maintain clean code**: Follow linting rules
4. **Write meaningful tests**: Test business logic, not just coverage
5. **Update dependencies**: Keep packages up to date
6. **Review pipeline failures**: Don't ignore warnings

### Pipeline Enhancements (Future)

- [ ] Add SonarCloud integration for advanced code quality metrics
- [ ] Implement automatic dependency updates (Dependabot)
- [ ] Add performance testing stage
- [ ] Implement automated deployment to staging
- [ ] Add smoke tests after deployment
- [ ] Integrate with Slack/Discord for notifications

---

## 📚 References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [black Documentation](https://black.readthedocs.io/)
- [bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)

---

## ✅ Pipeline Status Badge

Add to README.md:

```markdown
![CI/CD Pipeline](https://github.com/jeobran69367/Mspr4_commande/actions/workflows/ci-api-orders.yml/badge.svg)
```

---

**Last Updated**: January 3, 2026
**Maintained by**: DevOps Team
