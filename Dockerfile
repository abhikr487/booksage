FROM python
WORKDIR /app
COPY . /app
#RUN pip3 install -r requirements.txt
RUN pip3 install beautifulsoup4
RUN pip3 install blis
RUN pip3 install bs4
RUN pip3 install catalogue
RUN pip3 install certifi
RUN pip3 install charset-normalizer
RUN pip3 install click
RUN pip3 install colorama
RUN pip3 install confection
RUN pip3 install contextvars
RUN pip3 install cycler
RUN pip3 install cymem
RUN pip3 install dash
RUN pip3 install dash-core-components
RUN pip3 install dash-html-components
RUN pip3 install dash-table
RUN pip3 install dataclasses
RUN pip3 install Flask
RUN pip3 install idna
RUN pip3 install immutables
RUN pip3 install importlib-metadata
RUN pip3 install importlib-resources
RUN pip3 install itsdangerous
RUN pip3 install Jinja2
RUN pip3 install joblib
RUN pip3 install kiwisolver
RUN pip3 install langcodes
RUN pip3 install MarkupSafe
RUN pip3 install matplotlib
RUN pip3 install murmurhash
RUN pip3 install nltk
RUN pip3 install numpy
RUN pip3 install packaging
RUN pip3 install pandas
RUN pip3 install Pillow
RUN pip3 install plotly
RUN pip3 install preshed
RUN pip3 install pydantic
RUN pip3 install pyparsing
RUN pip3 install python-dateutil
RUN pip3 install pytz
RUN pip3 install regex
RUN pip3 install requests
RUN pip3 install retrying
RUN pip3 install scikit-learn
RUN pip3 install scipy
RUN pip3 install six
RUN pip3 install smart-open
RUN pip3 install soupsieve
RUN pip3 install spacy
RUN pip3 install spacy-legacy
RUN pip3 install spacy-loggers
RUN pip3 install srsly
RUN pip3 install tenacity
RUN pip3 install thinc
RUN pip3 install threadpoolctl
RUN pip3 install tqdm
RUN pip3 install typer
RUN pip3 install typing_extensions
RUN pip3 install urllib3
RUN pip3 install vaderSentiment
RUN pip3 install wasabi
RUN pip3 install Werkzeug
#RUN pip3 install wordcloud==1.8.0
RUN pip3 install wordcloud
RUN pip3 install zipp
RUN wget https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.6.0/en_core_web_sm-3.6.0-py3-none-any.whl
#RUN pip3 install en_core_web_sm-3.6.0-py3-none-any.whl
RUN python3 -m spacy download en_core_web_sm



# Special case for package from URL
#RUN pip3 install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.6.0/en_core_web_sm-3.6.0-py3-none-any.whl
CMD ["python3", "booksage_dashboard.py", "--host", "0.0.0.0"]
