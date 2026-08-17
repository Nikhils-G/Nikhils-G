<div align="center">

<img src="assets/header.svg" width="800" alt="nikhil@ai-agents:~$ whoami — Nikhil Sukthe, AI Engineer, building agents that automate business across voice, WhatsApp, chat and email">

</div>

I build **AI agents that automate real business and get measured on outcomes** — voice agents that talk on the phone (LiveKit + SIP, streaming STT-LLM-TTS), WhatsApp commerce agents that take a customer from catalog to Razorpay payment without leaving the chat, and the chat & email automation around them. Founding AI Engineer at [Fika.ai](https://powersmy.biz). The metric is never the demo — it's collection rates, bookings, and latency. Hyderabad, India.

### Open source

[**livekit/agents #4798**](https://github.com/livekit/agents/pull/4798) · `fix(sarvam): prevent transcript loss after long agent responses`

A race condition in the Sarvam STT plugin: agent responses longer than ~10 s triggered premature task cancellation while buffered audio was still being processed — transcripts were silently dropped and the agent went mute mid-call. Found it running live voice-agent operations; fixed it upstream.

### Now

| | |
|---|---|
| **Building** | Multi-channel AI agents (voice · WhatsApp · chat · email) for healthcare, fintech and real-estate clients at Fika.ai |
| **Running** | Live voice-agent ops — SIP trunks, STT/TTS provider A/B tests, per-call cost & latency telemetry |
| **Exploring** | Speech-to-speech (Gemini Live), predictive & outbound dialers, MCP tool servers |

### Selected work

| | Project | The number that matters |
|---|---|---|
| Voice | **WhatsApp Voice Bridge** | WhatsApp Desktop → WASAPI → LiveKit → Gemini Live: two-way audio at **300–800 ms RTT**, zero SIP cost |
| Voice | **LiveKit SIP Manager** | Full-stack SIP ops dashboard — trunks, dispatch rules, IP whitelisting, dialer — **zero CLI** |
| Agents | **NBFC collections voice agent** | Production collections calls at Fika.ai — **collection rate up 50%** |
| Agents | **LangGraph + RAG assistant** | **Sub-5 s** end-to-end latency, 15% engagement uplift |
| Lab | [**ai-experiments-lab**](https://github.com/Nikhils-G/ai-experiments-lab) | Reproducible experiments across ML · DL · NLP · LLMs, one concept at a time |

More on [nikhilsukthe.vercel.app](https://nikhilsukthe.vercel.app/).

### One agent runtime, every channel

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#2e1f54", "primaryTextColor": "#ece7f4", "primaryBorderColor": "#a78bfa", "lineColor": "#f0a63a", "fontFamily": "monospace", "fontSize": "14px"}}}%%
flowchart LR
    P["Phone · PSTN / SIP"] --> R["Agent runtime — LiveKit · STT ⇄ TTS"]
    W["WhatsApp"] --> R
    C["Chat · Email"] --> R
    R --> L["LLM · tools · RAG · memory"]
    L --> O["Outcomes — payments · bookings · collections · support"]
```

### Stack

<img src="assets/stack.svg" width="800" alt="Stack — voice: LiveKit, SIP/WebRTC, STT/TTS, Gemini Live · agents: LangGraph, LangChain, MCP, RAG, LoRA/QLoRA · backend: Python, FastAPI, WebSockets, MongoDB, Redis, PostgreSQL · infra: Docker, Kubernetes, AWS, GCP Vertex, Langfuse · data: PyTorch, Pinecone, FAISS, ChromaDB">

### Live stats

<img src="assets/fetch-card.svg" width="820" alt="Neofetch-style card with live GitHub stats for Nikhils-G">

### Recent activity

<!-- ACTIVITY:START -->
- Quiet on the public feed lately — the work is in production.
<!-- ACTIVITY:END -->

---

<div align="center">

[Website](https://nikhilsukthe.vercel.app/) · [LinkedIn](https://www.linkedin.com/in/nikhilsukthe) · [Email](mailto:sukthenikhil@gmail.com) · [ORCID](https://orcid.org/0009-0009-8318-1049)

<sub>This profile updates itself — a daily [GitHub Action](.github/workflows/profile.yml) runs [one Python script](scripts/update_profile.py) that regenerates the stats card and activity feed. <!-- UPDATED:START -->
Last refreshed: 2026-08-18 (UTC).
<!-- UPDATED:END --></sub>

<img src="https://github.com/Nikhils-G/Nikhils-G/actions/workflows/profile.yml/badge.svg" alt="profile refresh status">

</div>
