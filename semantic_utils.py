#__import__('pysqlite3')
#import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import re
from langchain.docstore.document import Document
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.retrievers import BM25Retriever, EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker


def get_all_examples(examples):
    all_examples = [x for x in re.split('\n[#]{1,2} \*', examples) if len(x)>20]
    return all_examples

def get_all_outlines(outlines):
    all_outlines = [x for x in re.split('_{5,}', outlines) if len(x)>20]
    return all_outlines

def get_outline_matches(all_examples, all_outlines, compressed_docs):
    outline_dict = dict(zip(all_examples, all_outlines))
    match_outlines = ''
    for example in [x.page_content for x in compressed_docs]:
        match_outlines += outline_dict[example] + '\n\n'
    return match_outlines

def get_retrieval_matches(idea, all_examples, k_val=2):
    docs = [Document(page_content=x) for x in all_examples]
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs, embeddings)
    dense_retriever = db.as_retriever(search_kwargs = {"k":k_val})
    sparse_retriever = BM25Retriever.from_documents(docs)
    sparse_retriever.k = k_val
    ensemble_retriever = EnsembleRetriever(retrievers = [dense_retriever, sparse_retriever],
                                                        weights = [0.25, 0.75])
    hf_rerank_model = HuggingFaceCrossEncoder(model_name='mixedbread-ai/mxbai-rerank-xsmall-v1')
    compressor_hf = CrossEncoderReranker(model=hf_rerank_model, top_n=k_val)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor_hf,
        base_retriever=ensemble_retriever
    )

    compressed_docs = compression_retriever.invoke(idea)
    return compressed_docs
