# Python + PyTorch Standards

Standards for projects using PyTorch for ML model training and inference.

## Inference Stage Checklist

Every class that wraps a PyTorch model behind a Stage/adapter interface must satisfy all of the following:

### 1. `torch.load()` — always use `weights_only=True`

```python
# ❌ security risk — arbitrary code execution via pickle
state = torch.load(path, map_location="cpu")

# ✅ correct
state = torch.load(path, map_location="cpu", weights_only=True)
```

### 2. Lazy model initialization — always use `threading.Lock`

Any `_infer` or `_model` attribute initialized on first call (not in `__init__`) must be guarded by a lock to prevent check-then-act races in multi-threaded servers.

```python
import threading

class MyStage:
    def __init__(self, weights_path):
        self._weights_path = weights_path
        self._infer: MyInfer | None = None
        self._lock = threading.Lock()

    def _get_infer(self) -> MyInfer:
        with self._lock:
            if self._infer is None:
                self._infer = MyInfer(self._weights_path)
        return self._infer

    def run(self, image, ctx):
        infer = self._get_infer()
        # ...
```

### 3. Class-level model caches — protect with a class-level lock

```python
class MyInfer:
    _models: dict = {}
    _models_lock = threading.Lock()

    @classmethod
    def _load(cls, path):
        with cls._models_lock:
            if path not in cls._models:
                cls._models[path] = _load_model(path)
            return cls._models[path]
```

### 4. `@torch.inference_mode()` — use as decorator, not context manager

```python
# ❌ verbose, can be forgotten mid-refactor
def predict(self, x):
    with torch.no_grad():
        return self._model(x)

# ✅ decorator form — applies to entire method body, slightly faster than no_grad
@torch.inference_mode()
def predict(self, x):
    return self._model(x)
```

`torch.inference_mode()` is a strict superset of `torch.no_grad()` — it additionally disables version counting and is preferred for all inference paths.

### 5. Numpy conversion — always `.detach()` before `.cpu().numpy()`

Non-leaf tensors (those created by operations) require `.detach()` before `.numpy()`:

```python
# ❌ crashes on non-leaf tensors
out = model(x).cpu().numpy()

# ✅ always safe
out = model(x).detach().cpu().numpy()
```

### 6. Return `.copy()` from numpy arrays to avoid mutable aliasing

When returning a numpy array that was derived from an internal buffer, return a copy:

```python
# ❌ caller can mutate the internal buffer
return self._cache[key]

# ✅ safe — caller gets an independent array
return self._cache[key].copy()
```

---

## Training Checklist

- Use `torch.no_grad()` (context manager) in validation loops — `@torch.inference_mode()` is for inference-only code
- Always call `model.eval()` before evaluation, `model.train()` before training loop
- Use `loss.item()` not `float(loss)` to avoid unnecessary tensor retain
- Log to W&B / MLflow from the start — retrofitting logging after training is painful

---

## Model Serialization

```python
# Save — state dict only, not the full model
torch.save(model.state_dict(), path)

# Load — weights_only=True, strict=True by default
state = torch.load(path, map_location="cpu", weights_only=True)
model.load_state_dict(state)
model.eval()
```

Never `torch.save(model)` (full pickle) for deployment artifacts.
