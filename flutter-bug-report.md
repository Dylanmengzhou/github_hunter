# 🐛 Flutter Android 工具类 App — 点击无响应 Bug 报告

**生成时间：** 2026-03-08 01:32　|　**平台：** Android　|　**仓库数：** 7　|　**Bug 总计：** 23 条

> 仅收录「点击 / 点按 没有反应」类交互 bug，且 issue 中必须明确提及 **Android** 平台。

---

## 📊 总览

| 排名 | 仓库 | ⭐ Stars | 🐛 点击Bug | 📦 近期版本 | 综合得分 |
|:---:|:---|---:|:---:|:---:|:---:|
| 1 | [media-kit/media-kit](https://github.com/media-kit/media-kit) | 1,694 | 12 | 0 | 0.630 |
| 2 | [florent37/Flutter-AssetsAudioPlayer](https://github.com/florent37/Flutter-AssetsAudioPlayer) | 773 | 5 | 0 | 0.615 |
| 3 | [simonoppowa/OpenNutriTracker](https://github.com/simonoppowa/OpenNutriTracker) | 1,611 | 1 | 3 | 0.578 |
| 4 | [ubuntu-flutter-community/musicpod](https://github.com/ubuntu-flutter-community/musicpod) | 623 | 1 | 11 | 0.577 |
| 5 | [namidaco/namida](https://github.com/namidaco/namida) | 5,062 | 1 | 3 | 0.569 |
| 6 | [nt4f04uNd/sweyer](https://github.com/nt4f04uNd/sweyer) | 216 | 2 | 1 | 0.467 |
| 7 | [moritz-weber/mucke](https://github.com/moritz-weber/mucke) | 251 | 1 | 0 | 0.452 |

---

## 📋 详细报告

### #1 [media-kit/media-kit](https://github.com/media-kit/media-kit)

> A cross-platform video player & audio player for Flutter & Dart.

| 项目 | 数值 |
|------|------|
| ⭐ Stars | 1,694 |
| 📋 Open Issues | 289 条 |
| 🐛 点击无响应 Bug | **12 条** |
| 📦 近期版本（1 年内）| 0 个 |
| 🏆 综合得分 | `0.630` |

#### 🖱 点击 / 点按无响应 Bug（12 条）

| Issue 标题 | 时间 | 链接 |
|:----------|:----:|:----:|
| iOS-only Issue: Video Playback Interruption During PageView Transition Due to Player Lifecycle Order | 2026-02-10 | [查看](https://github.com/media-kit/media-kit/issues/1382) |
| RTSP streams (H.264/H.265) stop after first frame on Android - MediaCodec format change issue | 2025-12-29 | [查看](https://github.com/media-kit/media-kit/issues/1357) |
| [Android Emulator] Video not visible — only black screen displayed | 2025-12-10 | [查看](https://github.com/media-kit/media-kit/issues/1343) |
| Crash on Hot Restart in Flutter 3.38.x on Android and iOS | 2025-12-04 | [查看](https://github.com/media-kit/media-kit/issues/1340) |
| Network video not playing on macOS (local file works fine) | 2025-10-06 | [查看](https://github.com/media-kit/media-kit/issues/1284) |
| RTMP Playback Failure on Home Page Initial Load(info cplayer VO: [null]) | 2025-09-01 | [查看](https://github.com/media-kit/media-kit/issues/1258) |
| Shortcuts break due fullscreen. | 2025-08-28 | [查看](https://github.com/media-kit/media-kit/issues/1253) |
| Non-clickable and hided part of MaterialSeekBar | 2025-07-15 | [查看](https://github.com/media-kit/media-kit/issues/1221) |
| Player Freeze on Android | 2025-03-18 | [查看](https://github.com/media-kit/media-kit/issues/1141) |
| Stream authentication does not allow video playback (Android) | 2024-11-19 | [查看](https://github.com/media-kit/media-kit/issues/1038) |
| HLS m3u8 - audio but no video on Android | 2024-02-07 | [查看](https://github.com/media-kit/media-kit/issues/701) |
| dispose() blocks the main thread. | 2024-02-07 | [查看](https://github.com/media-kit/media-kit/issues/700) |

#### 📦 版本记录（共 60 个，展示最近 6 个）

| 版本 | 发布时间 | 状态 | 更新摘要 |
|:-----|:--------:|:----:|:--------|
| [media_kit_video-v1.2.3](https://github.com/media-kit/media-kit/releases/tag/media_kit_video-v1.2.3) | 2023-10-19 | ⬜ 旧版 | - feat: `VideoState.update` & `VideoViewParameters` |
| [media_kit-v1.1.10](https://github.com/media-kit/media-kit/releases/tag/media_kit-v1.1.10) | 2023-10-19 | ⬜ 旧版 | - feat: prevent multiple calls to `MediaKit.ensureInitialized` |
| [media_kit_video-v1.2.2](https://github.com/media-kit/media-kit/releases/tag/media_kit_video-v1.2.2) | 2023-10-16 | ⬜ 旧版 | - fix: override `setState` & check `mounted` in `MaterialVideoControls` & `MaterialDesktopVideoContr |
| [media_kit_libs_android_video-v1.3.6](https://github.com/media-kit/media-kit/releases/tag/media_kit_libs_android_video-v1.3.6) | 2023-10-16 | ⬜ 旧版 | - build: bump dependencies |
| [media_kit_libs_android_audio-v1.3.6](https://github.com/media-kit/media-kit/releases/tag/media_kit_libs_android_audio-v1.3.6) | 2023-10-16 | ⬜ 旧版 | - build: bump dependencies |
| [media_kit-v1.1.9](https://github.com/media-kit/media-kit/releases/tag/media_kit-v1.1.9) | 2023-10-16 | ⬜ 旧版 | - fix: `NativePlayer._command` - fix: `NativePlayer` play after completed - fix(web): `AssetLoader |

---

### #2 [florent37/Flutter-AssetsAudioPlayer](https://github.com/florent37/Flutter-AssetsAudioPlayer)

> Play simultaneously music/audio from assets/network/file directly from Flutter, compatible with android / ios / web / macos, displays notifications

| 项目 | 数值 |
|------|------|
| ⭐ Stars | 773 |
| 📋 Open Issues | 271 条 |
| 🐛 点击无响应 Bug | **5 条** |
| 📦 近期版本（1 年内）| 0 个 |
| 🏆 综合得分 | `0.615` |

#### 🖱 点击 / 点按无响应 Bug（5 条）

| Issue 标题 | 时间 | 链接 |
|:----------|:----:|:----:|
| Buttons not working on notification in android 13  | 2023-11-30 | [查看](https://github.com/florent37/Flutter-AssetsAudioPlayer/issues/816) |
| Handle certificate issues with old Android versions | 2022-05-25 | [查看](https://github.com/florent37/Flutter-AssetsAudioPlayer/issues/697) |
| Android TV notifications stop doesn't work / background playing doesn't stop | 2021-10-17 | [查看](https://github.com/florent37/Flutter-AssetsAudioPlayer/issues/629) |
| PlatformException(PLAY_ERROR, Cannot play ipod-library://item/item.mp3?id=8952320356688757343, The requested URL was not found on this server., null) | 2021-05-28 | [查看](https://github.com/florent37/Flutter-AssetsAudioPlayer/issues/557) |
| Fail to play Example code "main_livestream.dart" with url source HLS (m3u8) audio stream in web | 2020-08-11 | [查看](https://github.com/florent37/Flutter-AssetsAudioPlayer/issues/326) |

#### 📦 版本记录（共 0 个，展示最近 0 个）

*暂无版本记录*

---

### #3 [simonoppowa/OpenNutriTracker](https://github.com/simonoppowa/OpenNutriTracker)

> 🍴 OpenNutriTracker is a free and open source calorie tracker with a focus on simplicity and privacy.

| 项目 | 数值 |
|------|------|
| ⭐ Stars | 1,611 |
| 📋 Open Issues | 141 条 |
| 🐛 点击无响应 Bug | **1 条** |
| 📦 近期版本（1 年内）| 3 个 |
| 🏆 综合得分 | `0.578` |

#### 🖱 点击 / 点按无响应 Bug（1 条）

| Issue 标题 | 时间 | 链接 |
|:----------|:----:|:----:|
| Bug: scanner is broken on v 1.0.0 on android 10, shows rainbow pixels instead of image from camera | 2025-10-07 | [查看](https://github.com/simonoppowa/OpenNutriTracker/issues/280) |

#### 📦 版本记录（共 10 个，展示最近 6 个）

| 版本 | 发布时间 | 状态 | 更新摘要 |
|:-----|:--------:|:----:|:--------|
| [v1.0.0](https://github.com/simonoppowa/OpenNutriTracker/releases/tag/v1.0.0) | 2025-05-09 | ✅ 近期 | First Official Release Version |
| [v0.10.0](https://github.com/simonoppowa/OpenNutriTracker/releases/tag/v0.10.0) | 2025-04-20 | ✅ 近期 | Open Beta Release |
| [v0.9.0](https://github.com/simonoppowa/OpenNutriTracker/releases/tag/v0.9.0) | 2025-03-07 | ✅ 近期 | Open Beta Release |
| [v0.8.0](https://github.com/simonoppowa/OpenNutriTracker/releases/tag/v0.8.0) | 2025-01-27 | ⬜ 旧版 | Open Beta Release |
| [v0.7.2](https://github.com/simonoppowa/OpenNutriTracker/releases/tag/v0.7.2) | 2025-01-16 | ⬜ 旧版 | Open Beta Release |
| [v0.7.1](https://github.com/simonoppowa/OpenNutriTracker/releases/tag/v0.7.1) | 2025-01-14 | ⬜ 旧版 | Open Beta Release |

---

### #4 [ubuntu-flutter-community/musicpod](https://github.com/ubuntu-flutter-community/musicpod)

> Music, radio, television and podcast player for Ubuntu, MacOs and maybe soon Android

| 项目 | 数值 |
|------|------|
| ⭐ Stars | 623 |
| 📋 Open Issues | 53 条 |
| 🐛 点击无响应 Bug | **1 条** |
| 📦 近期版本（1 年内）| 11 个 |
| 🏆 综合得分 | `0.577` |

#### 🖱 点击 / 点按无响应 Bug（1 条）

| Issue 标题 | 时间 | 链接 |
|:----------|:----:|:----:|
| feat(Android): make export import buttons more clear in their purpose | 2025-05-21 | [查看](https://github.com/ubuntu-flutter-community/musicpod/issues/1318) |

#### 📦 版本记录（共 60 个，展示最近 6 个）

| 版本 | 发布时间 | 状态 | 更新摘要 |
|:-----|:--------:|:----:|:--------|
| [v2.15.0](https://github.com/ubuntu-flutter-community/musicpod/releases/tag/v2.15.0) | 2026-03-03 | ✅ 近期 | ## [2.15.0](https://github.com/ubuntu-flutter-community/musicpod/compare/v2.14.0...v2.15.0) (2026-03 |
| [v2.14.0](https://github.com/ubuntu-flutter-community/musicpod/releases/tag/v2.14.0) | 2025-10-29 | ✅ 近期 | ## [2.14.0](https://github.com/ubuntu-flutter-community/musicpod/compare/v2.13.0...v2.14.0) (2025-10 |
| [v2.13.0](https://github.com/ubuntu-flutter-community/musicpod/releases/tag/v2.13.0) | 2025-06-12 | ✅ 近期 | ## [2.13.0](https://github.com/ubuntu-flutter-community/musicpod/compare/v2.12.0...v2.13.0) (2025-06 |
| [v2.12.0](https://github.com/ubuntu-flutter-community/musicpod/releases/tag/v2.12.0) | 2025-05-13 | ✅ 近期 | ## [2.12.0](https://github.com/ubuntu-flutter-community/musicpod/compare/v2.11.4...v2.12.0) (2025-05 |
| [v2.11.4](https://github.com/ubuntu-flutter-community/musicpod/releases/tag/v2.11.4) | 2025-04-30 | ✅ 近期 | ## [2.11.4](https://github.com/ubuntu-flutter-community/musicpod/compare/v2.11.3...v2.11.4) (2025-04 |
| [v2.11.3](https://github.com/ubuntu-flutter-community/musicpod/releases/tag/v2.11.3) | 2025-04-30 | ✅ 近期 | ## [2.11.3](https://github.com/ubuntu-flutter-community/musicpod/compare/v2.11.2...v2.11.3) (2025-04 |

---

### #5 [namidaco/namida](https://github.com/namidaco/namida)

> A Beautiful and Feature-rich Music & Video Player with Youtube Support, Built in Flutter

| 项目 | 数值 |
|------|------|
| ⭐ Stars | 5,062 |
| 📋 Open Issues | 129 条 |
| 🐛 点击无响应 Bug | **1 条** |
| 📦 近期版本（1 年内）| 3 个 |
| 🏆 综合得分 | `0.569` |

#### 🖱 点击 / 点按无响应 Bug（1 条）

| Issue 标题 | 时间 | 链接 |
|:----------|:----:|:----:|
| [FEATURE REQUEST] Direct usb access | 2025-12-23 | [查看](https://github.com/namidaco/namida/issues/790) |

#### 📦 版本记录（共 18 个，展示最近 6 个）

| 版本 | 发布时间 | 状态 | 更新摘要 |
|:-----|:--------:|:----:|:--------|
| [v5.6.1](https://github.com/namidaco/namida/releases/tag/v5.6.1) | 2026-01-01 | ✅ 近期 | ## happy new year everyone! new version here with some cool new features and many changes and improv |
| [v5.3.9](https://github.com/namidaco/namida/releases/tag/v5.3.9) | 2025-09-03 | ✅ 近期 | ## hey guys, small update here ^^ new features and lots of improvements, also an integration with [n |
| [v5.2.6](https://github.com/namidaco/namida/releases/tag/v5.2.6) | 2025-07-08 | ✅ 近期 | hey guys ^^ its been a while  new update is here, in this one i focused a lot about app performanc |
| [v5.0.4](https://github.com/namidaco/namida/releases/tag/v5.0.4) | 2025-03-06 | ⬜ 旧版 | ### v5 with some hot new features! 🔥  ### 🎉 New Features:    - c92a8a3: headset buttons (single/d |
| [v4.8.6](https://github.com/namidaco/namida/releases/tag/v4.8.6) | 2025-01-01 | ⬜ 旧版 | happi new year cuties <3  new veersion for ya with cool features and maany tweaks n fixes, enjoy!  |
| [v4.7.2](https://github.com/namidaco/namida/releases/tag/v4.7.2) | 2024-11-22 | ⬜ 旧版 | ### 🎉 New Features:    - dfaf5f5: local video library & playback this also includes - refactor for  |

---

### #6 [nt4f04uNd/sweyer](https://github.com/nt4f04uNd/sweyer)

> Music player built with Flutter

| 项目 | 数值 |
|------|------|
| ⭐ Stars | 216 |
| 📋 Open Issues | 58 条 |
| 🐛 点击无响应 Bug | **2 条** |
| 📦 近期版本（1 年内）| 1 个 |
| 🏆 综合得分 | `0.467` |

#### 🖱 点击 / 点按无响应 Bug（2 条）

| Issue 标题 | 时间 | 链接 |
|:----------|:----:|:----:|
| Do not reset selection upon cancelling deletion | 2023-05-05 | [查看](https://github.com/nt4f04uNd/sweyer/issues/99) |
| Light theme system UI colors are poorly visible | 2023-05-05 | [查看](https://github.com/nt4f04uNd/sweyer/issues/97) |

#### 📦 版本记录（共 15 个，展示最近 6 个）

| 版本 | 发布时间 | 状态 | 更新摘要 |
|:-----|:--------:|:----:|:--------|
| [1.0.13](https://github.com/nt4f04uNd/sweyer/releases/tag/1.0.13) | 2025-03-09 | ✅ 近期 | ## What's Changed * Update all GitHub actions dependencies by @Abestanis in https://github.com/nt4f |
| [1.0.12](https://github.com/nt4f04uNd/sweyer/releases/tag/1.0.12) | 2024-08-31 | ⬜ 旧版 | ## What's Changed * Fix running app in a different zone than the framework was initialized by @Abes |
| [1.0.11](https://github.com/nt4f04uNd/sweyer/releases/tag/1.0.11) | 2024-06-29 | ⬜ 旧版 | ## What's Changed * Fix Fastlane CD by @nt4f04uNd in https://github.com/nt4f04uNd/sweyer/pull/118  |
| [1.0.10](https://github.com/nt4f04uNd/sweyer/releases/tag/1.0.10) | 2024-06-12 | ⬜ 旧版 | First release generated by Fastlane CD!  ## What's Changed * Added Turkish translation by @eren-i |
| [1.0.9](https://github.com/nt4f04uNd/sweyer/releases/tag/1.0.9) | 2023-04-08 | ⬜ 旧版 | [@Abestanis]: https://github.com/Abestanis  - [Fix being unable to request permissions to view aud |
| [1.0.8](https://github.com/nt4f04uNd/sweyer/releases/tag/1.0.8) | 2023-04-06 | ⬜ 旧版 | [@Abestanis]: https://github.com/Abestanis  All the work related to this version can be found in t |

---

### #7 [moritz-weber/mucke](https://github.com/moritz-weber/mucke)

> mucke - android music player

| 项目 | 数值 |
|------|------|
| ⭐ Stars | 251 |
| 📋 Open Issues | 60 条 |
| 🐛 点击无响应 Bug | **1 条** |
| 📦 近期版本（1 年内）| 0 个 |
| 🏆 综合得分 | `0.452` |

#### 🖱 点击 / 点按无响应 Bug（1 条）

| Issue 标题 | 时间 | 链接 |
|:----------|:----:|:----:|
| Import button not showing | 2024-01-24 | [查看](https://github.com/moritz-weber/mucke/issues/171) |

#### 📦 版本记录（共 12 个，展示最近 6 个）

| 版本 | 发布时间 | 状态 | 更新摘要 |
|:-----|:--------:|:----:|:--------|
| [v1.5.1](https://github.com/moritz-weber/mucke/releases/tag/v1.5.1) | 2023-09-10 | ⬜ 旧版 |  |
| [v1.5.0](https://github.com/moritz-weber/mucke/releases/tag/v1.5.0) | 2023-09-07 | ⬜ 旧版 |  |
| [v1.4.0](https://github.com/moritz-weber/mucke/releases/tag/v1.4.0) | 2023-07-09 | ⬜ 旧版 |  |
| [v1.3.1](https://github.com/moritz-weber/mucke/releases/tag/v1.3.1) | 2023-05-10 | ⬜ 旧版 | - Fixed bug with translation priorities (#79) |
| [v1.3.0](https://github.com/moritz-weber/mucke/releases/tag/v1.3.0) | 2023-05-03 | ⬜ 旧版 | - Fixed bug in "Append to manually queued songs" - Fixed bug in queue when moving a song directly b |
| [v1.2.0](https://github.com/moritz-weber/mucke/releases/tag/v1.2.0) | 2023-03-11 | ⬜ 旧版 | - Upgrade to Flutter 3.7 & dependency updates - Fix album cover bug on currently playing page (#57) |
