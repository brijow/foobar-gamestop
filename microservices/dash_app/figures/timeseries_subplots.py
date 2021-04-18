import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def ts_subplots():

    fig = make_subplots(
        rows=7,
        cols=1,
        row_heights=[0.4, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        vertical_spacing=0.01,
        specs=[[{"b": 0.042}], [{}], [{}], [{}], [{}], [{}], [{}]],
    )

    import pandas as pd

    df = pd.read_csv("wide1.csv")
    df = df.rename(
        columns={
            "hour": "DATE",
            "openprice": "OPEN",
            "highprice": "HIGH",
            "lowprice": "LOW",
            "closeprice": "CLOSE",
            "prediction_finn": "PRED_fin_feats",
            "prediction_wide": "PRED_all_feats",
            "prediction_reddit": "PRED_rdt_feats",
        }
    )
    df = df[df["PRED_fin_feats"].notna()]
    df = df[df["PRED_all_feats"].notna()]
    df = df[df["PRED_rdt_feats"].notna()]
    df = df[df["DATE"] > "2021-01-13"]

    ap_mean, ap_std = df["cnt_all_post"].mean(), df["cnt_all_post"].std()
    gm_mean, gm_std = df["cnt_gme_post"].mean(), df["cnt_gme_post"].std()

    df["cnt_all_post"] = (df["cnt_all_post"] - ap_mean) / ap_std
    df["cnt_gme_post"] = (df["cnt_gme_post"] - gm_mean) / gm_std

    ap_umean, ap_ustd = df["cnt_all_user"].mean(), df["cnt_all_user"].std()
    gm_umean, gm_ustd = df["cnt_gme_user"].mean(), df["cnt_gme_user"].std()
    df["cnt_all_user"] = (df["cnt_all_user"] - ap_umean) / ap_ustd
    df["cnt_gme_user"] = (df["cnt_gme_user"] - gm_umean) / gm_ustd

    series = [
        col for col in ["PRED_rdt_feats", "PRED_all_feats", "PRED_fin_feats", "CLOSE"]
    ]
    for s in series:
        fig.append_trace(
            go.Scatter(x=df.DATE, y=df[s], name=s,), row=1, col=1,
        )

    ###########################################################################
    # POSITIVE SENTIMENTS
    ###########################################################################
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.avg_all_post_pos,
            name="TOTAL",
            showlegend=False,
            line=dict(color="#206FBA"),
            opacity=0.7,
        ),
        row=2,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.avg_gme_post_pos,
            name="GAMESTOP",
            showlegend=False,
            line=dict(color="#20BA7B"),
            opacity=0.7,
        ),
        row=2,
        col=1,
    )
    ###########################################################################
    # NEGATIVE SENTIMENTS
    ###########################################################################
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.avg_all_post_neg,
            name="TOTAL",
            showlegend=False,
            line=dict(color="#206FBA"),
            opacity=0.7,
        ),
        row=3,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.avg_gme_post_neg,
            name="GAMESTOP",
            showlegend=False,
            line=dict(color="#20BA7B"),
            opacity=0.7,
        ),
        row=3,
        col=1,
    )
    ###########################################################################
    # POST COUNTS
    ###########################################################################
    fig.append_trace(
        go.Scatter(
            x=df.DATE, y=df.cnt_all_post, name="TOTAL", showlegend=False, opacity=0.7,
        ),
        row=4,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.cnt_gme_post,
            name="GAMESTOP",
            showlegend=False,
            opacity=0.7,
        ),
        row=4,
        col=1,
    )
    ###########################################################################
    # DISTINCT USER COUNTS
    ###########################################################################
    fig.append_trace(
        go.Scatter(
            x=df.DATE, y=df.cnt_all_user, name="TOTAL", showlegend=False, opacity=0.7,
        ),
        row=5,
        col=1,
    )
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.cnt_gme_user,
            name="GAMESTOP",
            showlegend=False,
            opacity=0.7,
        ),
        row=5,
        col=1,
    )
    ###########################################################################
    # TAG COUNTS
    ###########################################################################
    fig.append_trace(
        go.Scatter(
            x=df.DATE,
            y=df.cnt_all_tag,
            name="TICKER CNT",
            showlegend=False,
            line=dict(color="#D24400"),
            opacity=0.7,
        ),
        row=6,
        col=1,
    )
    ###########################################################################
    # VOLUME
    ###########################################################################
    fig.append_trace(
        go.Scatter(x=df.DATE, y=df.volume, name="VOLUME", showlegend=False),
        row=7,
        col=1,
    )

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
        annotations=[
            dict(
                text="POSITIVE",
                xref="paper",
                x=0.978,
                yref="paper",
                y=0.6,
                showarrow=False,
                font=dict(color="black", size=12),
            ),
            dict(
                text="NEGATIVE",
                xref="paper",
                x=0.982,
                yref="paper",
                y=0.49,
                showarrow=False,
                font=dict(color="black", size=12),
            ),
            dict(
                text="POSTS",
                xref="paper",
                x=0.965,
                yref="paper",
                y=0.38,
                showarrow=False,
                font=dict(color="black", size=12),
            ),
            dict(
                text="USERS",
                xref="paper",
                x=0.965,
                yref="paper",
                y=0.27,
                showarrow=False,
                font=dict(color="black", size=12),
            ),
            dict(
                text="TICKERS",
                xref="paper",
                x=0.975,
                yref="paper",
                y=0.16,
                showarrow=False,
                font=dict(color="black", size=12),
            ),
            dict(
                text="VOLUME",
                xref="paper",
                x=0.976,
                yref="paper",
                y=0.05,
                showarrow=False,
                font=dict(color="black", size=12),
            ),
        ],
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
