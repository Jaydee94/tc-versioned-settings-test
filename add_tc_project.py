import click
import requests
import logging


@click.command()
@click.option(
    "--url",
    default="http://localhost:8112",
    help="TeamCity server URL (default: http://localhost:8112)",
)
@click.option(
    "--bearer-token", prompt=True, hide_input=True, help="Your TeamCity bearer token"
)
@click.option(
    "--project_name",
    prompt="Enter the name of the new project",
    help="Name of the new TeamCity project",
)
def main(url, bearer_token, project_name):
    teamcity_url = url.rstrip("/")

    # Prepare authorization header with bearer token
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Check if the project already exists
    try:
        check_project_url = f"{teamcity_url}/app/rest/projects/{project_name}"
        response = requests.get(check_project_url, headers=headers)
        response.raise_for_status()
        project_exists = True
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            project_exists = False
        else:
            click.echo(f"Failed to check project existence: {e}")
            return

    if project_exists:
        click.echo(f"Project '{project_name}' already exists. Skipping creation.")
    else:
        # Creating a new project
        try:
            click.echo(f"Creating new project '{project_name}'...")
            create_project_url = f"{teamcity_url}/app/rest/projects"
            create_project_payload = {"name": project_name}
            response = requests.post(
                create_project_url, json=create_project_payload, headers=headers
            )
            response.raise_for_status()  # Raise an error for non-2xx responses
            click.echo(f"Project '{project_name}' created successfully!")
        except requests.HTTPError as e:
            click.echo(f"Error occurred while creating the project: {e}")
            return

    # Add a new VCS root to the project
    vcs_root_name = f"{project_name}_VCS_Root"
    try:
        click.echo("Adding a new VCS root to the project...")
        add_vcs_root_url = f"{teamcity_url}/app/rest/vcs-roots"
        add_vcs_root_payload = {
            "id": vcs_root_name,
            "name": vcs_root_name,
            "vcsName": "jetbrains.git",
            "project": {"id": project_name},
            "properties": {
                "property": [
                    {"name": "authMethod", "value": "ANONYMOUS"},
                    {"name": "branch", "value": "refs/heads/main"},
                    {
                        "name": "url",
                        "value": "https://github.com/Jaydee94/tc-versioned-settings-test.git",
                    },
                ]
            },
        }
        response = requests.post(
            add_vcs_root_url, json=add_vcs_root_payload, headers=headers
        )
        response.raise_for_status()  # Raise an error for non-2xx responses
        click.echo("VCS root added successfully!")
    except requests.HTTPError as e:
        click.echo(f"Error occurred while adding VCS root: {e}")
        return

    # Enabling versioned settings for the project
    try:
        click.echo("Enabling versioned settings for the project...")
        enable_settings_url = (
            f"{teamcity_url}/app/rest/projects/{project_name}/versionedSettings/config"
        )
        enable_settings_payload = {
            "format": "kotlin",
            "synchronizationMode": "enabled",
            "allowUIEditing": "true",
            "storeSecureValuesOutsideVcs": "true",
            "portableDsl": "true",
            "showSettingsChanges": "true",
            "vcsRootId": vcs_root_name,
            "buildSettingsMode": "alwaysUseCurrent",
            "importDecision": "importFromVCS",
        }
        response = requests.put(
            enable_settings_url, json=enable_settings_payload, headers=headers
        )
        response.raise_for_status()  # Raise an error for non-2xx responses
        click.echo("Versioned settings enabled successfully!")
    except requests.HTTPError as e:
        click.echo(f"Error occurred while enabling versioned settings: {e}")
        return


if __name__ == "__main__":
    main()
