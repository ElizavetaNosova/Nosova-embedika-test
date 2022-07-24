from .generate import generate

from dash import Dash, dcc, html, Input, Output, State

app = Dash(__name__)

PERSON_PLACEHOLDER = "Персона"
ORGANIZATION_PLACEHOLDER = "Организация"
BUTTON_TEXT = "Сгенерировать"
INSTRUCTION_TEXT = f'Укажите персону (рекомендуем указывать не только фамилию, но и имя или инициалы) или организацию и нажмите на кнопку "{BUTTON_TEXT}"'


app.layout = html.Div(
    [
        html.Div(dcc.Input(id="person", type="text", placeholder=PERSON_PLACEHOLDER)),
        html.Div(
            dcc.Input(
                id="organization", type="text", placeholder=ORGANIZATION_PLACEHOLDER
            )
        ),
        html.Button("Сгенерировать", id="submit-val", n_clicks=0),
        html.Div(id="container-button-basic", children=INSTRUCTION_TEXT),
        html.Div(id="title", style={"font-weight": "bold"}),
        html.Div(id="text"),
    ]
)


@app.callback(
    Output("title", "children"),
    Output("text", "children"),
    Input("submit-val", "n_clicks"),
    State("person", "value"),
    State("organization", "value"),
)
def update_output(n_clicks, person, organization):
    if n_clicks == 0:
        return "", ""
    person = person if person else ""
    organization = organization if organization else ""
    title, text = generate(person, organization)
    return title, text
