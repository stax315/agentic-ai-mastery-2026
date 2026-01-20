# Day 5: Two-Session Workflow

## Theme: Learning from Your Own Code

Today's focus is the **Two-Session Workflow** - a disciplined approach to improving code through structured self-review.

---

## The Two-Session Pattern

### Session 1: Build (Done on Days 1-2)
- Built agents with planning-first approach
- Achieved zero-bug development
- Tests all passing

### Session 2: Review (TODAY)
- Act as senior engineer reviewing your own code
- Identify what could be improved
- Document critique without fixing yet

### Session 3: Improve
- Build v3 incorporating review feedback
- Apply specific improvements identified
- Maintain backwards compatibility

### Session 4: Document
- Capture the review → improvement process
- Add patterns to CLAUDE.md
- Note what review revealed that tests didn't

---

## Today's Task

**Pick ONE Day 1-2 agent for deep review:**

| Agent | Location | Good Candidate? |
|-------|----------|-----------------|
| CalculatorAgent v2 | day-01/ | Yes - most methods, most mature |
| StringAgent | day-02/ | Yes - good complexity level |
| DateTimeAgent | day-02/ | Yes - has edge cases |
| UtilityAgent | day-02/ | Maybe - coordination vs implementation |

**Recommended:** CalculatorAgent v2 (7 methods, well-tested, room for production hardening)

---

## Review Checklist

When acting as senior engineer, ask:

### Code Quality
- [ ] Are method names clear and consistent?
- [ ] Are docstrings complete and accurate?
- [ ] Is error handling appropriate?
- [ ] Are edge cases covered?

### Production Readiness
- [ ] Are error messages helpful for debugging?
- [ ] Is logging needed?
- [ ] Are there performance concerns?
- [ ] Is the API intuitive?

### Testing
- [ ] Are there gaps in test coverage?
- [ ] Are edge cases tested?
- [ ] Are error cases tested?
- [ ] Is verify() comprehensive?

### Architecture
- [ ] Is the code well-organized?
- [ ] Are responsibilities clear?
- [ ] Is there unnecessary complexity?
- [ ] Could anything be simpler?

---

## Expected Outputs

By end of Day 5:

1. **code_review.md** - Detailed critique of chosen agent
2. **[agent]_v3.py** - Improved version incorporating feedback
3. **test_[agent]_v3.py** - Updated tests for v3
4. **CLAUDE.md update** - New patterns from review process

---

## Why This Matters

The Two-Session Workflow teaches:

1. **Self-Critique Skill** - See your own code as others would
2. **Incremental Improvement** - v1 → v2 → v3 progression
3. **Review-Driven Development** - Reviews reveal what tests miss
4. **Pattern Recognition** - Identify improvement categories

---

## Anti-Goals

Do NOT:
- Review all agents at once (pick ONE)
- Rewrite from scratch (improve, don't replace)
- Add features not identified in review
- Skip documentation

---

## Success Criteria

Day 5 is successful when:
- [ ] One agent deeply reviewed with documented critique
- [ ] v3 created with specific improvements
- [ ] All tests passing (v2 tests + new v3 tests)
- [ ] Review → improvement process documented
- [ ] At least 2 new patterns added to CLAUDE.md

---

Last updated: January 20, 2026
Status: Ready for tomorrow's work
