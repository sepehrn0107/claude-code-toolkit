toolbox/
├── CLAUDE.md # Toolbox identity + how to use it
├── memory/ # Your global persistent memory (already exists)
│ ├── MEMORY.md
│ └── \*.md
│
├── standards/ # Layer 2 — stack standards
│ ├── universal/ # Applies to every project regardless of stack
│ │ ├── architecture.md # SOLID, separation of concerns, clean arch
│ │ ├── security.md # OWASP, secrets, input validation
│ │ ├── git.md # commit conventions, branching strategy
│ │ ├── testing.md # test pyramid, coverage expectations
│ │ └── documentation.md # what to document and how
│ │
│ └── stacks/ # Discovered or chosen per project
│ ├── typescript-react/
│ ├── python-fastapi/
│ ├── go/
│ └── ... # Grows as you work with new stacks
│
├── templates/ # Scaffolding templates
│ ├── CLAUDE.md.template # Base project CLAUDE.md
│ ├── memory/ # Starter memory files for new projects
│ └── pipeline/ # CI/CD templates per platform
│ ├── github-actions/
│ └── ...
│
└── skills/ # Custom lifecycle skills (Layer 1 additions)
├── new-project.md
├── add-feature.md
├── standards-check.md
└── retrospective.md
