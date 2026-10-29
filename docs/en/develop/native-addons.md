---
title: Native Addons (Rust NAPI)
---

# 🦀 Native Addons (Rust NAPI)

EchoMusic's performance-sensitive and platform-sensitive capabilities live in **9 Rust crates**, compiled via the [napi-rs](https://napi.rs/) framework (**NAPI 3**) into Node.js native modules (`.node`) loaded directly in the **Electron main process**. The renderer never touches native modules directly — every call goes through main-process wrappers exposed over IPC (`window.electron`).

- Rust toolchain requires **rust-version 1.87** (uniform across crates).
- The NAPI dependency is uniformly `napi = { version = "3", features = ["napi9", ...] }`: the player additionally enables `serde-json` and `tokio_rt`; modules that need async runtimes enable `tokio_rt`.
- Each crate builds into a **`.node` file named after the crate** (e.g. `native/echo-audio-capture/echo-audio-capture.node`), produced by the napi-rs CLI together with an `index.d.ts` type declaration. There is **no** manual rename to `index.node`.

## Module Overview

8 ship with the installer; 1 is an internal dependency only:

| Module | Purpose | Distribution platforms |
|--------|---------|------------------------|
| `echo-audio-player` | Playback, decoding and effects (FFmpeg + SoundTouch) | macOS / Windows / Linux |
| `echo-audio-capture` | System audio and microphone capture (song recognition) | macOS / Windows / Linux |
| `echo-media-controls` | System media controls (SMTC / MPRIS / MPNowPlayingInfoCenter) | macOS / Windows / Linux |
| `echo-sqlite-store` | SQLite persistence | macOS / Windows / Linux |
| `echo-opencc` | Chinese script conversion for lyrics | macOS / Windows / Linux |
| `echo-upnp` | DLNA / UPnP device control | macOS / Windows / Linux |
| `echo-airplay` | AirPlay discovery and audio streaming | macOS / Windows / Linux |
| `echo-platform-adaptor` | Window, taskbar and other platform integration | macOS / Windows (not built on Linux) |
| `echo-native-log` (internal) | Native → main-process log bridge, depended on by other crates | — (not shipped) |

> Every crate uses **functional exports** (free functions annotated with `#[napi]`); there is no class-based API. The rest of this page documents each crate's purpose, platforms, and exported NAPI function signatures.

---

## echo-audio-player — Playback Engine

The core playback engine: FFmpeg decoding + effects + output. All DSP runs inside the playback process — no sidecar process, no PCM IPC.

```toml
[dependencies]
napi = { version = "3", features = ["napi9", "serde-json", "tokio_rt"] }
ffmpeg_audio = { path = "vendor/ffmpeg-audio/crates/ffmpeg_audio", features = ["http"] }
cpal = "0.18"
fundsp = "0.23"
libloading = "0.8"
rubato = "0.16"
rustfft = "6.4"
soundtouch-rs = { path = "vendor/soundtouch-rs" }
```

### Key dependencies and subsystems

