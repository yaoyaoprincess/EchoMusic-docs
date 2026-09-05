---
title: Changelog
sidebar: false
---

# Changelog

This page records the major version updates for EchoMusic. For the complete changelog, see [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases).

> ⚠️ This software is completely free and open-source. Do not obtain it through any paid channels.
>
> 🤡 If you acquired it by paying, you've been scammed.



> **🔔 New versions detected: 2.3.1-beta.24**
> This section is auto-generated from the upstream CHANGELOG (Chinese). Please translate manually or use the Chinese changelog as reference.
>

## [2.3.1-beta.15] - 2026-08-17

### Added

- Added a toggle to disable default browser key behaviors (space, arrow keys, page-up/down scrolling and activation)

### Improved

- Improved VHE performance by reducing high-sample-rate overhead through tiered partitioned convolution

### Fixed

- Fixed an issue where setting the pause shortcut to Space prevented typing a space in input fields
- Fixed an issue where arrow-key switching failed when the playback queue drawer reached the leftmost or rightmost queue

## [2.3.1-beta.14] - 2026-08-16

### Improved

- Improved desktop lyric scaling and lock interaction on macOS/Linux, as well as playback and lyric data sync performance
- Extended VHE sample-rate support so non-44.1/48 kHz audio also applies headphone spatial processing, with tiered partitioned convolution to reduce high-sample-rate overhead

### Fixed

- Fixed an issue where dragging the desktop lyric window on Windows slowly enlarged it, the scaling hotzone sat outside the window, and the background disappeared during scaling
- Fixed desktop lyric lock state desync, single-character word-level lyrics failing to highlight, and failed enable-state rollback

## [2.3.1-beta.13] - 2026-08-16

### Improved

- Extended VHE sample-rate support so non-44.1/48 kHz audio also applies headphone spatial processing

### Fixed

- Corrected song quality level mapping, removed the erroneous DSD tier, and moved Viper Mastering into the quality selector

## [2.3.1-beta.12] - 2026-08-15

### Fixed

- Fixed the recently-played statistics page not filling the available width on large screens

## [2.3.1-beta.11] - 2026-08-15

### Improved

- Improved VPF parameter effect processing, calibrating the full-chain output of EQ, VHE, soundstage, dynamics, bass, clarity, reverb and limiting

### Fixed

- Fixed an issue where music kept playing without sound after Windows sleep/hibernation wake

## [2.3.1-beta.10] - 2026-08-15

### Added

- Added the Effect Community for browsing, downloading and using parameter effects, convolution effects and combo effects online

### Improved

- Spatial audio now uses unified full-convolution output, and EQ was adjusted to standard 10-band center frequencies with re-tuned built-in curves
- Improved Personal FM, persisting recommendation mode and recommendation pool options

## [2.3.1-beta.9] - 2026-08-14

### Added

- Added the Effect Community for browsing, downloading and using community spatial effects online

### Improved

- Improved dialog interaction and styling with unified layer management, popup animations, and adjusted intro dialog width

### Fixed

- Fixed an issue where overlapping dialogs became unresponsive

## [2.3.1-beta.8] - 2026-08-14

### Added

- Added QQ QR-code login

### Improved

- Improved login method switching and Kugou API network request stability
- Improved app state persistence encapsulation with unified storage key management and cleanup

## [2.3.1-beta.7] - 2026-08-13

### Improved

- Improved audio output device switching and exception recovery logic
- Improved delayed release of audio devices when not playing, accommodating Bluetooth multipoint switching

### Fixed

- Fixed an issue where the old output thread did not fully exit when switching devices, potentially causing dual-device output, speed-ups or stuttering
- Fixed an issue where playback progress stopped updating after track switch or source reload

## [2.3.1-beta.6] - 2026-08-13

### Fixed

- Fixed an issue where paged lists like "My Favorites" could be cleared after repeated refresh or API failure

## [2.3.1-beta.5] - 2026-08-13

### Improved

- Improved native audio playback network stream recovery and seek stability

### Fixed

- Fixed sound stuttering when playing music on some devices
- Fixed an issue where paged lists like "My Favorites" could repeatedly reload and briefly show empty data during rapid refresh

## [2.3.1-beta.4] - 2026-08-12

### Fixed

- Fixed an issue where some audio backends could repeatedly buffer-recover after underrun, causing sound stuttering

## [2.3.1-beta.3] - 2026-08-12

### Improved

- Improved Mini mode initialization to avoid re-entering the main player init flow when switching windows
- Improved desktop lyric second-line display logic: translation/transliteration shown first, next-line preview only when neither is shown

### Fixed

- Fixed an issue where switching to Mini mode during Personal FM playback could stop desktop lyric progress

## [2.3.1-beta.2] - 2026-08-12

### Added

- Added Windows taskbar playback progress display
- Added login device management in the profile center to view and remove non-local devices
- Added a device identity reset entry to clear local `guid`, `mid`, `dfid` and regenerate on restart

