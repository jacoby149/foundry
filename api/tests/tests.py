from fastapi.testclient import TestClient
from main import app

def test_fork_project_endpoint():
    client = TestClient(app)
    resp = client.get("/test-fork-project")
    assert resp.status_code == 200, f"Status was: {resp.status_code} — {resp.text}"
    d = resp.json()
    print("Playground url:")
    print(d["playground_url"])
    print("\nOpen main.scad source:")
    print(d["main_scad"])
    print("-" * 40)
    print("Visit this URL in your browser to see the fork with its dependencies!")
    # Optionally, add stricter checks:
    assert d["playground_url"].startswith("https://ochafik.com/openscad2/#")
    assert "module fork()" in d["main_scad"]

if __name__ == "__main__":
    test_fork_project_endpoint()