| Dependency / subsystem | Description |
|------------------------|-------------|
| FFmpeg (vendored) | Full path: `native/echo-audio-player/vendor/ffmpeg-audio/crates/ffmpeg_audio_sys/vendor/`. `ffmpeg-audio` is itself vendored (containing the `ffmpeg_audio` / `ffmpeg_audio_sys` / `ffmpeg_wasm` / `soundtouch` crates) and is unpacked from `ffmpeg_slim.zip` at build time; no system FFmpeg needed |
| cpal 0.18 | Cross-platform audio output. On Linux the `pipewire` / `pulseaudio` features are enabled (PipeWire / PulseAudio backends); WASAPI (Windows), CoreAudio (macOS) and ALSA (Linux) provide exclusive output (`src/output/wasapi.rs`, `coreaudio_exclusive.rs`, `alsa_exclusive.rs`, `cpal_shared.rs`) |
| fundsp + rustfft | Built-in EQ and IR convolution and other basic DSP (`src/dsp/basic.rs`, `src/dsp/limiter.rs`) |
| soundtouch-rs (vendored) | Tempo (WSOLA) engine |
| rubato | High-quality resampling |
| libloading | Runtime dynamic loading of external DSP providers (`src/dsp/provider.rs`) |
| `src/transition/` | Track-transition subsystem: 8 JSON transition plans (`plans/`: `echo_tail`, `fallback_exchange`, `filter_eq`, `layered_filter`, `simple_exchange`, `simple_filter`, `smooth_filter`, `three_band`) plus analysis (`analysis.rs`), decision (`decide.rs`), mixing (`mixer.rs`), plans (`plan.rs`) and effects (`effects.rs`) |
| `src/tempo.rs` | Dual tempo engine: spectral phase vocoder + SoundTouch (WSOLA), speed range **0.1x – 5x** (`MIN_SPEED = 0.1`, `MAX_SPEED = 5.0`) |
| `src/audio_graph.rs` | Audio processing graph snapshot with runtime parameter/plan adjustments |
| `src/stream/` | HTTP streaming (proxy, timeouts, pause caching), local files, URL resolution |
| `src/device/` | Output device enumeration/selection/hot-plug watching (`watcher.rs`, `selection.rs`, per-platform `platform_*.rs`) |
| `src/spectrum.rs` | Engine built-in real-time spectrum (for audio visualizer subscriptions) |
| `src/embedded_metadata.rs` | Embedded metadata (tags/cover) reading |
| `src/output/airplay_tap.rs` | Output tap used when streaming to AirPlay |

### Exported NAPI functions

