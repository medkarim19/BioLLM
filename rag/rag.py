import os
import re
from langchain_nomic.embeddings import NomicEmbeddings
#from api_app import process_dna, query_rag_model, fold_sequence

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"

### LLM

local_llm = "llama3"


### Index

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings, HuggingFaceBgeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


local_directory = r"C:\Users\mhame\OneDrive\Bureau\TalanSummerCamp-main\chromaDb"
embedding_model=NomicEmbeddings(model="nomic-embed-text-v1.5", inference_mode="local")

vectorstore = Chroma(
    persist_directory=local_directory,
    collection_name="rag-chroma",
    embedding_function=embedding_model
    
    
    
)
retriever = vectorstore.as_retriever()


### Retrieval Grader

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

# LLM
llm1 = ChatOllama(model=local_llm, format="json", temperature=0)

prompt1 = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing relevance 
    of a retrieved document to a user question. If the document contains keywords related to the user question, 
    grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here is the retrieved document: \n\n {document} \n\n
    Here is the user question: {question} \n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["question", "document"],
)

retrieval_grader = prompt1 | llm1 | JsonOutputParser()
#question = "agent memory"
#docs = retriever.invoke(question)
#doc_txt = docs[1].page_content
#print(retrieval_grader.invoke({"question": question, "document": doc_txt}))


### Generate

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# Prompt
prompt2 = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. 
    Use seven sentences maximum and keep the answer concise <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question: {question} 
    Context: {context} 
    Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question", "document"],
)

llm2 = ChatOllama(model=local_llm, temperature=0)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
rag_chain = prompt2 | llm2 | StrOutputParser()

# Run
# question = "agent memory"
# docs = retriever.invoke(question)
# generation = rag_chain.invoke({"context": docs, "question": question})
# print(generation)


### Hallucination Grader

# LLM
llm3 = ChatOllama(model=local_llm, format="json", temperature=0)

# Prompt
prompt3 = PromptTemplate(
    template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether 
    an answer is grounded in / supported by a set of facts. Give a binary 'yes' or 'no' score to indicate 
    whether the answer is grounded in / supported by a set of facts.\n you must provide the binary score as a JSON with a 
    single key 'score' and no preamble or explanation!. <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here are the facts:
    \n ------- \n
    {documents} 
    \n ------- \n
    Here is the answer: {generation}  <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["generation", "documents"],
)

hallucination_grader = prompt3 | llm3 | JsonOutputParser()
# generation =hallucination_grader.invoke({"documents": docs, "generation": generation})
# print(generation)

### Answer Grader

# LLM
llm4 = ChatOllama(model=local_llm, format="json", temperature=0)

# Prompt
prompt4 = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether an 
    answer is useful to resolve a question. Give a binary score 'yes' or 'no' to indicate whether the answer is 
    useful to resolve a question. Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
    <|eot_id|><|start_header_id|>user<|end_header_id|> Here is the answer:
    \n ------- \n
    {generation} 
    \n ------- \n
    Here is the question: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["generation", "question"],
)

answer_grader = prompt4 | llm4 | JsonOutputParser()
#answer_grader.invoke({"question": question, "generation": generation})



### Router

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import httpx


# LLM
llm5 = ChatOllama(model=local_llm, format="json", temperature=0)

