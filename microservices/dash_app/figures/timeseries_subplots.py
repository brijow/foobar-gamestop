import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def ts_subplots():

    fig = make_subplots(
        rows=6,
        cols=1,
        row_heights=[0.5, 0.1, 0.1, 0.1, 0.1, 0.1],
        vertical_spacing=0.01,
        specs=[[{"b": 0.042}], [{}], [{}], [{}], [{}], [{}]],
    )

    import pandas as pd

    df = pd.read_csv("data/wide.csv")
    df = df.rename(
        columns={
            "hour": "DATE",
            "openprice": "OPEN",
            "highprice": "HIGH",
            "lowprice": "LOW",
            "closeprice": "CLOSE",
            "prediction": "PRED",
        }
    )
    df = df[df["PRED"].notna()]
    df = df[df["DATE"] > "2021-01-01"]

    series = [col for col in ["OPEN", "LOW", "HIGH", "CLOSE"]]
    # series = [col for col in ["OPEN", "LOW", "HIGH", "CLOSE", "PRED"]]
    for s in series:
        fig.append_trace(
            go.Scatter(
                x=df.DATE,
                y=df[s],
                name=s,
            ),
            row=1,
            col=1,
        )

    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.avg_all_post_pos,
            name="STOCKS :)",
            showlegend=False,
            line=dict(color="#20BA7B"),
        ),
        row=2,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.avg_all_post_neg,
            name="STOCKS :(",
            showlegend=False,
            line=dict(color="#206FBA"),
        ),
        row=2,
        col=1,
    )
    # fig.append_trace(
    #     go.Scatter(
    #         x=df.date, y=df.avg_all_post_neu, name="avg_all_post_neu", showlegend=False
    #     ),
    #     row=2,
    #     col=1,
    # )

    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.avg_gme_post_pos,
            name="GME :)",
            showlegend=False,
            line=dict(color="#20BA7B"),
        ),
        row=3,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.avg_gme_post_neg,
            name="GME :(",
            showlegend=False,
            line=dict(color="#206FBA"),
        ),
        row=3,
        col=1,
    )
    # fig.append_trace(
    #     go.Scatter(
    #         x=df.date, y=df.avg_gme_post_neu, name="avg_gme_post_neu", showlegend=False
    #     ),
    #     row=3,
    #     col=1,
    # )

    fig.append_trace(
        go.Scatter(x=df.DATE, y=df.cnt_all_user, name="USERS", showlegend=False),
        row=4,
        col=1,
    )
    fig.append_trace(
        go.Scatter(x=df.DATE, y=df.cnt_all_post, name="POSTS", showlegend=False),
        row=4,
        col=1,
    )
    fig.append_trace(
        go.Scatter(x=df.DATE, y=df.cnt_all_comments, name="CMNTS", showlegend=False),
        row=4,
        col=1,
    )

    fig.append_trace(
        go.Scatter(x=df.DATE, y=df.cnt_gme_user, name="GME USRS", showlegend=False),
        row=5,
        col=1,
    )
    fig.append_trace(
        go.Scatter(x=df.DATE, y=df.cnt_gme_post, name="GME POSTS", showlegend=False),
        row=5,
        col=1,
    )
    fig.append_trace(
        go.Scatter(x=df.DATE, y=df.cnt_gme_comments, name="GME CMTS", showlegend=False),
        row=5,
        col=1,
    )

    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.cnt_gme_tag,
            name="GME TAGS",
            showlegend=False,
            line=dict(color="#D29400"),
        ),
        row=6,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.cnt_all_tag,
            name="TICKERS",
            showlegend=False,
            line=dict(color="#D24400"),
        ),
        row=6,
        col=1,
    )

    # fig.append_trace(
    #     go.Scatter(x=df.DATE, y=df.volume, name="VOLUME", showlegend=False),
    #     row=6,
    #     col=1,
    # )

    # fig.update_xaxes(dtick="M1", tickformat="%b\n%Y", ticklabelmode="period")
    fig.update_xaxes(
        dtick="24*60*60*1000", tickformat="%e\n%b\n%Y", ticklabelmode="period"
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")

    fig.update_layout(
        xaxis={"title": ""},
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            x=0.89,
            y=0.8,
            traceorder="normal",
            font=dict(family="sans-serif", size=12, color="black"),
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        zeroline=False,
        rangeslider_visible=False,
        # showticklabels=False,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        showline=False,
        spikecolor="grey",
        spikethickness=1,
        spikedash="solid",
    )

    fig.update_layout(spikedistance=1000, hoverdistance=1000)
    fig.update_traces(xaxis="x1")
    fig.update_yaxes(ticklabelposition="inside")

    return fig
