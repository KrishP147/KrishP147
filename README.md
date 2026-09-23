<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://capsule-render.vercel.app/api?type=rect&color=0:0D1117,100:161B22&height=140&section=header&text=Krish%20Punjabi&fontSize=40&fontColor=E6EDF3&fontAlign=50&fontAlignY=45&desc=Software%20Engineering%20%40%20Waterloo%20%E2%80%94%20agentic%20AI%20%C2%B7%20full-stack%20%C2%B7%20Praxic&descSize=15&descAlign=50&descAlignY=70&descColor=8B949E&animation=fadeIn" />
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:FFFFFF,100:F6F8FA&height=140&section=header&text=Krish%20Punjabi&fontSize=40&fontColor=1F2328&fontAlign=50&fontAlignY=45&desc=Software%20Engineering%20%40%20Waterloo%20%E2%80%94%20agentic%20AI%20%C2%B7%20full-stack%20%C2%B7%20Praxic&descSize=15&descAlign=50&descAlignY=70&descColor=57606A&animation=fadeIn" alt="Krish Punjabi" />
</picture>

<div align="center">

[![Site](https://img.shields.io/badge/site-krishpunjabi.com-000000?style=flat-square)](https://krishpunjabi.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://ca.linkedin.com/in/krish-punjabi)

</div>

## About

I'm a Software Engineering student at the University of Waterloo. This year I worked at Ciena building agentic AI tooling that turns hours of manual crash debugging into minutes, shipped full-stack AI products end to end across backend, frontend, infrastructure, and deployment, and I'm co-founding **Praxic**, a startup capturing the operational knowledge small teams keep only in their heads. I like problems where the interesting part is designing the right abstraction, and I do my best work when I'm handed a substantial problem and the room to own it.

## Work Focus

| | |
|---|---|
| 🔨 Building | **Praxic** — turning tacit team workflows into approved, running automations |
| 🔬 Researching | agentic AI tooling at Ciena — a 15-agent crash-analysis pipeline (Google ADK) |
| 🚀 Shipping | [NutriSync](https://nutrisync.me) · [FrameShift](https://frame-shift.tech) — solo, live, real users |
| 🏆 Competing | Hack the North · YHack · DeltaHacks · Amazon Robotics Hackathon · GoOnHacks |

## Recent Activity

_Auto-updated daily by [`.github/workflows/recent-activity.yml`](.github/workflows/recent-activity.yml) — merged PRs and pushes across active repos, newest first._

<!--START_SECTION:activity-->
- **2026-07-16** — merged PR in [KrishP147/frameshift](https://github.com/KrishP147/frameshift/pull/2): merging Justin's changes w improvements to prod
- **2025-11-19** — merged PR in [KrishP147/nutrisync-backend](https://github.com/KrishP147/nutrisync-backend/pull/12): Fix GOOGLE_API_KEY environment variable loading
<!--END_SECTION:activity-->

## Projects

### Solo-Built

| Project | What it does | Stack |
|---|---|---|
| [NutriSync](https://github.com/KrishP147/nutrisync) — live at [nutrisync.me](https://nutrisync.me) | AI nutrition tracking: Gemini food-photo recognition over a 400K-item USDA dataset, BMR/TDEE goal engine, intermittent-fasting tracking, 222 tests in CI | React · FastAPI · Supabase |
| [FrameShift](https://github.com/KrishP147/frameshift) — live at [frame-shift.tech](https://frame-shift.tech) | Object-aware video editor — click any object on a frame, confirm the mask, then remove/recolor/resize/replace it across the clip. Started at Hack Canada 2026 | Next.js · FastAPI (Modal GPU) · SAM 2 |
| [WatSpend](https://github.com/KrishP147/watspend) — live at [watspend.vercel.app](https://watspend.vercel.app) | Chrome extension → dashboard pipeline for UWaterloo WatCard spending: syncs transaction history, visualizes it | React · Node/Express · MySQL |
| [ExamStudyPlanner](https://github.com/KrishP147/examstudyplanner) | Multi-agent system (Google ADK) generating day-by-day study plans from course syllabi, midterm topics, and textbooks | Python · Google ADK |
| [youtubetomp3](https://github.com/KrishP147/youtubetomp3) | Batch YouTube→mp3/mp4 converter, plus a Spotify-playlist screenshot flow: OCR the track list, search and download each track | Flask · yt-dlp · Tesseract OCR |

### Built with Teams / Hackathons

| Project | Result | What it does |
|---|---|---|
| [Dryft Decode Engine](https://github.com/KrishP147/dryft-decode-engine) | 5th of 58 — Hack the North 2026 | From-scratch Triton/CUDA decode engine for Qwen3-4B on one H100: static KV cache, fused kernels, speculative decoding inside the CUDA graph |
| [GodsEye](https://github.com/KrishP147/godseye) | 2nd of 212 — Polymarket track, YHack 2026 | AI forecaster personas debate live Polymarket events and converge on a probability; led the frontend (3D globe, live debate feed) |
| [Zephyr](https://github.com/KrishP147/zephyr) | Top 12 — Warp "Best Developer Tool," Hack the North 2026 | Control plane for AI agents — a small decision model routes each step, and nothing private or irreversible leaves without policy approval. Broad contribution across the run engine: provider routing, approvals/pause-resume, tool broker, CI |
| [ColourGuard](https://github.com/KrishP147/colourguard) | DeltaHacks 2026 | Real-time navigation assistant for colorblind users (Expo · React Native · YOLOv3) |
| [ML-CV-Target-Tracking](https://github.com/KrishP147/ML-CV-Target-Tracking) | Waterloo Aerial Robotics Group | Autonomy modules bridging perception and flight — [ObjectTracker (DepthAI + software tracker)](https://github.com/UWARG/ML-CV-Target-Tracking/pull/1) and [DroneCommander (MAVLink move-to / face-target)](https://github.com/UWARG/ML-CV-Target-Tracking/pull/2), both open PRs to the org repo |
| [Autonomous Maze-Solving Robot](https://github.com/KrishP147/autonomous-maze-solving-robot) | 2nd of 50+ — Amazon Robotics Hackathon 2025 | 5-mode autonomous robot: Kalman-filtered sensor fusion, PID line-following, dead-end detection; the team also built a congestion-aware Dijkstra router for multi-source package delivery ([ArHackathon2025](https://github.com/KrishP147/ArHackathon2025)) |
| [BaddieLink](https://github.com/KrishP147/BaddieLink) | Top 8 — GoOnHacks 2025 | Gamified LinkedIn "dating scout" — PhantomBuster-sourced candidate cards, Gemini-drafted icebreakers/DMs; built the Gemini integration |

### Early / Coursework

| Project | What it is |
|---|---|
| [basic-alarm-app](https://github.com/KrishP147/basic-alarm-app) | Dark-themed alarm clock — real-time display, localStorage persistence, optional Express backend |
| [ics3u-ics4u-assorted-projects](https://github.com/KrishP147/ics3u-ics4u-assorted-projects) | Java coursework from ICS3U/ICS4U — arrays, OOP, GUI, recursion, Swing |

## A Benchmark, Not a Badge

The GPU work, in one table — a from-scratch Qwen3-4B decode engine built for Hack the North 2026, judged entirely on hidden benchmarks:

| Build | tok/s | What changed |
|---|---|---|
| v1 | 440.8 | Static KV cache, CUDA-graphed decode, plain PyTorch ops |
| v5 | 968.9 | Fused Triton kernels: RMSNorm, split-KV attention, split-K GEMV |
| v15 | ~1047 | Programmatic dependent launch, mask-free GEMV — plateaus at ~71% of measured HBM bandwidth |
| 2a527ff | 1098.6 | In-graph speculative decoding — draft and verify inside the CUDA graph |
| final | **1156.1** | Margin-based draft acceptance within the judge's tolerance — 2.6x v1, 5th of 58 teams |

Full log: [`CONTEXT.md`](https://github.com/KrishP147/dryft-decode-engine)

## Skills

| | |
|---|---|
| Languages | Python, TypeScript/JavaScript, C++, C, Java, SQL |
| Frontend | React, Next.js, Vite, Three.js, Tailwind, Zustand |
| Backend & APIs | FastAPI, Node.js/Express, REST, Server-Sent Events, async SQLAlchemy |
| Data & Infra | PostgreSQL, MySQL, SQLite, Supabase, Docker, Modal, Vercel, GitHub Actions |
| AI & ML | PyTorch, Google ADK, Gemini, SAM 2, multi-agent orchestration, MCP |
| GPU & Inference | Triton, CUDA graphs, fused kernels, speculative decoding, roofline analysis |
| Embedded & Robotics | MAVLink, Arduino, Kalman filtering, PID control |

## Honours

- 5th of 58 — Dryft inference-speed challenge, Hack the North 2026
- 2nd of 212 — Polymarket-sponsored Prediction Markets track, YHack 2026
- 2nd of 50+ — Amazon Robotics Hackathon 2025
- Top 8 — GoOnHacks 2025
- Selected participant — Microsoft AI Business Leaders program

## Contribution Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/KrishP147/KrishP147/output/github-snake-dark.svg" />
  <img src="https://raw.githubusercontent.com/KrishP147/KrishP147/output/github-snake.svg" alt="Contribution snake" />
</picture>

<div align="center">

[![Site](https://img.shields.io/badge/site-krishpunjabi.com-000000?style=flat-square)](https://krishpunjabi.com)

</div>
