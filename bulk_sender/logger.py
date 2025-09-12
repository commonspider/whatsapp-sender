from dash import callback, Output, Input, State, set_props
from dash.dcc import Store
from dash_mantine_components import Code

logger = Code(children="Logs:", id="log_container", block=True)
appender = Store(id="log_appender")


@callback(
    Output("log_container", "children"),
    Output("log_appender", "data", allow_duplicate=True),
    Input("log_appender", "data"),
    State("log_container", "children"),
    prevent_initial_call=True,
)
def append_log(new_line: str, log_history: str):
    return f"{log_history}\n> {new_line}", None


def log(message: str):
    set_props("log_appender", {"data": message})
