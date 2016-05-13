# RSSGrab

This project uses Python 3.5.1 and the Git Flow branching model.
Instructions on how to install git flow can be found [here](https://github.com/nvie/gitflow/wiki/Installation)


## Setup Dev Environment

1. Checkout project via git
2. [Install Anaconda](http://docs.continuum.io/anaconda/install) 
2. Create a new environment using anaconda and the environment.yml

    ```conda env create -f environment.yml``` 
    
3. Activate your the environment

    ```source activate rssgrab```
    
5. Start the backend

    ```python server.py```

6. Start the client

    1. If you haven't done so already
        * [Install node.js](https://nodejs.org/en/download/package-manager/)

    2. Switch directory
     
        ```cd client```
    
    3. Install npm modules:
    
        ```npm install```
    
    4. Install bower dependencies
        
        ```bower install```
        
    2. Start the client 
        
        ```gulp serve```
    
    The client application is located under client/app

## Update conda environment

To update the currently active conda environment simply execute:
    
    conda env update
    
## Links and useful resources
- [Designing a RESTful API with Python and Flask](http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)
- [Anaconda Documentation](http://conda.pydata.org/docs/using/index.html)
- [Documentation Flask-CORS](https://flask-cors.readthedocs.org/en/latest/)
- [Documentation for requests lib](http://docs.python-requests.org/en/latest/)
- [Documentation Advanced Python Scheduler](http://apscheduler.readthedocs.org/en/3.0/)
- [GIT Workflow Tutorial](https://www.atlassian.com/git/tutorials/comparing-workflows)
