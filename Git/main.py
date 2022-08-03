from Capstone import create_app

#run web server
app = create_app()
if __name__ == '__main__':
    
    app.run(debug=True)