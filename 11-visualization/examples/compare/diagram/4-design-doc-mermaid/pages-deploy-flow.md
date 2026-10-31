# Markdown 수정 → GitHub Pages 반영 과정

`.github/workflows/pages.yml` 기준입니다. Pages는 `gh-pages` 브랜치를 직접 서빙합니다("Deploy from a branch").

## 전체 흐름

```mermaid
flowchart TD
    Edit([✏️ .md 파일 수정]) --> Local[🧪 로컬 커밋<br/>pre-commit 문서 검사 5종]
    Local --> Push[📤 main 브랜치에 push / PR 병합]
    Push --> Filter{📂 paths 필터<br/>**/*.md 등 변경?}
    Filter -->|No| Skip([⏭️ 워크플로 실행 안 됨])
    Filter -->|Yes| Concur[🔒 concurrency: pages-gh<br/>이전 실행 취소]
    Manual([🖱️ workflow_dispatch]) --> Concur
    Concur --> Checkout[📥 actions/checkout]
    Checkout --> Uv[⚙️ uv 설치]
    Uv --> Cache[💾 vendor 에셋 캐시 복원<br/>scripts/.vendor-cache]
    Cache --> Build[🏗️ uv run scripts/build_website.py<br/>Markdown → HTML, 링크 재작성]
    Build --> Site[📦 site/ 디렉터리 생성]
    Site --> Init[🔧 touch .nojekyll<br/>git init, gh-pages 브랜치]
    Init --> Force[🚀 git push -f gh-pages<br/>GITHUB_TOKEN 사용]
    Force --> Serve[🌐 GitHub Pages가 gh-pages 서빙]
    Serve --> Live([✅ 웹사이트 반영])

    classDef trigger fill:#FFD700,stroke:#333,stroke-width:2px,color:black
    classDef step fill:#87CEEB,stroke:#333,stroke-width:2px,color:darkblue
    classDef done fill:#90EE90,stroke:#333,stroke-width:2px,color:darkgreen
    classDef skip fill:#FFB6C1,stroke:#DC143C,stroke-width:2px,color:black

    class Filter,Manual trigger
    class Local,Push,Concur,Checkout,Uv,Cache,Build,Site,Init,Force,Serve step
    class Edit,Live done
    class Skip skip
```

## 시퀀스 보기

```mermaid
sequenceDiagram
    actor Dev as 👤 작성자
    participant Main as 📁 main 브랜치
    participant GHA as ⚙️ GitHub Actions (pages.yml)
    participant Build as 🏗️ build_website.py
    participant GP as 🌿 gh-pages 브랜치
    participant Web as 🌐 GitHub Pages

    Dev->>Main: .md 수정 후 push
    Main->>GHA: push 이벤트 (paths 일치 시)
    GHA->>GHA: checkout, uv 설치, vendor 캐시 복원
    GHA->>Build: uv run scripts/build_website.py --verbose
    Build-->>GHA: site/ (HTML, 에셋)
    GHA->>GP: .nojekyll 추가 후 force push
    GP->>Web: 브랜치 내용 서빙
    Web-->>Dev: 갱신된 사이트
```

## 핵심 정리

| 항목 | 내용 |
|------|------|
| 트리거 | `main` push 중 `**/*.md`, `scripts/build_website.py`, `scripts/vendor_assets.py`, `scripts/website_templates/**`, `pages.yml` 변경, 또는 수동 실행 |
| 동시성 | `pages-gh` 그룹, 진행 중인 이전 실행은 취소 |
| 빌드 | `uv run scripts/build_website.py`, Markdown이 단일 소스이며 내부 `.md` 링크는 HTML로 재작성 |
| 배포 | `site/`를 새 git 저장소로 만들어 `gh-pages`에 force push (`.nojekyll` 포함) |
| 권한 | `contents: write` |
