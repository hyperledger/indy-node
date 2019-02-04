Build up a provisioning script composed of scriptlets encapsulating discrete, 
resusable units of work.

The scriptlets must be written in a language compatible with the target       
operating system. For example, bash or sh for Linux, and powershell for Windows.

Some operating systems manage packages differently and may even use different 
package names for the same dependencies. Therefore, package manager agnostic  
scriptlets are separated from package manager centric scriptlets. Tools like
Ansible, Puppet, Chef, and Salt help with this. Perhaps a configuration
management tool will be used in the future, but for now please define scriptlets
for each package manager.

Scriptlets are defined in the 'scriptlets' directory and the provisioning     
script is composed by the provisioning tool (i.e. Vagrant) in the following
order:

```
<os family> ::= linux | windows
<package manager> ::= apt | yum | others?
<repo> ::= TODO: decide how repos are defined

scriptlets/common/pre/<os family>/setup
scriptlets/common/pre/<os family>/<package manager>/setup
for each <repo>
  scriptlets/<repo>/<os family>/pre/setup
  scriptlets/<repo>/<os family>/pre/<package manager>/setup
  scriptlets/<repo>/<os family>/build
  scriptlets/<repo>/<os family>/env
  scriptlets/<repo>/<os family>/test
  scriptlets/<repo>/<os family>/bundle
  scriptlets/<repo>/<os family>/deposit
  scriptlets/<repo>/<os family>/deploy/<package manager>
  scriptlets/<repo>/<os family>/clean                                       
  scriptlets/<repo>/<os family>/post/<package manager>/setup                  
  scriptlets/<repo>/<os family>/post/setup                   
scriptlets/common/post/<os family>/<package manager>/setup                    
scriptlets/common/post/<os family>/setup 
```

Scriptlet Targets Explained

Target | Purpose | Description
------ | ------- | -----------
pre | Setup | Pre-CI/CD pipeline scriptlets
build | CI/CD | Build the project(s)
env | CI/CD | Setup the environment. Artifacts from the build target may need to be added to the PATH, LD_LIBRARY_PATH, PYTHONPATH, etc.
test | CI/CD | Run tests (i.e. unit, integration, smoke...)
bundle | CI/CD | Create packages (i.e. .deb, .rpm, tar, etc.)
deposit | CI/CD | Deposit tested and bundled artifacts. This scriptlet may need to be branch aware.
deploy | CI/CD | Deploy tested, bundled, and optionally deposited artifacts (Continuous Deployment)
post | CI/CD | Any cleanup needed to keep the build environment footprint small, but still have a functional development/build environment. For example, delete third party source files needed to build a dependency. Perhaps this target can be used to run smoke tests on deployed artifacts?

The following depicts this project's scriptlets directory. The elipses (...)
are added for brevity.

```
├── common
│   ├── pre
│   │   ├── <os family>
│   │   │   ├── <package manager>
│   │   │   │   └── setup
│   │   │   └── setup
│   │   └── <os family>...
│   └── post
│       ├──<os family> 
│       │   ├── <package manager>
│       │   │   └── setup
│       │   └── setup
│       └── <os family>...
├── <repo>
│   ├── <os family> 
│   │   ├── pre
│   │   │   ├── <package manager>
│   │   │   │   └── setup
│   │   │   ├── <package manager>...
│   │   │   └── setup
│   │   ├── build
│   │   ├── env
│   │   ├── test
│   │   ├── bundle
│   │   ├── deposit
│   │   ├── deploy
│   │   │   ├── <package manager>
│   │   │   └── <package manager>...
│   │   ├── clean
│   │   └── post
│   │       ├── <package manager>
│   │       │   └── setup
│   │       ├── <package manager>...
│   │       └── setup
│   └── <os family>...
└── <repo>...
```
