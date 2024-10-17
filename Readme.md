# Carscan - Market

## Description
This project is a Python-based application that utilizes pip for package management. The primary goal of this project is control the number of cars which go and out from main market in Nukus. The application is designed to count the number of cars, calculate daily reports, and export data to an Excel file.
## Features
- Count Cars: Clearly count the number of cars.
- Daily Report: Calculate each day's daily report.
- Export Data: Export data to an Excel file.
- Image Compression: Compress uploaded images. 
- Delete Unknown Cars: Remove unknown car images and their database entries.

## Installation
To install the necessary dependencies, run the following command:

### Prepare the Environment
1. Clone the repository:
    ```bash
    git clone https://github.com/batirniyaz/carscan-market.git
    ```
2. Set up a virtual environment:
    ```bash
    python3 -m venv venv
    ```
3. Activate the virtual environment:
   - Linux:
    ```bash
    source venv/bin/activate
    ```
    - Windows:
     ```bash
    venv\Scripts\activate
    ```
4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Refactor the `.env-example` file to `.env` and set the necessary environment variables.

### Run the Application
To run the application, use the following command:
1. Run the application:
    ```bash
    uvicorn app.main:app --host 1.1.1.1 --port 1111 --reload
    ```
2. Open the browser and navigate to `http://1.1.1.1:1111`.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- [Batirniyaz Muratbaev](https://www.github.com/batirniyaz): Python Developer

# Thank you for using my application!

