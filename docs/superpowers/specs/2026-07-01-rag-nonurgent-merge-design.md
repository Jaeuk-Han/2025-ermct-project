현재 상태로 보존하는 것은 확인했습니다. merge, push, commit, discard는 하지 마세요.

이제 선택지를 다시 제시하지 말고, 현재 worktree의 변경사항을 read-only로 점검해서 구현 리뷰 리포트만 작성해주세요.

## 금지 사항

- commit 금지
- push 금지
- merge 금지
- discard 금지
- 파일 수정 금지
- 선택지 재제시 금지

## 수행할 작업

현재 브랜치 `fix/rag-ktas-nonurgent-merge`에서 아래 내용을 확인하고 한국어 리포트로 정리해주세요.

1. `git status --short`
2. `git diff --stat`
3. 수정 파일 목록
4. `app/ktas_engine.py`에서 변경된 valid-RAG merge branch 요약
5. RAG 1~3에서 기존처럼 `min(rule, rag)`가 적용되는지
6. RAG 4~5 + rule 3에서 RAG 결과가 최종 KTAS로 채택되는지
7. RAG 4~5 + rule 1~2에서 rule 결과가 최종 KTAS로 채택되는지
8. rule override 시 `fallback_reason="rule_based_safety_priority"`가 들어가는지
9. `safety_merge_applied` 값이 정책에 맞게 설정되는지
10. 기존 parse/validation/low confidence/empty evidence fallback contract가 유지되는지
11. parser, schema, route, frontend, deploy 설정이 변경되지 않았는지

## 정책 확인

아래 케이스가 테스트로 검증되는지 확인해주세요.

- rule=3, rag=4 → final=4
- rule=3, rag=5 → final=5
- rule=3, rag=2 → final=2
- rule=2, rag=3 → final=2
- rule=1, rag=4 → final=1, fallback_reason="rule_based_safety_priority"
- rule=2, rag=5 → final=2, fallback_reason="rule_based_safety_priority"
- confidence 낮은 rag=4 → 기존 rule fallback
- evidence 없는 rag=4 → 기존 rule fallback
- parse failure → 기존 fallback contract 유지
- validation failure → 기존 fallback contract 유지

## 검증 결과 요약

아래 검증 결과도 다시 요약해주세요.

```bash
poetry run python -m compileall app
poetry run python -m unittest discover -s tests -v
git diff --check
```

마지막에는 아래 셋 중 하나로 판단해주세요.

push/PR 가능
추가 수정 필요
보류