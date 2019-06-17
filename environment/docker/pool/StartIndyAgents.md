Starting the Indy Agent Scripts on a Docker Indy Test Deployment
------

Once you have the Indy test nodes and client running, and before you run through the Indy tutorial script, you need to start the Indy Agents that represent the organizations in the scenario - Faber College, Acme Corp. and Thrift Bank. The steps to start the agents are outlined below.

## Open terminal and exec into the client docker container:
When you start up the Indy client for testing, you will be in a shell running the Indy CLI. Leave that command line as is (we'll return to it after these steps) and start up a new shell to carry out the series of steps here.

Within the new command line, log into the Indy Client docker container:

```docker exec -i -t indyclient bash```

### Start up Indy and carry out the next series of commands with Indy.

To start indy client:

```indy```

Connect to the test network - the nodes that you are running on docker:

```connect test```

#### Create Steward

Create an initial Indy Steward for the test network. The Steward will be used to add the three organizations as Endorsers in the network.

_NOTE_: The commands in this script need to be copied and pasted exactly as specified here. There are many "magic strings" that must match exactly for the communication to work.

```new key with seed 000000000000000000000000Steward1```

#### Register the Faber Identity and Agent Endpoint

Create Faber College as an Identity and one that is a Endorser.

```send NYM dest=ULtgFQJe6bjiFbs7ke3NJD role=ENDORSER verkey=~5kh3FB4H3NKq7tUDqeqHc1```

NOTE: Be sure that the CLI responds with an "ADDED" response such as
```
Adding nym ULtgFQJe6bjiFbs7ke3NJD
Nym ULtgFQJe6bjiFbs7ke3NJD added
```

If you don't get the "ADDED" response then one of the Nodes may not have started and you likely have to restart the pool with the ./pool_start.sh command

```new key with seed Faber000000000000000000000000000```

In the next step to create the endpoint for the Faber Agent, we're using the IP address of the Indy client (10.0.0.6), and a unique port for the agent. If you used a different IP in starting up Indy, you need to replace your IP/Port in the following command:

```send ATTRIB dest=ULtgFQJe6bjiFbs7ke3NJD raw={"endpoint": {"ha": "10.0.0.6:5555", "pubkey": "5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z"}}```

#### Register ACME Identity and Agent Endpoint
That's it for Faber...on to Acme.  Before starting, we have to go back to using the Steward identity.

```use DID Th7MpTaRZVRYnPiabds81Y```

Once that's done, repeat the steps for Acme (with different parameters).

```send NYM dest=CzkavE58zgX7rUMrzSinLr role=ENDORSER verkey=~WjXEvZ9xj4Tz9sLtzf7HVP```

```new key with seed Acme0000000000000000000000000000```

As with Faber, we're using the IP address of the Indy client (10.0.0.6), and a unique port for the agent in the next command. If you used different IPs in starting up Indy, you need to replace your IP/Port in the following command:

```send ATTRIB dest=CzkavE58zgX7rUMrzSinLr raw={"endpoint":{"ha": "10.0.0.6:6666", "pubkey": "C5eqjU7NMVMGGfGfx2ubvX5H9X346bQt5qeziVAo3naQ"}}```

#### Register Thrift Bank Identity and Agent Endpoint
And on to Thrift.  Before starting, we have to go back to using the Steward identity.

```use DID Th7MpTaRZVRYnPiabds81Y```

Once that's done, repeat the steps, using different IDs.

```send NYM dest=H2aKRiDeq8aLZSydQMDbtf role=ENDORSER verkey=~3sphzTb2itL2mwSeJ1Ji28```

```new key with seed Thrift00000000000000000000000000```

As with Faber and Acme, we're using the IP address of the Indy client (10.0.0.6), and a unique port for the agent in the next command. If you used different IPs in starting up Indy, you need to replace your IP/Port in the following command:

```send ATTRIB dest=H2aKRiDeq8aLZSydQMDbtf raw={"endpoint": {"ha": "10.0.0.6:7777", "pubkey":"AGBjYvyM3SFnoiDGAEzkSLHvqyzVkXeMZfKDvdpEsC2x"}}```

#### Indy steps complete - Exit
Exit from the Indy command line application, but stay in the bash shell in the docker container. To do that, just run at the 'indy' prompt:

```exit```

You should be back to the bash prompt within the indyclient container.

## Start the Indy Agents

We'll now invoke the Indy Agents from the same command line, redirecting the output to different files. We can then review the logs as commands are executed.

#### Invoke the clients
Use these commands to invoke each of the clients. Note the ports entered on the commands above for setting the endpoints are referenced below. If you used different ports above, adjust these commands below to match.

```python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/faber.py --port 5555 >faber.log &```

```python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/acme.py --port 6666 >acme.log &```

```python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/thrift.py --port 7777 >thrift.log &```

For those not familiar with Linux - the trailing "&" runs the command in the background.

If you want to monitor one of the logs while executing the rest of the tutorial, you can use a command such as:

```tail -f faber.log```

To stream the end of the (in the case) Faber College agent log. Ctrl-C to exit out of that.

That completes the process for starting the Agents. Leave this command line running while you complete the rest of the tutorial - the story of Alice, her transcripts, job, and banking - in the terminal window in which you ran the script to start the Indy Client. You should be at a "indy" prompt.

Note that when the indyclient container stops, the agents will stop automatically. That will happen when you "exit" from the indy command line in the other terminal window.
