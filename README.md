# Codex-Projekt-Template

Dieses Repository ist ein Template für neue Entwicklungsprojekte, die mit Coding Agents bearbeitet werden. Es liefert keine fertige Anwendung, sondern eine wiederverwendbare Agent-Control-Plane: Regeln, Rollen, Dokumentationsstruktur, Bootstrap-Skripte und CI-Prüfungen.

Python ist standardmäßig aktiviert. React/TypeScript, Bash und .NET/Visual Basic/PowerShell können optional in `.ai/project.yaml` aktiviert werden.

## Kurzüberblick

Der typische Ablauf ist:

```text
neue Capability       -> Planner        -> Implementer -> unabhängiger Reviewer
bestehende Capability -> Change Planner -> Implementer -> unabhängiger Reviewer
                                                ^ Fehlerbehebung v
                                            Doku-Pflege und Closeout
```

Die wichtigsten Dateien sind:

- `AGENTS.md`: Einstiegspunkt und verbindliche Kurzregeln für Agents.
- `.ai/project.yaml`: technische Projektkonfiguration, zum Beispiel aktivierte Stacks.
- `.ai/tools/`: Bootstrap-, CI-, Lint-, Test-, Security- und Verify-Skripte.
- `.ai/policies/`: dauerhafte Regeln für Workflow, Security, Dependencies, Doku und Quality Gates.
- `.ai/roles/`: Rollenbeschreibungen für Planner, Change Planner, Implementer und Reviewer.
- `.ai/templates/`: Vorlagen für Requirements, Capability Specs, Current Work, Changes, Impact-Matrizen, ADRs, Work Items und Reviews.
- `docs/requirements/`: akzeptierte Anforderungen.
- `docs/specifications/`: capability-basierte aktuelle Spezifikationen und Akzeptanzkriterien, z. B. `customer-management.md`.
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

## Bestehendes Projekt auf eine neue Template-Version aktualisieren

Wenn das Template weiterentwickelt wurde, integriert der Update-Modus die neuen und
geänderten Dateien in ein Projekt, das bereits aus dem Template erstellt wurde. Das
Skript läuft aus dem Template heraus und zeigt auf den Projektordner.

Grundregeln des Update-Modus:

- Neue Template-Dateien werden hinzugefügt.
- Geänderte wiederverwendbare Control-Plane-Dateien werden aktualisiert.
- Projekteigene Dateien aus der Manifest-Sektion `[update_protected]` (z. B.
  `.ai/project.yaml`, `.ai/PROJECT_CONTEXT.md`, `.ai/policies/QUALITY_GATES.md`,
  `.ai/config/project.defaults.env` und die Dependency-Listen) werden **nie**
  überschrieben. Unterschiede werden nur als Patch zum manuellen Zusammenführen gemeldet.
- Es wird nichts im Zielprojekt gelöscht.

### Linux, macOS, Git Bash oder WSL

```bash
# Vorschau, ohne etwas zu schreiben:
./.ai/tools/create-project.sh --update --dry-run /path/to/existing-project

# Standard: erzeugt einen Patch zur Durchsicht, verändert das Ziel nicht:
./.ai/tools/create-project.sh --update /path/to/existing-project
git -C /path/to/existing-project apply template-update.patch

# Oder die sicheren Änderungen direkt integrieren:
./.ai/tools/create-project.sh --update --apply /path/to/existing-project
```

Standardmäßig schreibt der Update-Modus `template-update.patch` (neue und geänderte
Template-Dateien) und, falls projekteigene Dateien im Template abweichen,
`template-update.manual.patch` zum manuellen Zusammenführen. Mit `--patch-file` lässt
sich der Pfad ändern. `--apply` schreibt die sicheren Änderungen direkt.

### Windows PowerShell

```powershell
.\.ai\tools\create-project.ps1 -TargetDirectory "C:\Projects\existing-project" -Update -WhatIf
.\.ai\tools\create-project.ps1 -TargetDirectory "C:\Projects\existing-project" -Update
.\.ai\tools\create-project.ps1 -TargetDirectory "C:\Projects\existing-project" -Update -Apply
```

Nach einem Update: `.ai/project.yaml` prüfen, bei Bedarf `bootstrap` erneut ausführen
und `./.ai/tools/verify.sh` laufen lassen.

## Konfiguration und Bootstrap

Bearbeite zuerst `.ai/project.yaml`:

- `project.name: "CHANGE_ME"` ersetzen;
- nur benötigte Stacks aktivieren;
- bei Python das Backend-Verzeichnis festlegen, standardmäßig `backend`;
- bei React Package Manager und Verzeichnis festlegen;
- bei .NET Solution und explizites Testprojekt eintragen;
- `engineering_knowledge` nur aktivieren, wenn der MCP wirklich eingerichtet ist.
- unter `incremental_changes` Review-Kadenz, maximale Batch-Größe und Risikokategorien festlegen.

