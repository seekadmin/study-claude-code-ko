---
name: design-diagram
description: 실제 코드와 설정 파일을 읽고 근거(file:line)가 달린 Mermaid 다이어그램을 만듭니다. 사용자가 아키텍처·흐름·시퀀스 다이어그램, 구성도, 서비스 관계도, 요청 흐름도, "그림으로 보여 줘"를 요청할 때 사용합니다.
argument-hint: "[무엇을 그릴지 (예: 로그인 요청 흐름)]"
allowed-tools: Read, Grep, Glob
---
<!-- 한국어판 독자 예제: 대응하는 영어 원문이 없습니다 -->
<!-- i18n-date: 2026-10-31 -->

# 설계 다이어그램 스킬

## 사용자 입력

```text
$ARGUMENTS
```

입력이 비어 있으면 "저장소 전체 아키텍처 개요"를 그린다고 가정하고, 그렇게 가정했다고 먼저 알립니다.

## 원칙

- **추측하지 않습니다.** 코드나 설정에서 확인한 노드·엣지만 그립니다. 확인하지 못한 것은 다이어그램에 넣지 말고 "미확인" 목록에 적습니다.
- **작게 유지합니다.** 다이어그램 하나에 노드 15개 미만. 넘으면 개요 1장 + 영역별 상세로 나눕니다.
- **텍스트로 남깁니다.** 결과는 diff·리뷰가 가능한 Mermaid 텍스트입니다.

## 실행 단계

### 1단계: 실제 파일 읽기

그리기 전에 다음을 찾아 읽습니다(있는 것만).

1. **매니페스트**: `package.json`, `pyproject.toml`, `go.mod`, `pom.xml`, `build.gradle`, `Cargo.toml`
2. **엔트리포인트**: `main.*`, `index.*`, `app.*`, `server.*`, `cmd/`
3. **라우트·핸들러**: `routes/`, `controllers/`, `handlers/`, `api/`, 프레임워크 데코레이터(`@app.get`, `@GetMapping` 등)
4. **배포·인프라**: `Dockerfile`, `docker-compose.yml`, `k8s/`, `helm/`, `*.tf`
5. **외부 연결**: DB 연결 문자열·ORM 설정, HTTP 클라이언트, 메시지 큐 클라이언트

사용자가 특정 흐름을 지정했다면 그 흐름의 시작점(라우트 또는 함수)부터 호출을 따라갑니다. 매니페스트도 엔트리포인트도 없으면 무엇을 그릴지 사용자에게 묻습니다.

### 2단계: 다이어그램 유형 고르기

| 질문 | 유형 |
|------|------|
| 서비스·모듈이 어떻게 연결되나 | `graph LR` (외부 시스템은 `subgraph`) |
| 함수 안의 분기·재시도 | `flowchart TD` |
| 요청이 컴포넌트를 거치는 순서 | `sequenceDiagram` |
| 테이블·엔터티 관계 | `erDiagram` |
| 객체의 상태 전이 | `stateDiagram-v2` |

### 3단계: Mermaid와 근거 표 작성

- 노드 ID는 짧은 영문(`api`, `orderSvc`), 라벨은 큰따옴표로 감쌉니다: `api["API Server"]`.
- 엣지 라벨은 실제 호출·프로토콜·조건을 짧게 씁니다.
- 다이어그램 바로 아래에 근거 표를 둡니다.

```markdown
| 요소 | 근거 |
|------|------|
| `api --> orderSvc` | `src/routes/orders.ts:18` |
| `orderSvc --> db` | `src/services/order.ts:41` |
```

### 4단계: 자체 검증

출력 전에 근거 표의 **모든 행**을 다시 확인합니다.

1. 해당 `file:line`을 열어 그 호출·의존이 실제로 있는지 봅니다.
2. 화살표 방향(호출자 → 피호출자)이 맞는지 봅니다.
3. 근거를 찾지 못한 엣지는 다이어그램에서 지우고 "미확인" 목록으로 옮깁니다.
4. 노드 수가 15개 이상이면 나눕니다.

검증 결과를 한 줄로 요약합니다. 예: `검증: 엣지 9개 중 9개 확인, 미확인 1개`.

### 5단계: 저장

`docs/diagrams/<name>.md`에 저장합니다. `<name>`은 소문자-하이픈 슬러그(예: `login-sequence`)입니다. 파일 구성:

1. 제목과 한 문장 설명
2. Mermaid 코드 블록
3. 근거 표
4. 미확인 목록(있으면)
5. 생성 날짜와 기준 커밋(`git rev-parse --short HEAD` 결과를 사용자가 제공했거나 확인할 수 있으면)

기존 파일이 있으면 덮어쓰기 전에 사용자에게 확인합니다.

### 6단계: 렌더링(선택)

사용자가 이미지가 필요하다고 하면 다음 명령을 제안합니다. 직접 실행하려면 사용자 승인이 필요합니다.

```bash
npx -p @mermaid-js/mermaid-cli mmdc -i docs/diagrams/<name>.md -o docs/diagrams/<name>.rendered.md
# 단일 .mmd 파일이라면
npx -p @mermaid-js/mermaid-cli mmdc -i docs/diagrams/<name>.mmd -o docs/diagrams/<name>.svg
```

렌더링이 실패하면 문법 오류이므로 라벨의 특수 문자(괄호, 콜론, 따옴표)부터 고칩니다.

## 출력 형식

채팅에는 다음 순서로 답합니다.

1. 무엇을 그렸는지 한 문장
2. Mermaid 다이어그램
3. 근거 표
4. 검증 요약 한 줄과 미확인 목록
5. 저장한 경로
