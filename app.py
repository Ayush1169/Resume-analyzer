from flask import Flask, render_template, request, jsonify, send_file
from main import analyze_resume, generate_feedback
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        files = request.files.getlist("resumes")
        role = request.form.get("role", "").strip().lower()
        results = []

        for file in files:
            if file.filename == "":
                continue
            filename = file.filename
            file.save(filename)
            found, score, missing, _ = analyze_resume(filename, role)
            results.append({
                "name": filename,
                "score": score,
                "skills": found,
                "missing": missing,
                "role": role or "general"   # ✅ never empty
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        return render_template("index.html", results=results)

    return render_template("index.html")


@app.route("/get-feedback", methods=["POST"])
def get_feedback():
    try:
        data = request.get_json()  # ✅ safer than request.json
        print("Received:", data)   # ✅ you'll see this in terminal

        found   = data.get("found", [])
        missing = data.get("missing", [])
        role    = data.get("role", "general")

        feedback = generate_feedback(found, missing, role)
        return jsonify({"feedback": feedback})

    except Exception as e:
        print("Route error:", e)
        return jsonify({"feedback": f"Server error: {str(e)}"}), 500
    
@app.route("/download")
def download_pdf():

    results = request.args.get("data")

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Resume Analysis Report", styles["Title"]))

    doc.build(content)

    return send_file("report.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)