Initialization and events:

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize` | `(config: PlayerConfigOptions \| null) → void` | Initialize the engine (buffering, sample-rate/channel/format policies, gapless policy, cache, network timeout, HTTP proxy, etc. — see `src/config.rs`) |
| `destroy` | `() → void` | Tear down the engine |
| `register_event_handler` | `(callback: EventCallback) → void` | Register playback event callback (progress, state, end, errors, device changes, etc.) |
| `register_log_handler` | `(callback) → void` | Register log callback (bridged to main-process electron-log via echo-native-log) |

Loading and source switching (gapless / source-change group):

| Function | Signature |
|----------|-----------|
| `begin_source_change` | `() → void` |
| `load_file` | `(url: string, seq?: number) → AsyncTask` |
| `load_mkv_track` | `(url: string, track_id: number, seq?: number) → AsyncTask` |
| `switch_source` | `(url: string, track_id?: number \| null, ...) → AsyncTask` |
| `begin_next_source_preparation` | `() → number` (returns requestId) |
| `cancel_next_source_preparation` | `(request_id: number) → boolean` |
| `prepare_next_source` | `(url: string, request_id: number, track_id?: number \| null, normalization_gain_db?: number) → AsyncTask` |
| `commit_prepared_next_source` | `(transition_ms?: number) → ...` |
| `clear_prepared_next_source` | `() → void` |
| `get_track_list` | `(url?: string) → AsyncTask` |

Playback control and basic processing:

| Function | Signature |
|----------|-----------|
| `play` / `pause` / `stop` | `() → AsyncTask / void` |
| `seek` | `(time: f64) → AsyncTask` |
| `set_volume` | `(volume: f64) → void` |
| `set_speed` | `(speed: f64) → AsyncTask` (0.1x – 5x, dual engine) |
| `set_equalizer` | `(gains: Vec<f64>) → AsyncTask` (10 bands) |
| `set_audio_effect` | `(payload: JSON) → AsyncTask` (IR / VPF resources + DSP provider config) |
| `set_normalization_gain` | `(gain_db: f64) → AsyncTask` |
| `fade` / `cancel_fade` / `pause_with_fade` / `play_with_fade` | Volume fade group |
| `set_loop_file` | `(loop_file: bool) → void` |
| `get_state` | `() → PlayerState` |
| `get_embedded_metadata` | `(request) → ...` |

Output devices and networking:

| Function | Signature |
|----------|-----------|
| `set_audio_output` | `(device_name: string, exclusive: bool) → AsyncTask` |
| `get_audio_devices` | `() → AsyncTask` |
| `set_pause_on_device_disconnect` | `(enabled: bool) → void` |
| `set_stall_timeout` | `(seconds: f64) → void` |
| `set_network_timeout` | `(seconds: f64) → void` |
| `set_http_proxy` | `(proxy: string) → void` |
| `set_http_proxies` | `(proxies: Vec<string>) → void` |

Audio graph / transitions / spectrum / providers:

| Function | Signature |
|----------|-----------|
| `get_audio_graph` / `set_audio_graph_parameter` / `set_audio_graph_plan` | Audio graph snapshot and runtime adjustments |
| `set_transition_settings` / `get_transition_settings` / `get_transition_diagnostics` | Transition modes (`none` / `gapless` / `fade` / `automix-basic` / `automix-pro`), fade duration, tempo matching |
| `inspect_dsp_provider` | `(path: string) → AsyncTask` (validate an external provider before import) |
| `configure_spectrum` / `get_spectrum_status` / `get_spectrum_snapshot` | Spectrum configuration and frame snapshots |

### JS-side wrapper

The main-process wrapper lives in `src/main/player/`: `controller.ts` (~44KB, engine lifecycle and IPC command mapping), `session.ts` (runtime session), `dspProviderRegistry.ts` (installed provider registry), `audioEffectCommand.ts`, `embeddedMetadata.ts`, etc. The renderer calls it via `electron.player.*` (preload) — see the [Audio Engine](/en/develop/internal-api/audio-engine) page.

---

## echo-media-controls — System Media Controls

Bridges each OS's native media control API. Functional exports:

| Platform | API |
|----------|-----|
| Windows | SMTC (WinRT `SystemMediaTransportControls`, `windows` 0.62 crate) |
| Linux | MPRIS (D-Bus, `mpris-server` crate) |
| macOS | MPNowPlayingInfoCenter / MPRemoteCommandCenter (`objc2-media-player`) |

**NAPI exports**:

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize` | `(app_name: string) → void` | Initialize the media control session |
| `shutdown` | `() → void` | Close the session |
| `register_log_handler` | `(callback) → void` | Log bridging |
| `update_metadata` | `(payload: { title, artist, album, coverUrl?, durationMs? }) → AsyncTask` | Update track metadata (cover loaded by URL) |
| `update_play_state` | `(payload: { status, playbackRate }) → void` | Play/pause state |
| `update_timeline` | `(payload: { currentTimeMs, totalTimeMs, isPlaying, playbackRate }) → void` | Progress bar |
| `update_skip_intervals` | `(payload: { forwardMs, backwardMs }) → void` | Skip forward/backward step |
| `register_event_handler` | `(callback: ThreadsafeFunction<MediaControlEvent>) → void` | System media key events (play/pause/next/previous/seek, etc.) |

Main-process wrapper: `src/main/mediaControls.ts`, exposed to the renderer as `electron.mediaControls.*`.

---

## echo-sqlite-store — SQLite Persistence

SQLite persistence built on `rusqlite 0.32` (`bundled` + `backup` features — SQLite is statically compiled into the binary). **Functional exports** (no `Storage` class); payloads and return values are JSON strings (`serde_json`), wrapped by the main process in `src/main/storage/native.ts`.

**Database tables** (created in `initialize`):

| Table | Key columns | Purpose |
|-------|-------------|---------|
| `app_kv` | `key` PK, `value_json`, `updated_at` | Generic key-value store |
| `playback_queues` | `id` PK, `title`, `subtitle`, `cover_url`, `type`, `active`, `last_non_fm`, `current_track_id`, `filtered_invalid_count`, `queued_next_track_ids_json`, `dynamic`, `meta_json`, timestamps | **Multi-queue** model (FM / default / playlist etc. are separate queues) |
| `songs` | `song_key` PK, `source_id`, `hash`, `title`, `artist`, `album`, `cover_url`, `duration`, `payload_json` | Deduplicated song pool |
| `queue_items` | `(queue_id, position)` PK, `song_key`, `added_at`, cascading foreign keys | Ordered queue entries |
| `play_history` | `song_key` PK, `history_key` UNIQUE, `last_played_at`, `play_count` | Play history (aggregated per song) |