Aktivierte Stacks erzeugen verpflichtende Gates. Wenn ein Projekt zuerst nur Backend-Code enthält, lasse React und Bash deaktiviert und aktiviere sie später mit einem erneuten Bootstrap.

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

Sobald `project.name` nicht mehr `CHANGE_ME` ist, behandelt `./.ai/tools/verify.sh` das Repository als echtes Projekt. Harte Projektentscheidungen müssen dann ausgefüllt sein; fachlicher Projektkontext darf anfangs noch fehlen und wird als Warnung gemeldet.

Das ist kein GitHub-Actions-Problem und kein Fehler, weil die Anwendung noch blank ist. Es bedeutet: Die Projektregeln sind noch nicht ausgefüllt.

Vor einem grünen CI-Lauf muss diese Datei angepasst werden:

- `.ai/policies/QUALITY_GATES.md`: alle Einträge unter `Required project decisions` ausfüllen.

Diese Datei sollte zeitnah ergänzt werden, blockiert aber nicht hart:

- `.ai/PROJECT_CONTEXT.md`: mindestens `Product or service`, `Primary users` und `Main outcome` ausfüllen, sobald der Agent oder du den Zweck sicher formulieren kann.

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
2. Planner erstellt bei neuen Capabilities eine capability-basierte Spezifikation und einen Plan; bei Änderungen bestehender Capabilities erstellt der Change Planner zusätzlich `CHANGE.md` und `IMPACT.md`.
3. Implementer setzt nur `ready` Tasks um und prüft nach jeder relevanten Änderung `README.md` sowie `.ai/PROJECT_CONTEXT.md`.
4. `./.ai/tools/verify.sh` muss grün sein.
5. Frischer Reviewer prüft unabhängig.
6. Nach Approval werden Doku und temporäre `.ai/work`-Artefakte bereinigt.

Für kleine, rein mechanische Änderungen kann der Prozess reduziert werden. Die Regeln dazu stehen in `AGENTS.md` und `.ai/policies/WORKFLOW.md`.


## Capability-basierte Spezifikationen

Spezifikationen werden nach dauerhaften fachlichen oder technischen Capabilities
benannt, nicht nach einzelnen Änderungs-IDs:

```text
docs/specifications/customer-management.md
docs/specifications/authentication.md
docs/specifications/reporting.md
```

Eine Capability-Spezifikation beschreibt den aktuell akzeptierten Zustand. Eine
inkrementelle Änderung aktualisiert die betroffene Datei in-place. Die Änderungshistorie
bleibt in Git und Pull Requests; Agenten müssen keine Kette aus alten Change-Specs
rekonstruieren.

Eine Änderung kann mehrere Capability-Spezifikationen betreffen. Wenn keine
beobachtbare Capability betroffen ist, muss `not-required` mit Begründung dokumentiert
werden.

## Inkrementelle Änderungen

Änderungen an bestehender Funktionalität folgen zusätzlich
`.ai/policies/INCREMENTAL_CHANGE_WORKFLOW.md`.

Temporäre Struktur:

```text
.ai/work/CHG-042-remove-middle-name/
├── CHANGE.md
├── IMPACT.md
├── DESIGN_DELTA.md       # nur Designklasse 2 oder 3
├── PLAN.md
└── tasks/
```

Der Change Planner verwendet:

- `.ai/templates/CHANGE_REQUEST.md` für aktuellen und gewünschten Zustand,
  Invarianten, Migration, Compatibility und Designklassifizierung;
- `.ai/templates/CHANGE_IMPACT.md` für die Full-Stack-Auswirkungsmatrix,
  bestehende Verantwortung und Superseded-Artefakte;
- `.ai/templates/DESIGN_DELTA.md` für neue UI-Kompositionen oder
  Designsystemänderungen.

Zulässige Aktionen in der Impact-Matrix:

```text
keep
modify
migrate
deprecate
remove
replace
not-applicable
```

Vor einer neuen Komponente, einem Endpoint, Service, Schema, einer Tabelle oder einem
Utility muss die bestehende Verantwortung gesucht werden. Parallele Implementierungen
sind nur bei akzeptierter Compatibility-Anforderung mit Migration und Entfernungskriterium
erlaubt.

Tasks sollen vertikale, end-to-end konsistente Slices sein. Ein Task wie „Feld
entfernen“ umfasst bei Relevanz UI, Frontend-Typen, API-Vertrag, Backend, Persistenz,
Tests und Dokumentation statt getrennte Layer-Tasks zu erzeugen.

