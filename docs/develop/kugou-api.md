---
title: 酷狗 API 参考（第三方）
---

# 🔌 酷狗 API 参考（第三方）

本文档介绍 EchoMusic 如何调用酷狗音乐公开 API，并列出常用接口参考。API 层完全基于第三方项目 [KuGouMusicApi](https://github.com/MakcRe/KuGouMusicApi)（以 git 子模块形式内嵌于 `server/` 目录）。

::: warning 注意
EchoMusic 不提供任何服务端。所有 API 请求均由客户端直接发起，调用酷狗音乐的公开接口。这些接口仅供学习研究参考。
:::

## 工作机制

### 子模块与进程内加载

`server/` 是 KuGouMusicApi 的 git 子模块（`.gitmodules` 声明，锁定特定 commit），同时是 pnpm workspace 成员。EchoMusic **没有自研的路由层或服务封装**——不存在 `server/services/kugou.ts`、`server/routes/` 之类的代码，路由完全由子模块的 `module/*.js` 文件派生：

- 路由规则：`'/' + 文件名去掉 .js、下划线替换为斜杠`。例如 `song_url.js` → `/song/url`、`login_qr_key.js` → `/login/qr/key`
- 当前锁定版本共 **235 个 module**，覆盖歌曲、搜索、歌单、用户、评论、视频、音效等全部能力
- 请求经 IPC 而非 HTTP 处理：渲染进程调用 `window.electron.api.request()`，preload 转发为 `api:request` IPC 消息，主进程 `src/main/server.ts` 的 `handleApiRequest` 按路由匹配 module 并**按需加载**（首次调用时 require，之后走缓存）
- module 发出的 HTTPS 请求、参数签名与加密（`server/util/`）均由子模块自身完成

### 设备身份

主进程初始化 API 服务时会生成并持久化设备标识（guid、mid、MAC、WebGL hash），后续请求以默认 Cookie 携带这些标识，保证与真实客户端行为一致。

## 常用接口参考

以下路由均以**锁定的子模块版本**为准，"Module" 列为对应的 `server/module/` 文件名，"方法"列是 EchoMusic 渲染层实际使用的方法（上游 module 对 HTTP 方法无严格限制）。

### 歌曲

#### 获取音源 URL（授权聚合）

```
GET /song/url/auth/merge        # module: song_url_auth_merge.js
```

歌曲播放的核心接口：先调用歌曲授权接口获取 `auth`，再聚合换取播放地址。EchoMusic 播放前会先请求 `/user/verify` 拿到 auth。

| 参数 | 类型 | 说明 |
|------|------|------|
| hash | string | 歌曲 hash（内部会转为小写） |
| quality | string | 音质（支持魔法音乐标识，如 `piano`/`acappella`/`subwoofer`/`ancient`/`dj`） |
| auth | string | 歌曲授权凭证（来自 `/user/verify`） |
| album_id | string? | 专辑 ID |
| album_audio_id | string? | 专辑歌曲 ID |
| ppage_id | string? | 播放页 ID |

#### 其他歌曲接口

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/song/url` | `song_url.js` | 直接获取音源 URL |
| `/song/url/new` | `song_url_new.js` | 新版音源接口 |
| `/song/url/auth` | `song_url_auth.js` | 音源授权（被 merge 接口内部复用） |
| `/song/auth` | `song_auth.js` | 歌曲播放授权 |
| `/privilege/lite` | `privilege_lite.js` | 播放权限/音质信息（参数 `hash`、`album_id`） |
| `/audio` | `audio.js` | 按 hash 批量获取歌曲元信息（歌名、歌手、封面） |
| `/krm/audio` | `krm_audio.js` | 按 `album_audio_id` 批量获取歌曲/歌手/专辑信息 |
| `/song/climax` | `song_climax.js` | 歌曲高潮片段（参数 `hash`） |
| `/song/ranking` | `song_ranking.js` | 歌曲榜单信息（参数 `album_audio_id`） |
| `/song/ranking/filter` | `song_ranking_filter.js` | 歌曲榜单过滤（参数 `album_audio_id`、`page`、`pagesize`） |
| `/images/audio` | `images_audio.js` | 歌曲关联歌手图片（参数 `hash`、`audio_id` 等） |

### 歌词

```
GET /lyric                      # module: lyric.js
```

| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 歌词 ID（由 `/search/lyric` 匹配获得） |
| accesskey | string | 歌词访问密钥 |
| fmt | string | 格式：`krc`（默认）/ `lrc` |
| decode | string | 是否解码内容（`true` 时返回 `decodeContent`） |
| client | string | 客户端类型，默认 `android` |

歌词匹配使用 `/search/lyric`（`search_lyric.js`）：支持 `hash` 自动匹配或 `keywords` 手动搜索，可选 `duration`（毫秒）、`album_audio_id`、`man`（`yes` 返回候选列表）。

### 搜索

```
GET /search                     # module: search.js
```

| 参数 | 类型 | 说明 |
|------|------|------|
| keywords | string | 搜索关键词 |
| type | string | 类型：`song` / `album` / `author` / `mv` / `special` / `lyric`（默认 `song`） |
| page | number | 页码（默认 1） |
| pagesize | number | 每页数量（歌曲默认 30，专辑默认 20） |

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/search/suggest` | `search_suggest.js` | 搜索建议（参数 `keywords`） |
| `/search/default` | `search_default.js` | 默认搜索词 |
| `/search/hot` | `search_hot.js` | 热搜榜 |
| `/search/complex` | `search_complex.js` | 综合搜索 |
| `/search/mixed` | `search_mixed.js` | 混合搜索 |
| `/search/lyric` | `search_lyric.js` | 歌词匹配搜索 |

### 歌手

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/artist/detail` | `artist_detail.js` | 歌手详情（参数 `id`，即 author_id） |
| `/artist/audios` | `artist_audios.js` | 歌手歌曲列表 |
| `/artist/audios/new` | `artist_audios_new.js` | 歌手新歌 |
| `/artist/albums` | `artist_albums.js` | 歌手专辑列表 |
| `/artist/lists` | `artist_lists.js` | 歌手相关列表 |
| `/artist/videos` | `artist_videos.js` | 歌手视频 |
| `/artist/follow` / `/artist/unfollow` | `artist_follow.js` / `artist_unfollow.js` | 关注/取关歌手 |
| `/artist/honour` | `artist_honour.js` | 歌手荣誉 |
| `/artist/follow/newsongs` | `artist_follow_newsongs.js` | 关注歌手新歌 |

### 专辑

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/album/detail` | `album_detail.js` | 专辑详情（参数 `id`，即 album_id） |
| `/album/songs` | `album_songs.js` | 专辑曲目列表 |
| `/album/dycover` | `album_dycover.js` | 专辑动态封面 |

### 歌单

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/playlist/detail` | `playlist_detail.js` | 歌单详情（参数 `ids`，逗号分隔的 global_collection_id） |
| `/playlist/track/all` | `playlist_track_all.js` | 歌单全部歌曲 |
| `/playlist/track/all/new` | `playlist_track_all_new.js` | 新版歌单歌曲列表 |
| `/playlist/add` / `/playlist/del` | `playlist_add.js` / `playlist_del.js` | 创建/删除歌单 |
| `/playlist/tracks/add` / `/playlist/tracks/del` / `/playlist/tracks/sort` | `playlist_tracks_*.js` | 歌单内歌曲增删排序 |
| `/playlist/sort` / `/playlist/update` | `playlist_sort.js` / `playlist_update.js` | 歌单排序与信息更新 |
| `/playlist/tags` | `playlist_tags.js` | 歌单分类标签 |
| `/playlist/pic` / `/playlist/pic/upload` | `playlist_pic.js` / `playlist_pic_upload.js` | 歌单封面获取/上传 |
| `/playlist/similar` | `playlist_similar.js` | 相似歌单 |

### 排行榜

```
GET /rank/list                  # module: rank_list.js
```

| 参数 | 类型 | 说明 |
|------|------|------|
| withsong | number | 是否附带歌曲（默认 1） |

其他榜单接口：`/rank/top`（`rank_top.js`）、`/rank/audio`（`rank_audio.js`）、`/rank/info`（`rank_info.js`）、`/rank/vol`（`rank_vol.js`）。

### 推荐与私人 FM

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/personal/fm` | `personal_fm.js` | 私人 FM（见下） |
| `/fm/recommend` | `fm_recommend.js` | FM 推荐 |
| `/fm/songs` / `/fm/class` | `fm_songs.js` / `fm_class.js` | FM 歌曲/分类 |
| `/everyday/recommend` | `everyday_recommend.js` | 每日推荐歌曲 |
| `/everyday/style/recommend` | `everyday_style_recommend.js` | 风格推荐（参数 `platform`、`tagids`） |
| `/home/discover` | `home_discover.js` | 首页推荐流（参数 `support`、`recall_type`） |
| `/ai/recommend/song` | `ai_recommend_song.js` | 概念版免费听推荐流 |
| `/recommend/songs` | `recommend_songs.js` | 推荐歌曲 |
| `/top/song` | `top_song.js` | 新歌速递（参数 `type` 即 rank_id，默认 21608；`page`、`pagesize`） |
| `/top/album` | `top_album.js` | 新碟上架 |
| `/top/playlist` | `top_playlist.js` | 歌单榜 |
| `/top/ip` | `top_ip.js` | IP 榜 |

私人 FM 参数（`GET /personal/fm`）：

| 参数 | 类型 | 说明 |
|------|------|------|
| mode | string | 模式：`normal` / `small` / `peak` / `radio` |
| action | string | 动作：`play` / `garbage` / `click_red` / `download` 等 |
| hash | string | 当前歌曲 hash |
| songid | string | 歌曲 ID |
| playtime | string/number | 已播放时长 |
| song_pool_id | string/number | 歌曲池 ID |
| remain_songcnt | number | 剩余歌曲数 |
| is_overplay | number | 是否播完 |

### 用户与登录

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/login` | `login.js` | 账号登录 |
| `/login/cellphone` | `login_cellphone.js` | 手机验证码登录（参数 `mobile`、`code`） |
| `/login/qr/key` / `/login/qr/create` / `/login/qr/check` | `login_qr_*.js` | 二维码登录三步流程 |
| `/login/qq/qr/create` / `/login/qq/qr/check` | `login_qq_qr_*.js` | QQ 二维码登录 |
| `/login/wx/create` / `/login/wx/check` | `login_wx_*.js` | 微信二维码登录 |
| `/login/token` | `login_token.js` | Token 登录 |
| `/login/device` / `/login/device/kick` | `login_device*.js` | 设备登录管理 |
| `/login/openplat` | `login_openplat.js` | 开放平台登录 |
| `/user/detail` | `user_detail.js` | 用户详情（参数 `userid`，登录凭证经 cookie/token） |
| `/user/info` | `user_info.js` | 用户信息 |
| `/user/verify` | `user_verify.js` | 歌曲播放授权凭证（获取 `auth`） |
| `/user/update` / `/user/update/avatar` | `user_update.js` / `user_update_avatar.js` | 更新资料/头像 |
| `/user/cloud` 系列 | `user_cloud*.js` | 音乐云盘：列表 `/user/cloud`、上传 `/user/cloud/upload`、删除 `/user/cloud/del`、播放地址 `/user/cloud/url`、匹配 `/user/cloud/match` |
| `/user/history` | `user_history.js` | 播放历史 |
| `/user/listen/report` | `user_listen_report.js` | 听歌上报 |
| `/user/preference` / `/user/preference/update` | `user_preference*.js` | 听歌偏好 |
| `/user/purchased/songs` / `/user/purchased/albums` | `user_purchased_*.js` | 已购歌曲/专辑 |
| `/user/playlist` | `user_playlist.js` | 用户歌单 |
| `/user/follow` 系列 | `user_follow*.js` | 关注、粉丝、私信 |
| `/captcha/sent` | `captcha_sent.js` | 发送验证码 |
| `/register/dev` | `register_dev.js` | 设备注册 |

### 评论

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/comment/music` | `comment_music.js` | 歌曲评论 |
| `/comment/floor` / `/comment/floor/send` | `comment_floor.js` / `comment_floor_send.js` | 评论楼层/回复 |
| `/comment/count` | `comment_count.js` | 评论数 |
| `/comment/music/classify` / `/comment/music/hotword` | `comment_music_*.js` | 评论分类/热词 |
| `/comment/music/del` | `comment_music_del.js` | 删除评论 |
| `/comment/album` / `/comment/playlist` | `comment_album.js` / `comment_playlist.js` | 专辑/歌单评论 |
| `/favorite/count` | `favorite_count.js` | 收藏数 |

### 视频、识曲与其他

| 路由 | Module 文件 | 说明 |
|------|-------------|------|
| `/video/detail` / `/video/url` / `/video/privilege` | `video_*.js` | MV 详情/播放地址/权限 |
| `/kmr/audio/mv` | `kmr_audio_mv.js` | 歌曲 MV 信息 |
| `/audio/match` | `audio_match.js` | 听歌识曲（PCM 音频以二进制 body 上传） |
| `/import/playlist` | `import_playlist.js` | 外部歌单导入 |
| `/effects/artist` / `/effects/brand` / `/effects/brand/detail` / `/effects/match` | `effects_*.js` | 音效品牌/歌手/匹配 |
| `/get/model` / `/get/mode/info` | `get_model.js` / `get_mode_info.js` | 音效模型信息 |
| `/listen/together/*` | `listen_together_*.js` | 一起听（房间、歌曲、聊天等） |
| `/blacklist` / `/blacklist/list` | `blacklist.js` / `blacklist_list.js` | 内容黑名单 |
| `/server/now` | `server_now.js` | 服务器时间 |
| `/playhistory/upload` | `playhistory_upload.js` | 播放历史上报 |
| `/youth/*` | `youth_*.js` | 青春频道与 VIP 权益 |

::: tip 命名说明
路由名来自 module 文件名，因此与"直觉命名"可能有出入：歌手是 `artist_*`（而非 `singer`），登录在 `/login/*`（而非 `/user/login`），用户详情是 `/user/detail`（而非 `/user/profile`）。旧版文档中的 `/song/detail`、`/singer/detail`、`/recommend/home` 等路由在当前子模块版本中不存在。
:::

## 实现参考

EchoMusic 侧的集成代码只有一处：`src/main/server.ts`。它在主进程内复现了上游 `server.js` 的 Express 路由逻辑（IPC 模式）：

1. **路由分发**：启动时扫描 `server/module/*.js` 建立路由表（不立即加载），收到 `api:request` 后精确匹配 URL 并按需 require 对应 module，结果缓存
2. **Cookie 合并**：默认设备 Cookie → 请求参数中的 `cookie` → `Authorization` header 中的凭证，优先级依次提高
3. **参数规范化**：IPC 传输保留原始类型，分发前统一将标量参数转为字符串，兼容依赖字符串方法的 module
4. **二进制 body**：听歌识曲的 PCM 数据等 Buffer 请求体放入 `query.data`，由 module 以 octet-stream 上传
5. **签名与加密**：请求签名（`signParamsKey`）、AES/RSA 加密、设备标识等全部由子模块及其 `server/util/` 完成，应用层不参与
6. **音源直连**：接口只返回音源 URL，音频流由 echo-audio-player 直接拉取，不经过前端中转

## 免责声明

以上 API 接口仅为学习研究参考。接口可能随时变更，EchoMusic 会及时跟进更新子模块。请勿将这些接口用于任何商业用途。
