# 央视频 (Yangshipin) 逆向解析指南

本篇详细记录中央广播电视总台 5G 新媒体旗舰平台 **央视频 (Yangshipin)** 的微视频、微短剧、体育资讯作品与图文文章解析方案。

---

## 1. 平台特征与支持能力

* **平台标识**：`央视频`
* **支持媒体类型**：原画/蓝光/超清无水印视频源 (`video_url`) / 高分辨率封面 / 完整视频标题 / 创作者与机构作者信息（头像与名称）/ 视频 ID (`vid`) / 图文文章正文 (`desc`) 与全部配图直链 (`image_list`)
* **常见链接形态**：
  * 官方分享短链：`https://www.yspapp.cn/5Sqx`, `https://www.yspapp.cn/d1o`
  * 移动端竖屏微短剧/小视频：`https://m.yangshipin.cn/portrait_video?vid=l00005817wl`
  * 移动端常规横屏视频：`https://m.yangshipin.cn/video?type=0&vid=v000007pgfu&cid=...`
  * 图文文章：`https://m.yangshipin.cn/static/article.html?articleid=e05kmjv3gty29`（短链 `https://www.yspapp.cn/6j3j` 同样落在这里）
  * PC/网页端：`https://yangshipin.cn/...`
* **Cookie 依赖**：🟢 免配置，无需任何 Cookie 登录态。

---

## 2. 核心逆向流程

1. **Meta Refresh 重定向自动跟随**：
   * 央视频短链 `yspapp.cn/{code}` 采用 HTML `<meta http-equiv="refresh" content="0; URL='https://m.yangshipin.cn/...'"/>` 形式执行页面跳转。
   * 解析器在 `WebFetcher` 与 `YangshipinParser` 中双重内置了针对 `<meta http-equiv="refresh">` 的无感自动追踪，直接锁定最终目标落地页。
2. **SSR 双状态机数据提取**：
   * **横屏常规视频**：页面注入全局变量 `window.__STATE_video__`，解析 `payloads.sharevideo` 结构，获取 `title`、`cover_pic`、`cid`、`vid` 及 `om_info.title`（发布机构或频道名）。
   * **竖屏微短剧/短视频**：页面注入全局变量 `window.__STATE_portrait_video__`，解析 `payloads.videoDataList.items[0].videoData`，获取微短剧标题、`shareItem.shareImgUrl`（超清封面）、以及 `detailFollowItem.actorItem` 中的创作者昵称与头像。
3. **cKey 8.1 签名与 VOD 视频流提取**：
   * 央视频播放器使用 `cKey 8.1` 鉴权算法与 `playvv.yangshipin.cn/playvinfo` 接口交互。
   * 解析器通过先探测获取服务端实时时间戳 `curTime`，然后使用内置纯 Python 实现的 AES-128-CBC + PKCS7 算法生成签名 `cKey`，向 `playvinfo` 接口请求高清/蓝光（1080P/720P）视频下载地址与 `fvkey`，拼接构造得到完整可直接播放的 `.mp4` 直链。
4. **图文文章接口提取**：
   * 文章页 `article.html?articleid=xxx` 是空壳 SPA，服务端只渲染 `<div id="app">`，正文由前端异步拉取，任何静态抓取都得不到内容。
   * 正文与配图只存在于 `https://comment.yangshipin.cn/web/article/article_info` 接口，参数为 `targetId=1&vappid=59306155&vsecret=b42702bf7309a179d102f3d51b1add2fda0bc7ada64cb801&raw=1&id={articleid}`（`vappid` / `vsecret` 为前端硬编码凭证，无需登录）。
   * 返回结构：`data.head` 含 `title` / `source` / `publishTime` / `coverImage`，`data.content.content` 为 CKEditor HTML 正文，配图以 `<img src="/general_cos/article-imgs/...">` 相对路径内嵌。
   * 配图相对路径必须补全为 `https://cover.yangshipin.cn`。同一路径在 `w.` / `s.` / `img.yangshipin.cn` 上返回的都是 HTTP 200 的 HTML 占位页（约 2562 字节），直链会静默失效。URL 上的 `?size=336x177` 是缩略图参数，去掉才拿到原图。
   * 注意 `UrlParser.extract_video_address` 必须为央视频保留 `articleid` 查询参数，否则解析器拿不到文章 ID，接口只会返回 `MEDIA_NOT_FOUND`。

---

## 3. 测试与验证

* **单元测试**：[tests/test_yangshipin_parser.py](file:///Users/leo/Projects/media-parser/tests/test_yangshipin_parser.py)
* **执行命令**：`python3 -m unittest tests/test_yangshipin_parser.py`
* **线上回归**：`python .venv/Scripts/python.exe tests/manual_yangshipin_check.py https://www.yspapp.cn/6j3j`（直连短链跑完整链路，输出标题、正文、配图、封面与作者）
