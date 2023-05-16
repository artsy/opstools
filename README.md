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

Alternative way to load environment vars using Foreman:
```
foreman run --env .env.shared,.env [COMMAND]
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
