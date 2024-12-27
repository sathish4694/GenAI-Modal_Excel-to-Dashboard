import os
import pandas as pd
import plotly.express as px
import openai
import streamlit as st
from dotenv import load_dotenv
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
    """Use GPT to suggest visualizations based on the data with improved prompt."""
    
    # Create a prompt that is more specific and focuses on the type of data
    prompt = f"""
    I have the following data from an uploaded file:
    {sheet_data.head().to_string(index=False)}

    The dataset consists of columns with different types of data, such as numeric, categorical, and date values. 
    Please suggest creative, insightful, and effective visualizations based on this data. Here are the types of insights I am looking for:

    1. What patterns or trends can be identified?
    2. What comparisons can be drawn between different categories or values?
    3. How can time-based trends be visualized, if applicable?
    4. What relationships between variables can be highlighted through a chart?

    Provide the names of suitable visualizations and why they are a good fit for the data.
    If possible, suggest both common visualizations (e.g., bar charts, line graphs) and more creative alternatives (e.g., heatmaps, radar charts, etc.).
    """
    
    try:
        # Call OpenAI's model with the updated prompt
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=300
        )
        
        # Return the response
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
        fig.update_layout(title=f"{y_col} vs {x_col}", xaxis_title=x_col, yaxis_title=y_col)
        return fig
    except Exception as e:
        st.error(f"Error generating Bar Chart: {e}")
        return None

def generate_scatter_plot(df, x_col, y_col, color_col, color_scale):
    """Generate a scatter plot."""
    try:
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title="Scatter Plot", color_continuous_scale=color_scale)
        fig.update_layout(title="Scatter Plot", xaxis_title=x_col, yaxis_title=y_col)
        return fig
    except Exception as e:
        st.error(f"Error generating Scatter Plot: {e}")
        return None

def generate_line_chart(df, x_col, y_col, color_col, color_scale):
    """Generate a line chart."""
    try:
        if color_col:
            # Color for continuous scale (e.g., numeric data)
            fig = px.line(df, x=x_col, y=y_col, color=color_col, title="Line Chart", color_continuous_scale=color_scale)
        else:
            # Default line color without color column
            fig = px.line(df, x=x_col, y=y_col, title="Line Chart")
        
        fig.update_layout(title="Line Chart", xaxis_title=x_col, yaxis_title=y_col)
        return fig
    except Exception as e:
        st.error(f"Error generating Line Chart: {e}")
        return None

def generate_heatmap(df, x_col, y_col, value_col, color_scale):
    """Generate a heatmap."""
    try:
        pivot_table = df.pivot_table(index=y_col, columns=x_col, values=value_col, aggfunc="sum").fillna(0)
        fig = px.imshow(pivot_table, title="Heatmap", labels={"color": value_col}, color_continuous_scale=color_scale)
        fig.update_layout(title="Heatmap", xaxis_title=x_col, yaxis_title=y_col)
        return fig
    except Exception as e:
        st.error(f"Error generating Heatmap: {e}")
        return None

def save_to_html(fig, filename="visualization.html", save_png=False, folder_path="visualizations"):
    """Save the figure to an HTML file and optionally as a PNG."""
    try:
        # Save as HTML
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        fig.write_html(os.path.join(folder_path, filename))
        st.success(f"Visualization saved as {filename}")

        # Save as PNG if requested
        if save_png:
            png_filename = filename.replace(".html", ".png")
            pio.write_image(fig, os.path.join(folder_path, png_filename), scale=3)  # Scale to improve image quality
            st.success(f"Visualization saved as {png_filename}")

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
                    save_to_html(gantt_fig, "gantt_chart.html", save_png=True)

        elif viz_type == "Bar Chart":
            st.write("Generating Bar Chart...")
            bar_x_col = st.selectbox("Select X-axis Column", sheet_data.columns)
            bar_y_col = st.selectbox("Select Y-axis Column", sheet_data.columns)

            if bar_x_col and bar_y_col:
                bar_fig = generate_bar_chart(sheet_data, bar_x_col, bar_y_col, color_scale)
                if bar_fig:
                    st.plotly_chart(bar_fig)
                    save_to_html(bar_fig, "bar_chart.html", save_png=True)

        elif viz_type == "Scatter Plot":
            st.write("Generating Scatter Plot...")
            scatter_x_col = st.selectbox("Select X-axis Column", sheet_data.columns)
            scatter_y_col = st.selectbox("Select Y-axis Column", sheet_data.columns)
            scatter_color_col = st.selectbox("Select Color Column (optional)", [None] + list(sheet_data.columns))

            scatter_fig = generate_scatter_plot(sheet_data, scatter_x_col, scatter_y_col, scatter_color_col, color_scale)
            if scatter_fig:
                st.plotly_chart(scatter_fig)
                save_to_html(scatter_fig, "scatter_plot.html", save_png=True)

        elif viz_type == "Line Chart":
            st.write("Generating Line Chart...")
            line_x_col = st.selectbox("Select X-axis Column", sheet_data.columns)
            line_y_col = st.selectbox("Select Y-axis Column", sheet_data.columns)
            line_color_col = st.selectbox("Select Color Column (optional)", [None] + list(sheet_data.columns))

            line_fig = generate_line_chart(sheet_data, line_x_col, line_y_col, line_color_col, color_scale)
            if line_fig:
                st.plotly_chart(line_fig)
                save_to_html(line_fig, "line_chart.html", save_png=True)

        elif viz_type == "Heatmap":
            st.write("Generating Heatmap...")
            heatmap_x_col = st.selectbox("Select X-axis Column", sheet_data.columns)
            heatmap_y_col = st.selectbox("Select Y-axis Column", sheet_data.columns)
            heatmap_value_col = st.selectbox("Select Value Column", sheet_data.columns)

            heatmap_fig = generate_heatmap(sheet_data, heatmap_x_col, heatmap_y_col, heatmap_value_col, color_scale)
            if heatmap_fig:
                st.plotly_chart(heatmap_fig)
                save_to_html(heatmap_fig, "heatmap.html", save_png=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
