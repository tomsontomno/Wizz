import os
from src.rating_routes import rate_all, get_progress_rating, abort, get_results
from flask import Flask, request, render_template, jsonify
import threading
import time

app = Flask(__name__)

task_results = {}
task_lock = threading.Lock()


@app.route('/', methods=['GET'])
def home():
    """
    Renders the home page of the application.

    This function handles GET requests to the root URL ('/').
    It returns the HTML content of the 'index.html' template.

    Returns:
        Response: The rendered HTML content of 'index.html'.
    """
    return render_template('index.html')


@app.route('/start_calculation', methods=['POST'])
def start_calculation():
    """
    Starts a background calculation task.

    This function handles POST requests to the '/start_calculation' URL. It retrieves the input parameters
    from the request, starts a new background thread to perform the calculation, and returns a JSON response
    with the task ID.

    Request Form Parameters:
        - original_start (str): The original starting point.
        - radius_start (float): The radius around the starting point.
        - original_end (str): The original ending point.
        - radius_end (float): The radius around the ending point.
        - tolerance (int): The tolerance level for the calculation.

    Returns:
        Response: A JSON object containing the task ID and status.
    """
    start = request.form['original_start']
    radius_start = float(request.form['radius_start'])
    end = request.form['original_end']
    radius_end = float(request.form['radius_end'])
    tolerance = int(request.form['tolerance'])

    task_id = f"task_{int(time.time())}"

    thread = threading.Thread(target=rate_all, args=(start, radius_start, end, radius_end, tolerance, task_id))
    thread.start()

    return jsonify({"task_id": task_id, "status": "Calculation started"})


@app.route('/get_progress/<task_id>')
def get_progress(task_id):
    """
    Retrieves the progress of a running task.

    This function handles GET requests to the '/get_progress/<task_id>' URL. It retrieves the progress of
    the specified task and returns a JSON response with the current progress percentage and status.

    Args:
        task_id (str): The ID of the task to check progress for.

    Returns:
        Response: A JSON object containing the state ('PROGRESS', 'SUCCESS', 'ERROR'), progress percentage, and result (if applicable).
    """

    percentage = get_progress_rating(task_id)
    if percentage <= 100.0:
        response = {'state': 'PROGRESS', 'progress': percentage}
    else:
        result = get_results(task_id)
        if result is None:
            response = {'state': 'ERROR', 'progress': 100.0,
                        'result': 'Task ID not found or task did not complete successfully'}
        else:
            response = {'state': 'SUCCESS', 'progress': 100.0, 'result': result}
    return jsonify(response)


@app.route('/abort_calculation', methods=['POST'])
def abort_calculation():
    """
    Aborts a running calculation task.

    This function handles POST requests to the '/abort_calculation' URL. It marks the specified task as aborted
    and attempts to stop any further progress.

    Request Form Parameters:
        - task_id (str): The ID of the task to be aborted.

    Returns:
        Response: A JSON object indicating the status of the abort operation.
    """
    task_id = request.form['task_id']
    abort(task_id)
    task_results[task_id] = 'Calculation aborted by client'
    return jsonify({"status": "aborted"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8082))
    app.run(host="0.0.0.0", port=port)
