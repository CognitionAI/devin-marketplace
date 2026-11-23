---
name: fix-nginx-vuln
description: "Use when the user asks to fix, patch or upgrade an nginx vulnerability (e.g. 'Please fix my nginx vulnerability'), NGINX2Root, CVE-2026-123007, CVE-2026-123633, CVE-2026-121810, CVE-2026-123634 or CVE-2026-113425, or to find vulnerable nginx versions in Dockerfiles, distro packages, source builds, ingress controllers, OpenResty, Helm/IaC or Ansible/Chef/Puppet. Read-only inventory, approval gate, regression tests, focused PRs."
---

# Fix nginx vulnerability (NGINX2Root, five CVEs)

## Overview
Find and fix nginx deployments affected by NGINX2Root: five memory-corruption bugs disclosed on 2026-11-18 and fixed in nginx 1.31.9 (mainline) and 1.30.7 (stable). Each lets an unauthenticated remote attacker run code as the nginx worker in a specific configuration (CVSS v4 9.2, CVSS v3.1 8.1; F5 says code execution needs ASLR disabled or bypassed). Root on the host comes from a separate Linux kernel SCTP bug that upgrading nginx does not fix. Inventory read-only first. Wait for approval before editing. Patch each approved repo to a fixed vendor build, verify the built artifact, and open focused PRs.

| CVE | Bug | Needs | Vulnerable (nginx.org) |
| --- | --- | --- | --- |
| CVE-2026-123007 | HTTP/2 flow-control out-of-bounds write | HTTP/2 enabled | 1.9.5–1.31.8 |
| CVE-2026-123633 | HTTP/2 use-after-free | HTTP/2 and proxying to an upstream | 1.19.7–1.31.8 |
| CVE-2026-121810 | HTTP/3 use-after-free | HTTP/3 and proxying to an upstream | 1.25.0–1.31.8 |
| CVE-2026-123634 | Resolver use-after-free | `resolver`, a `proxy_pass` target built from variables, and an SSI or mirror subrequest | 0.6.18–1.31.8 |
| CVE-2026-113425 | Mail proxy use-after-free | Mail proxy with `proxy on` and `auth_http` | 0.5.33–1.31.8 |

## What's Needed From User
- Repos or org to scan. Default: every repo connected to Devin.
- Approval of which discovered repos to patch, and of any branch change (stable ↔ mainline), base-OS change or config change.
- Registry, package-mirror and CI access needed to verify targets and run builds.

## Procedure
1. Search all accessible repos read-only with the git host's code search before cloning (if there is none, which is common on GitHub Enterprise Server and self-managed GitLab, shallow-clone and `rg -n --hidden --glob '!.git'`). Look for:
   - `nginx:` images, `nginxinc/*` and other images built on nginx, including multi-stage builds.
   - `nginx*` OS packages (apt/apk/dnf), the nginx.org package repo, and nginx source downloads/`./configure` builds.
   - Products that bundle nginx: OpenResty, Tengine, Kubernetes ingress controllers (ingress-nginx, NGINX Ingress Controller), NGINX Plus, Kong, and vendor images.
   - Helm charts, Kustomize, Terraform/Packer, and Ansible/Chef/Puppet code that installs or configures nginx.
   - nginx config (`nginx.conf`, `conf.d/`, `sites-*`, templates, ConfigMaps and ingress annotations) for the conditions in the table: `http2`, `listen ... quic`/`http3`, `proxy_pass`, `resolver`, `ssi`, `mirror`, and a `mail {}` block with `auth_http`.
   - SCTP on the hosts and node images nginx runs on: a `/etc/modprobe.d/` entry for `sctp`, `modprobe sctp` or `sctp` in `modules-load.d`, and SCTP Services or ports in Kubernetes manifests.
2. Produce one inventory table: repo, file:line, signal, current version, channel (official image, distro package, source build, bundled in a product, managed platform), exact/floating/digest pin, which of the five CVEs the config meets the conditions for, internet exposure if discernible, test coverage (none, thin, suite), and confidence. List repos you could not search separately.
3. Mark each entry fixed, vulnerable, or unknown. A version in range with none of the five conditions met is still vulnerable-by-version: report it as lower priority, not as fixed. For distro and managed-platform builds, check the vendor's package changelog or advisory for all five CVEs. Never compare `nginx -v` with upstream numbers to decide this: distributions backport fixes without changing the version. If the distribution has not shipped a fix yet (Debian and Ubuntu had not at disclosure), the entry is vulnerable and blocked on the vendor.
4. Stop. Show the table and ask which repos to patch. Ask in the same message about branch changes, base-OS changes and any temporary config mitigation, so they can all be approved up front. Change nothing during discovery.
5. Start one child session per approved repo, at most five running at once. Each child rechecks the inventory for its repo before editing.
6. In each child, pick the smallest fixed target per path and confirm it exists before editing. Check against the registry or package mirror the repo's CI already uses (Artifactory, Nexus, Harbor or a cloud registry) when public hosts are blocked; if neither is reachable, mark the target unverified in the PR and let the CI build prove it.
   - Exact image tag: bump to the fixed release on the same branch (stable → 1.30.7, mainline → 1.31.9), keeping the variant (`-alpine`, `-slim`, `-perl`, `-otel`, etc.).
   - Digest pin: resolve and pin the new digest.
   - Floating tag (`nginx:stable`, `nginx:latest`, `nginx:1.30`): leave the tag. Require a `--pull --no-cache` rebuild and redeploy, and record the per-platform digest you verified. Say if the tag's base OS has moved.
   - Placeholder or unresolvable digest: flag it, since what is actually deployed is unknown, and ask the user to confirm the running image.
   - Distro package: upgrade from the vendor security repo and record the package release and its changelog's CVE entries. In Dockerfiles, pin the fixed release or fail the build if an older one is installed. In Ansible/Chef/Puppet, `state=present` (or equivalent) never upgrades existing hosts: use `latest` or a version pin.
   - Distro package with no fixed release yet: report it as blocked and offer the temporary mitigations below, or, with approval for the channel change, a move to the nginx.org package repo or official image at 1.30.7 or 1.31.9.
   - Source build: move to the fixed tarball, verify its PGP signature from nginx.org, and keep configure flags, modules and patches. Rebuild dynamic and third-party modules against the new version.
   - Bundled nginx (OpenResty, ingress controllers, NGINX Plus, vendor images): upgrade the product to the release its vendor says contains the fixes. Do not swap the nginx binary inside it. For NGINX Plus, F5 lists R37.3.0.1 and R37.0.8.1 as fixed (R37.2.0.1 and R37.0.7.1 for CVE-2026-123633 only); confirm against F5 K000163926 before picking one. If the vendor has not released one, report it as blocked with the temporary mitigations below.
   - Helm/IaC: change the input that actually selects the artifact (image tag/digest, chart version, AMI, package pin) and regenerate lock or render outputs.
