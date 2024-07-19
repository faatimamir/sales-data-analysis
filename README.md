# Sales Data Analysis and Forecasting Application

Welcome to the Sales Data Analysis and Forecasting Application! This application leverages the power of Flask and a Large Language Model (Gemini API) to provide deep insights and forecasts based on your sales data. This application ingests data from an XLSX file and offers RESTful API endpoints to analyze performance feedback, team performance, and sales trends.

## Features

- **Data Ingestion**: Upload XLSX files containing sales data with ease.
- **Performance Feedback**: Get detailed, AI-generated feedback on individual units.
- **Team Performance Analysis**: Understand your team's overall performance metrics and areas for improvement.
- **Sales Trends and Forecasting**: Analyze past sales trends and predict future sales patterns using advanced AI algorithms.

## Project Structure

```
sales-data-analysis/
│
├── app.py
├── data_ingestion.py
├── llm_integration.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── uploads/
├── requirements.txt
└── README.md
```

- `app.py`: Main application file with Flask routes and logic.
- `data_ingestion.py`: Script to load data from the XLSX file.
- `llm_integration.py`: Integrates with the LLM to generate insights.
- `templates/`: HTML templates directory.
- `static/`: Static files directory containing CSS.
- `uploads/`: Directory for storing uploaded files.
- `requirements.txt`: Project dependencies.
- `README.md`: This README file.

## Installation

### Prerequisites

Ensure you have Python installed. This application has been tested with Python 3.8+.

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/faatimamir/sales-data-analysis.git
   cd sales-data-analysis
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the LLM API key:**

   Open `llm_integration.py` and replace `'your_api_key_here'` with your actual API key.

   ```python
   genai.configure(api_key='your_api_key_here')
   ```

## Usage

1. **Run the application:**

   ```bash
   python app.py
   ```

2. **Access the application:**

   Open your web browser and navigate to `http://127.0.0.1:5000`.

### API Endpoints

#### Load Data

- **URL**: `/api/load_data`
- **Method**: `POST`
- **Description**: Upload an XLSX file and load data into the application.
- **Request Body**: Form data with the file to be uploaded.
- **Response**: JSON message indicating success or error.

#### Performance Feedback

- **URL**: `/api/performance_feedback`
- **Method**: `GET`
- **Description**: Retrieve AI-generated performance feedback for a specific unit.
- **Parameters**:
  - `unit_id`: The ID of the unit to retrieve feedback for.
- **Response**: JSON with feedback or error message.

#### Team Performance

- **URL**: `/api/team_performance`
- **Method**: `GET`
- **Description**: Analyze and retrieve overall team performance metrics.
- **Response**: JSON with performance insights or error message.

#### Sales Trends and Forecasting

- **URL**: `/api/sales_trends`
- **Method**: `GET`
- **Description**: Analyze sales trends and forecast future sales patterns.
- **Response**: JSON with trend analysis and forecasting or error message.

## How It Works

### Data Ingestion

The `/api/load_data` endpoint handles file uploads. The `data_ingestion.py` script reads the XLSX file, extracting data from the 'building_table,' 'unit_table,' and 'history_table' sheets, and stores this data for further processing.

```python
def load_data(file_path):
    try:
        if file_path.endswith('.xlsx'):
            xls = pd.ExcelFile(file_path)
            data = {
                'building_table': pd.read_excel(xls, sheet_name='building_table'),
                'unit_table': pd.read_excel(xls, sheet_name='unit_table'),
                'history_table': pd.read_excel(xls, sheet_name='history_table')
            }
        else:
            raise ValueError("Unsupported file format. Please provide an XLSX file.")
        return data
    except Exception as e:
        raise ValueError(f"Error loading data from file: {str(e)}")
```

### Performance Feedback

The `/api/performance_feedback` endpoint calls `get_performance_feedback` from `llm_integration.py`. This function sends a detailed prompt to the LLM, including relevant unit data, to generate performance feedback.

```python
def get_performance_feedback(data, unit_id):
    unit_id = str(unit_id).strip()
    data['unit_table']['unit'] = data['unit_table']['unit'].astype(str).str.strip()
    unit_data = data['unit_table'][data['unit_table']['unit'] == unit_id]

    if unit_data.empty:
        return "No data found for the given unit_id."

    feedback_prompt = (
        f"Please provide performance feedback for the unit with ID {unit_id}. "
        f"Here is the relevant data for this unit: {unit_data.to_dict()}. "
        f"Based on this information, provide a detailed analysis of the unit's performance."
    )
    
    response = chat.send_message(feedback_prompt)
    return response.text
```

### Team Performance Analysis

The `/api/team_performance` endpoint calls `get_team_performance` from `llm_integration.py`. It merges the data tables and sends a detailed prompt to the LLM for team performance analysis.

```python
def get_team_performance(data):
    merged_units_buildings = pd.merge(
        data['unit_table'], 
        data['building_table'], 
        left_on='building_id', 
        right_on='id', 
        suffixes=('_unit', '_building')
    )
    
    combined_data = pd.merge(
        merged_units_buildings, 
        data['history_table'], 
        left_on='unit', 
        right_on='unit_id', 
        suffixes=('_combined', '_history')
    )
    
    team_performance_prompt = (
        f"Analyze the overall team performance based on the following merged data: {combined_data.describe().to_dict()}. "
        f"Provide insights into key metrics and suggest areas for improvement."
    )
    
    response = chat.send_message(team_performance_prompt)
    return response.text
```

### Sales Trends and Forecasting

The `/api/sales_trends` endpoint calls `get_sales_trends_and_forecasting` from `llm_integration.py`. It merges the data, analyzes sales trends, and sends a detailed prompt to the LLM for forecasting.

```python
def get_sales_trends_and_forecasting(data):
    merged_data = pd.merge(
        data['unit_table'], 
        data['history_table'], 
        left_on='id', 
        right_on='unit_id',
        how='inner'
    )
    
    date_column = 'available date_x' if 'available date_x' in merged_data.columns else 'available date_y'
    merged_data[date_column] = pd.to_datetime(merged_data[date_column], errors='coerce')
    merged_data = merged_data.dropna(subset=[date_column])

    sales_trends = merged_data.groupby(date_column).agg({'price_y': 'mean'}).reset_index()
    summary = sales_trends.describe().to_dict()

    sales_trends_prompt = (
        f"Based on the sales data provided, here are key statistics: {summary}. "
        f"Please analyze these trends and provide insights into potential sales patterns, "
        f"and forecast future sales trends based on this data."
    )

    response = chat.send_message(sales_trends_prompt)
    return {'llm_response': response.text}
```

## Logging

The application uses Python's `logging` module to provide detailed debugging information. Logs are output to the console with a `DEBUG` level, enabling you to trace the application's operations and quickly identify issues.

## Error Handling

The application includes comprehensive error handling to manage issues such as missing files, data processing errors, and integration issues with the LLM. Appropriate HTTP status codes and descriptive error messages are returned to the client.


