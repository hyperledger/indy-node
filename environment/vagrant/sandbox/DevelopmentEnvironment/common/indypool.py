#!/usr/bin/python3

# Ideally, we would use a virtualenv instead of hardcoding python3.
# python3 is hardcoded, because the python Docker SDK is being installed in a
# python >= 3.5.2 site-packages using pip3/pip3.5.

from __future__ import print_function
from docker.errors import BuildError, APIError, ImageNotFound, ContainerError, NotFound
import sys, docker, argparse

client = docker.from_env()

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def require_str(name, val):
    if not (type(val) is str):
        raise AssertionError("Param %s is not a valid string." % (name))

def getImageByTag(tag):
    '''Check if an image with a given tag exists. No side-effects. Idempotent.
    Handles ImageNotFound and APIError exceptions, but only reraises APIError.
    '''
    require_str("tag", tag)

    image = None
    try:
        image = client.images.get(tag)
        print("Found image", tag, "...")
    except ImageNotFound:
        print("Image", tag, "does not exist ...")
    except APIError as exc:
        eprint("Unhandled error while getting image", tag)
        raise exc

    return image

def getImage(path, dockerfile, tag):
    '''Check if an image with a given tag exists. If not, build an image from
    using a given dockerfile in a given path, tagging it with a given tag.
    No extra side effects. Handles and reraises BuildError, TypeError, and
    APIError exceptions.
    '''
    image = getImageByTag(tag)

    if not image:
        # Build an Image using the dockerfile in the path
        try:
            image = client.images.build(
              path=path,
              dockerfile=dockerfile,
              tag=tag
            )
        except BuildError as exc:
            eprint("Failed to build docker image")
            raise exc
        except TypeError as exc:
            eprint("You must give a path to the build environemnt.")
            raise exc
        except APIError as exc:
            eprint("Unhandled error while building image", tag)
            raise exc

    return image

def runContainer(image, **kwargs):
    '''Run a docker container using a given image; passing keyword arguments
    documented to be accepted by docker's client.containers.run function
    No extra side effects. Handles and reraises ContainerError, ImageNotFound,
    and APIError exceptions.
    '''
    container = None
    try:
        container = client.containers.run(image, **kwargs)
        if "name" in kwargs.keys():
          print("Container", kwargs["name"], "is now running.")
    except ContainerError as exc:
        eprint("Failed to run container")
        raise exc
    except ImageNotFound as exc:
        eprint("Failed to find image to run as a docker container")
        raise exc
    except APIError as exc:
        eprint("Unhandled error")
        raise exc

    return container

def getContainer(name_or_id):
    '''Get the container with the given name or ID (str). No side effects.
    Idempotent. Returns None if the container does not exist. Otherwise, the
    continer is returned'''
    require_str("name_or_id", name_or_id)

    container = None
    try:
        container = client.containers.get(name_or_id)
    except NotFound as exc:
        # Return None when the container is not found
        pass
    except APIError as exc:
        eprint("Unhandled error")
        raise exc

    return container

def containerIsRunning(name_or_id):
    '''Check if container with the given name or ID (str) is running. No side
    effects. Idempotent. Returns True if running, False if not.'''
    require_str("name_or_id", name_or_id)

    try:
        container = getContainer(name_or_id)
        # Refer to the latest status list here: https://docs.docker.com/engine/
        #   api/v1.33/#operation/ContainerList
        if container:
            if container.status == 'created':
              return False
            elif container.status == 'restarting':
              return True
            elif container.status == 'running':
              return True
            elif container.status == 'removing':
              return False
            elif container.status == 'paused':
              return False
            elif container.status == 'exited':
              return False
            elif container.status == 'dead':
              return False
            else:
              return False
    except NotFound as exc:
        return False

    return False

def getContainerByTag(tag):
    '''Check if a container with a given tag exists. No side-effects.
    Idempotent. Handles NotFound and APIError exceptions, but only reraises
    APIError. Returns None if the container is not found. Otherwise, returns the
    container.'''
    require_str("tag", tag)

    container = None
    try:
        container = client.containers.get(tag)
        print("Found container", tag, "...")
    except NotFound:
        #print("Container", tag, "does not exist ...")
        pass
    except APIError as exc:
        eprint("Unhandled error while getting container", tag)
        raise exc

    return container

def removeContainer(tag):
    '''Check if a container with a given tag exists. Kill it if it exists.
    No extra side effects. Handles and reraises TypeError, and
    APIError exceptions.
    '''
    container = getContainerByTag(tag)

    if container:
        # Build an Image using the dockerfile in the path
        try:
            container.remove(force=True)
            #print("Removed container", tag, "...")
        except APIError as exc:
            eprint("Unhandled error while removing container", tag)
            raise exc

