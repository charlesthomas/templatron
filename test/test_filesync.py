"""
Test FileSync class
"""

from os import environ
from unittest import TestCase
from unittest.mock import MagicMock, patch

from sh import ErrorReturnCode

from filesync.exceptions import (
    AmbiguousOrgConfigError,
    FilesyncException,
    GitConfigError,
    MissingRequiredConfigError,
    UnrecognizableBaseBranchError,
)
from filesync.filesync import FileSync

# pylint: disable=too-many-public-methods


class TestFileSyncBuildRepo(
    TestCase
):  # pylint: disable=too-many-instance-attributes
    """
    Test build_repo() method in FileSync class
    """

    def setUp(self):
        self.fake_repo = "fake_repo"
        self.fake_org = "fake_org"
        self.fake_token = "ABC123"
        self.fake_clone_root = "/tmp/fake/clone/root"
        self.fake_template = "fake_template"
        self.fake_branch = "fake_main"
        self.fake_github_repo = f"{self.fake_org}/{self.fake_repo}"

        environ["FAKE_TOKEN"] = self.fake_token
        self.filesync = FileSync(
            token_variable_name="FAKE_TOKEN", clone_root=self.fake_clone_root
        )
        self.filesync.github = MagicMock()
        self.filesync.github.get_organization().get_repo.return_value = (
            self.fake_github_repo
        )

    @patch("filesync.filesync.FileSync.validate_repo")
    @patch("filesync.filesync.Repository")
    def test_build_repo_with_base_branch(self, mock_repo, mock_validate):
        """
        Test build_repo() with base_branch set
        """

        mock_validate.return_value = (self.fake_repo, self.fake_org, {})
        self.filesync.template = self.fake_template
        self.filesync.build_repo(self.fake_repo, base_branch=self.fake_branch)
        mock_validate.assert_called_with(self.fake_repo)
        mock_repo.assert_called_with(
            self.fake_repo,
            self.fake_token,
            self.fake_github_repo,
            self.fake_clone_root,
            self.fake_template,
            base_branch=self.fake_branch,
        )

    @patch("filesync.filesync.FileSync.validate_repo")
    @patch("filesync.filesync.Repository")
    def test_build_repo_without_base_branch(self, mock_repo, mock_validate):
        """
        Test build_repo() with base_branch set
        """

        mock_validate.return_value = (self.fake_repo, self.fake_org, {})
        self.filesync.template = self.fake_template
        self.filesync.build_repo(self.fake_repo)
        mock_validate.assert_called_with(self.fake_repo)
        mock_repo.assert_called_with(
            self.fake_repo,
            self.fake_token,
            self.fake_github_repo,
            self.fake_clone_root,
            self.fake_template,
        )


class TestBuildRepos(TestCase):
    """
    Test FileSync.build_repos()
    """

    def setUp(self):
        environ["FAKE_TOKEN"] = "FAKE123"
        self.filesync = FileSync(token_variable_name="FAKE_TOKEN")
        self.filesync.logger = MagicMock()

    @patch("filesync.filesync.FileSync.fetch_repo_list")
    @patch("filesync.filesync.FileSync.build_repo")
    def test_build_repos_base(self, mock_build_repo, mock_repo_list):
        """
        Base test for build_repos()
        """

        mock_repo_list.return_value = ["fake1", "fake2", "fake3"]
        mock_build_repo.side_effect = ["fake4", "fake5", "fake6"]
        repos = self.filesync.build_repos()
        self.assertEqual(repos, ["fake4", "fake5", "fake6"])
        mock_build_repo.assert_any_call("fake1")
        mock_build_repo.assert_any_call("fake2")
        mock_build_repo.assert_any_call("fake3")


