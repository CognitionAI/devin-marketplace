---
name: fix-java-vuln
description: "Use when the user asks to fix, patch or upgrade a Java, JDK or JVM vulnerability (e.g. 'Please fix my Java vulnerability'), Java4Shell or CVE-2026-114938, or to find vulnerable JDK versions in Dockerfiles, distro packages, SDKMAN/asdf version files, setup-java CI, Gradle/Maven toolchains, Helm/IaC or Ansible/Chef/Puppet. Read-only inventory, approval gate, regression tests, focused PRs."
---

# Fix Java vulnerability (Java4Shell, CVE-2026-114938)

## Overview
Find and fix Java runtimes affected by Java4Shell: a heap memory-corruption bug in the HotSpot JVM's AVX-512 Base64 decoder, disclosed on 2026-11-17 (CVSS v3.1 8.1 per Oracle and OpenJDK, CVSS v4 9.2 per Calif). When Base64 that an attacker controls reaches `java.util.Base64` decoding, it can leak memory or lead to unauthenticated remote code execution. A deployment is affected if both hold:
- JDK 17.0.6 or later, 21, 25 or 27 on a build older than its vendor's fixed build. Standard Java 8 and 11 builds are not affected. Oracle Java 8 Enterprise Performance Pack is. The advisories do not list the non-LTS lines (18–20, 22–24, 26) and no fixed build exists for them: treat them as vulnerable.
- An x86-64 CPU with AVX-512 VBMI (Intel Ice Lake or newer Xeon, AMD Zen 4 or newer). ARM64 and older x86 CPUs are not affected.

Base64 from an untrusted source reaching the decoder is what makes it exploitable, and that is rarely something a repo can rule out. Servers decode it in auth headers, tokens and uploads. Clients are exposed too: a Java program that only opens a TLS connection to a malicious server can be compromised, so outbound-only workloads (CLI tools, build agents, batch jobs, integration workers) count.

Inventory read-only first. Wait for approval before editing. Patch each approved repo to a fixed vendor build, verify the built artifact, and open focused PRs. This is a JVM bug, not a library bug: no dependency bump fixes it.

## What's Needed From User
- Repos or org to scan. Default: every repo connected to Devin.
- Approval of which discovered repos to patch, and of any major upgrade, JDK vendor change or base-OS change.
- Registry, package-mirror and CI access needed to verify targets and run builds.
- Where it is not in the repos: the CPU or instance types the services run on.

## Procedure
1. Search all accessible repos read-only with the git host's code search before cloning (if there is none, which is common on GitHub Enterprise Server and self-managed GitLab, shallow-clone and `rg -n --hidden --glob '!.git'`, since version files are dotfiles). Look for:
   - JDK and JRE base images (`eclipse-temurin`, `amazoncorretto`, `openjdk`, `azul/zulu-openjdk`, `mcr.microsoft.com/openjdk`, `container-registry.oracle.com/java`, `ghcr.io/graalvm`, distroless Java, UBI OpenJDK), including multi-stage builds where the runtime stage differs from the build stage.
   - `openjdk-*`/`java-*-openjdk` OS packages (apt/apk/dnf) and JDK tarball downloads.
   - `.sdkmanrc`, `.java-version`, `.tool-versions`, `actions/setup-java` steps and CI images.
   - Gradle toolchains (`languageVersion`), Maven toolchains and `maven.compiler.release` as usage signals, and jlink/jpackage custom runtimes.
   - Managed runtime settings (Lambda `java17`/`java21`, App Engine, Azure Functions, buildpacks).
   - Helm, Kustomize, Terraform/Packer, and Ansible/Chef/Puppet code that installs a JDK.
   - Products that ship their own JVM: Keycloak, Jira, Confluence, Artifactory, Jenkins, PingFederate, Kafka, Solr, Elasticsearch, Gerrit, Spinnaker, and other vendor images or appliances.
   - Instance types, node pools and `nodeSelector`/architecture settings. An architecture pinned to ARM64 is evidence. An x86 instance family is only a hint, because hypervisors can hide CPU features: the reliable check is the `avx512f`, `avx512bw`, `avx512vbmi` and `bmi2` flags in `/proc/cpuinfo` on the host.
   - JVM options (`JAVA_TOOL_OPTIONS`, `JDK_JAVA_OPTIONS`, `JAVA_OPTS`, product-specific variables, `-XX` flags in entrypoints and manifests), to see whether a mitigation flag is already set.
   - Base64 decoding of request or response data: `Base64.getDecoder()`, `getUrlDecoder()`, `getMimeDecoder()`, and frameworks that decode for you (HTTP Basic auth, JWT and session tokens, SAML, data URIs, multipart and JSON binary fields).
