---
title: Changelog
sidebar: false
---

# Changelog

This page records the major version updates for EchoMusic. For the complete changelog, see [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases).

> ⚠️ This software is completely free and open-source. Do not obtain it through any paid channels.
>
> 🤡 If you acquired it by paying, you've been scammed.

> **🔔 Translation pending: 2.3.3**
> Automatic translation failed for these versions, so their notes below are shown in Chinese. Please refer to the Chinese changelog for reference.

## [2.3.3-beta.6] - 2026-11-28

### 新增

- 新增音效市场搜索功能
- 应用菜单「窗口」新增「关闭窗口」项，快捷键 ⌘W（Windows / Linux 为 Ctrl+W）
- 实验性设置支持导入用户信息并复用登录状态
- 网络设置中新增自定义 User-Agent 设置，可分别控制不同模块的请求头
- 空格键暂停/播放当前歌曲
- 插件支持通过 manifest `requires.platforms` 声明支持平台（windows/macos/linux）：不支持当前平台的插件在市场与本地安装/更新时会被拒绝，卡片展示平台标签与「平台不支持」原因
- 歌词页新增外观模式设置，提供深色 / 浅色 / 跟随主程序三档（默认深色）：浅色档基于封面主色提亮生成背景并降低饱和度，歌词背景、默认歌词色、皮肤配色与 AMLL 文字色等全链路按档位分色

### 优化

- 优化歌词行切换的性能消耗
- 优化windows任务栏快捷控制图标显示
- 优化在线插件加载失败时的提示：网络错误（DNS 解析失败、连接超时、连接被重置、代理不可用等）将展示为分类后的友好文案，并支持通过「显示详情」查看与复制原始错误、一键打开网络设置
- 退出登录时可选择是否保留账号数据，如选择保留可以直接恢复登录
- 开发者模式开放 CDP 调试端口，支持使用 chrome-devtools-mcp 调试应用
- 输入框新增右键菜单，支持复制，粘贴等操作
- 重构「播放历史」的听歌统计页，对齐 EchoMusicNext 新版视觉：新增单曲循环、最常听专辑黑胶插画、35 天听歌足迹热力日历、24 小时音乐时钟、偏爱的歌手榜与私人重播册歌曲网格，统计数字支持滚动动画，并支持一键复制统计分享图
- 本地播放历史上限由 500 条提升至 1000 条
- 听歌统计的「已记录时长」接入本地实听累计：暂停、seek、卡顿不计时，播放中周期结算；总时长由独立聚合存储承载，不随历史裁剪、单条删除或清空历史而减少

### 修复

- 修复 macOS 控制中心两侧显示快进/快退的问题，改为上一首/下一首，保留进度拖动
- 修复音频独占无法关闭的问题
- 修复 Windows 共享模式下切换输出设备后播放报「音频加载失败」的问题：启动超时会在同端点自动重试，日志中记录启动卡点与 HRESULT 便于排查
- 修复 macOS「显示/隐藏窗口」快捷键行为：仅保留全局快捷键，隐藏时跟随 Dock / 菜单栏隐藏设置，窗口被遮挡或在其他桌面时置前而非隐藏
- 修复探索页歌单误报「已收藏」、点击取消收藏会误删其他已收藏歌单的问题：收藏判定改用全局唯一 gid 匹配，gid 无法直接对照时回退「创建者账号 + 列表号」组合键（含历史收藏条目只有收藏者侧 gid 的情况），不再使用按账号分配的裸 listid
- 修复 Apple Music 皮肤歌词没有正确使用歌词字体
- 修复 Fedora / RHEL 系发行版无法安装 RPM 包的问题：依赖 libpulse 改为跨发行版布尔依赖（pulseaudio-libs / libpulse0 / libpulse）
- 修复部分歌曲无法播放，提示歌曲不支持问题
- 修复首次打开 mini 窗口报错问题
- 修复插件浮窗内的 https 外链（`target=_blank` / `window.open`）被静默拦截、点击无响应的问题：现改为交给系统浏览器打开，窗口内页面导航仍保持禁止
- 修复插件市场和本地 ZIP 安装丢失可执行权限，导致插件原生程序无法启动且不弹出授权提示的问题
- 修复 Apple Music 皮肤暂停播放时调整窗口大小后歌词布局不重算，字号与间距停留在旧值的问题
- 修复听歌统计的本地实听时长恒为 0 的问题：响应式 Proxy 对象传入 IPC 时无法被结构化克隆，实听时长在静默失败中丢失

