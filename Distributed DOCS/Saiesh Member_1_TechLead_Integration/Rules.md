# LunarMatch — Tech Lead + Integration Rules

## 1. Own Your Module

System orchestration, interfaces, end-to-end pipeline, Git/GitHub integration, final reliability

## 2. Respect Interfaces

Do not change another member's public function signature without coordinating with Member 1.

## 3. No Fake Results

Never hard-code algorithmic results, metrics or confidence values.

## 4. No Overclaiming

Only describe a capability as implemented after it has actually run and been tested.

## 5. Keep Core Code UI-Free

Core modules must not contain Streamlit-specific logic unless this role explicitly owns the UI.

## 6. Test Before Merge

Before opening a pull request:
- run the module tests;
- run at least one real lunar image example;
- document known limitations.

## 7. Preserve the Baseline

If experimental work breaks the baseline, revert or isolate it.

## 8. Git Discipline

Work only on the assigned branch.

Use clear commits such as:

```text
feat: implement SIFT extractor
fix: handle empty descriptor output
test: add registration edge case
```

## 9. Integration Communication

Report:

```text
DONE:
...

CHANGED:
...

TESTED:
...

BLOCKED:
...

NEXT:
...
```

## 10. Deadline Rule

The team's working demo has priority over optional research extensions.
