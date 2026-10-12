# DevSecOps Security Pipeline

A GitHub Actions CI/CD pipeline that enforces automated security gates (SAST, SCA, DAST, and secret scanning) across a multi-language application (Python/Flask + Node.js), with supply chain security (image signing, SBOM), Kubernetes-hardened deployment manifests, and a manual approval gate before production.

Every gate below was added incrementally, tested in isolation, and debugged against real (and sometimes false-positive) findings — see the case studies at the bottom for the most instructive ones.

## Architecture


![DevSecOps Pipeline Graph](pipeline-graph.png)

Parallel static gates (SAST, Secrets, SCA, IaC) → DAST fuzzing → Keyless Cosign signing → Auto Staging → Manual Approval for Production.


Branch protection on `main` requires these checks to pass before merge is even possible — this isn't just a CI pipeline that reports problems, it's a gate that blocks bad code from landing.

## Tools

Bandit: Fast AST-level static analysis for Python, targeting pattern-based insecure function calls and rule violations.

CodeQL: Deep semantic SAST focused on taint analysis. Tracks unsanitized input flows from sources to vulnerable sinks across interprocedural call graphs.

TruffleHog: Scans git commit history and CI runners for high-entropy secrets and verified credentials. Enforced locally via a Docker-based pre-commit hook for a shift-left workflow.

Trivy (SCA & Image): Scans the container base image and language-level dependencies (pip/npm) for known CVEs.

Trivy (IaC / Config): Audits Kubernetes deployment and service manifests under k8s/ for privilege escalation, root execution, and missing securityContext parameters.

Trivy (SBOM - CycloneDX): Generates standardized CycloneDX 1.7 JSON specs capturing direct, transitive, and OS-level components for software supply chain visibility.

OWASP ZAP (Full Scan): Active HTTP fuzzing against live services, validating attack vectors like Open Redirects, SSRF, and injection flaws.

Cosign (Sigstore): Keyless container signing and signature verification leveraging GitHub Actions OIDC identity tokens.


## Deployment gate

Every image that reaches `Deploy to Production` has already: passed all four security gates, been signed with a verifiable, tamper-evident signature, and been deployed to staging. Production still requires a human to click "Approve" in GitHub — a deliberate policy decision, not a technical necessity, reflecting how real financial/regulated systems treat production pushes.

Note: staging/production deployment steps are currently simulated (no real cluster is connected — GitHub Actions runners can't reach a local machine behind NAT, and no cloud cluster is provisioned for this project). The approval mechanism itself is fully real and functions exactly as it would with a live deployment target.

## Local development

Secrets are checked twice: once locally, before a commit is even created, and again in CI as a backstop.


pip install pre-commit
pre-commit install



## Roadmap

**Done**
-  Four independent, parallel security gates (SAST ×2, SCA, DAST, Secrets)
-  Kubernetes manifests (Deployment, Service, NetworkPolicy, RBAC) with security hardening — non-root, read-only filesystem, resource limits, restricted egress
-  `trivy config` scan of Kubernetes manifests as a CI job
-  Keyless container signing (Cosign) + verification
-  SBOM generation (CycloneDX)
-  Staging/production environments with a manual approval gate for production
-  Email notification on pipeline failure
-  Pre-commit hook for local secret scanning (Docker-based Trufflehog)
-  Dependabot for automated dependency updates
- Real cloud-hosted staging/production clusters to replace the current simulated deploy steps

**Planned**
- Re-architect the demo application into a fintech-style microservice setup (auth service with JWT, payment/transfer endpoint, balance query service, API gateway) to demonstrate security patterns relevant to regulated financial systems (IDOR, token handling, PCI-DSS-adjacent controls)
- AI-assisted triage — LLM-based summarization and prioritization of scan findings on each PR
- Real cloud-hosted staging/production clusters to replace the current simulated deploy steps

## Running locally

```bash
docker build -t devsecops-demo-app:latest .
docker run -d --name test-app -p 5000:5000 devsecops-demo-app:latest
```