class TestBuildTemplate(
    TestCase
):  # pylint: disable=too-many-instance-attributes
    """
    Test FileSync.build_template()
    """

    def setUp(self):
        self.fake_repo = "fake_repo"
        self.fake_org = "fake_org"
        self.fake_token = "ABC123"
        self.fake_clone_root = "/tmp/fake/clone/root"
        self.fake_template = "fake_template"
        self.fake_branch = "fake_main"
        self.fake_github_repo = f"{self.fake_org}/{self.fake_repo}"
        self.fake_dry_run = False
        self.fake_template_config = {}
        self.fake_operation = "NUL"
        self.fake_interactive = False

        environ["FAKE_TOKEN"] = self.fake_token
        self.filesync = FileSync(
            token_variable_name="FAKE_TOKEN",
            clone_root=self.fake_clone_root,
            template_branch=self.fake_branch,
            dry_run=self.fake_dry_run,
            template_config=self.fake_template_config,
            operation=self.fake_operation,
            interactive=self.fake_interactive,
        )
        self.filesync.logger = MagicMock()
        self.filesync.github = MagicMock()
        self.filesync.github.get_organization().get_repo.return_value = (
            self.fake_github_repo
        )

    @patch("filesync.filesync.FileSync.split_org_and_name")
    @patch("filesync.filesync.Template")
    def test_build_template_valid(self, mock_template, mock_split):
        """
        Test valid build_template() call
        """

        mock_template.return_value = self.fake_template
        mock_split.return_value = (self.fake_org, self.fake_repo)
        template = self.filesync.build_template(self.fake_repo)

        mock_split.assert_called_with(self.fake_repo)
        mock_template.assert_called_with(
            self.fake_repo,
            self.fake_token,
            self.fake_github_repo,
            self.fake_clone_root,
            base_branch=self.fake_branch,
            dry_run=self.fake_dry_run,
            template_config=self.fake_template_config,
            operation=self.fake_operation,
            interactive=self.fake_interactive,
        )
        self.assertEqual(template, self.fake_template)

    @patch("filesync.filesync.FileSync.die")
    @patch("filesync.filesync.FileSync.split_org_and_name")
    @patch("filesync.filesync.Template")
    def test_build_template_with_error(
        self, mock_template, mock_split, mock_die
    ):
        """
        Test valid build_template() call
        """

        mock_template.side_effect = FilesyncException
        mock_die.side_effect = SystemExit
        mock_split.return_value = (self.fake_org, self.fake_repo)

        with self.assertRaises(SystemExit):
            self.filesync.build_template(self.fake_repo)

        mock_split.assert_called_with(self.fake_repo)
        mock_template.assert_called_with(
            self.fake_repo,
            self.fake_token,
            self.fake_github_repo,
            self.fake_clone_root,
            base_branch=self.fake_branch,
            dry_run=self.fake_dry_run,
            template_config=self.fake_template_config,
            operation=self.fake_operation,
            interactive=self.fake_interactive,
        )
        mock_die.assert_called()