def startIndyPool(**kwargs):
    '''Start the indy_pool docker container iff it is not already running. See
    <indy-sdk>/ci/indy-pool.dockerfile for details. Idempotent. Simply ensures
    that the indy_pool container is up and running.'''

    # TODO: Decide if we need a separate docker container for testing and one for
    #       development. The indy_sdk tests setup and teardown "indy_pool" on
    #       ports 9701-9708. Perhaps we need an "indy_dev_pool" on 9709-9716? I'm
    #       not quite sure where all of our dependencies are on port 9701-9708.
    #       If the test harness (mocks) are hardcoding 9701-9708, then an
    #       indy_dev_pool on different ports will not work.

    print("Starting indy_pool ...")

    # Check if indy_pool is running
    if containerIsRunning("indy_pool"):
        print("... already running")
        exit(0)
    else:
        # If the container already exists and isn't running, force remove it and
        # readd it. This is brute force, but is sufficient and simple.
        container = getContainer("indy_pool")
        if container:
          container.remove(force=True)

    # Build and run indy_pool if it is not already running
    # Build the indy_pool image from the dockerfile in:
    #   /vagrant/indy-sdk/ci/indy-pool.dockerfile
    # 
    # In shell using docker cli:
    # cd /vagrant/indy-sdk
    # sudo docker build -f ci/indy-pool.dockerfile -t indy_pool .
    #
    # NOTE: https://jira.hyperledger.org/browse/IS-406 prevents indy_pool from
    #       starting on the `rc` branch. Apply the patch in the Jira issue to
    #       overcome this problem.

    try:
      # indy-sdk won't be in /vagrant if the indy-sdk is cloned to a directory outside
      # the Vagrant project. Regardless of where indy-sdk is cloned, it will be found
      # in /src/indy-sdk in the Vagrant VM.
      image = getImage(path="/src/indy-sdk", dockerfile="ci/indy-pool.dockerfile",
        tag="indy_pool")
    except TypeError as exc:
      image = getImage(path="/vagrant/indy-sdk", dockerfile="ci/indy-pool.dockerfile",
        tag="indy_pool")
    except:
      print("Failed to find indy-pool.dockerfile in /vagrant/indy-sdk or /src/indy-sdk")

    # Run a container using the image
    #
    # In shell using docker cli:
    # sudo docker run -itd -p 9701-9708:9701-9708 indy_pool
    #
    # NOTE: {'2222/tcp': 3333} is sufficient. A tuple of (address, port) if you
    #       want to specify the host interface. 
    container = runContainer(image, ports={
        '9701/tcp': ('0.0.0.0', 9701),
        '9702/tcp': ('0.0.0.0', 9702),
        '9703/tcp': ('0.0.0.0', 9703),
        '9704/tcp': ('0.0.0.0', 9704),
        '9705/tcp': ('0.0.0.0', 9705),
        '9706/tcp': ('0.0.0.0', 9706),
        '9707/tcp': ('0.0.0.0', 9707),
        '9708/tcp': ('0.0.0.0', 9708)
      }, detach=True, name="indy_pool"
    )

    print("...started")

def stopIndyPool(**kwargs):
    '''Stop (docker rm) the indy_pool docker container stopped/removed.
    Idempotent. Simply ensures that the indy_pool container is stopped/removed.
    '''
    print("Stopping...")
    try:
      removeContainer("indy_pool")
      print("...stopped")
    except Exception as exc:
      eprint("...Failed to stop")
      raise exc

def statusIndyPool(**kwargs):
    '''Return the status of the indy_pool docker container. Idempotent.'''
    if containerIsRunning("indy_pool"):
        print("running")
    else:
        print("not running")

def restartIndyPool(**kwargs):
    '''Restart the indy_pool docker container. Idempotent. Ensures that the
    indy_pool container is a new running instance.'''
    print("Restarting...")
    try:
      stopIndyPool()
      startIndyPool()
      print("...restarted")
    except Exception as exc:
      eprint("...failed to restart")
      raise exc

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    graceful = argparse.ArgumentParser(add_help=False)
    sp = parser.add_subparsers()

    sp_start = sp.add_parser('start',
      description="Starts the indy_pool docker container if it is not already running",
      help='Starts the indy_pool docker container')
    sp_start.set_defaults(func=startIndyPool)

    sp_stop = sp.add_parser('stop',
      description="Stops the indy_pool docker container if it is not already stopped",
      help='Stops the indy_pool docker container')
    sp_stop.set_defaults(func=stopIndyPool)

    sp_restart = sp.add_parser('restart',
      description="Stops the indy_pool docker container if it is not already stopped and then starts it",
      help='Restarts the indy_pool docker container')
    sp_restart.set_defaults(func=restartIndyPool)

    sp_status = sp.add_parser('status',
      help='Get the status of the indy_pool docker container')
    sp_status.set_defaults(func=statusIndyPool)

    args = parser.parse_args()
    args.func(args=args)
