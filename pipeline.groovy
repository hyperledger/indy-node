#!/usr/bin/env groovy

def init() {
    return [
        stages : [
            // stages
            staticVerify: params.staticVerify ?: true,
            runTests: params.runTests ?: true,
            sendNotif: params.sendNotif ?: false,
        ],

        // other
        failFast: params.failFast ?: false,
        dryRun: params.dryRun ?: true
    ]
}

return this;