## [2.3.2] - 2026-10-26

### Added

- Added reading of embedded metadata during playback to fill in missing title, artist, album and cover, with embedded lyrics offered as candidates
- Added manual search to the lyrics selection dialog: edit the title and artist to look up lyrics, and remember the selected version for the current song
- Added an MV audio fallback, available in "Playback Experience" and disabled by default
- Added Windows taskbar lyrics
- Added plugin file authorization, streaming download and media reading APIs, supporting external large-file resources
- Added unified "Authorized Files and Directories" management, with support for revoking authorization and removing records
- Added multi-account switching management
- Added multi-select for playlists and lists in "Add to"
- Added a Concept Edition free-listening feature, preserving the playback queue and app configuration
- Added cover-following colors for desktop and Mini lyrics
- Added a richer personal profile display
- Added 3 new Viper quality tiers
- Added a brand-new sidebar layout with layout editing
- Added a unified Theme Center
- Added separate macOS toggles for hiding the Dock and menu bar icons when running in the background
- Added a "Song Replay" feature
- Added Simplified/Traditional Chinese conversion settings for lyrics, supporting Original, Simplified, Traditional, Variant Traditional, Taiwan Standard and Hong Kong Traditional
- Added a global lyric time offset setting, calibrating the play page, desktop lyrics, Mini lyrics and taskbar lyrics together
- Added a settings button on the desktop lyrics window to open lyrics settings directly
- Added Friends, Following, Followers and Visitors drawers in the profile center, supporting relationship lists and text private messaging
- Added discovering and connecting to DLNA / AirPlay devices
- Added a "More" menu and layout editing for the player bar
- Added MV favoriting and unfavoriting
- Added Plugin Management to the title bar "More" menu
- Added a plugin local WebSocket API
- Added a "Beat Alignment" toggle for Rhythm Fusion, disabled by default
- Added a service request interception plugin API
- Added skin switching for page lyrics
- Added editing of user-created playlist info: cover image, name, tags and description
- Added automatic cover updating for user-created playlists
- Added custom sorting for playlist songs and the sidebar playlist list
- Added the song transition feature and its settings
- Added TCP plugin API capability
- Added listening preference settings, viewable and configurable in the profile center
- Added animated album covers, supporting lyrics cover mode and muted looping display on album details, falling back to static covers when unavailable
- Added "More Apps": pin or unpin built-in and plugin actions directly, with drag-to-reorder icons in the popup and top bar, auto-saved layouts and a reset-to-default option
- Added a unified plugin title bar API, supporting default position, in-app tooltips and dynamic state
- Added level details: click the level in the profile center to view experience progress, the gap to the next level, and refresh
- Added plugin update checks after startup, viewable in the Task Center with individual or batch updates and retries for failed items
- Added an extended plugin task API, supporting pending-action states, task details and disabled action buttons
- Added a sleep timer
- Added comment posting for songs, playlists and albums, with support for viewing threaded replies and replying to specific comments
- Added danmaku (bullet comment) display and posting on the lyrics page and MVs

### Improved

