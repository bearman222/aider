import os
import tempfile
import unittest
from subprocess import CompletedProcess
from unittest.mock import patch

from aider.repomap import RepoMap


class TestRepoMap(unittest.TestCase):
    def test_get_repo_map(self):
        # Create a temporary directory with sample files for testing
        test_files = [
            "test_file1.py",
            "test_file2.py",
            "test_file3.md",
            "test_file4.json",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            for file in test_files:
                with open(os.path.join(temp_dir, file), "w") as f:
                    f.write("")

            repo_map = RepoMap(root=temp_dir)
            other_files = [os.path.join(temp_dir, file) for file in test_files]
            result = repo_map.get_repo_map([], other_files)

            # Check if the result contains the expected tags map
            self.assertIn("test_file1.py", result)
            self.assertIn("test_file2.py", result)
            self.assertIn("test_file3.md", result)
            self.assertIn("test_file4.json", result)

    def test_get_repo_map_with_identifiers(self):
        # Create a temporary directory with a sample Python file containing identifiers
        test_file1 = "test_file_with_identifiers.py"
        file_content1 = """\
class MyClass:
    def my_method(self, arg1, arg2):
        return arg1 + arg2

def my_function(arg1, arg2):
    return arg1 * arg2
"""

        test_file2 = "test_file_import.py"
        file_content2 = """\
from test_file_with_identifiers import MyClass

obj = MyClass()
print(obj.my_method(1, 2))
print(my_function(3, 4))
"""

        test_file3 = "test_file_pass.py"
        file_content3 = "pass"

        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, test_file1), "w") as f:
                f.write(file_content1)

            with open(os.path.join(temp_dir, test_file2), "w") as f:
                f.write(file_content2)

            with open(os.path.join(temp_dir, test_file3), "w") as f:
                f.write(file_content3)

            repo_map = RepoMap(root=temp_dir)
            other_files = [
                os.path.join(temp_dir, test_file1),
                os.path.join(temp_dir, test_file2),
                os.path.join(temp_dir, test_file3),
            ]
            result = repo_map.get_repo_map([], other_files)

            # Check if the result contains the expected tags map with identifiers
            self.assertIn("test_file_with_identifiers.py", result)
            self.assertIn("MyClass", result)
            self.assertIn("my_method", result)
            self.assertIn("my_function", result)
            self.assertIn("test_file_pass.py", result)

    def test_check_for_ctags_failure(self):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("ctags not found")
            repo_map = RepoMap()
            result = repo_map.check_for_ctags()
            self.assertFalse(result)

    def test_check_for_ctags_success(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=["ctags", "--version"],
                returncode=0,
                stdout=(
                    b'{"_type": "tag", "name": "status", "path": "aider/main.py", "pattern": "/^   '
                    b' status = main()$/", "kind": "variable"}'
                ),
            )
            repo_map = RepoMap()
            result = repo_map.check_for_ctags()
            self.assertTrue(result)

    def test_get_repo_map_without_ctags(self):
        # Create a temporary directory with a sample Python file containing identifiers
        test_files = [
            "test_file_without_ctags.py",
            "test_file1.txt",
            "test_file2.md",
            "test_file3.json",
            "test_file4.html",
            "test_file5.css",
            "test_file6.js",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            for file in test_files:
                with open(os.path.join(temp_dir, file), "w") as f:
                    f.write("")

            repo_map = RepoMap(root=temp_dir)
            repo_map.has_ctags = False  # force it off

            other_files = [os.path.join(temp_dir, file) for file in test_files]
            result = repo_map.get_repo_map([], other_files)

            # Check if the result contains each specific file in the expected tags map without ctags
            for file in test_files:
                self.assertIn(file, result)


if __name__ == "__main__":
    unittest.main()