### Improved

- Improved the boundary between login state and device identity; logout and session expiry no longer clear the local device identity

### Fixed

- Fixed an issue where the login device list could not mark "this device" when the local `mid` was not yet synced
- Fixed an issue where the native engine's volume equalization could cause sudden volume fluctuations
- Fixed an issue where audio device monitoring on Linux could exhaust PulseAudio/PipeWire connections

## [2.3.1-beta.1] - 2026-08-12

### Added

- Added plugin desktop lyric and Mini player snapshot subscription APIs

### Improved

- Improved the music-age calculation in the profile

### Fixed

- Fixed an issue where audio device monitoring on Linux could continuously create PulseAudio client connections, exhausting pipewire-pulse connections and affecting other apps
- Fixed an issue where "My Favorites" could retain stale favorites/follows/videos after login state change or account switch
- Fixed an issue where enabling desktop lyrics and then switching to Mini mode could stop lyric progress

## [2.3.0] - 2026-08-11

### Fixed

- Fixed an issue where repeatedly clicking "Play All" could trigger duplicate loading and freeze playback

## [2.2.9] - 2026-08-11

### Added

- Added a toggle for the unlock button display when desktop lyrics are locked; when disabled, unlock via the tray menu

## [2.2.9-beta.30] - 2026-08-10

### Added

- Added the Tasks module

## [2.2.9-beta.29] - 2026-08-05

### Added

- Added Linux PulseAudio/PipeWire output device support, allowing selection of audio server devices like Bluetooth headphones on Linux

### Improved

- Improved native engine output device hot-switch and disconnect handling, supporting auto-recovery or immediate pause per settings
- Improved native engine playback clock, prioritizing backend live-delay correction of the audible position
- Improved native engine sample rate, channel, output format and device buffer negotiation to reduce output jitter when switching between different sample rates

### Fixed

- Fixed an issue where some devices could exhibit speed-up-like playback, stuttering, or stop streaming after output underrun
- Fixed an issue where Windows WASAPI could not auto-recover after output device failure or audio service restart

## [2.2.9-beta.28] - 2026-08-04

### Fixed

- Fixed an issue where cloud-drive fallback playback and library quality fetch failures lacked clear prompts or left stale prompts

## [2.2.9-beta.27] - 2026-08-03

### Added

- Added automatic cloud-drive file fallback when the library source is unavailable

### Improved

- Improved cloud-source playback strategy: reuse the library playback chain by default, fall back to cloud files only when unavailable
- Improved music cloud drive list default ordering, prioritizing recently added files
- Improved cloud playback quality entry, supporting temporary switching between cloud files and library quality for the current song

### Fixed

- Fixed an issue where the cloud quality list could stay stuck loading during track switches
- Fixed an issue where effect presets could still be toggled but not take effect when actually playing cloud files
- Fixed an issue where missing loudness parameters during cloud file playback could break volume equalization

## [2.2.9-beta.26] - 2026-08-03

### Added

- Added "prefer cloud drive files" setting: when sound effects are disabled and a matched cloud drive file exists, the cloud source is prioritized

### Improved

- Improved player audio source status display: shows `CLD` badge on the quality entry when playing from cloud drive

### Fixed

- Fixed issue where sound effect presets could still be toggled but not applied when playing cloud drive files
- Fixed issue where clicking a track in the playback queue drawer could activate the wrong queue

## [2.2.9-beta.25] - 2026-08-03

### Added

- Added cloud drive file deletion
- Added seek forward / backward application and global shortcut settings
- Added plugin system-level global shortcut registration API, allowing plugins to respond to shortcuts when EchoMusic is in background

### Improved

- Refactored renderer process plugin runtime: split into context, business API, host API, service, UI, shortcuts, theme, and module loader modules

## [2.2.9-beta.24] - 2026-08-03

> Hotfix for issues introduced in beta.23.

### Fixed

- Fixed several stability issues introduced in beta.23

## [2.2.9-beta.23] - 2026-08-02

### Added

- Added plugin local audio metadata reading API, allowing local library plugins to read title, artist, album, and duration
- Added basic local audio file scanning capability for future local music library and plugin local media reuse

### Improved

- Improved cloud drive upload library matching and association logic
- Improved cloud drive upload flow: no longer reads full file content during selection phase; on-demand read with per-window isolated temporary whitelist
- Unified local audio extension list: cloud drive upload and plugin file scanning derive from the same local playback format list
- Optimized plugin file API: file enumeration, read, write, and audio metadata reading now use async IPC

### Fixed

- Fixed issue where some search result track IDs were mapped incorrectly

## [2.2.9-beta.22] - 2026-08-01

### Added

- Added music cloud drive upload

## [2.2.9-beta.21] - 2026-08-01

### Added

- Added top gradient color toggle
- Added option to disable theme color source

## [2.2.9-beta.20] - 2026-08-01

