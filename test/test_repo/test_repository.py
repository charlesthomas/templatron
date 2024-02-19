"""
Unit tests for templatron/repo/repository.py
"""

# pylint: disable=protected-access,too-many-arguments,too-many-public-methods
# pylint: disable=unused-argument

from unittest import TestCase
from unittest.mock import MagicMock, patch

from templatron.exceptions import HookFailure
from templatron.repo.repository import Repository
from templatron.repo.template import Template


class TestRepository(TestCase):
    """
    Tests for templatron.repo.template:Repository
    """

    def setUp(self):
        with patch("templatron.repo.template.BaseRepo.clone"):
            with patch("templatron.repo.template.Template.load_template_config"):
                self.template = Template(
                    name="test_template",
                    token="fake_token",
                    github=MagicMock(),
                    clone_root="fake_root",
                )
        self.test_repo = Repository(
            name="fake repo",
            token="fake_token",
            github=MagicMock(),
            clone_root="/fake/root",
            template=self.template,
        )

    @patch("templatron.repo.repository.commit_template")
    def test_commit_message(self, mock_template):
        """
        Tests Repository.commit_message, which is a wrapper function
        """

        self.template._branches = ["main"]
        mock_template.format.return_value = "Fake commit message"
        self.assertEqual(self.test_repo.commit_message, "Fake commit message")

    def test_fixing(self):
        """
        Tests Repository.fixing, which is a wrapper function
        """

        self.test_repo.operation = "fixing"
        self.assertTrue(self.test_repo.fixing)

    def test_onboarding(self):
        """
        Tests Repository.onboarding, which is a wrapper function
        """

        self.test_repo.operation = "onboarding"
        self.assertTrue(self.test_repo.onboarding)

    def test_updating(self):
        """
        Tests Repository.updating, which is a wrapper function
        """

        self.test_repo.operation = "updating"
        self.assertTrue(self.test_repo.updating)

    @patch.object(Repository, "branches", ["fake_branch"])
    @patch.object(Repository, "update_branch_name", "fake_branch")
    def test_has_update_branch(self):
        """
        Tests Repository.has_update_branch, which is a wrapper function
        """

        self.assertTrue(self.test_repo.has_update_branch)

    @patch("yaml.safe_load")
    @patch("templatron.repo.repository.open")
    def test_template_version(self, _, mock_load):
        """
        Test Repository.template_version
        """

        mock_load.return_value = {"_template_version": "abc123"}
        self.assertEqual(self.test_repo.template_version, "abc123")

    @patch.object(Repository, "has_update_branch", True)
    @patch.object(Repository, "update_branch_name", "fake_main")
    def test_needs_update_with_has_update_branch(self):
        """
        Test Repository.needs_update when an update branch exists
        """

        self.assertFalse(self.test_repo.needs_update)

    @patch.object(Repository, "has_update_branch", False)
    @patch.object(Repository, "template_version", "abc123")
    @patch.object(Template, "head", "abc123")
    def test_needs_update_with_matching_template_hash(self):
        """
        Test Repository.needs_update when last updated template hash matches
        template head
        """

        self.assertFalse(self.test_repo.needs_update)

    @patch.object(Repository, "has_update_branch", False)
    @patch.object(Repository, "template_version", "def456")
    @patch.object(Template, "head", "abc123")
    def test_needs_update_everything_else(self):
        """
        Test Repository.needs_update when:
        * update branch doesn't exist
        * answers file exists
        * last updated template hash doesn't match template head
        """

        self.assertTrue(self.test_repo.needs_update)

    @patch.object(Repository, "base_branch", "fake_main")
    def test_update_branch_name_fixing(self):
        """
        Test Repository.update_branch_name when fixing == True
        """

        self.test_repo.operation = "fixing"
        self.assertEqual(self.test_repo.update_branch_name, "fake_main")

    @patch.object(Template, "head", "abc123")
    def test_update_branch_name_not_fixing(self):
        """
        Test Repository.update_branch_name when fixing == False
        """

        self.test_repo.operation = "not_fixing"
        self.test_repo.branch_prefix = "test"
        self.test_repo.template.name = "fake_template"
        self.assertEqual(
            self.test_repo.update_branch_name,
            "test/fake_template/abc123",
        )

    @patch("templatron.repo.repository.Repository.close_pr")
    @patch("templatron.repo.repository.Repository.delete_branch")
    def test_clean_stale_branches(self, mock_delete, mock_close):
        """
        Test Repository.clean_stale_branches
        """

        mock_branch = MagicMock()
        mock_branch.name = "templatron/test_template/fake"
        mock_pr = MagicMock()
        mock_branch.commit.get_pulls.return_value = [mock_pr]
        self.test_repo.github.get_branches.return_value = [mock_branch]
        self.test_repo.clean_stale_branches()
        mock_delete.assert_called()
        mock_close.assert_called_with(mock_pr)

    def test_close_pr_dry_run(self):
        """
        Test Repository.close_pr() with a dry run.
        """

        self.test_repo.dry_run = True
        test_pr = MagicMock()
        self.test_repo.close_pr(test_pr)
        test_pr.edit.assert_not_called()

    def test_close_pr_no_dry_run(self):
        """
        Test Repository.close_pr() without a dry run.
        """

        self.test_repo.dry_run = False
        test_pr = MagicMock()
        self.test_repo.close_pr(test_pr)
        test_pr.edit.assert_called_with(state="closed")

    @patch("templatron.repo.repository.Repository.git_cmd")
    def test_confirm_changes_answers_file(self, mock_git):
        """
        Test Repository.confirm_changes() where answers file was the only
        change.
        """

        mock_git.return_value = "\n".join([self.test_repo.answers_file, ""])
        self.assertFalse(self.test_repo.confirm_changes())

    @patch("templatron.repo.repository.Repository.git_cmd")
    def test_confirm_changes_anything_else(self, mock_git):
        """
        Test Repository.confirm_changes() where anything other than the
        answers file was changed.
        """

        mock_git.return_value = "\n".join(
            [self.test_repo.answers_file, "/fake/file", ""]
        )
        self.assertTrue(self.test_repo.confirm_changes())

    @patch("templatron.repo.repository.Repository.git_cmd")
    def test_delete_branch_dry_run(self, mock_git):
        """
        Test Repository.delete_branch() with a dry run.
        """

        self.test_repo.dry_run = True
        test_branch = MagicMock()
        test_branch.name = "fake_branch"
        self.test_repo.delete_branch(test_branch)
        mock_git.assert_not_called()

    @patch("templatron.repo.repository.Repository.git_cmd")
    def test_delete_branch_no_dry_run(self, mock_git):
        """
        Test Repository.delete_branch() without a dry run.
        """

        self.test_repo.dry_run = False
        test_branch = MagicMock()
        test_branch.name = "fake_branch"
        self.test_repo.delete_branch(test_branch)
        mock_git.assert_called_with("push", "origin", "--delete", "fake_branch")

    @patch("templatron.repo.repository.Repository.update")
    def test_fix(self, mock_update):
        """
        Test Repository.fix()
        """

        self.test_repo.fix()
        mock_update.assert_called_with(operation="fixing")

    @patch("templatron.repo.repository.Repository.run_hook")
    def test_post_copier_hook(self, mock_hook):
        """
        Test Repository.post_copier_hook() which is a wrapper function
        """

        self.test_repo.post_copier_hook()
        mock_hook.assert_called_with("post-copier")

    @patch("templatron.repo.repository.Repository.run_hook")
    def test_post_push_hook(self, mock_hook):
        """
        Test Repository.post_push_hook() which is a wrapper function
        """

        self.test_repo.post_push_hook()
        mock_hook.assert_called_with("post-push")

    @patch("templatron.repo.repository.Repository.run_hook")
    def test_pre_clone_hook(self, mock_hook):
        """
        Test Repository.pre_clone_hook() which is a wrapper function
        """

        self.test_repo.pre_clone_hook()
        mock_hook.assert_called_with("pre-clone")

    @patch("templatron.repo.repository.Repository.run_hook")
    def test_pre_copier_hook(self, mock_hook):
        """
        Test Repository.pre_copier_hook() which is a wrapper function
        """

        self.test_repo.pre_copier_hook()
        mock_hook.assert_called_with("pre-copier")

    @patch("templatron.repo.repository.Repository.run_hook")
    def test_pre_push_hook(self, mock_hook):
        """
        Test Repository.pre_push_hook() which is a wrapper function
        """

        self.test_repo.pre_push_hook()
        mock_hook.assert_called_with("pre-push")

    @patch("templatron.repo.repository.Repository.run_hook")
    def test_post_clone_hook(self, mock_hook):
        """
        Test Repository.post_clone_hook() which is a wrapper function
        """

        self.test_repo.post_clone_hook()
        mock_hook.assert_called_with("post-clone")

    @patch("templatron.repo.repository.Repository.update")
    def test_onboard(self, mock_update):
        """
        Test Repository.onboard() which is a wrapper function
        """

        self.test_repo.onboard()
        mock_update.assert_called_with(operation="onboarding")

    @patch.object(Repository, "base_branch", "abc123")
    def test_open_pull_request_fixing(self):
        """
        Test Repository.open_pull_request() when current operation is 'fixing'
        """

        self.test_repo.operation = "fixing"
        self.test_repo.open_pull_request()
        self.test_repo.github.get_branch().commit.get_pulls.assert_called()

    @patch.object(Repository, "base_branch", "abc123")
    @patch.object(Repository, "commit_message", "1\n\n3\n4\n5")
    @patch.object(Repository, "update_branch_name", "def456")
    def test_open_pull_request_not_fixing_dry_run(self):
        """
        Test Repository.open_pull_request() when current operation is not
        'fixing' and dry_run == True
        """

        self.test_repo.operation = "not fixing"
        self.test_repo.dry_run = True
        self.test_repo.open_pull_request()
        self.test_repo.github.create_pull.assert_not_called()

    @patch.object(Repository, "base_branch", "abc123")
    @patch.object(Repository, "commit_message", "1\n\n3\n4\n5")
    @patch.object(Repository, "update_branch_name", "def456")
    def test_open_pull_request_not_fixing_no_dry_run(self):
        """
        Test Repository.open_pull_request() when current operation is not
        'fixing' and dry_run == True
        """

        self.test_repo.operation = "not fixing"
        self.test_repo.dry_run = False
        self.test_repo.open_pull_request()
        self.test_repo.github.create_pull.assert_called_with(
            title="1", body="3\n4\n5", head="def456", base="abc123"
        )

    @patch.object(Repository, "commit_message", "1\n\n3\n4\n5")
    @patch("templatron.repo.repository.Repository.git_cmd")
    def test_push_changes_dry_run(self, mock_git):
        """
        Test Repository.push_changes() when dry_run == True
        """

        self.test_repo.dry_run = True
        self.test_repo.push_changes()
        mock_git.assert_not_called()

    @patch.object(Repository, "commit_message", "1\n\n3\n4\n5")
    @patch.object(Repository, "update_branch_name", "def456")
    @patch("templatron.repo.repository.Repository.git_cmd")
    def test_push_changes_no_dry_run(self, mock_git):
        """
        Test Repository.push_changes() when dry_run == False
        """

        self.test_repo.dry_run = False
        self.test_repo.push_changes()
        mock_git.assert_called_with("push")

    @patch("templatron.repo.repository.run_copy")
    @patch("templatron.repo.template.Template.clone")
    def test_run_copier_interactive(self, mock_clone, mock_copy):
        """
        Test Repository.run_copier() in interactive mode
        """

        def noop():
            return

        self.test_repo.interactive = True
        self.test_repo.pretty_print_answers_file = noop
        self.test_repo.run_copier()
        mock_copy.assert_called_with(
            "fake_root/test_template",
            "/fake/root/fake repo",
            answers_file=".copier-answers.yml",
            quiet=False,
            vcs_ref=None,
        )

    @patch("templatron.repo.repository.run_update")
    @patch("templatron.repo.template.Template.clone")
    def test_run_copier_noninteractive(self, mock_clone, mock_copy):
        """
        Test Repository.run_copier() in non-interactive mode
        """

        def noop():
            return

        self.test_repo.interactive = False
        self.test_repo.operation = "updating"
        self.test_repo.pretty_print_answers_file = noop
        self.test_repo.run_copier()
        mock_copy.assert_called_with(
            dst_path="/fake/root/fake repo",
            answers_file=".copier-answers.yml",
            defaults=True,
            quiet=True,
            overwrite=True,
            vcs_ref=None,
        )

    @patch("templatron.repo.repository.subprocess.run")
    def test_run_hook_successful(self, mock_run):
        """
        Test Repository.run_hook()
        """

        self.test_repo.hooks["fake-hook"] = "post-fake"
        self.test_repo.operation = "testing"
        mock_run().returncode = 0
        self.test_repo.run_hook("fake-hook")
        mock_run.assert_called_with(
            [
                "fake_root/test_template/post-fake",
                "testing",
                "/fake/root",
                "fake repo",
                ".copier-answers.yml",
            ],
            capture_output=True,
        )

    @patch("templatron.repo.repository.subprocess.run")
    def test_run_hook_no_hook(self, mock_run):
        """
        Test Repository.run_hook() when the given hook
        doesn't exist
        """

        self.test_repo.operation = "testing"
        self.test_repo.run_hook("fake-hook")
        mock_run.assert_not_called()

    @patch("templatron.repo.repository.subprocess.run")
    def test_run_hook_failure(self, mock_run):
        """
        Test Repository.run_hook() when hook fails
        """

        self.test_repo.hooks["fake-hook"] = "post-fake"
        self.test_repo.operation = "testing"
        mock_run().returncode = 1
        with self.assertRaises(HookFailure):
            self.test_repo.run_hook("fake-hook")
        mock_run.assert_called_with(
            [
                "fake_root/test_template/post-fake",
                "testing",
                "/fake/root",
                "fake repo",
                ".copier-answers.yml",
            ],
            capture_output=True,
        )

    @patch("templatron.repo.repository.Repository.git_cmd")
    def test_switch_to_update_branch_fixing(self, mock_git):
        """
        Docs
        """

        self.test_repo.operation = "fixing"
        self.test_repo.switch_to_update_branch()
        mock_git.assert_not_called()

    @patch.object(Repository, "update_branch_name", "fake_branch")
    @patch("templatron.repo.repository.Repository.git_cmd")
    def test_switch_to_update_branch_not_fixing(self, mock_git):
        """
        Docs
        """

        self.test_repo.operation = "not fixing"
        self.test_repo.switch_to_update_branch()
        mock_git.assert_called_with("checkout", "-b", "fake_branch")

    @patch.object(Repository, "needs_update", True)
    @patch("templatron.repo.repository.Repository.clean_stale_branches")
    @patch("templatron.repo.repository.Repository.clone")
    @patch("templatron.repo.repository.Repository.confirm_changes")
    @patch("templatron.repo.repository.Repository.open_pull_request")
    @patch("templatron.repo.repository.Repository.push_changes")
    @patch("templatron.repo.repository.Repository.run_hook")
    @patch("templatron.repo.repository.Repository.run_copier")
    @patch("templatron.repo.repository.Repository.switch_to_update_branch")
    def test_update_needs_update(
        self,
        mock_switch,
        mock_copier,
        mock_hook,
        mock_push,
        mock_open,
        mock_confirm,
        mock_clone,
        mock_clean,
    ):
        """
        Test Repository.update() where updating and needs update
        """

        self.test_repo.update("updating")
        mock_clean.assert_called()
        mock_hook.assert_called_with("post-push")

    @patch.object(Repository, "needs_update", True)
    @patch("templatron.repo.repository.Repository.clean_stale_branches")
    @patch("templatron.repo.repository.Repository.clone")
    @patch("templatron.repo.repository.Repository.confirm_changes")
    @patch("templatron.repo.repository.Repository.open_pull_request")
    @patch("templatron.repo.repository.Repository.push_changes")
    @patch("templatron.repo.repository.Repository.run_hook")
    @patch("templatron.repo.repository.Repository.run_copier")
    @patch("templatron.repo.repository.Repository.switch_to_update_branch")
    def test_update_no_confirm_changes(
        self,
        mock_switch,
        mock_copier,
        mock_hook,
        mock_push,
        mock_open,
        mock_confirm,
        mock_clone,
        mock_clean,
    ):
        """
        Test Repository.update() where confirm_changes() returns False
        """

        mock_confirm.return_value = False
        self.test_repo.update("updating")
        mock_push.assert_not_called()

    @patch.object(Repository, "needs_update", True)
    @patch("templatron.repo.repository.Repository.clean_stale_branches")
    @patch("templatron.repo.repository.Repository.clone")
    @patch("templatron.repo.repository.Repository.confirm_changes")
    @patch("templatron.repo.repository.Repository.open_pull_request")
    @patch("templatron.repo.repository.Repository.push_changes")
    @patch("templatron.repo.repository.Repository.run_hook")
    @patch("templatron.repo.repository.Repository.run_copier")
    @patch("templatron.repo.repository.Repository.switch_to_update_branch")
    def test_update_fixing(
        self,
        mock_switch,
        mock_copier,
        mock_hook,
        mock_push,
        mock_open,
        mock_confirm,
        mock_clone,
        mock_clean,
    ):
        """
        Test Repository.update() where operation is "fixing"
        """

        self.test_repo.update("fixing")
        mock_clean.assert_not_called()
