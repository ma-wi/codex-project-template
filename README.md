# Codex-Projekt-Template

Dieses Repository ist ein Template für neue Entwicklungsprojekte, die mit Coding Agents bearbeitet werden. Es liefert keine fertige Anwendung, sondern eine wiederverwendbare Agent-Control-Plane: Regeln, Rollen, Dokumentationsstruktur, Bootstrap-Skripte und CI-Prüfungen.

Python ist standardmäßig aktiviert. React/TypeScript, Bash und .NET/Visual Basic/PowerShell können optional in `.ai/project.yaml` aktiviert werden.

## Kurzüberblick

Der typische Ablauf ist:

```text
akzeptierte Anforderung -> Planner -> Implementer -> unabhängiger Reviewer
                                      ^ Fehlerbehebung v
                                  Doku-Pflege und Closeout
```

Die wichtigsten Dateien sind:

- `AGENTS.md`: Einstiegspunkt und verbindliche Kurzregeln für Agents.
- `.ai/project.yaml`: technische Projektkonfiguration, zum Beispiel aktivierte Stacks.
- `.ai/tools/`: Bootstrap-, CI-, Lint-, Test-, Security- und Verify-Skripte.
- `.ai/policies/`: dauerhafte Regeln für Workflow, Security, Dependencies, Doku und Quality Gates.
- `.ai/roles/`: Rollenbeschreibungen für Planner, Implementer und Reviewer.
- `.ai/templates/`: Vorlagen für Requirements, Specs, ADRs, Work Items und Reviews.
- `docs/requirements/`: akzeptierte Anforderungen.
- `docs/specifications/`: dauerhafte Spezifikationen und Akzeptanzkriterien.
- `docs/architecture/decisions/`: Architekturentscheidungen, also ADRs.
- `.ai/work/`: temporäre aktive Arbeitspläne pro Requirement.

## Wie das Template funktioniert

1. Mit `create-project.*` wird aus dem Template ein neues Projekt kopiert.
2. Template-interne Dateien wie Template-Tests, Copy-Skripte und Template-eigene Requirements werden nicht übernommen.
3. In `.ai/project.yaml` werden Projektname und Stacks konfiguriert.
4. `bootstrap` erzeugt projektkonkrete Defaults in `.ai/config/project.defaults.env`.
5. `verify.sh` führt alle verbindlichen Gates aus.

`verify.sh` prüft unter anderem:

- Work-State
- Dokumentations-Readiness
- Setup
- Formatierung
- Linting und statische Analyse
- Tests
- Dependency Policy
- Security Checks
- Build

Wichtig: `.ai/config/project.env` darf lokale Befehle für fokussierte Gates überschreiben. `verify.sh` ignoriert diese Datei aber absichtlich. CI verwendet nur die committed Defaults aus `.ai/config/project.defaults.env`.

## Neues Projekt erstellen

Kopiere das Template nicht manuell. Nutze die Copy-Skripte, damit Template-interne Dateien nicht im neuen Projekt landen.

### Linux, macOS, Git Bash oder WSL

```bash
./.ai/tools/create-project.sh --dry-run /path/to/new-project
./.ai/tools/create-project.sh /path/to/new-project
cd /path/to/new-project
```

### Windows PowerShell

```powershell
.\.ai\tools\create-project.ps1 -TargetDirectory "C:\Projects\new-project" -WhatIf
.\.ai\tools\create-project.ps1 -TargetDirectory "C:\Projects\new-project"
Set-Location "C:\Projects\new-project"
```

Das Zielverzeichnis muss leer sein, außer `--force` oder `-Force` wird bewusst verwendet. Force-Modus darf gleichnamige Template-Dateien überschreiben, aber keine fremden Inhalte löschen.

Die Kopie enthält die wiederverwendbaren Projektregeln, Security-Regeln, Konfiguration, CI, Bootstrap und Verify-Skripte. Nicht kopiert werden unter anderem:

