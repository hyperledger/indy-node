#!groovy​

def success = true

try {

// ALL BRANCHES: master, stable, PRs

    // 1. TEST
    stage('Test') {
        parallel 'ubuntu-test':{
            node('ubuntu') {
                stage('Ubuntu Test') {
                    testUbuntu()
                }
            }
        },
        'windows-test':{
            stage('Windows Test') {
                testWindows()
            }
        }
    }

// MASTER AND STABLE ONLY

    if (env.BRANCH_NAME != 'master' && env.BRANCH_NAME != 'stable') {
        echo "Ledger ${env.BRANCH_NAME}: skip publishing"
        return
    }

    // 2. PUBLISH TO PYPI
    stage('Publish to pypi') {
        node('ubuntu') {
            version = publishToPypi()
        }
    }

    // 3. BUILD PACKAGES
    stage('Build packages') {
        parallel 'ubuntu-build':{
            node('ubuntu') {
                stage('Build deb packages') {
                    buildDeb()
                }
            }
        },
        'windows-build':{
            stage('Build msi packages') {
                buildMsi()
            }
        }
    }

    // 4. SYSTEM TESTS
    stage('System tests') {
        parallel 'ubuntu-system-tests':{
            stage('Ubuntu system tests') {
                ubuntuSystemTests()
            }
        },
        'windows-system-tests':{
            stage('Windows system tests') {
                windowsSystemTests()
            }
        }
    }

// MASTER ONLY

    if (env.BRANCH_NAME != 'stable') {
        return
    }

    // 5. NOTIFY QA
    stage('QA notification') {
        notifyQA(version)
    }

    // 6. APPROVE QA
    def qaApproval
    stage('QA approval') {
        qaApproval = approveQA()
    }
    if (!qaApproval) {
        return
    }

    // 7. RELEASE PACKAGES
    stage('Release packages') {
        parallel 'ubuntu-release-packages':{
            stage('Ubuntu release packages') {
                echo 'TODO: Implement me'
            }
        },
        'windows-release-packages':{
            stage('Windows release packages') {
                echo 'TODO: Implement me'
            }
        }
    }

    // 8. SYSTEM TESTS FOR RELEASE
    stage('Release system tests') {
        parallel 'ubuntu-system-tests':{
            stage('Ubuntu system tests') {
                ubuntuSystemTests()
            }
        },
        'windows-system-tests':{
            stage('Windows system tests') {
                windowsSystemTests()
            }
        }
    }

} catch(e) {
    success = false
    currentBuild.result = "FAILED"
    notifyFail()
    throw e
} finally {
    if (success && (env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'stable')) {
        currentBuild.result = "SUCCESS"
        notifySuccess()
    }
}

@NonCPS
def extractVersionFromText(match, text) {
    def pattern = /.*(${match}[-a-z=\\.0-9]*)'/
    def matcher = (text =~ pattern)
    return matcher[0][1]
}

@NonCPS
def dropVersion(text) {
    def pattern = /([-a-z]+)[=\\.0-9]*/
    def matcher = (text =~ pattern)
    return matcher[0][1]
}

def extractVersion(match, file='setup.py') {
    def text = sh(returnStdout: true, script: "grep \"${match}[-a-z=\\.0-9]*'\" ${file}").trim()
    echo "${match}Version -> matching against ${text}"
    return extractVersionFromText(match, text)
}

def testUbuntu() {
    try {
        echo 'Ubuntu Test: Checkout csm'
        checkout scm

        echo 'Ubuntu Test: Build docker image'
        sh 'ln -sf ci/sovrin-node-ubuntu.dockerfile Dockerfile'
        def dockerContainers = sh(returnStdout: true, script: 'docker ps -a').trim()
        echo "Existing docker containers: ${dockerContainers}"
        if (dockerContainers.toLowerCase().contains('orientdb')) {
            sh('docker start orientdb')
        } else {
            sh("docker run -d --name orientdb -p 2424:2424 -p 2480:2480 -e ORIENTDB_ROOT_PASSWORD=password -e ORIENTDB_OPTS_MEMORY=\"${env.ORIENTDB_OPTS_MEMORY}\" orientdb")
        }

        def testEnv = docker.build 'sovrin-node-test'

        testEnv.inside('--network host') {
            echo 'Ubuntu Test: Install dependencies'
            sh 'cd /home/sovrin && virtualenv -p python3.5 test'

            def sovrinCommon = extractVersion('sovrin-common')
            def sovrinClient = extractVersion('sovrin-client')

            sh "mkdir -p /home/sovrin/tmp"
            sh "pip3 download -b /home/sovrin/tmp --no-clean ${sovrinCommon}"

            def sovrinCommonPackageOnly = dropVersion("${sovrinCommon}")
            plenum = extractVersion('plenum', "/home/sovrin/tmp/${sovrinCommonPackageOnly}/setup.py")

            sh 'cp -r /usr/local/lib/python3.5/dist-packages/Charm_Crypto-0.0.0.egg-info /home/sovrin/test/lib/python3.5/site-packages/Charm_Crypto-0.0.0.egg-info'
            sh 'cp -r /usr/local/lib/python3.5/dist-packages/charm /home/sovrin/test/lib/python3.5/site-packages/charm'

            sh 'ln -f /home/sovrin/test/bin/python /usr/local/bin/python'

            sh "/home/sovrin/test/bin/pip install ${plenum}"
            sh "/home/sovrin/test/bin/pip install ${sovrinClient}"
            sh '/home/sovrin/test/bin/python setup.py install'
            sh '/home/sovrin/test/bin/pip install pytest'

            echo 'Ubuntu Test: Test'
            try {
                sh '/home/sovrin/test/bin/python -m pytest --junitxml=test-result.xml'
            }
            finally {
                junit 'test-result.xml'
            }
        }
    }
    finally {
        echo 'Ubuntu Test: Cleanup'
        sh "docker stop orientdb"
        step([$class: 'WsCleanup'])
    }
}

