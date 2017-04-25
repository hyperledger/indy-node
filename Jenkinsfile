#!groovy

@Library('SovrinHelpers') _

def name = 'sovrin-node'

def testUbuntu = {
    try {
        echo 'Ubuntu Test: Checkout csm'
        checkout scm

        echo 'Ubuntu Test: Build docker image'
        def testEnv = dockerHelpers.build(name)

        testEnv.inside('--network host') {
            echo 'Ubuntu Test: Install dependencies'
            def sovrinCommon = helpers.extractVersion('sovrin-common')
            def sovrinClient = helpers.extractVersion('sovrin-client')
            def plenum = helpers.extractVersionOfSubdependency(sovrinCommon, 'plenum')
            testHelpers.install(deps: [plenum, sovrinCommon, sovrinClient])

            echo 'Ubuntu Test: Test'
            testHelpers.testRunner(resFile: "test-result.${NODE_NAME}.txt")
            //testHelpers.testJUnit(resFile: "test-result.${NODE_NAME}.xml")
        }
    }
    finally {
        echo 'Ubuntu Test: Cleanup'
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

        testHelpers.createVirtualEnvAndExecute({ python, pip ->
            echo 'Windows No Docker Test: Install dependencies'
            def sovrinClient = helpers.extractVersion('sovrin-client')
            testHelpers.install(python: python, pip: pip, deps: [sovrinClient], isVEnv: true)

            echo 'Windows No Docker Test: Test'
            testHelpers.testJUnit(resFile: "test-result.${NODE_NAME}.xml", python: python)
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
