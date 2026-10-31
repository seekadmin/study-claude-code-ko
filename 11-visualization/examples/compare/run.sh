#!/bin/bash
# Same question, one approach per folder. Project-scoped skills or --plugin-dir only (no ~/.claude changes).
cd /root/lab/cmp
E=/root/lab/cmp/ext
QD="Markdown 파일을 고치면 이 저장소의 웹사이트(GitHub Pages)에 반영되기까지의 과정을 다이어그램으로 그려줘. 사용자에게 질문하지 말고 기본값으로 진행해. 결과물은 docs/compare/ 폴더에 파일로 저장하고, 마지막 줄에 저장한 파일 경로만 적어줘."
QE="MCP가 뭐야? 초보자한테 설명해줘. 사용자에게 질문하지 말고 기본값으로 진행해. 결과물은 docs/compare/ 폴더에 파일로 저장하고, 마지막 줄에 저장한 파일 경로만 적어줘."
TOOLS="Skill,Read,Glob,Grep,Write,Edit,Bash"
run(){ # name prompt [extra args...]
  local n=$1 p=$2; shift 2
  ( cd $n && mkdir -p docs/compare && start=$(date +%s) &&
    timeout 900 claude -p "$p" --permission-mode acceptEdits --allowedTools "$TOOLS" --output-format stream-json --verbose "$@" > ../out-$n.jsonl 2> ../err-$n.log;
    echo "$n exit=$? sec=$(( $(date +%s)-start ))" >> ../done.log )
}
case "$1" in
  d0) run d0 "$QD" ;;
  d1) run d1 "/design-diagram $QD" ;;
  d2) run d2 "/engineer-design-diagram:engineer-design-diagram $QD" --plugin-dir $E/claude-code-plugins-plus-skills/plugins/devops/engineer-design-diagram ;;
  d3) run d3 "/diagram-design:diagram-design $QD" --plugin-dir $E/diagram-design ;;
  d4) run d4 "/design-doc-mermaid $QD" ;;
  d5) run d5 "/excalidraw:draw $QD" --plugin-dir $E/excalidraw-plugin ;;
  e0) run e0 "$QE" ;;
  e1) run e1 "/eli5 $QE" ;;
  e2) run e2 "/eli5:eli5 $QE" --plugin-dir $E/claude-plugins-community/eli5 ;;
  e3) run e3 "/eli5 $QE" ;;
  e4) run e4 "/eli5 $QE" ;;
esac
