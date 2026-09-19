import unittest

from src.parsers.weibo_parser import WeiboParser


class WeiboParserTest(unittest.TestCase):
    def test_extracts_numeric_id_from_video_fid(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://video.weibo.com/show?fid=1034%3A5336275486703690"
        self.assertEqual(parser._extract_id(), "5336275486703690")

    def test_extracts_numeric_id_from_redirected_video_page(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://weibo.com/tv/show/1034:5336275486703690"
        self.assertEqual(parser._extract_id(), "5336275486703690")

    def test_extracts_video_oid_from_redirected_video_page(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://weibo.com/tv/show/1034:5336275486703690"
        self.assertEqual(parser._extract_video_oid(), "1034:5336275486703690")

    def test_extracts_numeric_id_from_pc_numeric_url(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://weibo.com/7928442102/5331959570240710"
        self.assertEqual(parser._extract_id(), "5331959570240710")

    def test_extracts_id_from_pc_base62_url(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://weibo.com/7928442102/O8yqz0I8Q"
        self.assertEqual(parser._extract_id(), "5020389670169684")

    def test_extracts_id_from_mobile_detail_numeric_url(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://m.weibo.cn/detail/5331959570240710"
        self.assertEqual(parser._extract_id(), "5331959570240710")

    def test_extracts_id_from_mobile_detail_base62_url(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://m.weibo.cn/detail/O8yqz0I8Q"
        self.assertEqual(parser._extract_id(), "5020389670169684")

    def test_extracts_id_from_mobile_channel_url(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://m.weibo.cn/7753941940/5332536008119716/qq?wm=3333_2001"
        self.assertEqual(parser._extract_id(), "5332536008119716")

    def test_image_list_extraction(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "text_raw": "图文微博测试",
            "pics": [
                {"large": {"url": "https://wx1.sinaimg.cn/large/pic1.jpg"}},
                {"large": {"url": "https://wx2.sinaimg.cn/large/pic2.jpg"}},
            ],
            "user": {
                "screen_name": "博主昵称",
                "id": "12345678",
                "avatar_hd": "https://wx1.sinaimg.cn/avatar.jpg"
            }
        }
        self.assertEqual(
            parser.get_image_list(),
            ["https://wx1.sinaimg.cn/osj1080/pic1.jpg", "https://wx2.sinaimg.cn/osj1080/pic2.jpg"]
        )
        self.assertIsNone(parser.get_title_content())
        self.assertEqual(parser.get_description(), "图文微博测试")
        self.assertEqual(parser.get_author_info()["nickname"], "博主昵称")

    def test_live_photo_extraction(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "pics": [
                {
                    "large": {"url": "https://wx1.sinaimg.cn/large/pic1.jpg"},
                    "videoSrc": "https://video.weibo.com/media/play?livephoto=https%3A%2F%2Flivephoto.us.sinaimg.cn%2Fvideo1.mov",
                    "type": "livephoto"
                },
                {
                    "large": {"url": "https://wx2.sinaimg.cn/large/pic2.jpg"}
                }
            ]
        }
        self.assertEqual(
            parser.get_image_list(),
            [
                {
                    "url": "https://wx1.sinaimg.cn/osj1080/pic1.jpg",
                    "live_photo_url": "https://video.weibo.com/media/play?livephoto=https%3A%2F%2Flivephoto.us.sinaimg.cn%2Fvideo1.mov"
                },
                {
                    "url": "https://wx2.sinaimg.cn/osj1080/pic2.jpg",
                    "live_photo_url": None
                }
            ]
        )

    def test_video_component_fields(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "title": "公开微博视频",
            "author": "测试作者",
            "author_id": 1,
            "cover_image": "//example.com/cover.jpg",
            "urls": {"高清 1080P": "//example.com/video.mp4"},
        }
        self.assertEqual(parser.get_real_video_url(), "https://example.com/video.mp4")
        self.assertEqual(parser.get_cover_photo_url(), "https://example.com/cover.jpg")
        self.assertEqual(parser.get_title_content(), "公开微博视频")
        self.assertEqual(parser.get_author_info()["nickname"], "测试作者")


    def test_extracts_id_and_oid_from_wblive_url(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.real_url = "https://weibo.com/l/wblive/p/show/1022:2321325311149536575703"
        self.assertEqual(parser._extract_video_oid(), "1022:2321325311149536575703")
        self.assertEqual(parser._extract_id(), "2321325311149536575703")

    def test_wblive_fields(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "title": "直播标题",
            "cover": "https://wx2.sinaimg.cn/large/cover.jpg",
            "replay_origin_url": "http://live.video.weibocdn.com/replay.m3u8",
            "user": {
                "screenName": "主播昵称",
                "uid": 123456,
                "avatar": "https://tvax1.sinaimg.cn/avatar.jpg"
            }
        }
        self.assertEqual(parser.get_real_video_url(), "http://live.video.weibocdn.com/replay.m3u8")
        self.assertEqual(parser.get_cover_photo_url(), "https://wx2.sinaimg.cn/osj1080/cover.jpg")
        self.assertEqual(parser.get_title_content(), "直播标题")
        self.assertEqual(parser.get_author_info()["nickname"], "主播昵称")
        self.assertEqual(parser.get_author_info()["author_id"], "123456")
        self.assertEqual(parser.get_author_info()["avatar"], "https://tvax1.sinaimg.cn/avatar.jpg")


    def test_video_pick_prefers_unwatermarked_variant(self):
        """playback_list 里同时存在带水印与无水印档位时，优先无水印档。"""
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "page_info": {
                "media_info": {
                    "playback_list": [
                        {"play_info": {"label": "mp4_720p", "bitrate": 1200004, "size": 8832938,
                                       "watermark": "original",
                                       "url": "https://f.video.weibocdn.com/o0/a.mp4?label=mp4_720p"}},
                        {"play_info": {"label": "mp4_hd", "bitrate": 794552, "size": 5848503,
                                       "watermark": "none",
                                       "url": "https://f.video.weibocdn.com/u0/b.mp4?label=mp4_hd"}},
                    ]
                }
            }
        }
        self.assertEqual(parser.get_real_video_url(), "https://f.video.weibocdn.com/u0/b.mp4?label=mp4_hd")

    def test_video_pick_takes_highest_bitrate_when_all_watermarked(self):
        """微博视频号成片全部带烧录水印，此时退化为按码率取最高清档。"""
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "page_info": {
                "media_info": {
                    "playback_list": [
                        {"play_info": {"label": "mp4_hd", "bitrate": 794552, "size": 5848503,
                                       "watermark": "original",
                                       "url": "https://f.video.weibocdn.com/o0/b.mp4?label=mp4_hd"}},
                        {"play_info": {"label": "mp4_720p", "bitrate": 1200004, "size": 8832938,
                                       "watermark": "original",
                                       "url": "https://f.video.weibocdn.com/o0/a.mp4?label=mp4_720p"}},
                    ]
                }
            }
        }
        self.assertEqual(parser.get_real_video_url(), "https://f.video.weibocdn.com/o0/a.mp4?label=mp4_720p")

    def test_video_pick_prefers_720p_over_hd_without_playback_list(self):
        """移动端数据没有 playback_list，按 page_info.urls 档位取最高清的 720P。"""
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "page_info": {
                "urls": {
                    "mp4_720p_mp4": "https://f.video.weibocdn.com/o0/a.mp4?label=mp4_720p&template=720x1280.24.0",
                    "mp4_hd_mp4": "https://f.video.weibocdn.com/o0/b.mp4?label=mp4_hd&template=540x960.24.0",
                    "mp4_ld_mp4": "https://f.video.weibocdn.com/o0/b.mp4?label=mp4_hd&template=540x960.24.0",
                },
                "media_info": {
                    "stream_url": "https://f.video.weibocdn.com/o0/b.mp4?label=mp4_hd&template=540x960.24.0",
                    "stream_url_hd": "https://f.video.weibocdn.com/o0/b.mp4?label=mp4_hd&template=540x960.24.0",
                },
            }
        }
        self.assertEqual(parser.get_real_video_url(),
                         "https://f.video.weibocdn.com/o0/a.mp4?label=mp4_720p&template=720x1280.24.0")

    def test_video_pick_parses_playback_list_json_string(self):
        """PC ajax 有时把 playback_list 作为 JSON 字符串返回。"""
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "page_info": {
                "media_info": {
                    "playback_list": (
                        '[{"play_info": {"label": "mp4_hd", "bitrate": 794552, "watermark": "none",'
                        ' "url": "//f.video.weibocdn.com/u0/b.mp4?label=mp4_hd"}}]'
                    )
                }
            }
        }
        self.assertEqual(parser.get_real_video_url(), "https://f.video.weibocdn.com/u0/b.mp4?label=mp4_hd")

    def test_video_pick_falls_back_to_media_info_urls(self):
        parser = WeiboParser.__new__(WeiboParser)
        parser.post_data = {
            "page_info": {
                "media_info": {"mp4_sd_url": "http://f.video.weibocdn.com/u0/c.mp4?label=mp4_sd"}
            }
        }
        self.assertEqual(parser.get_real_video_url(), "http://f.video.weibocdn.com/u0/c.mp4?label=mp4_sd")


if __name__ == "__main__":
    unittest.main()
