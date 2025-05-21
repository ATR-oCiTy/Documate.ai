import os
import threading
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Import the main changelog generation function
try:
    from main import main as generate_changelog_main
except ImportError:
    # Handle potential path issues if main.py is not directly in PYTHONPATH
    # This is a simple fallback; more robust solutions might be needed depending on structure
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from main import main as generate_changelog_main

# Import and initialize logger (optional, if direct logging in app.py is needed)
# from common.logging import get_logger
# logger = get_logger(__name__) # Example: logger.info("Flask app starting...")

# Simulate a dictionary to store job statuses and results
jobs = {}

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)  # Enable CORS for all routes

# --- Helper function to run changelog generation and update job status ---
def long_running_task(epic_key, job_id):
    current_job = jobs[job_id]
    current_job["status"] = "processing"
    current_job["logs"].append(f"Process started for Epic: {epic_key}...")
    
    try:
        current_job["logs"].append(f"Invoking changelog generation for Epic: {epic_key}...")
        # This call will block until the main logic completes or errors out
        confluence_url = generate_changelog_main(epic_key)
        
        current_job["logs"].append("Changelog generation successful.")
        
        if confluence_url:
            current_job["previewContent"] = f'<html><body><h2>Changelog Generated!</h2><p>View on Confluence: <a href="{confluence_url}" target="_blank">{confluence_url}</a></p></body></html>'
            current_job["logs"].append(f"Process completed successfully. Confluence page: {confluence_url}")
        else:
            # Handle case where main function might return None or empty string without raising an error
            current_job["previewContent"] = "<html><body><h2>Completed</h2><p>Changelog process finished, but no Confluence URL was returned.</p></body></html>"
            current_job["logs"].append("Process completed, but no Confluence URL was provided.")
            
        current_job["status"] = "completed"

    except Exception as e:
        # logger.error(f"Error in long_running_task for job {job_id}: {str(e)}", exc_info=True) # Example direct logging
        current_job["status"] = "error"
        current_job["logs"].append(f"Error during changelog generation: {str(e)}")
        current_job["previewContent"] = "<html><body><h2>Error</h2><p>Failed to generate changelog. Check activity logs for more details.</p></body></html>"
        # To provide more details in logs for the user:
        import traceback
        current_job["logs"].append(f"Traceback: {traceback.format_exc()}")


# --- API Endpoints ---
@app.route('/api/generate-changelog', methods=['POST'])
def generate_changelog_endpoint():
    data = request.get_json()
    epic_key = data.get('epicKey')

    if not epic_key:
        return jsonify({"error": "epicKey is required"}), 400

    job_id = str(uuid.uuid4())
    # Initialize job entry with a list for logs
    jobs[job_id] = {"status": "starting", "logs": ["Request received for Epic: " + epic_key], "previewContent": ""}
    
    thread = threading.Thread(target=long_running_task, args=(epic_key, job_id))
    thread.start()
    
    return jsonify({"jobId": job_id, "message": "Process started"}), 202

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status_endpoint(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Invalid job ID"}), 404
    return jsonify(job)

# --- Serve React App ---
# Ensure this is BELOW your API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Serve index.html for any path that doesn't match a static file
        # This is crucial for client-side routing in React
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Note: For production, use a Gunicorn or other WSGI server.
    # The React app should be built first (`cd frontend && npm run build`)
    # and its build output should be in `../frontend/build` relative to `app.py`.
    app.run(debug=True, port=5000, threaded=True) # `threaded=True` is good for dev with background tasks
