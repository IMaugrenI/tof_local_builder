# Real-life user journey

## Goal

Use local AI with an existing project without letting the normal builder workflow modify the original project.

## First-time journey

1. Clone the repository and run the platform-specific `start_here` command.
2. Choose the project folder you want to work with.
3. Let ToF prepare and start the local workspace.
4. Wait until the control page says **Everything ready**.
5. Choose **Open workspace**.
6. Ask the local AI to create or change something for the project.
7. Review the generated work in the separate work area.
8. Move only the parts you actually want into your real project yourself.

**Successful end result:** you have useful generated work, while the original selected project was not written to by the normal builder path.

## Typical problem

If the control page says the project is not ready:

1. confirm that the project folder still exists
2. choose **Problems & technical details**
3. run **Find a problem**
4. follow the plain-language guidance
5. use the technical activity log only if deeper details are needed

## Stop and return later

Stop with `python run.py down`.

Later run `python run.py up` and `python run.py ui`. You do not need to choose the project again unless you want to change it.
