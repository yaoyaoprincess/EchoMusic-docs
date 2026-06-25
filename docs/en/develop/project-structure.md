---
title: Project Structure
---

# 📁 Project Structure

This document details the EchoMusic project's directory structure and module responsibilities.

## Directory Tree

```
EchoMusic/
├── .claude/                    # Claude Code configuration
│   └── settings.json           # Project-level Claude Code settings
├── .github/                    # GitHub CI/CD & Community config
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md       # Bug report template
│   │   └── feature_request.md  # Feature request template
│   └── workflows/
│       ├── build.yml           # Multi-platform build & release
│       ├── issue-ai-labeler.yml # AI-powered issue labeling
│       └── issue-closer.yml    # Auto-close stale issues
├── .vscode/
│   └── extensions.json         # Recommended VS Code extensions
├── build/                      # Build configuration and resources
│   ├── icons/                  # Application icons
│   └── afterPack.js            # Electron Builder post-packaging hook
├── electron/                   # Electron main process code
│   ├── main.ts                 # Main process entry point
│   ├── preload.ts              # Preload script
│   └── updater.ts              # Auto-update logic
├── native/                     # Rust native modules (napi-rs)
│   ├── echo-mpv-player/        # libmpv playback engine wrapper
│   │   ├── src/
│   │   │   ├── lib.rs          # Module entry
│   │   │   ├── player.rs       # Player core logic
│   │   │   ├── eq.rs           # EQ equalizer
│   │   │   └── fade.rs         # Crossfade control
│   │   └── Cargo.toml
│   ├── echo-media-controls/    # System media controls
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── macos.rs        # macOS implementation
│   │   │   ├── windows.rs      # Windows implementation
│   │   │   └── linux.rs        # Linux implementation
│   │   └── Cargo.toml
│   └── echo-storage/           # SQLite local storage
│       ├── src/
│       │   ├── lib.rs
│       │   ├── db.rs           # Database operations
│       │   ├── models.rs       # Data models
│       │   └── migrations.rs   # Database migrations
│       └── Cargo.toml
├── server/                     # Node.js backend service
│   ├── index.ts                # Service entry
│   ├── routes/                 # API routes
│   │   ├── song.ts             # Song-related endpoints
│   │   ├── search.ts           # Search endpoints
│   │   ├── playlist.ts         # Playlist endpoints
│   │   ├── artist.ts           # Artist endpoints
│   │   ├── album.ts            # Album endpoints
│   │   ├── lyric.ts            # Lyrics endpoints
│   │   └── user.ts             # User-related endpoints
│   ├── services/               # Business logic layer
│   │   ├── kugou.ts            # Kugou API call wrapper
│   │   └── cache.ts            # Caching logic
│   └── package.json
├── src/                        # Vue 3 frontend code
│   ├── App.vue                 # Root component
│   ├── main.ts                 # Frontend entry
│   ├── router/                 # Router configuration
│   │   └── index.ts
│   ├── stores/                 # Pinia state management
│   │   ├── player.ts           # Player state
│   │   ├── user.ts             # User state
│   │   ├── settings.ts         # Settings state
│   │   └── search.ts           # Search state
│   ├── views/                  # Page components
│   │   ├── HomeView.vue        # Home page
│   │   ├── DiscoverView.vue    # Discover page
│   │   ├── SearchView.vue      # Search page
│   │   ├── FMView.vue          # Personal FM
│   │   ├── RecognizeView.vue   # Music recognition
│   │   ├── SongDetailView.vue  # Song details
│   │   ├── PlaylistView.vue    # Playlist details
│   │   ├── ArtistView.vue      # Artist details
│   │   ├── AlbumView.vue       # Album details
│   │   ├── SettingsView.vue    # Settings page
│   │   └── ProfileView.vue     # User profile
│   ├── components/             # Common components
│   │   ├── PlayerBar.vue       # Bottom player bar
│   │   ├── PlayQueue.vue       # Play queue
│   │   ├── LyricPanel.vue      # Lyrics panel
│   │   ├── LyricDesktop.vue    # Desktop lyrics
│   │   ├── EqPanel.vue         # EQ panel
│   │   ├── SongCard.vue        # Song card
│   │   ├── SearchInput.vue     # Search input
│   │   └── ...
│   ├── composables/            # Composable functions
│   │   ├── usePlayer.ts        # Player logic
│   │   ├── useAudio.ts         # Audio device
│   │   ├── useLyric.ts         # Lyrics processing
│   │   ├── useSearch.ts        # Search logic
│   │   └── useTheme.ts         # Theme switching
│   ├── api/                    # API request wrappers
│   │   ├── index.ts            # Axios instance
│   │   ├── song.ts
│   │   ├── search.ts
│   │   └── ...
│   ├── utils/                  # Utility functions
│   ├── types/                  # TypeScript type definitions
│   └── assets/                 # Static assets
├── resources/                  # Application resource files
├── .eslintrc.json              # ESLint code linting configuration
├── .prettierrc                 # Prettier code formatting configuration
├── .prettierignore             # Prettier ignore rules
├── .npmrc                      # npm/pnpm configuration
├── .gitmodules                 # Git submodules configuration
├── CHANGELOG.md                # Version changelog
├── package.json                # Project configuration
├── pnpm-lock.yaml              # Dependency lock file
├── vite.config.ts              # Vite configuration
├── electron-builder.yml        # Electron Builder configuration
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── LICENSE                     # MIT License
└── README.md                   # Project README
```

## Key File Descriptions

### Entry Files

| File | Description |
|------|------|
| `electron/main.ts` | Electron main process entry — creates windows, initializes services, manages auto-start |
| `src/main.ts` | Vue 3 application entry — mounts root component and plugins |

### Configuration Files

| File | Description |
|------|------|
| `vite.config.ts` | Vite build configuration with Electron plugin |
| `electron-builder.yml` | Multi-platform packaging configuration |
| `tailwind.config.ts` | Tailwind CSS theme customization |
| `tsconfig.json` | TypeScript compilation options |
| `.eslintrc.json` | ESLint code style linting rules |
| `.prettierrc` | Prettier code formatting configuration |
| `.npmrc` | npm/pnpm registry and configuration |

### Developer Tooling

| File/Directory | Description |
|-----------|------|
| `.claude/` | Project-level Claude Code configuration (AI-assisted development) |
| `.vscode/extensions.json` | Recommended VS Code extensions list |

### GitHub Workflows

| File | Description |
|------|------|
| `.github/workflows/build.yml` | Multi-platform automated build & Release publishing (macOS/Windows/Linux) |
| `.github/workflows/issue-ai-labeler.yml` | AI-powered automatic issue labeling |
| `.github/workflows/issue-closer.yml` | Auto-close inactive issues |
| `.github/ISSUE_TEMPLATE/` | Issue templates (Bug Report / Feature Request) |

### Build-Related

| File | Description |
|------|------|
| `build/afterPack.js` | Electron Builder post-packaging hook script |

### Rust Native Modules

Each native module is an independent Rust crate, compiled to a `.node` file via napi-rs, loaded directly in the Electron main process.
