import datetime
import dash
from dash import dcc, html,dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from wordcloud import WordCloud
import base64
from io import BytesIO
import time


# Load data from results.csv
def load_data():
    return pd.read_csv("results_1.csv")


# Define function to create word cloud
def create_word_cloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='black').generate(text)
    img_bytes = BytesIO()
    wordcloud.to_image().save(img_bytes, format='PNG')
    return img_bytes.getvalue()


# Initialize the Dash app
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

# Define the layout of the app
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('booksage_logo.png'),
                     id='corona-image',
                     style={"height": "180px", "width": "auto", "align": "center"}
                     )
        ], className="one-half column")
    ], id="header", className="row flex-display", style={"margin-bottom": "10px"}),

    # Book details
    html.Div([
        html.Div([
            html.P(id="book-name",
                   style={
                       'textAlign': 'left',
                       'fontFamily': 'Bahnschrift SemiBold Condensed',
                       'color': 'white',
                       'fontSize': '20px',
                       'margin': '0',
                       'fontWeight': 'bold'
                   }),
            html.P(id="plot-summary",
                   style={
                       'textAlign': 'justify',
                       'fontFamily': 'Bahnschrift SemiBold Condensed',
                       'color': '#CCFFCC',
                       'fontSize': '15px',
                       'marginTop': '10px'
                   }),
        ], style={
            'padding': '20px',
            'margin': '10px 0',
            'borderRadius': '5px',
            'background': '#2A2A2A',
            'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2)',
            'border': '1px solid #444'
        })
    ], style={'padding': '20px'}),

    # Summary statistics
    html.Div([
        html.Div([
            html.H4("Total Positive Reviews (%)", className="card-title"),
            dcc.Graph(
                id='total_positive_gauge',
                config={'displayModeBar': False}
            ),
        ], className="card_container three columns"),
        html.Div([
            html.H4("Total Negative Reviews (%)", className="card-title"),
            dcc.Graph(
                id='total_negative_gauge',
            ),
        ], className="card_container three columns"),
        html.Div([
            html.H4("Total Neutral Reviews (%)", className="card-title"),
            dcc.Graph(
                id='total_neutral_gauge',
            ),
        ], className="card_container three columns"),
    ], className="row flex-display"),

    # Dropdown and pie chart
    html.Div([
        html.Div([
            html.Div([
                html.H6("⬇️ Select pointers here", style={
                    'textAlign': 'center',
                    'color': 'balck',
                    'fontSize': '16px',
                    'padding': '0px',
                    'background': 'white',
                    'borderRadius': '5px',
                    'margin': '10px 0',
                })
            ], style={
                'textAlign': 'center',
            }),

            dcc.Dropdown(id='w_countries', multi=False, clearable=True, value='positive',
                         placeholder='Select Sentiment Category',
                         options=[
                             {'label': 'Positive', 'value': 'positive'},
                             {'label': 'Negative', 'value': 'negative'}
                         ],
                         className='dcc_compon'),
            html.P('Extracted ON: ' + '  ' + ' ' + str(datetime.datetime.now().strftime("%B %d, %Y")) + '  ',
                   className='fix_label', style={'color': 'white', 'fontSize': 15, 'text-align': 'left'}),
        ], className="create_container three columns", id="cross-filter-options"),
        # Word cloud
        html.Div([
            html.Div([
                html.Div([
                    html.H6(id='wordcloud-title', style={
                        'textAlign': 'center',
                        'color': 'black',
                        'fontSize': '16px',
                        'padding': '0px',
                        'background': 'white',
                        'borderRadius': '5px',
                        'margin': '10px 0',
                    })
                ], style={
                    'textAlign': 'center',
                }),

                html.Img(id='wordcloud_image', style={'width': '430px', 'height': '480px'})
            ], className="create_container twelve columns"),
        ], className="row flex-display"),
        html.Div([
            dcc.Graph(id='pie_chart', config={'displayModeBar': 'hover'}),
        ], className="create_container four columns"),
    ], className="row flex-display", style={'marginTop': '0'}),

    # Interval component and dummy div for updating data
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0
    ),
    html.Div(id='dummy-div', style={'display': 'none'})

], id="mainContainer", style={"display": "flex", "flex-direction": "column"})

# Load initial data
df = load_data()

# Calculate initial total reviews and sentiment counts
total_reviews = len(df)
total_positive = len(df[df['review_category'] == 'positive'])
total_negative = len(df[df['review_category'] == 'negative'])
total_neutral = len(df[df['review_category'] == 'neutral'])