2. Produce one inventory table: repo, file:line, signal, JDK vendor and current version, channel (official image, distro package, tarball, managed platform), exact/floating/digest pin, production vs build/CI-only, CPU architecture and whether AVX-512 VBMI is known, whether a mitigation flag is set, whether it decodes untrusted Base64, internet exposure if discernible, test coverage (none, thin, suite), and confidence. List repos you could not search separately.
3. Mark each entry fixed, vulnerable, mitigated, not affected, or unknown.
   - Not affected needs evidence: a JDK line outside the affected set, or an architecture pinned to ARM64. "No Base64 decoding found" is not enough, since almost every web service decodes Base64 somewhere in its stack.
   - If the CPU cannot be determined from the repos, mark it unknown and treat the entry as vulnerable.
   - Mitigated means a vulnerable build that starts with `-XX:-UseBASE64Intrinsics` or `-XX:UseAVX=2`. It still needs the upgrade.
   - A product that bundles its JVM is unknown until the product vendor's advisory or the image itself gives the bundled JDK build.
   - For distro and managed-platform builds, check the vendor's package changelog or advisory for CVE-2026-114938. Version numbering differs by vendor, so never compare one vendor's `java -version` with another vendor's fixed build.
4. Stop. Show the table and ask which repos to patch. Ask in the same message about major upgrades, vendor changes and base-OS changes, so they can all be approved up front. Change nothing during discovery.
5. Start one child session per approved repo, at most five running at once. Each child rechecks the inventory for its repo before editing.
6. In each child, pick the smallest fixed target per path and confirm it exists before editing. Check against the registry or package mirror the repo's CI already uses (Artifactory, Nexus, Harbor or a cloud registry) when public hosts are blocked; if neither is reachable, mark the target unverified in the PR and let the CI build prove it.
   - Exact image tag: bump to the vendor's fixed build in the same major, keeping the vendor and the variant (`-jre`, `-alpine`, `-jammy`, etc.).
   - Digest pin: resolve and pin the new digest.
   - Floating tag (`eclipse-temurin:21`, `amazoncorretto:17`): leave the tag. Require a `--pull --no-cache` rebuild and redeploy, and record the per-platform digest you verified.
   - Placeholder or unresolvable digest: flag it, since what is actually deployed is unknown, and ask the user to confirm the running image.
   - Distro package: upgrade from the vendor security repo and record the package release and its changelog's CVE entry. In Dockerfiles, pin the fixed release or fail the build if an older one is installed. In Ansible/Chef/Puppet, `state=present` (or equivalent) never upgrades existing hosts: use `latest` or a version pin.
   - Version files and CI `setup-java`: set the fixed build, keep every file that names the version consistent, and confirm the resolved version in the CI log.
   - jlink/jpackage runtimes and anything that vendors a JDK: rebuild from the fixed JDK.
   - Managed runtimes: providers don't publish the exact build, so check the provider's base image or log `Runtime.version()` from the service, and say what the user must redeploy.
   - Helm/IaC: change the input that actually selects the artifact (image tag/digest, AMI, package pin) and regenerate lock or render outputs.
   - No fixed build available yet (vendor has not released, non-LTS line, or a bundled product without a vendor update): report it as blocked and, with approval, add `-XX:-UseBASE64Intrinsics` where the JVM options are set (see mitigations below). Keep the item open until the fixed build is in.
7. Leave Gradle/Maven language level and `release` settings unchanged. They don't select the deployed runtime.
8. Report JDK 17.0.0–17.0.5 and standard Java 8 and 11 as not affected by this CVE, and say separately that they are missing other fixes from the same release. Upgrade them only if the user approves.
9. Test for regressions before and after the change:
   - Baseline: before editing, build the current artifact (`--pull`, record its digest as the rollback target) and run the repo's tests (`./gradlew test`, `mvn verify`, or the CI test command) on the current JDK. Record results so pre-existing failures aren't blamed on the upgrade.
   - After: rebuild and run the same tests on the new JDK, inside the new image where the image is what ships. Treat new failures and new warnings as regressions.
   - Compare runtimes: diff `java -version` and `java -XshowSettings:properties -version` between old and new images, and report any vendor, VM or base-OS change.
   - Smoke test: start the service as production does, request a health or main route, and check logs for startup errors.
   - Save each step's output as a log (baseline, after, runtime diff, smoke) and attach it to the PR.
   - If the repo has no tests or doesn't build, say so prominently and validate with a scratch copy that only adds what's missing.
   - Confirm the artifact's version (`java -version` in the built production image, or the image SBOM). For distro builds, also confirm the installed package release contains the fix.
   - If a regression appears, finish the read-only checks above, then stop and report it with the failing output and the smallest fix, verified in a scratch copy. Leave the version bump uncommitted until the user decides. Don't change app code without approval.
