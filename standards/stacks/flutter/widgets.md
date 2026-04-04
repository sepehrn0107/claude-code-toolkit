# Widget Standards

## Structure
- Prefer `StatelessWidget` over `StatefulWidget` — only add state when the widget owns mutable UI state
- One widget per file; filename matches class name in `snake_case` (e.g., `user_card.dart` for `UserCard`)
- Colocate a widget, its helpers, and its tests in the same feature folder

## Composition
- Extract repeated widget subtrees into a named `StatelessWidget`, not a helper function that returns a widget
  - Functions that return widgets skip Flutter's element-reuse optimization and break `const` caching
- Keep `build()` methods focused: if a method exceeds ~60 lines, split into sub-widgets
- Compose small, single-purpose widgets rather than building one large widget with many branches

## const Constructors
- Use `const` constructors on every widget that supports it — Flutter short-circuits rebuilds for `const` instances
- Enable `flutter_lints` to get automated reminders; treat the `prefer_const_constructors` lint as an error

## setState Locality
- Call `setState()` as deep in the tree as possible — only the subtree rooted at that `State` rebuilds
- Never call `setState()` high in the tree for a change that only affects a leaf widget
- If you find yourself passing state callbacks through many levels, consider extracting state into a provider or `InheritedWidget`

## Stateful Widget Patterns
- Initialize controllers, animations, and subscriptions in `initState()`; dispose them in `dispose()`
- Never access `BuildContext` across async gaps without checking `mounted` first:
  ```dart
  if (!mounted) return;
  setState(() { ... });
  ```

## Responsibilities
- Widgets handle presentation and event wiring only — no business logic
- Business logic belongs in a ViewModel, Notifier, Bloc, or service class
- Data fetching does not belong in `build()` — trigger it in `initState()` or via a state management solution