- dieses Template-`README.md` und `CHANGELOG.md`;
- Template-Tests und temporäre `.ai/work/`-Artefakte;
- Template-eigene Requirements, Spezifikationen und ADRs;
- Copy-Skripte und `.ai/tools/verify-template.sh`;
- `.ai/config/copy-exclude.txt`, das nur für die Template-Pflege gebraucht wird;
- lokale IDE-/Agent-/Cache-/Build-Zustände.

`bootstrap` erzeugt später ein neues Projekt-README. Die Security-Regeln liegen in `.ai/policies/SECURITY_GUIDELINES.md`; ein separates Root-`SECURITY.md` wird nicht mehr mitgeführt.

## Konfiguration und Bootstrap

Bearbeite zuerst `.ai/project.yaml`:

- `project.name: "CHANGE_ME"` ersetzen;
- nur benötigte Stacks aktivieren;
- bei Python das Backend-Verzeichnis festlegen, standardmäßig `backend`;
- bei React Package Manager und Verzeichnis festlegen;
- bei .NET Solution und explizites Testprojekt eintragen;
- `engineering_knowledge` nur aktivieren, wenn der MCP wirklich eingerichtet ist.

Alle konfigurierten Pfade müssen unterhalb des Repository-Roots bleiben. Absolute Pfade und `..` werden abgelehnt.

Dann Bootstrap ausführen:

```bash
./.ai/tools/bootstrap.sh
```

Oder unter Windows ohne Bash:

```powershell
python .\.ai\tools\bootstrap.py
```

Wenn Python aktiviert ist, muss die in `.github/workflows/ci.yml` gepinnte `uv`-Version installiert sein. Wenn React aktiviert ist, muss die Version aus `.node-version` verwendet werden. Bei pnpm oder Yarn schreibt Bootstrap passende `packageManager`-Metadaten in `package.json`.

Bootstrap erzeugt oder aktualisiert:

```text
.ai/config/project.defaults.env
```

Diese Datei ist die committed Quelle für lokale Vollverifikation und CI. Sie muss eingecheckt werden. Lokale Overrides gehören in `.ai/config/project.env`; diese Datei darf keine Secrets enthalten und wird von `verify.sh` ignoriert.

## Pflichtfelder nach Bootstrap

Sobald `project.name` nicht mehr `CHANGE_ME` ist, behandelt `./.ai/tools/verify.sh` das Repository als echtes Projekt. Dann scheitert CI absichtlich, solange projektbezogene Pflichtfelder leer sind.

Das ist kein GitHub-Actions-Problem und kein Fehler, weil die Anwendung noch blank ist. Es bedeutet: Die Projektregeln sind noch nicht ausgefüllt.

Vor einem grünen CI-Lauf müssen diese Dateien angepasst werden:

- `.ai/PROJECT_CONTEXT.md`: mindestens `Product or service`, `Primary users` und `Main outcome` ausfüllen.
- `.ai/policies/QUALITY_GATES.md`: alle Einträge unter `Required project decisions` ausfüllen.

Für ein privates Einzelprojekt reichen einfache Regeln. Die Defaults in `.ai/policies/QUALITY_GATES.md` sind bewusst pragmatisch formuliert und können später verschärft werden.

Diese Werte stehen nicht an einer zentralen Stelle, weil sie verschiedene Arten von Projektdokumentation sind:

- `.ai/PROJECT_CONTEXT.md` ist kompakte Orientierung für Agents.
- `.ai/policies/QUALITY_GATES.md` ist die dauerhafte Quality-/CI-Policy.
- `.ai/policies/SECURITY_GUIDELINES.md` enthält die Security-Defaults und wird bei Security-relevanten Änderungen geladen.

Die zentrale technische Prüfung sitzt in `.ai/tools/check-docs.py`; sie prüft nur, ob die Pflichtfelder nicht mehr leer oder Platzhalter sind.

## Quality Gates verstehen

`.ai/policies/QUALITY_GATES.md` beschreibt die Regeln. Die konkreten Befehle stehen nach Bootstrap in `.ai/config/project.defaults.env`.