10. Open one focused PR per repo listing each path before → after, digests, floating tags needing rebuild, blocked items, baseline vs. after test results, runtime diffs and verification evidence. Label risk: low for a patch build on the same vendor, major and base, high for major upgrades, vendor changes, base-OS changes or untested repos. Include a rollout plan: staging or canary first, then the previous image digest/package version to roll back to. That rollback target is still vulnerable, so roll back only briefly.
11. Roll up child results into one table: repo, PR, path, before → after, production or CI-only, fix evidence, tests, blocked items, follow-ups. Remind the user that fixes and mitigation flags take effect only after deploying and restarting every JVM, and that `jcmd <PID> VM.version` and `jcmd <PID> VM.flags -all` confirm what a running JVM actually has.

## Specifications
- Discovery is read-only and ends at an explicit approval gate.
- Every target is confirmed to exist and contain the fix before editing.
- Each PR includes `java -version` evidence from the built production artifact. For CI-only paths, version files and managed runtimes, give the best available evidence and name the check the user must run after merge.
- Done means every approved deployment is either verified fixed or reported as blocked with a concrete next step.

## Advice and Pointers
- Known fixed builds (check each vendor's advisory for builds not listed, e.g. Corretto, Temurin, Zulu, Red Hat):
  - Oracle Java SE `17.0.21.1`, `21.0.13.1`, `25.0.5.1`, `27.0.1.1`, and `8u513-perf` for the Java 8 Enterprise Performance Pack.
  - Oracle GraalVM for JDK `17.0.21.1` and `21.0.13.1`; Oracle GraalVM Enterprise Edition `21.3.20.1`.
  - Microsoft Build of OpenJDK `17.0.21.1`, `21.0.13.1`, `25.0.5.1`.
- Amazon Corretto shipped fixes at disclosure. Red Hat was still preparing builds at disclosure.
- Temporary mitigations, for JVMs that cannot move to a fixed build yet. Either one blocks the bug; neither replaces the upgrade:
  - `-XX:-UseBASE64Intrinsics` turns off hardware-accelerated Base64, at the cost of slower Base64. It needs no unlock flag and ARM JVMs accept it, so it is safe to set fleet-wide, for example in `JAVA_TOOL_OPTIONS`. Prefer this one.
  - `-XX:UseAVX=2` turns off AVX-512 and may slow cryptography and other vectorized code. Set it only on x86-64: ARM JVMs do not recognize it and fail to start unless `-XX:+IgnoreUnrecognizedVMOptions` is also set.
  - Check after restart with `java -XX:+PrintFlagsFinal -version | grep -E 'UseAVX |UseBASE64Intrinsics'`.
  - A reverse proxy that buffers request bodies is not a mitigation.
- Prioritize internet-facing services, authentication services (Keycloak, PingFederate) and the products listed in step 1. Then patch outbound-only JVMs, including build agents and CI runners: they are exploitable from the server side of a TLS connection. A JDK that only compiles code and never runs in production or opens connections is the lowest priority.
- Do not confuse this with Log4Shell (a Log4j library bug) or with the October 2026 eMudhra certificate alerts (CVE-2026-91403, CVE-2026-114820), which are not remote code execution.
- Vendor products and appliances that bundle a JVM need vendor updates. Flag them; don't patch them in place.

## Forbidden Actions
- Do not edit before the user approves a repo.
- Do not guess image tags, digests, or package versions.
- Do not send input meant to trigger the bug, against the user's services or anyone else's. Decide exposure from versions and CPU, not from a live test.
- Do not present moving to ARM64 or another CPU as the fix.
- Do not present a mitigation flag as the fix, or add one without approval.
- Do not do a major JDK upgrade or change JDK vendor without explicit approval.
- Do not change the base distribution or image flavor without saying so.