### Improved

- Improved page loading experience with unified skeleton screen component, replacing some full-page loading indicators
- Improved loading placeholder behavior for homepage recommendations, Personal FM, search, details page, plugin marketplace, lyric source selection, and add-to-playlist scenarios

## [2.2.9-beta.19] - 2026-07-31

### Added

- Added plugin theme icon cover API, generating theme-color icon covers consistent with the built-in details page

### Improved

- Improved online update installation flow

### Fixed

- Fixed issue where clicking "Install Now" after Windows online update download could be unresponsive

## [2.2.9-beta.18] - 2026-07-31

### Added

- Added purchased music list with two categories: purchased singles and purchased albums

## [2.2.9-beta.17] - 2026-07-29

### Fixed

- Fixed issue where switching the system default output device on Windows could still output from the old device when "System Default" was selected

## [2.2.9-beta.16] - 2026-07-29

> Hotfix for issues introduced in beta.15.

### Fixed

- Fixed several stability issues introduced in beta.15

## [2.2.9-beta.15] - 2026-07-29

### Fixed

- Fixed issue where users could not select an account during verification code login when multiple Kugou accounts shared the same phone number

## [2.2.9-beta.14] - 2026-07-27

### Improved

- Improved native playback engine buffer recovery strategy, limiting recovery wait threshold to actual cache capacity
- Improved native playback engine parameter updates (speed, EQ, loudness, spatial effects) during playback to reduce unnecessary audio filter rebuilds
- Improved native playback engine exclusive output fallback logic when exclusive audio device fails to start
- Improved native playback engine seek retry logic, reducing probability of decoder restart when rapidly dragging the progress bar

### Fixed

- Fixed issue where buffer recovery threshold could exceed actual cache capacity under weak network or slow source conditions
- Fixed issue where native playback engine could directly interrupt playback when some exclusive audio devices failed to start
- Fixed issue where switching some DSP parameters during playback might not fully sync to running filters

## [2.2.9-beta.13] - 2026-07-26

### Added

- Added text selection and copy capability on comment pages
- Added "Copy Song Info" option in track right-click menu

### Fixed

- Fixed issue where trailing characters of some Japanese word-by-word lyrics could be incorrectly deleted

## [2.2.9-beta.12] - 2026-07-26

### Fixed

- Fixed issue where playback state and track info could become out of sync after a track change failure

## [2.2.9-beta.11] - 2026-07-24

> First official pre-release shipping the `echo-ffmpeg-player` native playback engine. This version includes all changes from beta.10.

### Added

- Added macOS / Windows system media control seek forward/backward semantics; Linux continues using MPRIS relative Seek
- Added 4-channel true-stereo spatial audio IR support
- Added plugin playback display state API
- Added gapless playback
- Added in-engine spectrum analysis
- Added player buffer recovery wait setting
- Added unified playback clock snapshot: plugin `nowPlaying`, lyrics, and desktop lyrics snapshots can now obtain playback clock anchors
- Added `echo-ffmpeg-player` native playback engine using embedded FFmpeg decoding and native audio output to replace the old playback pipeline
- Added third-party dependency and license notice document `THIRD_PARTY_NOTICES.md`

### Improved

- Optimized Electron icon and tray refresh to reduce memory usage
- Optimized image list loading to reduce image decoding and GPU texture usage
- Optimized desktop lyrics filtering logic
- Optimized preferences entry: macOS native menu now includes Preferences item; Windows/Linux support window-level `Ctrl+,` to open settings
- Optimized desktop lyrics transition animation speed
- Optimized timeline synchronization for page lyrics, desktop lyrics, and mini player lyrics, using unified playback clock snapshot for re-anchoring
- Converged output device protection to a native-event-based "Pause on device disconnect" toggle, disabled by default
- Optimized player state machine
- Optimized track change interaction responsiveness
- Removed `echo-spectrum-capture` native audio capture spectrum output module
- Project license changed to GNU GPL v3.0

### Fixed

- Fixed issue where native playback engine buffer recovery and resample output were unstable under network fluctuation
- Fixed issue where dragging the progress bar to the beginning could cause the progress display to freeze
- Fixed issue where desktop lyrics filtering could desync line index and word-by-word progress
- Fixed issue where word-by-word lyric progress could disappear after pausing desktop lyrics
- Fixed issue where desktop lyrics could gradually drift ahead during prolonged playback
- Fixed issue where the previous lyric line could occasionally flicker when page lyrics switched lines
- Fixed issue where the main window size could progressively enlarge on Windows after app updates, shutdown, restart, or logout
- Fixed issue where Windows SMTC did not respond to third-party media panel playback progress adjustment requests
- Fixed issue where spatial audio Dry/Wet mix formula was inaccurate, causing wet signal loudness to be too high after superposition
- Fixed issue where some EQ bands could retain stale values when a short array was passed to EQ settings
- Fixed issue where Electron could crash on startup on Windows 11 due to inability to open the `nul` device
- Fixed CI build pipeline

