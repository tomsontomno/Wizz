import os
from src.route_ranker import rate_my_options, task_progress
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
    original_start = request.form['original_start']
    radius_start = float(request.form['radius_start'])
    original_end = request.form['original_end']
    radius_end = float(request.form['radius_end'])
    tolerance = int(request.form['tolerance'])

    task_id = f"task_{int(time.time())}"

    with task_lock:
        task_progress[task_id] = [0.0, 1.0]  # [current_progress, total]

    thread = threading.Thread(target=rate_my_options_task,
                              args=(task_id, original_start, radius_start, original_end, radius_end, tolerance))
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
    with task_lock:
        progress, total = task_progress.get(task_id, (0.0, 1.0))
        percentage = (progress / total) * 100.0 if total > 0 else 100.0
        if percentage < 100.0:
            response = {'state': 'PROGRESS', 'progress': percentage}
        else:
            result = task_results.get(task_id)
            if result is None:
                response = {'state': 'ERROR', 'progress': 100.0,
                            'result': 'Task ID not found or task did not complete successfully'}
            else:
                response = {'state': 'SUCCESS', 'progress': 100.0, 'result': result}
    return jsonify(response)


def rate_my_options_task(task_id, original_start, radius_start, original_end, radius_end, tolerance):
    """
    Background task that performs the calculation.

    This function runs in a separate thread and executes the `rate_my_options` function. It updates the
    task's progress and stores the result or any errors encountered during execution.

    Args:
        task_id (str): The ID of the task.
        original_start (str): The original starting point.
        radius_start (float): The radius around the starting point.
        original_end (str): The original ending point.
        radius_end (float): The radius around the ending point.
        tolerance (int): The tolerance level for the calculation.
    """
    try:
        output = rate_my_options(original_start, radius_start, original_end, radius_end, tolerance, task_id)
        with task_lock:
            task_progress[task_id] = [1.0, 1.0]
            task_results[task_id] = output
    except Exception as e:
        with task_lock:
            task_progress[task_id] = [1.0, 1.0]
            task_results[task_id] = f"Error: {str(e)}"
        print(f"Error in task {task_id}: {e}")


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
    with task_lock:
        if task_id in task_progress:
            task_progress[task_id][1] = -3  # Mark as aborted (effectively stopping progress)
            task_results[task_id] = 'Calculation aborted by client'
    return jsonify({"status": "aborted"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8082))
    app.run(host="0.0.0.0", port=port)
