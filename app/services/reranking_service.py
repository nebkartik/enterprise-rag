import logfire
from flashrank import Ranker, RerankRequest
import time


def rerank_documents(docs: list[str],query:str,top_n:int=5):
    """
        Refines retrieval results by re-scoring documents against the query semantically.
        
        Why FlashRank? 
        Standard vector search (Cosine Similarity) is fast but mathematically "fuzzy."
        FlashRank uses a Cross-Encoder approach which is much more precise but usually slow.
        FlashRank solves this by using highly optimized, quantized ONNX models locally.
    """
     
    if not docs:
        logfire.warning("No documents provided for reranking.")
        return []
    try:
        start_time = time.time()
         # Use a specific cache directory to avoid permission issues in production
        ranker = Ranker(cache_dir="/tmp/flashrank")
        passages = [{"id":i,"text":doc} for i,doc in enumerate(docs)]


        request = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(request)
        reranked_docs = [doc["text"] for doc in results[:top_n]]
        total_time = time.time() - start_time
        logfire.info(f"Reranking completed in {total_time:.2f} seconds. Top {top_n} documents returned.")
        return reranked_docs
    
    except Exception as e:
        logfire.error(f"❌ [Reranker] Semantic Reranking Failed: {e}")
        # Fallback to the original Qdrant order to ensure the user still gets an answer
        return docs[:top_n]
        