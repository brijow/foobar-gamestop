import plotly.express as px


def financial_line_chart():
    df = px.data.stocks()

    fig = px.line(df, x="date", y=df.columns, hover_data={"date": "|%B %d, %Y"})

    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y", ticklabelmode="period")
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")

    fig.update_layout(
        yaxis={"visible": False, "showticklabels": False},
        xaxis={"title": ""},
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            x=0,
            y=1,
            traceorder="normal",
            font=dict(family="sans-serif", size=12, color="black"),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        rangeslider_visible=False,
        showticklabels=False,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        showline=False,
        spikecolor="grey",
        spikethickness=1,
        spikedash="solid",
    )
    # fig.update_yaxes(
    #     showspikes=True,
    #     spikedash="solid",
    #     spikemode="across",
    #     spikecolor="grey",
    #     spikesnap="cursor",
    #     spikethickness=1,
    # )
    fig.update_layout(spikedistance=1000, hoverdistance=1000)

    return fig
