
    
import google.generativeai as genai

import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)

genai.configure(api_key='AIzaSyDbTo4knGFw52--xAsOTzep3Kqt1AMPDbU')
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

def get_performance_feedback(data, unit_id):
    print("unit_id", unit_id)
  
    # Ensure unit_id is a string for comparison
    unit_id = str(unit_id).strip()
    
    # Strip whitespace from unit column values
    data['unit_table']['unit'] = data['unit_table']['unit'].astype(str).str.strip()
    
    # Print available unit IDs and their types for debugging
    print("Available unit IDs:", data['unit_table']['unit'].unique())
    print("Data type of unit column:", data['unit_table']['unit'].dtype)
    print("Data type of requested unit_id:", type(unit_id))
    
    print("Requested unit_id:", unit_id)
    
    # Filter data for the specified unit (not id)
    unit_data = data['unit_table'][data['unit_table']['unit'] == unit_id]
    
    if unit_data.empty:
        return "No data found for the given unit_id."

    
    # Create a detailed prompt
    feedback_prompt = (
        f"Please provide performance feedback for the unit with ID {unit_id}. "
        f"Here is the relevant data for this unit: {unit_data.to_dict()}. "
        f"Based on this information, provide a detailed analysis of the unit's performance."
    )
    
    response = chat.send_message(feedback_prompt)
    return response.text



def get_team_performance(data):
    try:
        print("unit_table columns:", data['unit_table'].columns)
        print("building_table columns:", data['building_table'].columns)
        print("history_table columns:", data['history_table'].columns)

        # Merge the tables
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
        
        # Create a detailed prompt
        team_performance_prompt = (
            f"Analyze the overall team performance based on the following merged data: {combined_data.describe().to_dict()}. "
            f"Provide insights into key metrics and suggest areas for improvement."
        )
        
        response = chat.send_message(team_performance_prompt)
        return response.text
    
    except KeyError as e:
        return f"KeyError: {str(e)}"
    except Exception as e:
        return f"Error in team performance calculation: {str(e)}"




def get_sales_trends_and_forecasting(data):
    try:
        # Debugging: Print column names
        logging.debug(f"unit_table columns: {data['unit_table'].columns}")
        logging.debug(f"history_table columns: {data['history_table'].columns}")

        # Check if tables are empty
        if data['unit_table'].empty or data['history_table'].empty:
            return {'error': 'One or both of the data tables are empty.'}

        # Merge the tables
        merged_data = pd.merge(
            data['unit_table'], 
            data['history_table'], 
            left_on='id', 
            right_on='unit_id',
            how='inner'  # Use 'inner' to avoid merging issues
        )

        # Debugging: Check merged data columns
        logging.debug(f"Merged data columns: {merged_data.columns}")
        
        # Handle potential renamed columns
        date_column = 'available date_x' if 'available date_x' in merged_data.columns else 'available date_y'
        
        if date_column not in merged_data.columns:
            return {'error': 'Date column not found in merged data.'}

        # Ensure date column is in datetime format
        merged_data[date_column] = pd.to_datetime(merged_data[date_column], errors='coerce')

        # Drop rows with invalid dates
        merged_data = merged_data.dropna(subset=[date_column])

        # Aggregate sales data by date
        sales_trends = merged_data.groupby(date_column).agg({'price_y': 'mean'}).reset_index()

        # Generate summary for LLM
        summary = sales_trends.describe().to_dict()

        # Create a detailed prompt
        sales_trends_prompt = (
            f"Based on the sales data provided, here are key statistics: {summary}. "
            f"Please analyze these trends and provide insights into potential sales patterns, "
            f"and forecast future sales trends based on this data."
        )

        # Assuming 'chat' is an instance of your LLM client
        response = chat.send_message(sales_trends_prompt)

        # Return LLM response
        return {'llm_response': response.text}
    
    except Exception as e:
        logging.error(f"Exception in get_sales_trends_and_forecasting: {str(e)}")
        return {'error': 'An error occurred during processing.'}