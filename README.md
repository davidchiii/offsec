# offsec-materials


# Develop New Challenges

- Write the new challenge
- Copy existing `challeng.json` and modify the values
- Set a `listen_port` for the new challenge
- Ask Osiris Infrastruction Manager to open such ports on the server
- Modify `Dockerfile` to make sure the dropflag works
- Build the image on the server
- Run `~/restart_chalbroker.sh` on the server
- Run `./upload_chal.py ../../chals/heap_1/Overflow-20.04` to update chal info
# System
- restart every 4AM

# Docker pull
- It's too old to pull new images, Infra Manager told me it's dangerous to update docker
- I have a way to use new images by using docker `save` and `load`
- Build the image on your computer and `docker save` to a file
- scp the file to the server
- `docker load` from the file

# No response after chalbroker restarts
- Remove new chals
- Run `~/restart_chalbroker`

