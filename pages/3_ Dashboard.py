import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from dbconnection import fetch_cheque_details, init_db_connection
from datetime import datetime
import streamlit_shadcn_ui as ui
import altair as alt
import plotly.graph_objects as go 


# initialize Supabase DB connection once
init_db_connection()

# cheque_data is initialized before use
if "cheque_data" not in st.session_state:
    records = fetch_cheque_details()
    if records:
        expected_columns = ["cheque_date", "account_number", "bank_name", "cheque_number", "payee_name", "amount", "uploaded_at"]
        if len(records[0]) == 8:
            expected_columns.append("status")
        st.session_state.cheque_data = pd.DataFrame(records, columns=expected_columns)
    else:
        st.session_state.cheque_data = pd.DataFrame()  # initialize an empty DataFrame to prevent errors

# load cheque data from session state
df = st.session_state.cheque_data

if df.empty:
    st.warning("No cheque data available.")
else:
    #df["cheque_date"] = pd.to_datetime(df["cheque_date"], errors='coerce', dayfirst=True)
    df["cheque_date"] = pd.to_datetime(df["cheque_date"], format="%Y-%m-%d", errors="coerce")
    df["uploaded_at"] = pd.to_datetime(df["uploaded_at"], errors='coerce')
    df["upload_date"] = df["uploaded_at"].dt.strftime("%Y-%m-%d")  

    total_cheques = len(df)
    today = datetime.today().date()
    today_count = len(df[df["upload_date"] == str(today)]) if "upload_date" in df.columns else 0
    failed_count = len(df[df["status"] == "Failed"]) if "status" in df.columns else 0

    # Dashboard UI
    st.subheader("Dashboard")
    selected_tab = ui.tabs(options=['Overview', 'Analytics', 'Reports', 'Tables'], default_value='Overview', key="main_tabs")

    if selected_tab == 'Overview':
        cols = st.columns(3)
        with cols[0]:
            ui.card(title="Total Cheques Processed", content=str(total_cheques), key="card1").render()
        with cols[1]:
            ui.card(title="Today's Cheques Processed", content=str(today_count), key="card2").render()
        with cols[2]:
            ui.card(title="Failed Cheques", content=str(failed_count), key="card3").render()

        # charts Section
        chart_cols = st.columns(2)

        with chart_cols[0]:  
            st.subheader("Cheques Processed Over Time")
            df["upload_date"] = pd.to_datetime(df["uploaded_at"], errors="coerce").dt.date  # Convert to date first

            # Convert back to datetime for Altair (needed for time-series)
            df["upload_date"] = pd.to_datetime(df["upload_date"])

            upload_counts = df.groupby("upload_date").size().reset_index(name="count")
            line_chart = alt.Chart(upload_counts).mark_line(point=True).encode(
                x=alt.X("upload_date:T", title="Upload Date"),
                y=alt.Y("count:Q", title="Total Cheques Processed"),
                tooltip=["upload_date:T", "count"]
            ).properties(width=500, height=400)
            st.altair_chart(line_chart, use_container_width=True)

        with chart_cols[1]:  
            st.subheader("Cheques by Bank")
            bank_counts = df["bank_name"].value_counts().reset_index()
            bank_counts.columns = ["Bank", "Count"]
            bar_chart = alt.Chart(bank_counts).mark_bar().encode(
                x=alt.X("Bank:N", title="Bank"),
                y=alt.Y("Count:Q", title="Cheques Processed"),
                tooltip=["Bank", "Count"]
            ).properties(width=500, height=400)
            st.altair_chart(bar_chart, use_container_width=True)
        

        st.subheader("Cheque Records")
        overview_data = df[["cheque_date", "cheque_number", "payee_name", "account_number", "bank_name", "amount"]]
        overview_data.columns = ["Cheque Date", "Cheque No", "Payee Name", "Account Number", "Bank Name", "Amount"]

        fig = go.Figure(data=[go.Table(
            header=dict(values=list(overview_data.columns), fill_color="#0cc789", font=dict(color="#000000", size=14), align="left"),
            cells=dict(values=[overview_data[col] for col in overview_data.columns], fill_color="white", align="left", font=dict(color="black", size=13))
        )])
        st.plotly_chart(fig, use_container_width=True)
                

    elif selected_tab == 'Analytics':        
        st.subheader("Cheque Amount Distribution by Bank")

        df["uploaded_at"] = pd.to_datetime(df["uploaded_at"], errors="coerce")
        df["upload_date"] = df["uploaded_at"].dt.date  # extract only the date

        pie_chart = alt.Chart(df).mark_arc().encode(
            theta=alt.Theta("amount:Q", title="Total Amount"),
            color=alt.Color("bank_name:N", scale=alt.Scale(scheme="category20"), legend=alt.Legend(title="Bank")),
            tooltip=["bank_name", "amount"]
        ).properties(width=400, height=300)
        st.altair_chart(pie_chart, use_container_width=True)

        st.subheader("Cheque Processing Trend by Day")  
        df["uploaded_at"] = pd.to_datetime(df["uploaded_at"], errors="coerce")

        # drop rows where `upload_date` is missing
        df = df.dropna(subset=["upload_date"])
        # proceed with Altair charts safely
        upload_counts = df.groupby("upload_date").size().reset_index(name="count")

        daily_chart = alt.Chart(upload_counts).mark_line(point=True).encode(
            x=alt.X("upload_date:T", title="Cheque Upload Date"),
            y=alt.Y("count:Q", title="Total Cheques Processed"),
            tooltip=["upload_date:T", "count"]
        ).properties(width=600, height=400)

        st.altair_chart(daily_chart, use_container_width=True) 

        st.subheader("Cheque Processing Trend by Month")
        df["upload_month"] = df["uploaded_at"].dt.strftime('%Y-%m')  
        monthly_counts = df.groupby("upload_month").size().reset_index(name="count")

        heatmap = alt.Chart(monthly_counts).mark_rect().encode(
            x="upload_month:N", y="count:Q", color="count:Q", tooltip=["upload_month", "count"]
        ).properties(width=600, height=300)
        st.altair_chart(heatmap, use_container_width=True) 
       

    elif selected_tab == 'Reports':
        st.subheader("Report & Insight")
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce").dt.date  

        # handle Date Range Selection
        min_date, max_date = df["upload_date"].min(), df["upload_date"].max()
        date_range = st.date_input("Select Date Range", [min_date, max_date] if min_date and max_date else [today, today])

        if isinstance(date_range, list) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = date_range[0]
            end_date = today  
        if end_date > today:
            st.error("End date cannot be in the future. Please select a valid date range.")
        elif start_date > end_date:
            st.error("Start date cannot be after end date. Please select a valid range.")
        else:
            filtered_df = df[(df["upload_date"] >= start_date) & (df["upload_date"] <= end_date)]
            
            if not filtered_df.empty:
                highest_cheque = filtered_df["amount"].max()
                lowest_cheque = filtered_df["amount"].min()
                avg_cheque = filtered_df["amount"].mean()

                metric_cols = st.columns(3)
                with metric_cols[0]:
                    ui.card(title="Highest Cheque Amount", content=f"₹{highest_cheque:,.2f}", key="metric1").render()
                with metric_cols[1]:
                    ui.card(title="Lowest Cheque Amount", content=f"₹{lowest_cheque:,.2f}", key="metric2").render()
                with metric_cols[2]:
                    ui.card(title="Average Cheque Amount", content=f"₹{avg_cheque:,.2f}", key="metric3").render()
            else:
                st.warning("No records found for the selected date range.")


    elif selected_tab == 'Tables':
        st.subheader("Cheque Records Table")
        # define the Supabase Table Fields (Ensure consistency with the database)
        supabase_columns = ["cheque_date", "account_number", "bank_name", "cheque_number", 
                        "payee_name", "amount", "uploaded_at", "status"]

        # filter DataFrame to Include Only These Columns
        cheque_data_filtered = df[supabase_columns] if all(col in df.columns for col in supabase_columns) else df

        # configure Ag-Grid Table
        gb = GridOptionsBuilder.from_dataframe(cheque_data_filtered)
        gb.configure_pagination(enabled=True)
        gb.configure_side_bar()
        gb.configure_default_column(editable=True, groupable=True)
        grid_options = gb.build()
        AgGrid(cheque_data_filtered, gridOptions=grid_options, fit_columns_on_grid_load=True)

        st.subheader("Cheque Records Summary")
        summary_data = df.groupby("bank_name").agg({"cheque_number": "count", "amount": "sum"}).reset_index()
        summary_data.columns = ["Bank Name", "Total Cheques", "Total Amount"]

        fig_summary = go.Figure(data=[go.Table(
            header=dict(values=list(summary_data.columns), fill_color="#0cc789", align="left", font=dict(color="black", size=14)),
            cells=dict(values=[summary_data[col] for col in summary_data.columns], fill_color="white", align="left")
        )])

        st.plotly_chart(fig_summary, use_container_width=True) 
