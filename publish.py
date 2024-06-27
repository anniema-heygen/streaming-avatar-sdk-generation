import subprocess

def publish():
    subprocess.run([
    "npm", "init",
    "--scope@heygen"
    ])

    subprocess.run([
    "npm", "publish",
    "--access", "public"
    ])

if __name__ == "__main__":
    publish()