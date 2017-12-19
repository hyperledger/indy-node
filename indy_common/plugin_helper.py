import os


def writeAnonCredPlugin(plugins_path, reloadTestModules: bool=False):
    if not os.path.exists(plugins_path):
        os.makedirs(plugins_path)

    initFile = os.path.join(plugins_path, "__init__.py")
    if not os.path.exists(initFile):
        with open(initFile, "a"):
            pass

    anonPluginFilePath = os.path.join(plugins_path, "anoncreds.py")
    if not os.path.exists(initFile):
        anonPluginContent = "" \
                            "import importlib\n" \
                            "\n" \
                            "import anoncreds.protocol.issuer\n" \
                            "import anoncreds.protocol.verifier\n" \
                            "import anoncreds.protocol.prover\n" \
                            "\n" \
                            "import indy_client.anon_creds.issuer\n" \
                            "import indy_client.anon_creds.verifier\n"\
                            "import indy_client.anon_creds.prover\n" \
                            "\n" \
                            "Name = \"Anon creds\"\n" \
                            "Version = 1.1\n" \
                            "IndyVersion = 1.1\n" \
                            "\n" \
                            "indy_client.anon_creds.issuer.Credential = anoncreds.protocol.types.Credential\n" \
                            "indy_client.anon_creds.issuer.AttribType = anoncreds.protocol.types.AttribType\n" \
                            "indy_client.anon_creds.issuer.AttribDef = anoncreds.protocol.types.AttribDef\n" \
                            "indy_client.anon_creds.issuer.Attribs = anoncreds.protocol.types.Attribs\n" \
                            "indy_client.anon_creds.issuer.AttrRepo = anoncreds.protocol.attribute_repo.AttrRepo\n" \
                            "indy_client.anon_creds.issuer.InMemoryAttrRepo = anoncreds.protocol.attribute_repo.InMemoryAttrRepo\n" \
                            "indy_client.anon_creds.issuer.Issuer = anoncreds.protocol.issuer.Issuer\n" \
                            "indy_client.anon_creds.prover.Prover = anoncreds.protocol.prover.Prover\n" \
                            "indy_client.anon_creds.verifier.Verifier = anoncreds.protocol.verifier.Verifier\n" \
                            "indy_client.anon_creds.proof_builder.ProofBuilder = anoncreds.protocol.proof_builder.ProofBuilder\n" \
                            "indy_client.anon_creds.proof_builder.Proof = anoncreds.protocol.types.Proof\n" \
                            "indy_client.anon_creds.cred_def.CredDef = anoncreds.protocol.credential_definition.CredentialDefinition\n" \

        modules_to_reload = ["indy_client.cli.cli"]
        test_modules_to_reload = [
            "indy_client.test.helper", "indy_client.test.cli.helper",
            "indy_client.test.anon_creds.conftest",
            "indy_client.test.anon_creds.test_anon_creds",
            # "indy_client.test.anon_creds.anon_creds_demo"
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
