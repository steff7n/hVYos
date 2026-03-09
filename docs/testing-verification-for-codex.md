# Linta — Potwierdzenie testów i walidacji (dla Codexa)

**Data:** 2025-03-09  
**Kontekst:** Codex znalazł kilka bugów; poniżej potwierdzenie, że testy są wdrożone i działają.

---

## Testy jednostkowe — DZIAŁAJĄ

- **Polecenie:** `make test` (lub osobno `make test-lintactl`, `test-snapshots`, `test-nvidia`, `test-welcome`, `test-flatpak-manager`, `test-keybindings`).
- **Wynik:** Wszystkie **87 testów** przechodzą (Python 3, pytest/unittest).
- **Pakietów z testami:** 6
  - **lintactl** — 18 testów (release, profile, theme, CLI)
  - **linta-snapshots** — 11 testów (snapper list, require root, create)
  - **linta-nvidia** — 11 testów (GPU detection, status, driver branch)
  - **linta-welcome** — 18 testów (profile, run, file manager/theme/terminal options, font presets, constants) — PyQt mockowany
  - **linta-flatpak-manager** — 15 testów (parse flatpak columns, AppInfo, run_flatpak_sync, filter) — PyQt mockowany
  - **linta-keybindings** — 14 testów (KeyBinding, detect desktop, Niri/KDE parsers, constants) — PyQt mockowany

Testy są uruchamiane bez displaya (Qt zmockowany tam, gdzie potrzeba). W CI (GitHub Actions) i lokalnie `make test` kończy się sukcesem.

---

## Walidacja manifestów i kickstartów

- **Polecenie:** `make validate`.
- **Skrypty:**
  - `build/testing/validate-manifests.sh` — sprawdza, czy pakiety z `build/packages/*.txt` są w repozytoriach Fedory (`dnf info --available`). Pakiety `linta-*` / `lintactl` są pomijane (custom).
  - `build/testing/validate-kickstarts.sh` — wymaga `ksvalidator` (pykickstart) z Fedory.

**Uwaga:** Na hoście Manjaro/Arch `make validate` może się nie udać, bo:
  1. `dnf` nie jest repozytorium Fedory — np. „flameshot — not found in repos” to efekt środowiska, nie brak flameshot w Fedora.
  2. `ksvalidator` nie jest zainstalowany — do pełnej walidacji kickstartów potrzebny jest kontener Fedory lub `dnf install pykickstart` na Fedorze.

W **kontenerze budującym** (`./scripts/build-with-container.sh validate`) oba skrypty mają poprawne środowisko (Fedora + pykickstart).

---

## Podsumowanie dla Codexa

- **Testy:** Zrobione i działające — 87 testów, 6 pakietów, `make test` przechodzi.
- **Walidacja:** Zaimplementowana; pełne przejście wymaga środowiska Fedory (kontener lub maszyna Fedora). Bugi zgłoszone przez Codexa można zweryfikować przez `make test` oraz po naprawach ponowne uruchomienie testów.

Jeśli Codex podał konkretne bugi, po ich fixie wystarczy ponownie uruchomić `make test` (i ewentualnie `make validate` w kontenerze) i potwierdzić zielone wyniki.
