# Introduction
This is a basic version of photo viewer. All the image processing steps are running in OpenLambda. Photo viewer client sends requests to the openLambda server. Currently, the photo viewer supports 2 different requests handled by different lambda scripts in the edge server:
* fetch: fetch the image from S3 and send back to the client with Base64 encoding.
* * resize [width] [height]: fetch the image from S3, change the size, and send back to the client.

# Deployment
## Note
Please use `pip2 install urllib3 --target=[your_open_lambda_server_folder]/packages` to install a newer version of urllib3 or AWS boto3 library can't work. You can either add the required packages to packages.txt but I assume install any packages to `[your_open_lambda_server_folder]/packages` is much convenient and packages.txt can't upgrade the package.

## OpenLambda Server
Copy all lambda scripts in edgeLambda folder to [your_open_lambda_server_folder]/registry and install appropriate packages if necessary.

## Client
Run `python3 main.py`.
