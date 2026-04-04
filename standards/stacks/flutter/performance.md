# Performance Standards

> Source: https://docs.flutter.dev/perf/best-practices (Flutter 3.41.5, 2025-11-23)

## Frame Budget
- Target 16ms total per frame on 60Hz displays (8ms build + 8ms render)
- On 120Hz devices, target 8ms total — design with this in mind from the start
- Profile in **profile mode** (`flutter run --profile`), never in debug mode
- Use the **DevTools Performance view** to identify jank; enable **Show widget rebuild information** in the Flutter plugin

## Control build() Cost
- Avoid repetitive or expensive work inside `build()` — it runs on every ancestor rebuild
- Never do I/O, network calls, or heavy computation in `build()`
- Use `const` constructors everywhere possible — Flutter skips rebuilds for identical `const` instances
- Localize `setState()` to the smallest subtree that actually changes
- Pass pre-built subtrees (built outside the animation loop) as `child` parameters to avoid rebuilding them on every animation tick:
  ```dart
  // Bad: subtree rebuilt every animation frame
  AnimatedBuilder(
    animation: _controller,
    builder: (context, _) => Column(children: [
      HeavySubtree(),       // rebuilt every tick
      AnimatedPart(_controller.value),
    ]),
  );

  // Good: HeavySubtree built once, passed as child
  AnimatedBuilder(
    animation: _controller,
    child: HeavySubtree(),  // built once
    builder: (context, child) => Column(children: [
      child!,
      AnimatedPart(_controller.value),
    ]),
  );
  ```

## Lazy Lists and Grids
- Always use lazy builder constructors for long lists: `ListView.builder`, `GridView.builder`, `SliverList.builder`
- Never use `ListView(children: [...])` or `Column(children: [...])` when most items are off-screen — all children are built immediately
- For paginated data, build items only as they scroll into view

## Avoid Expensive Rendering Operations
### Opacity
- Avoid the `Opacity` widget in animations — use `AnimatedOpacity` or `FadeInImage` instead
- For static semi-transparent shapes or text with no overlapping parts, use a semitransparent color directly rather than wrapping in `Opacity`
- For fading images, use `FadeInImage` (uses GPU fragment shader, avoids offscreen buffers)

### saveLayer
- `saveLayer()` allocates an offscreen buffer and forces a GPU render-target switch — use sparingly
- Widgets that implicitly call `saveLayer()`: `ShaderMask`, `ColorFilter`, `Chip` (when `disabledColorAlpha != 0xff`), `Text` (when `overflowShader` is set)
- For static overlapping transparent shapes: pre-calculate and cache the composited image rather than using `saveLayer()` at runtime
- Check `saveLayer` call frequency via `PerformanceOverlayLayer.checkerboardOffscreenLayers` in DevTools

### Clipping
- Clipping is costly — use `borderRadius` on widget properties instead of `ClipRRect` wherever possible
- Default is `Clip.none`; only enable clipping explicitly when needed
- Never use `Clip.antiAliasWithSaveLayer` unless absolutely required (it calls `saveLayer()`)

## Intrinsic Layout Passes
- Avoid `IntrinsicWidth` / `IntrinsicHeight` in grids and lists — they trigger a second layout pass over all cells (including off-screen ones)
- Fix cell sizes up front, or anchor one cell and lay out others relative to it with a custom `RenderObject`
- Debug with **Track Layouts** in DevTools; look for `$runtimeType intrinsics` events in the timeline

## String Building
- Use `StringBuffer` for multi-part string construction (especially in loops) — avoid `+` concatenation which allocates a new `String` per operation:
  ```dart
  // Bad
  String result = '';
  for (final item in items) {
    result += item.toString();
  }

  // Good
  final buffer = StringBuffer();
  for (final item in items) {
    buffer.write(item.toString());
  }
  final result = buffer.toString();
  ```

## operator == Pitfall
- Do NOT override `operator ==` on `Widget` subclasses — it causes O(N²) comparisons across the tree and prevents compiler static dispatch optimization
- Exception: leaf widgets (no children) where property comparison is substantially cheaper than rebuilding and where the widget rarely changes — but even then, prefer widget caching

## Battery and Thermal
- Rendering well under 16ms is still worthwhile: reduces battery drain and thermal load even when visually imperceptible
- Always test on the lowest-spec device you target, not just your dev device
