## Purpose

Defines the Next.js frontend project initialization, dependency installation, Shadcn/UI setup, and linter/formatter configuration for the Scripts Writer application.

## ADDED Requirements

### Requirement: Next.js frontend project initialization
The system SHALL have a Next.js frontend project initialized under `frontend/` with App Router, TypeScript, Tailwind CSS, ESLint, and `src/` directory structure.

#### Scenario: Frontend starts and renders
- **WHEN** `npm run dev` is executed in the `frontend/` directory
- **THEN** the dev server starts at `localhost:3000` and a blank page renders in the browser

#### Scenario: Frontend uses App Router with src directory
- **WHEN** the `frontend/src/app/` directory is inspected
- **THEN** it contains `layout.tsx` and `page.tsx` files

### Requirement: Frontend dependencies installed
The system SHALL have all frontend dependencies installed: `@tanstack/react-query`, `zustand`, `react-hook-form`, `@hookform/resolvers`, `zod`, `react-markdown`, `lucide-react`.

#### Scenario: Dependencies are installed
- **WHEN** `npm ls @tanstack/react-query zustand` is executed
- **THEN** both packages are listed as installed

### Requirement: Shadcn/UI component library initialized
The system SHALL have Shadcn/UI initialized with New York style, Zinc theme, and CSS variables configuration.

#### Scenario: Shadcn/UI button component can be added
- **WHEN** `npx shadcn@latest add button` is executed
- **THEN** a button component is created in the project and renders correctly

### Requirement: ESLint and Prettier configuration
The system SHALL have ESLint and Prettier configured in `frontend/` with `eslint-config-prettier` to disable conflicting rules.

#### Scenario: Lint passes on project code
- **WHEN** `npm run lint` is executed in the `frontend/` directory
- **THEN** it completes with no errors
