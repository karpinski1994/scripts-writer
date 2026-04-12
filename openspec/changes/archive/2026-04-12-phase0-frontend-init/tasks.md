## 1. Next.js Initialization

- [x] 1.1 Initialize frontend with `npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --use-npm` (accept defaults for other prompts)
- [x] 1.2 Verify: `npm run dev` starts, blank page renders at `localhost:3000`
- [x] 1.3 Verify: `frontend/src/app/layout.tsx` and `frontend/src/app/page.tsx` exist

## 2. Frontend Dependencies

- [x] 2.1 Install dependencies: `npm install @tanstack/react-query zustand react-hook-form @hookform/resolvers zod react-markdown lucide-react`
- [x] 2.2 Verify: `npm ls @tanstack/react-query zustand` shows both installed

## 3. Shadcn/UI Setup

- [x] 3.1 Initialize Shadcn/UI: `npx shadcn@latest init` (New York style, Zinc theme, CSS variables, TypeScript)
- [x] 3.2 Verify: `npx shadcn@latest add button` works, button component created and renders

## 4. Linter & Formatter

- [x] 4.1 Install dev dependencies: `npm install -D prettier eslint-config-prettier`
- [x] 4.2 Create `.prettierrc` config file with: semi=true, singleQuote=false, tabWidth=2, trailingComma="es5", printWidth=120
- [x] 4.3 Add `eslint-config-prettier` to `extends` in ESLint config
- [x] 4.4 Add format script to `package.json`: `"format": "prettier --write ."`
- [x] 4.5 Verify: `npm run lint` passes with no errors
