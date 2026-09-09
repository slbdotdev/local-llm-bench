FROM vllm/vllm-openai:v0.28.0-cu129@sha256:50509e700235cea487715cedeb501d20a1cd15fa6a54ce93688284bd0d96995d
RUN apt-get update && apt-get install -y --no-install-recommends curl jq && rm -rf /var/lib/apt/lists/*
