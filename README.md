# temporal-call-center-ui

## Running locally
Set following environment parameters:
- TWILIO_ACCOUNT_SID - Twilio account SID
- TWILIO_AUTH_TOKEN - Twilio auth token
- TWILIO_API_KEY - Twilio api key
- TWILIO_API_KEY_SECRET - Twilio api key secret
- TEMPORAL_HOST_URL - temporal endpoint i.e. call-center.sdddf.tmprl.cloud:7233
- TEMPORAL_NAMESPACE - Namespace i.e. call-center.sdddf
- TEMPORAL_TASK_QUEUE - Taskqueue name
- TEMPORAL_MTLS_TLS_CERT - Path to MTLS cert (optional)
- TEMPORAL_MTLS_TLS_KEY - Path to MTLS key (optional)

In addition to the environment variables, ngrok is required to expose the http server to Twilio. You will need to set that URL in the Twilio console webhook configuration for your phone number.

```
$ ngrok http 5000
```
