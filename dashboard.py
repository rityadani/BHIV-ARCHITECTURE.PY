import dash
from dash import html, dcc, dash_table
import pandas as pd
import plotly.express as px
from main import run_cycle, BucketLogger

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
    trace, decision, result = run_cycle(
        logger,
        app_id=item["app_id"],
        proposed_action=item["proposed_action"],
        metrics=item["metrics"],
    )

# Prepare data for dashboard
entries = logger.entries
df = pd.DataFrame(entries)

# Flatten details for display
df['details'] = df['details'].apply(lambda x: str(x))

# Extract metrics for plotting
metrics_data = []
for cycle in cycles:
    metrics_data.append({
        'app_id': cycle['app_id'],
        'cpu_usage': cycle['metrics']['cpu_usage'],
        'memory_mb': cycle['metrics']['memory_mb'],
        'request_rate': cycle['metrics']['request_rate']
    })
metrics_df = pd.DataFrame(metrics_data)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('BHIV Architecture Dashboard'),
    html.H2('Bucket Log Entries'),
    dash_table.DataTable(
        id='log-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
    ),
    html.H2('Metrics Overview'),
    dcc.Graph(
        id='cpu-chart',
        figure=px.bar(metrics_df, x='app_id', y='cpu_usage', title='CPU Usage by App')
    ),
    dcc.Graph(
        id='memory-chart',
        figure=px.bar(metrics_df, x='app_id', y='memory_mb', title='Memory Usage by App (MB)')
    ),
    dcc.Graph(
        id='request-chart',
        figure=px.bar(metrics_df, x='app_id', y='request_rate', title='Request Rate by App')
    )
])

if __name__ == '__main__':
    app.run(debug=True)