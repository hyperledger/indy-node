#!groovy

def systemTests(Closure body) {
    String prefix = "System Tests"
    String systemTestsNetwork = 'indy-test-automation-network'
    String systemTestsDir = './system_tests'

    def config = delegateConfig([
            repoChannel: 'master',
            pkgVersion: null,
            indyNodeRepoUrl: 'https://github.com/hyperledger/indy-node.git',
            srcVersion: null,
            testSchema: [['.']],
            testVersion: null,
            testVersionByTag: false,
            gatherLogs: true
        ],
        body, ['pkgVersion'], {}, prefix
    )

    Map systemTestsParams = [
        targetDir: systemTestsDir
    ]

    if (config.testVersion) {
        if (!!config.testVersionByTag) {
            systemTestsParams.tag = config.testVersion
        } else {
            systemTestsParams.branch = config.testVersion
        }
    }

    Map indyPlenumVersions = [:]
    Map indySDKVersions = [:]
    Map indyCryptoVersions = [:]

    def dockerClean = {
        sh "./system/docker/clean.sh $systemTestsNetwork"

        try {
            sh "docker ps -q --filter network=$systemTestsNetwork | xargs -r docker rm -f"
        } catch (Exception exc) {
            echo "$prefix: failed to remove docker containers in $systemTestsNetwork network: $exc"
            throw exc
        }

        try {
            sh "docker network ls -q --filter name=$systemTestsNetwork | xargs -r docker network rm"
        } catch (Exception exc) {
            echo "$prefix: failed to remove docker $systemTestsNetwork network: $exc"
            throw exc
        }

        sh "docker container prune -f"
        sh "docker network prune -f"
    }

    def runTest = { testGroup ->

        stage("[${testGroup}] Checkout system tests") {
            testHelpers.getSystemTests(systemTestsParams)
        }

        dir(systemTestsDir) {
            stage("[${testGroup}] Patch system tests python requirements") {
                sh """
                    sed -i 's/python3-indy.*/python3-indy==${indySDKVersions.pypi}/g' ./system/requirements.txt
                    #sed -i 's/indy-plenum.*/indy-plenum==${indyPlenumVersions.pypi}/g' ./system/requirements.txt
                    #sed -i 's/indy-crypto.*/indy-crypto==${indyCryptoVersions.pypi}/g' ./system/requirements.txt
                """
            }

            stage("[${testGroup}] Cleanup docker") {
                dockerClean()
            }

            stage("[${testGroup}] Prepare docker env") {
                withEnv([
                    "INDY_NODE_REPO_COMPONENT=${config.repoChannel}",
                    "LIBINDY_CRYPTO_VERSION=${indyCryptoVersions.debian}",
                    "PYTHON3_LIBINDY_CRYPTO_VERSION=${indyCryptoVersions.debian}",
                    "INDY_PLENUM_VERSION=${indyPlenumVersions.debian}",
                    "INDY_NODE_VERSION=${config.pkgVersion}",
                    "LIBINDY_REPO_COMPONENT=${indySDKVersions.debian == indySDKVersions.pypi ? 'stable' : 'master'}",
                    "LIBINDY_VERSION=${indySDKVersions.debian}",
                ]) {
                    sh "./system/docker/prepare.sh $systemTestsNetwork"
                }
            }

            try {
                def err
                String testReportFileNameXml = "system_tests_${testGroup}_report.${config.repoChannel}.xml"
                String testReportFileNamePlain = "system_tests_${testGroup}_report.${config.repoChannel}.txt"
                String testTargets = config.testSchema[testGroup].collect{"system/indy-node-tests/$it"}.join(' ')
                String buildLogsDir = "_build/logs"
                String gatherLogsOpt = config.gatherLogs ? ' --gatherlogs' : ''

                try {
                    stage("[${testGroup}] Run tests") {
                        sh """
                            bash -c "\
                                set -o pipefail; \
                                ./system/docker/run.sh \
                                    \\"$testTargets\\" \
                                    \\"-l -vv --junit-xml=$testReportFileNameXml ${gatherLogsOpt} --logsdir=${buildLogsDir}\\" \
                                    \\"$systemTestsNetwork\\" 2>&1 | tee $testReportFileNamePlain;\
                            "
                        """
                    }
                } catch (_err) {
                    err = _err
                    throw _err
                } finally {
                    stage("[${testGroup}] Upload test report") {
                        sh "ls -la *report* || true"
                        if (err) {
                            archiveArtifacts artifacts: testReportFileNamePlain, allowEmptyArchive: true
                            archiveArtifacts artifacts: "$buildLogsDir/**/*", allowEmptyArchive: true
                        }
                        junit testResults: testReportFileNameXml, allowEmptyResults: true
                    }
                }
            } catch (Exception exc) {
                echo "$prefix: fail: $exc"
                throw exc
            } finally {
                stage("[${testGroup}] Cleanup docker") {
                    dockerClean()
                }
            }
        }
    }

    nodeWrapper("ubuntu") {
        stage("Checkout SCM") {
            if (config.srcVersion) {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: config.srcVersion]],
                    userRemoteConfigs: [[
                        url: config.indyNodeRepoUrl,
                    ]]
                ])
            } else {
                checkout scm
            }
        }

        stage("Get versions of dependencies") {
            String pipLogName = "pip.intsall.log"
            def uid = sh(returnStdout: true, script: 'id -u').trim()
            docker.build("hyperledger/indy-node-ci", "--build-arg uid=$uid -f ci/ubuntu.dockerfile ci").inside {
                sh """
                    pip install .[tests] >$pipLogName
                """

                indyPlenumVersions.pypi = sh(returnStdout: true, script: """
                    grep "^Collecting indy-plenum==" $pipLogName | awk '{print \$2}' | awk -F'==' '{print \$2}'
                """).trim()
                indyPlenumVersions.debian = indyPlenumVersions.pypi.replaceAll(/\.?(dev|rc)(.*)/, "~\$1\$2")
                echo "indy-plenum versions: $indyPlenumVersions"

                indySDKVersions.pypi = sh(returnStdout: true, script: """
                    grep "^Collecting python3-indy==" $pipLogName | awk '{print \$2}' | awk -F'==' '{print \$2}'
                """).trim()
                indySDKVersions.debian = indySDKVersions.pypi.replaceAll(/-(dev|rc)-(.*)/, "~\$2")
                echo "indy-sdk version: ${indySDKVersions}"

                indyCryptoVersions.pypi = sh(returnStdout: true, script: """
                    grep "^Collecting indy-crypto==" $pipLogName | awk '{print \$2}' | awk -F'==' '{print \$2}'
                """).trim()
                indyCryptoVersions.debian = indyCryptoVersions.pypi.replaceAll(/-(dev|rc)-(.*)/, "~\$2")
                echo "indy-crypto version: ${indyCryptoVersions}"
            }

            if (!(indyPlenumVersions.debian && indySDKVersions.debian && indyCryptoVersions.debian)) {
                error "Failed to get versions for indy-plenum or indy-crypto or indy-sdk"
            }
        }
    }

    Map builds = [:]
    for (int i = 0; i < config.testSchema.size(); i++) {
        String testNames = config.testSchema[i].join(' ')
        Boolean isFirst = (i == 0)
        int testGroup = i
        builds[testNames] = {
            stage("Run ${testNames}") {
                nodeWrapper('ubuntu') {
                    runTest(testGroup)
                }
            }
        }
    }
    builds.failFast = false

    parallel builds
}

return this;
