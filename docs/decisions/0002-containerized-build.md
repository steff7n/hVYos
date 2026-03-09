# ADR-002: Containerized RPM/ISO build

**Date:** 2025-03-09  
**Status:** Accepted

## Context

Building RPMs and installation media (ISOs) must be reproducible and independent of the host OS to avoid “works on my machine” failures and to support CI and different contributor environments. Builds that depend on host-installed packages, versions, or paths are hard to debug and can produce inconsistent artifacts. A clean, documented build environment is required for trust and repeatability.

## Decision

RPM and ISO builds run inside a Fedora-based container defined by a Containerfile (or Dockerfile). The container provides a fixed set of build dependencies and a known filesystem layout; the build scripts assume this environment. Contributors and automation run the same container image (or an equivalent built from the same Containerfile) so that builds are reproducible across machines and over time.

## Consequences

- Build results are consistent regardless of host distribution or local package state. Onboarding is simplified: install a container runtime and run the image. CI can use the same image for every run. Downside: maintaining and updating the Containerfile is part of the project’s responsibility; image size and build time must be kept reasonable. Debugging build issues may require entering the container or matching its environment locally.
