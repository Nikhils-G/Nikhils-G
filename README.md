<div align="center">

<img src="assets/intro.svg" width="800" alt="Nikhil Sukthe, Founding AI Engineer at Fika.ai, Hyderabad. I build AI agents, and the models behind them. Voice agents that take live phone calls. WhatsApp agents that take payments without leaving the chat. When turn detection wasn't good enough, I trained my own. A collections agent lifting recovery by around 50%. A dialer placing 30,000 calls a day. Available today, for voice AI, agents, and fine-tuning.">

</div>

I build AI agents and the models behind them, end to end: from training and fine-tuning to production systems.

At [Fika.ai](https://powersmy.biz), I work on real-time voice pipelines on LiveKit (SIP + WebRTC): STT to LLM to TTS, Gemini Live speech-to-speech, Sarvam and Cartesia for Hindi and Telugu, and Silero VAD for speech detection. Turn detection pulled me in deep enough that I built my own model for it: [TurnWave](https://github.com/Nikhils-G/turnwave), a 7M-parameter transformer trained from scratch in PyTorch that beat the baseline I measured it against.

On the ML side I work with PyTorch, TensorFlow, and Hugging Face Transformers. I've fine-tuned Qwen2.5-7B with QLoRA and served it on vLLM, worked hands-on with quantization, and engineered a 200k-pair dataset where I beat the cue-word baseline (F1 0.798 vs 0.753). I've gone through the transformer architecture from the ground up, implementing attention, RoPE, and a BPE tokenizer myself.

Some of what I've shipped is running at real scale today: a collections agent that lifted recovery by around 50%, a dialer placing about 30,000 calls a day, a WhatsApp commerce agent that takes Razorpay payments without leaving the chat, and LangGraph + RAG agents serving live customer traffic.

My backend is FastAPI, WebSockets, async Python, MongoDB, Redis, and Postgres, with Grafana, Prometheus, Loki, and Langfuse watching everything in production. I recently started contributing to open source and fixed a race condition in LiveKit's Sarvam STT plugin that was silently dropping transcripts ([livekit/agents #4798](https://github.com/livekit/agents/pull/4798)).

I reach for TypeScript and React when a dashboard is needed, SQL everywhere, and I'm currently learning Go because LiveKit's server is written in it.

Always happy to talk voice AI, agents, or fine-tuning.

<div align="center">

[LinkedIn](https://www.linkedin.com/in/nikhilsukthe) · [Email](mailto:sukthenikhil@gmail.com) · [Website](https://nikhilsukthe.vercel.app/) · [ORCID](https://orcid.org/0009-0009-8318-1049)

</div>
