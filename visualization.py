import plotly.express as px
import plotly.graph_objects as go 
import matplotlib.pyplot as plt 
import seaborn as sns

def plot_heatmap_of_laptimes(lap_times_df):
    lower_bound = round(lap_times_df.min().min())-1
    upper_bound = round(lap_times_df.quantile().max())+3
    fig = go.Figure(data=go.Heatmap(
        z=lap_times_df[(lap_times_df<upper_bound)&(lap_times_df>lower_bound)].values,
        x=lap_times_df.columns,
        y=lap_times_df.index,
        colorscale='hot'))
    fig.update_layout(
        title='Heatmap of Lap Times')
    return fig

def line_plot_of_laptimes(lap_times_df,top_10_finish_df):
    lower_bound = round(lap_times_df.min().min())-1
    upper_bound = round(lap_times_df.quantile().max())+3
    fig = px.line(data_frame=lap_times_df[top_10_finish_df["Driver"].columns],
                  )
    fig.update_layout(yaxis_range=[lower_bound, upper_bound])
    return fig


def box_plot_laptimes(lap_times_df):
    lower_bound = round(lap_times_df.min().min())-1
    upper_bound = round(lap_times_df.quantile().max())+3
    fig = px.box(lap_times_df, y=lap_times_df.columns, title='Lap Times Box Plot', 
                 labels={"value":"Lap Times", "variable":"Driver"})
    fig.update_layout(yaxis_range=[lower_bound, upper_bound])
    return fig


def plot_team_performance(team_performance_df, team_colors):
    fig = px.bar(team_performance_df,
                x="Teams",
                y="Team Differences",
                title="Team Comparision",
                labels={"Team Differences":"Gap"},
                color="Teams",
                color_discrete_map=team_colors
                )
    return fig

def plot_top10(top_10_finish_df, country):
    fig = px.bar(top_10_finish_df,
                x="Driver",
                y="Points",
                #color="Driver Colour",
                title=f"{country} GP Top 10"
                )
    return fig