from ingestion_pipeline import search
from dotenv import load_dotenv
import httpx

load_dotenv()

query = "form an icp (ideal customer profile) from all the documents take most common lead awarness levels, identities, pain points, goals, dreams, desires, internal conficts, doubts, enemies, external barriers, failed attempts, what did not work, the emotional drivers - why now, and what makes them buy and give me detailed report with quotes based on that"

results = search(query, k=5)

print(f"User Query: {query}")
print("--- Context ---")
for i, (text, meta, dist) in enumerate(results, 1):
    print(f"Document {i} (source: {meta['source']}, distance: {dist:.2f}):")
    print(f"{text}\n")

combined_input = f"""Based on the following documents, please answer this question: {query}

Documents:
{chr(10).join([f"- {text}" for text, meta, dist in results])}

Please provide a clear, helpful answer using only the information from these documents. If you can't find the answer in the documents, say "I don't have enough information to answer that question based on the provided documents."
"""

LLM_MODEL = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF"

print("\n--- Generated Response ---")

response = httpx.post(
    "http://localhost:11434/api/chat",
    json={
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": combined_input},
        ],
        "stream": False,
    },
    timeout=120,
)

if response.status_code == 200:
    result = response.json()
    print(result["message"]["content"])
else:
    print(f"Error: {response.status_code}")
    print(response.text)
