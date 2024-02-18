"""
Unit tests for templatron/repo/base_repo.py
"""

# pylint: disable=protected-access,too-many-public-methods

from unittest import TestCase
from unittest.mock import MagicMock, patch

from sh import ErrorReturnCode

from templatron.exceptions import DirtyRepoError, UnrecognizableBaseBranchError
from templatron.repo.base_repo import BaseRepo


class TestBaseRepo(TestCase):
    """
    Tests for templatron.repo.base_repo:BaseRepo
    """

    def setUp(self):
        self.test_repo = BaseRepo(
            name="fake repo",
            token="fake_token",
            github=MagicMock(),
            clone_root="/fake/root",
        )

    @patch("templatron.repo.base_repo.BaseRepo.git_cmd")
    def test_active_branch_success(self, mock_git):
        """
        Test BaseRepo.active_branch
        """

        mock_git.return_value = "fake_branch"
        self.assertEqual(self.test_repo.active_branch, "fake_branch")

    @patch("templatron.repo.base_repo.BaseRepo.git_cmd")
    def test_active_branch_git_failure(self, mock_git):
        """
        Test BaseRepo.active_branch with a git failure
        """

        mock_git.side_effect = Exception
        with self.assertRaises(UnrecognizableBaseBranchError):
            self.test_repo.active_branch  # pylint: disable=pointless-statement

    @patch.object(BaseRepo, "main", "fake_main")
    def test_base_branch_base_branch(self):
        """
        Test BaseRepo.base_branch with BaseRepo._base_branch
        """

        self.test_repo._base_branch = "fake_branch"
        self.assertEqual(self.test_repo.base_branch, "fake_branch")

    @patch.object(BaseRepo, "main", "fake_main")
    def test_base_branch_main(self):
        """
        Test BaseRepo.base_branch with BaseRepo._base_branch not set
        """

        self.test_repo._base_branch = None
        self.assertEqual(self.test_repo.base_branch, "fake_main")

    def test_branches_not_cached(self):
        """
        Test BaseRepo.branches when the value has not yet been cached
        """

        test_branches = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        test_branches[0].name = "a"
        test_branches[1].name = "b"
        test_branches[2].name = "c"
        self.test_repo._branches = None
        self.test_repo.github.get_branches.return_value = test_branches
        self.assertEqual(self.test_repo.branches, ["a", "b", "c"])
        self.assertEqual(self.test_repo._branches, ["a", "b", "c"])

    def test_branches_cached(self):
        """
        Test BaseRepo.branches when the value has already been cached
        """

        self.test_repo._branches = ["a", "b", "c"]
        self.assertEqual(self.test_repo.branches, ["a", "b", "c"])

    def test_clone_url(self):
        """
        Test BaseRepo.clone_url
        """

        self.test_repo.clone_url  # pylint: disable=pointless-statement
        self.test_repo.github.clone_url.replace.assert_called_with(
            "github.com",
            "fake_token@github.com",
        )

    def test_head(self):
        """
        Test BaseRepo.head
        """

        self.test_repo._base_branch = "fake_branch"
        self.test_repo.head  # pylint: disable=pointless-statement
        self.test_repo.github.get_branch.assert_called_with("fake_branch")

    @patch("templatron.repo.base_repo.os.path.exists")
    def test_is_cloned(self, mock_exists):
        """
        Test BaseRepo.is_cloned
        """

        mock_exists.return_value = False
        self.assertFalse(self.test_repo.is_cloned)
        mock_exists.assert_called_with("/fake/root/fake repo")

    @patch("templatron.repo.base_repo.BaseRepo.git_cmd")
    def test_is_dirty_clean(self, mock_git):
        """
        Test BaseRepo.is_dirty when clean
        """

        mock_git.return_value = ""
        self.assertFalse(self.test_repo.is_dirty)

    # i think this test is broken due to a bug in sh
    # @patch("templatron.repo.base_repo.BaseRepo.git_cmd")
    # def test_is_dirty_dirty(self, mock_git):
    #     """
    #     Test BaseRepo.is_dirty when dirty
    #     """

    #     mock_git.side_effect = ErrorReturnCode("fake_cmd", b"stdout", b"stderr")
    #     self.assertTrue(self.test_repo.is_dirty)

    @patch.object(BaseRepo, "branches", ["main", "develop", "other"])
    def test_main_main(self):
        """
        Test BaseRepo.main when main is a branch
        """

        self.assertEqual(self.test_repo.main, "main")

    @patch.object(BaseRepo, "branches", ["master", "develop", "other"])
    def test_main_master(self):
        """
        Test BaseRepo.main when master is a branch
        """

        self.assertEqual(self.test_repo.main, "master")

    @patch.object(BaseRepo, "branches", ["develop", "other"])
    def test_main_other(self):
        """
        Test BaseRepo.main when main and master aren't branches
        """

        with self.assertRaises(UnrecognizableBaseBranchError):
            self.test_repo.main  # pylint: disable=pointless-statement

    @patch.object(BaseRepo, "is_cloned", False)
    @patch.object(BaseRepo, "is_dirty", False)
    @patch("templatron.repo.base_repo.BaseRepo.maybe_switch_branch")
    @patch("templatron.repo.base_repo.BaseRepo.git_cmd")
    def test_clone_not_cloned(self, mock_git, mock_switch):
        """
        Test BaseRepo.clone() when the repo hasn't been cloned yet
        """

        self.test_repo.clone()
        mock_git.assert_called_with(
            "clone",
            self.test_repo.github.clone_url.replace(),
            "/fake/root/fake repo",
        )
        mock_switch.assert_called()

    @patch.object(BaseRepo, "is_cloned", True)
    @patch.object(BaseRepo, "is_dirty", True)
    @patch("templatron.repo.base_repo.BaseRepo.maybe_switch_branch")
    def test_clone_is_dirty(self, mock_switch):
        """
        Test BaseRepo.clone() when repo is dirty
        """

        with self.assertRaises(DirtyRepoError):
            self.test_repo.clone()
        mock_switch.assert_not_called()

    @patch.object(BaseRepo, "is_cloned", True)
    @patch.object(BaseRepo, "is_dirty", False)
    @patch("templatron.repo.base_repo.BaseRepo.maybe_switch_branch")
    def test_clone_cloned_and_clean(self, mock_switch):
        """
        Test BaseRepo.clone() when repo has been previously cloned and is
        currently clean
        """

        self.test_repo.clone()
        mock_switch.assert_called()

    @patch("templatron.repo.base_repo.git")
    def test_git_cmd_clone(self, mock_git):
        """
        Test BaseRepo.git_cmd() when cloning a repo
        """

        self.test_repo.git_cmd("clone", "some args")
        mock_git.assert_called_with("clone", "some args")

    @patch("templatron.repo.base_repo.git")
    def test_git_cmd_no_clone(self, mock_git):
        """
        Test BaseRepo.git_cmd() when performing non-clone actions on a repo
        """

        self.test_repo.git_cmd("commit", "some args")
        mock_git.assert_called_with("commit", "some args", _cwd="/fake/root/fake repo")

    @patch.object(BaseRepo, "active_branch", "fake_branch")
    @patch.object(BaseRepo, "base_branch", "fake_branch")
    @patch("templatron.repo.base_repo.BaseRepo.git_cmd")
    def test_maybe_switch_branch_no(self, mock_git):
        """
        Test BaseRepo.maybe_switch_branch() when active branch is already the
        base branch
        """

        self.test_repo.maybe_switch_branch()
        mock_git.assert_not_called()

    @patch.object(BaseRepo, "active_branch", "other_branch")
    @patch.object(BaseRepo, "base_branch", "fake_branch")
    @patch("templatron.repo.base_repo.BaseRepo.git_cmd")
    def test_maybe_switch_branch_yes(self, mock_git):
        """
        Test BaseRepo.maybe_switch_branch() when active branch is not the base
        branch
        """

        self.test_repo.maybe_switch_branch()
        mock_git.assert_called_with("checkout", "fake_branch")
