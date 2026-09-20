# 汽水音乐 (Qishui Music) 逆向解析指南

本篇详细记录字节跳动旗下 **汽水音乐** UGC 视频与歌曲音频的提取方案。

---

## 1. 平台特征与支持能力

* **平台标识**：`汽水音乐`
* **支持媒体类型**：高清 UGC 视频 (MP4) / 歌曲音频 (audio_mp4) / 专辑封面 / 歌曲名称与作者 / 歌词
* **常见链接形态**：
  * 分享短链：`https://qishui.douyin.com/s/iX21ep91/`
  * 落地页：`https://music.douyin.com/qishui/share/track?track_id=xxx`
* **Cookie 依赖**：免费曲目无需 Cookie；**VIP 曲目需要 `QISHUI_COOKIE` 才能拿到完整音频**（详见第 3 节）。

---

## 2. 核心逆向流程

1. **短链跳转**：跟随 302 跳到 `music.douyin.com/qishui/share/track?track_id=...`，优先取 `track_id` 查询参数，其次兼容 `/track/<id>`、`/video/<id>` 路径。
2. **SSR 页面提取**：解析 `_ROUTER_DATA` 里 `loaderData.track_page.audioWithLyricsOption`，取出 `url`（音频直链）、`trackName`、`artistName`、`artistIdStr`、`coverURL`、`duration`、`offsetDuration`。
3. **播放接口兜底**：页面拿不到有效音频时，依次请求 `https://beta-luna.douyin.com/luna/h5/track_v2`、`.../luna/h5/seo_track`，从 `track_player.video_model.video_list[0]` 取 `main_url`。
4. **UGC 视频分支**：`videoOptions` 页面（`/share/ugc_video`）走原逻辑，取视频直链。

---

## 3. VIP 曲目只有 30 秒试听（重要）

汽水对**会员曲目**（`label_info.only_vip_playable = true`）只向未登录请求下发试听片段，表现如下：

| 字段 | 含义 |
| --- | --- |
| `track.duration` / `audioWithLyricsOption.duration` | 完整曲目时长（毫秒 / 秒），例如 `264333` / `264.333` |
| `track.preview.duration` / `audition_info.duration_ms` | 试听片段时长，通常是 `30001`（30 秒，部分曲目 60 秒） |
| `audioWithLyricsOption.offsetDuration` / `video_model.video_duration` | 实际下发流的时长，用于判定是否被截断 |

任何请求参数都改不了这个结果：实测传 `vid` / `media_id` / `quality` 均被服务端忽略，`track_player` 返回的 `video_id` 与预签名 `ptoken` 始终锁定试听 vid。**完整音频只能靠登录态**：

```env
# .env —— 必须是汽水音乐/抖音的 VIP 登录态
QISHUI_COOKIE="sessionid=xxx; sessionid_ss=xxx; sid_tt=xxx; uid_tt=xxx; passport_csrf_token=xxx;"
```

未配置 Cookie 时解析不报错，但响应会带截断标记，调用方据此判断即可：

```json
{ "audio_url": "https://...", "is_preview": true, "full_duration": 264.333 }
```

免费曲目（`label_info.only_vip_playable` 缺失或为 `false`）匿名请求即为完整音频，实测下发 388.728 秒与声明时长一致。

---

## 4. 测试与验证

* **单元测试**：[tests/test_qsmusic_parser.py](file:///Users/leo/Projects/media-parser/tests/test_qsmusic_parser.py)
* **执行命令**：`pytest tests/test_qsmusic_parser.py`
