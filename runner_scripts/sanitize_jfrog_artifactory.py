###
#USAGE:
#       library "pyartifactory" is needed to run the script
#       install it by "pip install pyartifactory"
# for running:
#       python sanitize_jfrog_artifactory.py USERNAME PASSWORD
###

import pyartifactory
import sys

ARTIFACTORY_BASE_URL = "https://artifacts.lulzbot.com/artifactory"

if len(sys.argv) != 3:
    print("Usage: python sanitize_jfrog_artifactory.py USERNAME PASSWORD\n"
          "Also needs pyartifactory library to run this script")
    exit()

USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]

def initialize_artifactory():
    return pyartifactory.Artifactory(url=ARTIFACTORY_BASE_URL, auth=(USERNAME, PASSWORD))

ARTIFACT_PATHS = {"cura-le/lulzbot/curaenginele"                        : True,
                  "cura-le/lulzbot/curale"                              : True,
                  "cura-le/lulzbot/fdm_printer"                         : True,
                  "cura-le/lulzbot/uraniumle"                           : True,
                  "cura-le/_/curaenginele"                              : True,
                  "cura-le/_/curale"                                    : True,
                  "cura-le/_/fdm_printer"                               : True,
                  "cura-le/_/uraniumle"                                 : True,
                  "cura-le-conan-cci-remote-cache/lulzbot/curaenginele" : True,
                  "cura-le-conan-cci-remote-cache/lulzbot/curale"       : True,
                  "cura-le-conan-cci-remote-cache/lulzbot/fdm_printer"  : True,
                  "cura-le-conan-cci-remote-cache/lulzbot/uraniumle"    : True,
                  "cura-le-conan-cci-remote-cache/_/curaenginele"       : True,
                  "cura-le-conan-cci-remote-cache/_/curale"             : True,
                  "cura-le-conan-cci-remote-cache/_/fdm_printer"        : True,
                  "cura-le-conan-cci-remote-cache/_/uraniumle"          : True,
                  "cura_le_conan-cci-remote-cache"	                    : False}


def list_artifacts(artifactory_client, artifact_path, depth):
    try:
        return artifactory_client.artifacts.list(f"{artifact_path}/", depth).files
    except pyartifactory.exception.ArtifactoryError as e:
        # artifact_path was not found in the repository, so we return empty dict
        # print(f"Repository {artifact_path} does not exist")
        return {}


def delete_artifact(artifactory_client, artifact_path):
    artifactory_client.artifacts.delete(artifact_path)


def artifact_modified_by_anonymous(artifactory_client, artifact_path):
    return str(artifactory_client.artifacts.info(artifact_path).createdBy) == "anonymous"


def process_artifact(artifactory_client, artifact_path, sequence_nr, depth):
    artifact_files =  list_artifacts(artifactory_client, artifact_path, depth)
    for artifact in artifact_files:
        artifact_file_path = f"{artifact_path}{artifact.uri}"
        if artifact_modified_by_anonymous(artifactory_client, artifact_file_path):
            sequence_nr += 1
            print(f"{sequence_nr}: {artifact_file_path}")
            delete_artifact(artifactory_client, artifact_file_path)

    return sequence_nr


def main():
    artifactory_client = initialize_artifactory()

    for (artifact_path, include_depth_2) in ARTIFACT_PATHS.items():
        number_files_deleted = 0
        number_files_deleted = process_artifact(artifactory_client, artifact_path, number_files_deleted, depth=1)
        if (include_depth_2):
            process_artifact(artifactory_client, artifact_path, number_files_deleted, depth=2)

if __name__ == "__main__":
    main()
