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
unset $(grep --no-filename --invert-match '^#' .env.shared .env | cut -f1 -d"=" | xargs)
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
