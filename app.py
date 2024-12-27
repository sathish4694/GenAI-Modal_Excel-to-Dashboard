import pandas as pd
import plotly.express as px
import openai
import streamlit as st
from dotenv import load_dotenv
import os
import plotly.io as pio

# Load environment variables
load_dotenv()

# OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key
else:
    st.error("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

# Color options for different visualizations
color_scales = [
    'Viridis', 'Cividis', 'Inferno', 'Plasma', 'Magma', 'Jet', 'Rainbow', 'Blues', 'Greens', 'Reds', 'Purples'
]

def suggest_visualizations(sheet_data):
    """Use GPT to suggest visualizations based on the data."""
    prompt = f"""
    I have the following data from an uploaded file:
    {sheet_data.head().to_string(index=False)}
    Suggest some creative and effective visualizations for the data and why they are suitable.
    """
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error generating suggestions: {e}"

def generate_gantt_chart(df, start_col, end_col, task_col, color_scale):
    """Generate a Gantt chart from given data."""
    try:
        fig = px.timeline(df, x_start=start_col, x_end=end_col, y=task_col, color=task_col, color_continuous_scale=color_scale)
        fig.update_layout(title="Gantt Chart", xaxis_title="Timeline", yaxis_title="Tasks")
        return fig
    except Exception as e:
        st.error(f"Error generating Gantt Chart: {e}")
        return None

def generate_bar_chart(df, x_col, y_col, color_scale):
    """Generate a bar chart."""
    try:
        fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}", color=y_col, color_continuous_scale=color_scale)
        return fig
    except Exception as e:
        st.error(f"Error generating Bar Chart: {e}")
        return None

def generate_scatter_plot(df, x_col, y_col, color_col, color_scale):
    """Generate a scatter plot."""
    try:
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title="Scatter Plot", color_continuous_scale=color_scale)
        return fig
    except Exception as e:
        st.error(f"Error generating Scatter Plot: {e}")
        return None

def generate_line_chart(df, x_col, y_col, color_col, color_scale):
    """Generate a line chart."""
    try:
        fig = px.line(df, x=x_col, y=y_col, color=color_col, title="Line Chart", color_continuous_scale=color_scale)
        return fig
    except Exception as e:
        st.error(f"Error generating Line Chart: {e}")
        return None

def generate_heatmap(df, x_col, y_col, value_col, color_scale):
    """Generate a heatmap."""
    try:
        pivot_table = df.pivot_table(index=y_col, columns=x_col, values=value_col, aggfunc="sum").fillna(0)
        fig = px.imshow(pivot_table, title="Heatmap", labels={"color": value_col}, color_continuous_scale=color_scale)
        return fig
    except Exception as e:
        st.error(f"Error generating Heatmap: {e}")
        return None

def save_to_html(fig, filename="visualization.html"):
    """Save the figure to an HTML file."""
    try:
        fig.write_html(filename)
        st.success(f"Visualization saved as {filename}")
    except Exception as e:
        st.error(f"Error saving visualization: {e}")

# Streamlit App for Interaction
st.title("Generative AI Visualization Model")

# File upload handling
uploaded_file = st.file_uploader("Upload a file (Excel or CSV)", type=["xlsx", "csv"])
if uploaded_file:
    try:
        # Determine file type and read data
        if uploaded_file.name.endswith(".xlsx"):
            excel_data = pd.ExcelFile(uploaded_file)
            sheet_names = excel_data.sheet_names
            st.write("Sheets available:", sheet_names)
            selected_sheet = st.selectbox("Choose a sheet", sheet_names)
            sheet_data = excel_data.parse(selected_sheet)
        else:
            sheet_data = pd.read_csv(uploaded_file)

        st.write("Preview of the data:")
        st.dataframe(sheet_data.head())

        # AI Suggestion
        st.subheader("AI Suggestions for Visualization:")
        suggestions = suggest_visualizations(sheet_data)
        st.write(suggestions)

        # Visualization Selection
        st.subheader("Choose Visualization Type")
        viz_type = st.selectbox("Visualization Type", ["Gantt Chart", "Bar Chart", "Scatter Plot", "Line Chart", "Heatmap"])

        # Color selection
        color_scale = st.selectbox("Select Color Scheme", color_scales)

        if viz_type == "Gantt Chart":
            st.write("Generating Gantt Chart...")
            gantt_start_col = st.selectbox("Select Start Date Column", sheet_data.columns)
            gantt_end_col = st.selectbox("Select End Date Column", sheet_data.columns)
            gantt_task_col = st.selectbox("Select Task Column", sheet_data.columns)

            if gantt_start_col and gantt_end_col and gantt_task_col:
                gantt_fig = generate_gantt_chart(sheet_data, gantt_start_col, gantt_end_col, gantt_task_col, color_scale)
                if gantt_fig:
                    st.plotly_chart(gantt_fig)
                    save_to_html(gantt_fig, "gantt_chart.html")

        elif viz_type == "Bar Chart":
            st.write("Generating Bar Chart...")
            bar_x_col = st.selectbox("Select X-axis Column", sheet_data.columns)
            bar_y_col = st.selectbox("Select Y-axis Column", sheet_data.columns)

            if bar_x_col and bar_y_col:
                bar_fig = generate_bar_chart(sheet_data, bar_x_col, bar_y_col, color_scale)
                if bar_fig:
                    st.plotly_chart(bar_fig)
                    save_to_html(bar_fig, "bar_chart.html")

        elif viz_type == "Scatter Plot":
            st.write("Generating Scatter Plot...")
            scatter_x_col = st.selectbox("Select X-axis Column", sheet_data.columns)
            scatter_y_col = st.selectbox("Select Y-axis Column", sheet_data.columns)
            scatter_color_col = st.selectbox("Select Color Column (optional)", [None] + list(sheet_data.columns))

            scatter_fig = generate_scatter_plot(sheet_data, scatter_x_col, scatter_y_col, scatter_color_col, color_scale)
            if scatter_fig:
                st.plotly_chart(scatter_fig)
                save_to_html(scatter_fig, "scatter_plot.html")

        elif viz_type == "Line Chart":
            st.write("Generating Line Chart...")
            line_x_col = st.selectbox("Select X-axis Column", sheet_data.columns)
            line_y_col = st.selectbox("Select Y-axis Column", sheet_data.columns)
            line_color_col = st.selectbox("Select Color Column (optional)", [None] + list(sheet_data.columns))

            line_fig = generate_line_chart(sheet_data, line_x_col, line_y_col, line_color_col, color_scale)
            if line_fig:
                st.plotly_chart(line_fig)
                save_to_html(line_fig, "line_chart.html")

        elif viz_type == "Heatmap":
            st.write("Generating Heatmap...")
            heatmap_x_col = st.selectbox("Select X-axis Column", sheet_data.columns)
            heatmap_y_col = st.selectbox("Select Y-axis Column", sheet_data.columns)
            heatmap_value_col = st.selectbox("Select Value Column", sheet_data.columns)

            heatmap_fig = generate_heatmap(sheet_data, heatmap_x_col, heatmap_y_col, heatmap_value_col, color_scale)
            if heatmap_fig:
                st.plotly_chart(heatmap_fig)
                save_to_html(heatmap_fig, "heatmap.html")

    except Exception as e:
        st.error(f"Error processing file: {e}")
