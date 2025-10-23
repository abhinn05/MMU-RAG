## Running the Project 🚀

Follow these steps to run the RAG API server and test it.

1.  **Install Dependencies:**
    Make sure you have Python 3.9+ installed. Open your terminal in the project's root directory and run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the API Server:**
    Run the `app.py` script to start the FastAPI server. It will listen on `http://localhost:5010`.
    ```bash
    python app.py
    ```
    **Leave this terminal running.** The server needs to be active to receive requests.

3.  **Test the `/run` Endpoint (in a New Terminal):**
    Open a **second terminal** window in the same project directory. Use the following PowerShell command to send a question to the `/run` endpoint:
    ```powershell
    # Assign the server's response to the $response variable
    $response = Invoke-WebRequest -Uri "http://localhost:5010/run" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{ "question": "What is Machine Learning?" }'
    
    ```
    * **Note:** Replace `"What is Machine Learning?"` with any question you want to test.
    * This command sequence sends the question and then prints the full streaming response, showing intermediate steps and the final answer.
