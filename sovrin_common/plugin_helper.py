import os

from sovrin_common.config_util import getConfig


def writeAnonCredPlugin(baseDir, reloadTestModules:bool=False):
    config = getConfig()
    pluginsPath = os.path.expanduser(os.path.join(baseDir, config.PluginsDir))

    if not os.path.exists(pluginsPath):
        os.makedirs(pluginsPath)

    initFile = pluginsPath + "/__init__.py"
    with open(initFile, "a"):
        pass

    anonPluginFilePath = pluginsPath + "/anoncreds.py"
    anonPluginContent = "" \
                        "import importlib\n" \
                        "\n" \
                        "import anoncreds.protocol.issuer\n" \
                        "import anoncreds.protocol.verifier\n" \
                        "import anoncreds.protocol.prover\n" \
                        "\n" \
                        "import sovrin_client.anon_creds.issuer\n" \
                        "import sovrin_client.anon_creds.verifier\n"\
                        "import sovrin_client.anon_creds.prover\n" \
                        "\n" \
                        "Name = \"Anon creds\"\n" \
                        "Version = 1.1\n" \
                        "SovrinVersion = 1.1\n" \
                        "\n" \
                        "sovrin_client.anon_creds.issuer.Credential = anoncreds.protocol.types.Credential\n" \
                        "sovrin_client.anon_creds.issuer.AttribType = anoncreds.protocol.types.AttribType\n" \
                        "sovrin_client.anon_creds.issuer.AttribDef = anoncreds.protocol.types.AttribDef\n" \
                        "sovrin_client.anon_creds.issuer.Attribs = anoncreds.protocol.types.Attribs\n" \
                        "sovrin_client.anon_creds.issuer.AttrRepo = anoncreds.protocol.attribute_repo.AttrRepo\n" \
                        "sovrin_client.anon_creds.issuer.InMemoryAttrRepo = anoncreds.protocol.attribute_repo.InMemoryAttrRepo\n" \
                        "sovrin_client.anon_creds.issuer.Issuer = anoncreds.protocol.issuer.Issuer\n" \
                        "sovrin_client.anon_creds.prover.Prover = anoncreds.protocol.prover.Prover\n" \
                        "sovrin_client.anon_creds.verifier.Verifier = anoncreds.protocol.verifier.Verifier\n" \
                        "sovrin_client.anon_creds.proof_builder.ProofBuilder = anoncreds.protocol.proof_builder.ProofBuilder\n" \
                        "sovrin_client.anon_creds.proof_builder.Proof = anoncreds.protocol.types.Proof\n" \
                        "sovrin_client.anon_creds.cred_def.CredDef = anoncreds.protocol.credential_definition.CredentialDefinition\n" \

    modules_to_reload = ["sovrin_client.cli.cli"]
    test_modules_to_reload = [
        "sovrin_client.test.helper", "sovrin_client.test.cli.helper",
        "sovrin_client.test.anon_creds.conftest",
        "sovrin_client.test.anon_creds.test_anon_creds",
        # "sovrin_client.test.anon_creds.anon_creds_demo"
    ]

    if reloadTestModules:
        modules_to_reload.extend(test_modules_to_reload)

    reload_module_code = \
        "reload_modules = " + str(modules_to_reload) + "\n" \
        "for m in reload_modules:\n" \
        "   try:\n" \
        "       module_obj = importlib.import_module(m)\n" \
        "       importlib.reload(module_obj)\n" \
        "   except AttributeError as ae:\n" \
        "       print(\"Plugin loading failed: module {}, detail: {}\".format(m, str(ae)))\n" \
        "\n"

    anonPluginContent += reload_module_code
    with open(anonPluginFilePath, "w") as f:
        f.write(anonPluginContent)