## [2.2.9-beta.10] - 2026-07-23

### New

- Added macOS / Windows system media control fast-forward and rewind semantics; Linux continues with MPRIS relative seek override
- Added 4-channel true-stereo spatial audio IR support
- Added plugin playback display status API
- Added gapless playback
- Added in-engine spectrum analysis within the playback engine
- Added player buffer recovery wait setting
- Added unified playback clock snapshot; plugin `nowPlaying`, lyrics, and desktop lyrics snapshots can access the playback clock anchor
- Added `echo-ffmpeg-player` native playback engine, using embedded FFmpeg decoding and native audio output to replace the old playback pipeline
- Added third-party dependency and licensing notice file `THIRD_PARTY_NOTICES.md`

### Improvements

- Improved desktop lyrics filtering logic
- Improved preference entry: macOS native menu now includes a Preferences item; Windows / Linux support `Ctrl+,` to open settings at window level
- Improved desktop lyrics transition animation speed
- Improved timeline sync for page lyrics, desktop lyrics, and mini-player lyrics, unified through playback clock snapshot re-anchoring
- Converged output device protection into a native device event-based "Pause on device disconnect" toggle, default off
- Improved player state machine
- Improved track-switch interaction responsiveness
- Removed `echo-spectrum-capture` native audio capture spectrum output module
- Changed project license to GNU GPL v3.0

### Fixes

- Fixed native playback engine buffer recovery and resampling output instability during network fluctuations
- Fixed native playback engine progress display potentially freezing after dragging seek bar to the beginning
- Fixed desktop lyrics filtering potentially causing lyric line index and word-level progress desync
- Fixed desktop lyrics word-level progress potentially disappearing after pausing
- Fixed desktop lyrics potentially drifting ahead of time after extended playback
- Fixed page lyrics previous line flickering/jumping during line transitions
- Fixed main window size potentially growing incrementally after app update, shutdown, restart, or logout on Windows
- Fixed Windows SMTC not responding to third-party media panel playback position adjustment requests
- Fixed spatial audio Dry/Wet mix formula inaccuracy causing wet signal loudness boost after blending
- Fixed EQ settings with short arrays potentially leaving stale values in some bands
- Fixed Electron potentially crashing on startup on Windows 11 due to inability to open `nul` device
- Fixed CI build process

## [2.2.8-beta.11] - 2026-07-08
### New

- Added API proxy and MPV proxy configuration
- Added risk control verification plug-in API
- Added Arch Linux pacman installation package
- Added sqlite plug-in API
- Added desktop lyrics plug-in API
- Added desktop lyrics vertical layout
- Added plug-in related statistical functions

### Optimization

- Optimize audio output device hot-plug processing, and uniformly use libmpv device list events to refresh output devices
- Optimize MPV song address selection logic and correctly try alternative CDN addresses
- Optimize API request logic and correctly apply system proxy configuration
- Optimize software menu
- Optimize song right-click menu grouping

### Fix

- Fixed an issue where the status of the play queue and private FM page was abnormal after adding the next song to play or queuing for playback through the right-click menu during private FM playback.
- Fixed an issue where Windows x64 packaging fails when the latest upstream mpv release contains only arm64 assets
- Fixed the problem of finding livmpv on Linux
- Fixed the issue where "Checking..." is always displayed when detecting updates on Arch Linux
- Fixed the problem of inconsistent thickness of the dividing lines in the right-click menu of songs

## [2.2.8-beta.9] - 2026-07-07
### New

- Added API proxy and MPV proxy configuration
- Added risk control verification plug-in API
- Added Arch Linux pacman installation package
- Added sqlite plug-in API
- Added desktop lyrics plug-in API
- Added desktop lyrics vertical layout
- Added plug-in related statistical functions

### Optimization

- Optimize MPV song address selection logic and correctly try alternative CDN addresses
- Optimize API request logic and correctly apply system proxy configuration
- Optimize software menu
- Optimize song right-click menu grouping

### Fix

- Fixed the issue of occasional CoreAudio/HAL crash during playback under macOS
- Fixed an issue where Windows x64 packaging fails when the latest upstream mpv release contains only arm64 assets
- Fixed the problem of finding livmpv on Linux
- Fixed the issue where "Checking..." is always displayed when detecting updates on Arch Linux
- Fixed the problem of inconsistent thickness of the dividing lines in the right-click menu of songs

## [2.2.8-beta.5] - 2026-07-02

### Added

- Arch Linux pacman installation package
- SQLite plugin API (`ctx.sqlite`)
- Desktop lyrics plugin API (`ctx.desktopLyric` + `ctx.lyricEffects` desktop scope)
- Vertical layout for desktop lyrics
- Plugin statistics functionality

### Improved

- Optimized app menus
- Optimized song right-click menu grouping

### Fixed

