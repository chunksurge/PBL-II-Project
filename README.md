# PDF Data Extractor

The **PDF Data Extractor** is a web application designed to extract tabular data from PDF files, store the data in a temporary SQLite database, and export the results as DOCX files.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **PDF Upload:** Upload academic record PDFs which contain tables of data.
- **Background Processing:** Processes the PDF in a background thread to extract tables.
- **Data Extraction:** Cleans and extracts table rows using regex-based filters.
- **Storage:** Saves the extracted data into a temporary SQLite database.
- **Data Export:** Allows users to select specific courses/columns and export the data as a DOCX file.
- **Responsive UI:** Updates the user on the upload and processing progress in real-time.

## Technologies Used

- **Backend:**
  - Python with Flask for managing web routes.
  - `pdfplumber` for PDF text extraction.
  - `sqlite-utils` for database operations.
  - `python-docx` for DOCX file generation.
- **Frontend:**
  - HTML, CSS, JavaScript for building the user interface.
- **Other Tools:**
  - Temporary file and directory management using Python’s `os` module.

## Project Structure

```
PBL-II-Project/
├── app.py                  # Main Flask application handling routes and file uploads.
├── utils.py                # Utility functions for PDF extraction, database initialization, and DOCX export.
├── static/
│   ├── css/                # CSS files for styling.
│   └── js/
│       ├── index.js        # Handles file upload UI and progress.
│       └── file.js         # Handles DOCX export and additional page interactions.
├── templates/              # HTML templates for the application.
├── temp/                   # Temporary directories for storing databases and DOCX files.
│   ├── database/
│   └── docx/
├── requirements.txt        # Python dependencies.
└── README.md               # Project documentation.
```

## Setup and Installation

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd PBL-II-Project
   ```

2. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   Make sure you have [pip](https://pip.pypa.io/en/stable/) installed.
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables (Optional):**
   If using a production configuration, set the appropriate Flask environment variables:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development  # For local development
   ```

5. **Run the Application:**
   ```bash
   flask run
   ```
   Then, navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Usage

1. **Upload PDF:**
   - Click on the upload card to select a PDF file.
   - The file upload progress and PDF processing progress are indicated in real-time.

2. **Select Courses and Export:**
   - After processing, select desired course columns.
   - Click the export button to generate a DOCX file with the extracted data.

3. **Download DOCX:**
   - Upon completion, your DOCX file will be automatically downloaded.

## Contributing

Your contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with clear messages.
4. Submit a pull request describing your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
