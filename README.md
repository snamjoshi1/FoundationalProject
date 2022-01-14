# FoundationalProject
Stock Price Prediction Using Sentiment Analysis
1. Data is scraped using GoogleAPI and Twitter API and sample code can be found in Scraping Code Folder
2. The respective data can be found in DataFiles Folder.This Folder also contains FinalDF file that has the date used for selecting model
3. All the analyzed models are are present in Analyzed Models folder
4. Selected Model and the related artifacts are found in Final Model folder.This also contains a file with monitoring code using evidently
5.Flask App and heruko deployment structure
	-Procfile
	-requirements.txt
	-app.py
	-templates
		-base.html
		-login.html
		-predict1.hmtl
6. Everytime the GIT REPO is checked in with new code build is automatically triggered and deployed on Production
7. If the build fails or app runs into problem while deployment, there is a provision that previous builds can be deployed until the error is
resolved so that downtime is reduced and old features are still available


