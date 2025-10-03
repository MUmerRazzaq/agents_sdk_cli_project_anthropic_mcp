from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.types import PromptMessage, TextContent
from mcp.server.fastmcp.prompts import base



mcp = FastMCP("DocumentMCP", log_level="ERROR", stateless_http=True)

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")

    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string."
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(
        description="The text to replace. Must match exactly, including whitespace."),
    new_str: str = Field(
        description="The new text to insert in place of the old text.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")

    if old_str not in docs[doc_id]:
        raise ValueError(f"Text '{old_str}' not found in document '{doc_id}'")

    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Successfully updated document {doc_id}"

# TODO: Write a resource to return all doc id's
@mcp.resource(uri="docs://documents", mime_type="application/json",
    name="list_documents",
    description="List all available document ids."
)
def list_documents():
    print("Listing documents")
    return list(docs.keys())

# TODO: Write a resource to return the contents of a particular doc
@mcp.resource(uri="docs://documents/{doc_id}",mime_type="application/json",
    name="get_document",
    description="Get the contents of a document by its ID."
)
def get_document(doc_id: str = Field(description="Id of the document to retrieve")):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")

    print(f"Getting document {doc_id}")
    return docs[doc_id]

# TODO: Write a prompt to summarize a doc
@mcp.prompt(
    name="summarize_doc",
    description="Summarize the contents of a document in markdown format."
)
def summarize_doc(doc_id: str = Field(description="Id of the document to summarize")):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")

    content = docs[doc_id]
    summary = f"# Summary of {doc_id}\n\n{content}...\n\n*This is a simulated summary.*"
    return summary

# TODO: Write a prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:
<document_id>
{doc_id}
</document_id>
You can retrieve the contents of the document by using the 'read_doc_contents' tool.
Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""
    
    return [
        base.UserMessage(prompt)
    ]


mcp_app = mcp.streamable_http_app()
