import dash
from dash.dependencies import Input, Output, State
#import dash_core_components as dcc
#import dash_html_components as html
from dash import dash_table,html,dcc
import pandas as pd
import subprocess
from scrapers import get_booklist_from_query, get_reviews_from_book
from analysis import analyze_reviews  # Make sure this import works correctly

header = {
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        'accept-language': 'en-GB,en;q=0.9',
    }

MAX_BOOK = 20

MAX_REVIEWS = 100

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Other components of app.layout
analysis_results_container = html.Div(id="analysis-results")
run_dashboard_button = html.Button('Run Dashboard', id='run-dashboard-button', n_clicks=0, style={'display': 'none'})
dashboard_instructions_container = html.Div(id='dashboard-instructions-container')

app.layout = html.Div([
    html.Img(
            src='/assets/booksage_logo.png',  
            style={"height": "180px", "width": "auto", "align": "center", 'marginTop': '20px', 'marginLeft': '80px', 'marginRight': 'auto'}
        ),
    html.Div([
        html.H1("Book Search 📖", style={'color': '#f2f2f2', 'textAlign': 'center'}),
        dcc.Input(
            id="query-input",
            type="text",
            placeholder="Enter your query",
            style={'color': '#000000', 'backgroundColor': '#ffffff', 'border': 'none', 'padding': '10px', 'borderRadius': '12px', 'margin': '10px 0', 'width': '50%'}
        ),
        html.Button(
            "Search",
            id="search-button",
            n_clicks=0,
            style={'backgroundColor': '#0E8D32', 'borderRadius': '12px', 'color': '#ffffff', 'border': '20', 'padding': '10px 20px', 'margin-left': '10px', 'lineHeight': '20px'}
        ),
    ],
    style={
        'border': '4px solid #f2f2f2',
        'padding': '20px',
        'marginTop': '70px', 
        'marginBottom': '20px',
        'borderRadius': '12px',
        'boxShadow': '0px 4px 8px rgba(0,0,0,0.1)',
        'textAlign': 'center',
        'width': '70%',
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'backgroundColor': 'rgba(0, 0, 0, 0.4)',
    }),    
    html.Div(id="book-table-container"),
    dcc.Store(id='store-book-data'),
    html.Div(id="book-details-container"),
    analysis_results_container,
    run_dashboard_button,
    dashboard_instructions_container,
])

@app.callback(
    [Output("book-table-container", "children"),
     Output("store-book-data", "data")],
    [Input("search-button", "n_clicks")],
    [State("query-input", "value")]
)
def update_book_table(n_clicks, query):
    if n_clicks > 0:
        book_names, book_links, book_plots = get_booklist_from_query(query, header, MAX_BOOK)
        
        if book_names:
            df = pd.DataFrame({
                "Book Name": book_names,
                "Plot Summary": book_plots
            })
            
            table = dash_table.DataTable(
                id='book-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                row_selectable='single',
                selected_rows=[],
                style_cell={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '100px', 'width': '100px', 'maxWidth': '150px',
                },
                style_table={
                    'maxWidth': '100%',
                    'overflowX': 'auto'
                },
                style_data={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                }
            )
            
            return table, book_links
        else:
            return html.P("No books found for the given query."), {}
    else:
        return html.P("Please enter a query and click search.", 
                               style={'textAlign': 'center', 'color': 'white'}), {}
  

@app.callback(
    Output("book-details-container", "children"),
    [Input("book-table", "selected_rows")],
    [State("store-book-data", "data")]
)
def display_book_details(selected_row_indices, book_links):
    if selected_row_indices:
        
        selected_book_link = book_links[selected_row_indices[0]]
        plot_summary, reviews_df = get_reviews_from_book(selected_book_link, header, MAX_REVIEWS)

        plot_summary_text = html.P(plot_summary)

        reviews_table = dash_table.DataTable(
            id='reviews-table',
            columns=[{"name": i, "id": i} for i in reviews_df.columns],
            data=reviews_df.to_dict('records'),
            style_cell={
                'maxWidth': '150px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'whiteSpace': 'normal'
            },
            style_table={'overflowX': 'auto'}
        )

        analysis_button = html.Button("Analyze Reviews", id="analyze-button", n_clicks=0)
        analysis_results_container = html.Div(id="analysis-results")

        return [html.H3("Plot Summary"), plot_summary_text, 
                html.H3("Reviews"), reviews_table, analysis_button, analysis_results_container]
    else:
        return []
    

# Include callbacks and other app setup as in the original app.py

@app.callback(
    [Output("analysis-results", "children"),
     Output("run-dashboard-button", "style")],  # Add output to control button style
    [Input("analyze-button", "n_clicks")],
    [State("reviews-table", "data")]
)
def update_analysis_results(n_clicks, reviews_data):
    if n_clicks > 0 and reviews_data:
        df = pd.DataFrame(reviews_data)
        analyzed_df = analyze_reviews(df)
        analyzed_df.to_csv("results_1.csv",index=False)
        # Display the "Run Dashboard" button by setting its style to block
        return html.Div("Analysis completed. Results are written to results_1.csv."), {'display': 'block'}
    return html.Div("No data to analyze or button not clicked yet."), {'display': 'none'}


# Rest of the app.py code remains unchanged


html.Button('Run Dashboard', id='run-dashboard-button', n_clicks=0),
html.Div(id='dashboard-instructions-container')



@app.callback(
    Output('dashboard-instructions-container', 'children'),
    [Input('run-dashboard-button', 'n_clicks')]
)
def show_dashboard_instructions(n_clicks):
    if n_clicks > 0:
        subprocess.Popen(['python', 'booksage_dashboard.py'])
        # Replace the URL with the actual URL where your booksage_dashboard1.py is accessible
        dashboard_url = 'http://localhost:8051'
        return html.Div([
            html.P("The dashboard is now ready to be viewed."),
            html.A("Click here to access the dashboard", href=dashboard_url, target="_blank")
        ])
    return ''








if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
