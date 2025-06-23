# helper/visualization_helper.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Any


class DataVisualizer:
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3

    def analyze_dataframe_for_viz(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataframe to suggest appropriate visualizations"""
        if df.empty:
            return {"error": "DataFrame is empty"}

        analysis = {
            "shape": df.shape,
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object', 'category']).columns.tolist(),
            "datetime_columns": df.select_dtypes(include=['datetime64']).columns.tolist(),
            "high_cardinality_cols": [],
            "low_cardinality_cols": []
        }

        # Analyze cardinality
        for col in analysis["categorical_columns"]:
            unique_count = df[col].nunique()
            if unique_count > 20:
                analysis["high_cardinality_cols"].append(col)
            else:
                analysis["low_cardinality_cols"].append(col)

        return analysis

    def create_summary_stats_viz(self, df: pd.DataFrame) -> go.Figure:
        """Create summary statistics visualization"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return None

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribution Overview', 'Correlation Matrix',
                            'Missing Values', 'Data Types'),
            specs=[[{"type": "bar"}, {"type": "heatmap"}],
                   [{"type": "bar"}, {"type": "table"}]]
        )

        # Distribution overview
        stats_df = df[numeric_cols].describe().T
        fig.add_trace(
            go.Bar(x=stats_df.index, y=stats_df['mean'], name='Mean'),
            row=1, col=1
        )

        # Correlation matrix (if more than 1 numeric column)
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig.add_trace(
                go.Heatmap(z=corr_matrix.values,
                           x=corr_matrix.columns,
                           y=corr_matrix.columns,
                           colorscale='RdBu',
                           showscale=False),
                row=1, col=2
            )

        # Missing values
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        if len(missing_data) > 0:
            fig.add_trace(
                go.Bar(x=missing_data.index, y=missing_data.values,
                       name='Missing Values'),
                row=2, col=1
            )

        fig.update_layout(height=600, showlegend=False,
                          title_text="Dataset Summary Statistics")
        return fig

    def create_distribution_plots(self, df: pd.DataFrame, column: str) -> go.Figure:
        """Create distribution plots for a specific column"""
        if column not in df.columns:
            return None

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(f'{column} - Histogram', f'{column} - Box Plot',
                            f'{column} - Value Counts', 'Summary Stats'),
            specs=[[{"type": "histogram"}, {"type": "box"}],
                   [{"type": "bar"}, {"type": "table"}]]
        )

        if df[column].dtype in ['int64', 'float64']:
            # Histogram
            fig.add_trace(
                go.Histogram(x=df[column], name='Distribution'),
                row=1, col=1
            )

            # Box plot
            fig.add_trace(
                go.Box(y=df[column], name='Box Plot'),
                row=1, col=2
            )

            # Summary stats table
            stats = df[column].describe()
            fig.add_trace(
                go.Table(
                    header=dict(values=['Statistic', 'Value']),
                    cells=dict(values=[stats.index, stats.values.round(2)])
                ),
                row=2, col=2
            )
        else:
            # Value counts for categorical
            value_counts = df[column].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=value_counts.index, y=value_counts.values),
                row=2, col=1
            )

        fig.update_layout(height=600, showlegend=False,
                          title_text=f"Distribution Analysis: {column}")
        return fig

    def create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create correlation heatmap for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) < 2:
            return None

        corr_matrix = df[numeric_cols].corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10}
        ))

        fig.update_layout(
            title="Correlation Matrix",
            xaxis_tickangle=-45,
            height=600
        )

        return fig

    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str,
                            color_col: str = None, size_col: str = None) -> go.Figure:
        """Create scatter plot with optional color and size dimensions"""
        fig = px.scatter(
            df, x=x_col, y=y_col,
            color=color_col, size=size_col,
            hover_data=df.columns[:5].tolist(),  # Include first 5 columns in hover
            title=f"{y_col} vs {x_col}"
        )

        fig.update_layout(height=500)
        return fig

    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str = None,
                         orientation: str = 'vertical') -> go.Figure:
        """Create bar chart"""
        if y_col is None:
            # Count plot
            value_counts = df[x_col].value_counts().head(20)
            fig = px.bar(
                x=value_counts.index, y=value_counts.values,
                title=f"Count of {x_col}",
                labels={'x': x_col, 'y': 'Count'}
            )
        else:
            # Aggregated bar chart
            agg_data = df.groupby(x_col)[y_col].mean().head(20)
            fig = px.bar(
                x=agg_data.index, y=agg_data.values,
                title=f"Average {y_col} by {x_col}",
                labels={'x': x_col, 'y': f'Average {y_col}'}
            )

        if orientation == 'horizontal':
            fig.update_layout(xaxis_title=fig.layout.yaxis.title.text,
                              yaxis_title=fig.layout.xaxis.title.text)
            fig.data[0].update(orientation='h')

        fig.update_layout(height=500)
        return fig

    def create_time_series_plot(self, df: pd.DataFrame, date_col: str,
                                value_col: str, group_col: str = None) -> go.Figure:
        """Create time series plot"""
        if group_col:
            fig = px.line(df, x=date_col, y=value_col, color=group_col,
                          title=f"{value_col} over Time by {group_col}")
        else:
            fig = px.line(df, x=date_col, y=value_col,
                          title=f"{value_col} over Time")

        fig.update_layout(height=500)
        return fig

    def suggest_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Suggest appropriate visualizations based on data structure"""
        analysis = self.analyze_dataframe_for_viz(df)
        suggestions = []

        if analysis.get("error"):
            return suggestions

        # Summary statistics
        if analysis["numeric_columns"]:
            suggestions.append({
                "type": "summary_stats",
                "title": "📊 Dataset Overview",
                "description": "Overall statistics and data quality assessment",
                "applicable": True
            })

        # Distribution plots for numeric columns
        for col in analysis["numeric_columns"][:5]:  # Limit to first 5
            suggestions.append({
                "type": "distribution",
                "title": f"📈 Distribution: {col}",
                "description": f"Histogram, box plot, and statistics for {col}",
                "column": col,
                "applicable": True
            })

        # Correlation matrix
        if len(analysis["numeric_columns"]) > 1:
            suggestions.append({
                "type": "correlation",
                "title": "🔗 Correlation Analysis",
                "description": "Correlation matrix for numeric variables",
                "applicable": True
            })

        # Bar charts for categorical columns
        for col in analysis["low_cardinality_cols"][:3]:  # Limit to first 3
            suggestions.append({
                "type": "bar_chart",
                "title": f"📊 Count: {col}",
                "description": f"Count distribution for {col}",
                "column": col,
                "applicable": True
            })

        # Scatter plots (if we have at least 2 numeric columns)
        if len(analysis["numeric_columns"]) >= 2:
            for i, x_col in enumerate(analysis["numeric_columns"][:2]):
                for y_col in analysis["numeric_columns"][i + 1:i + 3]:
                    suggestions.append({
                        "type": "scatter",
                        "title": f"🔍 {y_col} vs {x_col}",
                        "description": f"Scatter plot showing relationship",
                        "x_column": x_col,
                        "y_column": y_col,
                        "applicable": True
                    })

        return suggestions


def display_visualization_interface(df: pd.DataFrame, visualizer: DataVisualizer):
    """Display the visualization interface"""
    if df.empty:
        st.info("Execute a SELECT query to see visualization options")
        return

    st.subheader("📊 Data Visualization")

    # Get suggestions
    suggestions = visualizer.suggest_visualizations(df)

    if not suggestions:
        st.info("No visualizations available for this dataset")
        return

    # Create tabs for different visualization categories
    tab1, tab2, tab3 = st.tabs(["📈 Quick Insights", "🔧 Custom Charts", "💡 Suggestions"])

    with tab1:
        # Quick insights
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Dataset Overview"):
                fig = visualizer.create_summary_stats_viz(df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

        with col2:
            if st.button("🔗 Correlation Matrix"):
                fig = visualizer.create_correlation_heatmap(df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Custom chart builder
        st.subheader("Build Custom Chart")

        chart_type = st.selectbox("Chart Type",
                                  ["Bar Chart", "Scatter Plot", "Distribution Plot"])

        if chart_type == "Bar Chart":
            x_col = st.selectbox("X Column", df.columns)
            y_col = st.selectbox("Y Column (Optional)", [None] + list(df.columns))

            if st.button("Create Bar Chart"):
                fig = visualizer.create_bar_chart(df, x_col, y_col)
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Scatter Plot":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("X Column", numeric_cols)
                y_col = st.selectbox("Y Column", numeric_cols)
                color_col = st.selectbox("Color Column (Optional)",
                                         [None] + list(df.columns))

                if st.button("Create Scatter Plot"):
                    fig = visualizer.create_scatter_plot(df, x_col, y_col, color_col)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Need at least 2 numeric columns for scatter plot")

        elif chart_type == "Distribution Plot":
            column = st.selectbox("Column", df.columns)

            if st.button("Create Distribution Plot"):
                fig = visualizer.create_distribution_plots(df, column)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

    with tab3:
        # AI suggestions
        st.subheader("💡 Suggested Visualizations")

        for suggestion in suggestions[:6]:  # Limit to 6 suggestions
            with st.expander(suggestion["title"]):
                st.write(suggestion["description"])

                if suggestion["type"] == "summary_stats":
                    if st.button("Generate", key=f"gen_{suggestion['type']}"):
                        fig = visualizer.create_summary_stats_viz(df)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

                elif suggestion["type"] == "distribution":
                    if st.button("Generate", key=f"gen_{suggestion['type']}_{suggestion['column']}"):
                        fig = visualizer.create_distribution_plots(df, suggestion["column"])
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

                elif suggestion["type"] == "correlation":
                    if st.button("Generate", key=f"gen_{suggestion['type']}"):
                        fig = visualizer.create_correlation_heatmap(df)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

                elif suggestion["type"] == "bar_chart":
                    if st.button("Generate", key=f"gen_{suggestion['type']}_{suggestion['column']}"):
                        fig = visualizer.create_bar_chart(df, suggestion["column"])
                        st.plotly_chart(fig, use_container_width=True)

                elif suggestion["type"] == "scatter":
                    if st.button("Generate",
                                 key=f"gen_{suggestion['type']}_{suggestion['x_column']}_{suggestion['y_column']}"):
                        fig = visualizer.create_scatter_plot(df, suggestion["x_column"], suggestion["y_column"])
                        st.plotly_chart(fig, use_container_width=True)