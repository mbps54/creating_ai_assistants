from langchain_openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

emb = OpenAIEmbeddings()
vec1 = emb.embed_query("How to arrange a business trip?")
vec2 = emb.embed_query("How to get access to the office?")

similarity = cosine_similarity([vec1], [vec2])[0][0]
print(f"\nSimilarity between texts: {similarity:.2f}")
