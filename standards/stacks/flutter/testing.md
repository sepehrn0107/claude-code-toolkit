# Testing Standards

## Test Pyramid
Flutter has three test layers — use all three:
1. **Unit tests** — pure Dart logic, ViewModels, repositories, utilities
2. **Widget tests** — individual widgets in isolation using `WidgetTester`
3. **Integration tests** — full app flows on a real device/emulator via `integration_test`

Aim for the majority of coverage at unit and widget level; integration tests are slow and reserved for critical user journeys.

## File Organization
Mirror `lib/` structure under `test/`:
```
lib/features/auth/login_viewmodel.dart
test/features/auth/login_viewmodel_test.dart
test/features/auth/login_screen_test.dart
```

## Unit Tests
- Test one behavior per test; use descriptive names that read as a sentence:
  ```dart
  test('returns error state when credentials are invalid', () { ... });
  ```
- Use `mockito` or `mocktail` for dependency mocking — do not hit real network or DB in unit tests
- Group related tests with `group()`:
  ```dart
  group('LoginViewModel', () {
    test('emits loading then success on valid login', () { ... });
    test('emits error on network failure', () { ... });
  });
  ```

## Widget Tests
- Use `WidgetTester.pumpWidget()` with a minimal widget tree (wrap in `MaterialApp` if needed)
- Pump frames explicitly: `await tester.pump()` after triggering state changes; use `await tester.pumpAndSettle()` to wait for animations
- Find widgets with semantic finders when possible (`find.text`, `find.byType`, `find.byKey`) — avoid `find.byIndex`
- Assign `Key` values to widgets only when needed for testing or disambiguation, not by default
- Mock providers and services — widget tests should not depend on real network calls:
  ```dart
  testWidgets('shows error message on login failure', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [authServiceProvider.overrideWith((_) => FakeAuthService())],
        child: const MaterialApp(home: LoginScreen()),
      ),
    );
    await tester.tap(find.byType(ElevatedButton));
    await tester.pumpAndSettle();
    expect(find.text('Invalid credentials'), findsOneWidget);
  });
  ```

## Integration Tests
- Place in `integration_test/` directory
- Use `IntegrationTestWidgetsFlutterBinding.ensureInitialized()` at test entry point
- Test complete user journeys, not individual widget behavior
- Profile performance via `flutter drive --profile` + `traceAction()` to capture timeline data

## Performance Testing
- Use `flutter test --profile` + `LiveWidgetController.traceAction()` to measure frame build times in widget tests
- Assert frame timing where performance is critical:
  ```dart
  final frameTimings = await tester.traceAction(() async {
    await tester.fling(find.byType(ListView), const Offset(0, -300), 500);
    await tester.pumpAndSettle();
  });
  expect(frameTimings.summaryJson['worst_frame_rasterizer_time_millis'], lessThan(16));
  ```

## Coverage
- Run `flutter test --coverage` and view with `lcov`
- Do not target 100% coverage mechanically — target meaningful coverage of business logic and error paths
- Untested code that's genuinely trivial (generated code, `main.dart` bootstrapping) may be excluded