- Improved window throttling configuration logic
- Improved automatic lyrics matching, querying in order by song hash, artist & title, then embedded tags
- Native dialogs now uniformly prefix their titles with the app name, making it easier to tell where a dialog comes from
- Improved the taskbar lyrics line-switching animation, now scrolling the main and secondary lines upward as a whole block
- Improved tooltip interaction and styling, reducing duplicate tooltips and list rendering overhead
- Removed player popup arrows and unified spacing, reducing extra material drawing and geometry listeners
- Improved the startup display and startup error messages
- Replaced some feature entry icons
- Improved the Windows taskbar cover preview
- Improved plugin installation with streaming downloads to reduce memory usage
- Improved the plugin management page and authorization dialog; directory selection now supports creating new folders
- Improved the playback page background rhythm animation performance
- Improved the settings dialog loading logic
- Improved the quality switching UI and logic
- Improved playback error message logic and styling
- Improved song playback URL fetching logic
- Improved the lyrics settings structure, consolidating general, play page and desktop lyrics configurations, with general translation, transliteration, fine-tune step and lyrics filter settings managed in one place
- Improved plugin native network request failure logs, recording the plugin, request method, sanitized URL and error code for easier connection troubleshooting
- Improved the play page lyrics color fallback: when a skin does not set its own colors, the unified play page lyrics color is used
- Enhanced LRC word-by-word lyrics parsing, supporting inline timestamps to generate word-level lyric timelines
- Improved plugin performance: invisible plugin pages and lyrics skins automatically pause audio spectrum pushes, and hidden plugin windows are allowed to throttle and sleep
- Improved lyrics page performance: word-by-word lyric animations stop per-frame refreshes when the window is hidden or playback is paused, and resume syncing automatically when the window is shown again
- Improved plugin marketplace statistics caching and batch queries to reduce duplicate requests
- Improved the comment page to show user badges, VIP and other info
- Improved Personal FM recommendation pool switching and like/dislike logic, and added a Radio mode
- Adjusted unreasonable minimum and maximum width/height limits in the floating window API
- Improved the sticky header animation implementation for better performance
- MV playback volume now defaults to 50%
- Improved listening time reporting logic
- Improved lyrics progress sync, unifying the timelines of page, desktop, Mini and plugin lyrics for better consistency after track switches, speed changes and buffer recovery
- Improved Music Recognition audio source: system audio is used by default and the last choice is remembered across restarts
- Improved artist detail page sorting: songs and albums each remember their "Newest/Popular" choice across artist switches, page returns and restarts
- Adjusted Windows 10 transparency and frosted glass to share a transparent window, addressing ineffective frosted glass and gray outer edges
- Improved the window title bar with native window control buttons, adapting button positions, UI scaling and fullscreen states
- Improved the settings tab bar with left/right scroll arrows for tabs beyond the visible area; the mouse wheel works too
- Improved online plugin list loading, showing cached content first and checking updates automatically in the background
- Improved plugin description display: hovering over a description longer than two lines shows the full content
- Unified in-app tooltip styling and interaction
- Improved song effect switching interaction, adding a switching state and failure messages
- Improved MV source selection, opening more encodings and resolutions, preferring H.264 by default

### Fixed

