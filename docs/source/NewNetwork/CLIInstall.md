# Installing the `indy-cli`

The `indy-cli` is developed under the [indy-sdk](https://github.com/hyperledger/indy-sdk). This documentation may be not up to date.

You will need to perform the following once for each `indy-cli` machine you would like to set up (only 1 is required). 
It is recommended that you install the `indy-cli` in your native work environment if possible, so you always have it available even when traveling. 

## Containerized `indy-cli` Environment

The following sections describe how to install and configure the `indy-cli` directly on a machine or VM. However, possibly the most convenient option is to use a containerized `indy-cli` environment like the one included with [von-network](https://github.com/bcgov/von-network).  For information on how to use the containerized `indy-cli` in `von-network`, refer to [Using the containerized indy-cli](https://github.com/bcgov/von-network/blob/main/docs/Indy-CLI.md)

## Windows:
To install the `indy-cli` on Windows 10 perform the following steps:
1. Download https://repo.sovrin.org/windows/indy-cli/stable/1.16.0/indy-cli_1.16.0.zip and unzip it.
   If there is a newer version under https://repo.sovrin.org/windows/indy-cli/stable/ it instead.
2. Open a command prompt.  (This will work differently if you use Windows Terminal).
3. `cd` to the directory where you unzipped the `indy-cli` package.  For example, if you unzipped directly in your ‘downloads’ directory like I did you would type:  `cd \Users\<Username>\Downloads\indy-cli_1.14.2`
4. Create a JSON Config file containing your taaAcceptanceMechanism in the directory where indy-cli.exe resides (I created \Users\<Username>\Downloads\indy-cli_1.14.2\cliconfig.json on my machine)
   ```json
   {
   "taaAcceptanceMechanism": "for_session" 
   } 
   ```
5. Run  `indy-cli.exe --config cliconfig.json`  to verify proper installation.  You should see a new window appear with an `indy>` prompt,  (If you are double clicking to start `indy-cli`, you need to right click on the .exe in your window and add the --config parameter first.)  If you get an error stating that it is missing vcruntime140.dll then do the following:
6. Download and install vc_redist.x64.exe from the Visual Studio 2017 section on the https://support.microsoft.com/en-ae/help/2977003/the-latest-supported-visual-c-downloads page, and then rerun indy-cli.exe to see if it works as described in previous step.
7. Type ‘exit’ in the `indy-cli`

## Ubuntu:
To install the `indy-cli` on Ubuntu, perform the following steps from the ubuntu command line:

1. `sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88`
2. `sudo add-apt-repository "deb https://repo.sovrin.org/sdk/deb xenial stable"`
3. `sudo add-apt-repository "deb https://repo.sovrin.org/deb xenial stable"`
4. `sudo apt-get update -y`
5. `sudo apt-get upgrade -y `
6. `sudo apt-get install -y indy-cli`
7. `cd ~`
8. Create a JSON Config file containing your taaAcceptanceMechanism in your home directory:
`vim ~/cliconfig.json`

   Press the “i” key and paste the following into the file:
   ```json
   {
   "taaAcceptanceMechanism": "for_session" 
   } 
   ```
   Press the “esc” key then the following characters to write the file and quit
`:wq` 
9. Run `indy-cli --config ~/cliconfig.json` to start the `indy-cli`

## Mac:

Since there is not a prepackaged version of the `indy-cli` prepared for the Mac, the following steps will help you to create an environment, build, and run the `indy-cli` in a Mac terminal.

Open a Terminal
Run the following commands in the terminal:

1. `cd ~`
2. `mkdir github`
3. `cd github`
4. `git clone https://github.com/hyperledger/indy-sdk.git`(might need xcode-select --install if error occurs)
5. `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
6. `curl https://sh.rustup.rs -sSf | sh`
7. Follow onscreen instructions to install rust
8. `brew install pkg-config libsodium automake autoconf cmake openssl zeromq zmq`
   NOTE: the openssl path needs to match what you currently have on your system

9. Run  > `ls /usr/local/Cellar/openssl/`
   Note the name of the directory shown (the example below shows 1.0.2p but the latest version is 1.1.1l) 
 
   Use this directory in place of the one listed below in your .profile file 

10. Add the following lines to your` ~/.profile file `(making the correction shown in the previous step if needed)
      ```
      export PATH="$HOME/.cargo/bin:$PATH:~/github/indy-sdk/libindy/target/debug:~/github/indy-sdk/cli/target/debug"
      export PKG_CONFIG_ALLOW_CROSS=1
      export CARGO_INCREMENTAL=1
      export RUST_LOG=indy=trace
      export RUST_TEST_THREADS=1
      export OPENSSL_DIR=/usr/local/Cellar/openssl/1.0.2p  #use your path
      export LIBRARY_PATH=~/github/indy-sdk/libindy/target/debug/
      export LIBINDY_DIR=~/github/indy-sdk/libindy/target/debug/
      ```
11. Run the following commands from your terminal to build the `indy-cli`:
      ```
      source ~/.profile
      cd ~/github/indy-sdk/libindy
      cargo build
      cd ../cli
      cargo build
      ```
12. Create a JSON Config file containing your taaAcceptanceMechanism in your home directory:
    `vim ~/cliconfig.json`
   
      Press the “i” key and paste the following into the file:
      ```json
      {
      "taaAcceptanceMechanism": "for_session" 
      } 
      ```
      Press the “esc” key then the following characters to write the file and quit
   `:wq` 
13. You can now run `indy-cli` from within a terminal by typing

      `indy-cli --config ~/cliconfig.json`
   
      `indy> exit`     (To exit from the `indy-cli` prompt when you ar done) 

      If the above gives error regarding library not loaded libssl.1.0.0, you will probably need to run the following command (all in one line should work) to revert your version: 
  
      ```
      brew uninstall --ignore-dependencies openssl; brew uninstall openssl;
      brew install https://github.com/tebelorg/Tump/releases/download/v1.0.0/openssl.rb
      ```


