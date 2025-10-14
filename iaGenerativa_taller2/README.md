# iaGenerativa_taller2 Documentation

## Project Overview
The `iaGenerativa_taller2` project is designed to process various document formats (PDF, TXT, and Excel) and generate embeddings for the content, which are then stored in Pinecone for efficient retrieval and search capabilities.

## File Structure
```
iaGenerativa_taller2
├── src
│   ├── main2.py          # Main script for processing documents
│   ├── utils.py          # Utility functions for the project
│   └── readers
│       ├── pdf_reader.py # Functions for reading PDF files
│       ├── txt_reader.py # Functions for reading TXT files
│       └── excel_reader.py # Functions for reading Excel files
├── requirements.txt      # List of dependencies
├── pyproject.toml       # Project configuration
├── .env                  # Environment variables (e.g., API keys)
├── .gitignore            # Files and directories to ignore in Git
└── README.md             # Project documentation
```

## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd iaGenerativa_taller2
   ```

2. **Create a Virtual Environment**
   ```bash
   uv venv
   ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

5. **Set Environment Variables**
   - Create a `.env` file in the root directory and add your API keys:
     ```
     JINA_API_KEY="your_jina_api_key"
     PINECONE_API_KEY="your_pinecone_api_key"
     ```

## Usage
To process a document, run the main script with the desired file path:
```bash
uv run src/main2.py
```
Make sure to modify the `ruta_documento` variable in `main2.py` to point to the document you want to process.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.