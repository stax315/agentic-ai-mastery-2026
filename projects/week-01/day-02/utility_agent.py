"""
UtilityAgent v2 - A multi-agent coordinator that routes operations to sub-agents.

Day 2 of AI Mastery - Multi-agent system with enhanced UX features.

V2 Improvements:
- CalculatorAgent integration (7 new operations)
- Operation aliases (10 shortcuts)
- describe() method for self-documenting API
- "Did you mean?" suggestions for typos
- list_operations_by_category() for better discoverability

This agent doesn't implement operations itself - it coordinates StringAgent,
DateTimeAgent, and CalculatorAgent, routing requests to the appropriate sub-agent.
"""

from string_agent import StringAgent
from datetime_agent import DateTimeAgent
from calculator_agent_v2 import CalculatorAgent


class UtilityAgent:
    """Coordinator agent that routes operations to StringAgent, DateTimeAgent, or CalculatorAgent."""

    def __init__(self) -> None:
        """Initialize the UtilityAgent with sub-agents and operation registry."""
        self.version = "2.0"
        self.string_agent = StringAgent()
        self.datetime_agent = DateTimeAgent()
        self.calculator_agent = CalculatorAgent()
        self._operations = self._build_operation_registry()
        self._aliases = self._build_alias_registry()
        self._descriptions = self._build_descriptions()

    def _build_operation_registry(self) -> dict:
        """
        Build mapping of operation names to (agent, method_name) tuples.

        Returns:
            dict mapping operation name to (agent_instance, method_name)
        """
        return {
            # StringAgent operations (5)
            "reverse": (self.string_agent, "reverse_string"),
            "uppercase": (self.string_agent, "to_uppercase"),
            "lowercase": (self.string_agent, "to_lowercase"),
            "count_words": (self.string_agent, "count_words"),
            "remove_spaces": (self.string_agent, "remove_spaces"),
            # DateTimeAgent operations (5)
            "current_time": (self.datetime_agent, "get_current_time"),
            "current_date": (self.datetime_agent, "get_current_date"),
            "add_days": (self.datetime_agent, "add_days"),
            "days_between": (self.datetime_agent, "days_between"),
            "format_date": (self.datetime_agent, "format_date"),
            # CalculatorAgent operations (7) - NEW in v2
            "add": (self.calculator_agent, "add"),
            "subtract": (self.calculator_agent, "subtract"),
            "multiply": (self.calculator_agent, "multiply"),
            "divide": (self.calculator_agent, "divide"),
            "power": (self.calculator_agent, "power"),
            "modulo": (self.calculator_agent, "modulo"),
            "sqrt": (self.calculator_agent, "sqrt"),
        }

    def _build_alias_registry(self) -> dict:
        """
        Build mapping of alias names to canonical operation names.

        Returns:
            dict mapping alias to canonical operation name
        """
        return {
            # String aliases
            "rev": "reverse",
            "upper": "uppercase",
            "lower": "lowercase",
            "words": "count_words",
            # DateTime aliases
            "today": "current_date",
            "now": "current_time",
            # Calculator aliases
            "plus": "add",
            "minus": "subtract",
            "times": "multiply",
            "mod": "modulo",
        }

    def _build_descriptions(self) -> dict:
        """
        Build mapping of operation names to human-readable descriptions.

        Returns:
            dict mapping operation name to description string
        """
        return {
            # String operations
            "reverse": "Reverses a string. Args: (text)",
            "uppercase": "Converts string to uppercase. Args: (text)",
            "lowercase": "Converts string to lowercase. Args: (text)",
            "count_words": "Counts words in string. Args: (text)",
            "remove_spaces": "Removes all whitespace. Args: (text)",
            # DateTime operations
            "current_time": "Returns current time as HH:MM:SS. Args: ()",
            "current_date": "Returns current date as YYYY-MM-DD. Args: ()",
            "add_days": "Adds days to a date. Args: (date_str, days)",
            "days_between": "Days between two dates. Args: (date1, date2)",
            "format_date": "Formats date with pattern. Args: (date_str, format)",
            # Calculator operations
            "add": "Adds two numbers. Args: (a, b)",
            "subtract": "Subtracts b from a. Args: (a, b)",
            "multiply": "Multiplies two numbers. Args: (a, b)",
            "divide": "Divides a by b. Args: (a, b)",
            "power": "Raises base to exponent. Args: (base, exponent)",
            "modulo": "Returns remainder of a/b. Args: (a, b)",
            "sqrt": "Returns square root. Args: (a)",
        }

    def _resolve_alias(self, operation: str) -> str:
        """
        Resolve alias to canonical operation name.

        Args:
            operation: Operation name or alias

        Returns:
            Canonical operation name (or original if not an alias)
        """
        return self._aliases.get(operation, operation)

    def _find_similar(self, typo: str) -> str | None:
        """
        Find operation name similar to typo using prefix matching.

        Simple algorithm: longest common prefix wins.
        Returns None if no reasonable match found.

        Args:
            typo: The mistyped operation name

        Returns:
            Best matching operation/alias name, or None
        """
        if len(typo) < 2:
            return None

        typo_lower = typo.lower()
        best_match = None
        best_score = 0

        all_names = list(self._operations.keys()) + list(self._aliases.keys())
        for name in all_names:
            # Check prefix match
            common = 0
            for i in range(min(len(typo_lower), len(name))):
                if typo_lower[i] == name[i]:
                    common += 1
                else:
                    break

            if common >= 2 and common > best_score:
                best_score = common
                best_match = name

        return best_match

    def _validate_operation(self, operation) -> None:
        """
        Validate that operation is a known, non-empty string.

        Args:
            operation: The operation name to validate

        Raises:
            ValueError: If operation is None, empty, wrong type, or unknown
        """
        if operation is None:
            raise ValueError("operation cannot be None")
        if type(operation) is bool:
            raise ValueError("operation must be a string, got bool")
        if not isinstance(operation, str):
            raise ValueError(f"operation must be a string, got {type(operation).__name__}")
        if operation.strip() == "":
            raise ValueError("operation cannot be empty")
        if operation not in self._operations:
            available = ", ".join(sorted(self._operations.keys()))
            suggestion = self._find_similar(operation)
            msg = f"Unknown operation: '{operation}'."
            if suggestion:
                msg += f" Did you mean '{suggestion}'?"
            msg += f" Available: {available}"
            raise ValueError(msg)

    def list_operations(self) -> list:
        """
        Return sorted list of available operation names.

        Returns:
            Sorted list of operation names

        Example:
            >>> agent.list_operations()
            ['add', 'add_days', 'count_words', 'current_date', ...]
        """
        return sorted(self._operations.keys())

    def list_operations_by_category(self) -> dict:
        """
        Return operations grouped by sub-agent category.

        Returns:
            Dict mapping category name to sorted list of operations

        Example:
            >>> agent.list_operations_by_category()
            {
                "string": ["count_words", "lowercase", ...],
                "datetime": ["add_days", "current_date", ...],
                "calculator": ["add", "divide", ...],
            }
        """
        return {
            "string": sorted([
                "reverse", "uppercase", "lowercase",
                "count_words", "remove_spaces"
            ]),
            "datetime": sorted([
                "current_time", "current_date", "add_days",
                "days_between", "format_date"
            ]),
            "calculator": sorted([
                "add", "subtract", "multiply", "divide",
                "power", "modulo", "sqrt"
            ]),
        }

    def list_aliases(self) -> dict:
        """
        Return all available aliases and what they resolve to.

        Returns:
            Dict mapping alias to canonical operation name
        """
        return dict(self._aliases)

    def describe(self, operation: str) -> str:
        """
        Return description of what an operation does.

        Args:
            operation: Operation name (or alias)

        Returns:
            Human-readable description with args info

        Raises:
            ValueError: If operation is unknown

        Example:
            >>> agent.describe("reverse")
            'Reverses a string. Args: (text)'
        """
        # Resolve alias first
        resolved = self._resolve_alias(operation)
        # Validate the resolved operation
        self._validate_operation(resolved)
        return self._descriptions[resolved]

    def execute(self, operation: str, *args, **kwargs):
        """
        Execute an operation by routing to the appropriate sub-agent.

        Args:
            operation: Name of the operation or alias (e.g., "reverse", "rev", "add_days")
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Result from the sub-agent operation

        Raises:
            ValueError: If operation is invalid or unknown
            (Sub-agent errors propagate with original messages)

        Examples:
            execute("reverse", "hello")              -> "olleh"
            execute("rev", "hello")                  -> "olleh" (alias)
            execute("add_days", "2024-01-15", 5)     -> "2024-01-20"
            execute("add", 2, 3)                     -> 5.0
        """
        # Resolve alias first (v2 feature)
        operation = self._resolve_alias(operation)

        # Validate operation name
        self._validate_operation(operation)

        # Look up agent and method from registry
        agent, method_name = self._operations[operation]
        method = getattr(agent, method_name)

        # Execute and return result (sub-agent errors propagate naturally)
        return method(*args, **kwargs)

    def verify(self) -> dict:
        """
        Run self-tests and return structured results.

        Tests routing to all three sub-agents, error handling, aliases,
        describe, categories, and list_operations.

        Returns:
            dict with keys: status, passed, failed, total, details
        """
        import re

        tests = [
            # String routing tests (5)
            ("route reverse",
             lambda: self.execute("reverse", "hello"),
             "olleh", False),
            ("route uppercase",
             lambda: self.execute("uppercase", "hello"),
             "HELLO", False),
            ("route lowercase",
             lambda: self.execute("lowercase", "HELLO"),
             "hello", False),
            ("route count_words",
             lambda: self.execute("count_words", "a b"),
             2, False),
            ("route remove_spaces",
             lambda: self.execute("remove_spaces", "a b"),
             "ab", False),

            # DateTime routing tests (5)
            ("route current_time format",
             lambda: bool(re.match(r'\d{2}:\d{2}:\d{2}', self.execute("current_time"))),
             True, False),
            ("route current_date format",
             lambda: bool(re.match(r'\d{4}-\d{2}-\d{2}', self.execute("current_date"))),
             True, False),
            ("route add_days",
             lambda: self.execute("add_days", "2024-01-15", 5),
             "2024-01-20", False),
            ("route days_between",
             lambda: self.execute("days_between", "2024-01-15", "2024-01-20"),
             5, False),
            ("route format_date",
             lambda: self.execute("format_date", "2024-01-15", "%m/%d/%Y"),
             "01/15/2024", False),

            # Calculator routing tests (7) - NEW in v2
            ("route add",
             lambda: self.execute("add", 2, 3),
             5.0, False),
            ("route subtract",
             lambda: self.execute("subtract", 10, 4),
             6.0, False),
            ("route multiply",
             lambda: self.execute("multiply", 3, 4),
             12.0, False),
            ("route divide",
             lambda: self.execute("divide", 10, 2),
             5.0, False),
            ("route power",
             lambda: self.execute("power", 2, 3),
             8.0, False),
            ("route modulo",
             lambda: self.execute("modulo", 10, 3),
             1.0, False),
            ("route sqrt",
             lambda: self.execute("sqrt", 16),
             4.0, False),

            # Error handling tests (5)
            ("reject unknown op",
             lambda: self.execute("unknown", "x"),
             ValueError, True),
            ("reject None op",
             lambda: self.execute(None, "x"),
             ValueError, True),
            ("reject empty op",
             lambda: self.execute("", "x"),
             ValueError, True),
            ("propagate string error",
             lambda: self.execute("reverse", None),
             ValueError, True),
            ("propagate datetime error",
             lambda: self.execute("add_days", "bad-date", 5),
             ValueError, True),
            ("propagate calculator error",
             lambda: self.execute("divide", 1, 0),
             ValueError, True),

            # Alias tests (5) - NEW in v2
            ("alias rev",
             lambda: self.execute("rev", "hello"),
             "olleh", False),
            ("alias upper",
             lambda: self.execute("upper", "hi"),
             "HI", False),
            ("alias plus",
             lambda: self.execute("plus", 2, 3),
             5.0, False),
            ("alias now format",
             lambda: bool(re.match(r'\d{2}:\d{2}:\d{2}', self.execute("now"))),
             True, False),
            ("alias today format",
             lambda: bool(re.match(r'\d{4}-\d{2}-\d{2}', self.execute("today"))),
             True, False),

            # Describe tests (3) - NEW in v2
            ("describe reverse",
             lambda: "string" in self.describe("reverse").lower(),
             True, False),
            ("describe with alias",
             lambda: "string" in self.describe("rev").lower(),
             True, False),
            ("describe unknown raises",
             lambda: self.describe("xyz"),
             ValueError, True),

            # Categories tests (3) - NEW in v2
            ("categories returns dict",
             lambda: isinstance(self.list_operations_by_category(), dict),
             True, False),
            ("categories has three keys",
             lambda: len(self.list_operations_by_category()),
             3, False),
            ("categories string has reverse",
             lambda: "reverse" in self.list_operations_by_category()["string"],
             True, False),

            # list_operations tests (2) - UPDATED for v2
            ("list_operations count",
             lambda: len(self.list_operations()),
             17, False),
            ("list_operations sorted",
             lambda: self.list_operations() == sorted(self.list_operations()),
             True, False),
        ]

        results = []
        passed = 0
        failed = 0

        for desc, func, expected, should_raise in tests:
            try:
                result = func()
                if should_raise:
                    results.append({
                        "test": desc,
                        "status": "FAIL",
                        "reason": "Expected error, got result"
                    })
                    failed += 1
                elif result == expected:
                    results.append({"test": desc, "status": "PASS"})
                    passed += 1
                else:
                    results.append({
                        "test": desc,
                        "status": "FAIL",
                        "expected": expected,
                        "got": result
                    })
                    failed += 1
            except Exception as e:
                if should_raise and isinstance(e, expected):
                    results.append({"test": desc, "status": "PASS"})
                    passed += 1
                else:
                    results.append({
                        "test": desc,
                        "status": "FAIL",
                        "error": str(e)
                    })
                    failed += 1

        return {
            "status": "PASS" if failed == 0 else "FAIL",
            "passed": passed,
            "failed": failed,
            "total": len(tests),
            "details": results
        }

    def verify_print(self) -> bool:
        """
        Run verification and print human-readable output.

        Returns:
            True if all tests pass, False otherwise
        """
        result = self.verify()
        print(f"\nUtilityAgent v{self.version} Verification")
        print("=" * 60)
        print(f"Sub-agents: StringAgent v{self.string_agent.version}, "
              f"DateTimeAgent v{self.datetime_agent.version}, "
              f"CalculatorAgent v{self.calculator_agent.version}")
        print(f"Operations available: {len(self.list_operations())}")
        print(f"Aliases available: {len(self._aliases)}")
        categories = self.list_operations_by_category()
        print(f"Categories: {', '.join(categories.keys())}")
        print("-" * 60)
        for detail in result["details"]:
            status = "PASS" if detail["status"] == "PASS" else "FAIL"
            print(f"[{status}] {detail['test']}")
            if detail["status"] == "FAIL":
                if "expected" in detail:
                    print(f"        Expected: {detail['expected']}, Got: {detail['got']}")
                elif "error" in detail:
                    print(f"        Error: {detail['error']}")
                elif "reason" in detail:
                    print(f"        Reason: {detail['reason']}")
        print("=" * 60)
        print(f"Result: {result['passed']}/{result['total']} tests passed")
        print(f"Status: {result['status']}")
        return result["status"] == "PASS"


if __name__ == "__main__":
    agent = UtilityAgent()
    agent.verify_print()
