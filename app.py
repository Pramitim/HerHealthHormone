from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from groq import Groq
import os
from dotenv import load_dotenv

# Import AI + calender logic
from llama_service import generate_schedule, create_ics

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load .env values
    load_dotenv()

    # Initialize Groq client using environment variable
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))


    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/planner")
    def planner():
        return render_template("planner.html")

    # Send data + download ICS
    @app.route("/submit_data", methods=["POST"])
    def submit_data():
        data = request.json

        # Generate schedule using AI
        schedule = generate_schedule(data)

        # Convert schedule into ICS
        ics_text = create_ics(schedule)

        # File path (temporary)
        filename = f"{data.get('name', 'user')}_schedule.ics"
        filepath = os.path.join("/tmp", filename)

        # Save ICS to temporary directory
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(ics_text)

        # Send ICS file as download
        return send_file(
            filepath,
            mimetype="text/calendar",
            as_attachment=True,
            download_name=filename
        )


    # AI blueprint
    from routes.ai import ai_bp
    app.register_blueprint(ai_bp, url_prefix="/ai")


    return app


# This is only used when running locally with: python app.py
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)