- Fixed window throttling configuration causing desktop lyrics desync and similar issues
- Fixed asymmetric margins between the on and off states of switch styling
- Fixed windows not being brought to the front correctly when restoring the app from the tray on macOS
- Fixed the interface becoming unresponsive after clicking outside the dialog, clicking the close button or pressing Esc during cloud drive upload or playlist import
- Fixed native file/message dialogs not showing and freezing the app when attached to the main window
- Fixed brief playback stutter when switching the macOS system light/dark appearance
- Fixed song list button hover offset and the MV icon
- Fixed device names in the cast popup and settings page being squeezed by model info; device info is now shown on separate lines
- Fixed the app exiting on startup when the Windows installation directory lacked sandbox read permissions; permissions are now completed automatically during installation and updates
- Fixed the listening-stats share screenshot leaking the original page and the crop range including page content
- Fixed the play page not closing after clicking MV
- Fixed missing artist and album info when entering the detail page from a shared song, which prevented click-through navigation
- Fixed a regression where the plugin marketplace reported "Redirect was cancelled" when downloading GitHub Release and other redirected resources after streaming download was introduced
- Fixed the AMLL engine's lyrics line mounting order, resolving lyrics falling abnormally from the top during playback when the spring animation was disabled
- Fixed the parent popup closing when the mouse moved over a Tooltip inside it, while preserving nested interaction and normal outside-close behavior
- Fixed long text squeezing switches and deforming their track and knob
- Fixed song transitions not taking effect in shuffle and single-track loop modes
- Fixed sampling time being reset when playback progress was passed across windows, causing persistent sync drift between desktop lyrics and the main window
- Fixed the macOS system Now Playing rate remaining 1 after pausing, making Dynamic Island and other external panels misjudge playback as ongoing and keep advancing progress
- Fixed play commands issued while the audio source was still loading being silently dropped, showing "playing" in the UI with no sound until clicked again
- Fixed heart states updating slowly after adding or removing songs from "Liked Songs", and favorited songs' hearts turning hollow during normal playback and track switching
- Fixed abnormal window behavior on Windows 10 with a transparent background enabled
- Fixed a playback error being wrongly reported when the output device disconnected while "Pause on device disconnect" was enabled
- Fixed tab state being lost after navigating back or refreshing on search, discover, favorites, purchased, history and detail pages
- Fixed the desktop lyrics "Transliteration Style - Phonetic Annotation" setting not being saved after restart
- Fixed switching effects such as vocals and instrumental failing for some songs
- Fixed music stuttering on Windows ARM devices while videos were playing in the browser at the same time
- Fixed incorrect album search results
- Fixed the playback API missing in floating window plugins
- Fixed taskbar lyrics flashing at the top of the screen when exiting the app or closing taskbar lyrics
- Fixed song order display in user-created playlists
- Fixed sticky header animation stuttering while scrolling
- Fixed the Personal FM now-playing card and song title being covered and the scroll jumping at minimum window height
- Fixed playback failing on Windows after switching the system spatial sound
- Fixed the volume value jumping back when adjusting it with the wheel in Mini mode
- Fixed uncaught exceptions when the console log pipe broke
- Fixed the progress bar stopping after seamlessly switching effects or audio sources

## [2.3.1] - 2026-09-09

### Added

- Added listening time reporting
- Added the plugin Graphics API, supporting WebGPU rendering, HDR highlights and SDR fallback
- Added transparent app background and frosted glass effects, with adjustable opacity and base color
- Added a toast style for Mini mode
- Added standalone network settings, supporting follow-system, forced direct connection, WPAD auto-detection, PAC scripts and manual proxy rules
- Added the plugin backup and restore API `ctx.backups`, supporting imperative operations and `registerProvider()` storage providers
- Added backup and restore for app settings, plugins and plugin data
- Added profile and avatar editing
- Added hot-pluggable DSP modules, with dynamic loading and unloading of effect engines
- Added artist effects, headphone effects and an effect marketplace, supporting online browsing, downloading and use of parameter effects, convolution effects and combo effects
- Added a toggle for Photo mode to show the song cover when no photo image is available, disabled by default
- Added a session-based plugin task API, supporting run-generation isolation, `AbortSignal`, explicit terminal-state retention policies and automatic cleanup
- Added the plugin staged audio source takeover and conversion API
- Added the plugin native network request API `ctx.net.request`, issued by the main process through the Axios Node adapter
- Added transliteration phonetic annotation display for lyrics
- Added playlist import from screenshots
- Added a content blacklist
- Added Listen Together
- Added a spectral phase-vocoder time-stretch algorithm to the native playback engine, automatically selecting the optimal engine across the 0.1x-5x speed range for better quality at extreme speeds
- Added a toggle to disable default browser key behaviors (space, arrow keys, page-up/down scrolling and activation)
- Added QQ QR-code login
- Added Windows taskbar playback progress display
- Added login device management in the profile center to view and remove non-local devices
- Added a device identity reset entry to clear local `guid`, `mid`, `dfid` and regenerate on restart
- Added plugin desktop lyrics and Mini player snapshot subscription APIs
- Added Windows taskbar playback progress display
- Added the Effect Community for browsing, downloading and using community spatial effects online
- Added the Effect Community for browsing, downloading and using parameter effects, convolution effects and combo effects online

### Improved

