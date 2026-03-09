# ADR-003: Niri as default compositor for the Niri profile

**Date:** 2025-03-09  
**Status:** Accepted

## Context

Linta offers a Niri-oriented profile for users who want a tiling Wayland compositor with a focused, keyboard-driven workflow. The default compositor for this profile must be Wayland-native, actively maintained, and aligned with the profile’s goals: minimalism, scriptability, and clear window management. Other options (Sway, Hyprland, River, etc.) were considered for fit with the profile’s design and maintenance burden.

## Decision

Niri is the default Wayland compositor for the Niri profile. It is shipped and configured as the primary session option for that profile, with documentation and defaults (keybindings, optional integration with the rest of Linta) tailored to Niri. The profile is named and scoped around this choice so that users opting into “Niri profile” get a consistent, Niri-first experience.

## Consequences

- The Niri profile has a single, clear default compositor, which simplifies documentation and support. Users who prefer another tiling compositor can still install it and use a different profile or session. Maintenance is bounded to one primary compositor for this profile; version and config updates follow Niri’s releases and Linta’s schedule. If Niri’s direction or maintenance status changed significantly, the decision could be revisited with a new ADR.
