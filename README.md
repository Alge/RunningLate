# RunningLate
Project for TrainHack 2018

## Web frontend
The [Sapper](https://sapper.svelte.technology)-based frontend is found in
`frontend/`. The latest version is available at https://running-late.now.sh/.

## Python backend
The [Flask](http://flask.pocoo.org/)-based backend is found in `backend/`. The latest version is available at https://running-late-be.now.sh/.

##Docker
docker build -t runninglate .
docker run -p 0.0.0.0:5000:5000  runninglate