prompt5 = PromptTemplate(
    template="""
    You are an expert at routing a user's or biologist's request to the appropriate API based on the input data. 
    Analyze the input and determine which API should handle the request. In fact to which model should be routed,
    Choose one of the following options:
    - "query" for general biology questions provided by the user or the biologist : if the input field is a simple question
    dedicated to the biology domain generate a JSON with a single key "question" and no preamble or explanation
    containing the question. For example :  "input" : "what is biology?", "api_endpoint" : "query" as json
    - "process_dna" for DNA sequences (input containing only the characters A, G, T, or C) extract the DNA sequence from
    the input by the user or the biologist and remove all exclamations and interrogations marks, it means you should extract a substring
     and assure  and generate a JSON with a single key  "sequence" and no preamble or explanation
    containg the DNA sequence. For example :  "input" : "AGTC", "api_endpoint" : "process_dna" as json
    - "esm" for protein sequences (typically longer sequences with 20 standard amino acid codes) extract the protein sequence 
    from the input by the user or the biologist and generate a JSON with a single key "sequence" and no preamble or explanation
    containing the protein sequence. For example : "input" : "GENGEIPLEIRATTGAEVDTRAVTAVEMTEGTLGIFRLPEEDYTALENFRYNRVAGENWKPASTVIYVGGTYARLCAYAPYNSVEFKNSSLKTEAGLTMQTYAAEKDMRFAVSGGDEVWKKTPTANFELKRAYARLVLSVVRDATYPNTCKITKAKIEAFTGNIITANTVDISTGTEGSGTQTPQYIHTVTTGLKDGFAIGLPQQTFSGGVVLTLTVDGMEYSVTIPANKLSTFVRGTKYIVSLAVKGGKLTLMSDKILIDKDWAEVQTGTGGSGDDYDTSFN", "api_endpoint" : "esm" as json
    Return the appropriate API endpoint in a JSON format with the key 'api_endpoint' containing the input of the API.

    Input: {input}
    assistant
    """,
    input_variables=["input"],
)

question_router = prompt5 | llm5 | JsonOutputParser()

llm6 = ChatOllama(model=local_llm, format="json", temperature=0)

prompt6 = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an expert at routing a 
    user question to a vectorstore or web search. Use the vectorstore for questions on biology and biotechnology. You do not need to be stringent with the keywords 
    in the question related to these topics. Otherwise, use web-search. Give a binary choice 'web_search' 
    or 'vectorstore' based on the question. Return the a JSON with a single key 'datasource' and 
    no premable or explanation. Question to route: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question"],
)

question_routerS = prompt6 | llm6 | JsonOutputParser()


async def handle_request(input_data: dict):
    print(input_data)
    routing_decision = question_router.invoke(input=input_data)
    print(routing_decision)
    api_endpoint = routing_decision["api_endpoint"]
    print(api_endpoint)
    data = routing_decision["input"]
    print(data)
    return routing_decision


### Search
os.environ["TAVILY_API_KEY"] = "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"

from langchain_community.tools.tavily_search import TavilySearchResults

web_search_tool = TavilySearchResults(k=3)


from typing_extensions import TypedDict
from typing import List
from langchain_core.documents import Document

### State


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
    """

    question: str
    generation: str
    web_search: str
    documents: List[str]


### Nodes


def retrieve(state):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}


def generate(state):
    """
    Generate answer using RAG on retrieved documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    web_search = "No"
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score["score"]
        # Document relevant
        if grade.lower() == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        # Document not relevant
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            # We do not include the document in filtered_docs
            # We set a flag to indicate that we want to run web search
            web_search = "Yes"
            continue
    return {"documents": filtered_docs, "question": question, "web_search": web_search}


def web_search(state):
    """
    Web search based based on the question

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Appended web results to documents
    """

    print("---WEB SEARCH---")
    question = state["question"]
    documents = state["documents"]

    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)
    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]
    return {"documents": documents, "question": question}


### Conditional edge


def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    print(question)
    source = question_routerS.invoke({"question": question})
    print(source)
    print(source["datasource"])
    if source["datasource"] == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "websearch"
    elif source["datasource"] == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"


def decide_to_generate(state):
    """
    Determines whether to generate an answer, or add web search

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    question = state["question"]
    web_search = state["web_search"]
    filtered_documents = state["documents"]

    if web_search == "Yes":
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
        )
        return "websearch"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"


### Conditional edge


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    #print(state)
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    print(score)
    if "score" in score:
        print(f"Score exists: {score['score']}")
    else:
        print("Score key does not exist.")
        score["score"] = "yes"
    grade = score["score"]
    print("---CHECK HALLUCINATIONS DONE---")
    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score["score"]
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


from langgraph.graph import END, StateGraph

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("websearch", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generatae



# Build graph
workflow.set_conditional_entry_point(
    route_question,
    {
        "websearch": "websearch",
        "vectorstore": "retrieve",
    },
)

workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "websearch": "websearch",
        "generate": "generate",
    },
)
workflow.add_edge("websearch", "generate")
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "websearch",
    },
)

app = workflow.compile()