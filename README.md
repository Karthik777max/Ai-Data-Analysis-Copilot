# AI Data Analyst Copilot

An AI-powered data analysis assistant that helps users explore datasets,
run common analyses, visualize relationships, and understand results
through natural-language explanations.

The goal is to combine **reliable Python-based analytics** with an
**LLM-powered explanation layer**: Python and established data-science
libraries perform calculations, while the language model helps interpret
results and answer questions in plain English.

> **Project status:** MVP / active development. Features and setup
> details may evolve as the application is expanded.

## Table of Contents

-   [Overview](#overview)
-   [Problem Statement](#problem-statement)
-   [Goals](#goals)
-   [Features](#features)
-   [System Architecture](#system-architecture)
-   [Analysis Workflow](#analysis-workflow)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Getting Started](#getting-started)
-   [Using the Copilot](#using-the-copilot)
-   [Example Use Case](#example-use-case)
-   [Reliability and Data Handling](#reliability-and-data-handling)
-   [Roadmap](#roadmap)
-   [Contributing](#contributing)
-   [Troubleshooting](#troubleshooting)
-   [License](#license)

## Overview

Data analysis often requires switching between spreadsheets, Python
scripts, visualization tools, and documentation. The **AI Data Analyst
Copilot** aims to bring common analysis tasks into one accessible
workflow.

Users can upload a dataset, inspect its structure, review data quality,
visualize relationships between columns, run basic statistical or
machine-learning analysis, and ask an LLM to explain the output.

### Core principle

**The LLM explains; Python calculates.** Numerical results such as
regression metrics, descriptive statistics, and missing-value counts
should be computed using data-processing libraries. The LLM can then
explain those computed results, subject to the context and limitations
of the model.

## Problem Statement

People who are new to data analytics may find it difficult to:

-   Understand an unfamiliar dataset quickly.
-   Detect missing values, duplicate records, or columns that need
    cleaning.
-   Choose an appropriate analysis or visualization.
-   Interpret statistics and model evaluation metrics.
-   Turn analytical output into understandable insights.

This project aims to reduce that friction with a simple interface and
conversational assistance.

## Goals

-   Make exploratory data analysis easier to access.
-   Provide a clear preview and summary of uploaded data.
-   Support common cleaning and analysis tasks.
-   Visualize relationships between numerical variables.
-   Explain results in natural language using an LLM API.
-   Keep calculations transparent and reproducible where possible.
-   Build a modular foundation for future analytical capabilities.

## Features

The MVP is designed around the following capabilities. Exact
availability depends on the current application implementation.

  -----------------------------------------------------------------------
  Area                                Capability
  ----------------------------------- -----------------------------------
  Data input                          Upload CSV and Excel (`.xlsx`)
                                      files

  Data preview                        Inspect rows, columns, and dataset
                                      dimensions

  Data quality                        Review missing values, duplicates,
                                      and empty columns

  Basic cleaning                      Apply simple, inspectable
                                      preprocessing operations

  Descriptive analysis                Generate summary statistics for
                                      numeric columns

  Visualization                       Plot relationships between selected
                                      numeric columns

  Regression                          Fit a basic linear regression and
                                      show evaluation metrics

  AI assistance                       Ask questions and receive
                                      explanations of analytical results
  -----------------------------------------------------------------------

## System Architecture

The architecture separates the user interface, data processing,
analytical calculations, and LLM assistance. This helps keep computed
results separate from generated explanations.

``` mermaid
flowchart TD
    U[User] --> UI[Streamlit Interface]
    UI --> UP[Upload CSV or Excel]
    UP --> DL[Load Data with Pandas]
    DL --> QA[Data Quality Checks]
    QA --> PRE[Preprocessing]
    PRE --> ANA[Analytics Engine]
    PRE --> VIZ[Visualization Engine]
    ANA --> RES[Computed Results]
    VIZ --> CHARTS[Charts and Plots]
    RES --> CTX[Analysis Context]
    CHARTS --> UI
    RES --> UI
    CTX --> LLM[LLM API]
    Q[User Question] --> LLM
    LLM --> EX[Natural-Language Explanation]
    EX --> UI
```

### Component responsibilities

-   **Streamlit interface:** Displays controls, uploaded data, charts,
    metrics, and chat interactions.
-   **Data loading:** Reads supported files into a Pandas DataFrame.
-   **Preprocessing:** Applies basic cleaning and prepares columns for
    analysis.
-   **Analytics engine:** Uses Python libraries to calculate statistics
    and train supported models.
-   **Visualization engine:** Creates charts from selected columns and
    analytical outputs.
-   **LLM integration:** Uses an LLM API to interpret user questions and
    explain results supplied by the application.

The diagram represents the intended logical design; it does not imply
that every component already exists as a separate Python module.

## Analysis Workflow

``` mermaid
flowchart TD
    A([Start]) --> B[Upload dataset]
    B --> C{File supported?}
    C -- No --> D[Show validation error]
    D --> B
    C -- Yes --> E[Load dataset]
    E --> F[Preview rows and columns]
    F --> G[Inspect data quality]
    G --> H[Choose analysis]
    H --> I[Run Python calculations]
    I --> J[Display metrics and visualizations]
    J --> K[Ask a question]
    K --> L[Send relevant context to LLM]
    L --> M[Display explanation]
    M --> N([End or continue exploring])
```

## Technology Stack

  -----------------------------------------------------------------------
  Technology                          Purpose
  ----------------------------------- -----------------------------------
  Python                              Main application and analytical
                                      logic

  Streamlit                           Interactive web interface

  Pandas                              Loading, transforming, and
                                      summarizing tabular data

  NumPy                               Numerical operations

  Matplotlib / Plotly                 Data visualization, depending on
                                      the implemented chart

  scikit-learn                        Machine-learning models and
                                      evaluation metrics

  LLM API                             Natural-language interpretation and
                                      question answering

  Git and GitHub                      Version control and project
                                      collaboration
  -----------------------------------------------------------------------

SQLite or PostgreSQL may be considered later if the project needs
persistent storage. A database is not required for a basic
upload-and-analyze workflow.

## Project Structure

A minimal repository may look like this:

``` text
Ai-Data-Analysis-Copilot/
├── app.py
├── Requirements.txt
├── .gitignore
├── README.md
├── modules/                 # Optional: add as the app grows
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── analytics.py
│   ├── visualizations.py
│   └── llm_agent.py
├── tests/                   # Optional: automated tests
└── reports/                 # Optional: generated analysis reports
```

The `modules/`, `tests/`, and `reports/` directories are a suggested
organization for future development; create them only when you add the
corresponding code. Keep the dependency filename consistent with the one
in your repository (`Requirements.txt` or `requirements.txt`).

## Getting Started

### 1. Prerequisites

Install the following before running the project:

-   Python 3.10 or a version supported by your installed dependencies.
-   Git.
-   Visual Studio Code or another Python editor.
-   An API key for the LLM provider configured in your application, if
    LLM features are enabled.

### 2. Clone the repository

``` bash
git clone https://github.com/Karthik777max/Ai-Data-Analysis-Copilot.git
cd Ai-Data-Analysis-Copilot
```

### 3. Create a virtual environment

**Windows (PowerShell):**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

``` bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

Use the requirements file that exists in the repository. If its current
name is `Requirements.txt`, run:

``` bash
python -m pip install -r Requirements.txt
```

If you rename it to the conventional lowercase `requirements.txt`, use
that filename instead.

### 5. Configure the LLM API key

Use the environment-variable name expected by your current `app.py` and
LLM provider. For example, if the code reads `OPENAI_API_KEY`, set it in
PowerShell for the current terminal session:

``` powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

For Command Prompt:

``` bat
set OPENAI_API_KEY=your_api_key_here
```

Do not paste API keys into source code, commit them to Git, or include
real keys in screenshots. If the application uses a different provider
or environment-variable name, follow that provider's configuration.

### 6. Run the application

``` bash
streamlit run app.py
```

Streamlit normally prints a local URL in the terminal. Open that URL in
your browser. If the project currently uses a different entry point, run
the command documented in `app.py` or the project configuration.

## Using the Copilot

A typical analysis session follows these steps:

1.  **Launch the app** using Streamlit.
2.  **Upload a CSV or Excel file.**
3.  **Inspect the preview** and confirm that the headers and values were
    loaded correctly.
4.  **Check data quality** for missing values, duplicate records, and
    empty columns.
5.  **Select an analysis**, such as summary statistics, a scatter plot,
    or linear regression.
6.  **Review the output** including the relevant chart or evaluation
    metrics.
7.  **Ask a focused question** about the dataset or computed results.
8.  **Validate important conclusions** against the displayed data and
    metrics before using them in a report or decision.

## Example Use Case

Suppose a user uploads a dataset containing `Advertising_Spend` and
`Sales`.

A simple analysis can:

-   Inspect the two columns and their data types.
-   Check for missing or invalid values.
-   Plot advertising spend against sales.
-   Fit a linear regression model if the data is suitable.
-   Report metrics such as (R\^2), mean absolute error (MAE), and root
    mean squared error (RMSE), where implemented.
-   Ask the Copilot to explain what the coefficient and metrics mean.

Example question:

> "Explain the relationship between advertising spend and sales. What
> does the regression model tell me, and what are its limitations?"

The application should ground the explanation in the computed output
rather than asking the LLM to invent statistics. A relationship in
observational data does not, by itself, prove that advertising caused a
change in sales.

## Reliability and Data Handling

Data quality and trustworthy explanations are important parts of an
analytical tool.

-   **Validate uploads:** Handle unsupported file types, empty files,
    and files that cannot be parsed.
-   **Inspect missing data:** Report missing values and make any
    imputation or row removal explicit.
-   **Preserve the source:** Prefer performing cleaning on a working
    copy so users can compare it with the original.
-   **Check column types:** Confirm that columns used in a calculation
    are numeric and contain usable values.
-   **Handle small datasets:** Warn when there are too few usable rows
    for a meaningful model or evaluation.
-   **Explain metrics:** Present metric names and their meaning, not
    just numbers.
-   **Keep the LLM grounded:** Send only relevant context and computed
    outputs; avoid asking the model to fabricate calculations.
-   **Protect sensitive data:** Do not upload confidential or personally
    identifiable information to an external LLM provider unless you are
    authorized and understand the provider's data-handling terms.
-   **Keep secrets out of Git:** Store API credentials in environment
    variables or a local secrets file excluded by `.gitignore`.

These are recommended engineering practices. Confirm that each safeguard
is implemented before describing it as an enforced feature.

## Roadmap

Potential next steps for the project:

-   [ ] Improve file validation and user-friendly error messages.
-   [ ] Add configurable missing-value and duplicate-handling options.
-   [ ] Expand exploratory data analysis with distributions and
    correlation views.
-   [ ] Support more chart types and clearer chart labels.
-   [ ] Add model selection and comparisons for suitable tasks.
-   [ ] Improve LLM context management and explain how each answer was
    derived.
-   [ ] Add downloadable summaries or analysis reports.
-   [ ] Create unit tests for preprocessing and analytics.
-   [ ] Add example datasets and screenshots to the repository.
-   [ ] Add deployment instructions and a hosted demo.
-   [ ] Consider persistent storage only if the application needs it.

## Contributing

Contributions, bug reports, and suggestions are welcome.

1.  Fork the repository.
2.  Create a branch for your change.
3.  Make a focused change and test it locally.
4.  Commit your work with a clear message.
5.  Open a pull request describing the change and any relevant
    screenshots or test results.

Example Git workflow:

``` bash
git checkout -b feature/your-feature
git add .
git commit -m "Add your feature"
git push -u origin feature/your-feature
```

Before running `git add .`, review `git status` and confirm that API
keys, private datasets, virtual environments, and generated files are
excluded.

## Troubleshooting

  -----------------------------------------------------------------------
  Problem                             Things to check
  ----------------------------------- -----------------------------------
  `streamlit` is not recognized       Activate the virtual environment
                                      and install dependencies from the
                                      requirements file.

  `ModuleNotFoundError`               Confirm the correct environment is
                                      active, then install the missing
                                      dependency.

  API authentication error            Check the provider,
                                      environment-variable name, key
                                      validity, and whether the app can
                                      read the variable.

  CSV or Excel upload fails           Check file format, file integrity,
                                      and column headers.

  Regression fails                    Check that selected columns are
                                      numeric and contain enough valid
                                      rows after cleaning.

  Git push is rejected                Run `git status`, inspect the
                                      branch, and integrate remote
                                      changes carefully before pushing
                                      again.

  App changes do not appear           Save the file and check the
                                      Streamlit terminal for errors;
                                      restart the app if necessary.
  -----------------------------------------------------------------------

## License

No license has been specified here. Before making the repository public
for reuse, choose a license and add a `LICENSE` file. Without a license,
other users generally do not receive explicit permission to reuse,
modify, or redistribute the code.

## Author and Repository

-   **Repository:**
    [Ai-Data-Analysis-Copilot](https://github.com/Karthik777max/Ai-Data-Analysis-Copilot)
-   **Built with:** Python, Streamlit, data-science libraries, and an
    LLM API.

------------------------------------------------------------------------

If you find this project useful, consider starring the repository and
sharing suggestions through GitHub Issues.
