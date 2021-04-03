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

    df = px.data.stocks()
    stock_tickers = [col for col in df.columns if col != "date"]
    for ticker in stock_tickers:
        fig.append_trace(
            go.Scatter(
                x=df.date,
                y=df[ticker],
                name=ticker,
            ),
            row=1,
            col=1,
        )

    fig.append_trace(go.Scatter(x=df.date, y=df.GOOG, showlegend=False), row=2, col=1)
    fig.append_trace(go.Scatter(x=df.date, y=df.AAPL, showlegend=False), row=3, col=1)
    fig.append_trace(go.Scatter(x=df.date, y=df.AMZN, showlegend=False), row=3, col=1)
    fig.append_trace(go.Scatter(x=df.date, y=df.FB, showlegend=False), row=4, col=1)
    fig.append_trace(go.Scatter(x=df.date, y=df.NFLX, showlegend=False), row=5, col=1)
    fig.append_trace(go.Scatter(x=df.date, y=df.MSFT, showlegend=False), row=6, col=1)

    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y", ticklabelmode="period")
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")

    fig.update_layout(
        xaxis={"title": ""},
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            x=0.89,
            y=1,
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
