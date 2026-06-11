# Changelog

## [1.1.0] - 2026-06-11

### Added
- 사이드바 UI: API 키 입력, 모델 선택, 파라미터 조절을 사이드바로 통합
- 모델 선택 드롭다운: `gpt-4o-mini`(기본값), `gpt-4o`, `gpt-3.5-turbo` 중 선택 가능
- Temperature 슬라이더: 0.0 ~ 2.0 범위로 응답 창의성 조절
- 채팅 기록 내보내기: `.txt` 및 `.json` 형식 다운로드 버튼
- 대화 초기화 버튼 (Clear chat)
- API 오류 처리: 키 오류, 네트워크 오류 등 발생 시 화면에 에러 메시지 표시

### Changed
- 기본 모델을 `gpt-3.5-turbo` → `gpt-4o-mini`로 변경
- API 키 입력 위치를 메인 화면 → 사이드바로 이동

---

## [1.0.0] - 2026-06-11

### Added
- Streamlit 기반 챗봇 초기 버전 출시
- OpenAI `gpt-3.5-turbo` 모델을 사용한 스트리밍 응답
- 세션 상태를 통한 대화 기록 유지
- OpenAI API 키 입력 필드
