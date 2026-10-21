# Evaluation report

The real assistant is scored next to three deliberately broken ones. The broken ones should fail, which shows the checks can tell good answers from bad ones.

| Metric | Minimum | Assistant | Hallucinating | Overconfident | Broken format |
|---|---|---|---|---|---|
| Answers in the correct format | 100% | 100% | 100% | 100% | 0% |
| Citations point to real sections | 100% | 100% | 100% | 67% | 0% |
| Figures match the cited section | 100% | 100% | 12% | 100% | 0% |
| Golden questions answered correctly | 90% | 100% | 19% | 100% | 0% |
| Out-of-scope questions refused | 100% | 100% | 100% | 0% | 0% |
| Reworded questions get the same answer | 90% | 100% | 100% | 100% | 0% |

Result for the real assistant: PASS, every metric meets its minimum.
