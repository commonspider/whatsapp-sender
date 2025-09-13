import base64
import time
from io import StringIO, BytesIO
from typing import Callable, Sequence, Text

import PIL.Image
import pandas
from dash import callback, Output, Input, State
from dash.dcc import Upload, Store
from dash.exceptions import PreventUpdate
from dash_mantine_components import Button, TextInput, Textarea, Card, Image
from pandas import DataFrame

from .logger import log
from .threaded_manager import ThreadedManager
from .wautils import login_qr, post_login, login_code, send_message_old, open_wa

manager = ThreadedManager()
steps: list[Callable[[], tuple[str, list]]] = []


def step(f):
    steps.append(f)
    return f


# Whatsapp Login
@step
def step_login():
    return (
        "Whatsapp Login",
        [
            Button("Login con QR", id="button_login_qr"),
            "Clicca qui per mostrare il qr",
            Image(id="image_qr"), "e scannerizza con l'app",
            Button("Login con codice", id="button_login_code"),
            "Compila i campi sotto, poi clicca qui per mostrate il codice da inserire nell'app. ",
            TextInput(id="input_code", disabled=True), "Codice",
            TextInput("Italia", id="input_country", persistence=True, persistence_type="local"), "Stato di appartenenza (usato per il prefisso)",
            TextInput(id="input_phone", persistence=True, persistence_type="local"), "Numero di telefono",
            Store(id="store_logging_in")
        ]
    )


@callback(
    Output("image_qr", "src", allow_duplicate=True),
    Output("store_logging_in", "data", allow_duplicate=True),
    Input("button_login_qr", "n_clicks"),
    prevent_initial_call=True,
    running=[
        (Output("button_login_qr", "disabled"), True, False),
        (Output("button_login_code", "disabled"), True, False),
    ],
)
def callback_login_qr(_):
    data = login_qr()
    if data is not None:
        image = PIL.Image.open(BytesIO(data))
        old_size = image.size
        new_size = (old_size[0] + 30, old_size[1] + 30)
        image_with_border = PIL.Image.new("RGB", new_size)
        image_with_border.paste((255, 255, 255), (0, 0, new_size[0], new_size[1]))
        box = tuple((n - o) // 2 for n, o in zip(new_size, old_size))
        image_with_border.paste(image, box)
    else:
        image_with_border = None
    return image_with_border, True


@callback(
    Output("input_code", "value", allow_duplicate=True),
    Output("store_logging_in", "data", allow_duplicate=True),
    Input("button_login_code", "n_clicks"),
    State("input_country", "value"),
    State("input_phone", "value"),
    prevent_initial_call=True,
    running=[
        (Output("button_login_qr", "disabled"), True, False),
        (Output("button_login_code", "disabled"), True, False),
    ],
)
def callback_login_code(_, country: str, phone: str):
    code = login_code(country, phone)
    return code, True


@callback(
    Output("log_appender", "data", allow_duplicate=True),
    Output("image_qr", "src", allow_duplicate=True),
    Output("input_code", "value", allow_duplicate=True),
    Output("store_logging_in", "data", allow_duplicate=True),
    Input("store_logging_in", "data"),
    prevent_initial_call=True
)
def callback_logging_in(status):
    if status:
        post_login()
        return "Logged in", "", "", False
    else:
        raise PreventUpdate


# Load Contacts
@step
def step_load_contacts():
    return (
        "Carica i contatti dal file",
        [
            Upload(
                id="upload_contacts",
                children=Card([
                    Text("Drag and Drop oppure"),
                    Button("Seleziona il file")
                ]),
            ),
            "Estensioni supportate: csv"
        ]
    )


@callback(
    Output("table_contacts", "data", allow_duplicate=True),
    Input("upload_contacts", "contents"),
    prevent_initial_call=True,
)
def callback_load_contacts(content: str):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string).decode()
    df = pandas.read_csv(StringIO(decoded), sep=",")
    head, rows = get_contacts_table(df)
    log("Contatti caricati")
    return {"head": head, "body": rows}


