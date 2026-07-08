---
title: Changelog
---

# Changelog

This page records the major version updates for EchoMusic. For the complete changelog, see [GitHub Releases](https://github.com/hoowhoami/EchoMusic/releases).

> ⚠️ This software is completely free and open-source. Do not obtain it through any paid channels.
>
> 🤡 If you acquired it by paying, you've been scammed.

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