Die Felder unter `Required project decisions` sind keine Shell-Befehle. Dort stehen normale Projektregeln:

- `Minimum coverage policy`: Wann brauchst du Tests?
- `Supported runtime matrix`: Welche Laufzeitumgebung unterstützt du?
- `Warning-as-error policy`: Was passiert mit Warnungen?
- `Security severity threshold`: Ab welcher Security-Stufe ist Schluss?
- `Dependency update policy`: Wie gehst du mit neuen Libraries um?
- `Flaky-test policy`: Was passiert mit wackeligen Tests?
- `CI required checks`: Welche CI-Prüfung muss vor Merge grün sein?

## Git und GitHub initialisieren

```bash
git init
git add .
git commit -m "Initialize project from agent template"
git branch -M main
git remote add origin git@github.com:ORGANIZATION/REPOSITORY.git
git push -u origin main
```

Empfohlene Repository-Einstellungen:

- `main` schützen und Pull Requests verlangen;
- den CI-Verify-Job als required check setzen;
- direkte Pushes auf `main` verhindern;
- Secret Scanning, Dependency Alerts und Code Scanning aktivieren, wenn verfügbar;
- später für Deployments lieber OIDC und Environment Protection statt langlebiger Secrets verwenden.

## Entwicklungsworkflow

Für normale oder größere Änderungen gilt:

1. Requirement akzeptieren.
2. Planner erstellt Spezifikation und Plan.
3. Implementer setzt nur `ready` Tasks um.
4. `./.ai/tools/verify.sh` muss grün sein.
5. Frischer Reviewer prüft unabhängig.
6. Nach Approval werden Doku und temporäre `.ai/work`-Artefakte bereinigt.

Für kleine, rein mechanische Änderungen kann der Prozess reduziert werden. Die Regeln dazu stehen in `AGENTS.md` und `.ai/policies/WORKFLOW.md`.

## Agent-Rollen

Nutze für die Standardrollen frische Agent-Kontexte:

- Planner: `.ai/roles/PLANNER.md`
- Implementer: `.ai/roles/IMPLEMENTER.md`
- Independent reviewer: `.ai/roles/CODE_REVIEWER.md`

Nur diese drei Rollen sind Standard. Security-, Dependency-, Test- und Doku-Hinweise werden über `.ai/policies/REVIEW_LENSES.md` je nach Risiko geladen.

## Dauerhafte und temporäre Informationen

Dauerhaft:

- `docs/requirements/`: akzeptierte Anforderungen;
- `docs/specifications/`: beobachtbares Verhalten, Akzeptanzkriterien und Test-Seams;
- `docs/architecture/decisions/`: akzeptierte Architekturentscheidungen;
- gepflegte Projekt-, Betriebs-, Security- und Architektur-Dokumentation;
- Code und Tests.

Temporär:

- `.ai/work/<requirement-id>/PLAN.md`;
- Task-Dateien;
- lokale Review- und Closeout-Notizen.

Temporäre Dateien bleiben bis nach dem unabhängigen Review erhalten. Danach werden dauerhafte Informationen übertragen, `verify.sh` wird erneut ausgeführt, offene Punkte werden in Issues oder `.ai/NEXT_STEPS.md` verschoben und `.ai/CURRENT_PLAN.md` wird zurückgesetzt.

## Verifikation

Vor Bootstrap im Template:

```bash
./.ai/tools/verify.sh
```

Nach Bootstrap im konkreten Projekt:

```bash
./.ai/tools/ci-setup.sh
./.ai/tools/format.sh --check
./.ai/tools/lint.sh
./.ai/tools/test.sh
./.ai/tools/check-dependencies.sh
./.ai/tools/security.sh
./.ai/tools/build.sh
./.ai/tools/verify.sh
```

`verify.sh` führt die verpflichtenden Gates aus und behandelt ein fehlendes verpflichtendes Gate nicht als Erfolg.

## Dependencies und Supply Chain

