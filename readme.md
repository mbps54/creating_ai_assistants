# Course “Creating AI Assistants for IT Infrastructure”

🚀 LLM + automation = next-generation automation

What we do in the course:
- Connect LLM via Python and LangChain
- Use an AI assistant for log analysis
- Apply RAG to work with documentation and knowledge bases
- Build an AI assistant for network management

The usual human–machine interaction turns into a convenient human–human chat.

👉 Course link: <...>

## Target audience

- Network engineers and DevNetOps specialists who want to automate routine tasks using modern AI tools
- IT professionals looking to apply LLM in infrastructure tasks

## Skills you will gain

- Building LLM agents with tools
- Integration with CMDB, logs, VLAN, wiki
- RAG on your own documents
- Log analysis using LLM
- Creating memory in dialogue
- Debugging and tuning LangChain applications

## 🚀 How to launch the final application

```bash
git clone https://github.com/mbps54/creating_ai_assistants.git
cd creating_ai_assistants
python -m venv ~/llm
source ~/llm/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-proj-<...>
cd lessons/11_lesson_tshoot
streamlit run app.py
```
