from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)

completion = client.chat.completions.create(
  model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
  messages=[{"role":"user","content":"Please give me a json list of the most recent 7 wonders of the world. Only output the json list, no other text."}],
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")