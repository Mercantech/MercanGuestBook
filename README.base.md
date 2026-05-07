## Hvad går det ud på?
Hver elev laver en Pull Request (PR), der **tilføjer én personlig signatur** til gæstebogen.

- **1 PR = 1 elev = 1 fil** i `entries/`
- PR’en må først merges når **3 andre elever** har godkendt
- Signaturen skal indeholde:
  - **GitHub** (link)
  - **Website** (link)
  - **Quote** (citat)

## Sådan laver du din PR (elev-guide)
1. Lav en ny branch.
2. Kopiér skabelonen `entries/_template.md` til din egen fil:
   - Filnavn: `entries/<dit-github-handle>.md`
3. Udfyld felterne (GitHub, Website, Quote).
4. Commit og push, og opret en PR.
5. Få **3 andre elever** til at godkende PR’en.

## Regler (CI/validering)
Repo’et har en automatisk validering, der afviser PRs som ikke følger reglerne:
- PR’en må kun ændre filer i `entries/` og `README.md` (som genereres automatisk)
- PR’en skal ændre **præcis én** entry-fil (din egen)
- `entries/_template.md` må ikke ændres
- Din entry skal indeholde linjer i dette format:
  - `- **GitHub**: https://github.com/<handle>`
  - `- **Website**: https://<din-hjemmeside>`
  - `- **Quote**: "<dit-citat>"`

<!-- GUESTBOOK_INDEX_START -->
<!-- GUESTBOOK_INDEX_END -->

## GitHub Branch Protection (lærer/maintainers)
Dette sættes i GitHub (UI) på default-branchen (fx `main`):
- Slå “Require a pull request before merging” til
- Sæt **Required approvals = 3**
- (Anbefalet) Slå “Require status checks to pass” til og vælg **Validate guestbook entry**
- (Valgfrit) Slå “Require review from Code Owners” til

> Tip: Hvis I ikke vil have at `@MAGS-GH` er code owner, så ret `.github/CODEOWNERS` til jeres lærer/maintainers (eller et GitHub-team).

