# Facebook large page to page network

This project is built for the "social media analytics" course in our masters program in computer science.

## Project discription
Analysing the network and getting communities in the data using our implementation for Louvain algourithm for detecting communities.


## Branch Trials
    |__code.
    |   |__ Data_Redution.py
    |   |__ Graph_Exploration.py
    |   |__ Louvain_algo.py
    |   |__ utils.py
    |
    |__ Data.
    |   |__ musae_facebook_edges.csv
    |   |__ musae_facebook_target.csv
    |   |__ nodes_with_all_communities.csv
    |
    | __Images.
    |   |__ Different images and graphs for the report.
    |
    |__ some visuals.
    |    |__Sigma export folders for different graph visualizations.
    |
    |__ requirements.txt

## How to install
We tried the project on python 3.9 and 3.10. The requirements.txt is with python 3.10.12.
1. **Clone the repository**:
    ```bash
    git clone https://github.com/Arefay97/Social-Media-Analytics---Project
    ```
2. **Navigate to the project directory**:
    ```bash
    cd Social-Media-Analytics---Project
    ```
3. **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```
4. **Activate the virtual environment**:
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
5. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
## How to use
* If you want to run the main part, there is the main.py in the code folder. 
It performs some of the preprocessing, creates the graph and performs the Louvain algorithm.
At the end of it is the part of loading it into neo4j. 
For this a neo4j account is necessary and the you have to have URI, username and password read.
* Examples on how to apply the louvain algorithms is in apply_louvain.ipynb.
* The functions for graph exploration and reduction can be found in the other python files in code.
* The figures from in the report are produced in the jupyter-notebooks.
* The data musae_facebook is the original data.
* The file nodes_with_all_communities.csv contains results, every node with its community indexes for different algorithms.


