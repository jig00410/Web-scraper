# Web Scrape

## Project Overview

**Web Scrape** is a web application that extracts useful information from websites. It allows users to enter a website URL and retrieve specific data in a clean and organized format.

Built using **Streamlit** and **Playwright**, the system processes web content efficiently and presents the extracted data in a user-friendly way.

## Project Objective

The main objective of this project is to:

* Automate the process of collecting data from websites
* Extract only the required information
* Present structured and clean output to the user
* Provide a simple and interactive web interface

## Features

* User-friendly web interface
* URL-based data extraction
* Dynamic website support (JavaScript-rendered pages)
* Selective data extraction logic
* Clean and structured output display

## Tech Stack

* **Frontend \& UI:** Streamlit
* **Web Automation \& Scraping:** Playwright
* **Backend Logic:** Python
* **Optional Processing:** HTML filtering \& structured parsing

## How to Run the Project

Follow the steps below to run the Web Scrape application on your local machine.

### 1️⃣ Clone the Repository

```bash
git clone <your-forked-repository-url>
cd web-scrape
```

### 2️⃣ Create a Virtual Environment

It is recommended to create a virtual environment before installing dependencies.

#### For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### For Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Required Dependencies

```bash
pip install -r requirements.txt
```

If you are using Playwright for the first time, install the required browser drivers:

```bash
playwright install
```

### 4️⃣ Configure Environment Variables

Create a .env file in the root directory of the project and add the required keys.

Example:

```sh
OPENAI_API_KEY=your_api_key_here
```

Add any other required environment variables as needed.

### 5️⃣ Run the Application

Start the Streamlit application using the command below:

```bash
streamlit run app/main.py
```
