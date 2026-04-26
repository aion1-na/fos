# Studio

Studio is a Next.js 14 app-router application under `apps/studio`.

## Stages

The nine routes are `/studio/frame`, `/studio/compose`, `/studio/evidence`, `/studio/population`, `/studio/configure`, `/studio/execute`, `/studio/validate`, `/studio/explore`, and `/studio/brief`.

The stage rail is keyboard reachable, exposes `aria-current`, and uses `useStageStatus()` for status dots.

## Accessibility

WCAG 2.1 AA is enforced by static CI checks and Cypress axe smoke specs. Every stage has a main landmark, H1, rail navigation, focus-visible styling, and a skip link to the workspace.

Run:

```sh
uv run pytest tests/test_studio_accessibility.py -v
pnpm --filter @fw/studio test
```