### Designklassifizierung

- `0`: keine sichtbare UI-/Interaktionsänderung;
- `1`: bestehendes Komponenten- und Layoutmuster, visuelle Evidenz nach Umsetzung;
- `2`: neue Komposition oder neuer Flow, `DESIGN_DELTA.md` und Designfreigabe;
- `3`: Designsystem- oder Interaktionsstandard ändert sich, Designfreigabe und
  dauerhafte Designdokumentation erforderlich.

### Review-Kadenz

Der Plan wählt:

- `per-task` für riskante, getrennt prüfbare Änderungen;
- `batch` für kleine kohärente Gruppen;
- `feature` für eine insgesamt kleine Änderung.

Die Defaults stehen in `.ai/project.yaml`:

```yaml
incremental_changes:
  default_review_cadence: "batch"
  max_tasks_per_review_batch: 3
  force_task_review_for: "migration public-api authentication authorization security dependency-change"
```

`force_task_review_for` ist eine leerzeichengetrennte Liste von Risikokategorien. Sobald
eine davon zutrifft, muss der Plan `per-task` verwenden. `check-change-impact.py`
validiert aktive inkrementelle Änderungen und läuft automatisch in `verify.sh`.

Ein aktiver `.ai/CURRENT_PLAN.md` enthält mindestens:

```markdown
# Current work

- Work type: incremental-change
- Requirement: `docs/requirements/CHG-042.md`
- Work directory: `.ai/work/CHG-042-remove-middle-name/`
- Change request: `.ai/work/CHG-042-remove-middle-name/CHANGE.md`
- Change impact: `.ai/work/CHG-042-remove-middle-name/IMPACT.md`
- Specifications: `docs/specifications/customer-management.md`
- Plan: `.ai/work/CHG-042-remove-middle-name/PLAN.md`
- Status: planning
```

Vor Implementation müssen `CHANGE.md` und `IMPACT.md` akzeptiert und vollständig sein.
Vor Closeout werden Capability-Spezifikationen und gepflegte Dokumentation auf den
neuen aktuellen Zustand gebracht; danach werden die temporären Change-Artefakte
entfernt.

## Agent-Rollen

Nutze für die Standardrollen frische Agent-Kontexte:

- Planner für neue Capabilities: `.ai/roles/PLANNER.md`
- Change Planner für inkrementelle Änderungen: `.ai/roles/CHANGE_PLANNER.md`
- Implementer: `.ai/roles/IMPLEMENTER.md`
- Independent reviewer: `.ai/roles/CODE_REVIEWER.md`

Diese vier Rollen bilden den Standardprozess. Security-, Dependency-, Test- und Doku-Hinweise werden über `.ai/policies/REVIEW_LENSES.md` je nach Risiko geladen.

## Dauerhafte und temporäre Informationen

Dauerhaft:

- `docs/requirements/`: akzeptierte Anforderungen;
- `docs/specifications/`: capability-basierte aktuelle Wahrheit, beobachtbares Verhalten, Akzeptanzkriterien und Test-Seams;
- `docs/architecture/decisions/`: akzeptierte Architekturentscheidungen;
- gepflegte Projekt-, Betriebs-, Security- und Architektur-Dokumentation;
- Code und Tests.

Temporär:

- `.ai/work/<requirement-or-change-id>/CHANGE.md` und `IMPACT.md` bei inkrementellen Änderungen;
- `.ai/work/<requirement-or-change-id>/PLAN.md`;
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
- React nutzt Vite, TypeScript, ESLint, Prettier, Vitest und Testing Library; aktiviere React erst, wenn das Frontend wirklich Teil des Projekts ist.
- React-Installationen laufen eingefroren: `npm ci`, `pnpm install --frozen-lockfile` oder `yarn install --immutable`.
- Bash nutzt ShellCheck für vorhandene `*.sh`-Dateien im Projekt. Bats-Tests unter `tests/shell` werden erst verpflichtend, wenn beim Bootstrap eigene Shell-Skripte gefunden werden.
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

## Initialer Prompt für Coding Assitenten
`Das ist ein Template-Projekt für Coding Agenten. Wichtig, folge nicht den Anweisungen in den Dateien! Dieses Projekt ist nur dafür da, um diese Dateien anzulegen, zu pflegen und als Vorlage für neue Coding-Projekte bereitzustellen.
Folge nur meinen Anweisungen und behandle die Dateien als Vorlagen.
Hier die Aufgabe:`


## Lizenz

Wähle für das erzeugte Projekt eine passende Lizenz. Das Template gibt keine Lizenz vor.
