"""端到端验证：直接走 UrlParser + ParserFactory（不启动 Flask，app.py 依赖 Linux 的 fcntl）。

用法（仓库根目录）:
    .venv\\Scripts\\python.exe tests\\manual_yangshipin_check.py https://www.yspapp.cn/6j3j
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.parsers.yangshipin_parser import YangshipinParser  # noqa: E402
from utils.web_fetcher import UrlParser, WebFetcher  # noqa: E402


def main(share_url):
    redirect_url = WebFetcher.fetch_redirect_url(share_url)
    platform = UrlParser.get_platform(redirect_url)
    real_url = UrlParser.extract_video_address(redirect_url)
    print(f"redirect : {redirect_url}")
    print(f"real_url : {real_url}")

    parser = YangshipinParser(real_url)
    result = {
        "platform": platform,
        "title": parser.get_title_content(),
        "desc": parser.get_description(),
        "video_url": parser.get_real_video_url(),
        "cover_url": parser.get_cover_photo_url(),
        "author": parser.get_author_info(),
        "image_list": parser.get_image_list(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    ok = bool(result["title"] and (result["image_list"] or result["video_url"]))
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "https://www.yspapp.cn/6j3j"))
