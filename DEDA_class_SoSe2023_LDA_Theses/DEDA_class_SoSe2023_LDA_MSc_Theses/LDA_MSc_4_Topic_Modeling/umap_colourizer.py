import os
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np
from yellowbrick.text import UMAPVisualizer
from umap.umap_ import UMAP
import umap.plot
#%matplotlib notebook
from bokeh.plotting import show, figure, save, output_notebook, output_file, reset_output
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.io import output_notebook, push_notebook, reset_output
from bokeh.resources import INLINE
output_notebook(resources=INLINE)
import ipywidgets as widgets
from ipywidgets import interact

class UMAPColourizer:
    
    
    def __init__(self, model, words, topics_names, umap_terms_embedding, umap_theses_embedding):
        self.model = model
        self.umap_terms_embedding = umap_terms_embedding
        self.umap_theses_embedding = umap_theses_embedding
        self.words = words.copy()
        
        #calculates the most dominated topic for words
        topics_terms = self.model.state.get_lambda()
        terms_topics_proba = np.apply_along_axis(lambda x: x/x.sum(),1,topics_terms).T
        terms_topics_proba = pd.DataFrame(terms_topics_proba)

        dominant_topic_term = terms_topics_proba.idxmax(axis=1) + 1
        self.dominant_topic_term = dominant_topic_term
        
        self.words['Topic'] = dominant_topic_term
        self.words.columns = ['Term', 'Topic']

        # Create a dictionary to map topic numbers to topic titles
        topic_mapping = {i + 1: topic_title for i, topic_title in enumerate(topics_names)}
        self.topic_mapping = topic_mapping
        self.n_topics = len(self.topic_mapping)
        # Create the "Topic Title" column by mapping the "Topic" column using the topic_mapping dictionary
        self.words['Topic Title'] = self.words['Topic'].map(topic_mapping)
        self.words['Topic Title numbered'] = self.words.apply(lambda row: f"{row['Topic']:02d}: {row['Topic Title']}", axis=1)
    
    
    def colour_term_umap(self):
        reset_output()
        output_notebook(resources=INLINE)
        f = umap.plot.points(self.umap_terms_embedding, labels = self.words['Topic Title numbered'])
        f.set_title('UMAP: {} Terms Colored by Topics'.format(len(self.words)), fontsize = 24)
        plt.savefig('4_UMAP_terms_coloured.png', transparent = True, dpi = 300)
        plt.show()
        plt.close()

        fig = umap.plot.interactive(self.umap_terms_embedding, hover_data = self.words.drop('Topic Title numbered', axis=1),
                                    labels = self.words['Topic Title numbered'], point_size=3)
        show(fig)
        output_file("UMAP words interactive coloured.html")  # Set the output file path
        save(fig)
        push_notebook()
    
    
    def colour_term_umap_subplots(self, rows, columns, figsize_, ):
        # Create a 4x3 grid for subplots
        fig, axes = plt.subplots(rows, columns, figsize=figsize_)

        # Loop through topics
        for topic in range(1, self.n_topics+1):
            specific_term = self.dominant_topic_term == topic
            colormap = specific_term.apply(lambda x: 'blue' if x else 'grey')
            specific_term = specific_term.apply(lambda x: f'Topic {topic}' if x else 'Other topic')

            # Get the subplot position based on the topic number (index starts from 1)
            row = (topic - 1) // 3
            col = (topic - 1) % 3

            # Separate the blue dots and grey dots
            blue_dots = self.umap_terms_embedding.embedding_[colormap == 'blue']
            grey_dots = self.umap_terms_embedding.embedding_[colormap == 'grey']

            # Plot the grey dots with smaller size first
            axes[row, col].scatter(grey_dots[:, 0], grey_dots[:, 1], alpha=0.5, s=10, color='grey', label='Other topic')

            # Plot the blue dots with larger size on top
            axes[row, col].scatter(blue_dots[:, 0], blue_dots[:, 1], alpha=0.5, s=10, color='blue', label=f'Topic {topic}')

            axes[row, col].grid(False)
            axes[row, col].set_title(f'{topic}: {self.topic_mapping[topic]}', fontsize=20)  # Subplot title

            # Remove numbers on both x and y axes
            axes[row, col].set_xticks([])
            axes[row, col].set_yticks([])

        # Set the grand title for the entire plot
        fig.suptitle('UMAP Projection of Words by Most Dominant Topics', fontsize=24)

        plt.tight_layout()
        plt.savefig('5_UMAP_colored_for_each_topic.png', transparent = True, dpi = 300)
        plt.show()
        plt.close()
        
        
    def colour_term_umap_slicer(self):
        reset_output()

        # Call output_notebook to enable inline display
        output_notebook()

        # Create a function for the interactive plot
        @interact(topic=widgets.IntSlider(min=1, max=self.n_topics, step=1, value=1))
        def plot_topic(topic):
            specific_term = self.dominant_topic_term == topic
            colormap = specific_term.apply(lambda x: 'blue' if x else 'grey')
            specific_term = specific_term.apply(lambda x: f'Topic {topic}' if x else 'Other topic')

            # Separate the blue dots and grey dots
            blue_dots = self.umap_terms_embedding.embedding_[colormap == 'blue']
            grey_dots = self.umap_terms_embedding.embedding_[colormap == 'grey']

            # Create a DataFrame for hover data (words DataFrame without 'Topic Title numbered')
            hover_data = self.words.drop('Topic Title numbered', axis=1)

            # Create ColumnDataSources for hover data
            blue_source = ColumnDataSource(data=dict(
                x=blue_dots[:, 0],
                y=blue_dots[:, 1],
                label=specific_term[colormap == 'blue'],
                words=hover_data.loc[colormap == 'blue', 'Term']
            ))
            grey_source = ColumnDataSource(data=dict(
                x=grey_dots[:, 0],
                y=grey_dots[:, 1],
                label=specific_term[colormap == 'grey'],
                words=hover_data.loc[colormap == 'grey', 'Term']
            ))

            # Create a Bokeh figure
            p = figure(plot_width=800, plot_height=600, title=f'{topic}: {self.topic_mapping[topic]}', toolbar_location=None)

            # Plot the grey dots with size 1
            p.scatter('x', 'y', source=grey_source, size=3, color='grey', legend_label='Other topic', alpha=0.5)

            # Plot the blue dots with size 3 on top
            blue_renderer = p.scatter('x', 'y', source=blue_source, size=4, color='blue', legend_label=f'Topic {topic}', alpha=0.7)

            p.grid.visible = False
            p.axis.visible = False

            # Add hover tool to display word on hover for blue dots
            hover_tool = HoverTool(tooltips=[("Word", "@words")], renderers=[blue_renderer])
            p.add_tools(hover_tool)

            # Show the plot inline and update it when the slider is changed
            show(p, notebook_handle=True)
            #output_file(f"UMAP words coloured topic {topic}.html")  # Set the output file path
            #save(p)
            push_notebook()

        # This will create an interactive slider to select the topic
    
    
    def save_colour_term_umap_slicer(self):
        reset_output()

        # Create the folder "UMAP Terms by Topic" if it does not exist
        folder_name = "UMAP Terms by Topic"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)


        for topic in range(1, self.n_topics+1):
            specific_term = self.dominant_topic_term == topic
            colormap = specific_term.apply(lambda x: 'blue' if x else 'grey')
            specific_term = specific_term.apply(lambda x: f'Topic {topic}' if x else 'Other topic')

            # Separate the blue dots and grey dots
            blue_dots = self.umap_terms_embedding.embedding_[colormap == 'blue']
            grey_dots = self.umap_terms_embedding.embedding_[colormap == 'grey']

            # Create a DataFrame for hover data (words DataFrame without 'Topic Title numbered')
            hover_data = self.words.drop('Topic Title numbered', axis=1)

            # Create ColumnDataSources for hover data
            blue_source = ColumnDataSource(data=dict(
                x=blue_dots[:, 0],
                y=blue_dots[:, 1],
                label=specific_term[colormap == 'blue'],
                words=hover_data.loc[colormap == 'blue', 'Term']
            ))
            grey_source = ColumnDataSource(data=dict(
                x=grey_dots[:, 0],
                y=grey_dots[:, 1],
                label=specific_term[colormap == 'grey'],
                words=hover_data.loc[colormap == 'grey', 'Term']
            ))

            # Create a Bokeh figure
            p = figure(plot_width=800, plot_height=600, title=f'{topic}: {self.topic_mapping[topic]}', toolbar_location=None)

            # Plot the grey dots with size 1
            p.scatter('x', 'y', source=grey_source, size=3, color='grey', legend_label='Other topic', alpha=0.5)

            # Plot the blue dots with size 3 on top
            blue_renderer = p.scatter('x', 'y', source=blue_source, size=4, color='blue', legend_label=f'Topic {topic}', alpha=0.7)

            p.grid.visible = False
            p.axis.visible = False

            # Add hover tool to display word on hover for blue dots
            hover_tool = HoverTool(tooltips=[("Word", "@words")], renderers=[blue_renderer])
            p.add_tools(hover_tool)

            # Show the plot inline and update it when the slider is changed
            #show(p, notebook_handle=True)
            output_file(os.path.join(folder_name, f"UMAP words coloured topic {topic}.html"))  # Set the output file path
            save(p)
            push_notebook()

        # HTML content of file that combines all the plots
        html_content = f'''<!DOCTYPE html>
        <html>
        <head>
            <title>UMAP Terms by Topic</title>
            <style>
                body {{
                    font-family: Arial, sans-serif; /* Change font style to Arial */
                }}
                h1 {{
                    margin-bottom: 20px;
                }}
                .iframe-container {{
                    position: relative;
                    overflow: hidden;
                    padding-top: 56.25%; /* 16:9 Aspect Ratio */
                }}
                .iframe-container iframe {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    border: none;
                }}
            </style>
        </head>
        <body>
            <h1>UMAP Terms by Topic</h1>
            <label for="topic_slider">Select Topic:</label>
            <input type="range" id="topic_slider" min="1" max="{self.n_topics}" step="1" value="1">
            <span id="current_topic">Topic 1</span> <!-- Display the current topic number here -->

            <div class="iframe-container">
                <iframe id="topic_iframe" src="UMAP%20Terms%20by%20Topic/UMAP%20words%20coloured%20topic%201.html"></iframe>
            </div>

            <script>
                var slider = document.getElementById("topic_slider");
                var iframe = document.getElementById("topic_iframe");
                var currentTopic = document.getElementById("current_topic"); // Reference to the current topic element

                slider.oninput = function() {{
                    var topic = this.value;
                    currentTopic.textContent = `Topic ${{topic}}`; // Update the displayed topic number
                    iframe.src = `UMAP%20Terms%20by%20Topic/UMAP%20words%20coloured%20topic%20${{topic}}.html`;
                }};
            </script>
        </body>
        </html>
        '''

        # Save the HTML content to a file
        with open('UMAP terms subplots interactive coloured.html', 'w') as file:
            file.write(html_content)
            
            
    def colour_theses_umap(self, corpus, sorted_thesis_info):
        reset_output()
        output_notebook(resources=INLINE)
        
        theta, _ = self.model.inference(corpus)
        theta = pd.DataFrame(theta)

        dominant_topic_doc = theta.idxmax(axis=1) + 1

        len_docs = len(dominant_topic_doc)

        thesis_info_pd = pd.DataFrame(sorted_thesis_info).T
        thesis_info_pd.columns = ['Title', 'Author']

        thesis_info_pd = thesis_info_pd.reset_index()[['Title', 'Author']]
        thesis_info_pd['Topic']  = dominant_topic_doc

        thesis_info_pd = thesis_info_pd.drop_duplicates()
        thesis_info_pd = thesis_info_pd.reset_index(drop=True)

        # Create the "Topic Title" column by mapping the "Topic" column using the topic_mapping dictionary
        thesis_info_pd['Topic Title'] = thesis_info_pd['Topic'].map(self.topic_mapping)
        thesis_info_pd['Topic Title numbered'] = thesis_info_pd.apply(lambda row: f"{row['Topic']:02d}: {row['Topic Title']}", axis=1)

        f = umap.plot.points(self.umap_theses_embedding, labels=thesis_info_pd['Topic Title numbered'], theme = 'blue')
        f.set_title('UMAP: {} MSc Theses colored by Topics'.format(len_docs), fontsize = 24)
        plt.savefig('6_UMAP_theses_coloured.png', transparent = True, dpi = 300)
        plt.show()
        plt.close()

        fig2 = umap.plot.interactive(self.umap_theses_embedding, hover_data = thesis_info_pd[['Title', 'Author', 'Topic', 'Topic Title']], 
                                     labels=thesis_info_pd['Topic Title numbered'],
                                     point_size=9,  theme='blue')
        show(fig2)
        output_file("UMAP theses interactive coloured.html")  # Set the output file path
        save(fig2)
        push_notebook()