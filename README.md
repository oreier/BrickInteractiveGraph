# 📊 Brick Interactive Graph

Brick is an open-source ontology which describes, defines and contextualizes data sources in and around buildings. Brick standardizes semantic description of physical, virtual and logical entities and assets and the relationships between them. Brick facilitates the implementation of self-adapting data-driven software — software which can configure itself to operate in a particular setting — by enabling that software to query its environment and discover relevant data sources.

This is a Python-based web application for visualizing and interacting with graph data structures using keywords and relationships. It provides an interactive UI powered by pyvis and serves the interface in your browser.

## 🚀 How to Download & Run
1. Clone the Repository
To get started, clone the repository using Git:

git clone https://github.com/oreier/brickinteractivegraph.git


2. Running the Application
You have two main options for running the application:

🖥️ Option A: Run from Terminal
Navigate to the cloned repository:

cd /your-file-path-to-the-repo

Run the application with the following command:

uv run ui3.py

⚠️ Make sure you are in the same directory as the ui3.py file when running this command, or you may encounter errors. Also make sure you have install uv - if not read here how to install: https://docs.astral.sh/uv/getting-started/installation/#installation-methods 

💻 Option B: Run from VS Code
Open the project folder in Visual Studio Code.

Install required dependencies by running the following in your terminal:

pip install rdflib pyvis

Click the Run button in VS Code (or press F5).

The application will automatically open in your default web browser, or prompt you to choose a browser.

## 🧭 Application Guide
📁 Setting the Data File
The application uses a data file defined in the config.json file.

To change the data file:

Place your new data file in the same directory as ui3.py.

Open the config.json file and update the filename field with the new file's name:

{
  "rdf_file": "your-file-name-here",
  ...
}

🌐 Configuring Starting Nodes
The graph starts by displaying nodes associated with specific keywords.

To change the starting nodes:

Open config.json.

Update the start_keywords array with your desired node keywords:

{
  ...
  "starting_node_keywords": ["Keyword1", "Keyword2"]
}
This controls which nodes are initially visible and focused when the application loads.

## 📦 Dependencies
The core dependencies for this project are:

rdflib – for handling RDF data

pyvis – for rendering interactive graph visualizations in the browser

## 🛠️ Troubleshooting
If you get a "file not found" error when running ui3.py, double-check that you are in the correct directory.

Ensure all dependencies are installed and that you're using a compatible version of Python (3.7+ recommended).

If the application doesn’t open in the browser, try opening the URL manually or checking your browser settings.
