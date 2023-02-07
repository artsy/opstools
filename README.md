# Opstools

Tools for Operations.

* __Point People:__ [#product-velocity][velocity_channel]

# Setup

Read and run the setup script:
```
./bin/setup
```

Load environment vars:
```
export $(grep --no-filename --invert-match '^#' .env.shared .env | xargs)
```

# Testing

```
pytest
```

or

```
ptw
```

[velocity_channel]: https://artsy.slack.com/messages/product-velocity "#product-velocity Slack Channel"
