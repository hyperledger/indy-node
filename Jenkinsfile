#!groovy

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
            def plenum = helpers.extractVersionOfSubdependency(sovrinCommon, 'plenum')

            deps = [plenum, sovrinCommon, sovrinClient]
            testHelpers.installDeps(deps)

            echo 'Ubuntu Test: Test'
            sh 'python runner.py --pytest \"python -m pytest\" --output "test-result.txt"'
            //testHelpers.testJunit()
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
    try {
        echo 'Windows No Docker Test: Checkout csm'
        checkout scm

        echo 'Windows No Docker Test: drop orientdb databases'
        orientdb.cleanupWindows()


        testHelpers.createVirtualEnvAndExecute({ python, pip ->
            echo 'Windows No Docker Test: Install dependencies'

            def sovrinClient = helpers.extractVersion('sovrin-client')

            testHelpers.installDepsBat(python, pip, [sovrinClient])

            echo 'Windows No Docker Test: Test'
            testHelpers.testJunitBat(python, pip)
        })
    }
    finally {
        echo 'Windows No Docker Test: Cleanup'
        step([$class: 'WsCleanup'])
    }
}

//testAndPublish(name, [ubuntu: testUbuntu, windows: testWindowsNoDocker, windowsNoDocker: testWindowsNoDocker])

options = new TestAndPublishOptions()
options.skip([StagesEnum.GITHUB_RELEASE])
options.enable([StagesEnum.PACK_RELEASE_DEPS, StagesEnum.PACK_RELEASE_ST_DEPS])
options.setPublishableBranches(['3pc-batch']) //REMOVE IT BEFORE MERGE
options.setPostfixes([master: '3pc-batch']) //REMOVE IT BEFORE MERGE
testAndPublish(name, [ubuntu: testUbuntu], true, options)
