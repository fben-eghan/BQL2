import bql
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html

# Step 1: Setup Environment
bq = bql.Service()

# Step 2: Define functions for getting and processing data
def get_data(securities):
    """
    Retrieves price and date data for a list of securities from Bloomberg Query Language (BQL).

    Args:
        securities (list): A list of securities represented by their SEDOL codes.

    Returns:
        A pandas DataFrame containing the price and date data for the requested securities.
    """
    req = bql.Request(securities, {'Price': bq.data.px_last(fill='prev'),
                                   'Price Date': bq.data.px_last_date(fill='prev')})
    res = bq.execute(req)
    return pd.concat([field.df()[field.name] for field in res], axis=1)

def process_data(df):
    """
    Calculates the price changes and highlight values for a given DataFrame of security prices.

    Args:
        df (pandas DataFrame): A DataFrame containing security prices and dates.

    Returns:
        The original DataFrame with added columns for price changes and highlight values.
    """
    df['Price Change'] = df['Price'].diff(periods=1)
    df['Price Highlight'] = 'None'
    df.loc[(abs(df['Price Change']) / df['Price'].shift(1)) >= 0.1, 'Price Highlight'] = 'Yellow'
    return df

# Step 3: Get and process data
securities_df = pd.read_csv('securities.csv')
securities = list(securities_df['SEDOL'])

df = get_data(securities)
df = process_data(df)

# Step 4: Define the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Security Prices'),

    html.Table(children=[
        html.Thead(
            html.Tr(children=[
                html.Th('Security'),
                html.Th('Price'),
                html.Th('Price Date'),
                html.Th('Price Change'),
            ])
        ),
        html.Tbody([
            html.Tr(children=[
                html.Td(df.loc[i, 'SEDOL']),
                html.Td(df.loc[i, 'Price']),
                html.Td(df.loc[i, 'Price Date']),
                html.Td(df.loc[i, 'Price Change'], style={'background-color': df.loc[i, 'Price Highlight']})
            ]) for i in range(len(df))
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
