Challenge Broker
----------------

We're serving individualized challenges up to users, so we need to manage that.

This tool:

- Discovers new challenges on the filesystem
- Builds containers if they are not already built
- Spins up challenge containers if they are not up as a user connects
- Connects users through to containers, with an interstitial to get their username for challenge personalization
- Tears down challenge containers if they have not been accessed in awhile
- Tells containers about generated flags for challenges

In order to use `chalbroker`, you'll need a `challenge.json`, and a `Dockerfile`. If you have both of those, `chalbroker` will automatically detect them during periodic scans of the source directory. 

`challenge.json`
----------------

`TODO`
