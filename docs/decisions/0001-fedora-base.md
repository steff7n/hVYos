# ADR-001: Fedora as base distribution

**Date:** 2025-03-09  
**Status:** Accepted

## Context

Linta Linux needs a stable, well-maintained upstream that provides a large package set, predictable release cadence, and strong security updates. The base must support both traditional and immutable/atomic workflows and integrate well with modern tooling (Flatpak, containers, Wayland). Alternatives such as Debian/Ubuntu, Arch, or building from scratch were considered; each has trade-offs in repository freshness, lifecycle length, and default stack choices.

## Decision

Linta is derived from Fedora. We use Fedora’s official repositories and release cycle as the foundation: same kernel, base packages, and security updates, with a clear upgrade path. The package set and default configurations are curated for Linta’s target use cases (desktop, development, optional immutable profiles) while retaining compatibility with Fedora’s ecosystem and documentation where applicable.

## Consequences

- Users and contributors can rely on Fedora’s release schedule and support lifecycle. Package availability and quality inherit from Fedora’s maintainer community. Downstream maintenance is focused on Linta-specific packages, images, and defaults rather than forking the entire distribution. Trade-off: Linta’s release timing and some policies are coupled to Fedora’s; major changes in Fedora may require coordinated adjustments in Linta.