- Fixed update detection stuck on "Checking..." on Arch Linux
- Fixed inconsistent divider line thickness in song right-click menu

## [2.2.8] - 2026-07-17

### New

- Added sidebar VIP status display
- Added API proxy and MPV proxy configuration
- Added risk control verification plugin API
- Added Arch Linux pacman package
- Added SQLite plugin API
- Added desktop lyrics plugin API
- Added desktop lyrics vertical layout
- Added plugin statistics

### Improvements

- Improved Tooltip component z-index layering
- Improved Linux media control compatibility
- Improved song play button: enters source queue when context is available, adds to "My Queue" for sourceless tracks
- Improved VIP song playback failure notification
- Improved Switch component appearance in unchecked state
- Improved audio output device hot-plug handling, unified through libmpv device list events to refresh output devices
- Improved MPV song URL selection logic, correctly attempting fallback CDN addresses
- Improved API request logic, correctly applying system proxy settings
- Improved app menu
- Improved song right-click menu grouping

### Fixes

- Fixed sidebar playlist action button Tooltip missing when sidebar is collapsed
- Fixed spectrum capture failing to find monitor source on PipeWire-only Linux causing plugin spectrum with no output
- Fixed dragging or cancel-dragging the playback progress bar potentially causing duplicate seek jumps
- Fixed private FM playback queue and page state becoming corrupted after adding tracks via right-click "Play Next" or "Queue"
- Fixed Windows x64 build failure when upstream latest mpv release only contains arm64 assets
- Fixed Linux libmpv detection issue
- Fixed update detection stuck on "Checking..." on Arch Linux
- Fixed inconsistent divider line thickness in song right-click menu

## [2.2.7] - 2026-07-01

### Added

- Risk control verification
- Style recommendation
- High DPI support
- Share functionality
- Windows taskbar thumbnail toolbar
- "Queue on Next" in song right-click menu
- "Auto-play on startup" setting, disabled by default
- One-click plugin update
- Account verification flow
- Account password login
- New batch of plugin API capabilities
- Experimental feature: DevTools toggle

### Improved

- Homepage recommended playlists now include Hi-Res category filter
- Clicking song name in player bar now prioritizes album detail page
- App startup flow with "Continue Anyway" option
- Unified Linux startup wrapper, preloading system libav to prevent libmpv / libffmpeg symbol conflicts
- Song detail now includes chart performance data
- Playback engine async refactored, blocking operations moved to worker threads
- Optimized page lyrics loading and matching logic
- Optimized audio filter application on track switch
- API modules now loaded on demand instead of all at startup
- Playback history migrated to SQLite for persistence, reducing renderer state overhead
- Reduced high-frequency desktop lyrics IPC sync overhead
- Reduced high-frequency writes for window move, resize, and local state persistence
- Optimized playback history cleanup, auto-removing unreferenced song data
- Split plugin main process base modules to lower plugin system maintenance cost
- Optimized multiple internal pages
- Optimized online plugin loading logic
- Music recognition rewritten using official API
- Optimized MediaSession initialization timing, registering event handlers early
- Optimized song list right-click menu interaction, preventing scroll when menu is open
- Dynamically calculated minimum window height for high DPI compatibility
- Optimized echo-storage module bundling
- Optimized first screen loading
- Optimized gradient layer implementation

### Fixed

- Fixed shortcut mute/unmute potentially triggering volume reset
- Fixed Windows libmpv download failure during packaging
- Fixed Linux shortcut unable to pause playback
- Fixed page animation causing blur
- Fixed profile page data display errors
- Fixed Private FM "dislike" not correctly reporting and song info mapping incomplete
- Fixed Windows desktop lyrics mouse stutter when switching tracks while locked
- Fixed desktop lyrics unlock button occasionally persisting
- Fixed plugin system operations causing lyrics page track/lyrics/cover desync
- Fixed progress bar jumping when switching tracks
- Fixed page lyrics memory leak
- Fixed Windows ARM64 build issues
- Fixed playback freezing with stuck progress bar and no sound on network interruption or invalid URL
- Fixed MPRIS cover display and not refreshing after track change
- Fixed Linux packaging libav version regex causing HTTP audio stream playback failure
- Fixed page lyrics per-character highlight intermittently disappearing
- Fixed plugin update or uninstall failing due to file in use after plugin launches an executable
- Fixed VIP expiration causing playback failure even after claiming membership, requiring app restart
- Fixed Windows desktop lyrics width slowly increasing on click

## [2.2.6] - 2026-06-14

### Added

- Experimental captcha verification dialog
- Global page animations
- Settings search
- Audio buffer configuration for network-limited scenarios
- Spectrum capture
- Plugin system
- External playlist import now supports more platforms
- Auto-start on boot and start minimized to tray
- **Mini Mode**: compact mini window player
- Sort functionality for songs and albums on artist detail page
- Lyrics selection
- **Spatial Audio**: import, rename, and remove IR files in settings with quick switching

