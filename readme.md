**Please note this is not an official Twilio supported application.**\
**This application does not come with any warranties. You may use this application at your own risk.** 

## Intro
Use this app to import your studio logs into Elasticsearch and display using Kibana. 

Running this application requires Elasticsearch, Kibana and Python3.7. You may either download and install these required software yourself or you can run the entire stack in a Docker container running this stack in an Ubuntu environment.  

## Installation
#### Option 1: Docker
Instructions on downloading and intalling the Docker image are at: https://hub.docker.com/r/khurananick/twilio_studio_logs_pyapp

**Note**: After installing the docker image, skip to [Dashboard Setup](https://github.com/khurananick/TwilioStudioExecutionLogImport#dashboard-setup) below. 

#### Option 2: Manual Install
Use this option if you would prefer to not download an Ubuntu VM and run the individual services natively. \

**Step 1:** Ensure Elasticsearch and Kibana are installed an running on your machine. For mac users, download and install with:

- `brew install elasticsearch-full` or your preferred download method.
- `brew install kibana-full`  or your preferred download method.

Once installed, make sure the services are running:

- `brew services start elasticsearch-full`
- `brew services start kibana-full`

Confirm both services are running.

- **Elastisearch** defaults to: `localhost:9200`\
- **Kibana** defaults to: `localhost:5601`

**Step 2:** Clone this repo to your machine and `cd` into directoy.

**Step 3:** Create a .env file and add `ACCOUNT_SID` and `AUTH_TOKEN` from your Twilio account.

**Step 4:** Run `pip3 install -r requirements.txt` to download required libs.

**Step 5:** Go to `localhost:5601` and you will be taken to the kibana home page. Follow these steps:
1. Click on the Settings icon.
2. Click on "Saved Objects" under Kibana.
3. Click on Import.
4. Import the file in this repo at `assets/export.ndjson`
<p align="center"><img src="./screenshots/kibana-import.png?raw=true" width="650px" /></p>

**If successful, you will see these items listed:**

<p align="center"><img src="./screenshots/kibana-import-sucess.png?raw=true" width="650px" /></p>

## Dashboard Setup
1. Go to your kibana home page. For docker it's probably `localhost:8888` and for manual install it's probably `localhost:5601`. You will be greeted with the page below. Click the Dashboard icon to continue.
<p align="center"><img src="./screenshots/kibana-home-annotated.png?raw=true" width="650px" /></p>

2. Select STUDIO FLOW LIVE VIEW or AUTOPILOT LIVE VIEW.

<p align="center"><img src="./screenshots/kibana-dashboard-list.png?raw=true" width="650px" /></p>

3. Set up your dashboard to show the last 5 minutes of data, and refresh every 5 seconds. See the 5 steps listed below: 

<p align="center"><img src="./screenshots/kibana-dashboard-settings.png?raw=true" width="650px" /></p>

**Click Start and then Apply**

4. If you haven't already, run the python task to start importing your Studio Log data with `./start {FLOW_SID}` or `./start {AUTOPILOT_SID}` and start calling your studio flow or autopilot queries, then you can start seeing the data in your dashboard screen:

<p align="center"><img src="./screenshots/kibana-dashboard.png?raw=true" width="650px" /></p>

## How To Test
**Testing Requirements**
- This library will test against data in your Twilio project for which you enter your credentails into the secret.py file.
- Make sure you have run your flow at least once within the last 24 hours for this test to work.
- Once you have created a flow and ran it at least once, copy the SID of your flow and run the test as follows: 
`python3 test.py {FLOW_SID}`

## How To Run

`./start {FLOW_SID}` or `./start {AUTOPILOT_SID}`
- This will start the import.

## Setting Searchable Filter Variables

You can add data to your studio flow that can be later used in Kibana to filter down your graphs. To set filters:

1. Add a function to your Studio flow with the name `GET_REPORTING_FILTERS`
2. Make sure your function returns a json response in the format example: `{gender: "Male", occupation: "Nurse"}` - you can track any number of variables you'd like, just be sure that your json object is formatted as shown above.

<p align="center"><img src="./screenshots/kibana-tracking-variabls.png?raw=true" width="650px" /></p>

## Filtering By Variables

You can filter down your graphs to only display data that matches your filter variables. 

<p align="center"><img src="./screenshots/kibana-filtering-variables.png?raw=true" width="650px" /></p>