# Select contacts
@step
def step_select_contacts():
    return (
        "Seleziona i contatti",
        [
            TextInput(id="input_contacts_selection"),
            "Scrivi il numero delle righe dei contatti che vuoi selezionare. "
            "Dev'essere una sequenza di numeri o coppie di numeri separati da una virgola. "
            "(Esempio: 1,4-7,9 seleziona i contatti 1, 4, 5, 6, 7, 9)",
            TextInput(id="input_col_name", persistence=True, persistence_type="local"),
            "Nome della colonna con i nomi.",
            TextInput(id="input_col_phone", persistence=True, persistence_type="local"),
            "Nome della colonna con i numeri di telefono.",
            Button("Seleziona", id="button_contacts_select"),
        ]
    )


@callback(
    Output("table_selected", "data", allow_duplicate=True),
    Input("button_contacts_select", "n_clicks"),
    State("input_contacts_selection", "value"),
    State("input_col_name", "value"),
    State("input_col_phone", "value"),
    State("table_contacts", "data"),
    prevent_initial_call=True
)
def callback_select_contacts(_, selection: str, name_col: str, phone_col: str, contacts: dict):
    if selection is None:
        raise PreventUpdate
    rows = []
    for item in selection.split(","):
        parts = item.split("-")
        if len(parts) == 1:
            rows.append(int(parts[0]))
        elif len(parts) == 2:
            rows.extend(range(int(parts[0]), int(parts[1]) + 1))
        else:
            log("Selezione invalida")
            return {"caption": "Selezione invalida"}
    try:
        name_i = contacts["head"].index(name_col)
        phone_i = contacts["head"].index(phone_col)
    except ValueError as exc:
        name = exc.args[0].split("'")[1]
        log(f"Colonna {name} non trovata")
        return {"caption": f"Colonna {name} non trovata"}
    body = []
    for row in contacts["body"]:
        if int(row[0]) not in rows:
            continue
        name = capitalize(row[name_i])
        phone = parse_number(row[phone_i])
        body.append((row[0], name, phone))
    log("Contatti selezionati")
    return {"head": ["NUM", "Nome", "Telefono"], "body": body}


# Send Messages
@step
def step_send_messages():
    return (
        "Invia i messaggi",
        [
            Textarea(id="textarea_skeleton", persistence=True, persistence_type="local"),
            "Scrivi il tuo message. Puoi il usare il nome delle colonne tra parentesi graffe come placeholder. "
            "(Esempio: Ciao {Nome}! Come stai?)",
            TextInput("20", id="input_delay", persistence=True, persistence_type="local"),
            "Tempo di attesa tra un messaggio e l'altro",
            Button("INVIA!", id="button_send_messages"),
            "Invia tutto e ciaone!",
        ]
    )


@callback(
    Output("log_appender", "data", allow_duplicate=True),
    Input("button_send_messages", "n_clicks"),
    State("textarea_skeleton", "value"),
    State("table_selected", "data"),
    State("input_delay", "value"),
    background=True,
    manager=manager,
    prevent_initial_call=True,
    running=[
        (Output("button_send_messages", "disabled"), True, False),
    ],
)
def callback_send_messages(_, skeleton: str, selected: dict, delay: str):
    delay = float(delay)
    try:
        cols: list = selected["head"]
    except KeyError:
        return "Prima seleziona i tuoi contatti!"
    name_index = cols.index("Nome")
    phone_index = cols.index("Telefono")
    open_wa()
    for row in selected["body"]:
        name = row[name_index]
        phone = row[phone_index]
        if phone is None:
            log(f"ATTENZIONE! {name} non ha un numero di cellulare")
        else:
            text = skeleton.format(**dict(zip(cols, row)))
            if send_message_old(phone, text):
                log(f"Messaggio inviato a {name} ({phone})")
            else:
                log(f"ATTENZIONE! {name} ({phone}) non ha whatsapp!")
        time.sleep(delay)
    return "Finito!"


# Utils


def get_contacts_table(df: DataFrame) -> tuple[Sequence, Sequence]:
    return (
        ("NUM", *df.columns),
        [
            (str(int(i) + 2), *row)
            for i, row in df.iterrows()
        ]
    )


def capitalize(string: str | None):
    if isinstance(string, str):
        return " ".join([part.capitalize() for part in string.split()])
    else:
        return None


def parse_number(obj):
    if isinstance(obj, (str, int)):
        return str(obj)
    else:
        return None
