import streamlit as st
import mysql.connector
import pandas as pd

# Database connection details
host = 'mysql-272ae44e-aishwaryahalder01-ca5c.i.aivencloud.com'
port = 21640
user = 'avnadmin'
password = 'AVNS_0U7vYiJ9zKFyfsmDvMg'
database = 'Stocks'

# Function to connect to the database
def get_db_connection():
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

# Function to get all stocks from Stock_Links table
def get_all_stocks():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Stock_Name, Stock_URL FROM Stock_Links;")
    stocks = cursor.fetchall()
    connection.close()
    return pd.DataFrame(stocks, columns=['Stock Name', 'Stock URL'])

# Function to get all stocks from Segmented_Stock_List table
def get_segmented_stocks():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ID, Stock_Name FROM Segmented_Stock_List;")
    stocks = cursor.fetchall()
    connection.close()
    return pd.DataFrame(stocks, columns=['ID', 'Stock Name'])

# Function to add selected stocks to Segmented_Stock_List
def add_to_segmented_list(selected_stocks):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Get existing stocks in the Segmented_Stock_List
    existing_stocks = get_segmented_stocks()
    existing_stock_names = set(existing_stocks['Stock Name'].tolist())
    
    # Filter out stocks that are already present
    stocks_to_add = [stock for stock in selected_stocks if stock['Stock Name'] not in existing_stock_names]
    
    if stocks_to_add:
        insert_query = "INSERT INTO Segmented_Stock_List (Stock_Name, Stock_URL) VALUES (%s, %s);"
        cursor.executemany(insert_query, [(stock['Stock Name'], stock['Stock URL']) for stock in stocks_to_add])
        connection.commit()
        st.success(f"Added {len(stocks_to_add)} new stock(s) to Segmented_Stock_List!")
    else:
        st.info("All selected stocks are already present in Segmented_Stock_List.")
    
    connection.close()

# Function to delete stocks from Segmented_Stock_List
def delete_from_segmented_list(stock_ids):
    connection = get_db_connection()
    cursor = connection.cursor()
    delete_query = "DELETE FROM Segmented_Stock_List WHERE ID = %s;"
    # Convert each ID to int before executing the query
    for stock_id in stock_ids:
        cursor.execute(delete_query, (int(stock_id),))
    connection.commit()
    connection.close()

# Streamlit UI
st.title("Stock Management")

# Fetch all stocks from Stock_Links
all_stocks_df = get_all_stocks()

# Display a multiselect for stocks to add
selected_stocks = st.multiselect('Select Stocks to Add', all_stocks_df['Stock Name'].tolist())

# Filter DataFrame to get selected stocks' details
selected_stocks_df = all_stocks_df[all_stocks_df['Stock Name'].isin(selected_stocks)]

# Add Button
if st.button('Add to Segmented Stock List'):
    add_to_segmented_list(selected_stocks_df.to_dict('records'))

# Fetch stocks in Segmented_Stock_List for deletion
segmented_stocks_df = get_segmented_stocks()

# Multi-select for selecting stocks to delete
selected_stocks_to_delete = st.multiselect('Select Stocks to Delete from Segmented Stock List', segmented_stocks_df['Stock Name'].tolist())

# Find the IDs of the selected stocks for deletion
stock_ids_to_delete = segmented_stocks_df[segmented_stocks_df['Stock Name'].isin(selected_stocks_to_delete)]['ID'].tolist()

# Delete Button
if st.button('Delete from Segmented Stock List'):
    if stock_ids_to_delete:
        delete_from_segmented_list(stock_ids_to_delete)
        st.success(f"Deleted {len(stock_ids_to_delete)} stock(s) from Segmented_Stock_List.")
    else:
        st.info("No stocks selected for deletion.")