### Improved

- Optimized play queue logic
- Optimized EQ equalizer
- Improved add-to-playlist experience with duplicate detection and synced detail updates
- Improved favorite/unfavorite flow with real-time "Liked Songs" playlist updates
- Optimized various settings items
- Playlist UI with playlist indicator bar
- Improved sidebar collapse behavior
- Improved lyrics selection
- Improved log output

### Fixed

- Fixed desktop lyrics occasionally displaying incorrectly after track switch
- Fixed UI thread blocking and lag when play queue has too many songs
- Fixed Windows fullscreen mode with scaling causing window control button display issues
- Fixed page lyrics progress bar tooltip clipping at start and end on hover
- Fixed app freezing after waking from extended sleep

## [2.2.7-beta.22] - 2026-06-24

### Added

- Share functionality
- Windows taskbar thumbnail toolbar
- "Queue on Next" in song right-click menu
- "Auto-play on startup" setting, disabled by default
- One-click update all plugins
- Account verification flow
- Account password login
- New batch of plugin API capabilities
- Experimental feature: DevTools toggle

### Improved

- Optimized lyrics page loading and matching logic
- Optimized audio filter application logic when switching songs
- API modules now load on demand instead of preloading all at startup
- Playback history migrated to SQLite for persistence, reducing renderer state size
- Reduced high-frequency desktop lyrics IPC sync overhead
- Reduced high-frequency writes for window move, resize, and local state persistence
- Optimized playback history cleanup logic, auto-cleaning unreferenced song data
- Split plugin main process base modules to reduce plugin system maintenance cost
- Optimized multiple internal pages
- Optimized online plugin loading logic
- Music recognition rewritten using official API
- Optimized MediaSession initialization timing, registering event handlers early
- Optimized song list right-click menu interaction, preventing list scrolling when menu is open
- Optimized window code logic to prevent accidental window resizing
- Dynamically calculated minimum window height to adapt to high DPI environments
- Optimized echo-storage module bundling
- Optimized first screen loading
- Optimized gradient layer implementation

### Fixed

- Fixed desktop lyrics unlock button occasionally persisting
- Fixed plugin system operations causing song, lyrics, and cover desync on the lyrics page
- Fixed progress bar jumping when switching songs
- Fixed lyrics page memory leak
- Fixed Windows ARM64 build issues
- Fixed playback freezing, progress bar stuck, and no sound when network disconnects or URL becomes invalid during playback
- Fixed MPRIS cover display and cover not refreshing after track change
- Fixed Linux packaging libav library version regex causing HTTP audio stream playback failure
- Fixed page lyrics per-character highlight intermittently disappearing
- Fixed plugin update or uninstall failing due to file being in use after plugin launches an executable
- Fixed VIP membership expiration causing playback failure even after claiming membership in Profile, requiring app restart
- Fixed desktop lyrics width slowly increasing when clicked on Windows

## [2.2.6-beta.8] - 2026-06-04

### Added

- External playlist import now supports more platforms
- Auto-start on boot and start minimized to tray
- **Mini Mode**: shrink the player to a compact mini window
- Sort functionality for songs and albums on the artist detail page
- Lyrics selection feature
- **Spatial Audio** support: import, rename, and remove IR audio files in settings, with quick switching in the effects popup

### Improved

- Optimized certain settings items
- Optimized playlist UI with playlist indicator bar
- Improved sidebar collapse behavior
- Improved lyrics selection
- Improved log output

### Fixed

- Fixed UI thread blocking and lag when the play queue has too many songs
- Fixed fullscreen mode on Windows where scaling adjustments could cause window control buttons to display incorrectly
- Fixed page lyrics progress bar tooltip clipping at start and end when hovering
- Fixed app freezing after waking from extended sleep

## [2.2.5] - 2026-05-31

### Added

- Add-to-playlist feature in play queue
- Collapsible "Discover Music" and "My Library" sidebar sections
- Custom sorting for sidebar playlists
- Regex-based lyrics content filtering
- Custom GitHub acceleration site configuration for the update module
- Toggle for title bar search box recommendation terms, disabled by default
- Keep bottom action bar visible when lyrics photo mode is collapsed
- Sidebar collapse/expand with title bar button and shortcut switching, configurable toggle, disabled by default
- Input device selection for Music Recognition

### Improved

- Optimized play queue enqueue and removal logic
- Play queue respects sorted order when enqueuing
- Improved error page display, ignoring common non-functional browser errors
- Improved lyrics fetching to prioritize translations and transliterations
- Refactored page lyrics
- Refactored settings page
- Optimized list scrolling performance

### Fixed