- Improved the Mini mode playlist to use a custom scrollbar
- Improved transparent window edges with a fine stroke adapted to light/dark themes
- Improved app startup loading and animations, reducing the startup white screen and improving page transitions
- Improved the sidebar scroll layout: navigation menu, plugin menu and playlists share one scroll area, so a growing plugin menu no longer squeezes the visible height of playlists; the avatar and settings entries stay fixed
- Improved the macOS update flow, keeping version detection and the changelog, and providing DMG manual download entries matching the arm64/x64 architecture; when the check fails or no matching package is available, you can download from the releases page
- Refactored page sticky header and scrolling logic, compatible with transparent backgrounds
- Improved theme presentation: refactored gradient logic, unified interface colors, and added gradient range and intensity adjustment
- Reduced package size by removing duplicated frontend dependency source code, cutting download size and disk usage after installation
- Improved text and icon contrast for different hue theme colors in light/dark interfaces, and made Mini mode follow preset, custom and cover-derived dynamic theme colors
- Improved Music Recognition audio capture: microphone and system audio now use a unified cross-platform native capture module that outputs PCM directly, avoiding Chromium media capture startup failures and the extra overhead of microphone Opus encoding
- Improved the effect panel when switching between speakers/headphones: engine info, the preset list and the current effect marker are preserved during rebuilds, avoiding panel flicker or briefly flashing back to "Original"
- Plain toasts no longer pause their dismissal countdown on mouse hover; toasts with action buttons resume the countdown after the window loses focus
- Improved the settings page information architecture: "Appearance & Interface" is split into "Themes & Appearance", "Interface Display" and "Window & Startup", with platform-inapplicable options hidden
- Improved native engine manual track switching: the pending source is opened while the old one is still playing, reusing near-end pre-decoded results and short pop-free transitions to reduce noise, silent gaps and abruptness
- Improved the DSP sample rate and effect switching chain: the internal processing sample rate is decoupled from device output, effect graphs are prebuilt in the background and take over smoothly, and forcing a DSP sample-rate change no longer restarts the output device or decoding session
- Improved the gain semantics of built-in convolution effects: full convolution output with the IR's original gain by default, with safety limiting only when peaks exceed bounds, consistent with third-party effect engines
- Improved shortcut registration failure messages, clearly distinguishing global shortcuts from in-app shortcuts
- Pressing Esc while configuring a shortcut now clears the shortcut instead of being recorded
- Improved the GitHub Release publishing flow, keeping releases in draft until artifacts finish uploading, so in-progress builds are not picked up by update checks
- Improved global toast styling and placement
- Improved the global network proxy to uniformly cover the Kugou API, covers, audio direct links, updates, plugins and other app network requests
- Improved GitHub acceleration fallback: when the accelerator site is unavailable it automatically switches to the original GitHub, and both requests follow the global proxy rules
- Improved network settings submission: proxy, credentials and network timeouts are applied explicitly and persisted synchronously by the main process
- Improved the first-login hint, clarifying that a Kugou Concept Edition account must be registered and logged in on mobile first
- Refactored the Task Center lifecycle: playlist import and cloud drive uploads use task sessions directly, and update downloads connect to the unified state adapter
- Unified volume values to a `0-100` percentage; you may need to re-adjust your volume once
- Extended the loudness normalization range, allowing attenuation down to `-40 dB` for high-loudness sources
- Improved artist/album click interactions in song lists on detail pages, removing the same-route click restriction
- The Kugou verification dialog now shows a clear notice for accounts that need to bind a phone number
- Improved external playlist import efficiency and accuracy
- Improved native engine speed switching with crossfading and prebuilt backup engines, reducing switching pops and latency
- Improved desktop lyric scaling and lock interaction on macOS/Linux, as well as playback and lyric data sync performance
- Improved Personal FM, persisting recommendation mode and recommendation pool options
- Improved dialog interaction and styling with unified layer management, popup animations, and adjusted intro dialog width
- Improved login method switching and Kugou API network request stability
- Improved app state persistence encapsulation with unified storage key management and cleanup
- Improved audio output device switching and exception recovery logic
- Improved delayed release of audio devices when not playing, accommodating Bluetooth multipoint switching
- Improved native audio playback network stream cache seeks, weak-network reconnection and decoder recycling, reducing waits when seeking, switching tracks and under network fluctuation
- Improved Mini mode initialization to avoid re-entering the main player init flow when switching windows
- Improved desktop lyric second-line display logic: translation/transliteration shown first, next-line preview only when neither is shown
- Improved the boundary between login state and device identity; logout and session expiry no longer clear the local device identity
- Improved the music-age calculation in the profile
- Improved avatar upload validation: the main process restricts image format and size and generates safe file names
- Improved native audio playback network stream recovery and seek stability
- Spatial audio now uses unified full-convolution output, and EQ was adjusted to standard 10-band center frequencies with re-tuned built-in curves
- Improved Personal FM, persisting recommendation mode and recommendation pool options
- Improved VPF parameter effect processing, calibrating the full-chain output of EQ, VHE, soundstage, dynamics, bass, clarity, reverb and limiting
- Extended VHE sample-rate support so non-44.1/48 kHz audio also applies headphone spatial processing
- Improved desktop lyric scaling and lock interaction on macOS/Linux, as well as playback and lyric data sync performance
- Extended VHE sample-rate support so non-44.1/48 kHz audio also applies headphone spatial processing, with tiered partitioned convolution to reduce high-sample-rate overhead
- Improved VHE performance by reducing high-sample-rate overhead through tiered partitioned convolution

