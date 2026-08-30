<div align="center">

<img src="assets/header.svg" width="800" alt="nikhil@ai-agents:~$ whoami — Nikhil Sukthe, AI Engineer, building agents that automate business across voice, WhatsApp, chat and email">

</div>

**I build AI agents that businesses pay for** — voice agents that make and take phone calls, WhatsApp agents that sell (catalog to Razorpay payment without leaving the chat), and the chat and email automation around them. Founding AI Engineer at [Fika.ai](https://powersmy.biz), Hyderabad. The metric is never the demo. It's collection rates, bookings, and milliseconds.

### What production taught me

**Latency is the product.** Past about 800 ms, callers notice the lag. My WhatsApp Voice Bridge (WhatsApp Desktop → WASAPI → LiveKit → Gemini Live) holds two-way audio at **300–800 ms** round-trip, with zero SIP cost.

**A silent agent is the worst bug.** In LiveKit's Sarvam STT plugin, agent responses longer than ~10 s cancelled the task while audio was still buffered — transcripts vanished and the agent went mute mid-call. I found it on live calls and fixed it upstream: [livekit/agents #4798](https://github.com/livekit/agents/pull/4798) *(PR open)*.

**Same brain, different mouth.** Phone, WhatsApp, chat and email run on one agent runtime — LiveKit and SIP for voice, LangGraph with RAG and MCP for reasoning, FastAPI, Redis and Postgres underneath, Langfuse so the numbers are measured, not guessed.

**One concept at a time.** [ai-experiments-lab](https://github.com/Nikhils-G/ai-experiments-lab): 17 notebooks, each a single idea worked end to end — autoencoders, LSTMs, CNNs on Fashion-MNIST, GPT-2 generation, K-Means, PCA, cross-validated model tuning — and LoRA/QLoRA fine-tuning in the runtime's LLM core.

### Work

| | |
|---|---|
| **NBFC collections voice agent** | Production collections calls at Fika.ai — **collection rate up 50%** |
| **LiveKit SIP Manager** | Trunks, dispatch rules, IP whitelisting, dialer — the whole SIP ops surface, **zero CLI** |
| **LangGraph + RAG assistant** | **Sub-5 s** end to end, **15%** engagement uplift |
| **Now** | Multi-channel agents for healthcare, fintech and real-estate clients · live voice ops — SIP trunks, STT/TTS A/B tests, per-call cost & latency telemetry · exploring speech-to-speech, predictive dialers, MCP tool servers |

### One runtime, every channel

<img src="assets/stack.svg" width="800" alt="Nikhil's stack drawn as a circuit board: Phone/SIP, WhatsApp and Chat/Email inputs flow into an Agent Runtime chip (LiveKit, WebRTC, SIP, STT and TTS, Gemini Live, Sarvam) wired to an LLM Core chip (LangGraph, MCP, RAG, LoRA/QLoRA), mounted on an infra bus of FastAPI/WebSockets, MongoDB/Redis/Postgres, Docker/Kubernetes, AWS/GCP Vertex, Langfuse, and vector databases">

### Live stats

<img src="assets/fetch-card.svg" width="820" alt="Neofetch-style card with live GitHub stats for Nikhils-G">

---

<div align="center">

[Website](https://nikhilsukthe.vercel.app/) · [LinkedIn](https://www.linkedin.com/in/nikhilsukthe) · [Email](mailto:sukthenikhil@gmail.com) · [ORCID](https://orcid.org/0009-0009-8318-1049)

<sub>This profile updates itself — a daily [GitHub Action](.github/workflows/profile.yml) runs [one Python script](scripts/update_profile.py) that regenerates the stats card. <!-- UPDATED:START -->
Last refreshed: 2026-08-25 (UTC).
<!-- UPDATED:END --></sub>

<img src="https://github.com/Nikhils-G/Nikhils-G/actions/workflows/profile.yml/badge.svg" alt="profile refresh status">

</div>
