import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
#code for Q10
def plot_aqi_trend(df, city):

    city_data = df[df['City'] == city].copy()

    city_data['Date'] = pd.to_datetime(city_data['Date'])

    city_data = city_data.sort_values('Date')

    city_data['AQI_MA30'] = city_data['AQI'].rolling(window=30).mean()

    plt.figure(figsize=(12, 6))

    plt.plot(city_data['Date'], city_data['AQI'],
             label='Daily AQI', alpha=0.5)

    plt.plot(city_data['Date'], city_data['AQI_MA30'],
             label='30-Day Moving Average', linewidth=2)

    plt.axhspan(300, city_data['AQI'].max(),
                color='red', alpha=0.15,
                label='Severe AQI (Above 300)')

    plt.title(f'Annual AQI Trend over time - {city}')
    plt.xlabel('Date')
    plt.ylabel('AQI')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('reports/figures/primary_envelope.png')
    plt.show()

#code for Q11 part1 correlation heatmap
def plot_correlation_heatmap(df):

    columns = ['PM2.5', 'PM10', 'NO2', 'CO', 'AQI']

    data = df[columns]

    correlation = data.corr()

    plt.figure(figsize=(10, 7))

    sns.heatmap(
        correlation,
        annot=True,
        cmap='coolwarm',
        fmt='.2f',
        linewidths=0.5
    )

    plt.title('Air Pollutant Correlation Heatmap')

    plt.tight_layout()

    plt.savefig('reports/figures/correlation_heatmap.png')

    plt.close()
#code for Q11 part2 seasonal violin plot
def plot_seasonal_violin(df):

    data = df.copy()
    data['Date'] = pd.to_datetime(data['Date'])

    month = data['Date'].dt.month

    conditions = [
        month.isin([12, 1, 2]),
        month.isin([3, 4, 5]),
        month.isin([6, 7, 8, 9]),
        month.isin([10, 11])
    ]

    seasons = [
        'Winter',
        'Summer',
        'Monsoon',
        'Post-Monsoon'
    ]

    data['Season'] = np.select(
        conditions, seasons, default='Unknown'
    )

    data = data.dropna(subset=['AQI'])

    plt.figure(figsize=(10, 6))

    sns.violinplot(
     data=data,
     x='Season',
     y='AQI',
     hue='Season',
     order=seasons,
     inner='quartile',
     palette='Set2',
     legend=False
  )

    plt.title('AQI Distribution Across Seasons')
    plt.xlabel('Season')
    plt.ylabel('AQI')

    plt.tight_layout()

    plt.savefig(
        'reports/figures/distribution_regimes.png'
    )

    plt.close()
#code for Q12 interactive dashboard

def create_interactive_dashboard(df):

    data = df.copy()

    data['Date'] = pd.to_datetime(
        data['Date'], errors='coerce'
    )

    data = data.dropna(subset=['Date', 'City'])

    data = data.sort_values('Date')

    pollutants = [
        'AQI', 'PM2.5', 'PM10',
        'NO2', 'SO2', 'CO', 'O3'
    ]

    pollutants = [
        p for p in pollutants if p in data.columns
    ]

    for p in pollutants:
        data[p] = pd.to_numeric(
            data[p], errors='coerce'
        )

    if not pollutants:
        raise ValueError("No pollutant columns found.")

    cities = sorted(data['City'].unique())

    fig = px.line()

    trace_pollutants = []

    initial_pollutant = (
        'AQI' if 'AQI' in pollutants else pollutants[0]
    )

    for pollutant in pollutants:

        plot_data = data.dropna(
            subset=[pollutant]
        )

        pollutant_fig = px.line(
            plot_data,
            x='Date',
            y=pollutant,
            color='City',
            custom_data=['City'],
            title='Interactive CPCB Air Quality Dashboard'
        )

        pollutant_fig.update_traces(
            hovertemplate=(
                'City: %{fullData.name}'
                '<br>Date: %{x|%Y-%m-%d}'
                f'<br>{pollutant}: '
                '%{y:.2f}'
                '<extra></extra>'
            )
        )

        # Add traces to main figure
        for trace in pollutant_fig.data:

            trace.visible = (
                pollutant == initial_pollutant
            )

            fig.add_trace(trace)

            trace_pollutants.append(pollutant)

    buttons = []

    for pollutant in pollutants:

        visibility = [
            p == pollutant for p in trace_pollutants
        ]

        buttons.append(
            dict(
                label=pollutant,
                method='update',
                args=[
                    {'visible': visibility},
                    {'yaxis': {'title': pollutant}}
                ]
            )
        )

    fig.update_layout(

        title='Interactive CPCB Air Quality Dashboard',

        xaxis=dict(
            title='Date',
            type='date',
            autorange=True,
            rangeslider=dict(
                visible=True,
                thickness=0.15
            )
        ),

        yaxis=dict(
            title=initial_pollutant
        ),

        updatemenus=[
            dict(
                buttons=buttons,
                direction='down',
                x=1.0,
                y=1.15,
                showactive=True
            )
        ],

        legend_title='Cities',

        template='plotly_white',

        height=650
    )

    os.makedirs('reports', exist_ok=True)

    fig.write_html(
        'reports/interactive_dashboard.html',
        include_plotlyjs=True
    )

    print(
        'Interactive dashboard generated successfully!'
    )
