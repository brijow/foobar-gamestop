import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from foobar_gamestop.avocados.data_utils import load_avocado_data

df = load_avocado_data()
df = df.query("type == 'conventional' and region == 'Albany'")
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
df.sort_values("Date", inplace=True)

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(
            children="Avocado Analytics",
        ),
        html.P(
            children="Analyze the behavior of avocado prices"
            " and the number of avocados sold in the US"
            " between 2015 and 2018",
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": df["Date"],
                        "y": df["AveragePrice"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Average Price of Avocados"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": df["Date"],
                        "y": df["Total Volume"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Avocados Sold"},
            },
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
