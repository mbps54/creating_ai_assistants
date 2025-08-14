import json
from pydantic import BaseModel
from langchain.chat_models import init_chat_model  # model initialization
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# 1. Output structure description
class LogEntry(BaseModel):
    message: str
    severity: str  # values: low, mid, high

# 2. Parser matching the structure
parser = PydanticOutputParser(pydantic_object=LogEntry)

# 3. Instruction + escape the format according to PydanticOutputParser
instruction = (
    "You are an assistant for analyzing network logs from network equipment. "
    "Determine the message severity: ‘low’, ‘mid’, or ‘high’. "
    "Return the answer strictly in the format below (JSON):\n\n"
    "{{" + parser.get_format_instructions().replace("{", "{{").replace("}", "}}") + "}}"
)

# 4. Prompt template with a variable
prompt = ChatPromptTemplate.from_messages([
    ("system", instruction),
    ("user", "{log}")
])

# 5. Initialize the model via LangChain
llm = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai",
    temperature=0.3
)

# 6. Build the chain: prompt → model → parser
chain = prompt | llm | parser

# 7. Example input message
log_message = "Today we received this log from the switch: %SYS-3-CPUHOG: Task ran for 3000ms"

# 8. Invoke the chain
result = chain.invoke({"log": log_message})

# 9. Output the result in JSON format
print(json.dumps(result.model_dump(), indent=2))