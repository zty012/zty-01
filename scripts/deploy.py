#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path

from mpremote import commands
from mpremote.main import State


class DeploymentError(Exception):
    pass


class FileHashCache:
    """文件哈希缓存管理器 (保持不变)"""

    def __init__(self, cache_file=".filehashes"):
        self.cache_file = Path(cache_file)
        self.hashes = self._load_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.hashes, f, indent=2)

    def has_changed(self, file_path):
        current_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
        cached_hash = self.hashes.get(str(file_path))
        if cached_hash != current_hash:
            self.hashes[str(file_path)] = current_hash
            return True
        return False


class Deployer:
    def __init__(self, port=None):
        self.port = port
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.hash_cache = FileHashCache((self.project_root / ".filehashes").as_posix())

        self.state = State()
        self.state._auto_soft_reset = False

    def connect(self):
        if self.state.transport is None:
            self.state.ensure_raw_repl()

    def upload_file(self, local_path, remote_path):
        if not self.hash_cache.has_changed(local_path):
            print(f"Up to date: {local_path}")
            return False

        print(f"Upload: {local_path}")
        commands.do_filesystem_cp(
            self.state,
            str(local_path),
            f":{remote_path}",
            multiple=False,
            check_hash=False,
        )
        return True

    def deploy(self):
        self.connect()

        files = []
        for p in self.src_dir.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                rel = p.relative_to(self.src_dir).as_posix()
                files.append((p, rel))

        count = 0
        for local, remote in sorted(files):
            if self.upload_file(local, remote):
                count += 1

        self.hash_cache.save_cache()
        print("File hash cache updated.")

        # reset the device to apply changes
        commands.do_soft_reset(self.state)

        print(f"Deployment complete. {count} file(s) uploaded.")

    def disconnect(self):
        if self.state.transport:
            self.state.transport.close()


if __name__ == "__main__":
    deployer = Deployer()
    try:
        deployer.deploy()
    finally:
        deployer.disconnect()
