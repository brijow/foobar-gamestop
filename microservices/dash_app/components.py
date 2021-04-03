import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from figures import financial_line_chart, reddit_network

GITLAB_URL = "https://csil-git1.cs.surrey.sfu.ca/733-foobar"
REPORT_URL = "https://docs.google.com/document/d/1oBRxH3crYQBCuFkInnlJV4NEOUaxuc4ZvqbTEapj6_4/edit#heading=h.liyhn4k5ur9v"


financial_lines_fig = financial_line_chart()
reddit_network_fig = reddit_network()


nav_bar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("GitLab", href=GITLAB_URL)),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Default view", href="/"),
                dbc.DropdownMenuItem("Detailed view", href="/detailed-view"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("More Info", header=True),
                dbc.DropdownMenuItem(
                    "Source code", href=GITLAB_URL, external_link=True
                ),
                dbc.DropdownMenuItem(
                    "Project report", href=REPORT_URL, external_link=True
                ),
            ],
        ),
    ],
    brand="Short Squeeze Reddit Sentiment Index",
    brand_href=GITLAB_URL,
    sticky="top",
)

top_row = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    figure=reddit_network_fig,
                                    style={"height": "332px"},
                                )
                            ],
                            style={"height": "340px", "border-style": "solid"},
                        ),
                        dbc.RadioItems(
                            options=[
                                {"label": "Option {}".format(i), "value": i}
                                for i in range(1, 4)
                            ],
                            value=0,
                            inline=True,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.Graph(
                                figure=financial_lines_fig, style={"height": "332px"}
                            )
                        ],
                        style={"height": "340px", "border-style": "solid"},
                    ),
                    md=8,
                ),
            ]
        ),
    ]
)

boxed_row = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    "This is a 100px div in a column in a row in col 2 in row 2",
                    style={"height": "100px", "width": "100%", "border-style": "solid"},
                ),
            ),
        ),
    ],
)

option_checklist = html.Div(
    [
        dbc.Checklist(
            options=[
                {"label": "Option {}".format(i), "value": i} for i in range(1, 11)
            ],
            value=[],
        ),
    ],
    style={"height": "100%", "border-style": "solid"},
)

body_rows = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    option_checklist,
                    md=4,
                ),
                dbc.Col(
                    [
                        boxed_row,
                        boxed_row,
                        boxed_row,
                        boxed_row,
                        boxed_row,
                        boxed_row,
                    ],
                    md=8,
                ),
            ],
        ),
    ]
)
