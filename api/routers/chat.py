from fastapi import APIRouter, HTTPException
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from models.models import (
    ChatRequest,
    RawChatResponse,
    EnrichedChatResponse,
    PlaygroundPreferences,
    SourceFile
)
import re

router = APIRouter(prefix="/chat")

def flatten_sources(sources):
    """
    Moves all files to the top level, e.g. /utils/foo.scad => /foo.scad
    Updates include/use statements accordingly in file contents.
    """
    # Map old path to new top-level path
    path_map = {}
    for file in sources:
        basename = "/" + file.path.split("/")[-1]
        path_map[file.path] = basename

    # Now update includes/uses inside each file's content
    updated_sources = []
    for file in sources:
        content = file.content
        for orig, flat in path_map.items():
            if orig != flat:
                # Replace include/use statements addressing utils/ (with/without leading slash)
                orig_clean = orig.lstrip("/")
                flat_clean = flat.lstrip("/")
                # Regex targets both include and use with angle brackets, with or without /
                content = re.sub(
                    rf'(?<=\b(?:include|use)\s*<)(/?{re.escape(orig_clean)})(?=>)',
                    flat_clean,
                    content
                )
        # Set new top-level path
        updated_sources.append(SourceFile(
            path="/" + file.path.split("/")[-1],
            content=content
        ))
    return updated_sources

@router.post("/ask_for_object", response_model=EnrichedChatResponse)
async def chat_scad_endpoint(req: ChatRequest):
    parser = PydanticOutputParser(pydantic_object=RawChatResponse)

    prompt = PromptTemplate(
        template=(
            "You are an expert OpenSCAD assistant.\n"
            "Strictly reply ONLY in a JSON matching this schema (no commentary, no explanations):\n"
            "{format_instructions}\n"
            "\n"
            "For EACH user request:\n"
            "- Organize the project with MULTIPLE OpenSCAD files, in modular style.\n"
            "- IMPORTANT: Put ALL files at the project ROOT (e.g. /main.scad, /helpers.scad). NEVER use subfolders or utils/ or directories.\n"
            "- In all 'include <...>;' or 'use <...>;' statements, reference only top-level files, matching the given source file 'path'.\n"
            "- Never output ../, /utils/, or subdirectory paths.\n"
            "- The main logic is in /main.scad and demonstrates how to use helpers.\n"
            "- Always use at least two files unless impossible.\n"
            "- At the end of /main.scad, ensure any test/demo code or preview is included; for simplicity, just call the main module directly (e.g., 'my_object();').\n"
            "- The response MUST be VALID JSON matching the schema. No comments or extra output.\n"
            "- Summarize your design and file structure in 'reply_text'.\n"
            "\n"
            "EXAMPLE USER REQUEST: make a simple cube\n"
            "EXAMPLE RESPONSE:\n"
            "{{\n"
            "  \"sources\": [\n"
            "    {{\"path\": \"/main.scad\", \"content\": \"include <common.scad>\\nmy_cube();\\n\"}},\n"
            "    {{\"path\": \"/common.scad\", \"content\": \"module my_cube() {{ cube([10,10,10]); }}\"}}\n"
            "  ],\n"
            "  \"active_path\": \"/main.scad\",\n"
            "  \"reply_text\": \"This divides the simple cube project into a main file and a helper module at the root.\""
            "}}\n"
            "\n"
            "USER REQUEST:\n"
            "{input}\n"
        ),
        input_variables=["input"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm = ChatOpenAI(model="gpt-4.1")
    chain = prompt | llm | parser

    try:
        # 1. LLM raw response as model
        raw: RawChatResponse = await chain.ainvoke({"input": req.request_text})

        # 2. Ensure safety: flatten all sources to root and fix includes
        raw.sources = flatten_sources(raw.sources)
        raw.active_path = "/" + raw.active_path.split("/")[-1] # flatten active path to root

        # 3. Use model for playground URL
        playground_prefs = PlaygroundPreferences(
            sources=raw.sources,
            active_path=raw.active_path
        )
        url = playground_prefs.playground_url()
        return EnrichedChatResponse(chat_response=raw, encoded_url=url)
    except Exception as e:
        print(f"Error during LLM chain execution: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to produce/validate EnrichedChatResponse: {str(e)}"
        )