class TestFetchRepoList(TestCase):
    """
    Test FileSync.fetch_repo_list()
    """

    def setUp(self):
        environ["FAKE_TOKEN"] = "FAKE123"
        self.filesync = FileSync(token_variable_name="FAKE_TOKEN")
        self.filesync.logger = MagicMock()
        self.filesync.github = MagicMock()
        self.filesync.template = MagicMock()
        self.filesync.template.name = "fake_repo321"

    def test_fetch_repo_list_with_valid(self):
        """
        Test fetch_repo_list() with a valid repo
        """

        self.filesync.template.config.autoscan = True

        fake_repo = MagicMock()
        fake_repo.fork = False
        fake_repo.archived = False
        fake_repo.name = "not_the_repo_youre_looking_for"
        self.filesync.github.get_organization().get_repos.return_value = [
            fake_repo
        ]
        self.filesync.has_answersfile = MagicMock()
        self.filesync.has_answersfile.return_value = True

        repo_list = self.filesync.fetch_repo_list()
        self.assertEqual(repo_list, ["not_the_repo_youre_looking_for"])
        self.filesync.github.get_organization().get_repos.assert_called()

    def test_fetch_repo_list_with_no_autoscan(self):
        """
        Test fetch_repo_list() with
        """

        fake_list = list(set(["fake", "repos"]))
        self.filesync.template.config.repos.keys.return_value = fake_list
        self.filesync.template.config.autoscan = False
        repo_list = self.filesync.fetch_repo_list()
        self.assertEqual(repo_list, fake_list)

    def test_fetch_repo_list_with_fork(self):
        """
        Test fetch_repo_list() with a forked repo
        """

        self.filesync.template.config.autoscan = True

        fake_repo = MagicMock()
        fake_repo.fork = True
        fake_repo.archived = False
        fake_repo.name = "not_the_repo_youre_looking_for"
        self.filesync.github.get_organization().get_repos.return_value = [
            fake_repo
        ]

        repo_list = self.filesync.fetch_repo_list()
        self.assertEqual(repo_list, [])
        self.filesync.github.get_organization().get_repos.assert_called()

    def test_fetch_repo_list_with_archived(self):
        """
        Test fetch_repo_list() with an archived repo
        """

        self.filesync.template.config.autoscan = True

        fake_repo = MagicMock()
        fake_repo.fork = False
        fake_repo.archived = True
        fake_repo.name = "not_the_repo_youre_looking_for"
        self.filesync.github.get_organization().get_repos.return_value = [
            fake_repo
        ]

        repo_list = self.filesync.fetch_repo_list()
        self.assertEqual(repo_list, [])
        self.filesync.github.get_organization().get_repos.assert_called()

    def test_fetch_repo_list_with_template(self):
        """
        Test fetch_repo_list() with template repo
        """

        self.filesync.template.config.autoscan = True

        fake_repo = MagicMock()
        fake_repo.fork = False
        fake_repo.archived = False
        fake_repo.name = "fake_repo321"
        self.filesync.github.get_organization().get_repos.return_value = [
            fake_repo
        ]

        repo_list = self.filesync.fetch_repo_list()
        self.assertEqual(repo_list, [])
        self.filesync.github.get_organization().get_repos.assert_called()

    @patch("filesync.filesync.makedirs")
    def test_create_clone_root(self, mock_makedirs):
        """
        Test FileSync.create_clone_root()
        """

        self.filesync.config.clone_root = "/fake/root"
        self.filesync.create_clone_root()
        mock_makedirs.assert_called_with("/fake/root", exist_ok=True)

    @patch("filesync.filesync.FileSync.maybe_clean")
    def test_die(self, mock_clean):
        """
        Test FileSync.die()
        """

        with self.assertRaises(SystemExit):
            self.filesync.die("Not a real error")
        mock_clean.assert_called()

    @patch("filesync.filesync.FileSync.start")
    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    def test_fix_ok(self, mock_stop, mock_build, mock_start):
        """
        Test FileSync.fix() with no errors
        """

        self.filesync.fix("repo", "branch")
        mock_start.assert_called_with("fixing")
        mock_build().fix.assert_called()
        mock_stop.assert_called()

    @patch("filesync.filesync.FileSync.die")
    @patch("filesync.filesync.FileSync.start")
    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    def test_fix_unrecognizable_branch(
        self, mock_stop, mock_build, mock_start, mock_die
    ):
        """
        Test FileSync.fix() with unrecognized branch
        """

        mock_build.side_effect = UnrecognizableBaseBranchError
        mock_die.side_effect = SystemExit
        with self.assertRaises(SystemExit):
            self.filesync.fix("repo", "branch")
        mock_start.assert_called_with("fixing")
        mock_stop.assert_not_called()

    @patch("filesync.filesync.FileSync.maybe_clean")
    @patch("filesync.filesync.FileSync.start")
    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    def test_fix_keyboard_int(
        self, mock_stop, mock_build, mock_start, mock_clean
    ):
        """
        Test FileSync.fix() with keyboard interrupt
        """

        mock_build.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.filesync.fix("repo", "branch")
        mock_start.assert_called_with("fixing")
        mock_clean.assert_called()
        mock_stop.assert_not_called()

    @patch("filesync.filesync.rmtree")
    @patch("filesync.filesync.os.path.exists")
    def test_maybe_clean_autoclean_and_exists(
        self,
        mock_exists,
        mock_rmtree,
    ):
        """
        Test FileSync.maybe_clean() where autoclean = True and the clone root
        exists
        """

        self.filesync.config.autoclean = True
        mock_exists.return_value = True
        self.filesync.maybe_clean()
        mock_rmtree.assert_called()

    @patch("filesync.filesync.rmtree")
    @patch("filesync.filesync.os.path.exists")
    def test_maybe_clean_autoclean_and_not_exists(
        self,
        mock_exists,
        mock_rmtree,
    ):
        """
        Test FileSync.maybe_clean() where autoclean = True and the clone root
        does not exist
        """

        self.filesync.config.autoclean = True
        mock_exists.return_value = False
        self.filesync.maybe_clean()
        mock_rmtree.assert_not_called()

    @patch("filesync.filesync.rmtree")
    @patch("filesync.filesync.os.path.exists")
    def test_maybe_clean_not_autoclean_and_exists(
        self,
        mock_exists,
        mock_rmtree,
    ):
        """
        Test FileSync.maybe_clean() where autoclean = False and the clone root
        exists
        """

        self.filesync.config.autoclean = False
        mock_exists.return_value = True
        self.filesync.maybe_clean()
        mock_rmtree.assert_not_called()

    @patch("filesync.filesync.rmtree")
    @patch("filesync.filesync.os.path.exists")
    def test_maybe_clean_not_autoclean_and_not_exists(
        self,
        mock_exists,
        mock_rmtree,
    ):
        """
        Test FileSync.maybe_clean() where autoclean = False and the clone root
        does not exist
        """

        self.filesync.config.autoclean = False
        mock_exists.return_value = False
        self.filesync.maybe_clean()
        mock_rmtree.assert_not_called()

    @patch("filesync.filesync.log_or_print")
    def test_maybe_log_dry_run_dry_run(self, mock_log):
        """
        Test FileSync.maybe_log_dry_run() when a dry run
        """

        self.filesync.config.dry_run = True
        self.filesync.maybe_log_dry_run()
        mock_log.assert_called()

    @patch("filesync.filesync.log_or_print")
    def test_maybe_log_dry_run_no_dry_run(self, mock_log):
        """
        Test FileSync.maybe_log_dry_run() when not a dry run
        """

        self.filesync.config.dry_run = False
        self.filesync.maybe_log_dry_run()
        mock_log.assert_not_called()

    @patch("filesync.filesync.FileSync.start")
    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    def test_onboard_ok(self, mock_stop, mock_build, mock_start):
        """
        Test FileSync.onboard() with no errors
        """

        self.filesync.onboard("repo")
        mock_start.assert_called_with("onboarding")
        mock_build().onboard.assert_called()
        mock_stop.assert_called()

    @patch("filesync.filesync.FileSync.die")
    @patch("filesync.filesync.FileSync.start")
    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    def test_onboard_unrecognizable_branch(
        self, mock_stop, mock_build, mock_start, mock_die
    ):
        """
        Test FileSync.onboard() with unrecognized branch
        """

        mock_build.side_effect = UnrecognizableBaseBranchError
        mock_die.side_effect = SystemExit
        with self.assertRaises(SystemExit):
            self.filesync.onboard("repo")
        mock_start.assert_called_with("onboarding")
        mock_stop.assert_not_called()

    @patch("filesync.filesync.FileSync.maybe_clean")
    @patch("filesync.filesync.FileSync.start")
    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    def test_onboard_keyboard_int(
        self, mock_stop, mock_build, mock_start, mock_clean
    ):
        """
        Test FileSync.onboard() with keyboard interrupt
        """

        mock_build.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.filesync.onboard("repo")
        mock_start.assert_called_with("onboarding")
        mock_clean.assert_called()
        mock_stop.assert_not_called()

    @patch("filesync.filesync.LoggingConfig")
    @patch("filesync.filesync.logging")
    def test_setup_logging(self, mock_log, mock_config):
        """
        Test FileSync.setup_logging()
        """

        mock_config().get.side_effect = ["one", "two", "three", "four", "five"]
        self.filesync.setup_logging("fake_command")
        mock_config.assert_called()
        mock_log.basicConfig.assert_called_with(
            filename="one", format="two", datefmt="three", level="FOUR"
        )
        mock_log.getLogger().setLevel.assert_called_with("FIVE")

    def test_split_org_and_name_org_and_name(self):
        """
        Test FileSync.split_org_and_name() with the org and name
        """

        self.assertEqual(
            self.filesync.split_org_and_name("fake_org/fake_name"),
            ("fake_org", "fake_name"),
        )

    def test_split_org_and_name_just_name(self):
        """
        Test FileSync.split_org_and_name() with just the name
        """

        self.filesync.template.config.org = "fake_org"
        self.assertEqual(
            self.filesync.split_org_and_name("fake_name"),
            ("fake_org", "fake_name"),
        )

    def test_split_org_and_name_no_org(self):
        """
        Test FileSync.split_org_and_name() with no org defined
        """

        self.filesync.template.config.org = None
        with self.assertRaises(MissingRequiredConfigError):
            self.filesync.split_org_and_name("fake_name")

    @patch("filesync.filesync.FileSync.setup_logging")
    @patch("filesync.filesync.FileSync.maybe_log_dry_run")
    @patch("filesync.filesync.FileSync.validate_config")
    @patch("filesync.filesync.FileSync.die")
    @patch("filesync.filesync.FileSync.create_clone_root")
    @patch("filesync.filesync.FileSync.build_template")
    def test_start_valid(
        self,
        mock_build,
        mock_create,
        mock_die,
        mock_validate,
        mock_maybe_log,
        mock_setup_log,
    ):  # pylint: disable=too-many-arguments
        """
        Test FileSync.start() where the config is valid
        """

        mock_die.side_effect = SystemExit
        self.filesync.start("command")
        mock_setup_log.assert_called_with("command")
        mock_maybe_log.assert_called()
        mock_validate.assert_called()
        mock_die.assert_not_called()
        mock_create.assert_called()
        mock_build.assert_called()

    @patch("filesync.filesync.FileSync.setup_logging")
    @patch("filesync.filesync.FileSync.maybe_log_dry_run")
    @patch("filesync.filesync.FileSync.validate_config")
    @patch("filesync.filesync.FileSync.die")
    @patch("filesync.filesync.FileSync.create_clone_root")
    @patch("filesync.filesync.FileSync.build_template")
    def test_start_invalid(
        self,
        mock_build,
        mock_create,
        mock_die,
        mock_validate,
        mock_maybe_log,
        mock_setup_log,
    ):  # pylint: disable=too-many-arguments
        """
        Test FileSync.start() where the config is invalid
        """

        mock_validate.side_effect = FilesyncException
        mock_die.side_effect = SystemExit
        with self.assertRaises(SystemExit):
            self.filesync.start("command")
        mock_setup_log.assert_called_with("command")
        mock_maybe_log.assert_called()
        mock_validate.assert_called()
        mock_die.assert_called()
        mock_create.assert_not_called()
        mock_build.assert_not_called()

    @patch("filesync.filesync.FileSync.maybe_clean")
    def test_stop(self, mock_clean):
        """
        Test FileSync.stop()
        """

        self.filesync.stop()
        mock_clean.assert_called()

    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    @patch("filesync.filesync.FileSync.start")
    def test_update_single_repo(self, mock_start, mock_stop, mock_build):
        """
        Test FileSync.update() with a single repo
        """

        self.filesync.update("fake_repo")
        mock_start.assert_called_with("updating")
        mock_build.assert_called_with("fake_repo")
        mock_build().update.assert_called()
        mock_stop.assert_called()

    @patch("filesync.filesync.FileSync.build_repos")
    @patch("filesync.filesync.FileSync.stop")
    @patch("filesync.filesync.FileSync.start")
    def test_update_multi_repos(self, mock_start, mock_stop, mock_build):
        """
        Test FileSync.update() with multiple repos
        """

        self.filesync.update()
        mock_start.assert_called_with("updating")
        mock_build.assert_called()
        mock_stop.assert_called()

    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    @patch("filesync.filesync.FileSync.start")
    def test_update_update_error(self, mock_start, mock_stop, mock_build):
        """
        Test FileSync.update() when repo.update() fails
        """

        mock_build().update.side_effect = FilesyncException
        self.filesync.logger = MagicMock()
        self.filesync.update("fake_repo")
        mock_start.assert_called_with("updating")
        mock_build.assert_called_with("fake_repo")
        mock_build().update.assert_called()
        mock_stop.assert_called()
        self.filesync.logger.error.assert_called()

    @patch("filesync.filesync.FileSync.maybe_clean")
    @patch("filesync.filesync.FileSync.build_repo")
    @patch("filesync.filesync.FileSync.stop")
    @patch("filesync.filesync.FileSync.start")
    def test_update_keyboard_interrupt(
        self, mock_start, mock_stop, mock_build, mock_clean
    ):
        """
        Test FileSync.update() when a keyboard interrupt occurs
        """

        mock_build.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.filesync.update("fake_repo")
        mock_start.assert_called_with("updating")
        mock_build.assert_called_with("fake_repo")
        mock_stop.assert_not_called()
        mock_clean.assert_called()

    def test_validate_config_no_github_token(self):
        """
        Test FileSync.validate_config() when no github token is present
        """

        self.filesync.token = None
        with self.assertRaises(GitConfigError):
            self.filesync.validate_config()

    @patch("filesync.filesync.git")
    @patch("filesync.filesync.environ.get")
    def test_validate_config_env_vars_set(self, mock_get, mock_git):
        """
        Test FileSync.validate_config() when git config environment variables
        are set
        """

        mock_get.return_value = "fake value"
        self.filesync.validate_config()
        mock_git.assert_not_called()

    @patch("filesync.filesync.git")
    @patch("filesync.filesync.environ.get")
    def test_validate_config_git_error(self, mock_get, mock_git):
        """
        Test FileSync.validate_config() when git config encounters an error
        """

        mock_get.return_value = None
        mock_git.config.side_effect = ErrorReturnCode(
            "fake_cmd", b"stdout", b"stderr"
        )
        with self.assertRaises(GitConfigError):
            self.filesync.validate_config()
        mock_git.config.assert_called_with("--get", "user.email")

    @patch("filesync.filesync.git")
    @patch("filesync.filesync.environ.get")
    def test_validate_config_valid(self, mock_get, mock_git):
        """
        Test FileSync.validate_config() when config is valid
        """

        mock_get.return_value = None
        self.filesync.validate_config()
        mock_git.config.assert_called_with("--get", "user.name")

    # * repo_name in repo_keys
    # * kw_org = None
    # * org is not None and kw_org != org
    # * dry_run is True
    # * interactive is True
    # * ensure kwargs['org'] doesn't exist

    @patch("filesync.filesync.FileSync.split_org_and_name")
    def test_validate_repo_no_kw_org(self, mock_split):
        """
        Test FileSync.validate_repo() with no org set in config
        """

        mock_split.return_value = ("fake_org", "fake_repo")
        self.filesync.template.config.get.side_effect = [
            "answers_file",
            "branch_prefix",
            "branch_separator",
            "dry_run",
            "hooks",
        ]
        kwargs = {
            "answers_file": "answers_file",
            "branch_prefix": "branch_prefix",
            "branch_separator": "branch_separator",
            "dry_run": "dry_run",
            "hooks": "hooks",
        }
        self.assertEqual(
            self.filesync.validate_repo("fake_org/fake_repo"),
            ("fake_repo", "fake_org", kwargs),
        )

    @patch("filesync.filesync.FileSync.split_org_and_name")
    def test_validate_repo_repo_in_repos(self, mock_split):
        """
        Test FileSync.validate_repo() where repo_name is in repo config
        """

        mock_split.return_value = ("fake_org", "fake_repo")
        self.filesync.template.config.repos = {
            "fake_repo": {
                "org": "fake_org",
            }
        }
        self.filesync.template.config.get.side_effect = [
            "answers_file",
            "branch_prefix",
            "branch_separator",
            "dry_run",
            "hooks",
        ]
        kwargs = {
            "answers_file": "answers_file",
            "branch_prefix": "branch_prefix",
            "branch_separator": "branch_separator",
            "dry_run": "dry_run",
            "hooks": "hooks",
        }
        self.assertEqual(
            self.filesync.validate_repo("fake_repo"),
            ("fake_repo", "fake_org", kwargs),
        )

    @patch("filesync.filesync.FileSync.split_org_and_name")
    def test_validate_repo_org_mismatch(self, mock_split):
        """
        Test FileSync.validate_repo() where repo_name is in repo config
        """

        mock_split.return_value = ("other_org", "fake_repo")
        self.filesync.template.config.repos = {
            "fake_repo": {
                "org": "fake_org",
            }
        }
        with self.assertRaises(AmbiguousOrgConfigError):
            self.filesync.validate_repo("fake_repo")

    @patch("filesync.filesync.FileSync.split_org_and_name")
    def test_validate_repo_global_force(self, mock_split):
        """
        Test FileSync.validate_repo() where dry_run or interactive
        configs are enabled
        """

        mock_split.return_value = ("fake_org", "fake_repo")
        self.filesync.config.dry_run = True
        self.filesync.config.interactive = True
        self.filesync.template.config.repos = {
            "fake_repo": {
                "org": "fake_org",
            }
        }
        self.filesync.template.config.get.side_effect = [
            "answers_file",
            "branch_prefix",
            "branch_separator",
            "dry_run",
            "hooks",
        ]
        kwargs = {
            "answers_file": "answers_file",
            "branch_prefix": "branch_prefix",
            "branch_separator": "branch_separator",
            "dry_run": True,
            "hooks": "hooks",
            "interactive": True,
        }
        self.assertEqual(
            self.filesync.validate_repo("fake_repo"),
            ("fake_repo", "fake_org", kwargs),
        )
