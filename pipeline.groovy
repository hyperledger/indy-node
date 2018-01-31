#!/usr/bin/env groovy

def loadIndyLib(credentialsId) {
    library identifier: 'indy@feature/INDY-997_public-lib', retriever: modernSCM(
        github(credentialsId: credentialsId, repoOwner: 'evernym', repository: 'jenkins-shared')
    )
}

def init() {
    return [
        dockers: [
            ubuntu: [
                imgName: "hyperledger/indy-node-ci",
                dockerfile: "ci/ubuntu.dockerfile",
                contextDir: "ci"
            ]
        ],
        tests: [
            common: [
                resFile: { "test-result-common.${NODE_NAME}.xml" },
                testDir: 'indy_common',
                docker: 'ubuntu'
            ],
            client: [
                resFile: { "test-result-client.${NODE_NAME}.txt" },
                testDir: 'indy_client',
                useRunner: true,
                docker: 'ubuntu'
            ],
            node: [
                resFile: { "test-result-node.${NODE_NAME}.txt" },
                testDir: 'indy_node',
                useRunner: true,
                docker: 'ubuntu'
            ]
        ]
    ]
}


def buildDebUbuntu(releaseVersion, sourcePath) {
    def volumeName = "$name-deb-u1604"
    if (env.BRANCH_NAME && env.BRANCH_NAME != 'master') {
        volumeName = "${volumeName}.${env.BRANCH_NAME}"
    }
    if (sh(script: "docker volume ls -q | grep -q '^$volumeName\$'", returnStatus: true) == 0) {
        sh "docker volume rm $volumeName"
    }
    dir('build-scripts/ubuntu-1604') {
        sh "./build-$name-docker.sh \"$sourcePath\" $releaseVersion $volumeName"
        sh "./build-3rd-parties-docker.sh $volumeName"
    }
    return "$volumeName"
}


return this;