7. Report end-of-life branches (anything older than the current stable and mainline that gets no fixed release) separately, with an upgrade path to 1.30.7 or 1.31.9. Make a branch change only if the user approves.
8. Test for regressions before and after the change:
   - Baseline: before editing, build the current artifact (`--pull`, record its digest as the rollback target), run `nginx -t` against the repo's real config inside it, and run the repo's tests if any. Record results so pre-existing failures aren't blamed on the upgrade.
   - After: rebuild, run `nginx -t` and the same tests inside the new production image, not on the host. Treat new errors and new `[warn]` lines (deprecated directives) as regressions.
   - Compare runtimes: diff `nginx -V` (configure arguments, built-in and dynamic modules, OpenSSL version) between old and new images, and report any module or base-OS change.
   - Smoke test: start the container as production does, request a health or main route over each enabled protocol (HTTP/1.1, HTTP/2, and HTTP/3 where on), check that a proxied route still reaches its upstream, and check the error log.
   - Save each step's output as a log (baseline, after, runtime diff, smoke) and attach it to the PR.
   - If the repo has no tests or doesn't build, say so prominently and validate with a scratch copy that only adds what's missing.
   - Confirm the artifact's version (`nginx -v`, or the image SBOM). For distro builds, also confirm the installed package release contains the fix.
   - If a regression appears, finish the read-only checks above, then stop and report it with the failing output and the smallest fix, verified in a scratch copy. Leave the version bump uncommitted until the user decides. Don't change config or app code without approval.
9. Open one focused PR per repo listing each path before → after, digests, floating tags needing rebuild, blocked items, end-of-life items, baseline vs. after test results, runtime diffs and verification evidence. Label risk: low for a patch bump on the same branch and base, high for branch changes, base-OS changes or untested repos. Include a rollout plan: staging or canary first, then the previous image digest/package version to roll back to. That rollback target is still vulnerable, so pair it with the temporary mitigations below.
10. Roll up child results into one table: repo, PR, path, before → after, fix evidence, tests, blocked items, follow-ups. Remind the user of the two things a merged PR does not do:
    - The fix takes effect only after deploying and fully restarting nginx. `nginx -s reload` keeps the old binary running.
    - The kernel SCTP bug is still open on every host, and it is what turns worker code execution into host root, including from inside a container. For hosts and node images that do not use SCTP, recommend `install sctp /bin/false` in a file under `/etc/modprobe.d/`, as a separate approved change. That does not unload a module that is already loaded (unload it or reboot), and it does nothing where SCTP is built into the kernel.

## Specifications
- Discovery is read-only and ends at an explicit approval gate.
- Every target is confirmed to exist and contain the fix before editing.
- Each PR includes verification against the built artifact, plus baseline vs. after results from inside the image.
- Done means every approved deployment is either verified fixed or reported as blocked with a concrete next step.

## Advice and Pointers
- Prioritize internet-facing nginx with HTTP/2 on: CVE-2026-123007 needs nothing else, and most servers meet it. Next, container hosts where a compromised nginx worker could reach the shared kernel.
- Temporary mitigations only reduce exposure, and none covers all five:
  - `http2 off` blocks CVE-2026-123007 and CVE-2026-123633. It breaks native gRPC, so check for `grpc_pass` and gRPC clients first.
  - Removing `quic` listeners and setting `http3 off` blocks CVE-2026-121810.
  - Pointing `proxy_pass` at a fixed upstream instead of a variable, where `mirror` or SSI is in use, blocks CVE-2026-123634.
  - Binding the mail proxy to loopback, or firewalling it to trusted IPs, covers CVE-2026-113425.
  - Restart nginx afterwards so existing connections drop.
- Five other CVEs were fixed in the same nginx releases (CVE-2026-118899, -120967, -120993, -123640, -125283). They are not part of NGINX2Root; the same upgrade fixes them.
- The kernel SCTP bug has no CVE number or patch in the sources this skill was written from. Check the distribution's kernel advisories for one before reporting it as unpatched.
- A CDN or load balancer in front of nginx hides the version from outside but does not remove the bug from the origin.

## Forbidden Actions
- Do not edit before the user approves a repo.
- Do not guess image tags, digests, or package versions.
- Do not present a mitigation as a fix, or an nginx upgrade as a fix for the kernel bug.
- Do not send requests meant to trigger the bugs, against the user's hosts or anyone else's.
- Do not turn off HTTP/2 or HTTP/3, or change other nginx config, without approval.
- Do not change kernel module settings in the nginx PR or without approval.
- Do not change the base distribution, image flavor, modules, or build flags without saying so.
