import plotly.express as px
import plotly.graph_objects as go 
import matplotlib.pyplot as plt 
import seaborn as sns

def plot_heatmap_of_laptimes(lap_times_df):
    fig = go.Figure(data=go.Heatmap(
        z=lap_times_df[(lap_times_df<125)&(lap_times_df>105)].values,
        x=lap_times_df.columns,
        y=lap_times_df.index,
        colorscale='hot'))
    fig.update_layout(
        title='Heatmap of Lap Times')
    fig.show()
    return fig

def line_plot_of_laptimes(lap_times_df):
    fig = px.line(data_frame=lap_times_df, line_shape='spline', title="Belgian GP Lap Times",
              #color_discrete_map=drivers.items(),
              labels={"value":"Lap Times", "index":"Laps"})
    fig.update_layout(yaxis_range=[105,125])
    fig.show()
    return fig


def box_plot_laptimes(lap_times_df):
    fig = px.box(lap_times_df, y=lap_times_df.columns, title='Lap Times Box Plot')
    fig.update_layout(yaxis_range=[105,125])
    fig.show()
    return fig