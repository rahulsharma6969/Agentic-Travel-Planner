# MCP Based Multi-Agent Travel Planner

This project is a multi-agent travel planner that uses the MCP (Model Context Protocol) to coordinate multiple agents in planning a trip. The agents can search for flights, hotels, and attractions to create ane engaging itinerary for the user.

## Features
- Multi-agent coordination using MCP
- Search for flights, hotels, and attractions
- Gradio interface for user interaction

## Requirements
- Python 3.10 or higher
- Required Python packages listed in `requirements.txt`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/aatifahmad123/mercer-mettl-hackathon.git
   cd mercer-mettl-hackathon
    ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv myenv
   source myenv/bin/activate  
   ```
   or on Windows:
   ```bash
   myenv\Scripts\activate
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   
3. Set up the environment variables for API keys. Make sure you have a Google API Key and set it in a .env file. A sample `.env` file might look like this:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. Run the application:
   ```bash
   python app.py
   ```
## Usage
- Open the Gradio interface in your web browser.
- Input your travel deatils like destination, dates and budget.
- The agents will coordinate to provide you with the best travel options.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
