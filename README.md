<div align="center">

<img src="assets/header.svg" width="800" alt="nikhil@ai-agents:~$ whoami — Nikhil Sukthe, AI Engineer, building agents that automate business across voice, WhatsApp, chat and email">

</div>

I build **AI agents that automate real business and get measured on outcomes** — and the models underneath them. The whole arc: EDA and feature work on messy production data, training and fine-tuning (PyTorch, LoRA/QLoRA, 4-bit quantization), then shipping — voice agents that talk on the phone (LiveKit + SIP, streaming STT-LLM-TTS), WhatsApp commerce agents that take a customer from catalog to Razorpay payment without leaving the chat, and the chat & email automation around them. Founding AI Engineer at [Fika.ai](https://powersmy.biz). The metric is never the demo — it's collection rates, bookings, latency and eval scores. Hyderabad, India.

### Pick up the phone

<img src="assets/call.svg" width="800" alt="A live call with Nikhil's voice agent: the call connects, a recording timer counts up in real time, and the agent's transcript types itself out — who Nikhil is, what he has shipped, and how to reach him">

<sub>That timer is real time. There is no server behind it — the whole call is one hand-written SVG.</sub>

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

| | Project | In one line |
|---|---|---|
| Voice | **WhatsApp Voice Bridge** | WhatsApp Desktop → WASAPI → LiveKit → Gemini Live: two-way audio at **300–800 ms RTT**, zero SIP cost |
| Voice | **LiveKit SIP Manager** | Full-stack SIP ops dashboard — trunks, dispatch rules, IP whitelisting, dialer — **zero CLI** |
| Agents | **NBFC collections voice agent** | Production collections calls at Fika.ai — **collection rate up 50%** |
| Agents | **LangGraph + RAG assistant** | **Sub-5 s** end-to-end latency, 15% engagement uplift |
| Deep learning | [**Tooth detection & FDI numbering**](https://github.com/Nikhils-G/Automated-Tooth-Detection-and-FDI-Numbering-Using-Deep-Learning) | CNN pipeline that finds every tooth on a dental X-ray and assigns its FDI number automatically |
| ML | [**Fraud detection on banking data**](https://github.com/Nikhils-G/Fraud-Detection-with-SVMSMOTE-Neural-Networks) | SVMSMOTE resampling + neural networks on heavily imbalanced transaction data |
| Lab | [**ai-experiments-lab**](https://github.com/Nikhils-G/ai-experiments-lab) | Reproducible experiments across ML · DL · NLP · LLMs, one concept at a time |

More on [nikhilsukthe.vercel.app](https://nikhilsukthe.vercel.app/).

### Meanwhile, in the lab

<img src="assets/lab.svg" width="800" alt="Nikhil's lab, live: a training run where train and validation loss curves draw themselves down across three epochs until the checkpoint saves, beside an EDA notebook where a latency scatter plot plots itself, a regression line fits with r squared 0.94, and df.describe reports 1.2M rows, zero nulls, p95 latency cut 59%, AUC 0.97, F1 0.93 — production-ready">

### One runtime, every channel

<img src="assets/stack.svg" width="800" alt="Nikhil's stack drawn as a circuit board: Phone/SIP, WhatsApp and Chat/Email inputs flow into an Agent Runtime chip (LiveKit, WebRTC, SIP, STT and TTS, Gemini Live, Sarvam) wired to an LLM Core chip (LangGraph, MCP, RAG, LoRA/QLoRA), mounted on an infra bus of FastAPI/WebSockets, MongoDB/Redis/Postgres, Docker/Kubernetes, AWS/GCP Vertex, Langfuse, and vector databases">

---

<div align="center">

<img src="assets/linger.svg" width="800" alt="You've been here a while — long enough to say hi: sukthenikhil@gmail.com">

[Website](https://nikhilsukthe.vercel.app/) · [LinkedIn](https://www.linkedin.com/in/nikhilsukthe) · [Email](mailto:sukthenikhil@gmail.com) · [ORCID](https://orcid.org/0009-0009-8318-1049)

</div>
