---
title: Kugou API Reference
---

# 🔌 Kugou API Reference

This document provides a reference for the Kugou Music public API endpoints used by EchoMusic. The project uses [KuGouMusicApi](https://github.com/MakcRe/KuGouMusicApi) for API call encapsulation.

::: warning
EchoMusic does not provide any server. All API requests are made directly from the client, calling Kugou Music's public endpoints. These endpoints are for educational and research reference only.
:::

## API Categories

| Category | Description |
|------|------|
| Songs | Song info, audio URL, lyrics retrieval |
| Search | Song / artist / album / playlist search |
| Artists | Artist info, popular songs, album list |
| Albums | Album info, track list |
| Playlists | Playlist details, recommended playlists |
| Charts | Various chart data |
| Users | Login, user profile |
| Recommendations | Home recommendations, Personal FM |

## Song Endpoints

### Get Song Details

Retrieves basic song information.

```
GET /song/detail
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| hash | string | Song hash value |

**Response**:

```json
{
  "songName": "Song Name",
  "singerName": "Artist Name",
  "albumName": "Album Name",
  "duration": 240,
  "hash": "xxx",
  "imgUrl": "Cover image URL"
}
```

### Get Audio Source URL

Retrieves the song playback URL.

```
GET /song/url
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| hash | string | Song hash |
| quality | string | Quality: `flac` / `320` / `128` |

### Get Lyrics

Retrieves LRC or YRC lyrics.

```
GET /lyric
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| hash | string | Song hash |
| type | string | Lyrics type: `lrc` / `yrc` |

## Search Endpoints

### General Search

Global search for songs, artists, albums.

```
GET /search
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| keyword | string | Search keyword |
| type | string | Type: `song` / `singer` / `album` / `playlist` |
| page | number | Page number |
| pageSize | number | Items per page |

### Search Suggestions

Auto-complete suggestions during search input.

```
GET /search/suggest
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| keyword | string | Search keyword |

## Artist Endpoints

### Artist Details

Retrieves artist info and popular songs.

```
GET /singer/detail
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| singerId | string | Artist ID |

### Artist Songs

Retrieves all songs by an artist.

```
GET /singer/songs
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| singerId | string | Artist ID |
| page | number | Page number |

### Artist Albums

Retrieves albums by an artist.

```
GET /singer/albums
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| singerId | string | Artist ID |

## Album Endpoints

### Album Details

Retrieves album info and track list.

```
GET /album/detail
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| albumId | string | Album ID |

## Playlist Endpoints

### Playlist Details

Retrieves playlist info and song list.

```
GET /playlist/detail
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| playlistId | string | Playlist ID |

### Recommended Playlists

Retrieves recommended playlists for the home page.

```
GET /playlist/recommend
```

## Charts

Retrieves chart data.

```
GET /rank/list
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| rankId | string | Chart ID |

Supported charts:
- Rising Chart
- New Song Chart
- Hot Song Chart
- Original Chart

## Recommendation Endpoints

### Home Recommendations

Retrieves personalized home page recommendations.

```
GET /recommend/home
```

### Personal FM

Retrieves Personal FM recommended songs.

```
GET /fm/recommend
```

Returns a list of recommended songs based on listening history.

## User Endpoints

### Login

User account login.

```
POST /user/login
```

**Parameters**:

| Parameter | Type | Description |
|------|------|------|
| username | string | Username / Phone number |
| password | string | Password (encrypted) |

### User Profile

Retrieves the currently logged-in user's information.

```
GET /user/profile
```

## Implementation Reference

EchoMusic's backend service (`server/`) encapsulates these API calls:

- `server/services/kugou.ts` — Unified API client
- `server/routes/` — API route layer, converts Kugou API to frontend-friendly interfaces

### Key Implementation Details

1. **Request signing**: Some APIs require signature verification — the server handles signing logic automatically
2. **Cookie management**: Post-login cookies are managed by the server to maintain session state
3. **Error handling**: Unified error code handling, returning frontend-friendly error messages
4. **Caching**: Popular data uses in-memory caching to reduce API call frequency
5. **Streaming**: Audio source URLs are passed directly to libmpv without going through the frontend

## Disclaimer

The above API endpoints are for educational and research reference only. Endpoints may change at any time — EchoMusic will keep up with updates accordingly. Do not use these endpoints for any commercial purposes.