- Fixed title bar search box close animation executing unexpectedly multiple times
- Fixed playlist and other reusable routes not switching correctly when page cache is disabled
- Fixed playback engine failing to start on Windows ARM
- Fixed media session cover not displaying for some songs on Windows
- Fixed file lock issues when Windows users reinstall after uninstalling
- Fixed desktop lyrics dragging issues in Windows touchscreen environments
- Fixed music playback issues on some Linux distributions
- Fixed desktop lyrics not staying on top and mouse passthrough not working on Linux
- Fixed media session not working properly on Linux
- Fixed search page infinite scroll not loading more results
- Fixed artist detail page not loading more albums and MVs on scroll

## [2.2.4] - 2026-05-21

### Added

- **Global theme color system**: auto-extract from cover art, preset themes, and custom color modes
- First-time use tip banner on the login page

### Improved

- Page cache architecture refactored: each page has its own scroll container
- Simplified page cache settings: removed page selector, now global toggle + max cache count, all cacheable pages cached by default
- macOS builds now include zip format with in-app auto-update support
- Update dialog now shows "Go to Download" button on failure, guiding manual download
- Color picker layout optimized
- VIP expiration text in profile now shows hours/minutes precision with hover tooltip for start and full expiration time
- Dark mode overall brightness increased by one level
- Batch operations: confirmation dialog before deletion; add-to-playlist and delete now use server-side batch APIs for major speed boost
- Batch action buttons now show real-time progress and loading state
- Batched add-to-playlist order reversed to match playlist default reverse display

### Fixed

- Fixed title bar right-click crash
- Fixed some songs not scrolling or highlighting on the lyrics page
- Fixed window not restoring to previous size after closing/restarting while maximized

### Refactored

- Search box now shows trending recommendation terms when expanded, click to quick search
- Fixed scroll position not resetting on route change

## [2.2.3] - 2026-05-08

### Added

- Click cover on lyrics page to copy song info
- Personal FM: added "Peak" mode and "Gamma" recommendation pool for more diverse recommendations
- External playlist import functionality
- **Music Recognition**: supports microphone recording and system audio capture
- Fullscreen button on Windows/Linux title bar
- Experimental DSD premium quality option (limited song availability)
- Experimental equalizer

### Fixed

- Fixed native addon loading failure on Windows without Visual C++ Redistributable (statically linked MSVC C Runtime)
- Fixed first song always being the first in the playlist when shuffle is on
- Fixed QR code refresh button overlapping with scan prompt text on login page
- Fixed libmpv dependency issues on Linux

### Refactored

- **Playback engine migrated from mpv subprocess to libmpv embedded** via Rust NAPI addon directly calling libmpv C API
- Separated audio quality and audio effects logic and trigger buttons; merged effects and equalizer

### Improved

- Tray icon redesigned with brand blue + white glyph, clearly visible on both light and dark taskbars, unified across Windows and Linux
- Personal FM: improved playback logic, correctly sending `is_overplay: true` on natural song end to reduce recommendation repeats
- Personal FM: added `/personal/fm` and `/ai/recommend` to non-cached route list for real-time recommendations
- My Favorites: split followed users and artists into separate tabs
- Optimized playback logic and UI blocking/race condition issues
- Adjusted page lyrics translation/transliteration font sizes
- Lyrics out-of-sync warning when playback duration differs significantly from original track length

## [2.2.2] - 2026-04-27

### Refactored

- Playback engine upgraded to mpv with independent process playback, supporting more audio formats with higher decoding quality
- Vocal/instrumental track switching faster and more stable
- Volume normalization and crossfade adapted for new engine
- Audio output device list more accurate, switching more reliable
- Comment replies changed to inline expand/collapse for unified interaction

### Added

- **Exclusive Audio Device** toggle: bypass system mixer for direct output and higher audio quality
- **Auto Check for Updates** toggle in settings
- Logout confirmation dialog to prevent accidental clicks
- Comment button on lyrics page to view current song comments
- Long comments auto-truncated with expand/collapse support

### Improved

- Lyrics page light theme background readability improved
- Lyrics page play button and cover card visual consistency
- Audio device status hints layout more compact
- Play queue, batch operations, and comment drawer unified at bottom

### Fixed

- Modals blocked by player bar
- Lyrics translation and transliteration line colors following custom colors
- Progress bar drag handle lagging behind mouse

### Known Changes

- Slight increase in app package size

## [2.2.1] - 2026-04-24

### Added

- **Vocal** and **Instrumental** audio effect options with separated playback
- Extracted track data cached for instant vocal/instrumental switching on the same song
- Photo mode lyrics auto-collapse: auto-collapse to bottom two lines after inactivity, with configurable toggle and delay
- Photo mode button adaptive color: auto-switches light/dark based on background brightness, with toggle
- Lyrics page changed to overlay mode, fixing page cache invalidation on open/close
- Lyrics page open/close transition animation
- Font settings

### Improved

- Unified dark/light theme behavior in photo mode
- Photo mode cover card and controller layout optimized
- Lyrics page popup hierarchy adapted for overlay mode
- Play queue now supports direct drag-to-reorder
- Desktop lyrics lock/unlock interaction improved: can interact after locking without moving out of window
- Desktop lyrics text shadow changed to soft projection style
- Desktop lyrics multi-monitor support, remembers monitor position
- **Disable GPU Acceleration** toggle for troubleshooting rendering issues