> ⚠️ **There is no favorites table.** Favorites are cloud-side KuGou account data and are not persisted through this module.

**NAPI exports**:

```rust
initialize(database_path: String)            close()
kv_get(key) / kv_set(key, value_json)        kv_apply_batch(mutations_json)
kv_delete(key) / reset_all()
playback_get_snapshot(hydrate_all_songs?)    playback_get_queue(payload_json)
playback_replace_queue(payload_json)         playback_append_queue_items(payload_json)
playback_update_queue_meta(payload_json)     playback_clear_queue(payload_json)
playback_remove_queue(payload_json)          playback_remove_queue_item(payload_json)
playback_reorder_queue_items(payload_json)   playback_set_queue_current_track(payload_json)
playback_set_active_queue(queue_id)
history_get_entries(payload_json?)           history_record_play(payload_json)
history_remove_entries(payload_json)         history_clear()
plugin_sqlite_open(plugin_id, ...)           plugin_sqlite_close(database_id)
plugin_sqlite_close_by_prefix(prefix)        plugin_sqlite_exec(database_id, sql)
plugin_sqlite_run(database_id, sql, params?) plugin_sqlite_all(database_id, sql, params?, ...)
plugin_sqlite_transaction(database_id, statements_json)
plugin_sqlite_backup(source_path, destination_path)
```

The `plugin_sqlite_*` series backs **plugin databases** (consumed by `src/main/plugins/sqlite.ts`) with isolated database files and SQL execution; the plugin-facing API is documented in [Plugin SQLite Storage](/en/develop/plugin-dev/filesystem-storage). The preload surface is `electron.storage.*` — see [Playback State & Persistence](/en/develop/internal-api/playback-state).

---

## echo-audio-capture — System Audio Capture

System audio + microphone capture for **song recognition**. Captures via `cpal 0.18`, resamples PCM via `rubato 0.16`, with dual sources (`system` loopback / `input` microphone) that can be mixed or selected individually.

**NAPI exports**:

| Function | Signature | Description |
|----------|-----------|-------------|
| `list_input_devices` | `() → Vec<CaptureDevice>` | List capture devices |
| `start_capture` | `(options: CaptureStartOptions) → CaptureStatus` | Start capture (sources, device, sample rate, etc.) |
| `snapshot_capture` | `(options: CaptureReadOptions?) → CapturedAudio` | Read a snapshot of captured PCM |
| `stop_capture` | `(options: CaptureReadOptions?) → CapturedAudio` | Stop and return the full PCM |
| `cancel_capture` | `() → void` | Cancel and discard |
| `get_capture_status` | `() → CaptureStatus` | Query capture status |

Main-process wrapper: `src/main/audioCapture.ts`, exposed as `electron.recognize.*`.

---

## echo-opencc — Chinese Script Conversion

Simplified/Traditional Chinese conversion for lyrics, based on `opencc-fmmseg 0.12`.

**NAPI exports**:

| Function | Signature | Description |
|----------|-----------|-------------|
| `convert` | `(text: string, profile: string) → string` | Convert one string |
| `convert_batch` | `(texts: Vec<string>, profile: string) → Vec<string>` | Batch conversion (preload `opencc.convertBatch`) |

**Supported profiles (5)**: `s2t` (Simplified → Traditional), `s2t-variants` (Simplified → Traditional with character variants, composed as `tw2t(s2t(text))`), `t2s` (Traditional → Simplified), `s2tw` (Simplified → Taiwan standard), `s2hk` (Simplified → Hong Kong Traditional). Dictionaries live in `native/echo-opencc/dicts/`.

Main-process wrapper: `src/main/opencc/` + `src/main/ipc/opencc.ts`.