# Callback to update book details based on data changes
@app.callback(
    [Output("book-name", "children"),
     Output("plot-summary", "children"),
     Output("total_positive_gauge", "figure"),
     Output("total_negative_gauge", "figure"),
     Output("total_neutral_gauge", "figure")],
    [Input("w_countries", "value")]
)
def update_book_details(selected_sentiment):
    global total_positive, total_negative, total_neutral
    # Extract book name and plot summary based on selected sentiment
    book_name = df[df['review_category'] == selected_sentiment]["book_name"].iloc[0].title()
    plot_summary = df[df['review_category'] == selected_sentiment]["plot_summary"].iloc[0]

    # Calculate sentiment counts based on selected sentiment
    total_positive = len(df[df['review_category'] == 'positive'])
    total_negative = len(df[df['review_category'] == 'negative'])
    total_neutral = len(df[df['review_category'] == 'neutral'])

    # Update gauge figures based on new sentiment counts
    positive_figure = {
        'data': [{
            'type': 'indicator',
            'mode': 'gauge+number',
            'value': round(total_positive / total_reviews * 100, 2),
            'gauge': {
                'axis': {'range': [None, 100]},
                'bar': {'color': 'blue'},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': 'gray',
                'steps': [
                    {'range': [0, 25], 'color': 'lightgray'},
                    {'range': [25, 50], 'color': 'gray'},
                    {'range': [50, 75], 'color': 'lightgray'},
                    {'range': [75, 100], 'color': 'gray'}
                ]
            }
        }],
        'layout': {
            'autosize': True,
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'white'},
            'margin': {'l': 30, 'r': 30, 'b': 25, 't': 25}
        }
    }

    negative_figure = {
        'data': [{
            'type': 'indicator',
            'mode': 'gauge+number',
            'value': round(total_negative / total_reviews * 100, 2),
            'gauge': {
                'axis': {'range': [None, 100]},
                'bar': {'color': 'blue'},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': 'gray',
                'steps': [
                    {'range': [0, 25], 'color': 'lightgray'},
                    {'range': [25, 50], 'color': 'gray'},
                    {'range': [50, 75], 'color': 'lightgray'},
                    {'range': [75, 100], 'color': 'gray'}
                ]
            }
        }],
        'layout': {
            'autosize': True,
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'white'},
            'margin': {'l': 30, 'r': 30, 'b': 25, 't': 25}
        }
    }

    neutral_figure = {
        'data': [{
            'type': 'indicator',
            'mode': 'gauge+number',
            'value': round(total_neutral / total_reviews * 100, 2),
            'gauge': {
                'axis': {'range': [None, 100]},
                'bar': {'color': 'blue'},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': 'gray',
                'steps': [
                    {'range': [0, 25], 'color': 'lightgray'},
                    {'range': [25, 50], 'color': 'gray'},
                    {'range': [50, 75], 'color': 'lightgray'},
                    {'range': [75, 100], 'color': 'gray'}
                ]
            }
        }],
        'layout': {
            'autosize': True,
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'white'},
            'margin': {'l': 30, 'r': 30, 'b': 25, 't': 25}
        }
    }

    return book_name, plot_summary, positive_figure, negative_figure, neutral_figure

# Callback to update pie chart based on dropdown selection
@app.callback(
    Output('pie_chart', 'figure'),
    [Input('w_countries', 'value')]
)
def update_graph(w_countries):
    sentiment_counts = df['review_category'].value_counts(normalize=True) * 100  # Calculate percentages
    colors = ['orange', '#dd1e35', 'green']
    return {
        'data': [go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values,
                        marker=dict(colors=colors), hoverinfo='label+percent',
                        textinfo='label+percent', textfont=dict(size=13), hole=.7, rotation=45)],
        'layout': go.Layout(plot_bgcolor='#000000', paper_bgcolor='#000000', hovermode='closest',
                            title={'text': 'Total Review Sentiments', 'y': 0.93, 'x': 0.5,
                                   'xanchor': 'center', 'yanchor': 'top'},
                            titlefont={'color': 'white', 'size': 20},
                            legend={'orientation': 'h', 'bgcolor': '#000000',
                                    'xanchor': 'center', 'x': 0.5, 'y': -0.07},
                            font=dict(family="Bahnschrift SemiBold Condensed", size=12, color='rgb(146, 208, 80)'))
    }

# Callback to update word cloud based on dropdown selection
@app.callback(
    Output('wordcloud_image', 'src'),
    [Input('w_countries', 'value')]
)
def update_wordcloud(selected_sentiment):
    # Filter the DataFrame based on the selected sentiment category
    filtered_df = df[df['review_category'] == selected_sentiment]
    if filtered_df.empty:
        return None
    else:
        # Extract noun phrases from the filtered DataFrame
        noun_phrases = ' '.join(filtered_df['noun_phrases'])
        # Generate the word cloud image
        wordcloud_img = create_word_cloud(noun_phrases)
        # Convert the word cloud image to a data URI format for displaying in HTML
        wordcloud_data_uri = base64.b64encode(wordcloud_img).decode('utf-8')
        return f'data:image/png;base64,{wordcloud_data_uri}'

# Callback to update word cloud title based on dropdown selection
@app.callback(
    Output('wordcloud-title', 'children'),
    [Input('w_countries', 'value')]
)
def update_wordcloud_title(selected_sentiment):
    if selected_sentiment == 'positive':
        return "Positive Insights"
    elif selected_sentiment == 'negative':
        return "Negative Insights"
    else:
        return "Sentiment Insights"

# Update data every 60 seconds
@app.callback(
    Output('dummy-div', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_data(n):
    global df
    df = load_data()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

