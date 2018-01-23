#!/usr/bin/env groovy

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

return this;
