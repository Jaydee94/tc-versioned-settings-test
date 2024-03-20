import jetbrains.buildServer.configs.kotlin.*
import jetbrains.buildServer.configs.kotlin.buildSteps.script
import jetbrains.buildServer.configs.kotlin.vcs.GitVcsRoot

version = "2023.11"

project {

    vcsRoot(VersionedSettings_1)

    buildType(TestBuild)
}

object TestBuild : BuildType({
    name = "TestBuild"

    steps {
        script {
            name = "Test"
            id = "Test"
            scriptContent = """echo "This is a test""""
        }
    }
})

object VersionedSettings_1 : GitVcsRoot({
    id("VersionedSettings")
    name = "VersionedSettings"
    url = "https://github.com/Jaydee94/tc-versioned-settings-test.git"
    branch = "main"
})
