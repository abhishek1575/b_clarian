from app import app
# from your_app_package import app
 
if __name__ == '__main__':
    # Bind to all available interfaces (0.0.0.0)
    app.run(debug=True, host='0.0.0.0', port=5000)