Die Dependency Policy verlangt Lockfiles und lehnt offensichtlich unsichere oder nicht interpretierbare direkte Dependency-Angaben ab. Neue oder aktualisierte Dependencies brauchen weiterhin eine kurze menschliche Prüfung: Warum ist sie nötig, wer pflegt sie, welche Lizenz hat sie, gibt es bekannte Schwachstellen, welche Transitives kommen mit, und wie wird sie wieder entfernt oder ersetzt, falls sie problematisch wird?

Automatische Scanner helfen, beweisen aber nicht, dass eine Dependency vertrauenswürdig ist.

## IntelliJ IDEA

1. Neues Projektverzeichnis öffnen.
2. Prüfen, dass der Agent `AGENTS.md` lesen kann.
3. Command Approval und Sandbox möglichst restriktiv halten.
4. JetBrains Project Rules aus `.aiassistant/rules/` nur konfigurieren, wenn die IDE `AGENTS.md` nicht automatisch lädt.
5. Für AI Self-Review diesen Pfad setzen:

```text
$PROJECT_DIR$/.aiassistant/review/self-review.md
```

6. Optionalen `engineering-knowledge` MCP nur aktivieren, wenn `.ai/project.yaml` das erlaubt.

## Unterstützte Stack-Hinweise

- Python nutzt standardmäßig `backend/` als Quellverzeichnis und `tests/` für Tests.
- Python nutzt `uv`, Ruff, mypy, pytest, Bandit, pip-audit und build.
- React nutzt Vite, TypeScript, ESLint, Prettier, Vitest und Testing Library.
- React-Installationen laufen eingefroren: `npm ci`, `pnpm install --frozen-lockfile` oder `yarn install --immutable`.
- Bash nutzt ShellCheck und Bats, wenn sinnvolle Shell-Tests vorhanden sind.
- .NET nutzt Restore im Lock-Modus, Formatprüfung, Warnings-as-errors, Tests und Vulnerability-Prüfung.

Nicht benötigte Stacks und Regeln kannst du in konkreten Projekten entfernen, um Kontext und Wartungsaufwand zu reduzieren.

## Optionale Governance-Vorlagen

- `.ai/templates/THREAT_MODEL.md`: für Public APIs, sensible Daten, Identity, File Parsing, Netzwerke, irreversible Migrationen oder Security-relevante Änderungen.
- `.ai/templates/OWNERSHIP.md`: für Entscheidungs- und Review-Zuständigkeiten bei komplexeren Projekten.

## Gepinnte Tool-Versionen aktualisieren

Tool-Versionen sind absichtlich exakt gepinnt. Wenn du sie aktualisierst, ändere alle Stellen zusammen und führe danach aus:

```bash
./.ai/tools/verify-template.sh
```

Zu prüfende Stellen:

- `UV_VERSION`, `VITE_VERSION`, `PNPM_VERSION`, `YARN_VERSION`, `PYTHON_DEV_DEPENDENCIES` und `REACT_QUALITY_DEPENDENCIES` in `.ai/tools/bootstrap.py`;
- die `astral-sh/setup-uv` Version in `.github/workflows/ci.yml`;
- die gepinnten Ruff-, mypy- und Bandit-Versionen in `.ai/tools/verify-template.sh`;
- `.python-version` und `.node-version`.

## Start-Checkliste

- [ ] Projektname und benötigte Stacks in `.ai/project.yaml` gesetzt.
- [ ] Bootstrap ausgeführt und generierte Dateien geprüft.
- [ ] `.ai/PROJECT_CONTEXT.md` und `.ai/policies/QUALITY_GATES.md` ausgefüllt.
- [ ] `.ai/config/project.defaults.env`, Manifeste und Lockfiles committed.
- [ ] `./.ai/tools/verify.sh` läuft lokal oder in CI durch.
- [ ] GitHub Branch Protection verlangt den CI-Verify-Job.
- [ ] Initiales Requirement angelegt und akzeptiert.
- [ ] Spezifikation und relevante Architekturentscheidungen akzeptiert.

## Lizenz

Wähle für das erzeugte Projekt eine passende Lizenz. Das Template gibt keine Lizenz vor.
