#!groovy​

@Library('SovrinHelpers') _

def name = 'sovrin-node'

def testUbuntu = {
    try {
        echo 'Ubuntu Test: Checkout csm'
        checkout scm

        echo 'Ubuntu Test: Build docker image'
        orientdb.start()

        def testEnv = dockerHelpers.build(name)

        testEnv.inside('--network host') {
            echo 'Ubuntu Test: Install dependencies'

            def sovrinCommon = helpers.extractVersion('sovrin-common')
            def sovrinClient = helpers.extractVersion('sovrin-client')
            def plenum = helpers.helpers.extractVersionOfSubdependency(sovrinCommon, 'plenum')

            deps = [plenum, sovrinCommon, sovrinClient]
            testHelpers.installDeps(deps)

            echo 'Ubuntu Test: Test'
            testHelpers.testJunit()
        }
    }
    finally {
        echo 'Ubuntu Test: Cleanup'
        orientdb.stop()
        step([$class: 'WsCleanup'])
    }
}

def testWindows = {
    echo 'TODO: Implement me'
}

def testWindowsNoDocker = {
    echo 'TODO: Implement me'
}



testAndPublish(name, [ubuntu: testUbuntu, windows: testWindows, windowsNoDocker: testWindowsNoDocker])