---

## echo-upnp — DLNA / UPnP

Wraps the vendored `rupnp 3.0` (`vendor/rupnp`, with the `full_device_spec` feature) to provide device discovery and control for **network casting (DLNA)**.

**NAPI exports**:

| Function | Signature | Description |
|----------|-----------|-------------|
| `load_device` | `async (description_url: string) → UpnpDeviceSnapshot` | Load a device description document (cached) |
| `action` | `async (description_url, service_id, action_name, args_xml) → string` | Invoke a UPnP service action |
| `clear_device_cache` | `() → void` | Clear the device description cache |

> The `vendor/` directory also vendors `airplay2-rs` (split into the `airplay-client` / `airplay-audio` / `airplay-discovery` / `airplay-core` crates), reused by `echo-airplay`.

Main-process wrapper: `src/main/mediaTransport/upnpClient.ts` (DLNA adapter, GENA event subscription, etc. live in `src/main/mediaTransport/`).

---

## echo-airplay — AirPlay Sender

AirPlay audio sender. Cargo description: **"EchoMusic AirPlay sender. ALAC 44100 Hz 16-bit from post-DSP i16 PCM."** — i.e. post-DSP i16 PCM is encoded to ALAC 44.1kHz 16-bit for streaming. Reuses the `airplay2-rs` client / audio / discovery / core crates from `echo-upnp/vendor/`.

**NAPI exports**:

| Function | Signature | Description |
|----------|-----------|-------------|
| `discovery_backend` | `() → string` | Current discovery backend identifier |
| `discover` | `async (timeout_ms: u32) → Vec<AirplayFound>` | Discover AirPlay receivers |
| `discover_each` | `async (...)` | Incremental discovery (per-device callback) |
| `connect` | `async (id: string, pin: string, initial_volume?: f64) → AirplayLink` | Connect (supports pairing PIN) |
| `disconnect` / `pause` / `resume` / `stop` | `async () → void` | Session control |
| `seek` | `async (seconds: f64) → u32` | Seek |
| `set_volume` | `async (volume: f64) → void` | Receiver volume |
| `flush_track` | `async () → u32` | Flush the current track |
| `status` | `() → AirplayState` | Session state |
| `clear_records` | `() → void` | Clear records |
| `register_log_handler` | `(callback) → void` | Log bridging |

The main-process wrapper lives in `src/main/outputs/` (`outputHost.ts` is ~75KB and manages DLNA / AirPlay output sessions uniformly), exposed as `electron.output.*` — see the network casting section of [Window & Interaction Management](/en/develop/internal-api/window-management).

---

## echo-platform-adaptor — Platform Window Integration