### Fixed

- Fixed the macOS update package signature verification failure showing only a generic error and leading users to retry endlessly; it now clearly prompts manual download and installation
- Fixed some indirect runtime dependencies not being packaged, ensuring dependencies needed for audio metadata parsing and similar features are complete
- Fixed playback history batch operations being unable to fully select all when song IDs were duplicated or missing, breaking select-all state
- Fixed dialog content possibly appearing blurry on Windows high-DPI scaling due to scale animations and composited-layer resampling
- Fixed Music Recognition on macOS failing to show the microphone authorization dialog, adding media permission declarations and actively requesting authorization from the main process
- Fixed the main window minimum height being too large on Linux Wayland at 150% fractional scaling in quarter-screen tiling, clipping the bottom player bar
- Fixed the volume being wrongly limited to `1%` when dragging or scrolling the volume bar in Mini mode on Windows
- Fixed some downloaded convolution effects with unusually long leading silence causing repeated echo throughout playback in the built-in effect engine
- Fixed playing VIP songs while logged out wrongly reporting "no audio source available", and improved the generic message when a song cannot play for unknown reasons
- Fixed abnormal playback progress when the DSP used an independent sample rate, stale effects remaining after clearing effect presets, and asynchronous effect switching possibly overwriting the latest playback speed
- Fixed playback not resuming after manually switching to a preloaded song while paused, and false decoding timestamp jump reports during gapless track switching
- Fixed Canvas, spectrum subscriptions and DOM listeners not being released in time when closing the lyrics page with a spectrum plugin enabled, causing persistent renderer memory usage
- Fixed the plugin audio spectrum API not returning real waveform data as requested, leaving spectrum plugins' waveform mode blank
- Fixed desktop lyrics and plugin floating windows possibly growing larger after being opened repeatedly on Windows
- Fixed checking for updates showing a raw 404 error while update metadata was not yet ready during a release
- Fixed birthdays possibly displaying one day off in some time zones
- Fixed the profile date picker popup being covered by the profile editing dialog
- Fixed avatar uploads losing the multipart form, and the "under review" state being misreported as an upload failure
- Fixed some Windows audio drivers rejecting WASAPI exclusive initialization because the exclusive output period was forcibly enlarged
- Fixed intentional interruption during network stream seeks being misjudged as a fatal error, breaking cache seeks or corrupting playback state
- Fixed underlying reads possibly blocking after a network redirect timeout, leaving the buffering state unable to end in time
- Fixed unknown-length sequential streams such as network radios terminating playback outright after transient connection jitter
- Fixed audio failing to open when some servers returned HTTP 206 responses of unknown total length
- Fixed clearing preloaded audio sources possibly briefly blocking track switching and other player controls
- Fixed the app possibly exiting directly when macOS audio rendering or device monitoring callbacks hit exceptions
- Fixed prolonged playback possibly causing delayed track switching
- Fixed possible stuttering during playback
- Fixed completed or aborted background tasks not being cleaned up per policy, and stale async callbacks possibly affecting a new round of tasks
- Fixed volume possibly jumping when the same song repeats through gapless playback
- Fixed the UI showing sound after quickly unmuting during a track switch while the audio was still silent
- Fixed the player staying bound to the old output endpoint after Bluetooth headphones disconnect and reconnect on Windows, causing silence
- Fixed the user avatar and nickname not updating automatically after launching the app, requiring a visit to the profile center to refresh
- Fixed an issue where setting the pause shortcut to Space prevented typing a space in input fields
- Fixed an issue where arrow-key switching failed when the playback queue drawer reached the leftmost or rightmost queue
- Fixed desktop lyrics on Windows slowly enlarging while dragging, being unable to drag across multi-monitor displays with different DPI, the scaling hotzone sitting outside the window, and the background disappearing during scaling
- Fixed desktop lyric lock state desync, single-character word-level lyrics failing to highlight, and failed enable-state rollback
- Corrected song quality level mapping, removed the erroneous DSD tier, and moved Viper Mastering into the quality selector
- Fixed the recently-played statistics page not filling the available width on large screens
- Fixed an issue where music kept playing without sound after Windows sleep/hibernation wake
- Fixed an issue where overlapping dialogs became unresponsive
- Fixed an issue where the old output thread did not fully exit when switching devices, potentially causing dual-device output, speed-ups or stuttering
- Fixed an issue where playback progress stopped updating after track switch or source reload
- Fixed sound stuttering when playing music on some devices
- Fixed an issue where paged lists like "My Favorites" could be cleared after repeated refresh or API failure
- Fixed an issue where switching to Mini mode during Personal FM playback could stop desktop lyric progress
- Fixed an issue where the login device list could not mark "this device" when the local `mid` was not yet synced
- Fixed an issue where the native engine's volume equalization could cause sudden volume fluctuations
- Fixed an issue where audio device monitoring on Linux could exhaust PulseAudio/PipeWire connections
- Fixed an issue where "My Favorites" could retain stale favorites/follows/videos after login state change or account switch
- Fixed proxy settings and the proxy password possibly persisting inconsistently due to renderer process exceptions
- Fixed the native player unable to use authenticated SOCKS5 proxies
- Fixed Linux system media controls possibly bypassing the global proxy to fetch remote covers when cover download failed
- Fixed local PAC file paths possibly being exported into settings backups
- Fixed an issue where audio device monitoring on Linux could continuously create PulseAudio client connections, exhausting pipewire-pulse connections and affecting other apps
- Fixed an issue where "My Favorites" could retain stale favorites/follows/videos after login state change or account switch
- Fixed an issue where enabling desktop lyrics and then switching to Mini mode could stop lyric progress
- Fixed an issue where the login device list could not mark "this device" when the local `mid` was not yet synced
- Fixed an issue where some audio backends could repeatedly buffer-recover after underrun, causing sound stuttering
- Fixed an issue where paged lists like "My Favorites" could repeatedly reload and briefly show empty data during rapid refresh
- Fixed an issue where paged lists like "My Favorites" could be cleared after repeated refresh or API failure
- Fixed an issue where dragging the desktop lyric window on Windows slowly enlarged it, the scaling hotzone sat outside the window, and the background disappeared during scaling

## [2.3.0] - 2026-08-11

### Fixed

- Fixed an issue where repeatedly clicking "Play All" could trigger duplicate loading and freeze playback

## Earlier Versions

For earlier versions, see the [changelog archive](/en/changelog/archive), or check [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases) for the complete history.
