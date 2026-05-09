from flask import Flask, render_template, request, jsonify, redirect, url_for
import json, os

app = Flask(__name__)
DATA_FILE = "data/projects.json"

def load_projects():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_projects(projects):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

@app.route("/")
def home():
    projects = load_projects()
    query = request.args.get("q", "").lower()
    if query:
        projects = [p for p in projects if query in p["nome"].lower()]
    return render_template("index.html", projects=projects, query=query)

@app.route("/project/<int:project_id>")
def project_detail(project_id):
    projects = load_projects()
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return redirect(url_for("home"))
    return render_template("project.html", project=project)

@app.route("/api/projects")
def projects_api():
    return jsonify(load_projects())

@app.route("/api/projects/<int:project_id>", methods=["POST"])
def update_project(project_id):
    projects = load_projects()
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return jsonify({"ok": False}), 404
    data = request.get_json()
    if "descricao" in data:
        project["descricao"] = data["descricao"]
    if "passos" in data:
        project["passos"] = data["passos"]
    if "checks" in data:
        project["checks"] = data["checks"]
    if "bandeira" in data:
        project["bandeira"] = data["bandeira"]
    if "pais" in data:
        project["pais"] = data["pais"]
    # status logic
    checks = project.get("checks", [])
    passos = project.get("passos", [])
    orig = project.get("status_original", project["status"])
    project["status_original"] = orig
    if orig == "avariado":
        if passos and len(checks) >= len(passos) and all(checks[:len(passos)]):
            project["status"] = "recuperado"
        else:
            project["status"] = "avariado"
    save_projects(projects)
    return jsonify({"ok": True, "status": project["status"]})

@app.route("/api/projects", methods=["POST"])
def add_project():
    projects = load_projects()
    data = request.get_json()
    new_id = max((p["id"] for p in projects), default=0) + 1
    proj = {
        "id": new_id,
        "nome": data.get("nome", "Novo Projeto"),
        "status": data.get("status", "intacto"),
        "status_original": data.get("status", "intacto"),
        "descricao": data.get("descricao", ""),
        "bandeira": data.get("bandeira", "https://flagcdn.com/w40/br.png"),
        "pais": data.get("pais", "Brasil"),
        "passos": data.get("passos", []),
        "checks": []
    }
    projects.append(proj)
    save_projects(projects)
    return jsonify({"ok": True, "id": new_id})

if __name__ == "__main__":
    app.run(debug=True)
