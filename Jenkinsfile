#!groovy

@Library('SovrinHelpers') _

def name = 'indy-node'

def nodeTestUbuntu = {
    try {
        echo 'Ubuntu Test: Checkout csm'
        checkout scm

        echo 'Ubuntu Test: Build docker image'
        def testEnv = dockerHelpers.build(name)

        testEnv.inside('--network host') {
            echo 'Ubuntu Test: Install dependencies'
            testHelpers.install()

            echo 'Ubuntu Test: Test'
            testHelpers.testRunner([resFile: "test-result-node.${NODE_NAME}.txt", testDir: 'sovrin_node'])
            //testHelpers.testJUnit(resFile: "test-result-node.${NODE_NAME}.xml")
        }
    }
    finally {
        echo 'Ubuntu Test: Cleanup'
        step([$class: 'WsCleanup'])
    }
}

def clientTestUbuntu = {
    try {
        echo 'Ubuntu Test: Checkout csm'
        checkout scm

        echo 'Ubuntu Test: Build docker image'
        def testEnv = dockerHelpers.build(name)

        testEnv.inside('--network host') {
            echo 'Ubuntu Test: Install dependencies'
            testHelpers.install()

            echo 'Ubuntu Test: Test'
            testHelpers.testRunner([resFile: "test-result-client.${NODE_NAME}.txt", testDir: 'sovrin_client'])
            //testHelpers.testJUnit(resFile: "test-result-client.${NODE_NAME}.xml")
        }
    }
    finally {
        echo 'Ubuntu Test: Cleanup'
        step([$class: 'WsCleanup'])
    }
}

def commonTestUbuntu = {
    try {
        echo 'Ubuntu Test: Checkout csm'
        checkout scm

        echo 'Ubuntu Test: Build docker image'
        def testEnv = dockerHelpers.build(name)

        testEnv.inside {
            echo 'Ubuntu Test: Install dependencies'
            testHelpers.install()

            echo 'Ubuntu Test: Test'
            testHelpers.testJUnit([resFile: "test-result-common.${NODE_NAME}.xml", testDir: 'sovrin_common'])
        }
    }
    finally {
        echo 'Ubuntu Test: Cleanup'
        step([$class: 'WsCleanup'])
    }
}

options = new TestAndPublishOptions()
options.enable([StagesEnum.PACK_RELEASE_DEPS, StagesEnum.PACK_RELEASE_ST_DEPS])
testAndPublish(name, [ubuntu: [node: nodeTestUbuntu, client: clientTestUbuntu, common: commonTestUbuntu]], true, options)
