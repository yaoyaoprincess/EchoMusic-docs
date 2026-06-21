---
title: 酷狗 API 参考
---

# 🔌 酷狗 API 参考

本文档提供 EchoMusic 使用到的酷狗音乐公开 API 接口参考。项目基于 [KuGouMusicApi](https://github.com/MakcRe/KuGouMusicApi) 进行 API 调用封装。

::: warning 注意
EchoMusic 不提供任何服务端。所有 API 请求均由客户端直接发起，调用酷狗音乐的公开接口。这些接口仅供学习研究参考。
:::

## API 分类

| 分类 | 说明 |
|------|------|
| 歌曲 | 歌曲信息、音源 URL、歌词获取 |
| 搜索 | 歌曲/歌手/专辑/歌单搜索 |
| 歌手 | 歌手信息、热门歌曲、专辑列表 |
| 专辑 | 专辑信息、曲目列表 |
| 歌单 | 歌单详情、推荐歌单 |
| 排行榜 | 各类榜单数据 |
| 用户 | 登录、用户信息 |
| 推荐 | 首页推荐、私人 FM |

## 歌曲相关

### 获取歌曲详情

获取歌曲的基本信息。

```
GET /song/detail
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| hash | string | 歌曲 hash 值 |

**返回**：

```json
{
  "songName": "歌曲名",
  "singerName": "歌手名",
  "albumName": "专辑名",
  "duration": 240,
  "hash": "xxx",
  "imgUrl": "封面图 URL"
}
```

### 获取音源 URL

获取歌曲播放地址。

```
GET /song/url
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| hash | string | 歌曲 hash |
| quality | string | 音质：`flac` / `320` / `128` |

### 获取歌词

获取 LRC 或 YRC 歌词。

```
GET /lyric
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| hash | string | 歌曲 hash |
| type | string | 歌词类型：`lrc` / `yrc` |

## 搜索相关

### 综合搜索

全局搜索，可搜索歌曲、歌手、专辑。

```
GET /search
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 搜索关键词 |
| type | string | 类型：`song` / `singer` / `album` / `playlist` |
| page | number | 页码 |
| pageSize | number | 每页数量 |

### 搜索建议

搜索输入时的自动补全建议。

```
GET /search/suggest
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 搜索关键词 |

## 歌手相关

### 歌手详情

获取歌手信息和热门歌曲。

```
GET /singer/detail
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| singerId | string | 歌手 ID |

### 歌手歌曲列表

获取歌手的所有歌曲。

```
GET /singer/songs
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| singerId | string | 歌手 ID |
| page | number | 页码 |

### 歌手专辑列表

获取歌手的专辑。

```
GET /singer/albums
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| singerId | string | 歌手 ID |

## 专辑相关

### 专辑详情

获取专辑信息和曲目列表。

```
GET /album/detail
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| albumId | string | 专辑 ID |

## 歌单相关

### 歌单详情

获取歌单信息和歌曲列表。

```
GET /playlist/detail
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| playlistId | string | 歌单 ID |

### 推荐歌单

获取首页推荐的歌单列表。

```
GET /playlist/recommend
```

## 排行榜

获取各类排行榜数据。

```
GET /rank/list
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| rankId | string | 排行榜 ID |

支持的榜单：
- 飙升榜
- 新歌榜
- 热歌榜
- 原创榜

## 推荐相关

### 首页推荐

获取首页个性化推荐内容。

```
GET /recommend/home
```

### 私人 FM

获取私人 FM 推荐歌曲。

```
GET /fm/recommend
```

返回推荐歌曲列表，基于用户听歌历史。

## 用户相关

### 登录

用户账号登录。

```
POST /user/login
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| username | string | 用户名/手机号 |
| password | string | 密码（加密后） |

### 用户信息

获取当前登录用户信息。

```
GET /user/profile
```

## 实现参考

EchoMusic 的后端服务（`server/`）负责封装以上 API 调用：

- `server/services/kugou.ts` — 统一的 API 调用客户端
- `server/routes/` — API 路由层，将酷狗 API 转换为前端友好的接口

### 关键实现细节

1. **请求签名**：部分 API 需要签名验证，服务端会自动处理签名逻辑
2. **Cookie 管理**：登录后的 Cookie 由服务端管理，保持会话状态
3. **错误处理**：统一的错误码处理，返回前端友好的错误信息
4. **缓存**：热门数据使用内存缓存，减少 API 调用频率
5. **流式传输**：音源 URL 直接传递给 libmpv，不经过前端中转

## 免责声明

以上 API 接口仅为学习研究参考。接口可能随时变更，EchoMusic 会及时跟进更新。请勿将这些接口用于任何商业用途。