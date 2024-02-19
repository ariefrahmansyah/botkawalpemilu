import plotly.graph_objects as go


def draw_bar_chart(
    bar_chart_data, last_cached, total_processed_tps, total_tps, total_percentage_tps
):
    x_data = []
    y_data = []

    for data in bar_chart_data:
        x_data.append(data.paslon_votes)
        y_data.append(data.provinces)

    top_labels = ["Paslon 1", "Paslon 2", "Paslon 3"]

    colors = [
        "rgba(140, 185, 189, 1)",
        "rgba(199, 183, 163, 1)",
        "rgba(182, 115, 82, 1)",
    ]

    font_size = 10

    fig = go.Figure()

    for i in range(0, len(x_data[0])):
        yi = 0
        for xd, yd in zip(x_data, y_data):
            fig.add_trace(
                go.Bar(
                    x=[xd[i]],
                    y=[yd],
                    orientation="h",
                    marker=dict(
                        color=colors[i], line=dict(color="rgb(248, 248, 249)", width=1)
                    ),
                )
            )

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0.15, 1],
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode="stack",
        paper_bgcolor="rgb(248, 248, 255)",
        plot_bgcolor="rgb(248, 248, 255)",
        margin=dict(l=120, r=10, t=150, b=80),
        showlegend=False,
    )

    annotations = []

    for yd, xd in zip(y_data, x_data):
        # labeling the y-axis
        annotations.append(
            dict(
                xref="paper",
                yref="y",
                x=0.14,
                y=yd,
                xanchor="right",
                text=str(yd),
                font=dict(family="Arial", size=font_size, color="rgb(67, 67, 67)"),
                showarrow=False,
                align="right",
            )
        )
        # labeling the first percentage of each bar (x_axis)
        annotations.append(
            dict(
                xref="x",
                yref="y",
                x=xd[0] / 2,
                y=yd,
                text=str(xd[0]) + "%",
                font=dict(family="Arial", size=font_size, color="rgb(248, 248, 255)"),
                showarrow=False,
            )
        )
        # labeling the first Likert scale (on the top)
        if yd == y_data[-1]:
            annotations.append(
                dict(
                    xref="x",
                    yref="paper",
                    x=xd[0] / 2,
                    y=1.03,
                    text=top_labels[0],
                    font=dict(family="Arial", size=font_size, color="rgb(67, 67, 67)"),
                    showarrow=False,
                )
            )
        space = xd[0]
        for i in range(1, len(xd)):
            # labeling the rest of percentages for each bar (x_axis)
            annotations.append(
                dict(
                    xref="x",
                    yref="y",
                    x=space + (xd[i] / 2),
                    y=yd,
                    text=str(xd[i]) + "%",
                    font=dict(
                        family="Arial", size=font_size, color="rgb(248, 248, 255)"
                    ),
                    showarrow=False,
                )
            )
            # labeling the Likert scale
            if yd == y_data[-1]:
                annotations.append(
                    dict(
                        xref="x",
                        yref="paper",
                        x=space + (xd[i] / 2),
                        y=1.03,
                        text=top_labels[i],
                        font=dict(
                            family="Arial", size=font_size, color="rgb(67, 67, 67)"
                        ),
                        showarrow=False,
                    )
                )
            space += xd[i]

    fig.update_layout(
        annotations=annotations,
        title=go.layout.Title(
            text=f"""{len(y_data)} provinsi dengan sebaran suara Paslon 2 lebih dari 20%
<br><sup>Dari <a href="https://kawalpemilu.org">https://kawalpemilu.org</a> versi {last_cached}, progress: {total_processed_tps:,} dari {total_tps:,} TPS ({total_percentage_tps:.2f}%)</sup>""",
        ),
    )
    return fig
