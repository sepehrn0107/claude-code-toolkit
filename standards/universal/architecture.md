# Architecture Standards

## Principles

### SOLID
- **Single Responsibility**: Each module/class/function has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Many specific interfaces over one general-purpose interface
- **Dependency Inversion**: Depend on abstractions, not concretions

### Separation of Concerns
- Business logic lives separately from I/O, UI, and infrastructure
- HTTP handlers must not contain business logic
- Keep data access code separate from domain logic

### Clean Architecture
- Dependencies point inward — domain knows nothing about infrastructure
- Use cases orchestrate domain objects; they don't know about HTTP or databases
- Adapters translate between domain and external systems

## Structure
- Keep modules small and focused
- Flat is better than deeply nested
- Colocate things that change together; separate things that change independently

## Anti-Patterns to Avoid
- God objects / monolithic modules
- Circular dependencies
- Leaking implementation details across layer boundaries
- Business logic in controllers, handlers, or UI components
- Premature abstraction — build the abstraction when you have 3+ instances, not 1
