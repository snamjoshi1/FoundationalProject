# FoundationalProject
Stock Price Prediction Using Sentiment Analysis
1. Data is scraped using GoogleAPI and Twitter API and sample code can be found in Scraping Code Folder
2. The Data Files are attached seperately.The Input data to model is found in Final_Input_DF.xlsx,Scraped News Data is found in News_Data.xlsx and tweet data is found in Tweet_Data.xlsx
and PredictedValues for test data is found in RFPredicted_ArimaPredicted_ActualTest.xlsx
3. All the analyzed models are present in AnalyzedModels folder
4. Selected Model and the related artifacts are found in SelectedModel folder.This also contains a file with monitoring code using evidently
5.Flask App and heruko deployment structure-in ModelDeployment Folder
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


