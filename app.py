from flask import Flask, render_template
from main import run_cycle, BucketLogger

app = Flask(__name__)

@app.route('/')
def index():
    # Simulate some data
    logger = BucketLogger()
    cycles = [
        {
            "app_id": "payment-service",
            "proposed_action": "scale down",
            "metrics": {"cpu_usage": 72, "memory_mb": 420, "request_rate": 180},
        },
        {
            "app_id": "analytics-engine",
            "proposed_action": "shutdown",
            "metrics": {"cpu_usage": 22, "memory_mb": 180, "request_rate": 12},
        },
        {
            "app_id": "web-server",
            "proposed_action": "restart",
            "metrics": {"cpu_usage": 85, "memory_mb": 500, "request_rate": 250},
        },
    ]

    for item in cycles:
        run_cycle(
            logger,
            app_id=item["app_id"],
            proposed_action=item["proposed_action"],
            metrics=item["metrics"],
        )

    # Prepare data for dashboard
    entries = logger.entries
    
    # Extract metrics for plotting
    metrics_data = []
    for cycle in cycles:
        metrics_data.append({
            'app_id': cycle['app_id'],
            'cpu_usage': cycle['metrics']['cpu_usage'],
            'memory_mb': cycle['metrics']['memory_mb'],
            'request_rate': cycle['metrics']['request_rate']
        })

    return render_template('index.html', entries=entries, metrics=metrics_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