Windows and macOS desktop window integration, owning HWND/DWM behavior and local AppKit mouse observation. It contains **no** SMTC/MPRIS/Now Playing lifecycle or audio dependencies (that is `echo-media-controls`'s job).

| Platform | Capabilities |
|----------|--------------|
| Windows | DWM transparent/acrylic composition (`window_composition.rs`: DWM alpha clear and Accent BlurBehind backends, coordinating with Electron `setBackgroundMaterial` on Win11 22H2+), **taskbar lyric embedding** (`windows/taskbar/lyric.rs`, reparenting into the primary `Shell_TrayWnd` with UIA structure notifications + WinEvent layout), DWM thumbnail / Aero Peek cover previews (`taskbar/thumbnail.rs`, bounded BGRA/GDI caches), native double-click observation (`double_click.rs`), HWND destruction-order fix (`taskbar/window_lifecycle.rs`) |
| macOS | Local mouse-down monitor for the main window (`macos/window_pointer.rs`; forwards every event unchanged, does not observe other applications, needs no Accessibility permission) |
| Linux | **Not built, not packaged** (no such `.node` exists on Linux) |

The upstream README (`native/echo-platform-adaptor/README.md`) documents composition modes (mode 5/10/11/12), the Explorer-restart crash fix (on Explorer restart the lyric HWND can receive `WM_NCDESTROY` without `WM_DESTROY`, tripping Chromium's observer-destructor CHECK; `window_lifecycle.rs` reinstates the missing `WM_DESTROY` phase via a subclass), known Windows 10 failure scenarios, and the diagnostic workflow.

**Key NAPI exports** (platform-gated):

| Function | Platform | Description |
|----------|----------|-------------|
| `set_window_composition` | Windows | Set composition mode (`handle, mode, keep_on_blur?, tint?`) |
| `get_window_composition_diagnostics` | Windows | Read back Accent / DWM backdrop / layered styles etc. |
| `set_window_force_active_appearance` | Windows | Keep the frosted look on blur (WCA_FORCE_ACTIVEWINDOW_APPEARANCE) |
| `taskbar_thumbnail_enable` / `_disable` / `_set_cover` | Windows | DWM thumbnail/Peek enable/disable and cover bitmaps |
| `taskbar_lyric_mounted_taskbar` etc. (`TaskbarLyricSession`) | Windows | Taskbar lyric embedding session (mount / layout update / stop) |
| `start_windows_double_click_monitor` / `stop_...` / `get_windows_double_click_diagnostics` | Windows | Native double-click monitor |
| `start_window_pointer_monitor` / `stop_...` | macOS | Local mouse monitor |

Main-process wrapper: `src/main/native/platform.ts` (shared loader + API validation) and `src/main/native/logging.ts` (log bridging).

---

## echo-native-log — Native Log Bridge (internal dependency)

A shared **native → main-process** log bridge crate. It is not a `.node` addon but a plain Rust library referenced by other crates as a path dependency (`echo-native-log = { path = "../echo-native-log" }`):

- `set_log_handler(callback)`: registered by each host addon at startup (every addon's `register_log_handler` forwards here);
- `emit(level, message)`: called from inside the crates, delivering via `ThreadsafeFunction` to the main process.

On the main-process side, `src/main/native/logging.ts` normalizes callbacks to `debug | info | warn | error` and writes them into electron-log, so native logs appear in the unified main-process log. **Not shipped with the installer** (it is statically linked into each `.node`).

---

## Developing Native Modules

### Building a single module

```bash
# Install dependencies (first time)
cd native/<module>
npm install

# Debug / release build (napi-rs CLI; outputs <crate-name>.node + index.d.ts)
npm run build          # or npx napi build --release
```

Each crate's `Cargo.lock` is committed for reproducible dependency resolution. Cross-target type checking (e.g. checking the Windows target from macOS):

```bash
cargo check --manifest-path native/<module>/Cargo.toml --target x86_64-pc-windows-msvc --locked
```

### Loading in the main process

- Development: loaded directly from `native/<module>/<module>.node`;
- Packaged: located at `resources/native/<module>.node` (e.g. `echo-platform-adaptor` is resolved by `src/main/native/platform.ts` depending on `app.isPackaged`).
- Rebuild the addon and **restart the app** for changes to take effect.

### Debugging tips

- Addons bridge Rust-side logs into main-process electron-log via `register_log_handler` (see echo-native-log); check the unified main-process log. **Do not** rely on `println!` (invisible in packaged builds).
- VS Code + rust-analyzer recommended. Windows behaviors (DWM, taskbar, exclusive output) must be validated on a real desktop; cross-platform `cargo check` and browser fixtures are not a substitute.

## Reference

- [napi-rs documentation](https://napi.rs/)
- [FFmpeg documentation](https://ffmpeg.org/documentation.html)
- [SoundTouch audio library](https://www.surina.net/soundtouch/)
- [MPRIS specification](https://specifications.freedesktop.org/mpris-spec/latest/)
- [Upstream DSP Provider architecture](https://github.com/hoowhoami/EchoMusic/blob/main/docs/dsp-provider-architecture.md) (repo `docs/`)
- [Upstream platform adaptor README](https://github.com/hoowhoami/EchoMusic/blob/main/native/echo-platform-adaptor/README.md)
