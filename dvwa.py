#!/usr/bin/env python3
# dvwa.py - place DVWA files flat under /var/www/html/DVWA and set uploads permissions.
# Run as root: sudo python3 dvwa.py
#
# WARNING: destructive actions (rm -rf) and insecure perms (chmod 777) are used for testing only.

import os
import shutil
import subprocess
import sys
import tempfile

def run(cmd, check=False, timeout=300):
    print(f"\n--- Running: {cmd}")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        print(f"Timed out: {e}")
        return None
    if r.stdout:
        print(r.stdout.strip())
    if r.stderr:
        print(r.stderr.strip())
    print("Exit code:", r.returncode)
    if check and r.returncode != 0:
        print("Command failed and check=True; exiting.")
        sys.exit(r.returncode)
    return r

def run_mysql_statements(statements):
    sql = " ".join(statements)
    cmd = f"mysql -e \"{sql}\""
    return run(cmd)

def flatten_and_deploy(src_dir, dest_dir):
    """
    Ensure contents of src_dir (possibly containing a nested DVWA folder) end up directly under dest_dir.
    """
    print(f"\nPreparing to deploy from {src_dir} -> {dest_dir}")

    # Remove existing dest dir if present (as requested in original commands)
    if os.path.exists(dest_dir):
        print(f"Removing existing {dest_dir}")
        shutil.rmtree(dest_dir)

    # Create destination
    os.makedirs(dest_dir, exist_ok=True)

    # If repo created a nested 'DVWA' directory (common), use it
    nested = None
    candidate1 = os.path.join(src_dir, "DVWA")
    if os.path.isdir(candidate1):
        nested = candidate1

    # If there's exactly one top-level directory inside src_dir, and it contains index.php, use it
    if nested is None:
        entries = [e for e in os.listdir(src_dir) if not e.startswith('.')]
        if len(entries) == 1 and os.path.isdir(os.path.join(src_dir, entries[0])):
            candidate = os.path.join(src_dir, entries[0])
            # heuristic: if candidate contains index.php or config files, treat as nested
            if any(os.path.exists(os.path.join(candidate, f)) for f in ("index.php", "config", "DVWA")):
                nested = candidate

    source_root = nested if nested else src_dir
    print(f"Using source root: {source_root}")

    # Copy all files from source_root to dest_dir (preserve structure)
    for root, dirs, files in os.walk(source_root):
        rel = os.path.relpath(root, source_root)
        dest_root = os.path.join(dest_dir, rel) if rel != "." else dest_dir
        os.makedirs(dest_root, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(dest_root, f)
            shutil.copy2(src_file, dst_file)

    print(f"Deployment complete: files are under {dest_dir}")

def ensure_uploads_permissions(dest_dir):
    """
    Set ownership and permissions for hackable/uploads. Handle both possible nested and flattened locations.
    """
    # possible paths (user originally referenced /var/www/html/DVWA/DVWA/hackable/uploads)
    candidates = [
        os.path.join(dest_dir, "DVWA", "hackable", "uploads"),  # nested case
        os.path.join(dest_dir, "hackable", "uploads")           # flattened case
    ]
    found = False
    for p in candidates:
        if os.path.isdir(p):
            found = True
            print(f"Setting ownership and permissions on: {p}")
            # chown www-data:www-data recursively for DVWA dir (makes webserver owner)
            run(f"chown -R www-data:www-data \"{os.path.dirname(p)}\"")
            # make uploads writable by webserver. For DVWA lab it's common to use 777; warn user.
            run(f"chmod -R 0777 \"{p}\"")
    if not found:
        print("Warning: uploads directory not found in expected locations. Listing deployed tree for debugging:")
        for root, dirs, files in os.walk(dest_dir):
            level = root.replace(dest_dir, "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            if level > 4:  # avoid extremely deep print
                break

def main():
    if os.geteuid() != 0:
        print("ERROR: This script must be run as root. Use: sudo python3 dvwa.py")
        sys.exit(1)

    # Temporary clone area
    tmpdir = tempfile.mkdtemp(prefix="dvwa_clone_")
    print("Using temporary directory:", tmpdir)

    try:
        # Remove any existing DVWA under /var/www/html (per original commands)
        run("cd /var/www/html/ && rm -rf DVWA", check=False)

        # Clone into temporary directory
        run(f"git clone https://github.com/Mokshithv/DVWA.git \"{tmpdir}\"", check=True)

        # If there is a zip inside, try to unzip (original command included unzip)
        # Safely attempt to unzip any DVWA.zip found in tmpdir or its top-level child
        for candidate_dir in [tmpdir] + [os.path.join(tmpdir, d) for d in os.listdir(tmpdir) if os.path.isdir(os.path.join(tmpdir, d))]:
            zip_path = os.path.join(candidate_dir, "DVWA.zip")
            if os.path.isfile(zip_path):
                print("Found DVWA.zip at", zip_path, "-> attempting to unzip")
                run(f"unzip -o \"{zip_path}\" -d \"{candidate_dir}\"", check=False)

        # Deploy: flatten to /var/www/html/DVWA
        dest = "/var/www/html/DVWA"
        flatten_and_deploy(tmpdir, dest)

        # Start mysql
        run("systemctl start mysql", check=False)

        # Execute MySQL statements (non-interactive). If root requires password this will fail.
        mysql_cmds = [
            "drop database if exists dvwa;",
            "drop user if exists 'admin'@'127.0.0.1';",
            "create database dvwa;",
            "create user 'admin'@'127.0.0.1' identified by 'password';",
            "grant all privileges on dvwa.* to 'admin'@'127.0.0.1';",
            "flush privileges;"
        ]
        run_mysql_statements(mysql_cmds)

        # Start apache and tweak php.ini if present
        run("systemctl start apache2", check=False)
        php_ini = "/etc/php/8.4/apache2/php.ini"
        if os.path.exists(php_ini):
            run(f"sed -i 's/^allow_url_include\\s*=.*/allow_url_include = On/' {php_ini}", check=False)
        else:
            print(f"Warning: {php_ini} not found. Update path if your PHP version differs.")

        # Restart apache
        run("systemctl stop apache2", check=False)
        run("systemctl start apache2", check=False)

        # Set ownership and permissions for uploads directory
        ensure_uploads_permissions(dest)

        # Also set webserver ownership on entire DVWA folder (recommended for lab)
        run(f"chown -R www-data:www-data \"{dest}\"", check=False)

        # Open browser if in graphical session (best-effort; will do nothing in headless)
        run("firefox http://127.0.0.1/DVWA/setup.php &", check=False)

        print("\nDone.")

    finally:
        # cleanup temp dir
        try:
            shutil.rmtree(tmpdir)
        except Exception as e:
            print("Failed to remove tempdir:", e)

if __name__ == "__main__":
    main()
