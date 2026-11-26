
import numpy as np  
import pandas as pd
def get_season(month):

    if month in [6, 7, 8, 9]:
        return "Monsoon"

    elif month in [10, 11]:
        return "Post-Monsoon"

    elif month in [12, 1, 2]:
        return "Winter"

    else:
        return "Summer"

print(get_season(7))
print(get_season(12))
print(get_season(4))

def load_data():
    file_path = "data/raw/city_day.csv"
    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])

    return df
def add_season_column(df):
    df["Month"] = df["Date"].dt.month
    df["Season"] = df["Month"].apply(get_season)

    return df
def seasonal_imputation(df):
    pollutants = ["PM2.5", "PM10"]
    df = df.copy()
    groups = df.groupby(["City", "Season"])

    for _, group in groups:
        values = group[pollutants].to_numpy(dtype=float)

        medians = np.nanmedian(values, axis=0)

        missing_rows, missing_cols = np.where(np.isnan(values))

        values[missing_rows, missing_cols] = medians[missing_cols]

        df.loc[group.index, pollutants] = values

    return df

def compare_coastal_inland(df):
    coastal_cities = ["Kochi", "Thiruvananthapuram"]
    inland_cities = ["Delhi", "Lucknow"]
    coastal = df[df["City"].isin(coastal_cities)]
    inland = df[df["City"].isin(inland_cities)]

    coastal_aqi = coastal["AQI"].dropna().to_numpy()
    inland_aqi = inland["AQI"].dropna().to_numpy()

    coastal_severe = coastal_aqi > 300
    coastal_good = coastal_aqi < 50

    inland_severe = inland_aqi > 300
    inland_good = inland_aqi < 50
    coastal_severe_dates = set(
    coastal.loc[coastal["AQI"] > 300, "Date"]
    )

    inland_severe_dates = set(
        inland.loc[inland["AQI"] > 300, "Date"]
    )
    common_severe_dates = coastal_severe_dates.intersection(
        inland_severe_dates
    )
    "Common Severe Smog Dates": len(common_severe_dates)

    results = {
        "Coastal Mean AQI": np.mean(coastal_aqi),
        "Inland Mean AQI": np.mean(inland_aqi),
        "Coastal AQI Std": np.std(coastal_aqi),
        "Inland AQI Std": np.std(inland_aqi),
        "Coastal Severe Days": np.sum(coastal_severe),
        "Inland Severe Days": np.sum(inland_severe),
        "Coastal Good Days": np.sum(coastal_good),
        "Inland Good Days": np.sum(inland_good)
    }

    return results
def multiple_regression(df):
    required_columns = ["AQI", "PM2.5", "PM10", "NO2"]

    data = df[required_columns].dropna()
X = data[["PM2.5", "PM10", "NO2"]].to_numpy()y = data["AQI"].to_numpy()

X = np.column_stack((np.ones(len(X)), X))
    coefficients, residuals, rank, singular_values = np.linalg.lstsq(
        X, y, rcond=None
    )
    y_pred = X @ coefficients

    ss_total = np.sum((y - np.mean(y)) ** 2)
    ss_residual = np.sum((y - y_pred) ** 2)

    r_squared = 1 - (ss_residual / ss_total)
    return {
        "Intercept": coefficients[0],
        "PM2.5 Coefficient": coefficients[1],
        "PM10 Coefficient": coefficients[2],
        "NO2 Coefficient": coefficients[3],
        "R-squared": r_squared
    }
def missing_value_analysis(df):
    pollutants = ["PM2.5", "PM10", "NO2", "NH3", "SO2", "CO"]

    missing_percentages = df.groupby("City")[pollutants].apply(
        lambda group: group.isnull().mean() * 100
    )

    interpolated = df.groupby("City")[pollutants].transform(
        lambda group: group.interpolate(method="linear")
    )

    forward_filled = df.groupby("City")[pollutants].transform(
        lambda group: group.ffill()
    )

    interpolation_missing = interpolated.isnull().sum()
    forward_fill_missing = forward_filled.isnull().sum()

    return {
        "Missing Percentages by City": missing_percentages,
        "Interpolation Remaining Missing": interpolation_missing,
        "Forward Fill Remaining Missing": forward_fill_missing
    }