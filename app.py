import os
from route_ranker import rate_my_options, task_progress
from flask import Flask, request, render_template, jsonify
import threading
import time

app = Flask(__name__)

# Dictionary to store task results
task_results = {}
task_lock = threading.Lock()


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/start_calculation', methods=['POST'])
def start_calculation():
    original_start = request.form['original_start']
    radius_start = float(request.form['radius_start'])
    original_end = request.form['original_end']
    radius_end = float(request.form['radius_end'])
    tolerance = int(request.form['tolerance'])

    # Generate a unique task ID
    task_id = f"task_{int(time.time())}"

    # Initialize progress to 0% with thread lock
    with task_lock:
        task_progress[task_id] = 0.0

        # Start the calculation in a background thread
    thread = threading.Thread(target=rate_my_options_task,
                              args=(task_id, original_start, radius_start, original_end, radius_end, tolerance))
    thread.start()

    # Return the task id to track progress
    return jsonify({"task_id": task_id, "status": "Calculation started"})


@app.route('/get_progress/<task_id>')
def get_progress(task_id):
    with task_lock:
        progress = task_progress.get(task_id, 0.0)
        if progress < 100.0:
            response = {'state': 'PROGRESS', 'progress': progress}
        else:
            result = task_results.get(task_id)
            if result is None:
                response = {'state': 'ERROR', 'progress': 100.0,
                            'result': 'Task ID not found or task did not complete successfully'}
            else:
                response = {'state': 'SUCCESS', 'progress': 100.0, 'result': result}
    return jsonify(response)


def rate_my_options_task(task_id, original_start, radius_start, original_end, radius_end, tolerance):
    try:
        output = rate_my_options(original_start, radius_start, original_end, radius_end, tolerance, task_id)
        with task_lock:
            task_progress[task_id] = 100.0  # Mark as complete
            task_results[task_id] = output  # Store the result
    except Exception as e:
        output = "ERROR IN TASK_PROGRESS"
        with task_lock:
            task_progress[task_id] = 100.0
            task_results[task_id] = f"Error: {str(e)}"
        print(f"Error in task {task_id}: {e}")
    return output


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
