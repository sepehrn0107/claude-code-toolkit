# Naming Conventions

## Files and Directories
- All file names: `snake_case.dart` — matches Dart package convention
- One public class/widget per file; file name matches the class in snake_case
  - `UserProfileCard` → `user_profile_card.dart`
- Group by feature, not by type:
  ```
  lib/
    features/
      auth/
        login_screen.dart
        login_viewmodel.dart
        login_screen_test.dart   (or in test/ mirroring lib/)
      home/
        home_screen.dart
  ```

## Classes and Types
- `PascalCase` for all classes, enums, typedefs, and extension names
- Widget classes end with a descriptive noun (no `Widget` suffix needed): `UserCard`, `PriceTag`, `LoadingOverlay`
- Abstract base classes: prefix with nothing — just descriptive naming (e.g., `Repository`, `DataSource`)
- Mixins: `PascalCase`, often adjective-like (`Serializable`, `Disposable`)

## Variables, Parameters, and Fields
- `camelCase` for all local variables, parameters, and instance fields
- Private fields: prefix with `_` → `_controller`, `_isLoading`
- Boolean fields and parameters: use `is`, `has`, `can`, `should` prefix → `isLoading`, `hasError`, `canSubmit`
- Do not abbreviate unless universally understood (`ctx` → use `context`, `btn` → use `button`)

## Functions and Methods
- `camelCase` verbs: `fetchUser()`, `onTap()`, `handleSubmit()`
- Event callbacks: prefix with `on` → `onPressed`, `onChanged`, `onDismissed`
- Async methods: name reflects the result, not the async-ness (`fetchUser`, not `getUserAsync`)

## Constants
- Top-level and static constants: `camelCase` (Dart convention, not `SCREAMING_SNAKE_CASE`)
  ```dart
  const double defaultPadding = 16.0;
  const Duration animationDuration = Duration(milliseconds: 300);
  ```
- Enum values: `camelCase`
  ```dart
  enum AuthStatus { unauthenticated, loading, authenticated, error }
  ```

## Widgets
- Screen-level widgets: suffix with `Screen` or `Page` → `LoginScreen`, `HomeScreen`
- Dialog widgets: suffix with `Dialog` → `ConfirmDeleteDialog`
- Bottom sheets: suffix with `Sheet` → `FilterSheet`
- Reusable components: descriptive noun only → `AvatarCircle`, `TagChip`

## State and Providers
- Riverpod providers: suffix with `Provider` or `Notifier` → `authProvider`, `cartNotifier`
- Bloc classes: `AuthBloc`, `AuthEvent`, `AuthState`
- ViewModel classes: suffix with `ViewModel` → `LoginViewModel`
