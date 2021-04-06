# Crypto portfolio evaluation and exploration with Streamlit

## APIs consumed
- uphold for assets and tickers
- CryptoCompare for historical prices

## CryptoCompare API-KEY setup

  - Set up an api-key with CryptoCompare
  - Activate the google-cloud-secret-manager api and create a secret key
  - Add the secret key to your image
  - Provide the path to the secret key file through the `GOOGLE_APPLICATION_CREDENTIALS` environment variable
  - Upload it as a secret using google-cloud-secret-manager
  - Provision the secret name as `SECRET_NAME` environment variable

## Streamlit file

  - Add any streamlit files to your image in the `src` directory
  - Define the file to be run through the `DASHBOARD_FILE` environment variable