def testWindows() {
    echo 'TODO: Implement me'
}

def publishToPypi() {
    try {
        echo 'Publish to pypi: Checkout csm'
        checkout scm

        echo 'Publish to pypi: Prepare package'
        sh 'chmod -R 777 ci'
        //gitCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
        version = sh(returnStdout: true, script: 'ci/get-package-version.sh plenum $BUILD_NUMBER').trim()

        sh 'ci/prepare-package.sh . $BUILD_NUMBER'

        echo 'Publish to pypi: Publish'
        withCredentials([file(credentialsId: 'pypi_credentials', variable: 'FILE')]) {
            sh 'ln -sf $FILE $HOME/.pypirc'
            sh 'ci/upload-pypi-package.sh .'
            sh 'rm -f $HOME/.pypirc'
        }

        return version
    }
    finally {
        echo 'Publish to pypi: Cleanup'
        step([$class: 'WsCleanup'])
    }
}

def buildDeb() {
    try {
        echo 'Build deb packages: Checkout csm'
        checkout scm

        echo 'Build deb packages: Prepare package'
        sh 'chmod -R 777 ci'
        sh 'ci/prepare-package.sh . $BUILD_NUMBER'

        dir('sovrin-packaging') {
            echo 'Build deb packages: get packaging code'
            git branch: 'jenkins-poc', credentialsId: 'evernym-githib-user', url: 'https://github.com/evernym/sovrin-packaging'

            echo 'Build deb packages: Build debs'
            def sourcePath = sh(returnStdout: true, script: 'readlink -f ..').trim()
            sh "./pack-debs $BUILD_NUMBER plenum $sourcePath"

            echo 'Build deb packages: Publish debs'
            def repo = env.BRANCH_NAME == 'stable' ? 'rc' : 'master'
            sh "./upload-debs $BUILD_NUMBER plenum $repo"
        }
    }
    finally {
        echo 'Build deb packages: Cleanup'
        dir('sovrin-packaging') {
            deleteDir()
        }
        step([$class: 'WsCleanup'])
    }
}

def buildMsi() {
    echo 'TODO: Implement me'
}

def ubuntuSystemTests() {
    echo 'TODO: Implement me'
}

def windowsSystemTests() {
    echo 'TODO: Implement me'
}

def notifyQA(version) {
    emailext (
        subject: "New release candidate 'sovrin-node-$version' is waiting for approval",
        body: "Please go to ${BUILD_URL}console and verify the build",
        to: 'alexander.sherbakov@dsr-company.com'
    )
}

def approveQA() {
    def qaApproval
    try {
        input(message: 'Do you want to publish this package?')
        qaApproval = true
        echo 'QA approval granted'
    }
    catch (Exception err) {
        qaApproval = false
        echo 'QA approval denied'
    }
    return qaApproval
}


def notifyFail() {
    emailext (
        body: '$DEFAULT_CONTENT',
        recipientProviders: [
            [$class: 'CulpritsRecipientProvider'],
            [$class: 'DevelopersRecipientProvider'],
            [$class: 'RequesterRecipientProvider']
        ],
        replyTo: '$DEFAULT_REPLYTO',
        subject: '$DEFAULT_SUBJECT',
        to: '$DEFAULT_RECIPIENTS'
       )
}

def notifySuccess() {
    emailext (
        body: '$DEFAULT_CONTENT',
        recipientProviders: [
            [$class: 'CulpritsRecipientProvider'],
            [$class: 'DevelopersRecipientProvider'],
            [$class: 'RequesterRecipientProvider']
        ],
        replyTo: '$DEFAULT_REPLYTO',
        subject: "New ${BRANCH_NAME} build 'sovrin-node-$version'",
        to: '$DEFAULT_RECIPIENTS'
       )
}
