# Get started with OpenAI
### First API request
```
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    input="What is LLM?"
)

print(response.output_text)
```

### chat.completions
```
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What is LLM?"}
    ],
    temperature=1.0
)

print(response.choices[0].message.content)
```

### Realtime API
```
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What is LLM?"}
    ],
    stream=True,
)

for event in stream:
    delta = event.choices[0].delta
    if delta and delta.content:
        print(delta.content, end="", flush=True)
```

### JSON response and tokens
```
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    input="What is LLM?"
)

print(response.output_text)

response_dict = response.model_dump()
print(json.dumps(response_dict, indent=2,ensure_ascii=False))
```

### Tokens usage
```
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    input="What is LLM?"
)

print(response.output_text)

print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
print(f"Total tokens: {response.usage.total_tokens}")
```

### Tokens usage: tiktoken and tokenizer
```
#pip install tiktoken

import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o-mini")
text = "What is LLM?"
tokens = enc.encode(text)

for token in tokens:
    print(f"{token} → '{enc.decode([token])}'")
```

### Structured outputs example
```
from openai import OpenAI
from pydantic import BaseModel
from ipaddress import IPv4Address

client = OpenAI()

class Device(BaseModel):
   name: str
   ip: IPv4Address  # 👈 ensures that only a valid IPv4 address gets here

response = client.responses.parse(
   model="gpt-4o-mini",
   input=[
       {"role": "system", "content": "Extract device name and IP address."},
       {"role": "user", "content": "Device router01 has IP 192.168.1.254."}
   ],
   text_format=Device
)
# Output as JSON
print(response.output_parsed.model_dump_json(indent=2))
```

### Conversation with LLM
```
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    input=[
        {"role": "user", "content": "The server is down"},
        {"role": "assistant", "content": "Did you try reboot it?"},
        {"role": "user", "content": "Of course. Still nothing"},
    ],
)
```

### Managing tokens
```
from openai import OpenAI

client = OpenAI()

response = client.responses.parse(
   model="gpt-4o-mini",
   input=[
       {"role": "system", "content": "Extract device name and IP address."},
       {"role": "user", "content": "Device router01 has IP 192.168.1.254."}
   ],
   max_output_tokens=300, # 👈 ensures the use of no more than 300 tokens for the response
)
```
