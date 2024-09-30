import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style for the seaborn plots
sns.set(style='dark')

# Define a color palette for consistent styling
palette = sns.color_palette("viridis", 10)

def create_daily_rentals_df(df):
    daily_rentals_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    })
    daily_rentals_df = daily_rentals_df.reset_index()
    daily_rentals_df.rename(columns={
        "cnt": "total_rentals",
        "casual": "total_casual",
        "registered": "total_registered"
    }, inplace=True)
    
    return daily_rentals_df

def create_seasonal_df(df):
    seasonal_df = df.groupby("season").cnt.sum().reset_index()
    seasonal_df.rename(columns={"cnt": "total_rentals"}, inplace=True)
    return seasonal_df

def create_by_hour_df(df):
    by_hour_df = df.groupby("hr").cnt.sum().reset_index()
    return by_hour_df

def create_by_weekday_df(df):
    by_weekday_df = df.groupby("weekday").cnt.sum().reset_index()
    return by_weekday_df

def create_heatmap_df(df):
    heatmap_df = df.groupby(['weekday', 'hr']).agg({
        'cnt': 'sum'
    }).reset_index()
    
    heatmap_pivot = heatmap_df.pivot_table(index='weekday', columns='hr', values='cnt', aggfunc='sum')
    return heatmap_pivot

# Load cleaned data
all_df = pd.read_csv("preprocessed_hour.csv")

# Convert 'dteday' to datetime and sort
all_df['dteday'] = pd.to_datetime(all_df['dteday'])
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Filter data
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    # Add company logo
    st.image("logo.jpg")
    
    # Get start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label='Date Range', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                  (all_df["dteday"] <= str(end_date))]

# Prepare various dataframes
daily_rentals_df = create_daily_rentals_df(main_df)
seasonal_df = create_seasonal_df(main_df)
by_hour_df = create_by_hour_df(main_df)
by_weekday_df = create_by_weekday_df(main_df)
heatmap_df = create_heatmap_df(main_df)

# Dashboard Header
st.header('🚴 Bike Sharing Dashboard 🚴')

# Create tabs for Daily, Weekly, and Seasonal Analysis
tabs = st.tabs(["Daily Analysis", "Weekly Analysis", "Seasonal Analysis"])

# Daily Analysis Tab
with tabs[0]:
    st.subheader('Daily Rentals')
    
    col1, col2 = st.columns(2)

    with col1:
        total_rentals = daily_rentals_df.total_rentals.sum()
        st.metric("Total Rentals", value=total_rentals)

    with col2:
        total_casual = daily_rentals_df.total_casual.sum()
        total_registered = daily_rentals_df.total_registered.sum()
        st.metric("Total Casual Rentals", value=total_casual)
        st.metric("Total Registered Rentals", value=total_registered)

    # Daily Rentals Plot
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_rentals_df["dteday"],
        daily_rentals_df["total_rentals"],
        marker='o', 
        linewidth=2,
        color=palette[0]  # Use the first color from the palette
    )
    ax.set_title("Daily Bike Rental Trends", fontsize=24)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)

    st.pyplot(fig)

    # Rentals by Hour
    st.subheader("Rentals by Hour of the Day")

    # Highlight max and min in the bar plot
    max_rentals = by_hour_df['cnt'].max()
    min_rentals = by_hour_df['cnt'].min()

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar("hr", "cnt", data=by_hour_df, color=palette[1])
    
    # Highlight max and min bars
    for bar in bars:
        if bar.get_height() == max_rentals:
            bar.set_color(palette[2])  # Highlight max in a different color
        elif bar.get_height() == min_rentals:
            bar.set_color(palette[3])  # Highlight min in a different color

    ax.set_title("Total Rentals by Hour", fontsize=20)
    ax.set_ylabel("Total Rentals", fontsize=14)
    ax.set_xlabel("Hour", fontsize=14)
    st.pyplot(fig)

    # Stacked Bar Chart for Casual and Registered
    st.subheader("Stacked Bar Chart of Casual and Registered Rentals by Day")

    stacked_df = main_df.groupby('weekday').agg({
        'casual': 'sum',
        'registered': 'sum'
    }).reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(stacked_df['weekday'], stacked_df['casual'], label='Casual Rentals', color=palette[1])
    ax.bar(stacked_df['weekday'], stacked_df['registered'], bottom=stacked_df['casual'], label='Registered Rentals', color=palette[2])
    ax.set_title("Stacked Bar Chart of Casual and Registered Rentals by Day", fontsize=20)
    ax.set_ylabel("Total Rentals", fontsize=14)
    ax.set_xlabel("Day of the Week", fontsize=14)
    ax.legend()
    st.pyplot(fig)

# Weekly Analysis Tab
with tabs[1]:
    st.subheader("Rentals by Day of the Week")

    fig, ax = plt.subplots(figsize=(12, 6))
    max_weekday_rentals = by_weekday_df['cnt'].max()
    min_weekday_rentals = by_weekday_df['cnt'].min()

    bars = sns.barplot(x="weekday", y="cnt", data=by_weekday_df, palette=palette[4:8], ax=ax)

    # Highlight max and min in the bar plot
    for bar in bars.patches:
        if bar.get_height() == max_weekday_rentals:
            bar.set_facecolor(palette[8])  # Highlight max in a different color
        elif bar.get_height() == min_weekday_rentals:
            bar.set_facecolor(palette[9])  # Highlight min in a different color

    ax.set_title("Total Rentals by Day of the Week", fontsize=20)
    ax.set_ylabel("Total Rentals", fontsize=14)
    ax.set_xlabel("Weekday", fontsize=14)
    st.pyplot(fig)

# Seasonal Analysis Tab
with tabs[2]:
    st.subheader("Rentals by Season")

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = sns.barplot(x="season", y="total_rentals", data=seasonal_df, palette=palette[0:4], ax=ax)

    # Highlight max and min in the bar plot
    max_seasonal_rentals = seasonal_df['total_rentals'].max()
    min_seasonal_rentals = seasonal_df['total_rentals'].min()

    for bar in bars.patches:
        if bar.get_height() == max_seasonal_rentals:
            bar.set_facecolor(palette[8])  # Highlight max in a different color
        elif bar.get_height() == min_seasonal_rentals:
            bar.set_facecolor(palette[9])  # Highlight min in a different color

    ax.set_title("Total Rentals by Season", fontsize=20)
    ax.set_ylabel("Total Rentals", fontsize=14)
    ax.set_xlabel("Season", fontsize=14)
    st.pyplot(fig)

    # Heatmap
    st.subheader("Heatmap of Rentals by Hour and Day")

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_df, cmap='YlGnBu', annot=False, ax=ax)  # No labels on heatmap
    ax.set_title("Heatmap of Bike Rentals by Hour and Day", fontsize=20) 
    ax.set_xlabel("Hour", fontsize=14)
    ax.set_ylabel("Day of the Week", fontsize=14)
    st.pyplot(fig)

st.caption('Copyright © Diki Wahyudi 2024')
