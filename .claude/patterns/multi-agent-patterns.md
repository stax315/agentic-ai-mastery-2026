# Multi-Agent Patterns

Patterns for coordinating multiple agents. Use when building systems with sub-agents.

---

## Architecture: Coordinator vs Implementer

| Aspect | Implementer Agent | Coordinator Agent |
|--------|-------------------|-------------------|
| **Role** | Does the work | Routes to workers |
| **Operations** | Implements logic | Delegates to sub-agents |
| **Has sub-agents** | No | Yes |
| **Primary job** | Execute operations | Route to correct agent |
| **Error source** | Self only | Self + sub-agents |
| **Validation** | Input values | Operation names |
| **Testing focus** | Edge cases | Integration |

---

## Pattern 18: Agent Composition
```python
class CoordinatorAgent:
    def __init__(self) -> None:
        self.version = "1.0"
        # COMPOSITION: Create sub-agent instances
        self.string_agent = StringAgent()
        self.datetime_agent = DateTimeAgent()
        # Build routing registry
        self._operations = self._build_operation_registry()

# Coordinator OWNS sub-agents
# Sub-agents created in __init__ - always available
# Registry maps user-friendly names to internal methods
```

## Pattern 19: Operation Registry for Routing
```python
def _build_operation_registry(self) -> dict:
    """Map operation names to (agent, method_name) tuples."""
    return {
        # User-friendly name → (agent instance, internal method name)
        "reverse": (self.string_agent, "reverse_string"),
        "uppercase": (self.string_agent, "to_uppercase"),
        "add_days": (self.datetime_agent, "add_days"),
        "current_time": (self.datetime_agent, "get_current_time"),
    }

# Why registry pattern:
# - Explicit routing - no magic, no ambiguity
# - Easy to extend - add one line per new operation
# - Testable - deterministic behavior
# - Discoverable - list_operations() for introspection
```

## Pattern 20: Execute with Registry Lookup
```python
def execute(self, operation: str, *args, **kwargs):
    """Route operation to appropriate sub-agent."""
    self._validate_operation(operation)       # Validate first
    agent, method_name = self._operations[operation]  # Lookup
    method = getattr(agent, method_name)      # Get method
    return method(*args, **kwargs)            # Execute (errors propagate)

# Example flow:
# execute("reverse", "hello")
# → lookup: "reverse" → (string_agent, "reverse_string")
# → call: string_agent.reverse_string("hello")
# → return: "olleh"
```

## Pattern 21: Error Propagation in Multi-Agent
```python
# Let sub-agent errors propagate AS-IS - don't wrap them
return method(*args, **kwargs)  # If sub-agent raises, it propagates

# Why propagate (not wrap):
# - Sub-agents already have context-rich error messages
# - Wrapping loses specificity ("Cannot parse date" vs "UtilityAgent error")
# - Simpler code = fewer bugs
# - Consistent with Python exception handling
```

## Pattern 22: Coordinator Validation with Discovery
```python
def _validate_operation(self, operation) -> None:
    """Validate operation, include available options in error."""
    if operation is None:
        raise ValueError("operation cannot be None")
    if operation not in self._operations:
        available = ", ".join(sorted(self._operations.keys()))
        raise ValueError(f"Unknown operation: '{operation}'. Available: {available}")

# Include available operations in error message:
# - Helps users discover valid operations
# - Makes typos obvious
# - Self-documenting errors
```

## Pattern 23: Discovery Helper Method
```python
def list_operations(self) -> list:
    """Return sorted list of available operation names."""
    return sorted(self._operations.keys())

# Why include this:
# - Discoverability - users can see what's available
# - Supports error messages ("Available: ...")
# - Enables introspection and documentation
# - Easy to test (assert len(ops) == 10)
```

---

## V2 Enhancement Patterns

