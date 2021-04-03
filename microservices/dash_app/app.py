import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from components import nav_bar, single_row_page

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div(
    [
        nav_bar,
        dbc.Container(
            [
                html.Br(),
                single_row_page,
                html.Br(),
                html.Div(style={"height": "200px"}),
            ]
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
