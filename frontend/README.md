# Business Reports — Frontend

React + TypeScript + Vite + Tailwind CSS. Talks to the FastAPI backend in
`../backend/` over `/api/*` (proxied in dev by `vite.config.ts`, and by the
Cloudflare Worker in `../worker/` in production).

```bash
npm install
npm run dev      # http://localhost:5173, expects the backend on :8000
npm run build    # outputs dist/, consumed by ../worker
```

See `../DEPLOYMENT.md` for the full deployment flow.

## Design system

Dashboard UI built on shadcn/ui conventions: owned component code (no runtime
component dependency) over Radix primitives, styled with Tailwind.

- `src/index.css` defines the full token set as HSL CSS variables, with a
  `.dark` block overriding them. Components only ever reference semantic
  tokens (`bg-background`, `text-muted-foreground`, `border-border`), never
  raw colors, so light and dark stay in sync automatically.
- `src/components/ui/` holds the primitives (`Button`, `Card`, `Badge`,
  `Tabs`, `Alert`, `Skeleton`). Each is a deep module: a small prop surface
  (`variant`, `size`) hiding all styling, state, and accessibility details.
- `src/lib/theme.tsx` owns theme state (system preference + persisted
  override) behind a `useTheme()` hook. `index.html` applies the stored
  theme before paint to avoid a flash of the wrong theme.
- `src/lib/utils.ts` exports `cn()` for conditional class merging.
- Icons come from `@phosphor-icons/react`. Do not hand-roll SVG icons.
