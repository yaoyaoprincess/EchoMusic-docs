---
title: Kugou API Reference (Third-party)
---

# 🔌 Kugou API Reference (Third-party)

This document describes how EchoMusic calls the Kugou Music public APIs and lists the most frequently used endpoints. The API layer is entirely based on the third-party project [KuGouMusicApi](https://github.com/MakcRe/KuGouMusicApi), embedded in the `server/` directory as a git submodule.

::: warning
EchoMusic does not provide any server. All API requests are made directly from the client, calling Kugou Music's public endpoints. These endpoints are for educational and research reference only.
:::

## How It Works

### Submodule and In-Process Loading

`server/` is a git submodule of KuGouMusicApi (declared in `.gitmodules`, pinned to a specific commit) and is also a pnpm workspace member. EchoMusic has **no self-written routing layer or service wrapper** — there is no `server/services/kugou.ts` or `server/routes/`; routes are derived entirely from the submodule's `module/*.js` files:

- Route rule: `'/' + file name without .js, with underscores replaced by slashes`. For example `song_url.js` → `/song/url`, `login_qr_key.js` → `/login/qr/key`
- The pinned version has **235 modules** in total, covering songs, search, playlists, users, comments, videos, audio effects, and more
- Requests are handled over IPC rather than HTTP: the renderer calls `window.electron.api.request()`, the preload forwards it as the `api:request` IPC message, and `handleApiRequest` in the main process `src/main/server.ts` matches the route to a module and **lazy-loads** it (required on first call, cached afterwards)
- The HTTPS requests, parameter signing, and encryption (`server/util/`) are all handled by the submodule itself

### Device Identity

When the main process initializes the API service, it generates and persists a device identity (guid, mid, MAC, WebGL hash). Subsequent requests carry this identity in default cookies to behave like a real client.

## Endpoint Reference

The routes below are based on the **pinned submodule version**. The "Module" column is the corresponding `server/module/` file name, and the "Method" column is what EchoMusic's renderer actually uses (the upstream modules do not strictly restrict HTTP methods).

### Songs

#### Get Audio URL (Aggregated Auth)

```
GET /song/url/auth/merge        # module: song_url_auth_merge.js
```

The core playback endpoint: it first calls the song auth endpoint to obtain an `auth` token, then exchanges it for the playback URL. EchoMusic requests `/user/verify` beforehand to get the auth token.

| Parameter | Type | Description |
|------|------|------|
| hash | string | Song hash (lowercased internally) |
| quality | string | Quality (supports magic identifiers such as `piano`/`acappella`/`subwoofer`/`ancient`/`dj`) |
| auth | string | Song auth credential (from `/user/verify`) |
| album_id | string? | Album ID |
| album_audio_id | string? | Album song ID |
| ppage_id | string? | Play page ID |

#### Other Song Endpoints

| Route | Module File | Description |
|------|-------------|------|
| `/song/url` | `song_url.js` | Get the audio URL directly |
| `/song/url/new` | `song_url_new.js` | New audio URL endpoint |
| `/song/url/auth` | `song_url_auth.js` | Audio URL auth (reused internally by the merge endpoint) |
| `/song/auth` | `song_auth.js` | Song playback auth |
| `/privilege/lite` | `privilege_lite.js` | Playback privilege/quality info (params `hash`, `album_id`) |
| `/audio` | `audio.js` | Batch song metadata by hash (name, artist, cover) |
| `/krm/audio` | `krm_audio.js` | Batch song/artist/album info by `album_audio_id` |
| `/song/climax` | `song_climax.js` | Song climax segment (param `hash`) |
| `/song/ranking` | `song_ranking.js` | Song chart info (param `album_audio_id`) |
| `/song/ranking/filter` | `song_ranking_filter.js` | Song chart filter (params `album_audio_id`, `page`, `pagesize`) |
| `/images/audio` | `images_audio.js` | Artist images related to a song (params `hash`, `audio_id`, etc.) |

### Lyrics

```
GET /lyric                      # module: lyric.js
```

| Parameter | Type | Description |
|------|------|------|
| id | string | Lyric ID (obtained from `/search/lyric`) |
| accesskey | string | Lyric access key |
| fmt | string | Format: `krc` (default) / `lrc` |
| decode | string | Whether to decode the content (returns `decodeContent` when `true`) |
| client | string | Client type, defaults to `android` |

Lyric matching uses `/search/lyric` (`search_lyric.js`): it supports automatic matching by `hash` or manual search by `keywords`, with optional `duration` (ms), `album_audio_id`, and `man` (`yes` returns a candidate list).

### Search

```
GET /search                     # module: search.js
```

| Parameter | Type | Description |
|------|------|------|
| keywords | string | Search keywords |
| type | string | Type: `song` / `album` / `author` / `mv` / `special` / `lyric` (default `song`) |
| page | number | Page number (default 1) |
| pagesize | number | Page size (30 for songs, 20 for albums) |

| Route | Module File | Description |
|------|-------------|------|
| `/search/suggest` | `search_suggest.js` | Search suggestions (param `keywords`) |
| `/search/default` | `search_default.js` | Default search term |
| `/search/hot` | `search_hot.js` | Hot search list |
| `/search/complex` | `search_complex.js` | Complex search |
| `/search/mixed` | `search_mixed.js` | Mixed search |
| `/search/lyric` | `search_lyric.js` | Lyric matching search |

### Artists

| Route | Module File | Description |
|------|-------------|------|
| `/artist/detail` | `artist_detail.js` | Artist details (param `id`, the author_id) |
| `/artist/audios` | `artist_audios.js` | Artist song list |
| `/artist/audios/new` | `artist_audios_new.js` | Artist new songs |
| `/artist/albums` | `artist_albums.js` | Artist album list |
| `/artist/lists` | `artist_lists.js` | Artist-related lists |
| `/artist/videos` | `artist_videos.js` | Artist videos |
| `/artist/follow` / `/artist/unfollow` | `artist_follow.js` / `artist_unfollow.js` | Follow/unfollow an artist |
| `/artist/honour` | `artist_honour.js` | Artist honors |
| `/artist/follow/newsongs` | `artist_follow_newsongs.js` | New songs from followed artists |

### Albums

| Route | Module File | Description |
|------|-------------|------|
| `/album/detail` | `album_detail.js` | Album details (param `id`, the album_id) |
| `/album/songs` | `album_songs.js` | Album track list |
| `/album/dycover` | `album_dycover.js` | Dynamic album cover |

### Playlists

| Route | Module File | Description |
|------|-------------|------|
| `/playlist/detail` | `playlist_detail.js` | Playlist details (param `ids`, comma-separated global_collection_id values) |
| `/playlist/track/all` | `playlist_track_all.js` | All songs in a playlist |
| `/playlist/track/all/new` | `playlist_track_all_new.js` | New playlist song list endpoint |
| `/playlist/add` / `/playlist/del` | `playlist_add.js` / `playlist_del.js` | Create/delete a playlist |
| `/playlist/tracks/add` / `/playlist/tracks/del` / `/playlist/tracks/sort` | `playlist_tracks_*.js` | Add/remove/sort songs within a playlist |
| `/playlist/sort` / `/playlist/update` | `playlist_sort.js` / `playlist_update.js` | Playlist ordering and info update |
| `/playlist/tags` | `playlist_tags.js` | Playlist category tags |
| `/playlist/pic` / `/playlist/pic/upload` | `playlist_pic.js` / `playlist_pic_upload.js` | Get/upload playlist cover |
| `/playlist/similar` | `playlist_similar.js` | Similar playlists |

### Charts

```
GET /rank/list                  # module: rank_list.js
```

| Parameter | Type | Description |
|------|------|------|
| withsong | number | Whether to include songs (default 1) |

Other chart endpoints: `/rank/top` (`rank_top.js`), `/rank/audio` (`rank_audio.js`), `/rank/info` (`rank_info.js`), `/rank/vol` (`rank_vol.js`).

### Recommendations and Personal FM

| Route | Module File | Description |
|------|-------------|------|
| `/personal/fm` | `personal_fm.js` | Personal FM (see below) |
| `/fm/recommend` | `fm_recommend.js` | FM recommendations |
| `/fm/songs` / `/fm/class` | `fm_songs.js` / `fm_class.js` | FM songs/categories |
| `/everyday/recommend` | `everyday_recommend.js` | Daily recommended songs |
| `/everyday/style/recommend` | `everyday_style_recommend.js` | Style-based recommendations (params `platform`, `tagids`) |
| `/home/discover` | `home_discover.js` | Home discovery feed (params `support`, `recall_type`) |
| `/ai/recommend/song` | `ai_recommend_song.js` | Concept-edition free-listen feed |
| `/recommend/songs` | `recommend_songs.js` | Recommended songs |
| `/top/song` | `top_song.js` | New song express (param `type` is the rank_id, default 21608; plus `page`, `pagesize`) |
| `/top/album` | `top_album.js` | New album releases |
| `/top/playlist` | `top_playlist.js` | Playlist charts |
| `/top/ip` | `top_ip.js` | IP charts |

Personal FM parameters (`GET /personal/fm`):

| Parameter | Type | Description |
|------|------|------|
| mode | string | Mode: `normal` / `small` / `peak` / `radio` |
| action | string | Action: `play` / `garbage` / `click_red` / `download`, etc. |
| hash | string | Current song hash |
| songid | string | Song ID |
| playtime | string/number | Elapsed play time |
| song_pool_id | string/number | Song pool ID |
| remain_songcnt | number | Remaining song count |
| is_overplay | number | Whether playback finished |

### Users and Login

| Route | Module File | Description |
|------|-------------|------|
| `/login` | `login.js` | Account login |
| `/login/cellphone` | `login_cellphone.js` | Phone verification-code login (params `mobile`, `code`) |
| `/login/qr/key` / `/login/qr/create` / `/login/qr/check` | `login_qr_*.js` | Three-step QR code login flow |
| `/login/qq/qr/create` / `/login/qq/qr/check` | `login_qq_qr_*.js` | QQ QR code login |
| `/login/wx/create` / `/login/wx/check` | `login_wx_*.js` | WeChat QR code login |
| `/login/token` | `login_token.js` | Token login |
| `/login/device` / `/login/device/kick` | `login_device*.js` | Device login management |
| `/login/openplat` | `login_openplat.js` | Open-platform login |
| `/user/detail` | `user_detail.js` | User details (param `userid`; credentials via cookie/token) |
| `/user/info` | `user_info.js` | User info |
| `/user/verify` | `user_verify.js` | Song playback auth credential (obtains `auth`) |
| `/user/update` / `/user/update/avatar` | `user_update.js` / `user_update_avatar.js` | Update profile/avatar |
| `/user/cloud` family | `user_cloud*.js` | Music cloud: list `/user/cloud`, upload `/user/cloud/upload`, delete `/user/cloud/del`, playback URL `/user/cloud/url`, match `/user/cloud/match` |
| `/user/history` | `user_history.js` | Play history |
| `/user/listen/report` | `user_listen_report.js` | Listening report |
| `/user/preference` / `/user/preference/update` | `user_preference*.js` | Listening preferences |
| `/user/purchased/songs` / `/user/purchased/albums` | `user_purchased_*.js` | Purchased songs/albums |
| `/user/playlist` | `user_playlist.js` | User playlists |
| `/user/follow` family | `user_follow*.js` | Follows, fans, messages |
| `/captcha/sent` | `captcha_sent.js` | Send verification code |
| `/register/dev` | `register_dev.js` | Device registration |

### Comments

| Route | Module File | Description |
|------|-------------|------|
| `/comment/music` | `comment_music.js` | Song comments |
| `/comment/floor` / `/comment/floor/send` | `comment_floor.js` / `comment_floor_send.js` | Comment floors/replies |
| `/comment/count` | `comment_count.js` | Comment counts |
| `/comment/music/classify` / `/comment/music/hotword` | `comment_music_*.js` | Comment categories/hot words |
| `/comment/music/del` | `comment_music_del.js` | Delete a comment |
| `/comment/album` / `/comment/playlist` | `comment_album.js` / `comment_playlist.js` | Album/playlist comments |
| `/favorite/count` | `favorite_count.js` | Favorite counts |

### Videos, Recognition, and Others

| Route | Module File | Description |
|------|-------------|------|
| `/video/detail` / `/video/url` / `/video/privilege` | `video_*.js` | MV details/URL/privilege |
| `/kmr/audio/mv` | `kmr_audio_mv.js` | Song MV info |
| `/audio/match` | `audio_match.js` | Song recognition (PCM audio uploaded as a binary body) |
| `/import/playlist` | `import_playlist.js` | External playlist import |
| `/effects/artist` / `/effects/brand` / `/effects/brand/detail` / `/effects/match` | `effects_*.js` | Effect artists/brands/matching |
| `/get/model` / `/get/mode/info` | `get_model.js` / `get_mode_info.js` | Effect model info |
| `/listen/together/*` | `listen_together_*.js` | Listen Together (rooms, songs, chat, etc.) |
| `/blacklist` / `/blacklist/list` | `blacklist.js` / `blacklist_list.js` | Content blacklist |
| `/server/now` | `server_now.js` | Server time |
| `/playhistory/upload` | `playhistory_upload.js` | Play history reporting |
| `/youth/*` | `youth_*.js` | Youth channels and VIP benefits |

::: tip Naming Notes
Route names come from module file names, so they may differ from "intuitive" naming: artists are `artist_*` (not `singer`), login lives under `/login/*` (not `/user/login`), and user details are `/user/detail` (not `/user/profile`). Routes from the old documentation such as `/song/detail`, `/singer/detail`, and `/recommend/home` do not exist in the current submodule version.
:::

## Implementation Reference

The only integration code on the EchoMusic side is `src/main/server.ts`. It reproduces the upstream `server.js` Express routing logic in-process (IPC mode):

1. **Route dispatch**: on startup it scans `server/module/*.js` to build a route table (without loading immediately); when an `api:request` arrives, it matches the URL exactly, requires the module on demand, and caches the result
2. **Cookie merging**: default device cookies → `cookie` from request params → credentials from the `Authorization` header, in increasing priority
3. **Parameter normalization**: IPC preserves original types; scalar params are converted to strings before dispatch for modules that rely on string methods
4. **Binary bodies**: PCM audio for song recognition and other Buffer bodies are placed into `query.data` and uploaded by the module as octet-stream
5. **Signing and encryption**: request signing (`signParamsKey`), AES/RSA encryption, and device identity are all handled by the submodule and its `server/util/`; the app layer does not participate
6. **Direct audio fetch**: the API only returns the audio URL; the audio stream is fetched directly by echo-audio-player and is never proxied through the frontend

## Disclaimer

The endpoints above are for educational and research reference only. They may change at any time, and EchoMusic keeps its submodule up to date. Do not use these endpoints for any commercial purpose.
