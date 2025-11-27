#!/bin/bash

# 引数チェック（数字のみ）
if [ $# -ne 1 ]; then
  echo "Usage: $0 <number>"
  exit 1
fi

number=$1

# クリップボードからパス取得
if command -v pbpaste > /dev/null 2>&1; then
  path=$(pbpaste)
elif command -v xsel > /dev/null 2>&1; then
  path=$(xsel --clipboard)
elif command -v xclip > /dev/null 2>&1; then
  path=$(xclip -selection clipboard -o)
else
  echo "クリップボードからの取得コマンドが見つかりません"
  exit 1
fi

# ファイル名のみ取得、拡張子除去
filename=$(basename "$path")
filename_noext="${filename%.*}"

# SQL組み立て
sql="select * from \`henry-staging.pull_request_${number}.${filename_noext}\` limit 100"

# クリップボードへコピー＆表示
if command -v pbcopy > /dev/null 2>&1; then
  echo "$sql" | tee >(pbcopy)
elif command -v xsel > /dev/null 2>&1; then
  echo "$sql" | tee >(xsel --clipboard --input)
elif command -v xclip > /dev/null 2>&1; then
  echo "$sql" | tee >(xclip -selection clipboard)
else
  echo "$sql"
  echo "クリップボードコピーコマンドが見つかりません"
fi

