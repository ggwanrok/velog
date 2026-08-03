import re
from pathlib import Path

import feedparser
import git


# 자신의 벨로그 아이디 확인
RSS_URL = "https://api.velog.io/rss/@klmcw1004"

REPOSITORY_PATH = "."
POSTS_DIRECTORY = Path(REPOSITORY_PATH) / "velog-posts"


def sanitize_filename(title: str) -> str:
    """파일명으로 사용할 수 없는 문자를 제거한다."""
    filename = re.sub(r'[\\/:*?"<>|]', "-", title)
    filename = filename.strip().rstrip(".")

    if not filename:
        filename = "untitled"

    return f"{filename}.md"


def main() -> None:
    POSTS_DIRECTORY.mkdir(parents=True, exist_ok=True)

    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        raise RuntimeError(
            f"벨로그 RSS에서 글을 가져오지 못했습니다: {RSS_URL}"
        )

    updated_count = 0

    for entry in feed.entries:
        title = entry.get("title", "제목 없음")
        content = entry.get("description", "")

        filename = sanitize_filename(title)
        file_path = POSTS_DIRECTORY / filename

        previous_content = None

        if file_path.exists():
            previous_content = file_path.read_text(encoding="utf-8")

        # 새 글이거나 기존 글 내용이 변경됐을 때 저장
        if previous_content != content:
            file_path.write_text(content, encoding="utf-8")
            updated_count += 1
            print(f"업데이트: {filename}")

    repository = git.Repo(REPOSITORY_PATH)

    repository.git.add(str(POSTS_DIRECTORY))

    if repository.is_dirty(
        index=True,
        working_tree=True,
        untracked_files=True,
    ):
        repository.index.commit(
            f"docs: sync {updated_count} Velog post(s)"
        )
        repository.remote(name="origin").push()
        print(f"{updated_count}개의 글을 커밋했습니다.")
    else:
        print("변경된 벨로그 글이 없습니다.")


if __name__ == "__main__":
    main()
