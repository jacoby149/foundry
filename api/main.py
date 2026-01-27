from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.openscad_playground import router as openscad_playground_router
from routers.openscad_render import router as openscad_render_router
from routers.chat import router as chat_router # Correct import for your project
from routers.sim_stream_router import router as sim_stream_router
from routers.stream_test_router import router as stream_router
app = FastAPI(
    title="AI Object Foundry",
    description="""
<div style='margin: 1em 0'>
    <strong>LLM that thinks like an engineer</strong><br>
    <a href="/" style="font-size:1em;">&larr; Go Back Home</a>
</div>
""",
)
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(openscad_playground_router)
app.include_router(openscad_render_router)
app.include_router(chat_router)
app.include_router(sim_stream_router)
app.include_router(stream_router)


@app.get("/", response_class=HTMLResponse)
def root():
    with open("linktree.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

# This is correct for the Dockerfile above:
app.mount(
    "/ui",
    StaticFiles(directory="/static/ui", html=True),
    name="parts-maker-chat"
)
