export post_python_hook_description="Collecting static files and compiling translations"
post_python_hook() {
  remote_command "cd $RELEASE_DIRECTORY && pipx run uv run manage.py collectstatic"
  remote_command "cd $RELEASE_DIRECTORY && pipx run uv run manage.py compilemessages -l fr --ignore .venv"
}