### Pattern 24: Alias Resolution Layer
```python
def _build_alias_registry(self) -> dict:
    """Map aliases to canonical operation names."""
    return {
        "rev": "reverse",
        "upper": "uppercase",
        "now": "current_time",
        "plus": "add",
    }

def _resolve_alias(self, operation: str) -> str:
    """Resolve alias to canonical name, or return as-is."""
    return self._aliases.get(operation, operation)

# Usage in execute():
operation = self._resolve_alias(operation)  # BEFORE validation!

# Why separate from operations registry:
# - Aliases are shortcuts, not new operations
# - One canonical name in error messages
# - Easy to add/remove aliases without touching core
# - Users can discover aliases separately
```

### Pattern 25: Self-Documenting API
```python
def _build_descriptions(self) -> dict:
    """Human-readable descriptions for each operation."""
    return {
        "reverse": "Reverses a string. Args: (text)",
        "add_days": "Adds days to a date. Args: (date_str, days)",
        "add": "Adds two numbers. Args: (a, b)",
    }

def describe(self, operation: str) -> str:
    """Return description of what an operation does."""
    resolved = self._resolve_alias(operation)
    self._validate_operation(resolved)
    return self._descriptions[resolved]
```

### Pattern 26: Typo Suggestions in Errors
```python
def _find_similar(self, typo: str) -> str | None:
    """Find operation name similar to typo using prefix matching."""
    if len(typo) < 2:
        return None

    typo_lower = typo.lower()
    best_match, best_score = None, 0

    all_names = list(self._operations.keys()) + list(self._aliases.keys())
    for name in all_names:
        common = 0
        for i in range(min(len(typo_lower), len(name))):
            if typo_lower[i] == name[i]:
                common += 1
            else:
                break
        if common >= 2 and common > best_score:
            best_score, best_match = common, name

    return best_match

# In validation:
suggestion = self._find_similar(operation)
msg = f"Unknown operation: '{operation}'."
if suggestion:
    msg += f" Did you mean '{suggestion}'?"
msg += f" Available: {available}"
```

### Pattern 27: Operation Categories for Discoverability
```python
def list_operations_by_category(self) -> dict:
    """Return operations grouped by sub-agent category."""
    return {
        "string": sorted(["reverse", "uppercase", "lowercase", ...]),
        "datetime": sorted(["current_time", "add_days", ...]),
        "calculator": sorted(["add", "subtract", "multiply", ...]),
    }

# Why categories:
# - 17 operations is a lot to scan
# - Categories help users find what they need
# - Shows the multi-agent architecture
# - Supports organized help output
```

---

## Routing Strategy: Why Registry Wins

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Keyword matching | Natural language | Ambiguous, brittle | ❌ |
| Pattern detection | Automatic | Complex, still ambiguous | ❌ |
| Type parameter | Unambiguous | Verbose API | ⚠️ |
| **Operation Registry** | **Explicit, testable, extendable** | User must know names | ✅ |

---

## Error Handling in Multi-Agent Systems

| Error Type | Source | Handling |
|------------|--------|----------|
| Invalid operation | Coordinator | Raise with available list |
| Unknown operation | Coordinator | Raise with suggestions |
| Invalid arguments | Sub-agent | Propagate as-is |
| Internal error | Sub-agent | Propagate as-is |

---

## Integration Testing Strategy

Multi-agent testing requires different focus than single-agent:

| Single-Agent Tests | Multi-Agent Tests |
|-------------------|-------------------|
| Operation correctness | Routing correctness |
| Input validation | Operation validation |
| Edge cases | Error propagation |
| Return values | Integration flow |

---

## Extensibility Pattern

Adding a new sub-agent requires:
```python
# 1. Import
from new_agent import NewAgent

# 2. Initialize in __init__
self.new_agent = NewAgent()

# 3. Add to registry
"new_operation": (self.new_agent, "method_name"),

# 4. Write tests for new routes
# Effort: ~10 minutes per agent
```

---

Last updated: January 19, 2026
