import plotly.express as px
import plotly.graph_objects as go 

def get_boundaries(df):
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 2 * IQR
    upper_bound = Q3 + 2 * IQR
    return lower_bound, upper_bound

def plot_heatmap_of_laptimes(lap_times_df):
    lower_bound, upper_bound = get_boundaries(lap_times_df)
    fig = go.Figure(data=go.Heatmap(
        z=lap_times_df[(lap_times_df<upper_bound.median())&(lap_times_df>lower_bound.median())].values,
        x=lap_times_df.columns,
        y=lap_times_df.index,
        colorscale='hot'
        )
        )    
    return fig

def line_plot_of_laptimes(lap_times_df,top_10_finish_df):
    lower_bound, upper_bound = get_boundaries(lap_times_df)
    lap_times_df = lap_times_df[(lap_times_df<upper_bound.median())&(lap_times_df>lower_bound.median())]
    fig = px.line(data_frame=lap_times_df[top_10_finish_df["Driver"][:6]],
                  line_shape="spline",
                  labels={"value":"Times", "index":"Lap"}
                  )
    fig.update_layout(yaxis_range=[lower_bound[0], upper_bound[0]])
    return fig


def box_plot_laptimes(lap_times_df):
    lower_bound, upper_bound = get_boundaries(lap_times_df)
    fig = px.box(lap_times_df, y=lap_times_df.columns, 
                 labels={"value":"Lap Times", "variable":"Driver"})
    fig.update_layout(yaxis_range=[lower_bound[0], upper_bound[0]])
    return fig


def plot_team_performance(team_performance_df, team_colors):
    fig = px.bar(team_performance_df,
                x="Teams",
                y="Team Differences",
                
                labels={"Team Differences":"Gap"},
                color="Teams",
                color_discrete_map=team_colors
                )
    return fig

"""
def plot_heatmap_of_speed_traps(speed_trap_df):
    fig = go.Figure(data=go.Heatmap(
        z=speed_trap_df.max(15).values,
        x=speed_trap_df.columns,
        y=speed_trap_df.index,
        colorscale='hot'
        )
        )    
    return fig
"""

def plot_top10(top_10_finish_df, country):
    top_10_finish_df_sorted = top_10_finish_df.sort_values(by="Points", ascending=True)
    fig = px.bar(top_10_finish_df_sorted,
                y="Driver",
                x="Points",
                #color="Driver Colour",
                title=f"{country} GP Top 10", 
                orientation='h')
    return fig