### Fixed

- Lyrics stuck on "Loading" during rapid track switching
- Profile still showing previous account info after logout and login with different account
- Lyrics page shortcut key not opening
- Page cache invalidation on lyrics page open/close
- "My Favorites" page current song position offset
- Desktop lyrics position shifting on each open in Windows
- Progress bar flickering when switching audio quality or effects
- Volume normalization incorrectly applying default attenuation without valid loudness data
- Desktop lyrics line switching delay
- Scroll position not preserved when returning to page
- Lyrics played/unplayed color defaults inconsistency
- Artist detail info completed (followers, birthday, MV count)
- Album detail page showing album type and language, sticky header with favorite button
- Playlist detail page sticky header with favorite button
- Sidebar layout spacing adjusted

## [2.2.0] - 2026-04-21

### Added

- **Lyrics** and **MV** search tabs on the search page
- MV search results in card grid layout, reusing existing MV card component
- "Search Page" quick entry button on right side when title bar search box is expanded and empty
- **Volume Normalization**: automatically adjusts gain based on track LUFS loudness data for consistent volume across songs

### Improved

- Playback engine refactored from Howler.js to native HTML5 Audio, eliminating middleware event loss and state sync issues
- Volume normalization via Web Audio API (GainNode), reusing the same audio element without rebuilding the processing chain on track change
- Crossfade refactored to dual GainNode architecture (fadeGainNode + normGainNode), using Web Audio API native linearRampToValueAtTime scheduling, independent of JS timers, works even when window is minimized
- Lyrics page word-level animation upgraded to gradient fill effect matching desktop lyrics, using rAF real-time interpolation for smooth transitions
- Directly listen to native audio durationchange event, fixing inaccurate duration for streaming audio

### Fixed

- Fixed playback suddenly freezing with progress bar stuck and unresponsive to drag
- Fixed song progress reaching end but ended event not triggering, delaying next track switch
- Fixed auto track switch causing no sound due to crossfade
- Fixed HTML entities in English lyrics not being decoded (e.g., `&apos;` shown as raw text)

## [2.1.9] - 2026-04-20

### Added

- **My Favorites** page with Songs, Artists, Albums, and Videos tabs
- Auto-rotating lyrics photo backgrounds
- API cache layer (LRU, 200 entries max, 30-minute TTL), write operations auto-clear related caches
- Page cache (KeepAlive) settings with customizable cached pages and max count
- MultiSelect dropdown component

### Improved

- Removed global request timestamps; cache strategy managed by main process cache layer
- Title bar refresh button clears API cache on click for latest data
- "Liked Songs" playlist restored to custom playlist list in sidebar
- Favorited albums moved to "My Favorites" page
- Lyrics page translation/transliteration refactored as independent toggles
- Lyrics photo background mask and toolbar visual improvements
- Non-current and unplayed lyrics line color readability improved

### Fixed

- Lyrics color picker incorrect defaults
- Audio quality/effects badge and playlist song count badge settings not applying on lyrics page

## [2.1.8] - 2026-04-19

### Added

- MV tab on artist detail page with category filtering and scroll loading
- Audio quality and effects badge display toggle in settings
- Silent installation toggle: auto-complete updates in background without setup wizard
- Linux arm64 build

### Improved

- Native CSS dragging solution, completely fixing Windows high-DPI window drag flickering
- Removed ineffective PlayerBar frosted glass effect, reducing GPU overhead
- Artist detail page albums and MVs changed to lazy loading, request data only on tab switch
- Artist detail page albums support scroll pagination
- Modal and drawer components compatible with native drag layer, no interaction interference when open

### Fixed

- Lyrics page photo images failing to load
- Login expiration check falsely triggering on network disconnect, incorrectly clearing login state
- Login expired dialog clearing login state before user confirmation
- Manual track switch in single loop mode now follows list order, no longer repeating current song
- Page scroll position not resetting after route change
- macOS update dialog missing online update button

## [2.1.7] - 2026-04-19

### Added

- Changelog entry in settings page

### Fixed

- Window slowly enlarging when dragging on Windows high-DPI
- Version update content styles not displaying correctly

## [2.1.6] - 2026-04-18

### Added

- Artist list page under Discover
- Version update log viewable when checking for updates
- In-app online update for Windows and Linux

### Improved

- Refactored internal communication architecture for improved API stability and response speed
- Further reduced installer size
- Startup speed optimization
- Request log format optimization

### Fixed

- Lyrics page play queue overlapping with window control buttons
- API service becoming unresponsive after extended use, requiring app restart
- API service port conflicts
- Network proxy causing app to malfunction
- Title bar not draggable on certain pages

## Earlier Versions

For earlier test versions (2.1.5 and below), please see [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases).
