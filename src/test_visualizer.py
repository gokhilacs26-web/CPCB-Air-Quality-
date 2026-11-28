import pandas as pd
#code for Q10
from src.visualizer import plot_aqi_trend
#code for Q11 part1 correlation heatmap
from src.visualizer import plot_correlation_heatmap
#code for Q11 part2 seasonal violin plot
from src.visualizer import plot_seasonal_violin
#code for Q12 interactive dashboard
from src.visualizer import create_interactive_dashboard
#code for Q10
df = pd.read_csv('data/raw/cpcb_city_day_raw.csv')

print(df['City'].unique())
plot_aqi_trend(df, 'Kochi')
#code for Q11 part1 correlation heatmap
plot_correlation_heatmap(df)
print("Correlation heatmap generated successfully!")
#code for Q11 part2 seasonal violin plot
plot_seasonal_violin(df)
print("Seasonal violin plot generated successfully!")
#code for Q12 interactive dashboard
create_interactive_dashboard(df)

